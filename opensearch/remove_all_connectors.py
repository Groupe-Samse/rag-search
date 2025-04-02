import requests

# OpenSearch Configuration
OPENSEARCH_URL = "http://localhost:9200"
CONNECTORS_ENDPOINT = f"{OPENSEARCH_URL}/_plugins/_ml/connectors/_search"
HEADERS = {"Content-Type": "application/json"}

# Get all connectors
search_payload = {
    "size" : 100,
    "query": {
        "match_all": {}
    }
}

response = requests.post(CONNECTORS_ENDPOINT, json=search_payload, headers=HEADERS)

if response.status_code == 200:
    connectors = response.json().get("hits", {}).get("hits", [])

    if not connectors:
        print("No connector found")
    else:
        for connector in connectors:
            connector_id = connector["_id"]
            delete_url = f"{OPENSEARCH_URL}/_plugins/_ml/connectors/{connector_id}"
            delete_response = requests.delete(delete_url, headers=HEADERS)

            if delete_response.status_code == 200:
                print(f"Connector deleted : {connector_id}")
            else:
                print(f"Error when deleting connector {connector_id}: {delete_response.text}")

else:
    print(f"Error when getting connectors : {response.text}")