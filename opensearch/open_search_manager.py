import configparser
import json
import os
import sys

from file.manage_json_file import read_clean_and_aggregate_tab
from opensearch.data_manager import OpenSearchDataManager
from opensearch.model_manager import OpenSearchModelManager
from opensearch.open_search_client import OpenSearchClient

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
current_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(current_dir, "../resources/output.json")


class OpenSearchManager:
    def __init__(self, opensearch_config, resource_config, model_config):
        self.host = opensearch_config.get("HOST")
        self.port = opensearch_config.get("PORT")
        self.opensearch_client = OpenSearchClient(self.host, self.port)
        self.index_name = opensearch_config.get("INDEX_NAME")
        self.field_id = resource_config.get("ID")
        self.sentence_transformer_model_name = model_config.get("SENTENCE_TRANSFORMER")
        self.sentence_transformer_model_payload = {
            "name": self.sentence_transformer_model_name,
            "version": "1.0.1",
            "model_format": "TORCH_SCRIPT"
        }
        self.gpt_model_name = model_config.get("GPT")

    if OPEN_AI_KEY is None:
        print("La clé API OPEN_AI_KEY n'est pas définie.")
        sys.exit(1)
    else:
        print("Clé API chargée avec succès.")

    def __print_config(self):
        print("Opensearch host: " + self.host)
        print("Opensearch port: " + str(self.port))
        print("Opensearch index_name: " + self.index_name)
        print("field_id: " + self.field_id)
        print("sentence_transformer_model_name: " + self.sentence_transformer_model_name)
        print("sentence_transformer_model_payload: " + str(self.sentence_transformer_model_payload))
        print("gpt_model_name: " + self.gpt_model_name)
        print("OPEN_AI_KEY: " + OPEN_AI_KEY)

    def upload_data(self):
        """
        Print the configuration
        Load open search data manager and model manager
        Deploy the sentence transformer model (from config.ini)
        Put the ingest pipeline
        Create a new index
        Upload the data from the file output.json

        :return:
        """
        self.__print_config()
        # Data manager
        data_manager = OpenSearchDataManager(self.opensearch_client)
        model_manager = OpenSearchModelManager(self.opensearch_client)

        sentence_transformer_model_id = model_manager.register_and_deploy_ml_model(
            self.sentence_transformer_model_payload,
            self.sentence_transformer_model_name)
        model_manager.put_ingest_pipeline(sentence_transformer_model_id)

        new_index_name = data_manager.create_products_index(self.index_name)
        data_manager.upload_data_file(read_clean_and_aggregate_tab(output_path), new_index_name,
                                      self.field_id)
        return new_index_name

    def upload_model(self, new_index_name):
        # Opensearch model manager
        model_manager = OpenSearchModelManager(self.opensearch_client)
        sentence_transformer_model_id = model_manager.register_and_deploy_ml_model(
            self.sentence_transformer_model_payload,
            self.sentence_transformer_model_name)
        model_manager.put_ingest_pipeline(sentence_transformer_model_id)
        connector_id = model_manager.create_connector(self.gpt_model_name, OPEN_AI_KEY)
        print("Connector id " + connector_id)
        gpt_model_payload = {
            "name": self.gpt_model_name,
            "function_name": "remote",
            "description": "test model",
            "connector_id": connector_id
        }
        gpt_model_id = model_manager.register_and_deploy_ml_model(gpt_model_payload, self.gpt_model_name)
        print("GPT model id " + gpt_model_id)
        agent_id = model_manager.register_agent(f"{gpt_model_id}-agent", new_index_name, sentence_transformer_model_id,
                                                gpt_model_id)
        print("Agent id " + agent_id)
        return agent_id

    def upload_and_query_model(self, new_index_name, question):
        agent_id = self.upload_model(new_index_name)
        model_manager = OpenSearchModelManager(self.opensearch_client)
        inference = model_manager.query_agent(agent_id, question)
        print(inference)
        return json.loads(inference["inference_results"][0]["output"][0]["result"])["choices"][0]["message"]["content"]

    def query_model(self, agent_id, question):
        model_manager = OpenSearchModelManager(self.opensearch_client)
        inference = model_manager.query_agent(agent_id, question)
        print(inference)
        return json.loads(inference["inference_results"][0]["output"][0]["result"])["choices"][0]["message"]["content"]

    def delete_agent(self, agent_id):
        model_manager = OpenSearchModelManager(self.opensearch_client)
        try:
            model_manager.delete_agent(agent_id)
        except Exception as e:
            return f"Exception occurred while deleting agent {agent_id}: {e}"
        return f"Agent {agent_id} deleted successfully."


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("../config.ini")
    config_opensearch = config["OPENSEARCH"]
    config_resources = config["RESOURCES"]
    config_models = config["MODELS"]
    open_search_manager = OpenSearchManager(config_opensearch, config_resources, config_models)
    index_name = open_search_manager.upload_data()
    open_search_manager.upload_and_query_model(new_index_name=index_name,
                                               question="Bonjour, je souhaite acheter un Câble U1000 R2V 5G1,5 mm² 50 m")
