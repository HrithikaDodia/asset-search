from pathlib import Path

ASSETS_INDEX_NAME = "assets"

ASSETS_INDEX_BODY = {
    "settings": {
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                }
            },
            "analyzer": {
                "security_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "security_id": {
                "type": "keyword"
            },
            "symbol": {
                "type": "keyword"
            },
            "industry": {
                "type": "keyword"
            },
            "name": {
                "type": "text",
                "analyzer": "security_analyzer"
            },
            "country": {
                "type": "keyword",
            },
            "exchange": {
                "type": "keyword",
            },
            "description": {
                "type": "text"
            },
            "description_chunks": {
                "type": "nested",
                "properties": {
                    "text": {
                        "type": "text"
                    },
                    "vector": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            },
            "portfolio_ids": {
                "type": "keyword",
                "index": False,
                "doc_values": False
            }
        }
    }
}

ASSETS_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "securities_data.json"