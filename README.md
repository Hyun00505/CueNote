# CueNote Monorepo

Local-first desktop app with an Electron + Vue renderer and a FastAPI core service.

## Structure
- `apps/desktop`: Electron main process with Vue 3 + Vite renderer.
- `apps/core`: FastAPI service using SQLite at `apps/core/data/cuenote.db`.
- `packages/contracts`: Shared JSON schemas and TypeScript types.
- `packages/shared`: Shared utilities (stub for future common helpers).

## Getting Started

### Prerequisites
- [pnpm](https://pnpm.io/) installed for JavaScript dependencies.
- Python 3.11+ with `uvicorn` and `fastapi` available (install via `pip install -r apps/core/requirements.txt`).

### Install JS dependencies
```bash
pnpm install
```

### Run the core API (FastAPI)
```bash
pnpm dev:core
```
This runs `uvicorn app.main:app --reload --host 127.0.0.1 --port 8787` from `apps/core`. The `/health` endpoint returns `{ "status": "ok" }` and `/events` streams basic SSE updates.

### Run the desktop app
```bash
pnpm dev:desktop
```
Electron launches and boots a Vite dev server for the renderer automatically, pointing to `http://localhost:5173`.

### Run everything together
```bash
pnpm dev:all
```
This starts both the FastAPI core and the Electron renderer concurrently.

## Notes
- Core API is reachable at `http://127.0.0.1:8787`.
- The renderer is served by Vite in dev mode and communicates with the core API over HTTP and SSE.
- Database lives at `apps/core/data/cuenote.db`; it's created automatically on startup.
