## Docker deployment

Build and start the application with:

```powershell
docker compose up -d --build
```

The API is available at `http://localhost:5008`. The internal AI Control Center is at
`http://localhost:5008/admin`.

Set these values in `.env`; Compose passes them to the API but `.dockerignore` prevents
`.env` from being copied into the image:

```dotenv
GROQ_API_KEY=your-secret-key
ADMIN_USERNAME=vmschat
ADMIN_PASSWORD=change-this-before-production
ADMIN_COOKIE_SECURE=false
```

Use `ADMIN_COOKIE_SECURE=true` when the application is served behind HTTPS. Admin login
sessions expire five minutes after login. The `data/` bind mount persists the vector store,
cache, logs, and `admin_config.json` across container recreation.

The API container intentionally runs one Uvicorn worker so runtime Control Center changes
and in-memory chat sessions are consistent. Scale behind a shared session/configuration
service only after adding those shared-state guarantees.
