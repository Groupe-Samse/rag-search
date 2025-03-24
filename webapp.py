import json

from flask import Flask, render_template, request, jsonify

from app import upload_and_query_model
from connectors.elasticsearch.elastic_search_client import ElasticSearchClient

app = Flask(__name__)

with open("resources/data.json", "r", encoding="utf-8") as file:
    chatbot_data = json.load(file)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    print(request.json)
    user_message = request.json["message"]
    response = upload_and_query_model(question=user_message)
    return jsonify({"response": response})


@app.route("/download_from_elastic", methods=["GET"])
def download_from_elastic():
    e = ElasticSearchClient("https://labrique-integ-es.samse.fr/")
    return jsonify({"response": e.import_products_data("products_search_index-20250318_065953",
                                                       ["libelleProduit", "usageUtilite", "plusProduit", "marque",
                                                        "descriptifComplementaire"], 1)})


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
