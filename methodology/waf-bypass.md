# WAF Bypass Notes

**Author:** Okeke Godswill Ifeanyi  
**Contact:** fecolywill@gmail.com

---

## Overview

Notes and observations from testing against modern WAFs 
(Akamai, Cloudflare, AWS WAF) in 2026.

## Common WAF Signatures

| Signature | Blocked By | Bypass Approach |
|-----------|-----------|-----------------|
| `<script>` | All major WAFs | Use `<img>`, `<svg>`, `<body>` |
| `onerror=` | Akamai, Cloudflare | Use reflection APIs |
| `javascript:` | All | Use data URIs, base64 |
| `<h1>` | Akamai | WAF strips all HTML tags |
| `&` | Akamai (connection reset) | Encode as `%26`, avoid in payloads |

## Akamai-Specific Notes

Akamai uses multiple detection layers:
1. **IP reputation** — datacenter IPs flagged
2. **TLS fingerprinting (JA3)** — real browsers required
3. **HTTP header validation** — headers must be consistent
4. **JavaScript challenge** — sensor data required
5. **Behavioral analysis** — pattern detection

### Bypass Strategy
- Use a real browser (SeleniumBase with undetected-chromedriver)
- Rotate TLS fingerprints
- Send complete, ordered headers
- Solve JS challenges via headless browser
- Vary request timing

### Character Fuzzing Template

```python
import requests

chars = ['<', '>', '"', "'", '/', ';', '(', ')', '&', '#',
         '{', '}', '[', ']', '=', '`', '\\', '|', '+', '-', '*', '%']

for c in chars:
    try:
        r = requests.get('https://target.com/search?q=' + c)
        print(f'{"Reflected" if c in r.text else "Blocked"}: {c}')
    except Exception as e:
        print(f'Error: {c} — {e}')
Cloudflare-Specific Notes

· Blocks based on cf-ray header correlation
· Uses __cf_bm cookie for challenge tracking
· Rate-limits by IP + fingerprint

Bypass Strategy

· Solve the JS challenge via headless browser
· Preserve the cf_clearance cookie
· Use residential proxies

Payload Obfuscation Techniques

1. Case variation: <ScRiPt>
2. HTML entities: &lt;script&gt;
3. Unicode escapes: \u003cscript\u003e
4. Base64 encoding: <img src=x onerror=eval(atob('YWxlcnQoMSk='))>
5. Reflection API: Reflect.get(frames,'ale'+'rt')
6. Fragment splitting: <scr + ipt>

Detection Evasion

· Randomize User-Agent
· Add realistic Referer headers
· Send Accept-Language and Accept-Encoding
· Mimic browser Connection: keep-alive
· Throttle requests (1 every 3–10 seconds)

Ethical Reminder

Only test systems you own or have explicit written permission to test. 
Follow HackerOne and vendor disclosure policies strictly.

References

· PortSwigger WAF Bypass Research
· Akamai Security Blog
· Cloudflare WAF Documentation
· OWASP WAF Bypass Cheat Sheet

```

