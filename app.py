from file.manage_json_file import read_clean_and_aggregate_tab
from opensearch.client import OpenSearchClient
from opensearch.data_manager import OpenSearchDataManager
from opensearch.model_manager import OpenSearchModelManager

ID_FIELD = "_id"
INDEX_NAME = 'products_search_index'
OPEN_AI_KEY = "INSERT_KEY_HERE"
sentence_transformer_model_name = "huggingface/sentence-transformers/all-MiniLM-L12-v2"
sentence_transformer_model_payload = {
    "name": sentence_transformer_model_name,
    "version": "1.0.1",
    "model_format": "TORCH_SCRIPT"
}

gpt_model_name = "gpt4o-mini"
host = "localhost"
port = "9200"

opensearch_client = OpenSearchClient(host, port)

def main():
    opensearch_client.define_cluster_settings()
    # Data manager
    data_manager = OpenSearchDataManager(opensearch_client)
    # Opensearch model manager
    model_manager = OpenSearchModelManager(opensearch_client)

    new_index_name = data_manager.create_products_index(INDEX_NAME)
    data_manager.upload_data_file(read_clean_and_aggregate_tab("resources/outputtest.json"), new_index_name, ID_FIELD)

    sentence_transformer_model_id = model_manager.register_and_deploy_ml_model(sentence_transformer_model_payload,
                                                                 sentence_transformer_model_name)
    model_manager.put_ingest_pipeline(sentence_transformer_model_id)

    connector_id = model_manager.create_connector(gpt_model_name, OPEN_AI_KEY)

    gpt_model_payload = {
        "name": gpt_model_name,
        "function_name": "remote",
        "description": "test model",
        "connector_id": connector_id
    }

    gpt_model_id = model_manager.register_and_deploy_ml_model(gpt_model_payload, gpt_model_name)

    agent_id = model_manager.register_agent("gpt4o-mini-agent", new_index_name, sentence_transformer_model_id,
                              gpt_model_id)
    print(model_manager.query_agent(agent_id, "Bonjour, je souhaite acheter une scie circulaire pour le bois"))


main()
