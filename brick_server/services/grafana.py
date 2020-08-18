import pdb
from copy import deepcopy
from uuid import uuid4 as gen_uuid
from io import StringIO
import asyncio
from typing import ByteString, Any, Dict, Callable

import arrow
import rdflib
from rdflib import URIRef
from fastapi_utils.cbv import cbv
from fastapi import Depends, Header, HTTPException, Body, APIRouter, Query, Path
from fastapi_utils.inferring_router import InferringRouter
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from .models import TimeseriesData, ValueTypes, ValueType, IsSuccess, jwt_security_scheme, GrafanaDashboardResponse
from .models import entity_id_desc, graph_desc, relationships_desc, start_time_desc, end_time_desc
from .models import value_type_desc, timeseries_data_desc
from ..helpers import striding_windows

from ..auth.authorization import authorized, authorized_arg, O, R, W, parse_jwt_token, authenticated
from ..models import get_all_relationships, get_doc, User, GrafanaDashboard
from ..configs import configs
from ..dependencies import get_brick_db, get_ts_db, dependency_supplier, get_grafana
from ..interfaces import BaseTimeseries
from ..exceptions import AlreadyExistsError



grafana_router = InferringRouter('grafana')


@cbv(grafana_router)
class GrafanaDashboardResource:
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)
    grafana: Callable = Depends(get_grafana)

    @grafana_router.get('/',
                        status_code=200,
                        #description='Get data of an entity with in a time range.',
                        response_model=GrafanaDashboardResponse,
                        tags=['Data'],
                        )
    @authenticated
    async def get(self,
                  token: HTTPAuthorizationCredentials = jwt_security_scheme,
                  ) -> GrafanaDashboardResponse:
        payload = parse_jwt_token(token.credentials)
        user_id = payload['user_id']
        user = get_doc(User, user_id=user_id)
        gd = get_doc(GrafanaDashboard, user=user)
        return GrafanaDashboardResponse(url=gd.url)

    @grafana_router.post('/',
                     status_code=201,
                     #description='Get data of an entity with in a time range.',
                     response_model=GrafanaDashboardResponse,
                     tags=['Data'],
                     )
    @authenticated
    async def post(self,
                   token: HTTPAuthorizationCredentials = jwt_security_scheme,
                   ) -> GrafanaDashboardResponse:
        payload = parse_jwt_token(token.credentials)
        user_id = payload['user_id']
        user = get_doc(User, user_id=user_id)

        body = {
            'dashboard': {
                'uid': str(gen_uuid()),
                'title': user_id,
            }
        }
        print(body)
        resp = await self.grafana.post('/dashboards/db', json=body)
        print('------------------')
        print(resp.text)
        print(dir(resp))
        print('------------------')
        if resp.status_code == 200:
            resp = resp.json()
            print(resp)
            gd = GrafanaDashboard(user=user,
                                  uid=resp['uid'],
                                  url=resp['url']
                                  )
            gd.save()

            return GrafanaDashboardResponse(url=gd.url)
        else:
            if resp.json()['message'] == 'A dashboard with the same name in the folder already exists':
                raise AlreadyExistsError('Grafana Dashboard', user_id)
            else:
                raise HTTPException(detail='unknown error', status_code=500)

