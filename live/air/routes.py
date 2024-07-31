from flask import Blueprint, jsonify, request
import requests
import xmltodict

air_bp = Blueprint("air", __name__)


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


@air_bp.route("/quality", methods=["GET"])
def quality():
    return jsonify({"message": "Air quality route"})


@air_bp.route("/monitors", methods=["GET"])
def monitors():
    api_url = request.args.get(
        "api_url", "https://data.smartdublin.ie/sonitus-api/api/monitors"
    )
    data = {"username": "dublincityapi", "password": "Xpa5vAQ9ki"}
    result = fetch_and_convert(api_url, request_type="POST", data=data)

    print(type(result))
    print(result[0].get("label", ""))
    # now filter the mponitors are fetch the air quality only
    result = [record for record in result if not "Noise" in record.get("label", "")]
    # print(result)
    return jsonify(result)
