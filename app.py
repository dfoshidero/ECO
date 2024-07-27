import json
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from model_predictor import predictor
from feature_extractor import extract

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Core logic functions
def process_predict(data):
    prediction = predict(
        data.get("SECTOR"),
        data.get("SUBSECTOR"),
        data.get("GIA"),
        data.get("PERIMETER"),
        data.get("FOOTPRINT"),
        data.get("WIDTH"),
        data.get("HEIGHT"),
        data.get("ABOVE_GROUND"),
        data.get("BELOW_GROUND"),
        data.get("GLAZING_RATIO"),
        data.get("PILES"),
        data.get("PILE_CAPS"),
        data.get("CAPPING_BEAMS"),
        data.get("RAFT"),
        data.get("BASEMENT_WALLS"),
        data.get("LOWEST_FLOOR_SLAB"),
        data.get("GROUND_INSULATION"),
        data.get("CORE_STRUCTURE"),
        data.get("COLUMNS"),
        data.get("BEAMS"),
        data.get("SECONDARY_BEAMS"),
        data.get("FLOOR_SLAB"),
        data.get("JOISTED_FLOORS"),
        data.get("ROOF"),
        data.get("ROOF_INSULATION"),
        data.get("ROOF_FINISHES"),
        data.get("FACADE"),
        data.get("WALL_INSULATION"),
        data.get("GLAZING"),
        data.get("WINDOW_FRAMES"),
        data.get("PARTITIONS"),
        data.get("CEILINGS"),
        data.get("FLOORS"),
        data.get("SERVICES"),
    )
    return prediction.tolist() if isinstance(prediction, np.ndarray) else prediction


def process_extract(text):
    extracted_values = extract(text)
    for key, value in extracted_values.items():
        if isinstance(value, np.ndarray):
            extracted_values[key] = value.tolist()
    return extracted_values


def process_extract_predict(text):
    extracted_values = process_extract(text)

    # Map extracted values to the required parameters
    formatted_values = {
        "SECTOR": extracted_values.get("Sector"),
        "SUBSECTOR": extracted_values.get("Sub-Sector"),
        "GIA": extracted_values.get("Gross Internal Area (m2)"),
        "PERIMETER": extracted_values.get("Building Perimeter (m)"),
        "FOOTPRINT": extracted_values.get("Building Footprint (m2)"),
        "WIDTH": extracted_values.get("Building Width (m)"),
        "HEIGHT": extracted_values.get("Floor-to-Floor Height (m)"),
        "ABOVE_GROUND": extracted_values.get("Storeys Above Ground"),
        "BELOW_GROUND": extracted_values.get("Storeys Below Ground"),
        "GLAZING_RATIO": extracted_values.get("Glazing Ratio (%)"),
        "PILES": extracted_values.get("Piles Material"),
        "PILE_CAPS": extracted_values.get("Pile Caps Material"),
        "CAPPING_BEAMS": extracted_values.get("Capping Beams Material"),
        "RAFT": extracted_values.get("Raft Foundation Material"),
        "BASEMENT_WALLS": extracted_values.get("Basement Walls Material"),
        "LOWEST_FLOOR_SLAB": extracted_values.get("Lowest Floor Slab Material"),
        "GROUND_INSULATION": extracted_values.get("Ground Insulation Material"),
        "CORE_STRUCTURE": extracted_values.get("Core Structure Material"),
        "COLUMNS": extracted_values.get("Columns Material"),
        "BEAMS": extracted_values.get("Beams Material"),
        "SECONDARY_BEAMS": extracted_values.get("Secondary Beams Material"),
        "FLOOR_SLAB": extracted_values.get("Floor Slab Material"),
        "JOISTED_FLOORS": extracted_values.get("Joisted Floors Material"),
        "ROOF": extracted_values.get("Roof Material"),
        "ROOF_INSULATION": extracted_values.get("Roof Insulation Material"),
        "ROOF_FINISHES": extracted_values.get("Roof Finishes Material"),
        "FACADE": extracted_values.get("Facade Material"),
        "WALL_INSULATION": extracted_values.get("Wall Insulation Material"),
        "GLAZING": extracted_values.get("Glazing Material"),
        "WINDOW_FRAMES": extracted_values.get("Window Frames Material"),
        "PARTITIONS": extracted_values.get("Partitions Material"),
        "CEILINGS": extracted_values.get("Ceilings Material"),
        "FLOORS": extracted_values.get("Floors Material"),
        "SERVICES": extracted_values.get("Services"),
    }

    prediction = predict(**formatted_values)
    return prediction.tolist() if isinstance(prediction, np.ndarray) else prediction


# Flask routes
@app.route("/predict", methods=["POST"])
def predict_route():
    data = request.get_json()
    prediction = process_predict(data)
    return jsonify(prediction)


@app.route("/extract", methods=["POST"])
def extract_route():
    text = request.get_json().get("text")
    extracted_values = process_extract(text)
    return jsonify(extracted_values)


@app.route("/extract_predict", methods=["POST"])
def extract_predict_route():
    text = request.get_json().get("text")
    result = process_extract_predict(text)
    return jsonify(result)


def predict(
    SECTOR,
    SUBSECTOR,
    GIA,
    PERIMETER,
    FOOTPRINT,
    WIDTH,
    HEIGHT,
    ABOVE_GROUND,
    BELOW_GROUND,
    GLAZING_RATIO,
    PILES,
    PILE_CAPS,
    CAPPING_BEAMS,
    RAFT,
    BASEMENT_WALLS,
    LOWEST_FLOOR_SLAB,
    GROUND_INSULATION,
    CORE_STRUCTURE,
    COLUMNS,
    BEAMS,
    SECONDARY_BEAMS,
    FLOOR_SLAB,
    JOISTED_FLOORS,
    ROOF,
    ROOF_INSULATION,
    ROOF_FINISHES,
    FACADE,
    WALL_INSULATION,
    GLAZING,
    WINDOW_FRAMES,
    PARTITIONS,
    CEILINGS,
    FLOORS,
    SERVICES,
):
    user_input = {
        "Sector": [None if SECTOR == "None" else SECTOR],
        "Sub-Sector": [None if SUBSECTOR == "None" else SUBSECTOR],
        "Gross Internal Area (m2)": [None if GIA == "None" else GIA],
        "Building Perimeter (m)": [None if PERIMETER == "None" else PERIMETER],
        "Building Footprint (m2)": [None if FOOTPRINT == "None" else FOOTPRINT],
        "Building Width (m)": [None if WIDTH == "None" else WIDTH],
        "Floor-to-Floor Height (m)": [None if HEIGHT == "None" else HEIGHT],
        "Storeys Above Ground": [None if ABOVE_GROUND == "None" else ABOVE_GROUND],
        "Storeys Below Ground": [None if BELOW_GROUND == "None" else BELOW_GROUND],
        "Glazing Ratio (%)": [None if GLAZING_RATIO == "None" else GLAZING_RATIO],
        "Piles Material": [None if PILES == "None" else PILES],
        "Pile Caps Material": [None if PILE_CAPS == "None" else PILE_CAPS],
        "Capping Beams Material": [None if CAPPING_BEAMS == "None" else CAPPING_BEAMS],
        "Raft Foundation Material": [None if RAFT == "None" else RAFT],
        "Basement Walls Material": [
            None if BASEMENT_WALLS == "None" else BASEMENT_WALLS
        ],
        "Lowest Floor Slab Material": [
            None if LOWEST_FLOOR_SLAB == "None" else LOWEST_FLOOR_SLAB
        ],
        "Ground Insulation Material": [
            None if GROUND_INSULATION == "None" else GROUND_INSULATION
        ],
        "Core Structure Material": [
            None if CORE_STRUCTURE == "None" else CORE_STRUCTURE
        ],
        "Columns Material": [None if COLUMNS == "None" else COLUMNS],
        "Beams Material": [None if BEAMS == "None" else BEAMS],
        "Secondary Beams Material": [
            None if SECONDARY_BEAMS == "None" else SECONDARY_BEAMS
        ],
        "Floor Slab Material": [None if FLOOR_SLAB == "None" else FLOOR_SLAB],
        "Joisted Floors Material": [
            None if JOISTED_FLOORS == "None" else JOISTED_FLOORS
        ],
        "Roof Material": [None if ROOF == "None" else ROOF],
        "Roof Insulation Material": [
            None if ROOF_INSULATION == "None" else ROOF_INSULATION
        ],
        "Roof Finishes Material": [None if ROOF_FINISHES == "None" else ROOF_FINISHES],
        "Facade Material": [None if FACADE == "None" else FACADE],
        "Wall Insulation Material": [
            None if WALL_INSULATION == "None" else WALL_INSULATION
        ],
        "Glazing Material": [None if GLAZING == "None" else GLAZING],
        "Window Frames Material": [None if WINDOW_FRAMES == "None" else WINDOW_FRAMES],
        "Partitions Material": [None if PARTITIONS == "None" else PARTITIONS],
        "Ceilings Material": [None if CEILINGS == "None" else CEILINGS],
        "Floors Material": [None if FLOORS == "None" else FLOORS],
        "Services": [None if SERVICES == "None" else SERVICES],
    }

    prediction = predictor(user_input)

    return prediction


# Lambda handler
def lambda_handler(event, context):
    with app.app_context():
        with app.test_request_context(
            method="POST", data=json.dumps(event), content_type="application/json"
        ):
            if "function" in event:
                function_name = event["function"]
                if function_name == "predict_route":
                    response = predict_route()
                elif function_name == "extract_route":
                    response = extract_route()
                elif function_name == "extract_predict_route":
                    response = extract_predict_route()
                else:
                    response = jsonify({"error": "Unknown function name"})
                    response.status_code = 400

                return {
                    "statusCode": response.status_code,
                    "body": response.get_data(as_text=True),
                }
            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "No function name provided"}),
                }


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True, host="0.0.0.0", port=80)