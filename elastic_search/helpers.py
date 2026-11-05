import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from typing import Optional
from ollama import chat

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "data" / "securities_data.json"

class ParsedQuery(BaseModel):
    search_text: str
    name: Optional[str] = None
    country: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    industry: Optional[str] = None

def parse_query(query: str) -> ParsedQuery:
    assets = load_assets(DATA_PATH)

    industries = sorted({
        asset["industry"]
        for asset in assets
        if asset.get("industry")
    })

    exchanges = sorted({
        asset["exchange"]
        for asset in assets
        if asset.get("exchange")
    })

    print(exchanges)

    response = chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "system",
                "content": f"""
                    Extract structured information from a stock search query.
                    
                    Fields:
                    - name: company/security name
                    - country: canonical country name
                    - symbol: stock ticker symbol
                    - exchange: stock exchange
                    - industry: company industry
                    - search_text: remaining descriptive/semantic search terms
                    
                    Allowed industries:
                    {industries}
                    
                    Allowed exchanges:
                    {exchanges}
                    
                    Rules:
                    - Use null for name, symbol, country, and exchange if not specified.
                    - Infer exchange and industry from the user's intended company category.
                    - exchange and industry MUST be selected only from the allowed values above.
                    - If no allowed exchange or industry clearly applies, use null.
                    - Do not invent exchange or industry values.
                    - Do not guess name, symbol, country, or exchange.
                    - Remove company name, symbol, country, exchange and industry
                      from search_text once extracted.
                    - Preserve the remaining search intent in search_text.
                """
            },
            {
                "role": "user",
                "content": query
            }
        ],
        format=ParsedQuery.model_json_schema(),
        options={
            "temperature": 0
        }
    )

    return ParsedQuery.model_validate_json(
        response.message.content
    )


def form_query(search_text: str):
    parsed = parse_query(
        search_text
    )

    print(f"PARSED: {parsed}")

    filters = []

    if parsed.symbol:
        filters.append({
            "term": {
                "symbol": parsed.symbol
            }
        })

    if parsed.industry:
        filters.append({
            "term": {
                "industry": parsed.industry
            }
        })

    if parsed.country:
        filters.append({
            "term": {
                "country": parsed.country
            }
        })

    if parsed.exchange:
        filters.append({
            "term": {
                "exchange": parsed.exchange
            }
        })

    query_vector = None

    if search_text:
        query_vector = get_embedding(search_text)

    lexical_query = {
        "multi_match": {
            "query": search_text,
            "fields": ["name"],
            "boost": 0.3
        }
    }

    semantic_query = {
        "nested": {
            "path": "description_chunks",
            "query": {
                "knn": {
                    "field": "description_chunks.vector",
                    "query_vector": query_vector,
                    "k": 50,
                    "num_candidates": 100,
                    "boost": 0.7
                }
            },
            "inner_hits": {
                "size": 1,
                "_source": [
                    "description_chunks.text"
                ]
            }
        }
    }

    query = {
        "bool": {
            "filter": filters,
            "should": [
                lexical_query,
                semantic_query
            ],
            "minimum_should_match": 1
        }
    }

    return query

def chunk_text(
    text: str,
    chunk_size: int = 120,
    overlap: int = 20,
) -> list[str]:

    words = text.split()

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

def load_assets(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_embedding(text: str) -> list[float]:
    return embedding_model.encode_query(text).tolist()

def build_asset_document(raw: dict) -> dict:
    symbol = raw.get("symbol")
    exchange = raw.get("exchange")
    description = raw.get("description")

    asset = {
        "security_id": f"{exchange}:{symbol}",
        "symbol": symbol,
        "name": raw.get("name"),
        "country": raw.get("country"),
        "exchange": exchange,
        "description": description,
        "industry": raw.get("industry"),
        "portfolio_ids": []
    }

    if description:
        chunks = chunk_text(
            description,
            chunk_size=120,
            overlap=20
        )
        vectors = embedding_model.encode_document(
            chunks,
            batch_size=32,
            normalize_embeddings=True
        )
        asset["description_chunks"] = [
            {
                "text": chunk,
                "vector": vector.tolist()
            }
            for chunk, vector in zip(
                chunks,
                vectors
            )
        ]

    return asset

def load_asset_data(path: str) -> list[dict]:
    raw_assets = load_assets(path)

    assets = [
        build_asset_document(raw)
        for raw in raw_assets
    ]

    return assets