Build a production-ready **AI Control Center** for the existing `VMS_Help_Menu` application. The purpose of this project is to provide an internal administration UI for controlling the AI/RAG application's models, prompts, retrieval settings, performance settings, guardrails, and system health.

## 1. IMPORTANT — PRESERVE THE EXISTING ARCHITECTURE

The existing project is already implemented in Python/FastAPI and has the following structure:

```text
VMS_Help_Menu/
├── src/
│   ├── config.py
│   ├── core/
│   │   ├── rag.py
│   │   ├── retrievers.py
│   │   └── prompts.py
│   ├── api/
│   │   ├── app.py
│   │   └── schemas.py
│   ├── storage/
│   │   ├── cache.py
│   │   ├── vector_db.py
│   │   └── datastore.py
│   └── utils/
│       └── logging.py
├── scripts/
├── data/
├── app.py
├── main.py
├── .env
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── KB_PDF/
└── DOCKER.md
```

Do NOT replace or rewrite the existing architecture. Do NOT migrate the project to React, Angular, Vue, Node.js, TypeScript, or another frontend framework.

The frontend must use only:

- HTML5
- Bootstrap 5
- Bootstrap Icons
- CSS
- Vanilla JavaScript
- Browser `fetch()` API

Keep the existing Python/FastAPI backend.

Do not introduce a frontend build system unless it is absolutely required. The Control Center should be deployable with the existing FastAPI/Docker setup.

The existing RAG behavior must remain backward compatible. Do not modify the core RAG pipeline unnecessarily.

The existing project is a pure RAG chatbot. Preserve that behavior. Do not introduce lead generation, sales flows, marketing functionality, or unrelated chatbot functionality.

---

## 2. OBJECTIVE

Create an internal **AI Control Center** that allows an administrator to manage the AI application's runtime configuration without directly editing Python source code.

The Control Center should manage:

1. Model Configuration
2. Prompt Configuration
3. RAG Configuration
4. Performance Configuration
5. Guardrails
6. System Health
7. Configuration validation
8. Configuration testing

This is a configuration/control application, not an analytics dashboard.

Do NOT create conversation analytics, user analytics, sales analytics, or business reporting unless specifically required later.

---

## 3. FRONTEND STRUCTURE

Add a lightweight frontend such as:

```text
VMS_Help_Menu/
├── static/
│   ├── index.html
│   ├── css/
│   │   └── admin.css
│   └── js/
│       ├── app.js
│       ├── api.js
│       ├── models.js
│       ├── prompts.js
│       ├── rag.js
│       ├── performance.js
│       ├── guardrails.js
│       └── health.js
```

Use Bootstrap components wherever practical.

Do not create unnecessarily complicated frontend abstractions.

Use reusable JavaScript functions for:

- API requests
- loading states
- error handling
- success messages
- form population
- form serialization
- validation
- status indicators

Avoid duplicating the same JavaScript logic across pages.

Prefer a single-page admin interface with sidebar navigation rather than creating many independent HTML pages.

---

## 4. UI DESIGN

Create a clean internal administration interface:

```text
┌──────────────────────────────────────────────────────────────┐
│ AI CONTROL CENTER                              ● System OK   │
├────────────────┬─────────────────────────────────────────────┤
│ Dashboard      │                                             │
│ Models         │ Main Configuration Area                     │
│ Prompts        │                                             │
│ RAG            │                                             │
│ Performance    │                                             │
│ Guardrails     │                                             │
│ System         │                                             │
│                │                                             │
│                │                                             │
└────────────────┴─────────────────────────────────────────────┘
```

Use Bootstrap cards, forms, tabs, alerts, badges, tables, modals, and buttons.

The UI should be:

- clean
- professional
- responsive
- lightweight
- easy to understand
- suitable for an internal engineering/admin tool

Do not make it look like a marketing website.

---

# 5. DASHBOARD

Create a basic overview dashboard containing:

### System Status

Display:

- API
- Primary LLM
- Fallback LLM
- Vector DB
- Embedding service
- Cache

Each should have a status:

- Healthy
- Degraded
- Unavailable
- Disabled
- Unknown

Do not hardcode these statuses.

Retrieve them from actual backend health checks.

### Active Configuration

Display:

- Primary provider
- Primary model
- Fallback provider
- Fallback model
- RAG strategy
- Vector Top-K
- BM25 Top-K
- Final Top-K
- Active prompt version

### Configuration Status

Display:

- Current configuration version
- Last updated timestamp
- Configuration validity
- Unsaved changes state

---

# 6. MODEL CONFIGURATION

Create a Model Configuration section.

Support:

```text
Primary Provider
Primary Model

Fallback Provider
Fallback Model

Temperature
Max Tokens
Request Timeout

Primary Model Enabled
Fallback Enabled
```

The frontend must not hardcode all available models.

Create a backend endpoint that returns supported providers/models.

Example:

```http
GET /admin/providers
```

Example response:

```json
{
  "providers": [
    {
      "id": "groq",
      "name": "Groq",
      "models": [
        "llama-3.1-8b-instant"
      ]
    },
    {
      "id": "nvidia",
      "name": "NVIDIA",
      "models": [
        "..."
      ]
    }
  ]
}
```

The UI should dynamically populate provider/model dropdowns.

Provider-specific implementation must remain in backend provider/service modules.

Do not spread provider-specific logic throughout the RAG pipeline.

---

# 7. PROMPT CONFIGURATION

Create a Prompt Configuration section.

Support:

```text
System Prompt
RAG Prompt
No-Answer Prompt
Greeting Prompt
Context Instructions
```

Each prompt should have:

- editable textarea
- character/token indication where practical
- validation
- version
- last updated information

Example:

```text
System Prompt
┌────────────────────────────────────────────────────┐
│ You are a strict knowledge-base assistant...       │
│                                                    │
│                                                    │
└────────────────────────────────────────────────────┘

Characters: 1,284

[Validate Prompt] [Test Prompt] [Save]
```

Do not allow arbitrary code execution through prompts.

Prompt changes must affect the existing prompt construction system through a clean configuration/service layer.

Do not duplicate prompt construction logic in the frontend.

---

# 8. RAG CONFIGURATION

Create a RAG Configuration section.

Support:

```text
Vector Top-K
BM25 Top-K
Final Top-K

Similarity Threshold

Chunk Size
Chunk Overlap

Retrieval Strategy
```

Retrieval strategy can initially support the strategies already available in the existing application.

Do not invent unsupported retrieval strategies merely for UI purposes.

The current RAG architecture already uses vector retrieval and BM25 retrieval. Preserve that implementation.

Configuration changes should flow into the existing retriever/RAG configuration through the backend configuration layer.

---

# 9. PERFORMANCE CONFIGURATION

Support:

```text
Cache Enabled

Semantic Cache Threshold

Maximum History Messages

Maximum History Characters

Request Timeout
```

Validate all values before saving.

Example:

```text
Vector Top-K
[ 5 ]

Semantic Threshold
[ 0.92 ]

Max History Messages
[ 10 ]
```

Do not permit unreasonable values that could cause memory, latency, or token problems.

---

# 10. GUARDRAILS

Create a Guardrails section.

Support:

```text
Strict RAG Mode
Allow General Questions
Hallucination Protection
Minimum Retrieval Score
Out-of-Scope Response
```

For boolean values use Bootstrap switches.

For text responses use textareas.

The existing pure-RAG behavior must remain the default.

If strict RAG mode is enabled, the AI must not answer unsupported questions using unrelated model knowledge.

---

# 11. SYSTEM HEALTH

Create actual backend health endpoints.

Example:

```http
GET /admin/health
GET /admin/health/llm
GET /admin/health/vector-db
GET /admin/health/embedding
GET /admin/health/cache
```

Or use a single aggregated endpoint:

```http
GET /admin/health
```

Response:

```json
{
  "api": {
    "status": "healthy"
  },
  "primary_llm": {
    "status": "healthy",
    "provider": "groq",
    "model": "llama-3.1-8b-instant"
  },
  "fallback_llm": {
    "status": "healthy"
  },
  "vector_db": {
    "status": "healthy"
  },
  "embedding": {
    "status": "healthy"
  },
  "cache": {
    "status": "healthy"
  }
}
```

Do not fake health information.

Health-check failures should be handled gracefully and should never crash the dashboard.

---

# 12. CONFIGURATION STORAGE

Do NOT create a database for configuration.

Use configuration files.

Recommended:

```text
VMS_Help_Menu/
├── config/
│   ├── models.yaml
│   ├── prompts.yaml
│   ├── rag.yaml
│   ├── performance.yaml
│   └── guardrails.yaml
```

However, inspect the existing `src/config.py` first.

Do not blindly duplicate configuration.

Create a configuration-management layer that can:

```text
load configuration
        ↓
validate configuration
        ↓
return typed configuration
        ↓
update selected values
        ↓
validate complete configuration
        ↓
atomically persist configuration
        ↓
reload/apply configuration
```

The frontend must never directly access YAML/JSON files.

Use:

```text
HTML / JavaScript
        ↓
FastAPI
        ↓
Configuration Service
        ↓
Configuration Files
```

---

# 13. IMPORTANT — DO NOT STORE SECRETS

Never store:

- GROQ API keys
- NVIDIA API keys
- passwords
- access tokens
- authorization headers
- credentials

inside the dashboard configuration files.

Secrets must remain in `.env` or the existing secret-management mechanism.

The dashboard must never return secrets to the browser.

---

# 14. CONFIGURATION API

Create clean REST APIs.

Recommended:

```http
GET  /admin/config
PUT  /admin/config

POST /admin/config/validate
POST /admin/config/test

GET  /admin/providers
GET  /admin/health
```

If a better route structure already exists, reuse it.

Use Pydantic schemas for all request/response models.

Example:

```python
class AdminConfigUpdate(BaseModel):
    models: ModelConfig | None = None
    prompts: PromptConfig | None = None
    rag: RAGConfig | None = None
    performance: PerformanceConfig | None = None
    guardrails: GuardrailConfig | None = None
```

Do not allow arbitrary unvalidated dictionaries to modify runtime configuration.

---

# 15. SAVE / VALIDATE / APPLY FLOW

Do not make the Save button blindly write configuration.

Use:

```text
Edit
 ↓
Validate
 ↓
If invalid → show errors
 ↓
If valid
 ↓
Save
 ↓
Apply / Reload
 ↓
Show success
```

The existing configuration must remain untouched if validation fails.

Configuration writes should be atomic.

Avoid partially written configuration files.

Where practical, maintain the previous valid configuration so rollback is possible.

---

# 16. TEST CONFIGURATION

Add a configuration test capability.

The administrator should be able to modify settings temporarily and click:

```text
Test Configuration
```

The backend should run a real test without permanently changing production configuration.

Display:

```text
Provider
Model
Retrieved Chunks
Retrieval Scores
Prompt
Response
Latency
Token information if available
Errors
```

Clearly indicate:

```text
TEST CONFIGURATION
```

and:

```text
NOT APPLIED TO PRODUCTION
```

This feature should reuse the existing RAG pipeline rather than creating a second RAG implementation.

---

# 17. BACKWARD COMPATIBILITY

This is critical.

Do not break:

```text
python app.py
python main.py
```

Do not remove existing API endpoints.

Do not change existing chatbot request/response contracts unless absolutely necessary.

Do not break Docker deployment.

Do not change the vector database format.

Do not rebuild the knowledge base unnecessarily.

Do not modify the existing RAG algorithm unless required to connect configuration dynamically.

The Control Center must be an addition to the existing system.

---

# 18. CODE QUALITY / PP6 PRINCIPLES

Follow strong production coding principles:

### Single Responsibility

Each module should have one clear responsibility.

Do not create a huge `admin.py` containing configuration, health checks, provider management, and business logic.

Prefer:

```text
admin/
├── config_service.py
├── health_service.py
├── provider_service.py
└── schemas.py
```

if this fits the existing architecture.

### DRY

Do not duplicate:

- API request code
- validation logic
- configuration loading
- status rendering
- error handling
- Bootstrap components

### KISS

Do not introduce unnecessary frameworks or infrastructure.

The application only needs:

```text
FastAPI
HTML
Bootstrap
JavaScript
YAML/JSON configuration
```

where practical.

### Explicit Contracts

Use Pydantic models for backend API contracts.

Use clear JSON structures between frontend and backend.

### Separation of Concerns

Frontend:

```text
presentation
interaction
API calls
```

Backend:

```text
validation
configuration
RAG integration
health checks
provider integration
```

Configuration layer:

```text
load
validate
save
reload
version
```

---

# 19. SECURITY

The Control Center is an administrative interface.

Do not expose it as an unrestricted public endpoint.

Integrate with the application's existing authentication mechanism if available.

If authentication is not currently available, create a clean authentication integration point rather than embedding hardcoded credentials.

Never hardcode admin passwords.

Never expose secrets.

Validate all administrator input.

Prevent filesystem traversal.

Prevent arbitrary file writes.

Prevent arbitrary code execution.

---

# 20. ERROR HANDLING

The UI must gracefully handle:

- API unavailable
- invalid configuration
- invalid prompt
- provider unavailable
- model unavailable
- vector DB unavailable
- embedding service unavailable
- configuration file missing
- configuration file corrupted
- timeout
- permission errors

Use Bootstrap alerts/toasts for user feedback.

Example:

```text
✓ Configuration saved successfully.

✕ Configuration validation failed.

⚠ NVIDIA provider is currently unavailable.
```

Do not expose Python stack traces directly to administrators.

Log detailed technical errors on the backend.

---

# 21. LOGGING

Use the existing structured logging mechanism.

Do not use raw `print()` statements inside backend modules.

Do not log:

- API keys
- passwords
- authorization tokens
- secrets

Log useful operational information such as:

```text
configuration updated
configuration validation failed
provider health check failed
configuration reload failed
RAG test executed
```

---

# 22. TESTING

Add tests for:

### Configuration

- configuration loading
- default configuration
- valid configuration
- invalid configuration
- missing configuration
- corrupted configuration
- partial updates
- atomic writes

### API

- GET config
- PUT config
- validation endpoint
- provider endpoint
- health endpoint
- unauthorized access

### RAG Integration

- updated Top-K values
- updated prompts
- model selection
- fallback configuration

### Frontend

Test the most important user flows:

```text
Load configuration
Edit configuration
Validate
Save
Handle API error
Display health status
Test configuration
```

Do not aim for meaningless 100% coverage. Prioritize critical behavior.

---

# 23. IMPLEMENTATION PROCESS

Before writing code:

1. Inspect the existing repository.
2. Inspect `src/config.py`.
3. Inspect `src/core/rag.py`.
4. Inspect `src/core/prompts.py`.
5. Inspect `src/core/retrievers.py`.
6. Inspect `src/api/app.py`.
7. Inspect `src/api/schemas.py`.
8. Inspect existing Docker configuration.
9. Identify what configuration already exists.
10. Identify which settings can safely become runtime-configurable.

Then provide a concise implementation assessment.

After that:

1. Add the configuration-management layer.
2. Add Pydantic configuration schemas.
3. Add configuration API endpoints.
4. Add health/provider endpoints.
5. Add static Bootstrap UI.
6. Add JavaScript API integration.
7. Connect configuration to the existing RAG system.
8. Add validation.
9. Add test-configuration functionality.
10. Add automated tests.
11. Verify backward compatibility.
12. Update README/DOCKER documentation.

Do not perform a massive rewrite in one step.

---

# 24. FINAL ACCEPTANCE CRITERIA

The implementation is considered complete only when:

- The existing chatbot still works.
- `python app.py` still works.
- `python main.py` still works.
- Docker deployment still works.
- Existing RAG retrieval still works.
- Existing vector DB still works.
- HTML + Bootstrap + vanilla JS is used for the frontend.
- No React/Angular/Vue frontend is introduced.
- No unnecessary database is introduced.
- Configuration can be viewed through the dashboard.
- Configuration can be validated.
- Configuration can be updated safely.
- Prompts can be edited.
- Model configuration can be edited.
- RAG settings can be edited.
- Performance settings can be edited.
- Guardrails can be edited.
- System health is based on real backend checks.
- Secrets are never exposed.
- Invalid configuration cannot replace a valid configuration.
- Configuration changes are logged.
- The code is modular and maintainable.
- Critical functionality has automated tests.
- Documentation explains how to run and configure the Control Center.

Most importantly, **do not over-engineer this project**. The goal is a lightweight, reliable internal **AI Control Center** on top of the existing VMS RAG application, using the existing Python/FastAPI architecture and a simple HTML + Bootstrap + JavaScript frontend.