import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers

load_dotenv()

elastic_search_url = os.getenv("ELASTIC_SEARCH_URL")
elastic_search_username = os.getenv("ELASTIC_SEARCH_USERNAME")
elastic_search_password = os.getenv("ELASTIC_SEARCH_PASSWORD")
elastic_search_ca_cert = os.getenv("ELASTIC_SEARCH_CA_CERT")

class ElasticSearchUtils:
    def __init__(self):
        self.es = Elasticsearch(
            elastic_search_url,
            basic_auth=(elastic_search_username, elastic_search_password),
            ca_certs=elastic_search_ca_cert
        )

    def create_index(self, index_name, index_body):
        if not self.es.indices.exists(index=index_name):
            response = self.es.indices.create(
                index=index_name,
                body=index_body
            )
            print(f"Index created with response: {response}")
        else:   
            raise Exception(f"Index '{index_name}' already exists")

    def get_mapping(self, index_name):
        mapping = self.es.indices.get_mapping(index=index_name)
        return mapping

    def bulk_index_assets(self, assets: list[dict], index_name: str):
        actions = []

        for asset in assets:
            actions.append({
                "_index": index_name,
                "_id": asset["security_id"],
                "_source": asset
            })

        success, errors = helpers.bulk(
            self.es,
            actions,
            raise_on_error=False,
        )

        print(f"Successfully indexed: {success}")

        if errors:
            print(f"Failed documents: {len(errors)}")

            for error in errors:
                print(error)

    def hybrid_search(
            self,
            query: dict,
            index_name: str,
            size: int = 10
    ):

        response = self.es.search(
            index=index_name,
            query=query,
            size=size
        )

        return [
            {
                "score": hit["_score"],
                **hit["_source"]
            }
            for hit in response["hits"]["hits"]]