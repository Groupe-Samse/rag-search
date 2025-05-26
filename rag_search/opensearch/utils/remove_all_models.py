import configparser

import requests


def remove_all_models(open_search_url):
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

    response = requests.post(f"{open_search_url}/_plugins/_ml/models/_search", json=search_payload,
                             headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        models = response.json().get("hits", {}).get("hits", [])

        if not models:
            print("No model found")
        else:
            for model in models:
                model_id = model["_id"]
                delete_url = f"{open_search_url}/_plugins/_ml/models/{model_id}"
                undeploy_response = requests.post(f"{delete_url}/_undeploy",
                                                  headers={"Content-Type": "application/json"})
                if undeploy_response.status_code == 200:
                    print(f"Model undeployed : {model_id}")
                    delete_response = requests.delete(delete_url, headers={"Content-Type": "application/json"})
                    if delete_response.status_code == 200:
                        print(f"Model deleted : {model_id}")
                    else:
                        print(f"Error when deleting model {model_id}: {delete_response.text}")
                else:
                    print(f"Error when deleting model {model_id}: {undeploy_response.text}")

    else:
        print(f"Error when getting model : {response.text}")


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("../../../config.ini")
    config_opensearch = config["OPENSEARCH"]
    remove_all_models("http://" + config_opensearch["HOST"] + ":" + config_opensearch["PORT"])
