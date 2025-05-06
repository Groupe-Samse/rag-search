import configparser

import requests


def remove_all_agents(open_search_url):
    # Get all agents
    search_payload = {
        "size": 100,
        "query": {
            "match_all": {}
        }
    }

    response = requests.post(f"{open_search_url}/_plugins/_ml/agents/_search", json=search_payload,
                             headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        agents = response.json().get("hits", {}).get("hits", [])

        if not agents:
            print("No agent found")
        else:
            for agent in agents:
                agent_id = agent["_id"]
                delete_url = f"{open_search_url}/_plugins/_ml/agents/{agent_id}"
                delete_response = requests.delete(delete_url, headers={"Content-Type": "application/json"})

                if delete_response.status_code == 200:
                    print(f"Agent deleted : {agent_id}")
                else:
                    print(f"Error when deleting agent {agent_id}: {delete_response.text}")

    else:
        print(f"Error when getting agents : {response.text}")


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("../config.ini")
    config_opensearch = config["OPENSEARCH"]
    remove_all_agents("http://" + config_opensearch["HOST"] + ":" + config_opensearch["PORT"])
