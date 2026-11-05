from utils import ElasticSearchUtils
from constants import ASSETS_INDEX_NAME, ASSETS_INDEX_BODY

def create_assets_index():
    es = ElasticSearchUtils()
    try:
        es.create_index(ASSETS_INDEX_NAME, ASSETS_INDEX_BODY)
        assert es.get_mapping(ASSETS_INDEX_NAME)[ASSETS_INDEX_NAME] == ASSETS_INDEX_BODY["mappings"]
    except Exception as e:
        print(e)

if __name__ == "__main__":
    create_assets_index()