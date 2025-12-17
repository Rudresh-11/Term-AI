import os
import sys
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai  # Added for listing models
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt        # Added for user input
from agent import Agent

# Load env

app = typer.Typer()
console = Console()

def select_model_interactive(api_key: str):
    """
    Fetches available Gemini models and asks the user to pick one.
    """
    try:
        genai.configure(api_key=api_key)
        
        with console.status("[bold green]Fetching available models...[/bold green]"):
            # Get models that support content generation
            models = [
                m for m in genai.list_models() 
                if 'generateContent' in m.supported_generation_methods
            ]
            # Sort for cleaner display (pro/flash usually at top)
            models.sort(key=lambda x: x.name)

        console.print("\n[bold cyan]Available Gemini Models:[/bold cyan]")
        for idx, m in enumerate(models):
            display_name = m.name.split("/")[-1]
            console.print(f"  [bold green]{idx + 1}.[/bold green] {display_name}")

        # Default choice logic
        choice = Prompt.ask(
            "\n[bold yellow]Select a model number[/bold yellow]", 
            default="1",
            show_default=True
        )

        # Validate input
        try:
            selection_index = int(choice) - 1
            if 0 <= selection_index < len(models):
                selected_model = models[selection_index].name
                console.print(f"[dim]Selected: {selected_model}[/dim]\n")
                return selected_model
            else:
                console.print("[red]Invalid selection. Defaulting to first model.[/red]")
                return models[0].name
        except ValueError:
            console.print("[red]Invalid input. Defaulting to first model.[/red]")
            return models[0].name

    except Exception as e:
        console.print(f"[bold red]Could not fetch models:[/bold red] {e}")
        console.print("[yellow]Falling back to default 'gemini-1.5-flash'[/yellow]")
        return "gemini-1.5-flash"


@app.command()
def start():
    """
    Start the Term-AI Assistant.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] GOOGLE_API_KEY is not set.")
        console.print("Please set it in a .env file or export it in your shell.")
        sys.exit(1)

    console.print("[bold green]Term-AI[/bold green] initialized.")
    console.print("[dim]Powered by Google Gemini. Current Directory is sandboxed.[/dim]")
    
    # --- NEW: Select Model ---
    selected_model_name = select_model_interactive(api_key)

    try:
        # Pass the selected model to the Agent
        agent = Agent(model_name=selected_model_name)
    except Exception as e:
        console.print(f"[bold red]Failed to initialize agent:[/bold red] {e}")
        sys.exit(1)

    console.print(f"[bold blue]Session started with {selected_model_name.split('/')[-1]}[/bold blue]. Type 'exit' to quit.")

    while True:
        try:
            user_input = console.input("\n[bold cyan]>[/bold cyan] ")
            
            if user_input.lower() in ["exit", "quit"]:
                console.print("Goodbye!")
                break
            if user_input.lower() in ["clear", "reset"]:
                # Re-initialize with the SAME model
                agent = Agent(model_name=selected_model_name) 
                console.print("[bold green]Memory cleared. Context reset.[/bold green]")
                continue
            if not user_input.strip():
                continue

            with console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
                response = agent.send_message(user_input, console)

            console.print(Markdown(response))

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Runtime Error:[/bold red] {e}")

if __name__ == "__main__":
    app()