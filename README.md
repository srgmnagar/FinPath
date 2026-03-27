# FinPath — Event-Driven Fintech Analytics

> Simulating and analyzing real user journeys across a robo-advisory app at scale.

---

## What is this?

FinPath is an end-to-end data engineering and analytics project that simulates how users behave inside a robo-advisory investment platform — from first app open to portfolio creation, deposits, and churn.

It is **not** just a toy dataset. It models real fintech product behavior:
- Probabilistic drop-offs at every funnel stage
- 40 distinct event types across 10 lifecycle phases
- Rich JSON properties on every event (risk scores, amounts, fund types, timing)
- Realistic Indian fintech context (UPI, Aadhaar KYC, INR deposits, SIP goals)

---

## Scale

| Metric | Value |
|---|---|
| Simulated users | 250,000 |
| Total events | 5,100,000+ |
| Event types | 40 |
| Lifecycle phases | 10 |
| Simulation time | ~120 seconds |
| DB size | ~2.5 GB |

---

## Architecture

```
Simulator ──► Kafka ──► FastAPI Consumer ──► PostgreSQL ──► Analytics ──► Streamlit
   │                                              │
   └── (direct bulk mode for local dev) ──────────┘
```

- **Simulator** — generates 250k users and 5M+ events using probabilistic flow engine
- **FastAPI** — REST API for event ingestion (`/users`, `/events`)
- **Kafka** — event queue for production-grade async ingestion (coming)
- **PostgreSQL** — stores all users and events with indexes for fast analytics
- **Analytics** — SQL queries for funnels, drop-offs, cohorts, behavior, churn
- **Streamlit** — dashboard visualizing all analytics (coming)

---

## Project Structure

```
FinPath/
├── backend/                  # FastAPI application
│   ├── routes/
│   │   ├── events.py         # POST /events
│   │   └── users.py          # POST /users
│   ├── database.py
│   └── main.py
│
├── simulator/                # Data generation engine
│   ├── run.py                # Entry point — python run.py --users 250000
│   ├── user_factory.py       # Generates user profiles
│   ├── flow_engine.py        # Probabilistic journey simulation
│   ├── event_builder.py      # Builds event payloads with rich properties
│   └── bulk_writer.py        # PostgreSQL COPY bulk insert
│
├── postgres/                 # Database layer
│   ├── schema_creation.sql   # Table definitions
│   └── analytics_queries.sql # All analytical SQL queries
│
├── notebooks/
│   └── finpath_analytics.ipynb  # SQL queries + results + charts
│
├── dashboard/                # Streamlit (in progress)
└── data/
    └── events.md             # Full event taxonomy documentation
```

---

## Event Taxonomy

Full event taxonomy across 10 lifecycle phases and 40 event types is documented in [`data/events.md`](data/events.md)

---

## Funnel Results (actual simulated data)

| Stage | Users | Conversion |
|---|---|---|
| Total users | 250,000 | — |
| signup_completed | 175,204 | 70.1% |
| email_verified | 149,089 | 85.1% of signups |
| onboarding_completed | 134,176 | 90.0% of verified |
| risk_quiz_completed | 55,591 | 41.4% of onboarded |
| kyc_completed | 49,679 | 89.4% of quiz done |
| deposit_completed | 32,055 | 64.5% of KYC done |
| portfolio_created | 30,377 | 94.8% of depositors |

**Overall conversion: 250,000 → 30,377 = 12.2%**

Biggest drop-off: risk quiz (41.4% abandon rate) — consistent with real robo-advisory industry data where risk profiling questionnaires cause the most friction.

---

## Analytics (in progress)

- [x] Funnel conversion rates
- [x] Drop-off analysis per stage
- [ ] Time between stages (avg days signup → deposit)
- [ ] Cohort retention by signup week
- [ ] Risk profile vs behavior (do high-risk users invest more?)
- [ ] Churn signal detection
- [ ] Session depth analysis

Full queries and results in [`notebooks/finpath_analytics.ipynb`](notebooks/finpath_analytics.ipynb)

---

## Running locally

**1. Clone and set up:**
```bash
git clone https://github.com/yourusername/finpath
cd finpath
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Set up environment:**
```bash
# create backend/.env
DB_HOST=localhost
DB_NAME=finpath
DB_USER=postgres
DB_PASSWORD=yourpassword
```

**3. Create database tables:**
```bash
psql -U postgres -d finpath -f postgres/schema_creation.sql
```

**4. Run the simulator:**
```bash
cd simulator
python run.py --users 250000
# generates ~5.1M events in ~120 seconds
```

**5. Start the API:**
```bash
cd backend
uvicorn main:app --reload
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| API | FastAPI |
| Database | PostgreSQL 16 |
| ORM / DB driver | psycopg2, SQLAlchemy |
| Event queue | Kafka (coming) |
| Data generation | Faker, custom probability engine |
| Analytics | SQL, Pandas |
| Notebook | Jupyter |
| Dashboard | Streamlit (coming) |
| Environment | python-dotenv |

---

## Status

| Component | Status |
|---|---|
| Database schema | Done |
| FastAPI backend | Done |
| Simulator (250k users) | Done |
| Analytics SQL + notebook | In progress |
| Kafka integration | Planned |
| Streamlit dashboard | Planned |
| Docker setup | Planned |

---
