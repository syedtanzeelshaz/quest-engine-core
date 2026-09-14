# Quest Engine Core

Quest Engine Core is an enterprise-grade, multi-tenant AI data-access platform that allows users to interact with their business data through organization-created **AI Agents** using natural language, securely and reliably.

Instead of knowing where information lives or how to retrieve it, users can simply ask a question and Quest Engine finds the relevant information and provides an answer.

For example, users can ask:
* *"What were our top-selling products last month?"*
* *"How many orders were placed in Chennai this week?"*
* *"Show me customers who haven't purchased anything in the last 90 days."*

The goal is to make accessing and understanding business information simple, secure, and reliable — as easy as having a conversation.

---

## Key Capabilities

- 💬 **Natural Language Agent Interaction**  
  Interact with tailored domain-specific AI Agents (e.g., Sales, Finance, HR) that handle natural language query planning.
- 🏢 **Multi-Tenant Organization Management**  
  Complete organization isolation where every resource maps back to exactly one tenant.
- 🤖 **Agent-Centric Architecture**  
  Agents serve as the user-facing AI experience, connecting to external datasources via dedicated, least-privilege customer-side identities.
- 🔌 **Flexible Datasource Connectors**  
  Designed with a connector abstraction. The initial release supports **PostgreSQL, MySQL, and MongoDB**, with future extensibility for files, wikis, and document stores.
- 🛡️ **AI-as-an-Untrusted-Planner Principle**  
  LLMs are strictly treated as intent interpreters rather than security authorities. All generated queries undergo deterministic application-level policy validation.
- 🔒 **Read-Only Data Access & Defense-in-Depth**  
  External systems are queried strictly via read-only credentials with multi-layer authorization (Authentication → Org Membership → Agent Access Policy → Data Access Policy → Query Validation).
- 👀 **Observability & Evaluation**  
  First-class OpenTelemetry and Langfuse-ready instrumentation tracking execution traces, token usage, cost accounting, and security decisions.

---

## Core System Architecture & Flow Diagrams

### 1. High-Level End-to-End User Interaction Flow
When a user asks a question, the request flows through strict server-side authorization boundaries before interacting with the target datasource via an Agent.

```text
                     ┌──────────────────┐
                     │       User       │
                     └────────┬─────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │    Quest Engine Core    │
                │                         │
                │  1. Authenticate User   │
                │  2. Resolve Org & Roles │
                │  3. Check Agent Access  │
                │  4. AI Intent Planning  │
                │  5. Data Policy Check   │
                │  6. Validate SQL Query  │
                └─────────────┬───────────┘
                              │
                              │ Secure, Read-Only Query (Agent Credential)
                              ▼
                ┌─────────────────────────┐
                │   Customer Datasource   │
                │  (Postgres/MySQL/Mongo) │
                └─────────────┬───────────┘
                              │
                              │ Authorized Result
                              ▼
                ┌─────────────────────────┐
                │    Quest Engine Core    │
                │     → Final Answer      │
                └─────────────────────────┘
```

---

### 2. Datasource Onboarding Lifecycle
Datasource integration follows a rigorous multi-step lifecycle encompassing security approvals, connection checks, and metadata analysis before activation.

```text
  [ START ]
      │
      ▼
[ Select Agent(s) ] ──────────────► [ Select Category & Connector Type ]
                                            │
                                            ▼
                                [ Secure Connection Setup ]
                                            │
                                            ▼
                                [ SUPER_ADMIN Approval ]
                                            │
                                            ▼
                                  [ Test Connection ]
                                            │
                                            ▼
                               [ Metadata Extraction/Analysis ]
                                            │
                                            ▼
                               [ Admin Metadata Review ]
                                            │
                                            ▼
                               [ Define Data Access Policies ]
                                            │
                                            ▼
                                  [ ACTIVE DATASOURCE ]
```

---

### 3. Authorization & Agent-Level Security Model
Security decisions are split cleanly between user identity resolution, Agent access policies, and fine-grained data permissions.

```text
                ┌────────────────────────────────┐
                │   Authenticated User Context   │
                └───────────────┬────────────────┘
                                │
                                ▼
                ┌────────────────────────────────┐
                │      Organization & Roles      │
                └───────────────┬────────────────┘
                                │
                                ▼
                ┌────────────────────────────────┐
                │      Agent Access Policy       │
                │  (Can user talk to this agent?)│
                └───────────────┬────────────────┘
                                │ Allowed
                                ▼
                ┌────────────────────────────────┐
                │      Datasource & Metadata     │
                └───────────────┬────────────────┘
                                │
          ┌─────────────────────┴─────────────────────
          ▼                                           ▼
┌───────────────────┐                       ┌───────────────────┐
│ Agent-Specific DB │                       │ Data Access Policy│
│ Physical Identity │                       │ (Field/Table ACL) │
└─────────┬─────────┘                       └─────────┬─────────┘
          │                                           │
          └─────────────────────┬─────────────────────┘
                                │
                                ▼
                ┌────────────────────────────────┐
                │    Query Gateway Validation    │
                └───────────────┬────────────────┘
                                │
                                ▼
                ┌────────────────────────────────┐
                │   Customer External Database   │
                └────────────────────────────────┘
```

---

## Tech Stack & Architecture

- **Language & Runtime:** Python 3.11+, managed via `uv`
- **Framework:** FastAPI (Modular Monolith architecture)
- **Database & Migrations:** PostgreSQL, SQLAlchemy, Alembic (enforcing strict multi-tenant constraints)
- **Security & Config:** Pydantic-settings, secure secret management layers for external database credentials
- **Observability:** OpenTelemetry, Langfuse integration for distributed tracing and model accounting

---

## Getting Started

1. **Clone the repository and configure environment variables:**
   ```bash
   cp .env.example .env
   ```

2. **Synchronize dependencies using `uv`:**
   ```bash
   uv sync
   ```

3. **Run the development server:**
   ```bash
   uv run dev
   ```

---

## Project Engineering Goals

* **Non-Negotiable Tenant Isolation:** Absolute separation of organization resources.
* **AI-as-an-Untrusted-Planner:** Deterministic application-level validation for all AI outputs.
* **Defense-in-Depth:** Multiple structural layers from database permissions to application queries.
* **Observability by Design:** Built-in tracing, cost metrics, and evaluation strategies from day one.