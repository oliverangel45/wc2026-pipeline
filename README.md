# WC2026 Data Pipeline 🌍⚽🏆(still in progress)
 
A real-time data engineering pipeline built to extract, load, transform (ELT) and visualise live FIFA World Cup 2026 data. The pipeline streams match results, group standings, and match events from the [football-data.org](https://www.football-data.org/) REST API through Apache Kafka into Snowflake, transforms the raw data with dbt, and surfaces it through a Grafana dashboard, all containerised within Docker Compose. 

I would've loved to have used a Websocket API to have scores and match updates flow through to the grafana dashboard immediately, but chose against this due to the additonal incurred cost 🫠
 
 
## Stack
 
| Layer | Technology |
|---|---|
| Data source | football-data.org REST API (free tier) |
| Message broker | Apache Kafka (KRaft mode, no Zookeeper) |
| Stream processing | Python producers and consumer |
| Cloud data warehouse | Snowflake |
| Infrastructure provisioning | Terraform (Snowflake provider v0.100) |
| Transformation | dbt (dbt-core + dbt-snowflake) |
| Orchestration | Docker Compose |
| Dashboard | Grafana |
| CI/CD | GitHub Actions |
 
---
 
## Project structure
 
```
wc2026-pipeline/
├── producers/
│   ├── matches_events_producer.py   # polls matches + events
│   ├── standings_producer.py        # polls standings
│   └── Dockerfile
├── consumer/
│   ├── consumer.py                  # routes messages to Snowflake raw tables
│   └── Dockerfile
├── dbt_project/
│   ├── models/
│   │   ├── staging/                 # stg_matches, stg_standings, stg_events
│   │   └── marts/                   # fct_match_results, fct_top_scorers, dim_group_standings, dim_team_stats
│   ├── seeds/
│   │   ├── teams.csv                # team metadata and flag mappings
│   │   └── match_statuses.csv       # valid status values for accepted_values tests
│   └── dbt_project.yml
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/             # Snowflake datasource config
│   │   └── dashboards/              # dashboard provisioning config
│   └── dashboards/                  # live scores, standings, top scorers, match events
├── terraform/
│   ├── main.tf                      # all Snowflake resources
│   ├── variables.tf                 # input variable declarations
│   └── outputs.tf                   # post-apply outputs
├── .github/
│   └── workflows/
│       └── dbt_ci.yml               # runs dbt build on push to main
├── docker-compose.yml
├── .env.example
└── requirements.txt
```
 
---
 
## Kafka topics
 
| Topic | Producer | Poll interval | Consumer destination |
|---|---|---|---|
| `wc.matches` | matches_events_producer | 60 seconds | `RAW.MATCHES` |
| `wc.events` | matches_events_producer | 60 seconds | `RAW.EVENTS` |
| `wc.standings` | standings_producer | 5 minutes | `RAW.STANDINGS` |
 
Kafka runs in KRaft mode — no Zookeeper. A single broker node acts as both broker and controller. Each producer and consumer waits for the broker healthcheck to pass before starting - see broker service in docker-compose.yml.
 
---
 
## Snowflake infrastructure
 
All infrastructure is provisioned via Terraform using the Snowflake provider. No manual setup is required beyond the initial bootstrap of user role grants, which is a known limitation of personal Snowflake accounts.
 
Resources provisioned:
 
- `WC2026` database with `RAW` and `ANALYTICS` schemas
- `WC2026_WH` virtual warehouse (X-SMALL, auto-suspend 60s to avoid burning through credits)
- `LOADER` role — used by the Kafka consumer, grants INSERT/UPDATE/SELECT on RAW tables
- `TRANSFORMER` role — used by dbt, grants SELECT on RAW and CREATE TABLE/VIEW on ANALYTICS
- Three raw tables: `MATCHES`, `STANDINGS`, `EVENTS` — each with structured columns and a `VARIANT` `RAW_PAYLOAD` column storing the complete API response
---
 
## dbt models
 
```
RAW schema (Snowflake, written by consumer)
    └── stg_matches       (staging, deduplicates on MATCH_ID)
    └── stg_standings     (staging, deduplicates on TEAM_ID)
    └── stg_events        (staging, deduplicates on EVENT_ID)
            │
            ├── fct_match_results      (incremental, one row per match)
            ├── fct_top_scorers        (incremental, goals by player excl. own goals)
            ├── dim_group_standings    (latest standing per team per group)
            └── dim_team_stats         (win rate, goals per game, form)
```
 
Seeds: `teams.csv` provides team metadata joined into mart models. `match_statuses.csv` feeds `accepted_values` tests on the `STATUS` column.
 
Source freshness checks are configured on all three raw tables. dbt tests cover `not_null`, `unique`, and `accepted_values` on key columns across staging and mart models.
 
---
 
## CI/CD
 
A GitHub Actions workflow runs `dbt build` on every push to `main`, validating all models, tests, and seeds against the Snowflake ANALYTICS schema. No manual dbt runs are required for validation.
 
---

## Known Limitations

**In-memory event deduplication**
The matches/events producer tracks which finished matches have had their events fetched using a Python set stored in memory. If the producer container restarts, this set resets and events for finished matches will be re-fetched once before being added to the set again. This may result in a small number of duplicate event rows in `RAW.EVENTS`. The dbt deduplication logic in `stg_events` handles these duplicates cleanly via `ROW_NUMBER()` partitioned on `EVENT_ID`.

**Manual Snowflake bootstrapping steps**
Two Snowflake grants could not be provisioned via Terraform due to personal account limitations — granting roles to the user and `CREATE SCHEMA` on the database. These were applied manually via SQL. In a production Snowflake account managed by an administrator these would be handled entirely by Terraform. The exact SQL statements required are documented in the setup instructions below.

**Grafana Snowflake plugin**
The official Grafana Snowflake datasource plugin requires an Enterprise licence for self-managed instances. The community plugin (`michelin-snowflake-datasource`) was used instead. This plugin does not support image rendering in table columns, meaning team crest images cannot be displayed. A future iteration would use Streamlit or Evidence.dev for richer visual formatting.

**Kafka topics created on first message**
Kafka topics `wc.matches`, `wc.standings`, and `wc.events` are created automatically when the first message is produced rather than being pre-created. In a production environment topics would be pre-created with explicit partition and replication settings.
 
## Running the pipeline
 
### Prerequisites
 
- Docker Desktop
- Snowflake account
- football-data.org API key
- Terraform (v1.7+)

> **Note:** Two manual SQL steps are required after `terraform apply` due to personal Snowflake account limitations. Run these in a Snowflake worksheet:
> ```sql
> USE ROLE ACCOUNTADMIN;
> GRANT ROLE LOADER TO USER your_username;
> GRANT ROLE TRANSFORMER TO USER your_username;
> GRANT CREATE SCHEMA ON DATABASE WC2026 TO ROLE TRANSFORMER;
> ```

### Setup

```bash
git clone https://github.com/oliverangel45/wc2026-pipeline.git
cd wc2026-pipeline
cp .env.example .env
# fill in .env with your Snowflake credentials, API key
# SNOWFLAKE_ACCOUNT should be the full identifier e.g. ORGNAME-ACCOUNTNAME
```
 
### Provision Snowflake infrastructure

Load environment variables into your terminal session first:

```powershell
# Windows PowerShell
Get-Content .env | Where-Object { $_ -notmatch '^#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
}
```

```bash
# Mac/Linux
export $(grep -v '^#' .env | xargs)
```

Then provision:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```
 
### Start the pipeline

```bash
docker compose up --build
```

This starts the Kafka broker, both producers, the consumer, dbt, Grafana, and Streamlit.

- Grafana dashboard: `http://localhost:3000` (admin/admin)
- Streamlit dashboard: `http://localhost:8501`

dbt runs automatically on startup — seeding reference data, building all models, and running all 46 tests.
 
## Personal reflection
 
This project idea stemmed from my genuine interest in sports and football, and the 2026 World Cup came at a perfect time to challenge myself building an end-to-end ELT data pipeline with more complexity than my previous weather pipeline project. 

Having a live data source with real events happening every day (goals, upsets, group table shifts) kept me motivated to push through the harder parts of the build rather than settling for a static dataset.
 
The biggest new addition over my first portfolio project was Terraform. I had no prior experience with Infrastructure as Code before starting this pipeline. Working through the Snowflake provider documentation, understanding the layered grant model, and debugging provider version mismatches gave me a solid grounding in how Terraform works and why it is the right tool for reproducible infrastructure, even when provisioning a single cloud warehouse rather than a full multi-service platform. I came to genuinely appreciate the discipline of defining infrastructure as code: the ability to destroy and rebuild an identical environment from a single `terraform apply` is something an init script cannot replicate.
 
Managing three Kafka topics simultaneously introduced a level of architectural complexity I hadn't dealt with in previous projects (1-2 topics maximum). Designing the routing logic in the consumer, handling the different polling intervals across producers, and thinking through what happens when one topic has messages and another doesn't were all genuinely enjoyable engineering problems to try and solve.
 
---