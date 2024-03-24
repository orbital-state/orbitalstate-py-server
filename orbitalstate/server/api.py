"""
Flask app implementing REST API for orbital-state protocol.
"""
import re
from flask import Flask, Blueprint, request, jsonify
from ..storage.orm import AlchemyContractStorage


__name__ = "orbitalstate.server.api"


contract_storage = None
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.url_map.strict_slashes = False
    app.register_blueprint(api_bp)
    db_url = app.config.get("DB_URL", "sqlite:///contracts.db")
    global contract_storage
    contract_storage = AlchemyContractStorage(db_url)
    return app


@api_bp.route("/contract", methods=["GET", "POST"])
def contract():
    if request.method == "GET":
        # TODO: implement pagination
        # Handle get request to retrieve contracts by state
        state = request.args.get("state")
        if state:
            return jsonify(contract_storage.get_all(state))
        # Handle get request to retrieve all contracts
        return jsonify(contract_storage.get_all())
    elif request.method == "POST":
        # Handle post request to create a new contract

        # Validate the contract
        data = request.json
        if not data:
            return jsonify({"error": "Invalid contract data"}), 400
        if not re.match(r"^[a-zA-Z0-9_\-]+$", data.get("kind")) \
                or data.get("kind") not in ["OrbitalState"]:
            return jsonify({"error": "Invalid contract kind"}), 400
        if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", data.get("version")):
            return jsonify({"error": "Invalid contract version"}), 400
        if not data.get("metadata"):
            return jsonify({"error": "Invalid contract metadata"}), 400
        if not data.get("payload"):
            return jsonify({"error": "Invalid contract payload"}), 400
        
        # Create the contract
        contract = contract_storage.create(data)
        log_message = f"Contract <{contract['id']}> created"
        response = {"id": contract["id"], "message": "Contract created"}
        return jsonify(response), 201

def _validate_contract_id_matches_uuid(contract_id):
    if not re.match(r"^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$", contract_id):
        return jsonify({"error": "Invalid contract ID"}), 400

@api_bp.route("/contract/<contract_id>", methods=["GET", "PUT"])
def contract_detail(contract_id):
    # Validate the contract ID
    _validate_contract_id_matches_uuid(contract_id)

    if request.method == "GET":
        # Handle get request to retrieve contract
        contract = contract_storage.get(contract_id)
        if not contract:
            return jsonify({"error": "Contract not found"}), 404
        return jsonify(contract)
    elif request.method == "PUT":
        # Handle put request to update contract state
        data = request.json
        if not data:
            return jsonify({"error": "Invalid contract data"}), 400
        if not data.get("state"):
            return jsonify({"error": "Invalid contract state"}), 400
        if not data.get("message"):
            return jsonify({"error": "Invalid log message"}), 400
        contract = contract_storage.update_contract_state(contract_id, data["state"])
        response = {"id": contract["id"], "message": "Contract state updated"}
        return jsonify(response)
