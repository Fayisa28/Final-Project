"""Extract the real vacancies and stock-exchange-listed companies from job-hunter-africa.html
into data/jobs.json and data/listed_companies.json (used by the AI agents' tools).
Run:  python3 scripts/extract_data.py"""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "job-hunter-africa.html").read_text(encoding="utf-8")
def grab(name):
    m = re.search(r"const " + name + r"=(\[.*?\]);\n", html, re.S)
    return json.loads(m.group(1))
jobs = grab("REAL")
for i, j in enumerate(jobs): j["id"] = 100 + i
listed = grab("LISTED")
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data/jobs.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
(ROOT / "data/listed_companies.json").write_text(json.dumps(listed, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"jobs: {len(jobs)}  exchanges: {len(listed)}  listed companies: {sum(len(x['rows']) for x in listed)}")
