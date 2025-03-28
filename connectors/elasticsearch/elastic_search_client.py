import json

from elasticsearch import Elasticsearch


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

        with open("../../resources/output.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)

        return f"Extraction over : {len(all_results)} documents saved in output.json"
