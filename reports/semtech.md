# Semtech.com — ExpressionEngine System Directory Exposure

**Author:** Okeke Godswill Ifeanyi  
**Date:** September 2026  
**Contact:** fecolywill@gmail.com  
**Severity:** Low (Information Disclosure)  
**Target:** https://www.semtech.com  
**Category:** CMS Security / Information Disclosure

---

## Summary

Semtech.com runs ExpressionEngine (PHP CMS) on Apache behind CloudFront and 
Cloudflare. The `/system/` directory is exposed, revealing the CMS 
architecture. Sensitive configuration files (`config.php`, `database.php`) 
exist but are protected with 403 responses.

## Target Overview

| Attribute | Value |
|-----------|-------|
| Primary IP | 149.97.171.6 |
| CDN | Amazon CloudFront |
| WAF | Cloudflare |
| Web Server | Apache |
| CMS | ExpressionEngine (PHP) |
| Load Balancer | AWS ELB |

## Methodology

1. DNS and subdomain enumeration.
2. HTTP header fingerprinting.
3. Directory and file enumeration.
4. JavaScript bundle analysis.
5. Historical reconnaissance via Wayback Machine.

## Findings

### 1. Exposed `/system/` Directory

The ExpressionEngine system directory is accessible. It should be 
protected at the web server level.

| Path | Status | Interpretation |
|------|--------|----------------|
| `/system/` | 301 | Directory exists, redirects to homepage |
| `/system/index.php` | 301 | Confirms CMS installation |
| `/system/config.php` | 403 | Config file exists, access denied |
| `/system/database.php` | 403 | Database config exists, access denied |
| `/system/user/` | 403 | User management directory exists |
| `/system/user/docs/` | 301 | Documentation directory exists |

**Impact:** Information disclosure. The existence of these paths 
confirms the CMS. If any of these files ever become accessible 
through a misconfiguration, database credentials could be leaked.

### 2. Directory Enumeration Results

| Path | Status |
|------|--------|
| `/themes/` | 403 (protected) |
| `/assets/` | 200 (accessible) |
| `/assets/uploads/` | 301 (exists) |
| `/admin/`, `/cp/`, `/login/` | 301 (redirects) |

## Conclusion

Semtech's ExpressionEngine installation has the system directory exposed, 
which is a configuration oversight. The sensitive files are protected with 
403 responses. Path traversal is blocked by CloudFront. No credentials 
or exploitable vulnerabilities were found.

## Recommendations

1. Block `/system/` at the web server level (return 404).
2. Ensure directory listing is disabled on all asset directories.
3. Review and update ExpressionEngine to the latest version.

## References

- ExpressionEngine Security: https://expressionengine.com/
- CWE-200: Exposure of Sensitive Information
