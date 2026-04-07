# FinPath — Event-Driven Fintech Analytics

> A end-to-end product analytics pipeline simulating a robo-advisory investment platform — built to demonstrate data engineering, backend development, and product analytics skills.

🔗 **Live Dashboard:** [finpath-dashboard.streamlit.app](https://finpath-dashboard.streamlit.app)

---

## What Is This?

FinPath simulates a fintech robo-advisory platform from the ground up. A Python-based event simulator generates **5.1 million behavioral events** across **250,000 synthetic users**, covering 40 distinct event types and 10 lifecycle phases — from signup through active investing.

The goal: build a realistic product analytics pipeline that mirrors how data teams at fintech companies track, analyze, and act on user behavior.

---

## Key Insights

### 🔻 Funnel Analysis
Out of 250,000 simulated users:

| Stage | Users | Conversion |
|---|---|---|
| Total Users | 250,000 | — |
| Signup Completed | 175,277 | 70.0% of total |
| Email Verified | 148,947 | 84.0% of signups |
| Onboarding Completed | 133,994 | 90.0% of verified |
| **Risk Quiz Completed** | **55,447** | **41.4% of onboarded** ⚠️ |
| KYC Completed | 49,426 | 89.1% of quiz |
| Deposit Completed | 31,926 | 64.6% of KYC |
| Portfolio Created | 30,388 | 95.2% of deposited |

**Critical Finding:** The risk quiz is the single biggest drop-off point in the entire funnel — more than half of onboarded users abandon here. Simplifying or gamifying the quiz could unlock the largest conversion gains. Once users make a deposit, 95.2% follow through to create a portfolio, confirming that financial commitment drives completion.

### 📉 Churn Analysis
Churn was defined by explicit user actions (withdrawal, account closure, unsubscribe) rather than inactivity — a more reliable signal in fintech where users may be inactive for weeks between investments.

### 🔁 Cohort Retention
Monthly cohort retention tracked across 12 cohorts, showing how different acquisition periods impact long-term engagement.

### 😰 Panic Sell Behavior
Analyzed how users respond to simulated market downturns across risk profiles — conservative users show significantly higher panic-sell rates than aggressive investors.

### 🏦 Deposit Distribution
Distribution of deposit amounts segmented by risk profile, revealing how risk appetite correlates with initial capital commitment.

### 🛠️ Feature Adoption
Tracked adoption rates of key platform features (auto-invest, tax harvesting, rebalancing) and their correlation with long-term retention.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FinPath Pipeline                    │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │   Python     │    │  PostgreSQL  │    │  Jupyter  │  │
│  │  Simulator   │───▶│   Database   │──▶│ Notebook  │  │
│  │              │    │              │    │           │  │
│  │ 250K users   │    │ 5.1M events  │    │ 12 SQL    │  │
│  │ 40 events    │    │ schema +     │    │ analyses  │  │
│  │ 10 phases    │    │ indexes      │    │           │  │
│  └──────────────┘    └──────────────┘    └─────┬─────┘  │
│                                                │        │
│                                          CSV exports    │
│                                                │        │
│                      ┌─────────────────────────▼──────┐ │
│                      │     Streamlit Dashboard        │ │
│                      │  5 pages · Plotly charts       │ │
│                      │  Funnel · Retention · Churn    │ │
│                      │  Behaviour · Features          │ │
│                      └────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (REST API)          │   │
│  │         Serves data via /events, /users          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  Everything containerised with Docker Compose           │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Simulation | Python (NumPy, Faker, psycopg2) |
| Database | PostgreSQL 15 |
| Analytics | SQL, Pandas, Matplotlib |
| Backend API | FastAPI + Uvicorn |
| Dashboard | Streamlit + Plotly |
| Containerisation | Docker + Docker Compose |

---

## Project Structure

```
FinPath/
├── backend/                  # FastAPI REST API
│   ├── main.py
│   ├── .env.example          # Copy to .env and fill in credentials
│   └── requirements.txt
├── dashboard/                # Streamlit analytics dashboard
│   ├── app.py                # Entry point
│   ├── pages/
│   │   ├── 1_overview.py     # Funnel analysis
│   │   ├── 2_behaviour.py    # Risk profile behaviour
│   │   ├── 3_retention.py    # Cohort retention
│   │   ├── 4_churn.py        # Churn analysis
│   │   └── 5_features.py     # Feature adoption
│   ├── data/                 # Pre-generated CSVs (committed to repo)
│   ├── Dockerfile
│   └── requirements.txt
├── notebooks/
│   └── finpath_analytics.ipynb   # All 12 SQL analyses
├── postgres/
│   └── schema_creation.sql       # DB schema + seed
├── simulator/                    # Event generation engine
│   └── simulate.py
├── docker-compose.yml
└── .env.example                  # Root-level env for Docker Compose
```

---

## Running Locally

### Prerequisites
- Docker Desktop installed and running
- Git

### 1. Clone the repo

```bash
git clone https://github.com/srgmnagar/FinPath.git
cd FinPath
```

### 2. Set up environment variables

```bash
# Root level — for Docker Compose
cp .env.example .env

# Backend level — for FastAPI and Jupyter notebook
cp backend/.env.example backend/.env
```

Open both `.env` files and fill in your database password:

```env
DB_PASSWORD=your_password_here
```

> ⚠️ Never commit `.env` files. They are already in `.gitignore`.

### 3. Start all services

```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on `localhost:5432` (auto-creates schema)
- **FastAPI backend** on `localhost:8000`
- **Streamlit dashboard** on `localhost:8501`

### 4. Run the simulator (first time only)

```bash
cd simulator
pip install -r requirements.txt
python simulate.py
```

This generates 5.1M events across 250K users into the PostgreSQL database. Takes ~5–10 minutes.

### 5. View the dashboard

Open `http://localhost:8501` in your browser.

**FastAPI docs:** `http://localhost:8000/docs`

---

## Jupyter Notebook

The notebook connects to your local PostgreSQL instance and runs 12 analytical queries.

> ⚠️ **Note on CSVs:** The `dashboard/data/` folder contains pre-generated CSVs that power the live Streamlit dashboard. If you run the notebook locally and want to export your own CSVs, update the export paths in the notebook to point to `notebooks/data/` instead — this keeps your local outputs separate and avoids overwriting the committed dashboard data.

### Setup

```bash
cd notebooks
pip install jupyter sqlalchemy psycopg2-binary pandas matplotlib
jupyter notebook
```

Make sure Docker is running and the simulator has been run before executing the notebook queries.

---

## Live Dashboard

The deployed dashboard reads from pre-generated CSVs — no database connection needed.

🔗 [finpath-dashboard.streamlit.app](https://finpath-dashboard.streamlit.app)

---

## Design Decisions

**Churn definition:** Churn is triggered by explicit user actions (account closure, withdrawal, unsubscribe) rather than inactivity. In fintech, users may be dormant for weeks between transactions — inactivity-based churn would produce misleading signals.

**Session metrics:** Sessions are measured by event count only, not duration. Without reliable timestamps on every micro-interaction, duration would be noisy and untrustworthy.

**Simulator is frozen:** The simulator parameters (user counts, drop-off rates, event types) are locked. All future work builds on top of the existing dataset rather than regenerating it.

---

## What I'd Build Next

- **Kafka integration** — Replace direct DB writes with an event streaming layer (`Simulator → Kafka → Consumer → PostgreSQL`) for a true real-time pipeline
- **dbt models** — Transform raw events into clean analytical models
- **Alerting** — Flag anomalies like sudden churn spikes or deposit drop-offs
