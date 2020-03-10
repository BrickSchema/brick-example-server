Reference Brick Server
================================

Brick Server is an implementation of Brick API on top of a timeseries database (TimescaleDB) and a Brick database (Virtuoso). Data in buildings are represented as streams of timestamped-values generated from [Point](http://brickschema.org/schema/1.0.3/Brick#Point)s which may record a physical property or actuate a device. Metadata helps to find the right data streams that an application needs. Data and metadata are in different formats, and thus we have to store them in different databases. Brick Server provides a single API endpoint to access those two different data sources.

Brick Server is
- a fully functional, minimal Bulding Operating System (BOS),
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
        - You can further configure `brickserver` module for optimization. The current image uses `gunicorn` as a web server and `uvicorn` as an ASGI. Please refer to [the image's doc](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker) for more information.

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


### Ansible (Unmaintained)

Ansible is a piece of provisioning software that simplifies the process of installing software on local or remote machines. Ansible is launched from a **control machine** (usually your laptop or personal computer) and targets a set of **hosts**, which consists of a list of IP addresses (this can contain your local machine if you use `localhost`). If you are unfamiliar with Ansible, we recommend reading the [Getting Started Documentation](https://docs.ansible.com/ansible/2.7/user_guide/intro_getting_started.html#getting-started)

1. Instal dependencies:
    - Make sure Python >=3.6 is installed on the deployment server.
    - Enable Filesystem ACL  in the host. ([for Ubuntu](https://help.ubuntu.com/community/FilePermissionsACLs<Paste>))
2. Install ansible on your local machine
    - follow instructions for the [control machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-the-control-machine)
3. Edit your `/etc/ansible/hosts` file to include the remote host and any SSH key you need; for example

    ```ini
    [ec2test]
    52.91.98.98 ansible_ssh_private_key_file=/path/to/my/ssh/key
    ```
    Ansible documentation for this step can be found [here](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
4. Edit the `ansible/brick-server-playbook.yml` file:

    ```yaml
    - hosts:
      - ec2test
      remote_user: ubuntu
      # ...
    ```

    Edit the remote user name and the hosts designator appropriately. Note that the `ec2test` here is
    the same as in the `/etc/ansible/hosts` file.
5. In the host machine, create a Linux user such as `prod` and assign sudo access to it. The user also should be able to execute sudo without password. ([example](https://www.cyberciti.biz/faq/linux-unix-running-sudo-command-without-a-password/))
6. Change `remote_user` inside `ansible-playbook brick-server-playbook.yml` to be matched to the one created in 5. (e.g., `prod`)
7. Run `ansible-playbook brick-server-playbook.yml` from the `ansible` directory.

## Getting Started
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
