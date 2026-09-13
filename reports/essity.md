# Essity.com — Akamai WAF Analysis & Open Redirect

**Author:** Okeke Godswill Ifeanyi  
**Date:** September 2026  
**Contact:** fecolywill@gmail.com  
**Severity:** Low (Open Redirect)  
**Target:** https://www.essity.com  
**Category:** Web Application Security / WAF Analysis

---

## Summary

Essity.com is protected by an enterprise-grade Akamai WAF. During testing, 
the primary finding was an Open Redirect via the search parameter (`q`). 
Extensive attempts at reflected XSS, HTML injection, and SQL injection 
were blocked by Akamai's WAF with well-configured filtering.

## Target Overview

| Attribute | Value |
|-----------|-------|
| Primary IP | 52.142.123.60 |
| CDN/WAF | Akamai |
| Web Server | Microsoft-IIS/10.0 |
| Framework | ASP.NET |
| Mail Provider | Office 365 (MX records) |

## Methodology

1. Passive reconnaissance: `dig`, DNS enumeration, subdomain discovery.
2. WAF fingerprinting via HTTP headers and error page analysis.
3. Character fuzzing to identify allowed vs. blocked input characters.
4. Manual payload testing for XSS, HTML injection, and Open Redirect.
5. Akamai WAF bypass attempts using custom obfuscated payloads.

## Findings

### 1. Open Redirect (Confirmed)

**Parameter:** `q` on `https://www.essity.com/search`  
**Payload:** `https://evil.com`

**Proof of Concept:**
https://www.essity.com/search?q=https://evil.com

The URL is reflected in an anchor tag on the search results page. When 
clicked, the user is redirected to the external domain.

**Impact:** Phishing, credential harvesting, redirection to malicious sites.

**CWE:** CWE-601 (URL Redirection to Untrusted Site)

### 2. WAF Analysis

Akamai successfully blocked:
- `<script>` tags
- Event handlers (`onerror`, `onmouseover`, `onload`)
- `<h1>` and generic HTML tags
- `javascript:` protocol (URL-encoded in response)
- SQL injection patterns
- Path traversal attempts

Allowed but encoded characters: `<`, `>`, `"`, `'`  
Connection reset triggered by: `&`

## Conclusion

Essity's Akamai WAF is well-configured. The only confirmed finding is a 
low-severity Open Redirect that could be chained with social engineering.

## References

- CWE-601: https://cwe.mit.edu/data/definitions/601.html
- Akamai WAF Documentation

