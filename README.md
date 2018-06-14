Reference (Minimal) Brick Server
================================

Brick Server is an implementation of Brick API on top of a timeseries database (TimescaleDB) and a metadata database (Virtuoso). Data in buildings are represented as streams of timestamped-values generated from [Point](http://brickschema.org/schema/1.0.3/Brick#Point)s which may record a physical property or actuate a device. Metadata helps to find the right data streams that an application needs. Data and metadata are in different formats, and thus we have to store them in different databases. Brick Server provides a single API endpoint to access those two different data.

1. It would help you understand the general method of integrating your system with Brick.
2. It is an emulator of a building for Brick applications development.
3. It is a testbed for new functions in Brick.

If you want to learn more about Brick, please visit [brickschema.org](https://brickschema.org) for materials.

### Design Goals
- Functional correctness
- Usable performance

### What we HAVE
1. Implementation of Brick API endpoint.
2. Example backend databases.
3. Interface to different databases.

### What we WILL have
1. We will add a general app authorization mechanism with Brick.
2. We will gradually add support for other databases.
3. We will integrate geometry of buildings.

### What we DON'T have
1. We do not have exact data of full buildings. For the access to example dataset, please visit XXX, YYY.


## Getting Started

1. Install Virtuoso
2. Install PostgreSQL
3. Install TimescaleDB
4. Install pip packages by ``pip install -r requirements.txt``
5. Configure the databases and configure ``configs/configs.json``.
6. Run ``./run_app``


# References
- Brick (BuildSys 2016)
- Brick (EnergyPlus 2018)
