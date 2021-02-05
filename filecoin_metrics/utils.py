

def query_preprocess(query: str) -> str:
    new_query = query + "\n LIMIT 100"
    return new_query