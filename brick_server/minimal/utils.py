def parse_graphdb_result(res):
    keys = res["head"]["vars"]
    d = {key: [] for key in keys}
    for row in res["results"]["bindings"]:
        for i, key in enumerate(keys):
            d[key].append(row[key]["value"])
    return d
