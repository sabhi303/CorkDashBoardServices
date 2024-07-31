from flask import Blueprint, jsonify, request
import requests
import xmltodict
from datetime import datetime

noise_bp = Blueprint("noise", __name__)


# convert timestamp to unix timestamp
def to_unix_timestamp(timestamp_str, date_format="%Y-%m-%d %H:%M:%S"):
    # Parse the timestamp string into a datetime object
    dt = datetime.strptime(timestamp_str, date_format)

    # Convert the datetime object to a UNIX timestamp
    unix_timestamp = int(dt.timestamp())

    return unix_timestamp


# Common function to fetch and convert data
def fetch_and_convert(api_url, request_type="GET", data=None):
    try:
        if request_type == "GET":
            response = requests.get(api_url, timeout=10)
        else:
            response = requests.request(
                "POST",
                api_url,
                data=data,
                timeout=10,
            )

        response.raise_for_status()

        if "json" in response.headers.get("Content-Type"):
            return response.json()
        else:
            xml_data = response.content
            json_data = xmltodict.parse(xml_data)
            return json_data

    except requests.exceptions.HTTPError as http_err:
        return {
            "error": "HTTP error occurred",
            "details": str(http_err),
        }, response.status_code
    except requests.exceptions.ConnectionError as conn_err:
        return {"error": "Connection error occurred", "details": str(conn_err)}, 503
    except requests.exceptions.Timeout as timeout_err:
        return {"error": "Timeout error occurred", "details": str(timeout_err)}, 504
    except requests.exceptions.RequestException as req_err:
        return {"error": "Request exception occurred", "details": str(req_err)}, 500
    except xmltodict.expat.ExpatError as xml_err:
        return {"error": "XML parsing error occurred", "details": str(xml_err)}, 400
    except Exception as err:
        return {"error": "An unexpected error occurred", "details": str(err)}, 500


@noise_bp.route("/levels", methods=["GET"])
def levels():
    return jsonify({"message": "Noise levels route"})


@noise_bp.route("/monitors", methods=["GET"])
def monitors():
    api_url = request.args.get(
        "api_url", "https://data.smartdublin.ie/sonitus-api/api/monitors"
    )
    data = {"username": "dublincityapi", "password": "Xpa5vAQ9ki"}
    result = fetch_and_convert(api_url, request_type="POST", data=data)

    # now filter the mponitors are fetch the noise quality only
    result = [record for record in result if "Noise" in record.get("label", "")]
    # print(result)
    return jsonify(result)


@noise_bp.route("/data", methods=["GET"])
def data():
    """
    1. Monitor label or serial number
    2. Start time in unix style
    3. End time im unix style
    Note: Both of the above are timestamps
    """
    start_time = request.args.get("start_time", "ithe system cha default ghya")
    end_time = request.args.get("end_time", "ithe system cha default ghya")
    monitor = request.args.get("monitor", "ithe konta tri ek monitor ghya")
    api_url = request.args.get(
        "api_url", "https://data.smartdublin.ie/sonitus-api/api/data"
    )
    data = {
        "username": "dublincityapi",
        "password": "Xpa5vAQ9ki",
        "start": to_unix_timestamp(start_time),
        "end": to_unix_timestamp(end_time),
        "monitor": monitor,
    }
    print(data)
    result = fetch_and_convert(api_url, request_type="POST", data=data)
    return jsonify(result)
