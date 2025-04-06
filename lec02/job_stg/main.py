import os

from flask import Flask, request, jsonify
from flask import typing as flask_typing

from job_stg.bll.sales_avro import save_json_as_avro

app = Flask(__name__)


@app.route("/", methods=["POST"])
def main() -> flask_typing.ResponseReturnValue:
    """
    Controller that accepts command via HTTP and triggers business logic layer.

    Expected POST body (JSON):
    {
      "raw_dir": "C:/data/r_d-de-course/raw/sales/2022-08-09",
      "stg_dir": "C:/data/r_d-de-course/stg/sales/2022-08-09"
    }
    """
    input_data: dict = request.json

    raw_dir = input_data.get("raw_dir")
    stg_dir = input_data.get("stg_dir")

    if not raw_dir or not stg_dir:
        return jsonify({
            "message": "Missing 'raw_dir' or 'stg_dir' in request body"
        }), 400

    try:
        save_json_as_avro(raw_dir, stg_dir)
    except Exception as e:
        return jsonify({
            "message": f"Failed to process request: {str(e)}"
        }), 500

    return jsonify({
        "message": f"JSON files from {raw_dir} successfully converted to Avro and saved to {stg_dir}"
    }), 201


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8082)
