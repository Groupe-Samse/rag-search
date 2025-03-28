import configparser

from flask import Flask, render_template, request, jsonify

from connectors.elasticsearch.elastic_search_client import ElasticSearchClient
from opensearch.open_search_manager import OpenSearchManager

# Config parser
config = configparser.ConfigParser()
config.read("config.ini")

elasticsearch_host = config["ELASTICSEARCH"].get("HOST")
elasticsearch_port = config["ELASTICSEARCH"].getint("PORT")

elasticsearch_index_name = config["ELASTICSEARCH"].get("INDEX_NAME")
elasticsearch_source_fields = config["ELASTICSEARCH"].get("SOURCE_FIELDS")
elasticsearch_size_limit = config["ELASTICSEARCH"].get("SIZE_LIMIT")
elasticsearch_query = config["ELASTICSEARCH"].get("QUERY")

app = Flask(__name__)
app.config["DEBUG"] = True

opensearch_manager = OpenSearchManager(config["OPENSEARCH"],config["RESOURCES"], config["MODELS"])

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
    e = ElasticSearchClient(config["ELASTICSEARCH"])
    return jsonify({"response": e.import_products_data(elasticsearch_index_name,
                                                       elasticsearch_source_fields,
                                                       elasticsearch_size_limit,
                                                       elasticsearch_query)})


@app.route("/upload_to_opensearch", methods=["POST"])
def upload_to_opensearch():
    pass


@app.route("/create_and_deploy_agent", methods=["POST"])
def create_and_deploy_agent():
    pass


@app.route("/deploy_existing_agent", methods=["POST"])
def deploy_existing_agent():
    pass


if __name__ == "__main__":
    app.run(debug=True)
