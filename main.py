import argparse
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from agent.loop import run_agent
from report.generator import generate_report

console = Console()


def load_config():
    config_path = Path(__file__).parent / "config.yml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="VulnWhisper — AI-powered bug bounty recon agent"
    )
    parser.add_argument("domain", help="Target domain (e.g. example.com)")
    parser.add_argument("--guided", action="store_true", help="Confirm before each action (beginner mode)")
    parser.add_argument("--model", help="Override model from config")
    args = parser.parse_args()

    config = load_config()
    model = args.model or config.get("model", "google/gemini-2.0-flash-exp")
    max_iterations = config.get("max_iterations", 30)

    # Get API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        api_key = Prompt.ask("[bold yellow]Enter your OpenRouter API key[/bold yellow]", password=True)
    if not api_key:
        console.print("[red]No API key provided. Exiting.[/red]")
        sys.exit(1)

    # Run agent
    findings = run_agent(
        domain=args.domain,
        api_key=api_key,
        model=model,
        guided=args.guided,
        max_iterations=max_iterations
    )

    # Save report
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"{args.domain}_{timestamp}.md"
    report_content = generate_report(args.domain, findings)
    report_path.write_text(report_content)

    console.print(f"\n[bold green]📄 Report saved → {report_path}[/bold green]")


if __name__ == "__main__":
    main()
