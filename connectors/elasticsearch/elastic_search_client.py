import json

from elasticsearch import Elasticsearch

ELASTIC_BATCH_SIZE = 1000


class ElasticSearchClient:
    def __init__(self, elastic_url):
        self.client = Elasticsearch(elastic_url)

    def import_products_data(self, elastic_index_name, source_fields, limit_size):
        # Requête avec filtre (exemple : documents créés après une certaine date)
        query = {
            "_source": source_fields,
            "size" : limit_size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "obsolete": {
                                    "value": "false"
                                }
                            }
                        },
                        {
                            "term": {
                                "webCompliant": {
                                    "value": "true"
                                }
                            }
                        }
                    ]
                }
            }
        }
        # Lancer la requête initiale avec un scroll
        response = self.client.search(index=elastic_index_name, body=query, scroll="2m", size=ELASTIC_BATCH_SIZE)

        # Récupération des premiers résultats
        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]

        # Stocker les résultats
        all_results = hits[:]

        # Boucle pour récupérer toutes les pages
        while len(hits) > 0:
            response = self.client.scroll(scroll_id=scroll_id, scroll="2m")
            hits = response["hits"]["hits"]
            all_results.extend(hits)

        # Sauvegarde en JSON local
        with open("../../resources/output.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)

        return f"Extraction terminée : {len(all_results)} documents enregistrés dans output.json"
