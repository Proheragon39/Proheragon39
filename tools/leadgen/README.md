# Lead generation scripts (Georgia)

Pipeline that builds a list of local businesses that need a website and drafts outreach messages.
Lead data itself is NOT committed (third-party contact data); it lives in Google Sheets.

1. Download OSM extract: `curl -o leads/georgia.osm.pbf https://download.openstreetmap.fr/extracts/asia/georgia-latest.osm.pbf`
2. `python3 extract.py leads/georgia.osm.pbf leads/pois.json` (needs `pip install osmium`)
3. `python3 check.py leads/pois.json leads/pois_checked.json` (filters occupied territories, checks sites)
4. `node recheck.js leads/pois_checked.json leads/pois_checked2.json` (re-checks "dead" sites in Chromium)
5. Remove chains -> `leads/pois_final.json` (see chain regex used in session), then
   `python3 segment.py leads/pois_final.json leads/leads_all.csv`
6. `python3 drafts.py leads/leads_all.csv leads/leads_georgia.csv` (email drafts + WhatsApp links)

Before each outreach wave: `python3 dnscheck.py urls.txt` re-checks that sites are still dead.
Run drafts with `SENDER_NAME=... SENDER_NAME_RU=... SENDER_WHATSAPP=... python3 drafts.py ...` (not committed).
The whole workflow ("План А") is in [PLAN_A.md](PLAN_A.md).
