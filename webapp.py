import configparser
import json

from flask import Flask, render_template, request, jsonify

from rag_search.connectors.elastic_search_client import ElasticSearchClient
from rag_search.opensearch.open_search_manager import OpenSearchManager
from semantic.semantic_detection import Classifier

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
classifier = Classifier()

try:
    elastic_client = ElasticSearchClient(config["ELASTICSEARCH"])
    opensearch_manager = OpenSearchManager(config["OPENSEARCH"], config["RESOURCES"], config["MODELS"])
except Exception as e:
    print(f"Error initializing clients: {e}")

override_index_name = "products_search_index_20250321175941"
global_agent_id = None
global_index_name = None
global_agent_memory_id = None


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


@app.route("/display_fine_tune", methods=["GET"])
def display_fine_tune():
    with open("resources/fine_tune.jsonl", "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    return json.dumps(data, indent=2, ensure_ascii=False)


@app.route("/display_prompt", methods=["GET"])
def display_prompt():
    if opensearch_manager is None:
        return jsonify({"error": "Open search not found, please launch an instance."})
    if global_agent_id is None:
        return jsonify({"error": "Agent ID is not set, please deploy the agent first."})
    return json.loads(opensearch_manager.get_agent_prompt(global_agent_id))


@app.route("/get_response", methods=["POST"])
def get_response():
    if opensearch_manager is None:
        return jsonify({"error": "Open search not found, please launch an instance."})
    if global_agent_id is None:
        return jsonify({"error": "Agent ID is not set, please deploy the agent first."})

    global global_agent_memory_id

    user_request = request.json["message"]
    semantic_detection = classifier.classify_query(user_request)

    print("User request detected as:", semantic_detection)

    if global_agent_memory_id is None:
        inference_output = opensearch_manager.query_model(global_agent_id, user_request, semantic_detection)
        global_agent_memory_id = inference_output[0]["result"]

    else:
        inference_output = opensearch_manager.query_model_memory(global_agent_id, global_agent_memory_id,
                                                                 user_request, semantic_detection)

    return jsonify({"response": json.loads(inference_output[2]["result"])["choices"][0]["message"]["content"]})


@app.route("/delete_memory", methods=["DELETE"])
def delete_memory():
    global global_agent_memory_id
    if global_agent_memory_id is None:
        return jsonify({"error": "Memory ID is not set, please query the model first."})
    response = opensearch_manager.delete_memory(global_agent_memory_id)
    global_agent_memory_id = None
    return jsonify({"response": f"Memory deleted successfully. {response}"})


if __name__ == "__main__":
    app.run(debug=True)
