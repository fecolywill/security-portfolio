# Methodology: Bootstrapping an Authenticated curl Session

When a target uses session-based auth, `curl` is dramatically faster than a browser for enumeration. This note documents the process for reliably establishing an authenticated curl session, including the failure modes I hit and how I solved them.

---

## The Basic Pattern

```bash
# 1. GET the login page to establish any pre-auth state
curl -sS -c ~/sess.txt -o /dev/null "https://target/index.php?page=sign_in.php"

# 2. POST credentials, saving the resulting session cookie
curl -sS -b ~/sess.txt -c ~/sess.txt \
  -X POST "https://target/index.php?page=sign_in.php" \
  --data "username=USER&password=PASS"

# 3. Verify auth by hitting a protected page
curl -sS -b ~/sess.txt "https://target/index.php?page=account.php" | grep -i "logout\|account\|sign out"
```

The -c flag writes cookies to the jar, -b reads them. Together they maintain session state across requests.

---

Failure Mode 1 — Special Characters in Passwords

Password Hunter!123! failed repeatedly. Root cause: the shell was mangling the ! character (history expansion) before curl ever saw it.

Fixes:

· URL-encode special chars: ! → %21, + → %2B, @ → %40
· Or change the account password to something without shell-special characters during testing (in a CTF context)
· Or wrap the data in single quotes: --data 'password=Hunter!123!'

---

Failure Mode 2 — Login Returns 200 Instead of 302

A 200 response with "wrong username" means the credentials weren't accepted.
A 302 response means success (redirect after login).

Always check status codes, not just the response body:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" -X POST ...
```

---

Failure Mode 3 — App Doesn't Use Cookies at All

Some apps use HTTP headers, URL tokens, or a platform-layer session instead of an app-level cookie.

Example: Hacker101 CTF challenges use a .hacker101.com-scoped _ctf_session cookie at the platform level. The individual challenge app (Postbook) uses a separate app-level cookie (id=md5(user_id)).

Diagnostic: Log in, then dump the cookie jar:

```bash
cat ~/sess.txt
```

If the jar is empty but you're authenticated, the app is using something other than cookies — check request/response headers for Authorization:, X-Session-, or custom tokens.

---

Failure Mode 4 — No Cookie Visible in Browser

Android Chrome's cookie viewer often shows "0 B stored data" even when cookies exist. To verify what cookies the browser is actually sending:

Option A — Chrome Netlog:

1. Navigate to chrome://net-export/
2. Tap "Start Logging to Disk" → save to Downloads
3. Perform the login in another tab
4. Stop logging
5. In Termux:

```bash
grep -oE '_ctf_session=[^;"]{1,200}' ~/downloads/netlog.json | sort -u
grep -oE '"[Cc]ookie[^"]{0,250}' ~/downloads/netlog.json | grep -i "session\|auth" | head
```

Option B — Just use curl from scratch. Don't try to extract browser cookies. Re-authenticate via curl directly.

---

Failure Mode 5 — Session Expires Between Sessions

Hacker101 CTF instances auto-terminate after inactivity. If curl returns 404 on every request, the instance is dead — check in the browser first.

Also: captured session tokens rotate. A cookie from a netlog two hours ago is likely expired.

---

Verification Checklist

Before running any exploit, confirm auth works:

```bash
curl -sS -b ~/sess.txt "https://target/protected-page" \
  | grep -iE "sign out|logout|welcome|username"
```

· "Sign out" or username present → authenticated, proceed
· "Sign in" or login form → session invalid, redo login

---

Key Lessons

1. Always use cookie jars — -c and -b together, every time.
2. URL-encode special characters in passwords and payloads.
3. Check status codes — 302 = success, 200 = often failure with a body.
4. Verify auth before exploiting — a single check saves minutes of confusion.
5. If curl auth fails 3 times, stop and diagnose — don't keep retrying blindly.

---

Methodology note by Okeke Godswill Ifeanyi — github.com/fecolywill
