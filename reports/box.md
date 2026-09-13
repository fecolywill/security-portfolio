# Box.com — OAuth Metadata & Module Federation Exposure

**Author:** Okeke Godswill Ifeanyi  
**Date:** September 2026  
**Contact:** fecolywill@gmail.com  
**Severity:** Informational (Information Disclosure)  
**Target:** https://www.box.com  
**Category:** Cloud Security / OAuth 2.0 Analysis

---

## Summary

Box.com is a well-secured enterprise SaaS platform. Reconnaissance revealed 
several information disclosures including an exposed OAuth 2.0 Authorization 
Server Metadata endpoint and a Webpack Module Federation configuration 
leaking internal microservice versions.

## Target Overview

| Attribute | Value |
|-----------|-------|
| Primary IP | 74.112.186.157 |
| CDN/WAF | Cloudflare |
| DNS Security | DNSSEC enabled |
| Auth Service | Auth0 (tenant: lora-dev-portal) |

## Subdomains Identified

Live subdomains discovered during enumeration:

| Subdomain | Purpose |
|-----------|---------|
| `www.box.com` | Main marketing site |
| `account.box.com` | Authentication service |
| `api.box.com` | REST API |
| `app.box.com` | Main application |
| `admin.box.com` | Admin panel (redirects) |
| `developer.box.com` | Developer portal |
| `support.box.com` | Zendesk support |
| `ftp.box.com` | FTP service (secured) |

## Methodology

1. Passive DNS enumeration via Google DNS-over-HTTPS API.
2. HTTP header fingerprinting on all subdomains.
3. OAuth 2.0 discovery via `/.well-known/` endpoints.
4. JavaScript source code analysis for architecture mapping.
5. Module Federation configuration extraction.

## Findings

### 1. OAuth 2.0 Authorization Server Metadata Exposed

**Endpoint:** `https://account.box.com/.well-known/oauth-authorization-server`

**Disclosed Data:**
- Issuer: `https://api.box.com`
- Authorization endpoint: `https://account.box.com/api/oauth2/authorize`
- Token endpoint: `https://api.box.com/oauth2/token`
- Supported grant types: `authorization_code`, `refresh_token`
- PKCE required: `S256`

**Impact:** Informational. This metadata is standard OAuth 2.0 discovery 
per RFC 8414. Not a vulnerability, but confirms the authentication 
architecture.

### 2. Module Federation Configuration Exposure

**File:** `https://cdn01.boxcdn.net/sign-assets/box_sign_client_remote.2.428.7.js`

**Disclosed Data:**
- Internal microservice versions (box_canvas, box_sign_client, box_forms_client, etc.)
- Module Federation runtime configuration
- Shared dependency versions

**Impact:** Low. Attackers can use version information for targeted attacks 
against specific microservice versions. However, no credentials or 
exploitable code paths were disclosed.

### 3. Client ID Not Disclosed

The OAuth `client_id` is not hardcoded in any public JavaScript file 
analyzed, indicating a secure configuration.

## Conclusion

Box.com demonstrates a mature, enterprise-grade security posture. The 
findings are informational only and do not represent exploitable 
vulnerabilities. The OAuth metadata and Module Federation configuration 
exposures are standard for modern web platforms.

## References

- RFC 8414: OAuth 2.0 Authorization Server Metadata
- Module Federation: https://module-federation.io
