import subprocess
import shlex
import json


def run_cmd(cmd, timeout=20):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=timeout
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        return out if out else err if err else "(no output)"
    except subprocess.TimeoutExpired:
        return "(command timed out)"
    except Exception as e:
        return f"(error: {e})"


def curl_probe(url, headers=None, follow_redirects=True, method="GET"):
    flags = "-sk"
    if follow_redirects:
        flags += "L"
    if method == "HEAD":
        flags += "I"
    header_str = ""
    if headers:
        for k, v in headers.items():
            header_str += f' -H "{k}: {v}"'
    cmd = f'curl {flags} -w "\\nHTTP_CODE:%{{http_code}}" {header_str} "{url}"'
    return run_cmd(cmd)


def ssl_inspect(domain):
    cmd = f'echo | openssl s_client -connect {domain}:443 2>/dev/null | openssl x509 -noout -text 2>/dev/null | grep -E "Subject:|Issuer:|Not After|DNS:"'
    return run_cmd(cmd)


def subdomain_enum(domain):
    result = run_cmd(f"subfinder -d {domain} -silent", timeout=60)
    if "(error" in result or "not found" in result.lower():
        result = run_cmd(f"dig +short {domain} ANY")
    return result


def httpx_probe(domains_list):
    if isinstance(domains_list, list):
        domains = "\n".join(domains_list)
    else:
        domains = domains_list
    # Write to temp file to avoid arg length issues
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(domains)
        tmp = f.name
    cmd = f"httpx -l {tmp} -silent -status-code -title -tech-detect 2>/dev/null"
    result = run_cmd(cmd, timeout=60)
    os.unlink(tmp)
    if "command not found" in result or "not found" in result.lower():
        # fallback: curl each domain
        results = []
        for d in domains.splitlines():
            d = d.strip()
            if d:
                r = run_cmd(f'curl -skL -o /dev/null -w "{d} → %{{http_code}}" "https://{d}"')
                results.append(r)
        return "\n".join(results)
    return result

def dns_lookup(domain):
    dig = run_cmd(f"dig +short {domain}")
    whois = run_cmd(f"whois {domain} 2>/dev/null | grep -E 'Registrar:|Creation|Expir|Name Server' | head -10")
    return f"=== DIG ===\n{dig}\n\n=== WHOIS ===\n{whois}"


def path_fuzz(base_url, paths=None):
    if not paths:
        paths = [
            "/api", "/api/v1", "/api/v2", "/health", "/status",
            "/admin", "/swagger", "/swagger-ui.html", "/api-docs",
            "/graphql", "/console", "/debug", "/metrics",
            "/.env", "/.git/HEAD", "/config", "/upload", "/uploads"
        ]
    results = []
    for path in paths:
        url = base_url.rstrip("/") + path
        cmd = f'curl -sk -o /dev/null -w "{url} → %{{http_code}}" "{url}"'
        results.append(run_cmd(cmd))
    return "\n".join(results)


def header_bypass(url):
    bypass_headers = [
        {"X-Forwarded-For": "127.0.0.1"},
        {"X-Original-URL": "/"},
        {"X-Rewrite-URL": "/"},
        {"X-Custom-IP-Authorization": "127.0.0.1"},
        {"X-Forwarded-Host": "localhost"},
    ]
    results = []
    for h in bypass_headers:
        header_str = " ".join([f'-H "{k}: {v}"' for k, v in h.items()])
        cmd = f'curl -sk -o /dev/null -w "{list(h.keys())[0]} → %{{http_code}}" {header_str} "{url}"'
        results.append(run_cmd(cmd))
    return "\n".join(results)


def s3_check(bucket_name):
    urls = [
        f"https://{bucket_name}.s3.amazonaws.com/",
        f"https://s3.amazonaws.com/{bucket_name}/",
    ]
    results = []
    for url in urls:
        cmd = f'curl -sk "{url}" | head -20'
        results.append(f"=== {url} ===\n{run_cmd(cmd)}")
    return "\n".join(results)


def graphql_introspect(url):
    payload = '{"query":"{__schema{types{name}}}"}'
    cmd = f'curl -sk -X POST "{url}" -H "Content-Type: application/json" -d \'{payload}\' | head -100'
    return run_cmd(cmd)


TOOL_MAP = {
    "curl_probe": curl_probe,
    "ssl_inspect": ssl_inspect,
    "subdomain_enum": subdomain_enum,
    "httpx_probe": httpx_probe,
    "dns_lookup": dns_lookup,
    "path_fuzz": path_fuzz,
    "header_bypass": header_bypass,
    "s3_check": s3_check,
    "graphql_introspect": graphql_introspect,
    "upload_probe": upload_probe,
}

def execute_tool(action, params):
    fn = TOOL_MAP.get(action)
    if not fn:
        return f"Unknown tool: {action}"
    try:
        return fn(**params)
    except TypeError as e:
        return f"(bad params for {action}: {e})"


def upload_probe(base_url):
    paths = [
        "/upload", "/api/upload", "/upload/file",
        "/api", "/health", "/status", "/ping",
        "/v1/upload", "/api/v1", "/api/v2",
    ]
    results = []
    for path in paths:
        url = base_url.rstrip("/") + path
        cmd = f'curl -sk -o /dev/null -w "{url} → %{{http_code}}" "{url}"'
        results.append(run_cmd(cmd))
    return "\n".join(results)
