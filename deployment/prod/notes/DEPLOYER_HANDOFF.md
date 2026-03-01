# Email template: ECO API deployment handoff

**Subject:** ECO Embodied Carbon API — container and App Runner setup

---

**To:** [Deployer email]

**Hi [Deployer name],**

Please deploy the ECO Embodied Carbon API using the container below on **AWS App Runner**. Here’s what you need.

---

**Container image**

- **Registry:** Docker Hub  
- **Image:** `dfoshidero/eco-embodied-carbon-api`  
- **Tag:** [FILL: e.g. `latest` or `release-v1.0.1`]  
- **Full reference:** `dfoshidero/eco-embodied-carbon-api:[TAG]`

If the repo is private, use your Docker Hub credentials when configuring the source in App Runner.

---

**AWS App Runner configuration**

- **Platform:** Deploy this as an App Runner **container** service (source = Docker Hub / ECR as appropriate).
- **Port:** Set the container port to **8080** (the app listens on 8080 inside the container).
- **Scaling:**
  - **Min instances:** 1 or 2 (so at least 1–2 containers are always running).
  - **Max instances:** Set as needed for your expected load (e.g. 10 or higher); App Runner will scale between min and max.
- **Health check:** Use the default HTTP health check. Set the path to **`/health`**. The service may return 503 for up to **~90 seconds** after deploy while the model loads; after that, 200 means the service is ready.
- **Startup:** No environment variables are required; the app is self-contained.

---

**What the service does**

- Single HTTP API that predicts embodied carbon (kgCO2e/m²) for building designs.
- Each container runs **1** uvicorn worker by default. With min 1–2 instances and App Runner’s auto scaling, you get redundancy and capacity without changing the image.

---

**API endpoints (base URL = the App Runner URL you get)**

| Endpoint       | Method | Description |
|----------------|--------|-------------|
| `/`            | GET    | API info, version, links to `/docs` and `/health` |
| `/health`      | GET    | 200 when ready, 503 while model is loading |
| `/predict`     | POST   | JSON body with building parameters → `{"prediction_kgCO2e_per_m2": <number>}` |
| `/predict/text`| POST   | JSON `{"text": "..."}` (natural language) → `{"prediction_kgCO2e_per_m2": <number>}` |
| `/docs`        | GET    | Interactive API docs (Swagger) |

---

**What I need back from you**

1. The **base URL** for the API (the App Runner URL, or your custom domain if you attach one). I’ll use this in our app to call the API.  
2. Quick confirmation that the service is up and `GET /health` returns 200 after the first minute or two.

Thanks — let me know if anything is unclear or if you need a different tag/version.

**[Your name]**
