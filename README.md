# Job Hunter Africa — AI career agent

**Job Hunter Africa** helps job seekers across Africa find real, verified job opportunities in one place — and gives them **Fayisa**, an AI career agent that searches jobs, spots scams, finds skill gaps, writes cover letters and prepares them for interviews.

Started in Accra, Ghana in 2021 by Fayisa Abdulai. Contact: thejobhuntergh@gmail.com

- **Live app:** _add your link here if you put it online_
- **Data:** 224 real vacancies across 10 African countries · 865 stock-exchange-listed companies

---

## Run it in 5 minutes

You need **Python 3.8 or newer**. Nothing else to install — the app uses only Python's standard library.

```bash
# 1. Get the code
git clone <your-repo-url>
cd job-hunter-africa-app

# 2. Add your API key
cp .env.example .env          # Windows: copy .env.example .env
#    open .env and paste your PORTKEY_API_KEY (or OPENAI_API_KEY)
#    The .env file can be in this folder OR one folder above it.

# 3. Start the app
python3 jobhunter_server.py   # Windows: python jobhunter_server.py

# 4. Open http://localhost:8000
```

Then:
1. Click **AI Tools** and ask Fayisa anything — e.g. *"Show me part-time jobs in Accra"* or *"Is this job offer a scam?"*
2. Click **Sign up** to create an account. The 6-digit code is emailed (if SMTP is set in `.env`) or printed in the terminal window.
3. Owner portal: `http://localhost:8000/#admin` with `OWNER_EMAIL` / `OWNER_PASSWORD` from `.env`.

## Keys (`.env`)

| Key | Needed? | What for |
|---|---|---|
| `PORTKEY_API_KEY` | Yes (or `OPENAI_API_KEY`) | Fayisa's AI model (`gpt-6-luna` on the course key) |
| `OPENAI_API_KEY` | Alternative | Use your own OpenAI key instead |
| `MODEL` | Optional | Model name, default `gpt-6-luna` |
| `OWNER_EMAIL`, `OWNER_PASSWORD` | Optional | Your owner (admin) login |
| `SMTP_*` | Optional | Email real sign-in codes (e.g. Gmail App Password) |

Never commit `.env`. It is listed in `.gitignore`.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Project structure

| Path | What it is |
|---|---|
| `job-hunter-africa.html` | The web app (jobs, map, Fayisa, profiles, Job Mail, hiring, Resume Books) |
| `jobhunter_server.py` | Server: accounts, email codes, Fayisa AI agent, token logging, safety limits |
| `data/jobs.json` | 224 real vacancies (used by the agent's tools) |
| `data/listed_companies.json` | 865 companies on 9 African stock exchanges |
| `data/sample_ads/` | Test job ads: genuine, scams, and a prompt-injection attack |
| `scripts/extract_data.py` | Rebuilds the data files from the web app |
| `tests/` | Automated security tests |
| `logs/` | Token usage per AI run (`fayisa_runs.jsonl`) and login audit log (not committed) |

## Troubleshooting

- **"AI is not connected"** — your `.env` has no key, or is in the wrong folder.
- **AI error 400/404** — set `MODEL=` to the exact model name your course uses (e.g. `@openai/gpt-6-luna`).
- **Port in use** — add `PORT=8001` to `.env`.
- **No email arrives** — without `SMTP_*` settings, codes are printed in the terminal.

## Making the app available to external users

External users cannot reach a localhost server. Deploy the app to a host with a public HTTPS URL, keep `data/app.db`, `data/users.json`, `data/cvs/`, and `logs/` on persistent storage, and set `HOST=0.0.0.0`. Configure Gmail SMTP with an App Password so verification and login codes are delivered by email. Put the production `PORTKEY_API_KEY`, SMTP values, and owner credentials in the host environment; never commit them. Use the public HTTPS URL in the app and report.

## Deployment files

`Dockerfile`, `Procfile`, and `render.yaml` are included for a public Render deployment. Configure the secret environment variables in the hosting dashboard, attach persistent storage for `data/` and `logs/`, and use the generated HTTPS URL for external users.
