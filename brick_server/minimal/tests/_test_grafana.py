from pdb import set_trace as bp

import requests

apikey = "eyJrIjoiRzRmMUlqT0c2bnQ3UTZ4TnBTR0oyMjlNQnN1Smk5WjYiLCJuIjoiYnJpY2tzZXJ2ZXItbWFuYWdlbWVudCIsImlkIjoxfQ=="
headers = {"Authorization": "Bearer " + apikey}

uid = "abcdefgh"

baseurl = "http://localhost:3000/api/dashboards/db"
body = {
    "dashboard": {
        # 'id': None,
        "uid": uid,
        "title": "User YYY",
    },
    # 'overwrite': True,
}
# {
#     "id": 4,
#     "slug": "user-yyy",
#     "status": "success",
#     "uid": "abcdefgh",
#     "url": "/d/abcdefgh/user-yyy",
#     "version": 1,
# }
resp = requests.post(baseurl, headers=headers, json=body)
print(resp.json())
bp()
