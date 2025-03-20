from elasticsearch import Elasticsearch
import json

# Nom de l'index Elasticsearch
INDEX_NAME = "products_search_index-20250318_065953"

# Nombre d'éléments par page
BATCH_SIZE = 1000

def import_products_data():
  # Connexion à Elasticsearch (ajustez l'hôte si nécessaire)
  es = Elasticsearch("ELASTIC_URL")  # Remplacez par votre URL

  # Requête avec filtre (exemple : documents créés après une certaine date)
  query = {
    "_source": ["libelleProduit", "usageUtilite", "plusProduit", "marque", "descriptifComplementaire"],
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
  response = es.search(index=INDEX_NAME, body=query, scroll="2m", size=BATCH_SIZE)

  # Récupération des premiers résultats
  scroll_id = response["_scroll_id"]
  hits = response["hits"]["hits"]

  # Stocker les résultats
  all_results = hits[:]

  # Boucle pour récupérer toutes les pages
  while len(hits) > 0:
    response = es.scroll(scroll_id=scroll_id, scroll="2m")
    hits = response["hits"]["hits"]
    all_results.extend(hits)

  # Sauvegarde en JSON local
  with open("../resources/output.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

  print(f"Extraction terminée : {len(all_results)} documents enregistrés dans output.json")

import_products_data()
