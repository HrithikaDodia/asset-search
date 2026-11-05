import json
from elastic_search.utils import ElasticSearchUtils
from elastic_search.constants import ASSETS_INDEX_NAME
from elastic_search.helpers import form_query

def search_query(query):
    es = ElasticSearchUtils()
    try:
        query = form_query(query)
        print(query)
        results = es.hybrid_search(query, index_name=ASSETS_INDEX_NAME)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return results
    except Exception as e:
        print(e)

if __name__ == "__main__":
    search_query("give me list of automobile companies in United States")