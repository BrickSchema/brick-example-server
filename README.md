Reference Brick Server
================================

Brick Server is an implementation of Brick API on top of a timeseries database (TimescaleDB) and a Brick database (Virtuoso). Data in buildings are represented as streams of timestamped-values generated from [Point](http://brickschema.org/schema/1.0.3/Brick#Point)s which may record a physical property or actuate a device. Metadata helps to find the right data streams that an application needs. Data and metadata are in different formats, and thus we have to store them in different databases. Brick Server provides a single API endpoint to access those two different data sources.

Brick Server is
- a minimal but fully functional Bulding Operating System (BOS),
- an interface for Brick applications,
- an emulator of a building for Brick applications development,
- a demonstration of general methods to integrate your system with Brick, and
- a testbed for new functions in Brick.

If you want to learn more about Brick, please visit [brickschema.org](https://brickschema.org) for materials.


# Instructions

## System Requirements
- OS: Linux (tested over Ubuntu 18.04 and Debian 9.)
- Python 3.6>= is required.

## Installation

### Docker Compose (Recommended)

1. Configure `config.json`.
    1. Change `configs/configs.json.template` to `configs/configs.json`
    2. Modify the configuration in `configs/configs.json`.
        - The preset parameters are working with the default docker-compose file.
        - You can ignore `oauth_connections` and `frontend` as they currently under development.
2. Configure `docker-compose.yml`
    1. Change `docker-compose.yml.template` to `docker-compose.yml`.
    2. Modify the configuration in `docker-compose.yml`.
        - Choose if you want to run https inside the docker. You can enable HTTPS by uncommenting `ENABLE_SSL=true`. In that case, you should specify the location of cert files (`CERTFILE` and `KEYFILE`)as well as bind the files from the host machine (e.g., `/etc/letsencrypt`.).
        - You can further configure `brickserver` module for more optimization. The current image uses `gunicorn` as a web server and `uvicorn` as an ASGI. Please refer to [the image's doc](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker) for more information.

3. Run docker-compose
    1. Execute `docker-compose up`.

4. Get an App Token.
    1. Execute `docker exec -t brickserver /app/tools/get_jwt_token`.
    2. Keep and use it as a bearer token.


### Manual Installation (Outdated, but will be updated.)

1. Install and run Virtuoso (Note: Please use only released versions in Virtuoso repository. [link](https://github.com/openlink/virtuoso-opensource/releases))
2. Install and run TimescaleDB/PostGIS/PostgreSQL. [link](https://docs.timescale.com/getting-started/installation)
5. Install pip packages by ``pip install -r requirements.txt``
6. Configure the databases and configure ``configs/configs.json``
    1. Create a database with a proper name in the db.
    2. Create a role/user of the database.
    3. Add them inside ``configs/configs.json``
7. Run ``python entry.py`` to run the server.
8. Run ``python examples/test_api.py`` in another console.
9. API Documentation would be available at https://localhost/api/v1/doc
10. Install and run the fronted based on its instruction: https://gitlab.com/jbkoh/brick-server-frontend


# Getting Started
1. API document is available at `YOUR_HOSTNAME/docs`
2. Example codes are available at `tests/remote/*.py`
3. Jupyter Notebooks will be available.

# Core Concepts
## Entities in Brick
- An entity (sensor, room, VAV, etc.) is associated with a UUID.
- An entity is an instance of at least one Brick Class. The Brick Class can be arbitrary even outside the standard though not preferred.
- An entity can have relationships with other entities.
- An entity's metadata consists of its direct relationships with other entities (or properties.)

## Timeseries Data
- The database schema of timeseries data is a long table with four columns of `uuid`, `timestamp`, `number`, and `text` where the combinations of `uuid` and `timestamp` are unique. `number` and `text` are the data types that each entity can have. Usually an entity may have only one data type for its values.
- Each row is a timestamped value.
- The `uuids` in the timeseries database are the same uuids in Brick.

## Authorization
- Currently, we only support a very primitive authorization. A user can manually generate a JWT token with the privkey used in Brick Server, which can be used as a bearer token. The token will authorize the usage of any APIs until it expires.
    - You can get it through `tools/get_jwt_token $expiration_time_in_seconds`.
- You can retrieve the public key at `/auth/jwt_pubkey`.


# Tests
1. Add a JWT token into `pytest.ini`.
2. Execute `pytest -c pytest.ini tests/remote`.

# Tutorials
## BrickBACnet as a BACnet connector
1. Prepare an app token.
2. Check the instruction at TODO

# References
- Metadata Models and Methods for Smart Buildings (Dissertation, UCSD, 2020)
- Who, What, and When (BuildSys 2019)
- Brick+ (BuildSys 2019)
- MortarData (BuildSys 2018)
- Brick (EnergyPlus 2018)
- Brick (BuildSys 2016)
