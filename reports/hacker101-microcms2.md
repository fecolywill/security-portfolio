# Security Assessment — Hacker101 Micro-CMS v2

**Target:** Hacker101 CTF — Micro-CMS v2
**Canonical URL:** https://ctf.hacker101.com/ctf
**Assessment date:** 2026-09-27
**Researcher:** fecolywill
**Environment:** Termux on Android (no root), curl + Python
**Result:** 3 / 3 flags recovered

---

## Executive Summary

Micro-CMS v2 is a small Flask-based content management application. Assessment
identified **three distinct vulnerabilities** that together allow complete
application compromise by an unauthenticated attacker:

1. **SQL injection** in the login endpoint — enables authentication bypass and
   admin session forgery.
2. **Missing HTTP method authorization** on the page-edit endpoint — allows
   unauthenticated modification of any page.
3. **Blind credential extraction** via the same SQL injection — recovers the
   admin username and plaintext password.

Together these represent a complete failure of authentication and authorization
at the application layer.

---

## Scope and Methodology

**Scope:** Hacker101 CTF instance of Micro-CMS v2. Testing was performed against
a single authorized target only. No third-party infrastructure was touched. All
requests were rate-limited.

**Methodology:**

1. Passive reconnaissance — response headers, framework fingerprinting
2. Endpoint enumeration — ffuf, targeted path discovery
3. Authentication analysis — login form, session cookie structure
4. Injection testing — boolean-oracle SQL injection, union-based bypass
5. Authorization testing — HTTP method fuzzing on state-changing endpoints
6. Data extraction — custom blind SQL injection tooling (see `tools/blind-sqli.py`)

**Stack identified:** OpenResty reverse proxy in front of a Flask (Python)
application. Session cookies follow the `itsdangerous` URLSafeTimedSerializer
format: `base64(payload).base64(timestamp).base64(hmac-sha1)`.

---

## Finding 1 — SQL Injection in Login Endpoint (Critical)

**Endpoint:** `POST /login`
**Vulnerable parameter:** `username`
**Impact:** Full authentication bypass; admin session forgery

### Description

The `username` parameter is concatenated directly into a SQL query without
parameterization or escaping. A single quote in the username causes a database
error (HTTP 500), confirming injection.

Query structure, determined by probing:

```sql
SELECT <single_column> FROM <table> WHERE username = '<username>'

Column count was confirmed as 1 by ORDER BY escalation
(ORDER BY 1 → 200, ORDER BY 2 → 500). The password is checked separately in
application code — a quote in the password field causes no error, while a
quote in username crashes the server.

Proof of Concept

Confirm injection:

```
POST /login HTTP/1.1
Host: <target>
Content-Type: application/x-www-form-urlencoded

username=admin'&password=x

→ HTTP/1.1 500 Internal Server Error
```

Bypass authentication with UNION injection:

```
POST /login HTTP/1.1

username=' UNION SELECT 'hello'-- 
password=hello

→ HTTP/1.1 200 OK
Set-Cookie: l2session=<base64({"admin":true})>.<timestamp>.<hmac>; HttpOnly; Path=/
```

The resulting session cookie decodes to:

```json
{"admin": true}
```

This session grants access to admin-only resources, including private pages that
return HTTP 403 to anonymous users.

Impact

Any unauthenticated user can obtain a fully privileged admin session, then read
or modify any content on the application.

Remediation

· Use parameterized queries (prepared statements) for all database access.
· Never concatenate user input into SQL strings.
· Reject unexpected characters at the boundary as defense-in-depth, but never
  as a substitute for parameterization.

---

Finding 2 — Missing HTTP Method Authorization (High)

Endpoint: POST /page/edit/<id>
Impact: Unauthenticated write access to any page

Description

The /page/edit/<id> route enforces authorization on GET but not on
POST. An unauthenticated GET /page/edit/1 correctly redirects to /login,
but an unauthenticated POST /page/edit/1 is processed as if the request were
authorized.

This is a common bug class: developers wrap one HTTP method's handler in an
auth check and assume the route is protected, unaware that other methods route
to separate handlers.

Proof of Concept

```
POST /page/edit/1 HTTP/1.1

title=x&body=x

→ HTTP/1.1 200 OK
→ Response body: ^FLAG^...$FLAG$
```

The same behavior applies to every page ID tested (/page/edit/1,
/page/edit/2, /page/edit/3, and nonexistent IDs), confirming the
authorization check is entirely absent from the POST handler rather than
page-scoped.

Method behavior matrix (verified):

Method /page/create /page/edit/3
GET 302 (login) 302 (login)
POST 302 (login) 200 (processed)
PUT 405 405
DELETE 405 405
PATCH 405 405
OPTIONS 200 200
HEAD 302 302

Note POST /page/create is correctly gated while POST /page/edit/<id> is
not — authorization is inconsistent even within the same route family.

Related observation — XSS filter bypass

The page editor accepts HTML and filters only the literal string <script>
(case-sensitive), replacing it with <scrubbed>. The following payloads are not
filtered:

· <img src=x onerror="...">
· <SCRIPT>...</SCRIPT> (uppercase)
· <scr<SCRIPT>ipt>...</scr<SCRIPT>ipt> (nested)
· <svg onload="...">

Combined with the unauthenticated POST write above, this allows planting stored
XSS on any page without authenticating.

Impact

Any unauthenticated user can overwrite the title and body of any page on the
site — including pages they cannot even view (HTTP 403 on GET). Combined with
the XSS filter bypass, this enables stored XSS delivery to any site visitor.

Remediation

· Enforce authorization inside each handler, or apply the check to all
  HTTP methods for the route.
· Centralize authorization via middleware or a decorator wrapping every method
  of a protected route.
· For the XSS vector: use a vetted HTML sanitizer (bleach, DOMPurify server-side
  equivalent) rather than string replacement. Consider disallowing raw HTML
  input entirely.

---

Finding 3 — Credential Extraction via Blind SQL Injection (Critical)

Endpoint: POST /login (same injection point as Finding 1)
Impact: Recovery of admin username and password

Description

The login endpoint leaks data via a boolean oracle: the application returns
"Unknown user" when a query matches no row and "Invalid password" when a query
matches a row but fails the password check. Combined with the SQL injection,
this allows character-by-character extraction of arbitrary database values.

Extraction technique

Using SUBSTR and LENGTH (MySQL/MariaDB), each character can be recovered by
observing which of the two error strings is returned:

```
POST /login

username=' OR (SUBSTR((SELECT password FROM admins),1,1)='o')-- 
password=x

→ "Invalid password" (TRUE)  or  "Unknown user" (FALSE)
```

A custom Python tool (tools/blind-sqli.py) was written to automate extraction.
Schema was first enumerated via information_schema:

· Tables: admins, pages
· admins columns: id, username, password — 1 row
· pages columns: id, title, body, public — 3 rows

Extracted values:

· Admin username: tomas
· Admin password: odette (stored in plaintext)

Impact

Complete credential compromise. Passwords are stored in plaintext, so any
database read (including via this injection) yields immediately reusable
credentials.

Remediation

· Parameterize queries (same fix as Finding 1).
· Store passwords using a modern memory-hard hash: Argon2id, scrypt, or
  at minimum bcrypt with an appropriate cost factor. Never store plaintext
  or fast-hash (MD5, SHA-1, SHA-256) passwords.
· Return a single generic error message for all login failures
  ("Invalid username or password") to eliminate the boolean oracle.
· Implement rate limiting and account lockout on the login endpoint.

---

Additional Observations

1. User enumeration via error messages.
The login endpoint returns distinct messages for "Unknown user" and
"Invalid password", allowing enumeration of valid usernames.

2. Inconsistent input validation on login.
Submitting only password crashes the server (HTTP 500); submitting only
username returns HTTP 400. Inconsistent handling indicates missing required-
field validation.

3. Short session lifetime without refresh.
Sessions expire within minutes of issuance with no refresh mechanism, logging
legitimate users out mid-session.

---

Negative Findings (Tested, Not Vulnerable)

The following vectors were tested and did not yield exploitable behavior.
Documented for completeness and to demonstrate coverage.

Vector Result
Cookie signature bypass (payload tampering with valid signature) Rejected — HMAC verified correctly
Session secret cracking (common wordlist, 20 candidates) No match
Mass assignment on /page/edit/<id> (is_public, admin fields) Ignored by server
Source disclosure (.git/HEAD, .env, app.py, Dockerfile, etc.) All 404
Debug console (/console, /__debug__, /debug) All 404
HTTP header authentication (Authorization: Basic/Bearer, X-Admin) Ignored (403)
HTTP method bypass on /page/3 (POST/PUT/DELETE/PATCH/HEAD) Correctly rejected
Alternate endpoints (/admin, /api, /users, /page/list, etc.) All 404
Hidden pages beyond id 3 Only 3 rows exist in pages
Alternate public column values No non-0/1 values present

---

Chain Analysis

The vulnerabilities form a complete compromise chain:

```
Finding 1 (SQLi, auth bypass)     → Admin session forgery
Finding 3 (SQLi, data extraction) → Credential recovery (tomas / odette)
                                          ↓
                                  Full admin access
                                          ↓
Finding 2 (method bypass)         → Unauthenticated write to any page
                                          ↓
                                  + XSS filter bypass = stored XSS delivery
```

Each finding is independently exploitable. Together they demonstrate a complete
failure of authentication and authorization controls at the application layer.

---

Lessons and Methodology Notes

Verifying with a browser when a manual HTTP client behaves unexpectedly.
During credential validation, the login flow with recovered real credentials
(tomas / odette) appeared to fail via curl — HTTP 200 with no Set-Cookie
header captured — yet succeeded in a browser. The session cookie had been set on
a response that curl's cookie jar did not associate correctly with the request
flow. Lesson: when a manual HTTP client behaves inconsistently, verify with
a real browser before investing further in theoretical analysis. Browser
behavior is ground truth for authentication flows.

Method-based access control requires per-handler enforcement.
Authorization must be enforced per handler, not per route. HTTP method fuzzing
should be a standard step in any auth review, not an afterthought. In this
assessment, method fuzzing on /page/3 (view endpoint) yielded nothing — but
the same technique on /page/edit/<id> (write endpoint) found the bug
immediately. Test state-changing endpoints with every HTTP method.

Distinguishing 403 from 404.
A 403 response on a sequential ID is a strong signal that an object exists but
is forbidden — a candidate for authorization bypass. A 404 on the same family
means the object does not exist. Both look like failures, but only one leaks
information about server-side state.

Error messages as an oracle.
Distinct error messages for different failure modes ("Unknown user" vs
"Invalid password") are a vulnerability, not a feature. They enable user
enumeration and, combined with SQL injection, blind data extraction.

---

Tools and Artifacts

· tools/blind-sqli.py — custom boolean-based blind SQL injection
  extractor. Configurable endpoint, parameter, prefix/suffix, true/false
  strings, and charset. Includes retry logic, timeout handling, and rate
  limiting.
· curl — all HTTP interaction
· ffuf — endpoint enumeration
· Python 3 — blind extraction

---

Remediation Summary

Finding Priority Fix
SQL injection in login Critical Parameterized queries
Plaintext password storage Critical Argon2id / bcrypt hashing
Missing POST auth on edit High Centralized per-handler authorization
XSS filter bypass High Vetted HTML sanitizer or remove raw HTML support
User enumeration Medium Generic error messages
Login crash on missing field Low Input validation

---

Disclosure

This assessment was performed against the Hacker101 CTF, a public
educational platform operated by HackerOne. All testing was authorized by the
platform's terms. No production systems were targeted. All findings were
submitted via the platform's standard flag mechanism.

---

Report prepared by fecolywill. For assessment inquiries, see the portfolio
README.
