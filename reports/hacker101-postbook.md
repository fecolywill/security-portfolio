# Hacker101 CTF — Postbook (Web, Easy) — 7/7 Flags

**Target:** Postbook (Hacker101 CTF instance)
**Date:** September 2026
**Result:** 7/7 flags found — 29/26 total Hacker101 points earned
**Achievement:** Crossed the 26-point threshold for private program invitations

---

## Executive Summary

Postbook is a deliberately vulnerable "social diary" web application hosted on Hacker101's CTF platform. Testing revealed **7 distinct vulnerability classes** across the application, all chained from the same root causes: **broken access control, unsalted MD5 identifiers, and missing session integrity checks**.

Every flag was found through methodical testing — no guessing, no automated scanners. Each flag taught a different real-world bug class.

---

## Flag-by-Flag Breakdown

### Flag 0 — Weak Credentials
**Hint:** *"The person with username 'user' has a very easy password..."*

**Bug class:** CWE-521 — Weak Password Requirements
**Root cause:** The `user` account was created with the password `password`.
**Exploit:** Iterated a short common-password wordlist against `user` via the sign-in form. The password `password` returned HTTP 302 (successful login).
**Real-world impact:** Weak/default credentials remain the #1 initial access vector in breach reports.
**Fix:** Enforce password complexity, block known-weak passwords at registration.

---

### Flag 1 — IDOR (Read)
**Hint:** *"Try viewing your own post and then see if you can change the ID"*

**Bug class:** CWE-639 — Authorization Bypass Through User-Controlled Key
**Root cause:** `view.php?id=<N>` does not verify that the requested post belongs to the authenticated user.
**Exploit:** Changed `id=3` (own post) to `id=2` (admin's private post) and read the flag.
**Real-world impact:** User data exposure — reading other users' private content.
**Fix:** Verify session ownership before serving any object.

---

### Flag 2 — HTTP Parameter Pollution
**Hint:** *"You should definitely use 'Inspect Element' on the form when creating a new post"*

**Bug class:** CWE-235 — Improper Handling of Extra Parameters (HTTP Parameter Pollution)
**Root cause:** The create-post form takes a hidden `user_id` field. Sending `user_id=3&user_id=1` caused Postbook to detect the anomaly and drop the flag into the redirect `message` parameter.
**Exploit:**
The flag appeared in the `location:` header.
**Real-world impact:** HPP bypasses WAF rules, authorization checks, and cache integrity in production apps.
**Fix:** Reject requests with duplicate parameter names, or normalize to a single value.

---

### Flag 3 — Predictable Object ID (Arithmetic Hint)
**Hint:** *"189 * 5"*

**Bug class:** CWE-639 — Predictable Object Identifier
**Root cause:** A hidden post exists at ID 945 (189 × 5), discoverable only by computing the arithmetic hint.
**Exploit:** `view.php?id=945` returned a post containing the flag.
**Real-world impact:** Sequential / predictable IDs let attackers enumerate hidden objects (invoices, messages, files).
**Fix:** Use UUIDv4 or cryptographically random object identifiers.

---

### Flag 4 — IDOR (Write/Edit)
**Hint:** *"You can edit your own posts, what about someone else's?"*

**Bug class:** CWE-639 — Authorization Bypass on Write Operation
**Root cause:** `edit.php?id=<N>` does not verify post ownership.
**Exploit:** Loaded `edit.php?id=2` (admin's private post), unchecked the "private" checkbox, saved. Flag rendered in the success banner.
**Real-world impact:** Write-capable IDOR is more severe than read-only — enables defacement and data tampering.
**Fix:** Enforce server-side ownership checks on all state-changing operations.

---

### Flag 5 — Cookie Forgery via Unsalted MD5
**Hint:** *"The cookie allows you to stay signed in. Can you figure out how they work so you can sign in to user with ID 1?"*

**Bug class:** CWE-565 — Reliance on Cookies without Validation and Integrity Checking
**Root cause:** Session cookie is `id=md5(user_id)`. MD5 is fast, unsalted, and reversible by brute force over a tiny keyspace.
**Exploit:**
Flag rendered on admin's home page.
**Real-world impact:** Complete account takeover — forge any user's session.
**Fix:** Use cryptographically random session tokens (≥128 bits), never derive them from IDs.

---

### Flag 6 — Broken Access Control on Delete
**Hint:** *"Deleting a post seems to take an ID that is not a number. Can you figure out what it is?"*

**Bug class:** CWE-639 — Missing Authorization on Destructive Action
**Root cause:** `delete.php?id=<md5(post_id)>` does not verify post ownership or session identity. Any authenticated user can delete any post by computing its MD5 hash.
**Exploit:**
Flag appeared in the redirect `message` parameter.
**Real-world impact:** Destructive IDOR — attackers delete arbitrary user content.
**Fix:** Authorization check on session user, not just object ID lookup.

---

## Methodology Summary

1. **Enumerate the app** — discover all endpoints and parameters via source inspection and curl
2. **Bootstrap a curl session** — sign up via POST, save cookie jar, reuse with `-b`/`-c`
3. **Read every form's source** — hidden fields (`user_id`), missing CSRF tokens, action URLs
4. **Test parameter pollution** — send duplicate keys (`user_id=3&user_id=1`)
5. **Identify hash patterns** — compare cookie/ID values against MD5 of known inputs
6. **Forge and exploit** — compute MD5 of target IDs, use them directly
7. **Always grep the redirect** — flags frequently appear in `location:` headers, not the page body

---

## Key Takeaways

- **Obfuscation is not security.** MD5-hashing IDs doesn't stop anyone — the hash is trivially computable.
- **Access control must be enforced server-side, on every endpoint.** Reading, editing, and deleting each need their own check.
- **Redirects leak.** Flags (and in real apps, tokens and errors) often land in `Location:` headers.
- **Compound vulnerability chains** turn low-severity bugs into high-severity impact — IDOR + cookie forgery = full admin takeover.

---

## Tools Used

- `curl` (with cookie jar persistence)
- `md5sum`
- Manual source inspection via `view-source:` (Android Chrome)
- Chrome Netlog (`chrome://net-export`) for capturing session cookies
- Hacker101 CTF platform hints

---

*Report authored by Okeke Godswill Ifeanyi — github.com/fecolywill*
