from pdb import set_trace as bp
import json
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

from .models import TimeseriesData, ValueTypes, ValueType, IsSuccess, jwt_security_scheme, GrafanaDashboardResponse, GrafanaUpdateRequest
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
class GrafanaDashboardDetailsResource:
    auth_logic: Callable = Depends(dependency_supplier.get_auth_logic)
    grafana: Callable = Depends(get_grafana)

    @grafana_router.get('/details',
                        status_code=200,
                        description='Get dashbaord metadata for the `uid`.',
                        tags=['Data'],
                        )
    @authenticated
    async def get(self,
                  token: HTTPAuthorizationCredentials = jwt_security_scheme,
                  ):
        payload = parse_jwt_token(token.credentials)
        user_id = payload['user_id']
        user = get_doc(User, user_id=user_id)
        gd = get_doc(GrafanaDashboard, user=user)
        uid = gd.uid

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        resp = await self.grafana.get(f'/dashboards/uid/{uid}', headers=headers)
        return resp.json()

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
        return GrafanaDashboardResponse(url=gd.url,
                                        grafana_id=gd.grafana_id,
                                        uid=gd.uid
                                        )

    async def create_grafana_dashboard(self, user):
        body = {
            'dashboard': {
                'uid': str(gen_uuid()),
                'title': user.user_id,
            }
        }
        resp = await self.grafana.post('/dashboards/db', json=body)
        if resp.status_code == 200:
            resp = resp.json()
            gd = GrafanaDashboard(user=user,
                                  uid=str(resp['uid']),
                                  grafana_id=str(resp['id']),
                                  url=resp['url']
                                  )
            gd.save()

            return GrafanaDashboardResponse(
                url=gd.url,
                uid=gd.uid,
                grafana_id=gd.grafana_id,
            )
        else:
            if resp.json()['message'] == 'A dashboard with the same name in the folder already exists':
                raise AlreadyExistsError('Grafana Dashboard', user.user_id)
            else:
                raise HTTPException(detail='unknown error', status_code=500)

    async def update_grafana_dashboard(self, user, grafana_request):
        gd = get_doc(GrafanaDashboard, user=user)
        grafana_request['dashboard']['uid'] = gd.uid
        grafana_request['dashboard']['id'] = gd.grafana_id
        grafana_request['dashboard']['title'] = user.user_id
        grafana_request['overwrite'] = True

        resp = await self.grafana.post('/dashboards/db', json=grafana_request)
        if resp.status_code == 200 and resp.json()['status'] == 'success':
            return GrafanaDashboardResponse(
                url=gd.url,
                uid=gd.uid,
                grafana_id=gd.grafana_id,
            )
        else:
            msg = resp.json()['message']
            if msg == 'A dashboard with the same name in the folder already exists':
                raise AlreadyExistsError('Grafana Dashboard', user_id)
            else:
                raise HTTPException(detail=msg, status_code=500)


    @grafana_router.post('/',
                     status_code=200,
                         description="Create or update the Grafana Dashboard. If JSON body is not given, it creates a Dashboard and assign it to the user. If JSON body is given, the body should be same as Grafana's dashboard model as defined at `https://grafana.com/docs/grafana/latest/http_api/dashboard/` except that uid, id, and title should be empty.",
                     response_model=GrafanaDashboardResponse,
                     tags=['Data'],
                     )
    @authenticated
    async def post(self,
                   request: Request,
                   token: HTTPAuthorizationCredentials = jwt_security_scheme,
                   #grafana_model: GrafanaUpdateRequest = Body(None, description='If given, update the existing Grafana dashboard assigned to the user. Otherwise, create a new Grafana Dashboard for the user.', required=False),
                   ) -> GrafanaDashboardResponse:
        payload = parse_jwt_token(token.credentials)
        user_id = payload['user_id']
        user = get_doc(User, user_id=user_id)

        body = await request.body()
        if body:
            grafana_request = json.loads(body)
            print('===========================')
            print(grafana_request)
            print('===========================')
            resp = await self.update_grafana_dashboard(user, grafana_request)
        else:
            resp = await self.create_grafana_dashboard(user)
        return resp

