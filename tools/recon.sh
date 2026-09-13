#!/bin/bash
# recon.sh — Comprehensive Recon Script
# Author: Okeke Godswill Ifeanyi
# Usage: ./recon.sh <domain>

DOMAIN=$1

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

echo "=========================================="
echo "  Reconnaissance Report: $DOMAIN"
echo "  By: Okeke Godswill Ifeanyi"
echo "=========================================="

echo -e "\n[1] Basic DNS Records"
for type in A MX NS TXT; do
    echo -n "  $type: "
    curl -s "https://dns.google/resolve?name=$DOMAIN&type=$type" | \
        python3 -c "import sys,json; d=json.load(sys.stdin); [print('   '+a['data']) for a in d.get('Answer',[])]"
done

echo -e "\n[2] HTTP Headers"
curl -s -I "https://$DOMAIN" | head -20

echo -e "\n[3] Subdomain Enumeration"
for sub in www mail admin dev test api staging portal dashboard \
  login secure vpn app mobile; do
    result=$(curl -s "https://dns.google/resolve?name=$sub.$DOMAIN&type=A" | \
        python3 -c "import sys,json; d=json.load(sys.stdin); \
        ans=d.get('Answer',[]); print(ans[0]['data'] if ans else '')")
    [ ! -z "$result" ] && echo "  $sub.$DOMAIN -> $result"
done

echo -e "\n[4] Common Path Enumeration"
for path in admin login dashboard api assets uploads files; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/$path")
    echo "  /$path -> $code"
done

echo -e "\n[5] Security Headers Check"
headers=$(curl -s -I "https://$DOMAIN")
for h in strict-transport-security x-frame-options \
         x-content-type-options content-security-policy; do
    if echo "$headers" | grep -qi "$h"; then
        echo "  [+] $h: present"
    else
        echo "  [-] $h: MISSING"
    fi
done

echo -e "\n=========================================="
echo "  Recon Complete"
echo "=========================================="
