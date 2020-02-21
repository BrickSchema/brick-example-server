import pdb
import numbers

from mongoengine import Document, StringField, DateTimeField, ListField, DictField, BooleanField, ReferenceField
from mongoengine import IntField
from werkzeug import exceptions

DEFAULT_TOKEN_LIFETIME = 24 * 60 * 60 * 100 # 100 day in secounds TODO: This is only for dev
DEFAULT_PERMISSION_LIFETIME = 24 * 60 * 60 * 100 # 100 day in secounds TODO: This is only for dev.


async def get_all_relationships(sparql_db, entity_id):
    #TODO: Implement owl:inverseOf inside Vrituoso
    print('warning: ``inverseOf`` is not implemented yet inside Virtuoso')
    qstr = """
    select ?p ?o where {{
    {{
    <{0}> ?p ?o.
    FILTER NOT EXISTS {{ <{0}> a ?o .}}
    }}
    UNION
    {{
    ?inverse_p owl:inverseOf ?p .
    ?o ?inverse_p <{0}>.
    }}
    }}
    """.format(entity_id)
    res = await sparql_db.query(qstr)
    return [(row['p']['value'], row['o']['value']) for row in res['results']['bindings']]

class App(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    app_id = StringField(required=True, unique=True)
    permission_templates = DictField(DictField())
    """
    Example:
    {
        "znt_query": {
            "query": "select ?znt where {?znt ?p ?o.};",
            "permission_type": "R",
        }
    }
    """
    result_storages = DictField(DictField(StringField()),
                                default={},
                                )

    #valid = BooleanField(required=True)
    #expiration_date = DateTimeField(required=True)
    client_id = StringField(required=True)
    client_secret = StringField(required=True)
    pending_approvals = DictField(ListField()) # pending approvals from users. If approved, the itme goes to approvals
    approvals = DictField(ListField())
    # In both of the above cases, key is query name and list of the values are the owner IDs.
    installer = StringField()
    admins = ListField(StringField())
    callback_url = StringField()
    token_lifetime = IntField(default=DEFAULT_TOKEN_LIFETIME)
    permission_lifetime = IntField(default=DEFAULT_PERMISSION_LIFETIME)

class AppOnMarket(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    permission_templates = DictField(DictField())
    result_storages = DictField(DictField(StringField()),
                                default={},
                                )

class User(Document):
    name = StringField(required=True)
    userid = StringField(required=True)
    email = StringField(required=True)
    installed_apps = ListField(ReferenceField(App))
    is_admin = BooleanField(default=False)

def get_doc(doc_type, unique=True, **query):
    docs = doc_type.objects(**query)
    if not docs:
        raise exceptions.NotFound('{0} for {1} does not exist.'.format(doc_type.__name__, query))
    if len(docs) > 1:
        raise exceptions.Conflict('Multiple {0} for {1} are found.'.format(doc_type.__name__, query))
    return docs[0]

