import requests

# OpenSearch Configuration
OPENSEARCH_URL = "http://localhost:9200"
MODELS_ENDPOINT = f"{OPENSEARCH_URL}/_plugins/_ml/models/_search"
HEADERS = {"Content-Type": "application/json"}

# Get all models
search_payload = {
    "size": 100,
    "query": {
        "term": {
            "model_state": {
                "value": "DEPLOYED"
            }
        }
    }
}

response = requests.post(MODELS_ENDPOINT, json=search_payload, headers=HEADERS)

if response.status_code == 200:
    models = response.json().get("hits", {}).get("hits", [])

    if not models:
        print("No model found")
    else:
        for model in models:
            model_id = model["_id"]
            delete_url = f"{OPENSEARCH_URL}/_plugins/_ml/models/{model_id}"
            undeploy_response = requests.post(f"{delete_url}/_undeploy", headers=HEADERS)
            delete_response = requests.delete(delete_url, headers=HEADERS)

            if delete_response.status_code == 200:
                print(f"Model deleted : {model_id}")
            else:
                print(f"Error when deleting model {model_id}: {delete_response.text}")

else:
    print(f"Error when getting model : {response.text}")
