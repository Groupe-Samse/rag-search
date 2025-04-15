import configparser

import requests


def remove_all_connectors(open_search_url):
    # Get all connectors
    search_payload = {
        "size": 100,
        "query": {
            "match_all": {}
        }
    }

    response = requests.post(f"{open_search_url}/_plugins/_ml/connectors/_search", json=search_payload,
                             headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        connectors = response.json().get("hits", {}).get("hits", [])

        if not connectors:
            print("No connector found")
        else:
            for connector in connectors:
                connector_id = connector["_id"]
                delete_url = f"{open_search_url}/_plugins/_ml/connectors/{connector_id}"
                delete_response = requests.delete(delete_url, headers={"Content-Type": "application/json"})

                if delete_response.status_code == 200:
                    print(f"Connector deleted : {connector_id}")
                else:
                    print(f"Error when deleting connector {connector_id}: {delete_response.text}")

    else:
        print(f"Error when getting connectors : {response.text}")


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("../config.ini")
    config_opensearch = config["OPENSEARCH"]
    remove_all_connectors("http://" + config_opensearch["HOST"] + ":" + config_opensearch["PORT"])
