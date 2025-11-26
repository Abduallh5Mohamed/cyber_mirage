# Cyber Mirage – AI-driven Deception Controller

This document explains the concrete implementation of the AI Agent inside Cyber Mirage as delivered in this iteration.

## Overview
- **Module**: `src/ai_agent/deception_agent.py`
- **Integration point**: `src/honeypots/honeypot_manager.py`
- **Storage**: PostgreSQL tables `agent_decisions` and `deception_events`
- **Dashboard visibility**: `src/dashboard/real_dashboard.py` → AI Analysis tab

## Reinforcement-Learning Model
- Lightweight **tabular Q-learning** agent (`DeceptionAgent`).
- **State features** (`DeceptionState`):
  - service/protocol
  - command_count
  - data_exfil_attempts
  - auth_success flag
  - session duration bucket
  - last_command bucket (auth/list/download/etc)
  - suspicion score (derived from frequency and command mix)
- **Action space (`ActionType`)**:
  1. `maintain_session`
  2. `inject_delay`
  3. `swap_service_banner`
  4. `present_lure`
  5. `drop_session`
- **Reward shaping**: bonuses for credentials, downloads, uploads; penalties for escape attempts or early termination.
- **Persistence**: in-memory Q-table during runtime; every decision recorded in Postgres for observability and offline analysis.

## Honeypot Integration
1. Honeypot logs new session (existing behaviour) and now builds a session context.
2. Agent selects an action before any banner/response is sent:
   - Delay injection slows brute-force attempts.
   - Banner swap rotates service fingerprints.
   - Lure presentation enables fake assets (e.g., `finance_Q4_backup.zip`).
   - Drop session terminates risky flows.
3. Each FTP command updates the state, computes reward, triggers another agent decision, and optionally activates lure mode.
4. All decisions + deception events are stored via helper functions (`log_agent_decision`, `log_deception_event`).
5. `ensure_ai_tables()` provisions the required tables automatically on startup.

## Dashboard Enhancements
- **Main Dashboard**: A dedicated "🤖 AI Deception Agent" status card now appears at the top of the main page showing:
  - Current status (ACTIVE / STANDBY)
  - Total decisions count
  - Average reward (cumulative feedback)
  - Lures presented
  - Deception events count
  - Timestamp of last decision
- **AI Analysis tab** now shows:
  - Total decisions, average reward, lure count.
  - Recent decision table (action, reason, service, attacker origin).
  - Latest deception events rendered inline.

## Further Extension Points
- Replace tabular Q-learning with Deep RL using `stable-baselines3` if longer training history becomes available.
- Subscribe to Redis/Kafka streams so external services (e.g., isolation layer) consume the same decision feed.
- Export Q-table snapshots for offline training / evaluation.
