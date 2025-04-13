import os

from flask import Flask, request, jsonify
from flask import typing as flask_typing

from job_raw.bll.sales_api import save_sales_to_local_disk
from job_raw.bll.exceptions import DataLoadError, SaveToDiskError, NoSalesDataFound


app = Flask(__name__)


@app.route("/", methods=["POST"])
def main() -> flask_typing.ResponseReturnValue:
    """
    Controller that accepts command via HTTP and triggers business logic layer.

    Expected POST body (JSON):
    {
      "date": "2022-08-09",
      "raw_dir": "C:/data/raw/sales/2022-08-09"
    }
    """
    input_data: dict = request.json

    date = input_data.get("date")
    raw_dir = input_data.get("raw_dir")

    if not date or not raw_dir:
        return jsonify({
            "message": "Missing 'date' or 'raw_dir' in request body"
        }), 400


    try:
        save_sales_to_local_disk(date, raw_dir)
    except DataLoadError as e:
        return jsonify({"message": f"Failed to load data: {str(e)}"}), 502
    except SaveToDiskError as e:
        return jsonify({"message": f"Failed to save data: {str(e)}"}), 500
    except NoSalesDataFound as e:
        return jsonify({"message": str(e)}), 204
    except Exception as e:
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500

    return jsonify({
        "message": f"Sales data for {date} saved successfully"
    }), 201


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8081)
