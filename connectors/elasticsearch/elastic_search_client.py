import configparser
import json
import os

from elasticsearch import Elasticsearch

current_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(current_dir, "../../resources/output.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)


class ElasticSearchClient:
    def __init__(self, elastic_config):
        self.client = Elasticsearch(elastic_config.get("HOST"))
        elasticsearch_size_limit = elastic_config.get("SIZE_LIMIT")
        self.batch_size = 1000 if not elasticsearch_size_limit else elasticsearch_size_limit

    def import_products_data(self, elastic_index_name, source_fields, size_limit, query):
        """
        Import data from elastic search to a local JSON file

        :param elastic_index_name: elastic search index name
        :param source_fields: source fields to extract
        :param size_limit: size limit of the data
        :param query: query to filter the data
        """
        query = {
            "_source": source_fields,
            "size": self.batch_size,
            "query": query
        }
        response = self.client.search(index=elastic_index_name, body=query, scroll="2m")

        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]

        all_results = hits[:]

        while len(hits) > 0 and len(all_results) < size_limit:
            response = self.client.scroll(scroll_id=scroll_id, scroll="2m")
            hits = response["hits"]["hits"]
            all_results.extend(hits)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)

        return f"Extraction over : {len(all_results)} documents saved in output.json"


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("../../config.ini")
    elastic_search_config = config["ELASTICSEARCH"]
    elastic_client = ElasticSearchClient(elastic_search_config)
    elastic_client.import_products_data(elastic_search_config.get("INDEX_NAME"),
                                        json.loads(elastic_search_config.get("SOURCE_FIELDS")),
                                        int(elastic_search_config.get("SIZE_LIMIT")),
                                        json.loads(elastic_search_config.get("QUERY")))
