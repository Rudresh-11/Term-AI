import os
import google.generativeai as genai
from google.generativeai.types import content_types
from collections.abc import Iterable
from security import confirm_action
from tools import TOOL_MAP, TOOLS_SCHEMA

# Configure API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")
genai.configure(api_key=api_key)

SYSTEM_INSTRUCTION = """
You are a Senior Systems Engineer and AI Architect assisting a developer in a CLI.
Your goal is to help build, debug, and refactor code safely and efficiently.

**Capabilities:**
1.  **File System:** You can read, write, and list files. Always explore the directory first if you don't know the structure.
2.  **Shell Execution:** You can run terminal commands (git, grep, python, npm, docker, etc.).

**Strict Rules:**
1.  **Safety First:** NEVER delete data or run destructive commands (rm -rf /) without explicit user request and extreme caution.
2.  **Step-by-Step:** specific plans before acting. If a task is complex, break it down.
3.  **Verification:** After writing code, try to run it or test it if possible.
4.  **Conciseness:** Be brief. You are in a terminal.
5.  **Tools:** Use the provided tools. Do not hallucinate file contents.

**Operating System:**
The user is running on a standard POSIX shell (Linux/macOS) or Windows. Adapt commands accordingly.
"""

class Agent:
    def __init__(self):
        # 2. OPTIMIZATION: Use 'gemini-2.0-flash' or 'gemini-1.5-flash' (usually cheaper/faster than 2.5)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite', 
            tools=TOOLS_SCHEMA,
            system_instruction=SYSTEM_INSTRUCTION
        )
        self.chat = self.model.start_chat(enable_automatic_function_calling=False)

    def send_message(self, user_input: str, console):
        # Rolling window history cleanup
        if len(self.chat.history) > 20:
            self.chat.history = self.chat.history[-10:]

        try:
            # 1. Send the user message
            response = self.chat.send_message(user_input)

            # 2. Loop to handle tool calls (until the AI is done)
            while True:
                # Helper: Find the first function call in the response parts
                function_call = None
                for part in response.parts:
                    if part.function_call:
                        function_call = part.function_call
                        break
                
                # If no function call found, we are done! Break the loop.
                if not function_call:
                    break
                
                # Setup Execution
                fname = function_call.name
                fargs = dict(function_call.args)

                # Security Confirmation
                allowed = True
                if fname == "write_file":
                    allowed = confirm_action("WRITE", f"{fargs.get('file_path')}")
                elif fname == "run_shell_command":
                    allowed = confirm_action("EXEC", f"{fargs.get('command')}")
                
                # Execute Tool
                result_content = ""
                if allowed:
                    console.print(f"[dim]>> Running {fname}...[/dim]")
                    try:
                        tool_func = TOOL_MAP.get(fname)
                        result = tool_func(**fargs)
                        
                        # Truncate large outputs
                        result_str = str(result)
                        if len(result_str) > 2000:
                            result_str = result_str[:2000] + "\n...[Output Truncated]..."
                        result_content = result_str
                    except Exception as e:
                        result_content = f"Error: {e}"
                else:
                    result_content = "User denied action."
                    console.print("[red]Cancelled.[/red]")

                # Send result back to AI
                # This generates a NEW response, which we loop back to check again
                response = self.chat.send_message(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fname,
                                response={'result': result_content}
                            )
                        )]
                    )
                )

            # 3. Return the final text response
            return response.text

        except Exception as e:
            return f"Error: {e}"