import configparser
import json
import os
import sys

from file.manage_json_file import read_clean_and_aggregate_tab
from opensearch.data_manager import OpenSearchDataManager
from opensearch.model_manager import OpenSearchModelManager
from opensearch.open_search_client import OpenSearchClient

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")

# Config parser
config = configparser.ConfigParser()
config.read("config.ini")

host = config["OPENSEARCH"].get("HOST")
port = config["OPENSEARCH"].getint("PORT")
index_name = config["OPENSEARCH"].get("INDEX_NAME")

field_id = config["RESOURCES"].get("ID")

sentence_transformer_model_name = config["MODELS"].get("SENTENCE_TRANSFORMER")

sentence_transformer_model_payload = {
    "name": sentence_transformer_model_name,
    "version": "1.0.1",
    "model_format": "TORCH_SCRIPT"
}

gpt_model_name = config["MODELS"].get("GPT")

opensearch_client = OpenSearchClient(host, port)

if OPEN_AI_KEY is None:
    print("La clé API OPEN_AI_KEY n'est pas définie.")
    sys.exit(1)
else:
    print("Clé API chargée avec succès.")

def print_config():
    print("Opensearch host: " + host)
    print("Opensearch port: " + str(port))
    print("Opensearch index_name: " + index_name)
    print("field_id: " + field_id)
    print("sentence_transformer_model_name: " + sentence_transformer_model_name)
    print("sentence_transformer_model_payload: " + str(sentence_transformer_model_payload))
    print("gpt_model_name: " + gpt_model_name)
    print("OPEN_AI_KEY: " + OPEN_AI_KEY)


def upload_data():
    print_config()
    # Data manager
    data_manager = OpenSearchDataManager(opensearch_client)
    model_manager = OpenSearchModelManager(opensearch_client)

    sentence_transformer_model_id = model_manager.register_and_deploy_ml_model(sentence_transformer_model_payload,
                                                                               sentence_transformer_model_name)
    model_manager.put_ingest_pipeline(sentence_transformer_model_id)

    new_index_name = data_manager.create_products_index(index_name)
    data_manager.upload_data_file(read_clean_and_aggregate_tab("resources/outputtest.json"), new_index_name, field_id)

    upload_and_query_model(new_index_name)


def upload_and_query_model(new_index_name="products_search_index_20250321175941", question="Bonjour, je souhaite acheter un Câble U1000 R2V 5G1,5 mm² 50 m"):
    # Opensearch model manager
    model_manager = OpenSearchModelManager(opensearch_client)

    sentence_transformer_model_id = model_manager.register_and_deploy_ml_model(sentence_transformer_model_payload,
                                                                               sentence_transformer_model_name)
    model_manager.put_ingest_pipeline(sentence_transformer_model_id)

    connector_id = model_manager.create_connector(gpt_model_name, OPEN_AI_KEY)
    print("Connector id " + connector_id)
    gpt_model_payload = {
        "name": gpt_model_name,
        "function_name": "remote",
        "description": "test model",
        "connector_id": connector_id
    }
    gpt_model_id = model_manager.register_and_deploy_ml_model(gpt_model_payload, gpt_model_name)
    print("GPT model id " + gpt_model_id)
    agent_id = model_manager.register_agent("gpt4o-mini-agent", new_index_name, sentence_transformer_model_id,
                                            gpt_model_id)
    print("Agent id " + agent_id)
    inference = model_manager.query_agent(agent_id, question)
    print(inference)
    return json.loads(inference["inference_results"][0]["output"][0]["result"])["choices"][0]["message"]["content"]

if __name__ == "__main__":
    upload_and_query_model()
