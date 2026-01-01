# NYC 311 Analytics Dashboard

**Your Data-Driven Insights Platform for NYC Service Requests**

---

![Live Demo](https://img.shields.io/badge/Live%20Demo-Online-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue) ![Pandas](https://img.shields.io/badge/Pandas-2.0+-orange) ![Plotly](https://img.shields.io/badge/Plotly-5.0+-blue) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-green)

🌐 **[Live Website](https://nyc-311-ops-analysis.streamlit.app/)** | 📊 **NYC Open Data API** | 🚀 **Streamlit Cloud**

---

A Postgres-backed Streamlit analytics application for analyzing NYC 311 service requests. This project provides a complete data pipeline from raw API data to interactive visualizations, enabling analysis of complaint trends, agency performance, and resolution metrics across New York City boroughs.

## Architecture

The application follows a layered data architecture:

1. **Raw Layer**: Fetches data from the NYC Socrata API and stores it in `raw.nyc311_requests` table
2. **Core Layer**: Cleans and transforms raw data into `core.nyc311_requests_clean` with standardized fields and derived metrics
3. **Marts Layer**: Pre-aggregated analytics tables (`marts.kpi_monthly`, `marts.top_complaints_monthly`, `marts.agency_performance_monthly`) for fast dashboard queries
4. **Application Layer**: Streamlit dashboard with interactive pages for overview metrics, complaint analysis, and agency performance

Data flows from the Socrata API → CSV files → Postgres raw schema → core schema → marts → Streamlit dashboard.

## Setup

### Local Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your `DATABASE_URL`:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nyc311
   ```
3. Start Postgres using Docker Compose:
   ```bash
   docker compose up -d
   ```
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set the `DATABASE_URL` environment variable (or load from `.env` file)

### GitHub Codespaces

1. Open the repository in Codespaces
2. Copy `.env.example` to `.env` and update `DATABASE_URL` if needed
3. Docker Compose and Python will be available in the Codespaces environment
4. Follow the same setup steps as local setup

## Configuration

### Local Development
Set `DATABASE_URL` in your `.env` file:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nyc311
```

Alternatively, you can set it as an environment variable in your shell:
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nyc311
```

### Streamlit Cloud Deployment
1. Go to your app's settings in Streamlit Cloud
2. Navigate to "Advanced settings" → "Secrets"
3. Add your DATABASE_URL in TOML format:
   ```toml
   DATABASE_URL = "postgresql://user:password@host:port/database"
   ```
4. Save and redeploy

## Commands

### Initial Setup

Start the Postgres database:
```bash
docker compose up -d
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Data Pipeline

Fetch data from the NYC 311 API (last 30 days):
```bash
python scripts/fetch_311.py --days 30
```

Load data into Postgres:
```bash
python scripts/load_311_to_postgres.py
```

### Database Schema

Create schemas:
```bash
psql $DATABASE_URL -f sql/schema/01_create_schemas.sql
```

Create raw table:
```bash
psql $DATABASE_URL -f sql/schema/02_create_raw_311_table.sql
```

Create core table:
```bash
psql $DATABASE_URL -f sql/schema/03_create_core_311.sql
```

Build all marts:
```bash
psql $DATABASE_URL -f sql/marts/00_build_all_marts.sql
```

### Run Application

Start the Streamlit dashboard locally:
```bash
streamlit run app/app.py
```

The dashboard will be available at `http://localhost:8501`

**Or access the live deployment:** [https://nyc-311-ops-analysis.streamlit.app/](https://nyc-311-ops-analysis.streamlit.app/)

## Data

Raw data files and processed outputs are not committed to the repository. The following directories are excluded via `.gitignore`:

- `data/raw/` - Raw CSV files downloaded from the API
- `data/processed/` - Intermediate processed data files
- `data/marts/` - Exported mart data (if any)

This approach keeps the repository lightweight and ensures that:
- Large data files don't bloat the repository
- Each user can fetch their own fresh data from the source
- Sensitive or environment-specific data remains local
- The repository focuses on code and configuration rather than data snapshots

To work with data, run the fetch and load scripts as described in the Commands section above.

