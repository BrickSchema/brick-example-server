# Brick Example Server

Brick Server is an example implementation of Brick API on top of a timeseries database (TimescaleDB) and a rdf database (Graphdb). Data in buildings are represented as streams of timestamped-values generated from [Point](http://brickschema.org/schema/1.2/Brick#Point)s which may record a physical property or actuate a device. Metadata helps to find the right data streams that an application needs. Data and metadata are in different formats, and thus we have to store them in different databases. Brick Server provides a single API endpoint to access those two different data sources.

Brick Example Server is
- a minimal but fully functional "Building Operating System" (BOS),
- an interface for Brick applications,
- an emulator of a building for Brick applications development,
- a demonstration of general methods to integrate your system with Brick, and
- a testbed for new functions in Brick.

If you want to learn more about Brick, please visit [brickschema.org](https://brickschema.org) for materials.

*Note: a recent update has drastically changed the entire codebase. The dependency management, the containerization, the rdf database and so on are all updated. Please make sure to check out the lastest version.*


# Getting Started

## System Requirements
- OS: Linux (tested over Ubuntu 18.04 and Debian 9.)
- Python 3.6>= is required.

## Installation

### Docker Compose (Recommended)

1. Build the docker image

    `DOCKER_BUILDKIT=1 docker build . -t brick_server:minimal`
2. (Optional) Configure your `docker-compose.yml` accordingly if necessary. The recommended way is to create sub configuration files for different use case e.g. `docker-compose-deployment.yml` and run

    `docker-compose -f docker-compose.yml -f docker-compose-deploy.yml up -d`
3. Run docker-compose

    `docker-compose -f docker-compose.yml up -d`



### Manual Installation
No longer supported.


## Test and Play!
After docker-compose is executed, you can run pytest to test the functionality:
1. Install local environment: `poetry install`. Or if you prefer, you can use the docker container which hosts brick-server which already has been started by `docker exec -it brick-server /bin/bash`
2. Either in your local env or docker, install the test environment: `poetry install -E test`
3. Run `pytest` (first time running may have a couple of failures with regards to entities and sparql if your machine is relatively slow, run the test again should resolve the issue).

The test code at `tests/*.py` could be referred to as example codes. You can also play with the APIs at `<HOSTNAME>/docs` e.g. `http://localhost:9000/docs`

# Background Concepts
## Entities in Brick
- An entity (sensor, room, VAV, etc.) is represented by its UUID under the [UUID namespace](https://tools.ietf.org/html/rfc4122).
    - E.g.,
- An entity is an instance of at least one Brick Class. The Brick Class can be arbitrary even outside the standard though not preferred.
- An entity can have relationships with other entities.
- An entity's metadata consists of its direct relationships with other entities (or properties.)

## Timeseries Data
- The database schema of timeseries data is a long table with four columns of `uuid`, `timestamp`, `number`, and `text` where the combinations of `uuid` and `timestamp` are unique. `number` and `text` are the data types that each entity can have. Usually an entity may have only one data type for its values.
- Each row is a timestamped value.
- The `uuids` in the timeseries database are the same uuids in Brick.

## Grafana (This part is outdated)
- If you use `docker-compose.yaml.template` to run Brick Server, a Grafana will be automatically instantiated on your localhost as well. The default username/password is `bricker/brick-demo` as specified in `config/grafana/grafana.ini`.
- You need to run `docker-compose up` once to instantiate a Grafana container. In the container instance, you need to get an API token (possibly without expiration) that BrickServer can use for maintenance. The generated API token should be added to `configs/configs.json` as in the example file.

## Authorization
- In this example server, we only support a very primitive authorization. A user can manually generate a JWT token with the privkey used in Brick Server, which can be used as a bearer token. The token will authorize the usage of any APIs until it expires.
- You can get it through `python -m brick_server.minimal generate-jwt --user-id=admin` (you can use any `user_id` here).

## Create Self-Signed SSL Certificate
- `tools/gen_selfsigned_certificate`


# Tutorials
## BrickBACnet as a BACnet connector
1. Prepare an app token.
2. Check the instruction at TODO

# TODO
- Better README and code commenting
- Incorporation of front end

# References
- Metadata Models and Methods for Smart Buildings (Dissertation, UCSD, 2020)
- Who, What, and When (BuildSys 2019)
- Brick+ (BuildSys 2019)
- MortarData (BuildSys 2018)
- Brick (EnergyPlus 2018)
- Brick (BuildSys 2016)
