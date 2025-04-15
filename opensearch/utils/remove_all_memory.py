import configparser

import requests


def remove_all_memories(open_search_url):
    # Get all memories
    search_payload = {
        "size": 100,
        "query": {
            "match_all": {}
        }
    }

    response = requests.post(f"{open_search_url}/_plugins/_ml/memory/_search", json=search_payload,
                             headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        memories = response.json().get("hits", {}).get("hits", [])

        if not memories:
            print("No memory found")
        else:
            for memory in memories:
                memory_id = memory["_id"]
                delete_url = f"{open_search_url}/_plugins/_ml/memory/{memory_id}"
                delete_response = requests.delete(delete_url, headers={"Content-Type": "application/json"})

                if delete_response.status_code == 200:
                    print(f"Memory deleted : {memory_id}")
                else:
                    print(f"Error when deleting memory {memory_id}: {delete_response.text}")

    else:
        print(f"Error when getting memories : {response.text}")


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("../config.ini")
    config_opensearch = config["OPENSEARCH"]
    remove_all_memories("http://" + config_opensearch["HOST"] + ":" + config_opensearch["PORT"])
