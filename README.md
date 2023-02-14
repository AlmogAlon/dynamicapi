# Dynamic API Responses

This project lets you create a dynamic API responses using simple configuration files
located in `services/api/config/responses` folder.

the server listens to `GET` requests on `http://localhost:1337/api/`
evaluates its context against the configured responses and acts by their actions.

## Requirements
- python3.10
- Docker (optional)
- docker-compose version 1.29.2 (optional)

## Installation

To run the services locally:
```bash
  cd services
  ./rebuild_env.bat
```
- open IDE from the root folder of the service
- configure python interpreter to use: `granulate/services/venv/bin/python`

```bash
  cd services/api
  python main.py
```


## Response

can be configured in `api/config/responses/`<response_name>.json

| Parameter | Type            | Description                                                                                  |
|:----------|:----------------|:---------------------------------------------------------------------------------------------|
| `name`    | `String`        | **Required** the name of the response                                                        |
| `expression`   | `String`        | **Required** a string that can contain request variables from `config/request/settings.json` |
| `actions` | `List[Actions]` | **Required** the actions to perform                                                          |

## Actions

### URL Action
sends a request to the given url and returns the response
parameters:


| Parameter    | Type     | Description                                         |
|:-------------|:---------|:----------------------------------------------------|
| `type`       | `String` | **Required** the type of the action (default: `url`)|
| `url` | `String` | **Required** the url to send the request to         |
| `field`       | `String` | **Required**  the field to return from the response |
| `method`       | `String` | **Optional**  the method to use (default: `GET`)    |

### Eval Action

evaluates the given expression and returns the result


| Parameter    | Type     | Description                                  |
|:-------------|:---------|:---------------------------------------------|
| `type`       | `String` | **Required** the type of the action = `eval` |
| `expression` | `String` | **Required**  the expression to evaluate     |
