class Descriptions:
    entity = "An entity can be defined in two ways. It's an instance of a (Brick) Class. More specifically, it is either a physical or a virtual thing whose properties are well-maintained to be a thing. Top three Brick Classes are Point (e.g., sensors, setpoints, etc.), Equipment (e.g., VAV, Luminaire, AHU, etc.), and Location (e.g., Room, Floor, etc.)"
    entity_id = "The identifier of an entity. Often a URI. This should be unique across the target systems (i.e., the graphs of the interest.)"
    graph = "The name of the graph. This is similar to a database name in relational databases."
    add_owner = (
        "If true, add the current user as an owner of all the entities in the graph."
    )
    relationships = "The list of relationships for the target entity. Assuming the target entity is the subject, each relation consists of the subject's predicate and object.s"
    type = "The entity's type, which is often a Brick Class."
    name = "An informative name for the entity. This does not have to be unique."
    start_time = "Starting time of the data in UNIX timestamp in seconds (float). If not given, the beginning of the data will be assumed."
    end_time = "Ending time of the data in UNIX timestamp in seconds (float). If not given, the end of the data will be assumed."
    value_type = "The type of value. Currently, there are numbers (for both floating points and integers), texts, and locations (blobs are under dev.)"
    timeseries_data = "A table of data where each row represents a value tuple. `data` field contains actual data and `columns` field contains information about the columns of the data."
    data = 'A value tuple is actually an array in JSON and consists of different columns such as an identifier, a timestamp, and a number. For example, `["http://brickserver.com#znt1", 1582412083, 71.4]`. A list of such tuples is a set of data. They share the same type of columns in a set of data, and the columns are explicitly represented in a separate field.'
    columns = "Columns explain how to interpret the values in the data. `uuid` and `timestamp` are mandatory, and specific `value_type`s can be specified."
    sql = "A raw SQL query for timeseries data. The table consist of the columns as in `value_types`."
    sparql = "A raw SPARQL query."
    actuation_value = "A value to set the target entity."
    relation_query = "A list of object URIs for the corresponding predicate. Brick Server will find entities having relations with all the objects with the predicate (i.e., AND operation.)"
