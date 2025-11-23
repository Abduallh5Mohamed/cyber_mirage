# PROJECT CONTEXT FOR AI — Cyber Mirage

> Purpose: single-file, structured, detailed description of the Cyber Mirage project so you can upload it to any AI model. The file contains machine-friendly metadata, full architecture description, components, file paths, endpoints, data flows, examples, and recommended prompts you can ask the model.

---

## Metadata (JSON summary for quick ingestion)

```json
{
  "project_name": "Cyber Mirage",
  "root": "A:/cyber_mirage",
  "language_primary": "Arabic (some docs in English)",
  "services": ["honeypot", "redis", "postgres", "prometheus", "grafana", "alertmanager", "node-exporter", "cadvisor", "dashboard (streamlit)"]
}
```

---

## 1. Short plain-English summary

Cyber Mirage is a containerized honeynet/honeypot platform built with Docker Compose. It runs multiple services (honeypot API, Redis, PostgreSQL, Prometheus, Grafana, Alertmanager, Node Exporter, cAdvisor, Streamlit dashboard). The system captures attacker interactions, stores artifacts (pcaps, sample files), enriches events (geoip, reputation), stores structured events in PostgreSQL, exposes metrics for Prometheus, and routes alerts through Alertmanager. Grafana visualizes metrics and alerts. An AI Engine (documented) can classify and score incidents.

---

## 2. Where the file is and how to use it

Path in repo: `A:\cyber_mirage\PROJECT_CONTEXT_FOR_AI.md` (this file). Upload this single file to any LLM or knowledge-base ingestion tool. For best results, chunk into < 2000 token pieces if the model has input size limits. Provide a short instruction: "Act as an expert on this repository and answer questions about service architecture, data flow, file locations, how to run, and forensic artifacts." Include follow-up instructions to ask for clarifying questions.

---

## 3. Repo layout (relevant parts)

- `A:\cyber_mirage\` (project root)
  - `docker-compose.yml` — main Compose file (development/dev-style) and `docker-compose.production.yml` exists for production.
  - `Dockerfile` and `Dockerfile.production` — build rules for honeypot/services
  - `.env` and `.env.production` — environment variables templates
  - `src/` — application code
    - `src/api/main.py` — FastAPI application (Honeypot API)
    - `src/dashboard/streamlit_app.py` — Streamlit dashboard code
    - `src/environment/base_env.py` — environment helpers
  - `docker/`
    - `docker/prometheus/prometheus.yml` — Prometheus scrape rules
    - `docker/prometheus/alerts.yml` — Prometheus alert rules
    - `docker/grafana/datasources/prometheus.yml` — Grafana provisioning
    - `docker/alertmanager/alertmanager.yml` — Alertmanager routes
    - `docker/postgres/init.sql` — DB initialization script
  - `data/` — persistent data volume (captures, models, backups)
  - `logs/` — application logs
  - documentation files: `PRODUCTION_QUICK_START.md`, `PROJECT_FINAL_STATUS.md`, `PRODUCTION_FILES_CREATED.md`, `README_PRODUCTION.md`, etc.

---

## 4. Services & Roles (short)

- honeypot (container): accepts attacker connections, simulates services (SSH/HTTP/FTP etc.), logs interactions, saves samples.
- redis: event queue/fast cache between honeypot and processors.
- postgres: stores structured event records, attacker profiles, analytics, and monitoring tables.
- prometheus: scrapes metrics from app endpoints and exporters, evaluates alert rules.
- alertmanager: receives alerts and routes notifications (Slack/email/webhooks).
- grafana: visualization dashboards for metrics and alerts.
- node-exporter / cadvisor: node and container metrics collectors.
- streamlit dashboard: front-end for internal monitoring and reports.
- AI Engine (optional): consumes events to classify and score incidents.

---

## 5. Main run commands

(Use PowerShell on Windows; run from `A:\cyber_mirage`)

```powershell
# Activate venv (if needed)
.\venv\Scripts\Activate.ps1

# Build & start core services (development)
docker-compose up -d redis postgres prometheus grafana node-exporter

# Start full production stack
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Check status
docker ps
docker-compose ps

# Logs for a service
docker-compose logs -f alertmanager
```

---

## 6. Important configuration files and their roles

- `docker-compose.production.yml` — production services, resource limits, healthchecks, networks and volumes.
- `Dockerfile.production` — multi-stage production build for the honeypot app (uses virtualenv, minimal runtime image, non-root user, exposes 8080).
- `.env.production` — production environment variables (Postgres/Redis passwords, API keys, Grafana creds).
- `docker/prometheus/prometheus.yml` — scrape and job configuration (jobs for prometheus self, node-exporter, cadvisor, honeypot-api, ai-engine, etc.).
- `docker/prometheus/alerts.yml` — alert rules (ServiceDown, HighCPUUsage, HighAttackRate, RedisDown, PostgreSQLDown, HighErrorRate, etc.).
- `docker/alertmanager/alertmanager.yml` — routing, receivers (Slack/email), inhibition rules and grouping.
- `docker/grafana/datasources/prometheus.yml` — pre-configures Prometheus as Grafana datasource.
- `docker/postgres/init.sql` — schema and tables (honeypot.attack_events, connection_logs, analytics tables).

---

## 7. Data flow (step-by-step, simplified)

1. Attacker connects → honeypot receives TCP/HTTP/SSH request.
2. Honeypot logs event locally (JSON line) and writes pcap if configured.
3. Honeypot pushes event to Redis queue (or directly to a worker API).
4. Worker/processor consumes from Redis, enriches (geoip, reputation), stores in Postgres tables.
5. Honeypot increments Prometheus metrics (counters/gauges/histograms) via client library.
6. Prometheus scrapes `/metrics` periodically and stores timeseries.
7. Prometheus evaluates alerting rules; when conditions match it fires alerts to Alertmanager.
8. Alertmanager routes alerts to configured receivers (Slack/email/Webhook) depending on routing rules.
9. Grafana reads Prometheus and shows dashboards; operators use Grafana to drill into incidents.
10. AI Engine (if used) reads DB or queue, classifies incidents, and suggests playbooks.

---

## 8. Where artifacts live (paths)

- Application logs: `./logs/` or inside container `/app/logs/` — JSON lines and human logs.
- Captures/pcaps: `./data/captures/*.pcap` or `/app/data/captures/` in container.
- Sample binaries: `./data/malware/<hash>.bin`.
- Postgres data volume (persistent): `postgres_data` volume mapped to `/var/lib/postgresql/data`.
- Prometheus data: `prometheus_data` volume mapped to `/prometheus`.
- Grafana DB: `grafana_data`.
- Alertmanager data: `alertmanager_data`.

---

## 9. Database schemas & key tables (short)

- Schemas: `honeypot`, `monitoring`, `analytics`.
- Key tables (from `docker/postgres/init.sql`):
  - `honeypot.attack_events`: uuid, timestamp, src_ip, dst_port, payload, attack_type, severity, geolocation (JSON), metadata (JSON).
  - `honeypot.connection_logs`: connection-level logs (duration, bytes, status).
  - `honeypot.credentials_attempted`: recorded login attempts.
  - `honeypot.malware_samples`: file metadata (hash, path, size, analyzed flag).
  - `monitoring.system_metrics`: cpu, memory, disk, network
  - `analytics.daily_attack_stats`, `analytics.attacker_profiles`.

---

## 10. Prometheus alerts summary (high level)

Examples of alert rules present:
- ServiceDown (honeypots, ai-engine, dashboard) — critical
- HighCPUUsage / HighMemoryUsage — warning
- DiskSpaceRunningOut — warning/critical
- PostgreSQLDown, RedisDown — critical
- HighErrorRate (5xx in honeypot) — warning
- SlowResponseTime — warning

These rules are defined in `docker/prometheus/alerts.yml`. Alertmanager routes and groups alerts based on severity and category.

---

## 11. API endpoints (honeypot FastAPI)

- GET /health — health check
- GET /metrics — Prometheus metrics
- POST /api/attack — submit an attack event (internal use or tests)
- GET /api/attacks — list recent attacks (paginated)
- Additional endpoints may exist under `src/api` — check `src/api/main.py` for full routes.

---

## 12. Example event (JSON) — upload to LLM for examples

```json
{
  "id": "b3f5a6b4-...",
  "timestamp": "2025-10-28T23:01:13.123Z",
  "src_ip": "203.0.113.45",
  "src_port": 52112,
  "dst_ip": "198.51.100.10",
  "dst_port": 8080,
  "protocol": "http",
  "attack_type": "http_login_bruteforce",
  "user_agent": "Mozilla/5.0 (compatible; scanner/1.0)",
  "payload_sample": "/data/malware/20251028_b3f5a6.bin",
  "reputation": {"abuseipdb_score": 92, "virus_total": "unknown"},
  "geo": {"country": "EG", "city": "Cairo"},
  "notes": "First seen: 2025-10-28T23:00:59Z"
}
```

Include several such events when uploading to an AI so it can learn the patterns and answer incident-specific queries.

---

## 13. Example pcap note (what to give the AI)

- Provide a short description instead of full pcap when uploading to LLM (pcap is binary): "pcap of TCP session from 203.0.113.45 to 198.51.100.10 port 8080, includes HTTP POST to /login with payload 'username=admin&password=test' and returned 200 OK". If the LLM allows files, add the pcap separately.

---

## 14. Security & isolation notes (important to communicate to any AI or operator)

- The honeypot is intentionally permissive to attract attackers but must be isolated from production (separate Docker networks, egress controls). Do NOT reuse production secrets in `.env.production` in the honeypot environment.
- Containers run with `no-new-privileges` and `cap_drop: ALL` where possible.
- File uploads and samples are stored in `data/malware/` and should be analyzed in an isolated sandbox.

---

## 15. Useful commands to include with the file (copyable)

```powershell
# From A:\cyber_mirage
# Build production images
docker-compose -f docker-compose.production.yml build
# Start production
docker-compose -f docker-compose.production.yml up -d
# Show containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
# Tail logs for alertmanager
docker-compose logs -f alertmanager
# Export a Postgres dump
docker exec -t cyber_mirage_postgres pg_dump -U cybermirage cyber_mirage > backup.sql
```

---

## 16. Recommended prompts to give the AI (examples)

When you upload this file to an LLM, use prompts like:

- "You are an expert on the Cyber Mirage repository (file context provided). Explain the exact path an HTTP brute-force attack takes from connection to alert, referencing file paths and tables where evidence is stored."
- "Given the example event JSON provided, produce a step-by-step SOC playbook (actions, commands, timeframe) to respond and contain the incident."
- "List all files that would contain evidence of an attack from `203.0.113.45` targeting `198.51.100.10:8080`. Include exact file paths and DB tables."
- "Summarize the Prometheus alerting rules that would fire for a spike in honeypot attacks and how Alertmanager will route them."
- "If a file sample is saved under `data/malware`, describe an isolated analysis workflow (sandboxing, static/dynamic analysis, reporting) suitable for this project."

Also include: "If you need clarification about a file or endpoint, ask a single clarifying question before answering." This helps the LLM avoid hallucinations.

---

## 17. How to chunk this file for LLM ingestion

- Use the JSON metadata + architecture section first for context (chunk 1). 
- Provide services & file list next (chunk 2). 
- Provide data flow and example events (chunk 3). 
- Provide commands and recommended prompts last (chunk 4).

If the model supports attachments, attach sample events and a representative pcap separately.

---

## 18. Known limitations & notes for the AI

- This file is a high-level single-document snapshot of the repository as of the creation time. For precise code logic, the model should be given `src/api/main.py` etc. if available.
- Binary pcaps and real sample files are not included in this text file; the AI cannot reconstruct raw packets from descriptions.
- Some runtime behaviors depend on environment variables in `.env.production` — do not assume defaults for sensitive secrets.

---

## 19. Checklist for uploading to any AI / knowledge-base

- [ ] Include this `PROJECT_CONTEXT_FOR_AI.md` as primary context file.
- [ ] Attach `src/api/main.py` and other source files for endpoint-level answers.
- [ ] Attach `docker-compose.production.yml` and `Dockerfile.production` for build/run questions.
- [ ] Attach sample event JSONs (3–10 examples) and one pcap summary (text) or pcap file if supported.
- [ ] Provide instructions: "Answer as a security analyst; reference file paths, DB tables, and exact commands." 

---

## 20. Final short paragraph for the AI to follow

When answering, always: reference file paths and config names, prefer exact commands to perform actions, state assumptions clearly (e.g., "assuming the `.env.production` contains X"), and ask a clarifying question if the user's question depends on runtime details not in the provided context.

---

(End of `PROJECT_CONTEXT_FOR_AI.md`)
