from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    DynamicDocument,
    ListField,
    ReferenceField,
    StringField,
)

from brick_server.minimal.exceptions import DoesNotExistError, MultipleObjectsFoundError

# DEFAULT_TOKEN_LIFETIME = (
#     24 * 60 * 60 * 100
# )  # 100 day in secounds TODO: This is only for dev
# DEFAULT_PERMISSION_LIFETIME = (
#     24 * 60 * 60 * 100
# )  # 100 day in secounds TODO: This is only for dev.


class User(DynamicDocument):
    name = StringField(required=True)
    user_id = StringField(required=True, unique=True)
    email = StringField(required=True)
    is_admin = BooleanField(default=False)
    is_approved = BooleanField(default=False)
    registration_time = DateTimeField(required=True)
    meta = {
        "allow_inheritance": True,
    }
    app_tokens = ListField(StringField(), default=[])


class AppToken(Document):
    user = ReferenceField(User, required=True)
    token = StringField(required=True)
    name = StringField(default=None)
    meta = {
        "indexes": ["user"],
    }


class OAuthRefreshToken(Document):
    user = ReferenceField(User)
    token = StringField(required=True)


class OAuthAccessToken(Document):  # TODO: Might not need this one.
    user = ReferenceField(User)
    token = StringField(required=True)


class GrafanaDashboard(Document):
    user = ReferenceField(User)
    uid = StringField(required=True)
    grafana_id = StringField(required=True)
    url = StringField(required=True)


class Domain(Document):
    name = StringField(required=True, unique=True)


def get_doc(doc_type, **query):
    try:
        doc = doc_type.objects.get(**query)
    except doc_type.DoesNotExist:
        print("WARNING: {} does not exist for {}".format(doc_type, query))
        raise DoesNotExistError(doc_type, str(query))
    except doc_type.MultipleObjectsReturned:
        raise MultipleObjectsFoundError(doc_type, str(query))
    return doc


def get_docs(doc_type, **query):
    docs = doc_type.objects(**query)
    return docs
