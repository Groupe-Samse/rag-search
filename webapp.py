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

elastic_client = ElasticSearchClient(config["ELASTICSEARCH"])
opensearch_manager = OpenSearchManager(config["OPENSEARCH"], config["RESOURCES"], config["MODELS"])
override_index_name = "products_search_index_20250321175941"
global_agent_id = None
global_index_name = None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download_from_elastic", methods=["GET"])
def download_from_elastic():
    return jsonify({"response": elastic_client.import_products_data(elasticsearch_index_name,
                                                                    elasticsearch_source_fields,
                                                                    elasticsearch_size_limit,
                                                                    elasticsearch_query)})


@app.route("/upload_to_opensearch", methods=["GET"])
def upload_to_opensearch():
    global global_index_name
    global_index_name = opensearch_manager.upload_data()
    return jsonify({"response": global_index_name})


@app.route("/create_and_deploy_agent", methods=["POST"])
def create_and_deploy_agent():
    global global_agent_id
    if global_index_name is None:
        global_agent_id = opensearch_manager.upload_model(override_index_name)
    else:
        global_agent_id = opensearch_manager.upload_model(global_index_name)
    return jsonify({"response": global_agent_id})


@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json["message"]
    if global_agent_id is None:
        return jsonify({"error": "Agent ID is not set, please deploy the agent first."}), 400

    response = opensearch_manager.query_model(global_agent_id, question=user_message)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
