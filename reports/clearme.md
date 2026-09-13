# CLEAR.me — Third-Party Service & Webflow Analysis

**Author:** Okeke Godswill Ifeanyi  
**Date:** September 2026  
**Contact:** fecolywill@gmail.com  
**Severity:** Informational  
**Target:** https://www.clearme.com  
**Category:** Attack Surface Analysis

---

## Summary

CLEAR.me is a marketing site built on Webflow and protected by Cloudflare. 
The site itself is a static front-end with no exposed admin panels or input 
vectors. Reconnaissance identified multiple third-party services loaded 
into the page, including Intellimize (personalization), OneTrust (cookie 
consent), and TFA Forms (form service).

## Target Overview

| Attribute | Value |
|-----------|-------|
| Primary IPs | 104.18.32.150, 172.64.155.106 |
| CDN/WAF | Cloudflare |
| Platform | Webflow |
| Personalization | Intellimize |
| Forms | TFA Forms (Form Assembly) |
| Consent Management | OneTrust |

## Methodology

1. DNS and subdomain enumeration.
2. HTTP header fingerprinting and CDN identification.
3. JavaScript source analysis of third-party scripts.
4. Directory and path enumeration.
5. Analysis of the Intellimize personalization configuration.

## Findings

### 1. Webflow-Based Static Site

The site is built on Webflow (no-code CMS). All paths return 404 except 
for the root, confirming a static deployment with no traditional 
directory structure.

| Path | Status |
|------|--------|
| `/admin`, `/login`, `/dashboard` | 404 |
| `/api`, `/cdn`, `/assets` | 404 |
| `/uploads`, `/files` | 404 |
| `/images`, `/css`, `/js` | 000 (connection reset — served via CDN) |

### 2. Third-Party Service Analysis

**Intellimize Configuration** (via `cdn.intellimize.co/snippet/117236205.js`):
- Reveals A/B testing campaigns and audience targeting
- Lists DMA (Designated Market Area) codes for targeting
- Exposes `webflowSiteId: 646a6ec3f634076bc7bf77f2`

**Impact:** Informational. Exposes marketing logic but no credentials 
or exploitable endpoints.

### 3. No Exposed Subdomains

Only `www.clearme.com` resolves via DNS. Authentication and user 
management services are not publicly exposed.

## Conclusion

CLEAR.me has a clean, static Webflow deployment with strong Cloudflare 
protection. No exploitable vulnerabilities were identified. The 
third-party service integrations are standard for a modern marketing site.

## Recommendations

1. Continue monitoring third-party scripts for supply chain risks.
2. Ensure Intellimize's webflowSiteId cannot be abused for unauthorized 
   content injection.

## References

- Webflow Security
- Intellimize Documentation
