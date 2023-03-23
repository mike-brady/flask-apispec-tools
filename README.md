
A set of tools to aid in adding [APISpec](https://apispec.readthedocs.io/en/latest/) to [Flask](https://palletsprojects.com/p/flask) projects.


## Installation

```
pip install flask-apispec-tools
```

## Configuration
flask-apispec-tools requires the following inside the Flask app config.
```
[FLASK_APISPEC_TOOLS]
version =
title =
description =
docs_dir =
docs_type =
```
|             |                                                                           |
|-------------|---------------------------------------------------------------------------|
| version     | The version of your api.                                                  |
| title       | The name of your api.                                                     |
| description | A description of your api.                                                |
| docs_dir    | The directory where api docs are to be stored.                            |
| docs_type   | The format you want your docs created as. Can be either "json" or "yaml". |

### Setting Config Values
There are multiple ways to add the config items to the Flask app. See [Flask Configuration Handling](https://flask.palletsprojects.com/en/2.2.x/config/). While it is recommended to use separate config files or environment variables, flask-apispec-tools allows you to pass configuration values to the `init()` function. See [Configuring flask-apispec-tools with init()](#configuring-flask-apispec-tools-with-init).

### Referencing Other Config Options
Config values can be references to other config options using the format `${section:option}`.
```
[FLASK_APISPEC_TOOLS]
version = ${METADATA:version}
title = ${METADATA:title}
description = ${METADATA:description}
docs_dir = myproj/static/docs
docs_type = json
```
## Initialization
```flask_apispec_tools.init(app)```

This registers the cli command `generate-api-docs` with Flask and adds 3 endpoints ( `/docs`, `/docs/json` or `/docs/yaml`, `/version`) to the app.

### Customizing Built-in Endpoints
Adding these endpoints can be disabled or their paths can be changed by passing additional arguments to `init()`.

The example below sets the paths for the docs and docs_json endpoints and disables the version endpoint.

```
flask_apispec_tools.init(
    app,
    docs_endpoint='/api/docs',
    docs_json_endpoint='/api/docs/json',
    version_endpoint=False
)
```
### APISpec Plugins
A list of apispec plugins can be passed to `init()` and they will be given to the APISpec object. See [APISpec Using Plugins](https://apispec.readthedocs.io/en/latest/using_plugins.html). You do not need to give `init()` the FlaskPlugin.
```
flask_apispec_tools.init(
    app,
    plugins=[MarshmallowPlugin(), MyCustomPlugin()]
)
```
### Configuring flask-apispec-tools with init()
flask-apispec-tools can be configured by passing a dictionary of config values to `init()`. This will override any existing configuration values.
```
flask_apispec_tools.init(
    app,
    config_values={
        'docs_dir': '/docs',
        'docs_type': 'json'
    }
)
```
## Generating API Docs
`flask generate-api-docs`

### Options
`-a, --all Include enpoints marked 'Exclude From Spec'.`

## Excluding Endpoints
Endpoints can be excluded from docs by adding `Exclude From Spec` at the top of the docstring. This exclusion can be ignored using `-a` or `--all` with `flask generate-api-docs`.
```
class MyEndpoint(MethodView):
    """Exclude From Spec"""

    def get(self):
        ...
```

## Built-in Endpoints
| endpoint   | description                   | query parameters                                          |
|------------|-------------------------------|-----------------------------------------------------------|
| /docs      | Display docs with Swagger UI. | version (optional): Which version of the API docs to get. |
| /docs/json | Get docs as JSON.             | version (optional): Which version of the API docs to get. |
| /docs/yaml | Get docs as YAML.             | version (optional): Which version of the API docs to get. |
| /version   | Get the API version.          |                                                           |

## Additional Functions
These functions are used internally, but you may find them useful as well.  
### `flask_apispec_tools.tools`
#### config_values(option: str, \*, config: Config = None) -> str | None:
```
Get the value of an option from the config.  

Args:  
	option: The option to get the value for. 
	config: Optional. Default: flask.current_app.config.  
Returns:  
	str: The config value. 
	None: The option was not found.
```

#### get_docs_filename(version: str = None, \*, config: Config = None) -> str:
```
Get the name of a docs file for a specific version.  

Args:  
	version: Optional. Default: The version set in the config. 
	config: Optional. Default: flask.current_app.config.  
Returns:  
	 The docs filename.
```

#### get_docs_filepath(version: str = None, \*, config: Config = None) -> str:
```  
Get the filepath of a docs file for a specific version.  
  
Args:  
	version: Optional. Default: The version set in the config. 
	config: Optional. Default: flask.current_app.config.  
Returns:  
	The docs filepath.
 ```
