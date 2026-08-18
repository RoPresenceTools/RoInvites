from pathlib import Path

def load_sql(namespace):
    queries = {}
    sql_path = Path(__file__).parent / "sql" / namespace
    for sql_file in sql_path.glob("*.sql"):
        data = sql_file.read_text()
        raw_queries = data.split("-- query: ")
        del raw_queries[0]

        for query in raw_queries:
            name = query.split("\n")[0]
            queries[name] = query.replace(f"{name}\n", "").strip()
    return queries
