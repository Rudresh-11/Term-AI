import os
import sys
from dotenv import load_dotenv
load_dotenv("./.env")
import typer
from rich.console import Console
from rich.markdown import Markdown
from agent import Agent

# Load env

app = typer.Typer()
console = Console()

@app.command()
def start():
    """
    Start the Term-AI Assistant.
    """
    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[bold red]Error:[/bold red] GOOGLE_API_KEY is not set.")
        console.print("Please set it in a .env file or export it in your shell.")
        sys.exit(1)

    console.print("[bold green]Term-AI[/bold green] initialized. Type 'exit' to quit.")
    console.print("[dim]Powered by Google Gemini. Current Directory is sandboxed.[/dim]")
    
    try:
        agent = Agent()
    except Exception as e:
        console.print(f"[bold red]Failed to initialize agent:[/bold red] {e}")
        sys.exit(1)

    while True:
        try:
            user_input = console.input("\n[bold cyan]>[/bold cyan] ")
            
            if user_input.lower() in ["exit", "quit"]:
                console.print("Goodbye!")
                break
            if user_input.lower() in ["clear", "reset"]:
                agent = Agent() # Re-initialize the agent entirely
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