# BBSS — Behavior-Based Security System

> **Authentication beyond passwords.**  
> A modular, production-grade behavioral biometrics engine that detects anomalous access patterns using statistical analysis and machine learning, even when credentials are correct.
---
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-pytest-yellow)
![Status](https://img.shields.io/badge/status-active-success)
---

## Table of Contents

- [Overview](#overview)
- [Motivation](#motivation)
- [System Architecture](#system-architecture)
- [Core Modules](#core-modules)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Development Phases](#development-phases)
  - [Phase 1 — Foundation & Authentication](#phase-1--foundation--authentication)
  - [Phase 2 — Behavior Capture Engine](#phase-2--behavior-capture-engine)
  - [Phase 3 — Behavior Profiling & Anomaly Detection](#phase-3--behavior-profiling--anomaly-detection)
  - [Phase 4 — Risk Scoring & Security Response](#phase-4--risk-scoring--security-response)
  - [Phase 5 — Logging & Audit System](#phase-5--logging--audit-system)
  - [Phase 6 — MVP Completion & Hardening](#phase-6--mvp-completion--hardening)
  - [Phase 7 — Machine Learning Integration](#phase-7--machine-learning-integration)
  - [Phase 8 — API Layer (Future)](#phase-8--api-layer-future)
- [MVP Feature Checklist](#mvp-feature-checklist)
- [Future Features](#future-features)
- [Security Considerations](#security-considerations)
- [Environment Variables](#environment-variables)
- [Installation & Setup](#installation--setup)
- [Running the System](#running-the-system)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

BCSS (Behavior-Based Security System) is a Python-based authentication and threat detection engine that goes beyond password verification. It continuously monitors and learns how individual users behave — their typing patterns, session timing, and command usage — and flags sessions that deviate significantly from established baselines.

The system assigns a **risk score** to every session based on multi-signal behavioral analysis. Risk scores trigger tiered responses: allow, warn, challenge, or block. All decisions are logged with full audit trails.

BCSS is designed as a backend security layer, suitable for integration into any application requiring continuous authentication and insider threat detection.

---

## Motivation

Traditional authentication is binary: the correct password grants full access. This model is fundamentally broken in practice:

- Credentials are stolen through phishing, data breaches, and social engineering
- Shared or borrowed credentials are indistinguishable from legitimate use
- Once authenticated, a session is trusted for its full duration
- There is no mechanism to detect when a legitimate session is hijacked mid-flight

**Behavioral biometrics** addresses all four of these gaps. By building a model of *how* a user behaves — not just *what they know* — the system can raise alerts when something feels wrong, even with valid credentials.

This same principle underlies:

- Banking fraud detection systems (transaction behavioral analysis)
- Enterprise UEBA platforms (User and Entity Behavior Analytics)
- Continuous authentication in high-security environments
- Insider threat detection in corporate security tooling

BCSS brings this concept to a self-contained, auditable Python implementation.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        BCSS Core Engine                     │
│                                                             │
│  ┌──────────────┐    ┌──────────────────┐                  │
│  │ Auth Engine  │───▶│ Behavior Capture │                  │
│  └──────────────┘    └────────┬─────────┘                  │
│                               │                             │
│                               ▼                             │
│                    ┌──────────────────────┐                 │
│                    │  Behavior Profile    │                 │
│                    │  Builder (Baseline)  │                 │
│                    └──────────┬───────────┘                 │
│                               │                             │
│                               ▼                             │
│                    ┌──────────────────────┐                 │
│                    │  Anomaly Detection   │                 │
│                    │  Engine              │                 │
│                    └──────────┬───────────┘                 │
│                               │                             │
│                               ▼                             │
│                    ┌──────────────────────┐                 │
│                    │  Risk Scoring System │                 │
│                    └──────────┬───────────┘                 │
│                               │                             │
│                               ▼                             │
│                    ┌──────────────────────┐                 │
│                    │  Security Response   │                 │
│                    │  Module              │                 │
│                    └──────────┬───────────┘                 │
│                               │                             │
│                               ▼                             │
│                    ┌──────────────────────┐                 │
│                    │  Logging & Audit     │                 │
│                    │  System              │                 │
│                    └──────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
         SQLite DB       Log Files         (Future)
         (MVP)                             PostgreSQL
                                           Redis Cache
                                           FastAPI Dashboard
```

### Data Flow

```
User Login Attempt
       │
       ▼
[Auth Engine] → Verify credentials → Fail → Deny access
       │
       │ (credentials valid)
       ▼
[Behavior Capture] → Collect session metrics
       │
       ▼
[Profile Builder] → Fetch user behavioral baseline
       │
       ▼
[Anomaly Detection] → Compare current session vs baseline
       │
       ▼
[Risk Scoring] → Compute weighted risk score (0–100)
       │
       ├── Score 0–30  → SAFE    → Grant access
       ├── Score 31–60 → WARNING → Secondary verification
       └── Score 61–100→ HIGH RISK → Block + alert
                │
                ▼
        [Logging System] → Persist all events
```

---

## Core Modules

### Module 1 — Authentication Engine (`auth/`)

Handles all credential-based authentication operations.

**Responsibilities:**
- User registration with secure password storage
- Login with credential verification
- Password hashing using Argon2id (memory-hard, resistant to GPU attacks)
- Secure token generation for session management
- Account lockout after repeated failed attempts

**Key decisions:**
- Argon2id is used over bcrypt/scrypt due to superior side-channel resistance and OWASP recommendation
- Tokens are generated with Python's `secrets` module (cryptographically secure CSPRNG)
- Raw passwords never persist beyond the immediate hashing operation

---

### Module 2 — Behavior Capture Engine (`behavior/capture.py`)

The data collection layer. Captures measurable behavioral signals during every authenticated session.

**Signals Captured:**

| Signal | Description | Storage |
|--------|-------------|---------|
| `typing_time` | Time (seconds) from first to last keystroke during password entry | `REAL` |
| `login_hour` | Hour of day (0–23) the session was initiated | `INTEGER` |
| `login_day_of_week` | Day of week (0=Monday, 6=Sunday) | `INTEGER` |
| `session_duration` | Total time (seconds) the session remained active | `REAL` |
| `command_count` | Number of actions/commands executed during session | `INTEGER` |
| `commands_used` | Ordered list of commands executed (stored as JSON array) | `TEXT` |
| `ip_address` | IP of the session initiator (for network anomaly detection) | `TEXT` |
| `user_agent` | Client identifier string, if applicable | `TEXT` |

**Design note:** All capture operations are non-blocking and fail silently — a capture failure must never interrupt an authenticated session. Capture errors are logged separately.

---

### Module 3 — Behavior Profile Builder (`behavior/profile.py`)

Builds and maintains a statistical baseline per user from their historical session data.

**Baseline Metrics Computed:**

| Metric | Computation |
|--------|-------------|
| `avg_typing_time` | Rolling mean of last N sessions |
| `std_typing_time` | Standard deviation (used for z-score thresholding) |
| `typical_login_hours` | Histogram of login hours → IQR-based typical range |
| `avg_session_duration` | Rolling mean |
| `avg_command_count` | Rolling mean |
| `common_commands` | Top-K commands by frequency |
| `known_ips` | Set of previously seen IP addresses |

**Cold Start Handling:**

A new user has no behavioral baseline. The system handles this in three stages:

1. **Bootstrapping (Sessions 1–4):** No anomaly detection runs. All sessions are treated as safe and stored as baseline data. User is informed their profile is being built.
2. **Warm-up (Sessions 5–9):** Anomaly detection runs with a higher tolerance threshold (lower sensitivity). Risk score contributions are halved.
3. **Active (Session 10+):** Full anomaly detection with normal thresholds.

The minimum session count before full detection is configurable via `config.py`.

---

### Module 4 — Anomaly Detection Engine (`behavior/anomaly.py`)

The intelligence layer. Compares current session behavior against the established baseline and identifies deviations.

**Detection Methods:**

**MVP — Statistical Detection:**

Z-score based deviation check for continuous signals:

```
z = (current_value - baseline_mean) / baseline_std
```

If `|z| > threshold` (default: 2.0), the signal is flagged as anomalous.

For categorical/time signals (login hour, day of week), IQR-based range checking is used:
- If `login_hour` falls outside `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]` of historical login hours, it is flagged.

**Phase 7 — ML Detection (Isolation Forest):**

Isolation Forest is an unsupervised anomaly detection algorithm well-suited to this domain:
- Trained on a user's historical `[typing_time, login_hour, session_duration, command_count]` vectors
- No labeled anomaly data required
- Produces a binary `normal / anomalous` classification per session
- Model is retrained periodically as new session data accumulates

---

### Module 5 — Risk Scoring System (`security/risk.py`)

Converts multiple anomaly signals into a single, interpretable risk score.

**Scoring Table (MVP):**

| Anomaly Signal | Risk Points Added |
|----------------|------------------|
| Typing time deviation (z > 2.0) | +20 |
| Unusual login hour | +25 |
| Unusual login day | +10 |
| Unknown IP address | +20 |
| Command count anomaly | +15 |
| Unknown commands detected | +10 |
| Session duration anomaly | +10 |
| ML model flags as anomalous (Phase 7) | +30 |

**Risk Level Thresholds:**

| Score Range | Level | Response |
|-------------|-------|----------|
| 0 – 30 | SAFE | Allow session |
| 31 – 60 | WARNING | Require secondary PIN verification |
| 61 – 100 | HIGH RISK | Block session, log alert |

All weights and thresholds are configurable in `config.py`. No hardcoded magic numbers exist in module logic.

---

### Module 6 — Security Response Module (`security/response.py`)

Executes the appropriate action based on the computed risk score.

**Response Actions:**

- `ALLOW` — Session proceeds normally. Behavior data is saved for future profiling.
- `CHALLENGE` — Session is paused. User must provide a secondary PIN or OTP. On success: session resumes. On failure: session is blocked and logged.
- `BLOCK` — Session is immediately terminated. Event is logged with full details. Future implementation: alert can be dispatched to a configured webhook or email.

**Post-Response:**

Regardless of response outcome, all session data (behavior metrics, risk score, decision) is persisted to the database for audit purposes.

---

### Module 7 — Logging & Audit System (`logs/logger.py`)

Provides structured, tamper-evident logging of all security events.

**Log Levels:**

| Level | Events |
|-------|--------|
| `INFO` | Successful logins, session creation |
| `WARNING` | Risk score in WARNING range, failed secondary verification |
| `ERROR` | Risk score in HIGH RISK range, blocked sessions |
| `CRITICAL` | System errors, database failures |

**Logged Fields per Event:**

```json
{
  "event_id": "uuid4",
  "timestamp": "ISO 8601",
  "username": "string",
  "user_id": "integer",
  "event_type": "LOGIN_ALLOWED | LOGIN_CHALLENGED | LOGIN_BLOCKED",
  "risk_score": "integer",
  "anomaly_signals": ["list of triggered anomalies"],
  "behavior_snapshot": {
    "typing_time": "float",
    "login_hour": "integer",
    "command_count": "integer",
    "ip_address": "string"
  },
  "decision": "ALLOW | CHALLENGE | BLOCK"
}
```

Logs are written to both a rotating file handler and the `risk_logs` database table. Log files rotate daily with a 30-day retention policy.

---

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Language | Python 3.11+ | Rich security/ML ecosystem, readability |
| Password Hashing | `argon2-cffi` | OWASP-recommended, memory-hard |
| Token Generation | `secrets` (stdlib) | Cryptographically secure CSPRNG |
| Database (MVP) | SQLite via `sqlite3` | Zero-config, portable for MVP |
| Database (Production) | PostgreSQL via `psycopg2` | ACID compliance, concurrent access |
| ML Framework | `scikit-learn` | Isolation Forest implementation |
| Numerical | `NumPy` | Statistical computations |
| Configuration | `python-dotenv` | Environment-based config management |
| Testing | `pytest` + `pytest-cov` | Coverage reporting |
| Logging | `logging` (stdlib) | Rotating file handler, structured output |
| (Future) Cache | Redis | Session storage, rate limiting |
| (Future) API | FastAPI | REST API backend |

---

## Database Schema

### `users`

```sql
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,
    email           TEXT UNIQUE,
    password_hash   TEXT NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### `behavior_logs`

```sql
CREATE TABLE behavior_logs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    typing_time         REAL,
    login_hour          INTEGER,
    login_day_of_week   INTEGER,
    session_duration    REAL,
    command_count       INTEGER DEFAULT 0,
    commands_used       TEXT,           -- JSON array
    ip_address          TEXT,
    user_agent          TEXT,
    timestamp           TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### `behavior_profiles`

```sql
CREATE TABLE behavior_profiles (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    avg_typing_time         REAL,
    std_typing_time         REAL,
    avg_session_duration    REAL,
    avg_command_count       REAL,
    typical_login_hours     TEXT,       -- JSON array
    common_commands         TEXT,       -- JSON array
    known_ips               TEXT,       -- JSON array
    session_count           INTEGER NOT NULL DEFAULT 0,
    profile_status          TEXT NOT NULL DEFAULT 'bootstrapping',  -- bootstrapping | warmup | active
    last_updated            TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### `risk_logs`

```sql
CREATE TABLE risk_logs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    behavior_log_id     INTEGER REFERENCES behavior_logs(id),
    risk_score          INTEGER NOT NULL,
    risk_level          TEXT NOT NULL,      -- SAFE | WARNING | HIGH_RISK
    anomaly_signals     TEXT,               -- JSON array of triggered signals
    decision            TEXT NOT NULL,      -- ALLOW | CHALLENGE | BLOCK
    secondary_auth      INTEGER DEFAULT 0,  -- 1 if secondary auth was triggered
    secondary_passed    INTEGER,            -- 1 = passed, 0 = failed, NULL = not triggered
    timestamp           TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### `sessions`

```sql
CREATE TABLE sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at  TEXT NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1,
    ip_address  TEXT,
    user_agent  TEXT
);
```

---

## Project Structure

```
bbss/
│
├── README.md
├── pyproject.toml              # Package metadata and build configuration
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
│
├── src/
│   └── bbss/                  # Main package
│       ├── __init__.py        # Package entry point (BBSS class, functions)
│       ├── config.py          # Central configuration (thresholds, limits, paths)
│       │
│       ├── auth/              # Authentication module
│       │   ├── signup.py      # User registration logic
│       │   ├── login.py       # Credential verification + session creation
│       │   └── hashing.py     # Argon2 password hashing + token generation
│       │
│       ├── behavior/           # Behavioral biometrics module
│       │   ├── capture.py     # Behavioral signal collection
│       │   ├── profile.py     # Baseline builder and updater
│       │   └── anomaly.py     # Statistical + ML anomaly detection
│       │
│       ├── security/          # Security module
│       │   ├── risk.py        # Risk score computation
│       │   └── response.py    # Response action dispatcher
│       │
│       ├── database/          # Database module
│       │   ├── db.py          # Connection management, migrations
│       │   └── models.py      # Table definitions + query helpers
│       │
│       ├── logs/              # Logging module
│       │   ├── logger.py      # Logging setup + structured event logger
│       │   └── audit.py      # Audit trail query helpers
│       │
│       ├── ml/                # Machine learning module
│       │   ├── features.py    # Feature extraction
│       │   ├── model.py       # Isolation Forest training + inference
│       │   └── trainer.py     # Model retraining pipeline
│       │
│       └── utils/             # Utilities module
│           └── helpers.py     # Shared utilities (time formatting, JSON helpers)
│
└── tests/
    ├── conftest.py            # Pytest fixtures (in-memory DB, mock users)
    ├── test_auth.py
    ├── test_behavior.py
    ├── test_anomaly.py
    ├── test_risk.py
    ├── test_response.py
    ├── test_logging.py
    └── test_ml.py
```

---

## Development Phases

### Phase 1 — Foundation & Authentication

**Goal:** A working, secure authentication system with a properly initialized database.

**Steps:**

1. Set up project directory structure as defined above
2. Create `requirements.txt` with initial dependencies: `argon2-cffi`, `python-dotenv`
3. Create `.env.example` with all required environment variable keys (no values)
4. Implement `config.py` — load all configuration from environment with safe defaults
5. Implement `database/db.py`:
   - SQLite connection with WAL mode enabled (better concurrent read performance)
   - Schema initialization function (`init_db()`) that creates all tables if not exist
   - Context manager for safe connection handling
6. Implement `database/models.py`:
   - `create_user(username, password_hash, email=None)`
   - `get_user_by_username(username) → dict | None`
   - `get_user_by_id(user_id) → dict | None`
   - `increment_failed_attempts(user_id)`
   - `reset_failed_attempts(user_id)`
   - `lock_account(user_id, until_datetime)`
7. Implement `auth/hashing.py`:
   - `hash_password(plain_text) → str` (Argon2id)
   - `verify_password(plain_text, hash) → bool`
   - `generate_token() → str` (32-byte hex via `secrets`)
   - `hash_token(token) → str` (SHA-256 for DB storage)
8. Implement `auth/signup.py`:
   - Validate username (length, allowed characters, uniqueness)
   - Validate password (minimum length, complexity rules)
   - Hash password and persist user record
   - Return structured result: `{success: bool, user_id: int | None, error: str | None}`
9. Implement `auth/login.py`:
   - Check account existence
   - Check account lock status
   - Verify password hash
   - On success: create session record, return session token
   - On failure: increment failed attempts, apply lockout if threshold exceeded
10. Write `tests/test_auth.py` with full coverage of signup, login, lockout, and token generation
11. Verify all tests pass

**Exit Criteria:** Users can register and authenticate. Passwords are hashed. Failed logins enforce lockout. Sessions are created and stored.

---

### Phase 2 — Behavior Capture Engine

**Goal:** Every successful login session captures behavioral signals and persists them.

**Steps:**

1. Add `behavior_logs` table to schema (already defined; ensure `init_db()` creates it)
2. Implement `behavior/capture.py`:
   - `CaptureContext` class or equivalent — a lightweight object passed through a session
   - `record_typing_time(start: float, end: float) → float`
   - `record_login_time() → dict` returns `{hour: int, day_of_week: int, timestamp: str}`
   - `record_command(command_name: str)` — appends to session command list
   - `record_session_end(start_time: float)` — computes session duration
   - `save_behavior_log(user_id, capture_context) → int` — persists to `behavior_logs`, returns log ID
3. Add `create_behavior_log(...)` and `get_behavior_logs_by_user(user_id, limit=50)` to `database/models.py`
4. Integrate capture into `auth/login.py` — after successful credential verification, instantiate capture context and attach to session
5. Implement graceful failure: if any capture operation raises an exception, log the error and continue — never block the authenticated session
6. Write `tests/test_behavior.py` covering signal capture accuracy, edge cases (zero typing time, no commands), and DB persistence

**Exit Criteria:** Every successful login persists a complete behavior record. Capture failures do not block authentication.

---

### Phase 3 — Behavior Profiling & Anomaly Detection

**Goal:** The system learns each user's normal behavior and detects deviations.

**Steps:**

1. Add `behavior_profiles` table to schema; update `init_db()`
2. Implement `behavior/profile.py`:
   - `build_profile(user_id) → dict` — queries last N behavior logs and computes all baseline metrics
   - `update_profile(user_id)` — called after each session to keep baseline current
   - `get_profile(user_id) → dict | None`
   - `get_profile_status(user_id) → str` — returns `bootstrapping | warmup | active`
   - Implement cold start logic:  
     - `session_count < 5` → status `bootstrapping`  
     - `5 ≤ session_count < 10` → status `warmup`  
     - `session_count ≥ 10` → status `active`
3. Add profile CRUD to `database/models.py`
4. Implement `behavior/anomaly.py`:
   - `detect_anomalies(current_behavior: dict, profile: dict) → list[str]`
   - Z-score check for `typing_time`, `session_duration`, `command_count`
   - IQR check for `login_hour`, `login_day_of_week`
   - IP address novelty check against `known_ips`
   - Unknown command detection against `common_commands`
   - Return list of triggered anomaly signal names (empty list = no anomalies)
   - Apply reduced sensitivity during `warmup` status
   - Return empty list immediately during `bootstrapping` status
5. Write `tests/test_anomaly.py` covering: no anomaly (typical session), single anomaly, multiple anomalies, cold start bypass, warmup sensitivity

**Exit Criteria:** System correctly identifies behavioral deviations in test scenarios. Cold start is handled safely.

---

### Phase 4 — Risk Scoring & Security Response

**Goal:** Detected anomalies are converted to a risk score that drives an automated security decision.

**Steps:**

1. Implement `security/risk.py`:
   - `compute_risk_score(anomaly_signals: list[str]) → int`
   - Load signal weights from `config.py` (not hardcoded)
   - Cap total score at 100
   - `classify_risk(score: int) → str` — returns `SAFE | WARNING | HIGH_RISK`
2. Implement `security/response.py`:
   - `dispatch_response(risk_level: str, user_id: int, session_context: dict) → dict`
   - `SAFE` → `{action: "ALLOW"}`
   - `WARNING` → trigger secondary verification, return result
   - `HIGH_RISK` → `{action: "BLOCK"}`, deactivate session token
   - Secondary verification: generate a 6-digit PIN, "deliver" it (print to stdout for MVP, configurable transport later), accept user input, verify
3. Add `create_risk_log(...)` and `get_risk_logs_by_user(user_id, limit=50)` to `database/models.py`
4. Integrate risk scoring into the main session flow after anomaly detection
5. Write `tests/test_risk.py` and add response scenarios to test suite

**Exit Criteria:** Every session receives a risk score and corresponding action. Secondary verification flow works end-to-end.

---

### Phase 5 — Logging & Audit System

**Goal:** Every security event is logged in both structured file output and the database.

**Steps:**

1. Implement `logs/logger.py`:
   - Configure Python `logging` with two handlers:
     - `RotatingFileHandler` — daily rotation, 30-day retention, JSON-formatted records
     - `StreamHandler` — development-mode console output (disabled in production via config)
   - `log_event(event_type, user_id, username, risk_score, anomaly_signals, behavior_snapshot, decision)`
   - Log levels mapped to event types (ALLOW → INFO, CHALLENGE → WARNING, BLOCK → ERROR)
2. Implement `logs/audit.py`:
   - `get_user_audit_trail(user_id, limit=100) → list[dict]`
   - `get_recent_high_risk_events(hours=24) → list[dict]`
   - `get_risk_summary_by_user(user_id) → dict` — counts by decision type
3. Ensure all existing modules emit proper log calls on all relevant events (auth failures, capture errors, anomaly triggers, score computations, decisions)
4. Write `tests/test_logging.py` verifying log output structure and database audit queries

**Exit Criteria:** All security events are logged with full context. Audit queries return correct data.

---

### Phase 6 — MVP Completion & Hardening

**Goal:** All modules are integrated, edge cases are handled, and the system is clean, testable, and documented.

**Steps:**

1. Implement `main.py` — end-to-end integration of all modules for a complete login flow:
   ```
   signup(username, password)
   login(username, password, typing_time, ip) → SessionResult
   execute_command(session_token, command_name)
   end_session(session_token)
   ```
2. Implement `config.py` fully — all thresholds, weights, limits, database path, log path externalized
3. Security hardening review:
   - Verify no raw passwords appear in logs
   - Verify session tokens are hashed before DB storage
   - Verify all DB queries use parameterized statements (no string interpolation)
   - Verify account lockout is enforced correctly
   - Verify behavior logs cannot be queried across users (IDOR prevention)
4. Write or complete `conftest.py` with:
   - In-memory SQLite fixture (isolated per test)
   - Mock user factory
   - Mock behavior log factory
   - Mock session context factory
5. Run full test suite, achieve ≥ 80% coverage
6. Write `CHANGELOG.md` for MVP version (v0.1.0)
7. Tag `v0.1.0` release

**Exit Criteria:** Full integration test passes. No raw credentials in logs. Test coverage ≥ 80%. Repository is clean and documented.

---

### Phase 7 — Machine Learning Integration

**Goal:** Replace or augment statistical anomaly detection with a trained Isolation Forest model per user.

**Steps:**

1. Add `scikit-learn` and `NumPy` to `requirements.txt`
2. Implement `ml/model.py`:
   - `train_model(user_id) → IsolationForest` — trains on user's `behavior_logs` history
   - `predict(model, behavior_vector: list) → str` — returns `"normal" | "anomalous"`
   - `save_model(model, user_id)` — serializes to disk with `joblib`
   - `load_model(user_id) → IsolationForest | None`
3. Implement `ml/trainer.py`:
   - `should_retrain(user_id) → bool` — true if N new sessions since last training
   - `retrain_if_needed(user_id)` — called after each session update
   - Minimum session requirement before first training: configurable (default: 20)
4. Integrate ML prediction into `behavior/anomaly.py`:
   - If model exists and profile is `active`, run prediction
   - If ML flags anomalous: add `"ml_isolation_forest"` to anomaly signals list
   - If no model yet: fall back to statistical detection only
5. Add `ml_model_version` and `last_trained` fields to `behavior_profiles` table
6. Write `tests/test_ml.py` with synthetic behavioral data

**Exit Criteria:** Isolation Forest model trains correctly on synthetic data and produces expected anomaly classifications.

---

### Phase 8 — API Layer (Future)

**Goal:** A RESTful API layer for programmatic access to BBSS functionality.

**Planned Features:**

- RESTful API for all BBSS operations
- API key authentication
- Rate limiting
- OpenAPI/Swagger documentation
- WebSocket support for real-time alerts

**Planned Stack:**
- FastAPI for the API layer
- Optional Redis for caching and rate limiting
- Docker Compose for local development environment

---

## MVP Feature Checklist

- [x] User registration with Argon2id password hashing
- [x] Login with credential verification and session token issuance
- [x] Account lockout after configurable failed attempt threshold
- [x] Behavior signal capture (typing time, login hour, session duration, commands, IP)
- [x] Per-user behavioral baseline computation
- [x] Cold start handling (bootstrapping and warmup stages)
- [x] Statistical anomaly detection (z-score + IQR)
- [x] Weighted risk scoring (0–100)
- [x] Tiered risk classification (SAFE / WARNING / HIGH RISK)
- [x] Secondary PIN verification challenge flow
- [x] Session blocking on HIGH RISK
- [x] Structured security event logging (file + database)
- [x] Audit trail queries
- [x] SQLite persistence with parameterized queries
- [x] Full test suite (≥ 80% coverage)
- [x] All configuration externalized to environment variables

---

## Future Features

| Feature | Phase | Priority |
|---------|-------|----------|
| Isolation Forest ML model | 7 | High |
| Automatic model retraining pipeline | 7 | High |
| REST API (FastAPI) | 8 | Medium |
| Real-time WebSocket event stream | 8 | Medium |
| PostgreSQL support | Post-MVP | Medium |
| Redis session storage | Post-MVP | Medium |
| Webhook/email alerting on HIGH RISK events | Post-MVP | Medium |
| Multi-factor authentication (TOTP) | Post-MVP | High |
| IP geolocation anomaly detection | Post-MVP | Low |
| Device fingerprinting | Post-MVP | Low |
| API key authentication mode | Post-MVP | Low |
| Docker Compose deployment configuration | Post-MVP | Medium |
| GDPR-compliant data deletion per user | Post-MVP | Medium |
| Behavioral profile export/import | Post-MVP | Low |

---

## Security Considerations

### Password Storage
All passwords are hashed with **Argon2id** using parameters meeting or exceeding OWASP recommendations:
- Memory: 64MB minimum
- Iterations: 3
- Parallelism: 4

Raw passwords are never logged, returned in API responses, or persisted anywhere other than the transient hashing operation.

### Session Tokens
Session tokens are:
- Generated with `secrets.token_hex(32)` (256 bits of entropy)
- Hashed with SHA-256 before database storage
- The raw token is only returned once at session creation and never stored in plain form

### SQL Injection
All database queries use parameterized statements. String interpolation into SQL is forbidden and treated as a critical bug.

### Behavioral Data Privacy
Behavioral logs contain timing data and command history. In any production deployment, this data must be:
- Encrypted at rest (PostgreSQL column encryption or full-disk encryption)
- Scoped strictly to the owning user (no cross-user queries without admin privilege)
- Subject to a defined retention policy (default: 90 days)
- Documented in user-facing privacy policy

### Audit Log Integrity
Audit logs are append-only by design. No update or delete operations are performed on `risk_logs`. Log files use rotation without truncation.

### Account Lockout
Repeated failed login attempts trigger a time-based lockout. Lockout duration is configurable. Failed attempt counts reset on successful authentication.

---

## Environment Variables

Copy `.env.example` to `.env` and populate before running.

```env
# Database
DATABASE_PATH=./bcss.db               # Path to SQLite database file
DATABASE_URL=                         # PostgreSQL DSN (Phase 8+)

# Security
SECRET_KEY=                           # Random 32-byte hex string for HMAC operations
SESSION_EXPIRY_HOURS=24               # Session token TTL
MAX_FAILED_ATTEMPTS=5                 # Login failures before lockout
LOCKOUT_DURATION_MINUTES=30           # Account lockout duration

# Anomaly Detection
MIN_SESSIONS_BOOTSTRAPPING=5         # Sessions before any detection runs
MIN_SESSIONS_WARMUP=10               # Sessions before full sensitivity
ZSCORE_THRESHOLD=2.0                 # Z-score above which a signal is flagged
IQR_MULTIPLIER=1.5                   # IQR multiplier for time-based anomalies

# Risk Scoring Weights
RISK_WEIGHT_TYPING_TIME=20
RISK_WEIGHT_LOGIN_HOUR=25
RISK_WEIGHT_LOGIN_DAY=10
RISK_WEIGHT_UNKNOWN_IP=20
RISK_WEIGHT_COMMAND_COUNT=15
RISK_WEIGHT_UNKNOWN_COMMANDS=10
RISK_WEIGHT_SESSION_DURATION=10
RISK_WEIGHT_ML_FLAG=30

# Risk Thresholds
RISK_THRESHOLD_WARNING=31
RISK_THRESHOLD_HIGH=61

# Logging
LOG_DIR=./logs
LOG_LEVEL=INFO                        # DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_RETENTION_DAYS=30
CONSOLE_LOGGING=true                  # Set false in production

# ML (Phase 7)
ML_MIN_SESSIONS_FOR_TRAINING=20
ML_RETRAIN_EVERY_N_SESSIONS=10
ML_MODELS_DIR=./ml/models
```

---

## Installation & Setup

**Requirements:** Python 3.11+

```bash
# Clone the repository
git clone https://github.com/Favour-OE/behavior-based-security-system.git
cd behavior-based-security-system

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install the package in development mode
pip install -e .

# Install dev dependencies (for testing)
pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Edit .env and populate any required values

# Initialize the database
python -c "from bbss.database import init_db; init_db()"
```

---

## Running the System

BBSS is a Python package that you integrate into your application:

```python
from bbss import signup, login, execute_command, end_session

# Register a new user
result = signup(username="john_doe", password="SecurePassword123!")
print(result)  # {"success": True, "user_id": 1}

# Authenticate a user
result = login(
    username="john_doe",
    password="SecurePassword123!",
    typing_time=2.14,
    ip_address="192.168.1.10"
)
print(result)
# {"success": True, "session_token": "...", "risk_score": 10, "decision": "ALLOW", ...}

if result["success"] and result.get("session"):
    # Record a command during the session
    execute_command(result["session"], "view_report")
    
    # End the session
    end_session(result["session"])
```

### Using the BBSS Engine Class

For more control, use the `BBSS` class directly:

```python
from bbss import BBSS, Session

engine = BBSS()

# Signup
engine.signup("john_doe", "SecurePassword123!")

# Login
result = engine.login(
    username="john_doe",
    password="SecurePassword123!",
    typing_time=2.14,
    ip_address="192.168.1.10"
)

if result["success"]:
    session = result["session"]
    # Use session...
```

### Environment Variables

See `.env.example` for all configurable options. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `./bcss.db` | SQLite database path |
| `SECRET_KEY` | (none) | Random key for HMAC operations |
| `SESSION_EXPIRY_HOURS` | `24` | Session token lifetime |
| `MAX_FAILED_ATTEMPTS` | `5` | Failed logins before lockout |
| `ML_ENABLED` | `true` | Enable ML anomaly detection |

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Run a specific test module
pytest tests/test_auth.py -v

# Run tests matching a keyword
pytest -k "anomaly" -v
```

---

## Contributing

Contributions are welcome. Please follow this process:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Write tests for any new functionality
4. Ensure the full test suite passes: `pytest`
5. Ensure code is formatted: `black .` and `isort .`
6. Open a pull request with a clear description of the change

Please do not open PRs that reduce test coverage below 80%.

---

## License

MIT License. See [LICENSE](LICENSE) for full text.

---

*Built by [Favour](https://github.com/Favour-OE) — NissiByte*
