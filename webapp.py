import configparser
import json

from flask import Flask, render_template, request, jsonify

from connectors.elasticsearch.elastic_search_client import ElasticSearchClient
from opensearch.open_search_manager import OpenSearchManager

# Config parser
config = configparser.ConfigParser()
config.read("config.ini")

elasticsearch_host = config["ELASTICSEARCH"].get("HOST")
elasticsearch_port = config["ELASTICSEARCH"].getint("PORT")

elasticsearch_index_name = config["ELASTICSEARCH"].get("INDEX_NAME")
elasticsearch_source_fields = json.loads(config["ELASTICSEARCH"].get("SOURCE_FIELDS"))
elasticsearch_size_limit = config["ELASTICSEARCH"].getint("SIZE_LIMIT")
elasticsearch_query = json.loads(config["ELASTICSEARCH"].get("QUERY"))

app = Flask(__name__)
app.config["DEBUG"] = True

opensearch_manager = None
elastic_client = None

try:
    elastic_client = ElasticSearchClient(config["ELASTICSEARCH"])
    opensearch_manager = OpenSearchManager(config["OPENSEARCH"], config["RESOURCES"], config["MODELS"])
except Exception as e:
    print(f"Error initializing clients: {e}")

override_index_name = "products_search_index_20250321175941"
global_agent_id = None
global_index_name = None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download_from_elastic", methods=["GET"])
def download_from_elastic():
    if elastic_client is None:
        return jsonify({"error": "Elastic search not found, please launch an instance."})

    return jsonify({"response": elastic_client.import_products_data(elasticsearch_index_name,
                                                                    elasticsearch_source_fields,
                                                                    elasticsearch_size_limit,
                                                                    elasticsearch_query)})


@app.route("/upload_to_opensearch", methods=["GET"])
def upload_to_opensearch():
    if opensearch_manager is None:
        return jsonify({"error": "Open search not found, please launch an instance."})
    global global_index_name
    global_index_name = opensearch_manager.upload_data()
    return jsonify({"response": global_index_name})


@app.route("/create_and_deploy_agent", methods=["POST"])
def create_and_deploy_agent():
    if opensearch_manager is None:
        return jsonify({"error": "Open search not found, please launch an instance."})
    global global_agent_id
    global_agent_id = opensearch_manager.upload_model(
        override_index_name if global_index_name is None else global_index_name)

    return jsonify({"response": global_agent_id})


@app.route("/override_prompt", methods=["POST"])
def override_prompt():
    if opensearch_manager is None:
        return jsonify({"error": "Open search not found, please launch an instance."})
    global global_agent_id

    global_agent_id = opensearch_manager.upload_model(
        override_index_name if global_index_name is None else global_index_name,
        "agent_override",
        request.json["prompt"])
    return jsonify({"response": global_agent_id})


@app.route("/delete_agent", methods=["DELETE"])
def delete_agent():
    if opensearch_manager is None:
        return jsonify({"error": "Open search not found, please launch an instance."})
    if global_agent_id is None:
        return jsonify({"error": "Agent ID is not set, please deploy the agent first."})
    return jsonify({"response": opensearch_manager.delete_agent(global_agent_id)})


@app.route("/get_response", methods=["POST"])
def get_response():
    if opensearch_manager is None:
        return jsonify({"error": "Open search not found, please launch an instance."})
    if global_agent_id is None:
        return jsonify({"error": "Agent ID is not set, please deploy the agent first."})
    return jsonify({"response": opensearch_manager.query_model(global_agent_id, question=request.json["message"])})


if __name__ == "__main__":
    app.run(debug=True)
