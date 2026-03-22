from datetime import datetime


def generate_report(domain, findings):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sev_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings_sorted = sorted(findings, key=lambda x: sev_order.get(x.get("severity", "info").lower(), 4))

    lines = [
        f"# VulnWhisper Report",
        f"",
        f"**Target:** `{domain}`  ",
        f"**Generated:** {now}  ",
        f"**Findings:** {len(findings)}",
        f"",
        "---",
        "",
        "## Summary",
        "",
    ]

    counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev = f.get("severity", "info").lower()
        counts[sev] = counts.get(sev, 0) + 1

    lines.append(f"| Severity | Count |")
    lines.append(f"|----------|-------|")
    for sev, count in counts.items():
        if count > 0:
            lines.append(f"| {sev.upper()} | {count} |")

    lines += ["", "---", "", "## Findings", ""]

    if not findings_sorted:
        lines.append("_No notable findings recorded._")
    else:
        for i, f in enumerate(findings_sorted, 1):
            sev = f.get("severity", "info").upper()
            lines += [
                f"### {i}. {f.get('title', 'Untitled')} `[{sev}]`",
                f"",
                f"**Detail:** {f.get('detail', 'N/A')}",
                f"",
                f"**Evidence:**",
                f"```",
                f"{f.get('evidence', 'N/A')}",
                f"```",
                f"",
            ]

    return "\n".join(lines)
