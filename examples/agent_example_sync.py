import logging
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from stagehand.sync import Stagehand, SyncAgent
from stagehand import StagehandConfig, AgentConfig
from stagehand.utils import configure_logging, StagehandLogger
from stagehand.schemas import AgentExecuteOptions, AgentProvider

# Create a custom theme for consistent styling
custom_theme = Theme(
    {
        "info": "bold white",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "highlight": "magenta",
        "url": "blue underline",
    }
)

# Create a Rich console instance with our theme
console = Console(theme=custom_theme)

load_dotenv()

# Configure logging with the utility function
configure_logging(
    level=logging.INFO,  # Set to INFO for regular logs, DEBUG for detailed
    use_rich=True,       # Use Rich for colorized output
    quiet_dependencies=True,  # Reduce noise from dependencies
)

console.print(
    Panel.fit(
        "[yellow]Logging Levels:[/]\n"
        "[white]- Set [bold]verbose=0[/] for errors (ERROR)[/]\n"
        "[white]- Set [bold]verbose=1[/] for minimal logs (INFO)[/]\n"
        "[white]- Set [bold]verbose=2[/] for medium logs (WARNING)[/]\n"
        "[white]- Set [bold]verbose=3[/] for detailed logs (DEBUG)[/]",
        title="Verbosity Options",
        border_style="blue",
    )
)

def main():
    # Build a unified configuration object for Stagehand
    config = StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        headless=False,
        dom_settle_timeout_ms=3000,
        model_name="gpt-4o",
        self_heal=True,
        wait_for_captcha_solves=True,
        system_prompt="You are a browser automation assistant that helps users navigate websites effectively.",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
        # Set verbosity level here. This affects both the server and client logs.
        verbose=2,  # Change to 1 for minimal, 2 for medium, 3 for detailed
    )

    # Create a Stagehand client using the configuration object.
    stagehand = Stagehand(
        config=config, 
        server_url=os.getenv("STAGEHAND_SERVER_URL"),
        use_rich_logging=True  # Enable rich formatting for logs
    )

    # Initialize - this creates a new session automatically.
    console.print("\n🚀 [info]Initializing Stagehand...[/]")
    stagehand.init()
    console.print(f"\n[yellow]Created new session:[/] {stagehand.session_id}")
    console.print(
        f"🌐 [white]View your live browser:[/] [url]https://www.browserbase.com/sessions/{stagehand.session_id}[/]"
    )
    
    # Configure the agent
    agent_config = AgentConfig(
        provider=AgentProvider.OPENAI,
        model="computer-use-preview",
        instructions="You are a helpful web navigation assistant that helps users find information. You are currently on the following page: google.com. Do not ask follow up questions, the user will trust your judgement.",
        options={"apiKey": os.getenv("MODEL_API_KEY")}
    )
    
    # Define the task for the agent
    execute_options = AgentExecuteOptions(
        instruction="Play a game of 2048",
        max_steps=20,
        auto_screenshot=True,
    )

    console.print("\n▶️ [highlight] Navigating[/] to Google")
    stagehand.page.goto("https://google.com/")
    console.print("✅ [success]Navigated to Google[/]")
    
    console.print("\n▶️ [highlight] Using Agent to perform a task[/]: playing a game of 2048")
    agent_result = stagehand.agent.execute(agent_config, execute_options)
    
    console.print("📊 [info]Agent execution result:[/]")
    console.print_json(f"{agent_result.model_dump_json()}")

    # Close the session
    console.print("\n⏹️ [warning]Closing session...[/]")
    stagehand.close()
    console.print("✅ [success]Session closed successfully![/]")
    console.rule("[bold]End of Example[/]")


if __name__ == "__main__":
    # Add a fancy header
    console.print(
        "\n",
        Panel.fit(
            "[light_gray]Stagehand 🤘 Sync Agent Example[/]",
            border_style="green",
            padding=(1, 10),
        ),
    )
    main() 