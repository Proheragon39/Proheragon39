"""Re-check that a lead's website is really dead right before writing to them.

Usage: python3 dnscheck.py urls.txt
urls.txt: one "<row>|<url>" per line (row = spreadsheet row number).

Uses Google DNS-over-HTTPS as an independent resolver, so a sandbox/local DNS
quirk is not mistaken for a dead site, then tries the page over HTTP.
"""
import json, re, sys, urllib.request

STATUS = {0: "OK", 2: "SERVFAIL", 3: "NXDOMAIN"}


def dns(host):
    url = f"https://dns.google/resolve?name={host}&type=A"
    try:
        d = json.load(urllib.request.urlopen(url, timeout=15))
    except Exception as e:  # network error is not proof the site is dead
        return f"DNS-ERR {e.__class__.__name__}", []
    return STATUS.get(d["Status"], str(d["Status"])), [a["data"] for a in d.get("Answer", [])]


def http(url):
    if not re.match(r"https?://", url):
        url = "http://" + url
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        r = urllib.request.urlopen(req, timeout=20)
        body = r.read(20000).decode("utf-8", "ignore")
        title = re.search(r"<title>([^<]*)", body, re.I)
        return r.status, title.group(1).strip() if title else ""
    except urllib.error.HTTPError as e:
        body = e.read(20000).decode("utf-8", "ignore")
        title = re.search(r"<title>([^<]*)", body, re.I)
        return e.code, title.group(1).strip() if title else ""
    except Exception as e:
        return 0, e.__class__.__name__


for line in open(sys.argv[1]):
    if "|" not in line:
        continue
    row, url = line.strip().split("|", 1)
    host = re.sub(r"^https?://", "", url).split("/")[0].lower()
    st, ans = dns(host)
    code, title = http(url) if st == "OK" and ans else (0, "")
    alive = st == "OK" and ans and 200 <= code < 400 and "error" not in title.lower()
    verdict = "ALIVE - do not say 'site is down'" if alive else "DEAD"
    print(f"{row}\t{host}\t{st}\t{code}\t{title[:50]}\t{verdict}")
