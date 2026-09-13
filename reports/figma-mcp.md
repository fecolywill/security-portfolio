# Figma MCP Server Exposure — Security Research Note

**Author:** Okeke Godswill Ifeanyi  
**Date:** September 13, 2026  
**Contact:** fecolywill@gmail.com  
**Severity:** Informational / Research Interest  
**Component:** Framelink Figma MCP Server (CVE-2025-53967)

---

## Summary
While conducting OSINT research on the Figma ecosystem, I identified 
an exposed instance of the Framelink Figma MCP Server accessible via 
the public internet. This server is known to be affected by 
CVE-2025-53967, a critical (CVSS 9.8) unauthenticated remote code 
execution vulnerability.

## Methodology

1. Reviewed Figma's public bug bounty program and disclosure policy.
2. Identified CVE-2025-53967 in the Framelink Figma MCP Server 
   (versions ≤ 0.6.3).
3. Used Shodan to search for internet-exposed instances of the server.
4. Analyzed the exposed service's HTTP headers and CORS configuration 
   without interacting with or exploiting the service.

## Findings

**Shodan Query:** `figma-mcp`  
**Results Found:** 1 exposed instance

| Attribute | Value |
|-----------|-------|
| Hosting Provider | Google LLC |
| Location | Council Bluffs, United States |
| Tags | `cloud`, `ai`, `mcp` |
| Exposed Headers | `Access-Control-Allow-Headers: Content-Type, Authorization, Accept, Mcp-Session-Id, Last-Event-Id, X-Figma-Access-Token` |

## Impact

An exposed MCP server running a vulnerable version could allow an 
unauthenticated attacker to execute arbitrary operating system 
commands on the host, per CVE-2025-53967. The presence of the 
`X-Figma-Access-Token` header indicates the server is configured 
to accept Figma authentication credentials.

**Important:** This instance is hosted on third-party infrastructure 
(Google Cloud) and is NOT within the scope of Figma's HackerOne 
program. No interaction was made with the service. This note is 
shared for educational and defensive purposes only.

## Recommendations

1. Organizations running the Framelink Figma MCP Server should 
   upgrade to version 0.6.4 or later immediately.
2. MCP servers should never be exposed to the public internet 
   without authentication and network-level access controls.
3. Conduct regular external attack surface assessments to identify 
   unauthorized exposed services.

## References

- CVE-2025-53967 — https://nvd.nist.gov/vuln/detail/CVE-2025-53967
- Figma HackerOne Program — https://hackerone.com/figma
- Figma security.txt — https://www.figma.com/.well-known/security.txt
