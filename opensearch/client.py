from opensearchpy import OpenSearch

host = 'localhost'
port = 9200


def client():
    # Create the client with SSL/TLS enabled, but hostname verification disabled.
    return OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )


def define_cluster_settings(opensearch_client):
    settings = {
        "persistent": {
            "plugins.ml_commons.memory_feature_enabled": True,
            "plugins.ml_commons.rag_pipeline_feature_enabled": True,
            "plugins.ml_commons.agent_framework_enabled": True,
            "plugins.ml_commons.only_run_on_ml_node": False,
            "plugins.ml_commons.connector_access_control_enabled": True,
            "plugins.ml_commons.trusted_connector_endpoints_regex": [
                ".*"
            ]
        }
    }
    opensearch_client.cluster.put_settings(body=settings)
