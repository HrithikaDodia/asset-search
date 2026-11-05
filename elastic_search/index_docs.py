from utils import ElasticSearchUtils
from constants import ASSETS_INDEX_NAME, ASSETS_DATA_PATH
from helpers import load_asset_data

def bulk_index_assets_docs():
    es = ElasticSearchUtils()
    try:
        assets = load_asset_data(path=ASSETS_DATA_PATH)
        es.bulk_index_assets(assets=assets, index_name=ASSETS_INDEX_NAME)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    bulk_index_assets_docs()