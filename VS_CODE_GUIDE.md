# Job Hunter Africa — VS Code build guide

Everything you need to get the AI agent app running in VS Code and finish your final project.
Do the parts **in order**. Paste each prompt into your AI assistant in VS Code (GitHub Copilot Chat in **Agent** mode, or the Claude Code extension) and let it finish before the next one.

---

## Part A — Set up (15 minutes, no prompts)

1. **Install** (skip what you have):
   - VS Code — https://code.visualstudio.com
   - Python 3.10+ — https://www.python.org/downloads (on Windows tick "Add Python to PATH")
   - Git — https://git-scm.com/downloads
   - In VS Code, install extensions: **Python** and **GitHub Copilot Chat** (or **Claude Code**)
2. **Unzip** `job-hunter-africa-app.zip` somewhere easy, e.g. `Documents/job-hunter-africa-app`.
3. In VS Code: **File → Open Folder…** → choose `job-hunter-africa-app`.
4. **Create your key file**: right-click `.env.example` → Copy → Paste → rename the copy to **`.env`**. Open it and fill in:
   ```
   PORTKEY_API_KEY=your-course-key-here
   MODEL=gpt-6-luna
   OWNER_EMAIL=thejobhuntergh@gmail.com
   OWNER_PASSWORD=pick-a-strong-password
   ```
   (Leave the SMTP lines empty for now — codes will show in the terminal.)
5. **Run it**: Terminal → New Terminal, then type:
   ```
   python3 jobhunter_server.py
   ```
   (Windows: `python jobhunter_server.py`). Open **http://localhost:8000**.
6. **Run the tests**: open a second terminal and type `python3 -m unittest discover -s tests -v` → you should see `OK`.

If anything fails, paste the error into your AI assistant with: *"I got this error running the app. Fix it."*

---

## Part B — The prompts (paste one at a time)

### Prompt 1 — Understand and check the project
```
You are helping me finish my final project: "Job Hunter Africa", an AI career agent app for job seekers in Ghana and across Africa.
Read README.md, jobhunter_server.py (Python standard-library server: accounts, email codes, the Fayisa AI agent, token logging, limits) and skim job-hunter-africa.html (the whole web app in one file). Data is in data/jobs.json (224 real vacancies), data/listed_companies.json (865 listed companies) and data/sample_ads/ (genuine ads, scam ads, and a prompt-injection ad).
1) Summarise in plain English how the app and Fayisa work today.
2) Start the server, call GET /api/health, and run: python3 -m unittest discover -s tests -v. Fix anything that fails.
3) Confirm .env is loaded from this folder first, then the parent folder (../.env), and that .env, data/users.json and logs/ are gitignored.
Don't change features yet.
```

### Prompt 2 — Connect the real AI model
```
Connect Fayisa to the real model using my PORTKEY_API_KEY and MODEL=gpt-6-luna from .env.
- Test one real question through POST /api/fayisa (e.g. "Show me part-time jobs in Accra") and show me the reply and the token usage it logged in logs/fayisa_runs.jsonl.
- If the call fails, find the correct Portkey setup for this course key (model string format, provider header, base URL) and fix it — use the Portkey SDK or OpenAI-compatible endpoint, whichever works. Keep the web-search attempt but make sure the fallback works if web search isn't available.
- In the web app, when Fayisa answers live, show a small "● Live AI" label and the tokens used for that answer.
```

### Prompt 3 — Make Fayisa a real tool-using agent
```
Upgrade Fayisa in jobhunter_server.py from "one model call with context" to a real tool-calling agent (OpenAI-style function calling through Portkey).
Tools (pure Python, using the files in data/):
1. search_jobs(country, region, city, industry, job_type, keyword, limit) — filters data/jobs.json (job_type includes Part-time).
2. check_company(name, country) — fuzzy match against data/listed_companies.json; returns exchange, ticker, confidence.
3. detect_red_flags(text) — rule-based scam check: fees (registration, training, medical, visa), Mobile Money payments, WhatsApp-only or Gmail/Yahoo contacts, unrealistic pay, urgency, requests for ID/bank details, injection phrases. Returns each flag with the exact quote, severity and a 0–100 risk score.
4. get_job(id) — full details and how to apply for one vacancy.
Rules: max 6 tool calls and 4 turns per question, max output tokens per call, and log every model call (agent name, input / cached / output tokens, latency) to logs/fayisa_runs.jsonl. Return a "trace" (which tools were called with what, and short results) with every answer.
In the web app, add a collapsible "How Fayisa answered" panel under each live answer showing the trace and tokens.
Test with: "Is this job real?" + the text of data/sample_ads/scam_registration_fee.txt, and "Find me remote jobs".
```

### Prompt 4 — Job Safety Check (the multi-agent feature)
```
Add a "Job Safety Check" feature — this is the main multi-agent part of my project.
Endpoint POST /api/check-job with {ad_text, profile}. An Orchestrator (in code) runs:
1. Input checks: max 5,000 characters; strip and flag prompt-injection text; wrap the ad as untrusted data between <<<AD>>> markers.
2. TrustShield Agent (LLM + tools detect_red_flags, check_company, search_jobs) → JSON {risk: Low|Medium|High, score, verdict, red_flags:[{flag, quote, severity}], advice}. Guardrail in code: the model can never lower the risk below what the rules found (any fee request = High), and it may only say "verified" if check_company found a match.
3. If risk is High → stop and return safety advice + 3 safe alternatives from search_jobs (no more model calls).
4. Otherwise Match Agent (LLM + search_jobs) → {match_percent, reasons, gaps, alternative_job_ids}; validate ids exist in data/jobs.json.
5. Apply Coach Agent (LLM, no tools) → {how_to_apply steps, documents, cover_note (max 150 words)}; remove any email/URL that isn't in the ad or jobs.json.
Return everything plus the full trace and token totals.
In the web app, add a "🛡 Check a job ad" tab inside AI Tools: a big text box, buttons to load each file in data/sample_ads/, and result cards (risk colour, quoted red flags, match %, how to apply, safer alternatives, agent trace, tokens). Run it on all 7 sample ads and show me a results table.
```

### Prompt 5 — Tokenomics (cost) with real numbers
```
Add cost tracking:
- config: price per 1M tokens for gpt-6-luna (input, cached input, output) read from .env (PRICE_INPUT, PRICE_CACHED, PRICE_OUTPUT) — leave a TODO for me to fill in the course prices; don't guess.
- GET /api/stats + a "Stats" section on the Insights page: number of runs, average input/cached/output tokens per run, cost per run, cost per user per month (assume 8 questions + 4 job checks per user), and projected monthly cost for 100 and 10,000 users. Break down by agent.
- Cost savers (each switchable in .env): keep the long fixed system prompts first so prompt caching works; answer simple job searches with search_jobs without calling the model; cache identical questions for 24 hours; skip Match + Apply Coach when risk is High; cap output tokens.
- scripts/benchmark.py: run all 7 sample ads and 10 typical questions with cost savers ON and OFF; save reports/benchmark.csv (tokens, cost, latency, and whether the verdict changed) and print a summary table.
Run it and show me the numbers.
```

### Prompt 6 — Safety, with proof
```
Harden safety and prove it with tests (all tests must run WITHOUT an API key — mock the model):
- Prompt injection: data/sample_ads/prompt_injection.txt must be flagged and must never be called "verified" or "safe".
- Hallucination: invented emails/URLs are removed from Apply Coach output; alternatives come only from jobs.json.
- Overspending: per-request token cap, daily budget cap (FAYISA_DAILY_TOKEN_CAP), 6-tool-call limit, rate limit per IP — each returns a friendly message.
- Accounts: keep the existing tests in tests/test_security.py passing.
Add tests/test_agents.py covering all of the above and run: python3 -m unittest discover -s tests -v. Show me the output.
Add a "Safety" section in the app (owner portal or AI Tools) with buttons that run the injection ad and the budget-cap demo, so I can screenshot the defenses working.
```

### Prompt 7 (optional) — Save profiles on the server
```
Right now profiles, CVs, applications and Job Mail live only in the browser. Move them to the server so different users see each other's data correctly:
- SQLite database data/app.db (gitignored) with tables: profiles, cvs (store PDFs in data/cvs/<user>/, PDF only, max 5 MB, check the %PDF header), applications, messages, companies.
- Endpoints that require the session cookie and check the user's role (job seekers only their own data; verified recruiters can see job seekers who uploaded a CV and are discoverable; owner sees everything).
- Resume Books lists real job seekers with uploaded CVs; View resume streams the PDF to verified recruiters only and logs the view.
- Recruiters can post vacancies after the owner approves their company (owner portal button).
Update the web app to use these endpoints when the server is running. Add tests for the permission rules.
```

### Prompt 8 — Repo ready for grading
```
Get the repo ready for the teaching staff:
1. Update README.md: one-paragraph description, a screenshot, and "Run it in 5 minutes" (clone → copy .env.example to .env → put PORTKEY_API_KEY in it (or put .env one folder up) → python3 jobhunter_server.py → open http://localhost:8000). Keep Troubleshooting.
2. .env.example must list every key with no real values. Check no secrets are committed anywhere (search for "sk-", "pk-", and my key).
3. Dry run: clone the repo into a brand-new temporary folder, put .env ONE LEVEL ABOVE it, follow the README exactly, ask Fayisa a question and run a Job Safety Check. Fix anything that breaks. Tell me how long setup took (must be under 10 minutes).
4. scripts/screenshots.py (Playwright, optional dependency) that saves to docs/screenshots/: home + Africa map, Find Jobs, Fayisa answering live with its trace, Job Safety Check on a scam ad (High risk), the injection ad being blocked, Stats/tokens, test output, owner portal. If Playwright isn't available, tell me which screens to capture by hand.
5. Commit and push to a new GitHub repo "job-hunter-africa-app". If private, tell me how to add "zlisto" as a collaborator.
```

> **Before Prompt 9 — your job (this is what gets Tier 3):** have 2–3 real job seekers try the app for 10 minutes each. Write down: their name/role (with permission), how long it took them to check a job ad by hand vs with the app, whether it caught a scam, and one quote each. Take a photo or screenshot.

### Prompt 9 — The report (report.html)
```
Write report.html: ONE self-contained file (all screenshots embedded as base64), 10–15 printed letter pages, clean design in my colours (deep green #0B5D3B, gold #E8A317, terracotta #C2502A) with print-friendly CSS.
Use ONLY real numbers from logs/fayisa_runs.jsonl, reports/benchmark.csv and the test output. Mark anything uncertain with [CHECK].
Sections in order:
1. Title + links — "Job Hunter Africa: AI career agent", Fayisa Abdulai, GitHub link [URL], app link if online, one-sentence summary.
2. Motivation — job seekers in Ghana/Africa face scattered vacancies and recruitment scams; how they cope today and what it costs (money, time, risk). My founder story: started in Accra in 2021 sharing vacancies. Real public sources with links (verify each).
3. What is new — compare Jobberman, LinkedIn, BrighterMonday, Indeed and plain ChatGPT; what we do differently (scam checks grounded in real listings and stock-exchange records, country-first and part-time search, how-to-apply guidance, injection-safe handling of untrusted ads, privacy-first Resume Books).
4. The agents — table of Fayisa, Orchestrator, TrustShield, Match, Apply Coach with their tools; an SVG diagram; why gpt-6-luna; one real run traced step by step with screenshots.
5. Tokenomics — tokens per run (input/cached/output), cost per run, per user per month, at 100 and 10,000 users, what we did to cut cost, and the benchmark showing any quality impact.
6. Safety — risks, defenses built, and evidence (injection blocked screenshot, test output, caps, account security: hashed passwords, email codes, lockout, owner-only portal).
7. Impact — my user tests: [PASTE names/roles, before vs after times, quotes]; scams caught; who it serves.
8. Limits + next steps — WhatsApp version, more languages, live job feeds, employer partnerships, mobile app, Supabase deployment.
Show me the printed page count.
```

### Prompt 10 — Slides, final check, demo video
```
1. Make slides.html with reveal.js from a CDN, max 10 slides, screenshots and the diagram embedded as base64, big text, my colours: Title + pitch | The problem | What's new | How the agents work (diagram) | Demo: scam caught | Demo: Fayisa + how to apply | Cost to run | Safety | Impact (user numbers + quote) | What's next. Open it and check every slide with the arrow keys and F.
2. Final check: run all tests; do the fresh-clone dry run again with .env one folder up; report.html and slides.html open offline with all images; no secrets in the repo; README link works; list anything still marked [CHECK].
3. Write me a 2–3 minute demo video script: open the app → ask Fayisa for part-time jobs in Accra → paste a WhatsApp scam ad into Job Safety Check (High risk, quoted red flags) → check a genuine job (match %, how to apply) → show the agent trace and tokens → show the injection ad being blocked.
```

---

## Part C — Submit on Canvas (due 6:00 PM)

- [ ] GitHub repo link (public, or private with **zlisto** added)
- [ ] `report.html`
- [ ] `slides.html`
- [ ] Optional: 2–3 minute demo video

## Useful commands

| Task | Command |
|---|---|
| Start the app | `python3 jobhunter_server.py` |
| Stop the app | `Ctrl + C` in the terminal |
| Run tests | `python3 -m unittest discover -s tests -v` |
| Rebuild data files | `python3 scripts/extract_data.py` |
| Save to GitHub | `git add . && git commit -m "update" && git push` |
