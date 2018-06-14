# PyCharm Usage for Development

If you setup the project using ```make setup-ansible``` command. It will
setup PyCharm configurations. You can then open it using PyCharm Professional
Edition to easily run/debug the project.

## Services

Before you start Running the project using PyCharm, start this command
from terminal in `deployment` directory

```
make build up realtime-worker headless-worker
```

This will set up basic docker services for development.

To run the webservice, use the following configuration:

1. Run Server Remote Debug

This will run a Django Web Server to your configured port (Default 61102)

2. Dev Celery Worker Debug

This will run Celery Worker for InaSAFE Django

3. Dev Celery Worker Indicator Debug

This will run Celery Worker for InaSAFE Django for indicator/health check jobs


Run each configuration in succession, the progress and logs will show up in PyCharm Run Window.
To run the configuration in Debug Mode, click the Debug button instead.
It will allow you to place and stop at breakpoints.

## Integration Tests

There are also other Run Configuration specifically used for running complex unittests.
If you want to use this Run Configuration, make sure all basic Run Configuration
services were switched off first.

1. Run Realtime Tests

This will tests integration between InaSAFE Realtime and InaSAFE Django.
Make sure that ```make up realtime-worker``` were executed before running this.
This unittest works by using a InaSAFE Realtime docker services (true celery worker)
and an eager (emulated) celery task of InaSAFE Django.

2. Celery Worker Integration Test Mode

This run configuration is only useful for doing full ```Integration Tests```.
It will spawn InaSAFE Django Celery Worker using a test database environment.

3. Integration Tests

This will do simulated integration tests by performing hazard event delivery.
It will run scenarios for each hazard and check that all InaSAFE Django, InaSAFE Realtime, and InaSAFE Headless
were integrated properly. To Run ```Integration Tests```, you need to also run
```Celery Worker Integration Test Mode```.
Make sure you run ```make up realtime-worker headless-worker``` before doing this.

