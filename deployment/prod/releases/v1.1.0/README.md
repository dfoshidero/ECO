# ECO API — version-specific documentation

This README describes the API for the **current** version in `dev/working/`. It is copied into each release as `releases/<tag>/README.md`, so endpoints and request/response shapes are documented per version. If you are using a released image, see `deployment/prod/releases/<tag>/README.md` for that version’s doc.

---

## Endpoints (this version)

| Endpoint         | Method | Description |
|------------------|--------|-------------|
| `/`              | GET    | API info and version |
| `/health`        | GET    | 200 when model loaded, 503 otherwise |
| `/predict`       | POST   | Structured JSON (33 building parameters) |
| `/predict/text`  | POST   | Natural language: `{"text": "..."}` |
| `/docs`          | GET    | OpenAPI documentation |

---

## GET `/`

**Request:** No body.

**Response (200):**
```json
{
  "name": "ECO Embodied Carbon API",
  "version": "<from version.json>",
  "docs": "/docs",
  "health": "/health"
}
```

---

## GET `/health`

**Request:** No body.

**Response (200 when model loaded):**
```json
{"status": "ok"}
```

**Response (503 when model not loaded):**
```json
{"detail": "Model not yet loaded"}
```

---

## POST `/predict`

**Request:** JSON with keys matching the 33 feature names. Use `null` for missing values.

**Request body (all 33 keys):**
```json
{
  "Sector": "Commercial",
  "Sub-Sector": "Office",
  "Gross Internal Area (m2)": 5000,
  "Building Perimeter (m)": 200,
  "Building Footprint (m2)": 1250,
  "Building Width (m)": 50,
  "Floor-to-Floor Height (m)": 3.5,
  "Storeys Above Ground": 4,
  "Storeys Below Ground": 1,
  "Glazing Ratio (%)": 40,
  "Piles Material": null,
  "Pile Caps Material": null,
  "Capping Beams Material": null,
  "Raft Foundation Material": "Concrete",
  "Basement Walls Material": "Concrete",
  "Lowest Floor Slab Material": "Concrete",
  "Ground Insulation Material": null,
  "Core Structure Material": "Concrete",
  "Columns Material": "Steel",
  "Beams Material": "Steel",
  "Secondary Beams Material": null,
  "Floor Slab Material": "Concrete",
  "Joisted Floors Material": null,
  "Roof Material": "Concrete",
  "Roof Insulation Material": null,
  "Roof Finishes Material": null,
  "Facade Material": "Curtain Wall",
  "Wall Insulation Material": null,
  "Glazing Material": null,
  "Window Frames Material": null,
  "Partitions Material": null,
  "Ceilings Material": null,
  "Floors Material": null,
  "Services": null
}
```

**Response (200):**
```json
{"prediction_kgCO2e_per_m2": 387.42}
```

---

## POST `/predict/text`

**Request:** JSON with a single `text` field.

**Request body:**
```json
{
  "text": "5 storey office building, 5000 m2 gross internal area, concrete frame, steel columns and beams, curtain wall facade"
}
```

**Response (200):**
```json
{"prediction_kgCO2e_per_m2": 412.18}
```

**Response (422 if `text` missing):**
```json
{"detail": [{"loc": ["body", "text"], "msg": "field required", "type": "value_error.missing"}]}
```

---

## Examples

### PowerShell

```powershell
# /predict/text
$body = @{ text = "5 storey office, 5000 m2, concrete frame, steel columns" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/predict/text" -Method Post -Body $body -ContentType "application/json"

# /predict (missing keys default to null)
$body = @{
  "Sector" = "Commercial"
  "Sub-Sector" = "Office"
  "Gross Internal Area (m2)" = 5000
  "Building Perimeter (m)" = 200
  "Building Footprint (m2)" = 1250
  "Building Width (m)" = 50
  "Floor-to-Floor Height (m)" = 3.5
  "Storeys Above Ground" = 4
  "Storeys Below Ground" = 1
  "Glazing Ratio (%)" = 40
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/predict" -Method Post -Body $body -ContentType "application/json"
```

### curl (with JSON file)

Save request body to `body.json`, then:

```bash
curl -X POST http://localhost:8080/predict/text -H "Content-Type: application/json" -d @body.json
```

---

## Container

```bash
docker run -p 8080:8080 eco-model:<tag>
```

Health check: `GET /health` (200 only when model is loaded).
