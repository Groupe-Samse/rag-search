# rag-search
OpenSearch ChatGPT Retrieval-Augmented Generation

## Downloading OpenSearch 2.17.1
https://opensearch.org/old_downloads.html 

# How to run
1. Download OpenSearch 2.17.1 and unzip it
2. Run OpenSearch
3. Change the `config.ini` file
   1. Set your OpenSearch host and port
   2. Set your ElasticSearch host, port, index name, source fields to vector index, the query and the size limit
   3. Set your OpenAI API key in your environment variables
   4. Override the default OpenAI model if you want to use a different one (Optional)
   5. If you want to override the sentence transformer model, you must adapt the text_embedding dimension vector
4. Run `webapp.py`
5. Open your browser and go to `http://localhost:5000`
6. Click on the Elasticsearch button to download the data (will be downloaded in the `resources` folder)
7. Click on the OpenSearch button to index the data
8. Click on the Server button to upload the agent
9. Discuss with your agent in the chat window
