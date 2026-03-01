"""
FastAPI application exposing the ECO embodied carbon prediction model.
"""
import json
import os
from contextlib import asynccontextmanager
from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel, Field

# Version is read from version.json (set by build.sh); no version hardcoded in app code.
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_VERSION_PATH = os.path.join(_APP_DIR, "..", "version.json")

model_ready = False
_model = None
_features = None
_label_encoders = None
_unique_values = None


def _load_version():
    """Read version.json; contents are set by deployment/prod/build.sh."""
    with open(_VERSION_PATH, encoding="utf-8") as f:
        return json.load(f)


def _version_str():
    """Version string for this build (from version.json only)."""
    return _load_version().get("version", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_ready, _model, _features, _label_encoders, _unique_values
    try:
        from .model_predictor import load_resources
        from .feature_extractor import initialize_resources

        _model, _features, _label_encoders, _unique_values = load_resources()
        initialize_resources()
        model_ready = True
    except Exception as e:
        model_ready = False
        raise e
    yield
    # Shutdown: clear references
    _model = _features = _label_encoders = _unique_values = None
    model_ready = False


app = FastAPI(
    title="ECO Embodied Carbon API",
    description="Predict embodied carbon (kgCO2e/m²) for building designs",
    version=_version_str(),
    lifespan=lifespan,
)


def _root_response_example():
    """Example for OpenAPI docs: version comes from version.json."""
    v = _load_version()
    return {
        "name": "ECO Embodied Carbon API",
        "version": v.get("version", ""),
        "docs": "/docs",
        "health": "/health",
    }


@app.get(
    "/",
    responses={
        200: {
            "description": "API info",
            "content": {
                "application/json": {
                    "example": _root_response_example(),
                }
            },
        },
    },
)
async def root():
    """**Output:** API name, version (from version.json), and links to `/docs` and `/health`."""
    return _root_response_example()


@app.get(
    "/health",
    responses={
        200: {
            "description": "Model loaded and ready",
            "content": {
                "application/json": {
                    "example": {"status": "ok"},
                }
            },
        },
        503: {
            "description": "Model not yet loaded",
            "content": {
                "application/json": {
                    "example": {"detail": "Model not yet loaded"},
                }
            },
        },
    },
)
async def health():
    """**Output:** `{"status": "ok"}` when model is loaded; 503 with `{"detail": "Model not yet loaded"}` otherwise."""
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model not yet loaded")
    return {"status": "ok"}


def _dict_to_user_input(data: dict) -> dict:
    """Convert API input dict to format expected by model (values as single-element lists)."""
    user_input = {}
    for k, v in data.items():
        if v is None or v == "None":
            user_input[k] = [None]
        else:
            user_input[k] = [v]
    return user_input


# Feature keys expected for structured predict (in order)
PREDICT_KEYS = [
    "Sector",
    "Sub-Sector",
    "Gross Internal Area (m2)",
    "Building Perimeter (m)",
    "Building Footprint (m2)",
    "Building Width (m)",
    "Floor-to-Floor Height (m)",
    "Storeys Above Ground",
    "Storeys Below Ground",
    "Glazing Ratio (%)",
    "Piles Material",
    "Pile Caps Material",
    "Capping Beams Material",
    "Raft Foundation Material",
    "Basement Walls Material",
    "Lowest Floor Slab Material",
    "Ground Insulation Material",
    "Core Structure Material",
    "Columns Material",
    "Beams Material",
    "Secondary Beams Material",
    "Floor Slab Material",
    "Joisted Floors Material",
    "Roof Material",
    "Roof Insulation Material",
    "Roof Finishes Material",
    "Facade Material",
    "Wall Insulation Material",
    "Glazing Material",
    "Window Frames Material",
    "Partitions Material",
    "Ceilings Material",
    "Floors Material",
    "Services",
]

# --- OpenAPI request/response models and examples ---


class PredictionResponse(BaseModel):
    """Prediction result: embodied carbon in kgCO2e per m²."""

    prediction_kgCO2e_per_m2: float = Field(
        ...,
        description="Predicted embodied carbon (kgCO2e/m²)",
        examples=[387.42],
    )


class PredictTextRequest(BaseModel):
    """Natural language building description."""

    text: str = Field(
        ...,
        description="Free-text description of the building (e.g. materials, size, use)",
        examples=["5 storey office building, 5000 m2 gross internal area, concrete frame, steel columns and beams, curtain wall facade"],
    )


# Example request body for POST /predict (all 33 keys)
PREDICT_REQUEST_EXAMPLE = {
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
    "Piles Material": None,
    "Pile Caps Material": None,
    "Capping Beams Material": None,
    "Raft Foundation Material": "Concrete",
    "Basement Walls Material": "Concrete",
    "Lowest Floor Slab Material": "Concrete",
    "Ground Insulation Material": None,
    "Core Structure Material": "Concrete",
    "Columns Material": "Steel",
    "Beams Material": "Steel",
    "Secondary Beams Material": None,
    "Floor Slab Material": "Concrete",
    "Joisted Floors Material": None,
    "Roof Material": "Concrete",
    "Roof Insulation Material": None,
    "Roof Finishes Material": None,
    "Facade Material": "Curtain Wall",
    "Wall Insulation Material": None,
    "Glazing Material": None,
    "Window Frames Material": None,
    "Partitions Material": None,
    "Ceilings Material": None,
    "Floors Material": None,
    "Services": None,
}


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        200: {
            "description": "Prediction (kgCO2e/m²)",
            "content": {
                "application/json": {
                    "example": {"prediction_kgCO2e_per_m2": 387.42},
                }
            },
        },
        503: {
            "description": "Model not yet loaded",
            "content": {
                "application/json": {
                    "example": {"detail": "Model not yet loaded"},
                }
            },
        },
    },
)
async def predict(
    data: dict = Body(
        ...,
        examples=[PREDICT_REQUEST_EXAMPLE],
        description="JSON with keys matching the 33 feature names. Use null for missing values.",
    ),
):
    """
    **Input:** JSON object with exactly these keys (values can be numbers, strings, or null):

    Sector, Sub-Sector, Gross Internal Area (m2), Building Perimeter (m), Building Footprint (m2), Building Width (m), Floor-to-Floor Height (m), Storeys Above Ground, Storeys Below Ground, Glazing Ratio (%), Piles Material, Pile Caps Material, Capping Beams Material, Raft Foundation Material, Basement Walls Material, Lowest Floor Slab Material, Ground Insulation Material, Core Structure Material, Columns Material, Beams Material, Secondary Beams Material, Floor Slab Material, Joisted Floors Material, Roof Material, Roof Insulation Material, Roof Finishes Material, Facade Material, Wall Insulation Material, Glazing Material, Window Frames Material, Partitions Material, Ceilings Material, Floors Material, Services.

    **Output:** `{"prediction_kgCO2e_per_m2": <number>}` — predicted embodied carbon in kgCO2e per m².
    """
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model not yet loaded")

    # Build user_input with all keys, defaulting to None for missing
    def _is_missing(v):
        if v is None:
            return True
        if isinstance(v, str) and v.strip() in ("", "None", "null"):
            return True
        return False

    user_input = {}
    for k in PREDICT_KEYS:
        v = data.get(k)
        user_input[k] = [None] if _is_missing(v) else [v]

    from .model_predictor import predict as model_predict

    pred = model_predict(user_input, _model, _features, _label_encoders)
    val = float(pred[0]) if hasattr(pred, "__getitem__") else float(pred)
    return {"prediction_kgCO2e_per_m2": val}


@app.post(
    "/predict/text",
    response_model=PredictionResponse,
    responses={
        200: {
            "description": "Prediction (kgCO2e/m²)",
            "content": {
                "application/json": {
                    "example": {"prediction_kgCO2e_per_m2": 412.18},
                }
            },
        },
        422: {
            "description": "Validation error (e.g. missing 'text' field)",
            "content": {
                "application/json": {
                    "example": {"detail": [{"loc": ["body", "text"], "msg": "field required", "type": "value_error.missing"}]},
                }
            },
        },
        503: {
            "description": "Model not yet loaded",
            "content": {
                "application/json": {
                    "example": {"detail": "Model not yet loaded"},
                }
            },
        },
    },
)
async def predict_text(data: PredictTextRequest):
    """
    **Input:** JSON object with one field: `"text": "<natural language description>"`.

    **Output:** `{"prediction_kgCO2e_per_m2": <number>}` — predicted embodied carbon in kgCO2e per m².
    """
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model not yet loaded")

    text = data.text

    from .feature_extractor import extract
    from .model_predictor import predict as model_predict

    try:
        value_list = extract(text)
    except RuntimeError as e:
        if "embedding model" in str(e).lower() or "sentence_transformer" in str(e).lower():
            raise HTTPException(status_code=503, detail=str(e)) from e
        raise
    user_input = {}
    for k in PREDICT_KEYS:
        v = value_list.get(k)
        missing = v is None or (
            isinstance(v, str) and v.strip() in ("", "None", "null")
        )
        user_input[k] = [None] if missing else [v]
    pred = model_predict(user_input, _model, _features, _label_encoders)
    val = float(pred[0]) if hasattr(pred, "__getitem__") else float(pred)
    return {"prediction_kgCO2e_per_m2": val}
