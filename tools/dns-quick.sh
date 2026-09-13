#!/bin/bash
# dns-quick.sh — Fast DNS lookup using Google's DNS-over-HTTPS API
# Author: Okeke Godswill Ifeanyi
# Usage: ./dns-quick.sh <domain> [subdomain1 subdomain2 ...]

DOMAIN=$1
shift
SUBS=("$@")

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain> [subdomains...]"
    exit 1
fi

echo "=== Base DNS Records for $DOMAIN ==="
for type in A MX NS TXT; do
    echo -n "$type: "
    curl -s "https://dns.google/resolve?name=$DOMAIN&type=$type" | \
        python3 -c "import sys,json; d=json.load(sys.stdin); [print(a['data']) for a in d.get('Answer',[])]"
done

if [ ${#SUBS[@]} -gt 0 ]; then
    echo -e "\n=== Subdomain Enumeration ==="
    for sub in "${SUBS[@]}"; do
        curl -s "https://dns.google/resolve?name=$sub.$DOMAIN&type=A" | \
            python3 -c "import sys,json; d=json.load(sys.stdin); ans=d.get('Answer',[]); print('$sub.$DOMAIN ->', ans[0]['data'] if ans else 'NO IP')"
    done
fi
