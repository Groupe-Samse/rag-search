def upload_data_file(opensearch_client, data, index_name, id_field):
    bulk_data = []
    for hit in data:
        action = {
            "index": {"_index": index_name, id_field: hit[id_field]}
        }
        bulk_data.append(action)
        bulk_data.append(hit)

    opensearch_client.bulk(bulk_data)


def create_products_index(opensearch_client, index_name):
    if opensearch_client.indices.exists(index_name):
        return

    index_body = {
        "mappings": {
            "properties": {
                "text": {
                    "type": "text"
                },
                "text_embedding": {
                    "type": "knn_vector",
                    "dimension": 384
                }
            }
        },
        "settings": {
            "index": {
                "knn.space_type": "cosinesimil",
                "default_pipeline": "test-pipeline-local-model",
                "knn": "true"
            }
        }
    }
    opensearch_client.indices.create(index_name, body=index_body)
