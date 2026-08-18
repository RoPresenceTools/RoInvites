import os

os.chdir(os.path.dirname(__file__))

def load_sql(namespace):
    queries = {}
    for sql_file in os.listdir(f"./sql/{namespace}/"):
        if not sql_file.endswith(".sql"):
            continue

        data = open(f"./sql/{namespace}/{sql_file}").read()
        raw_queries = data.split("-- query: ")
        del raw_queries[0]

        for query in raw_queries:
            name = query.split("\n")[0]
            queries[name] = query.replace(f"{name}\n", "").strip()
    return queries