# Home Control - Auto Robot clean

Tells the robot vacuum cleaner to clean the house when nobody is there.

## Install dependencies

```
poetry install
```

## Cut a release

```
poetry run release <version>
```

## Run

For a successful run, please provide the following environment variables:

### InfluxDB-specific environment variables

```
INFLUXDB_V2_URL
INFLUXDB_V2_ORG
INFLUXDB_V2_TOKEN
```

### Application-specific environment variables:

```
ROBOT_CLEANER_INFLUX_BUCKET
```

