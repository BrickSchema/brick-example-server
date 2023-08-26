from multidict import MultiDict


def parse_graphdb_result(res):
    keys = res["head"]["vars"]
    d = {key: [] for key in keys}
    for row in res["results"]["bindings"]:
        for i, key in enumerate(keys):
            d[key].append(row[key]["value"])
    return d


async def get_external_references(domain, entity_id):
    query = f"""
select distinct ?k ?v where {{
    {entity_id} ref:hasExternalReference ?o .
    ?o ?k ?v .
}}
        """
    from brick_server.minimal.dbs import graphdb

    res = await graphdb.query(domain.name, query)
    parsed_result = parse_graphdb_result(res)
    multi_dict = MultiDict(zip(parsed_result["k"], parsed_result["v"]))
    return multi_dict
