# Okeke Godswill Ifeanyi — Security Research Portfolio

## About Me
I am an independent security researcher focused on **web application security**, **access control vulnerabilities**, **authentication bypass**, and **reconnaissance**. I use tools like `curl`, `nmap`, `ffuf`, `nuclei`, `shodan`, and custom scripting to map attack surfaces and identify exploitable misconfigurations.

I document every finding — including negative results — because methodology matters more than luck.

## Research Interests
- Web Application Security (OWASP Top 10)
- Broken Access Control (IDOR, privilege escalation)
- Authentication & Session Security
- WAF Bypass Techniques
- OSINT & Reconnaissance
- CTF & Hands-On Labs (Hacker101)

## Hacker101 CTF Progress

**Total Points: 29/26** — Crossed the threshold for **private program invitations**

| Challenge | Difficulty | Flags | Skills |
|---|---|---|---|
| A little something to get you started | Trivial | 1/1 | Content-type analysis |
| **Postbook** | Easy | **7/7** | IDOR, HPP, cookie forgery, weak credentials, broken access control |

*Full Postbook writeup: [reports/hacker101-postbook.md](./reports/hacker101-postbook.md)*

## Portfolio Contents

### 1. Reports
- [Hacker101 — Postbook (7/7 flags)](./reports/hacker101-postbook.md) — IDOR, HTTP Parameter Pollution, MD5 cookie forgery, weak credentials, broken access control on delete
- [Essity.com — Attack Surface Analysis](./reports/essity.md)
- [Box.com — OAuth & Subdomain Enumeration](./reports/box.md)
- [Semtech.com — ExpressionEngine Exposure Analysis](./reports/semtech.md)
- [CLEAR.me — Third-Party Service Analysis](./reports/clearme.md)
- [Figma — Exposed MCP Server Discovery](./reports/figma-mcp.md)

### 2. Methodology Notes
- [Recon Methodology](./methodology/recon.md)
- [WAF Bypass Notes](./methodology/waf-bypass.md)
- [Bootstrapping Authenticated curl Sessions](./methodology/curl-sessions.md)
- [Shodan Query Library](./methodology/shodan.md)

### 3. Tools & Scripts
- [session-exploit.sh — Session / IDOR / Hash-Forgery Helper](./tools/session-exploit.sh)
- [recon.sh — Automated Subdomain Enumeration](./tools/recon.sh)
- [dns-quick.sh — Fast DNS Lookup via Google API](./tools/dns-quick.sh)

## Approach

1. **Recon** — enumerate subdomains, endpoints, parameters, and technologies
2. **Map** — read every form, hidden field, and URL parameter
3. **Probe** — test parameter pollution, IDOR, auth boundaries, and session handling
4. **Chain** — combine low-severity findings into high-impact exploits
5. **Document** — write up every finding, including negatives, in this portfolio

## Contact

- **Email:** fecolywill@gmail.com
- **WhatsApp:** +234 808 420 4679
- **GitHub:** [github.com/fecolywill](https://github.com/fecolywill)
- **HackerOne:** [hackerone.com/fecolywill](https://hackerone.com/fecolywill)
