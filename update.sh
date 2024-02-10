#!/bin/bash
python3 data.py
curl -H 'Cache-Control: no-cache, no-store' localhost:5000 >> index.html
mv index.html ../r-doener.github.io/
cd ../r-doener.github.io/
git commit -a -m "automatic update"
git push
