import time


class OpenSearchModelManager:
    def __init__(self, opensearch_client):
        self.client = opensearch_client.client

    def search_model(self, model_name):
        """
        Search for a model by name

        :param model_name: model name
        :return: empty list if no model found, list of models corresponding otherwise
        """
        endpoint = "/_plugins/_ml/models/_search"
        response = self.client.transport.perform_request(
            method="GET",
            url=endpoint,
            body={"query": {"match": {"name": model_name}}}
        )
        return response["hits"]["hits"]

    def register_and_deploy_ml_model(self, model_payload, model_name):
        """
        Register and deploy a model, if it already exists, return the existing model id

        :param model_payload: model payload
        :param model_name: model name
        :return: model id
        """
        existing_model = self.search_model(model_name)

        if len(existing_model) > 0:
            if "model_id" in existing_model[0]["_source"]:
                return existing_model[0]["_source"]["model_id"]
            return existing_model[0]["_id"]

        endpoint = "/_plugins/_ml/models/_register?deploy=true"
        response = self.client.transport.perform_request(
            method="POST",
            url=endpoint,
            body=model_payload,
        )
        task_id = response["task_id"]

        while self.get_model_id_from_task_id(task_id) is None:
            print("Waiting for model to be ready...")
            time.sleep(1)
        return self.get_model_id_from_task_id(task_id)

    def get_model_id_from_task_id(self, task_id):
        """
        Get the model id from a task id

        :param task_id:
        :return:
        """
        endpoint = "/_plugins/_ml/tasks/" + task_id
        response = self.client.transport.perform_request(
            method="GET",
            url=endpoint
        )
        if response["state"] == "COMPLETED":
            return response["model_id"]
        else:
            return None

    def put_ingest_pipeline(self, model_id):
        pipeline_body = {
            "description": "Text embedding pipeline",
            "processors": [
                {
                    "text_embedding": {
                        "model_id": model_id,
                        "field_map": {
                            "text": "embedding"
                        }
                    }
                }
            ]
        }
        self.client.ingest.put_pipeline("test-pipeline-local-model", body=pipeline_body)

    def search_connector(self, connector_name):
        endpoint = "/_plugins/_ml/connectors/_search"
        response = self.client.transport.perform_request(
            method="GET",
            url=endpoint,
            body={"query": {"match": {"name": connector_name}}}
        )
        return response["hits"]["hits"]

    def create_connector(self, model_name, openai_key):
        connector_name = "OpenAI Mini Chat Connector"

        # existing_connector = search_connector(opensearch_client, connector_name)
        # if len(existing_connector) > 0:
        #     return existing_connector[0]["_id"]

        connector_config = {
            "name": connector_name,
            "description": "The connector to model service for GPT 4o Mini",
            "version": 1,
            "protocol": "http",
            "parameters": {
                "endpoint": "api.openai.com",
                "model": model_name  # You can set a fine-tuned model here
            },
            "credential": {
                "openAI_key": openai_key
            },
            "actions": [
                {
                    "action_type": "predict",
                    "method": "POST",
                    "url": "https://${parameters.endpoint}/v1/chat/completions",
                    "headers": {
                        "Authorization": "Bearer ${credential.openAI_key}"
                    },
                    "request_body": "{ \"model\": \"${parameters.model}\", \"messages\": ${parameters.messages} }"
                }
            ]
        }

        endpoint = "/_plugins/_ml/connectors/_create"
        response = self.client.transport.perform_request(method="POST", url=endpoint, body=connector_config)
        return response["connector_id"]

    def search_agent(self, agent_name):
        endpoint = "/_plugins/_ml/agents/_search"
        response = self.client.transport.perform_request(
            method="GET",
            url=endpoint,
            body={"query": {"match": {"name": agent_name}}}
        )
        return response["hits"]["hits"]

    def register_agent(self, agent_name, index_name, sentence_transformer_model_id, gpt_model_id):
        # agent = search_agent(opensearch_client, agent_name)
        # if len(agent) > 0:
        #     return agent[0]["_id"]

        messages = """ [ { "role": "system",
                "content": "Tu es un expert en vente de produits de bricolage, spécialisé dans le conseil personnalisé aux clients et tu utilises des réponses provenant d'une recherche pour fournir des recommandations précises.  Mon contexte est que je travaille dans une enseigne de bricolage et je souhaite aider mes clients à trouver les produits adaptés à leurs projets. Tu vas jouer le rôle d'un vendeur de bricolage expérimenté, répondant uniquement si une réponse pertinente est disponible à partir de la recherche sémantique. Voici les étapes à suivre : 1. Si une réponse est fournie en entrée, analyser les informations pour comprendre le besoin du client. 2. Présenter le ou les produits recommandés, en décrivant leurs principales caractéristiques et avantages spécifiques au projet du client. 3. Expliquer en quoi ces produits sont les plus adaptés en fonction des critères fournis, comme la durabilité, le prix ou l'efficacité. 4. Offrir des conseils supplémentaires, comme des accessoires ou outils complémentaires, uniquement si la recherche sémantique propose des options pertinentes. 5. Si aucune information ne correspond exactement au besoin du client, indiquer poliment qu'aucun produit spécifique n’est disponible dans cette catégorie. Le résultat attendu est une réponse ciblée et utile pour le client, uniquement fournie si une recommandation pertinente existe via la recherche sémantique. Selon les réponses dans ce contexte, réponds au mieux à l'utilisateur : ${parameters.VectorDBTool.output}" },
                { "role": "user", "content": "${parameters.question}" }]"""

        agent_config = {
            "name": agent_name,
            "type": "flow",
            "description": "this is a test agent",
            "tools": [{
                "type": "VectorDBTool",
                "parameters": {
                    "model_id": sentence_transformer_model_id,
                    "index": index_name,
                    "embedding_field": "text_embedding",
                    "source_field": ["text"],
                    "k": 1,
                    "input": "${parameters.question}"
                }
            },
                {
                    "type": "MLModelTool",
                    "description": "A general tool to answer questions",
                    "parameters": {
                        "model_id": gpt_model_id,
                        "messages": messages
                    }
                }
            ]
        }

        endpoint = "/_plugins/_ml/agents/_register"
        response = self.client.transport.perform_request(method="POST", url=endpoint, body=agent_config)
        return response["agent_id"]

    def query_agent(self, agent_id, question):
        endpoint = "/_plugins/_ml/agents/" + agent_id + "/_execute"

        response = self.client.transport.perform_request(
            method="POST",
            url=endpoint,
            body={"parameters": {"question": question}}
        )
        return response
