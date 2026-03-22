import json
import re
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm
from agent.tools import execute_tool
from agent.prompts import SYSTEM_PROMPT

console = Console()


def parse_response(text):
    # Try to extract JSON from response
    text = text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def run_agent(domain, api_key, model, guided=False, max_iterations=30):
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Start recon on target domain: {domain}\nBegin with DNS, headers, and subdomain enumeration."}
    ]

    findings = []
    iteration = 0

    console.print(Panel(
        f"[bold green]🎯 Target: {domain}[/bold green]\n"
        f"[dim]Model: {model} | Mode: {'Guided 🧭' if guided else 'Autonomous 🤖'} | Max steps: {max_iterations}[/dim]",
        title="[bold red]VulnWhisper[/bold red]",
        border_style="red"
    ))

    while iteration < max_iterations:
        iteration += 1

        console.print(f"\n[dim]━━━ Step {iteration} ━━━[/dim]")

        # Call AI
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=1000,
            )
            raw = response.choices[0].message.content
        except Exception as e:
            console.print(f"[red]AI error: {e}[/red]")
            break

        parsed = parse_response(raw)
        if not parsed:
            console.print(f"[yellow]Could not parse AI response:[/yellow]\n{raw}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": "Please respond in the exact JSON format specified."})
            continue

        thought = parsed.get("thought", "")
        action = parsed.get("action", "")
        params = parsed.get("params", {})
        finding = parsed.get("finding")

        # Show thought
        console.print(f"\n[bold cyan]💭 Thought:[/bold cyan] {thought}")

        # Handle finding
        if finding:
            sev = finding.get("severity", "info").upper()
            color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "blue", "INFO": "dim"}.get(sev, "white")
            console.print(Panel(
                f"[bold]Title:[/bold] {finding.get('title')}\n"
                f"[bold]Detail:[/bold] {finding.get('detail')}\n"
                f"[bold]Evidence:[/bold] {finding.get('evidence')}",
                title=f"[{color}]🔍 Finding: {sev}[/{color}]",
                border_style=color
            ))
            findings.append(finding)

        # Done?
        if action == "DONE":
            console.print("\n[bold green]✅ Recon complete.[/bold green]")
            break

        # Show action
        console.print(f"[bold yellow]⚡ Action:[/bold yellow] [bold]{action}[/bold]")
        console.print(f"[dim]   Params: {json.dumps(params)}[/dim]")

        # Guided mode confirmation
        if guided:
            proceed = Confirm.ask("[bold magenta]   Run this?[/bold magenta]", default=True)
            if not proceed:
                console.print("[dim]   Skipped.[/dim]")
                messages.append({"role": "assistant", "content": raw})
                messages.append({"role": "user", "content": "User skipped that action. Choose a different action or move on."})
                continue

        # Execute tool
        console.print(f"[dim]   Running...[/dim]")
        observation = execute_tool(action, params)

        # Show observation (truncated if huge)
        obs_display = observation[:2000] + "\n... (truncated)" if len(observation) > 2000 else observation
        console.print(Panel(
            obs_display,
            title="[dim]📡 Observation[/dim]",
            border_style="dim"
        ))

        # Feed back to AI
        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user", "content": f"Observation:\n{observation}\n\nContinue recon. What's next?"})

    return findings
