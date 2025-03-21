from datetime import datetime


OPENSEARCH_BATCH_SIZE = 200

class OpenSearchDataManager:

    def __init__(self, opensearch_client):
        self.client = opensearch_client.client

    def upload_data_file(self, data, index_name, id_field):
        """
        Upload data to OpenSearch

        :param data: data to upload
        :param index_name: index name
        :param id_field: id field
        """
        bulk_data = []
        for i, hit in enumerate(data):
            action = {
                "index": {"_index": index_name, id_field: hit[id_field]}
            }
            bulk_data.append(action)
            bulk_data.append(hit)

            if (i + 1) % OPENSEARCH_BATCH_SIZE == 0 or (i + 1) == len(data):
                self.client.bulk(bulk_data)
                bulk_data = []
                completion_percentage = ((i + 1) / len(data)) * 100
                print(f"Progress: {completion_percentage:.2f}%")


    def create_products_index(self, base_index_name):
        """
        Create a new index for products with a KNN vector field and alias management

        :param base_index_name: base index name
        :return: new index name
        """
        date_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
        new_index_name = f"{base_index_name}_{date_suffix}"
        alias_name = base_index_name

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
                    "knn": "true",
                    "number_of_replicas": 0
                }
            }
        }

        # Create new index
        self.client.indices.create(new_index_name, body=index_body)
        print(f"Index created : {new_index_name}")

        # Check if an alias already exists
        existing_indices = self.client.indices.exists_alias(name=alias_name)
        if existing_indices:
            old_index_name = list(self.client.indices.get_alias(name=alias_name).keys())[
                0]  # Get the old index name from the alias

            # Swap alias from old index to new index
            actions = [
                {"remove": {"index": old_index_name, "alias": alias_name}},
                {"add": {"index": new_index_name, "alias": alias_name}}
            ]
            self.client.indices.update_aliases({"actions": actions})

            print(f"Alias '{alias_name}' moved from {old_index_name} to {new_index_name}")

            # Delete old index
            self.client.indices.delete(old_index_name)
            print(f"Old index deleted : {old_index_name}")
        else:
            # If no alias exists, create one
            self.client.indices.put_alias(index=new_index_name, name=alias_name)
            print(f"Alias '{alias_name}' created for index {new_index_name}")
        return new_index_name
