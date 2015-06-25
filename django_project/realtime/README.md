# InaSAFE Realtime Django REST API

[InaSAFE](http://insafe.org) is a contingency planning and preparedness tool
for disasters. This Realtime Django app provides REST API using Django REST 
Framework package. Now, the following Django model is supported:  

* Earthquake

**Please note that this project is in the early phase of its development.**

# License

Data: [Open Database License](http://opendatacommons.org/licenses/odbl/)
Code: [Free BSD License](http://www.freebsd.org/copyright/freebsd-license.html)

Out intention is to foster wide spread usage of the data and the code that we
provide. Please use this code and data in the interests of humanity and not for
nefarious purposes.

# Usage instructions

## Setup production or development environment

Please refer to the root project README.md file.

## API Endpoint

The API root is located at:

```
/realtime/api/v1/
```

So, if you are using local development environment, the API is located at: 

```
http://localhost:8000/realtime/api/v1/
```

From now on, the endpoint being explained are using relative URL from the 
Root API Endpoint.

The object endpoint that is currently being supported:

* Earthquake (via /earthquake )
* Earthquake Report (via /earthquake-report )

You can use browsable API via the object endpoint. For example: 

```
http://localhost:8000/realtime/api/v1/earthquake/
```

That URL will show web interface for earthquake model list. You can also 
post the model data using provided HTML form. If there was a URL link in 
the JSON results, it can also be clicked to follow the URL. 

## Common Features

### Return format

The result can be returned in different format. We currently support API 
and JSON format. To choose the format, simply append format query in the 
URL like this:

```
/earthquake/?format=json
```

The example will return earthquake list in JSON format.

### Result Filtering

Some endpoint can be filtered with a certain filter query. To apply 
filter, simply append filter query in the URL like this:

```
/earthquake/?depth_min=1&depth_max=10
```

The example will return earthquake list with depth d : **1 <= d <= 10**

### Result Pagination

Some endpoint, typically which returns a result list, supported pagination.
 To get a certain page, simply append page query in the URL:
 
```
/earthquake/?page=2
```

The example will return the second page of the results list, if any. In 
addition, the JSON result also provides **count**, **next**, and 
**previous** variable.

### HTML Form

Some endpoint support HTML Form for posting data.


# Endpoints

Right now, we supports these endpoints:

* Earthquake List
* Earthquake Detail
* Earthquake Report List
* Earthquake Report Detail

## Earthquake List

Provides GET and POST requests to retrieve and save Earthquake models.

### Filters

These are the available filters:

* depth_min
* depth_max
* magnitude_min
* magnitude_max
* location_description

## Earthquake Detail

Provides GET, PUT, and DELETE requests to retrieve, update and delete 
Earthquake models.

## Earthquake Report List

Provides GET and POST requests to retrieve and save Earthquake Report models.

### Filters

These are the available filters:

* earthquake__shake_id
* language

## Earthquake Report Detail

Provides GET, PUT, and DELETE requests to retrieve, update and delete 
Earthquake Report models.
