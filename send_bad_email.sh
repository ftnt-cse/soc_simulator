#!/bin/bash
emails=(asmith@fortielab.com dricardo@fortielab.com eis@fortielab.com masha@fortielab.com misha@fortielab.com phishing@fortielab.com sasha@fortielab.com sysadmin@fortielab.com)


sender=${emails[$RANDOM % ${#emails[@]} ]}

RAND=$(expr $RANDOM % 9999)

url=$(shuf -n 1 threat_intelligence/malicious_urls.txt)
dom=$(shuf -n 1 threat_intelligence/malicious_domains.txt)

swaks swaks --to Cheick.KOITA@orangemali.com --from "$RAND@$dom" --server 197.155.141.126 --body "$url"
