# My Reconnaissance Methodology

**Author:** Okeke Godswill Ifeanyi  
**Contact:** fecolywill@gmail.com

---

## Overview

This document describes my standard reconnaissance methodology for 
external black-box engagements. It is designed to be stealthy, 
methodical, and repeatable.

## Phase 1: Passive Reconnaissance

Goal: gather intelligence without touching the target.

### Commands

```bash
# DNS records via Google DNS-over-HTTPS (fast, no hangs)
curl -s "https://dns.google/resolve?name=target.com&type=ALL" | python -m json.tool

# Subdomain enumeration
for sub in www mail admin dev test api staging portal dashboard \
  login secure vpn app mobile shop store media cdn static files \
  ftp internal corp partner demo beta sandbox stage uat qa preprod \
  prod backup old intranet developer support help status; do
    curl -s "https://dns.google/resolve?name=$sub.target.com&type=A" | \
        python -c "import sys,json; d=json.load(sys.stdin); \
        ans=d.get('Answer',[]); print('$sub.target.com ->', \
        ans[0]['data'] if ans else 'NO IP')"
done
Tools

· dig — DNS enumeration
· curl — HTTP requests
· Google DNS-over-HTTPS API — fast, reliable DNS lookups
· Shodan — internet-wide scanning
· Wayback Machine — historical data
· GitHub — code search
· SecurityTrails / VirusTotal — subdomain discovery

Phase 2: Technology Fingerprinting

Goal: identify the web server, framework, WAF, and CMS.

curl -s -I https://target.com

What to look for

· Server: — web server type (IIS, Apache, Nginx)
· X-Powered-By: — framework (ASP.NET, PHP, Express)
· CF-RAY: — Cloudflare
· X-Cache: / Via: — CDN (CloudFront, Fastly, Akamai)
· Set-Cookie: — session management type
· Strict-Transport-Security — HTTPS enforcement

Phase 3: Active Enumeration

Goal: discover live endpoints and directories.

Directory Enumeration
for path in admin login dashboard account settings api cdn assets \
  static uploads files images css js; do
    curl -s -o /dev/null -w "$path -> %{http_code}\n" \
        "https://target.com/$path"
done


Phase 4: Vulnerability Probing

Goal: identify misconfigurations or weak points.

· Open Redirect: ?q=https://evil.com, ?redirect=, ?next=
· Reflected XSS: <script>alert(1)</script>, <img src=x onerror=>
· SSRF: ?url=http://169.254.169.254/, ?path=file:///etc/passwd
· Path traversal: /../, %2e%2e%2f
· Exposed files: /web.config, /.env, /.git/config, /trace.axd

Phase 5: Documentation

Every finding is documented with:

· Command used
· Raw output
· Interpretation
· Impact assessment
· Recommended remediation

OPSEC Notes

· Never scan production systems without authorization
· Use rate-limited scans to avoid detection
· Rotate IPs when possible (VPN, proxy, or residential)
· Never paste credentials into public chats or forums
· Always respect the target's disclosure policy

References

· OWASP Testing Guide
· PTES (Penetration Testing Execution Standard)
· HackerOne Disclosure Guidelines

```
