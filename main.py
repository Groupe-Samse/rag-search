from file.json_file import read_json_return_result_tab
from opensearch.client import client, define_cluster_settings
from opensearch.data import create_products_index, upload_data_file
from opensearch.model import register_and_deploy_ml_model, put_ingest_pipeline, \
    create_connector, register_agent, query_agent

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

search_client = client()


def main():
    define_cluster_settings(search_client)
    create_products_index(search_client, INDEX_NAME)
    upload_data_file(search_client, read_json_return_result_tab("resources/products.json"), INDEX_NAME, ID_FIELD)
    sentence_transformer_model_id = register_and_deploy_ml_model(search_client,
                                                                 sentence_transformer_model_payload,
                                                                 sentence_transformer_model_name)
    put_ingest_pipeline(search_client, sentence_transformer_model_id)

    connector_id = create_connector(search_client, gpt_model_name, OPEN_AI_KEY)

    gpt_model_payload = {
        "name": gpt_model_name,
        "function_name": "remote",
        "description": "test model",
        "connector_id": connector_id
    }

    gpt_model_id = register_and_deploy_ml_model(search_client, gpt_model_payload, gpt_model_name)

    agent_id = register_agent(search_client, "gpt4o-mini-agent", INDEX_NAME, sentence_transformer_model_id,
                              gpt_model_id)
    print(query_agent(search_client, agent_id, "Bonjour, je souhaite acheter une scie circulaire pour le bois"))


main()
