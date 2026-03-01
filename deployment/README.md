# ECO Deployment

Deployment pipeline for the ECO embodied carbon prediction model. Version is **always set by `build.sh`** (never manually).

## Versioning

`vMAJOR.MINOR.PATCH` (e.g. `v1.0.0`, `v1.2.1`)

- **Major** (v1 → v2): New model — new data, new training pipeline, new `.pkl` files
- **Minor** (v1.0.0 → v1.1.0): Code/feature changes, same model
- **Patch** (v1.1.0 → v1.1.1): Bug fixes, same model

Versions sharing a major number share the same model artifacts (`deployment/dev/models/v<major>/`).

## Folder Structure

```
deployment/
├── README.md              # This file (overview + endpoints)
├── dev/
│   ├── models/
│   │   └── v1/            # Model artifacts for all v1.x.x
│   │       ├── manifest.json
│   │       └── *.pkl
│   └── working/           # Current code
│       ├── version.json   # Set by build.sh only
│       ├── requirements.txt
│       ├── README.md      # Version-specific API doc (detailed)
│       └── app/
└── prod/
    ├── Dockerfile
    ├── build.sh           # Sets version; never edit version.json by hand
    ├── .dockerignore
    └── releases/         # Frozen per-version snapshots
        └── v1.0.0/        # Each has its own README.md (that version’s API)
            ├── README.md
            ├── app/
            ├── model/
            ├── version.json
            └── ...
```

## Build (version is automatic)

From repo root:

```bash
# Test build — uses current version from version.json
./deployment/prod/build.sh test

# Release — bumps version and writes version.json (patch | minor | major)
./deployment/prod/build.sh release patch   # e.g. 1.0.0 → 1.0.1
./deployment/prod/build.sh release minor  # e.g. 1.0.0 → 1.1.0
./deployment/prod/build.sh release major  # e.g. 1.0.0 → 2.0.0
```

- **Version is never set manually.** If `version.json` is missing, `build.sh` bootstraps it (e.g. `1.0.0`); thereafter only `build.sh release <patch|minor|major>` changes it.
- **Before first build:** Put `.pkl` files in `deployment/dev/models/v1/` per `manifest.json` (or run the trainer: from repo root, `cd trainers/v1 && python model_train_validate.py`).
- **Major release:** Optionally zips `data/v<major>/` and attaches to GitHub Release (requires `gh` and `data/v<major>/`).

## API Endpoints

Base URL when running container: `http://localhost:8080` (or your deployment host). Port **8080**.

| Endpoint        | Method | Description |
|----------------|--------|-------------|
| `/`            | GET    | API name, version (from version.json), links to `/docs` and `/health` |
| `/health`      | GET    | 200 when model loaded, 503 otherwise |
| `/predict`     | POST   | Structured JSON (building parameters). Response: `{"prediction_kgCO2e_per_m2": <number>}` |
| `/predict/text`| POST   | JSON `{"text": "..."}` (natural language). Response: `{"prediction_kgCO2e_per_m2": <number>}` |
| `/docs`        | GET    | OpenAPI (Swagger) documentation |

**Version-specific details** (request bodies, all 33 keys, examples, PowerShell/curl): see **`deployment/dev/working/README.md`** for the current development version, or **`deployment/prod/releases/<tag>/README.md`** for a released version (e.g. `releases/v1.0.0/README.md`). When the container is running, **`GET /docs`** also shows exact request/response schemas and examples.

## Run container

```bash
docker run -p 8080:8080 eco-model:v1.0.0
```

Use the tag from your release (e.g. `eco-model:v1.0.1`). Health check: `GET /health` returns 200 only when the model is loaded.

## Data download by version

Training data is attached to GitHub Releases on major releases. From repo root:

```bash
./scripts/download_data.sh v1.0.0   # → data/v1/
./scripts/download_data.sh v2.0.0   # → data/v2/
```

Requires [GitHub CLI](https://cli.github.com/) (`gh`).
