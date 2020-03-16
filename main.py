import os
os.environ["BRICK_CONFIGFILE"] = './configs/configs.json'
from brick_server import app

from brick_server.auth.authorization import *
from brick_server.dependencies import update_dependency_supplier
#update_dependency_supplier('auth_logic', check_admin2)
