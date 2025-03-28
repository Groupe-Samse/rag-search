import requests

# OpenSearch Configuration
OPENSEARCH_URL = "http://localhost:9200"
AGENTS_ENDPOINT = f"{OPENSEARCH_URL}/_plugins/_ml/agents/_search"
HEADERS = {"Content-Type": "application/json"}

# Get all agents
search_payload = {
    "size" : 100,
    "query": {
        "match_all": {}
    }
}

response = requests.post(AGENTS_ENDPOINT, json=search_payload, headers=HEADERS)

if response.status_code == 200:
    agents = response.json().get("hits", {}).get("hits", [])

    if not agents:
        print("No agent found")
    else:
        for agent in agents:
            agent_id = agent["_id"]
            delete_url = f"{OPENSEARCH_URL}/_plugins/_ml/agents/{agent_id}"
            delete_response = requests.delete(delete_url, headers=HEADERS)

            if delete_response.status_code == 200:
                print(f"Agent deleted : {agent_id}")
            else:
                print(f"Error when deleting agent {agent_id}: {delete_response.text}")

else:
    print(f"Erreur when getting agents : {response.text}")