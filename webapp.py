import configparser
import json

from flask import Flask, render_template, request, jsonify, g

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
index_name = "products_search_index_20250321175941"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    print(request.json)
    user_message = request.json["message"]
    response = opensearch_manager.upload_and_query_model(question=user_message)
    return jsonify({"response": response})


@app.route("/download_from_elastic", methods=["GET"])
def download_from_elastic():
    return jsonify({"response": elastic_client.import_products_data(elasticsearch_index_name,
                                                                    elasticsearch_source_fields,
                                                                    elasticsearch_size_limit,
                                                                    elasticsearch_query)})


@app.route("/upload_to_opensearch", methods=["GET"])
def upload_to_opensearch():
    g.new_index_name = opensearch_manager.upload_data()
    return jsonify({"response": index_name})


@app.route("/create_and_deploy_agent", methods=["POST"])
def create_and_deploy_agent():
    new_index_name = getattr(g, 'index_name', index_name)
    return jsonify({"response": opensearch_manager.upload_model(new_index_name)})


if __name__ == "__main__":
    app.run(debug=True)
