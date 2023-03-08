## Release History

### 1.0.1 (2017-02-24)

**This is not a backwards compatible change.**

First OSS release

**features** 

- dispatching handler for individual HTTP methods - (optional) jsonschema validation for endpoints
- automatic wrapping of responses

### 2.0.0 (2017-03-04)

**This is not a backwards compatible change.**

**features** 

- now json is divided into \[\"json\"\]\[\"body\"\] for post body and \[\"json\"\]\[\"query\"\] for json loaded query params 
- jsonschema validation gets whole \[\"json\"\] object so remember to change your schemas/code!!!

### 2.1.0 (2017-03-06)

**bugfixes** 

- empty body and queryStringParameters are tolerated

**features** 

- query parameters arrays are now supported 
- array items are tried casted to numbers, defaulted to strings (see last README example) 
- more tests

### 2.2.1 (2017-10-03)

**features** 

- builds and deploys automatically using travis to pypi and github releases

### 2.2.6 (2017-12-13)

**features** 

- An error handler can now be passed when creating a handler. Any unhandled error will be re-raise when None is passed

### 4.0.0 (2018-04-06)

**features** 

- added Werkzeug path parameters

### 4.1.0 (2018-04-12)

**features** 

- added support for custom domains

### 5.0.0 (2018-06-07)

**This is not a backwards compatible change.**

**features** 

- removed support for python 3.3

### 5.0.1 (2018-06-13)

**features** 

- Fixed issue with custom domains and path variables

### 5.1.0 (2018-11-01)

**features** 

- Return None only if the value of the variable is None. This will allow to return empty strings.

### 5.2.0 (2019-03-06)

**features** 

- you can override the json encoder with your own

### 5.3.0 (2019-03-06)

**features** 

- Add support for Application Load Balancer

### 5.4.0 (2019-03-06)

**features** 

- Add application\_load\_balancer arg to create\_lambda\_handler to create lambda\_handlers specifically for Application Load Balancer

### 5.4.0 (2019-08-17)

**features** 

- Support of resource path {placeholders} in the middle

### 5.6.0 (2020-01-27)

**features** 

- Add functools.wraps 
- use black for lint

### 6.0.0 (2020-01-27)

**features** 

**This is not a backwards compatible change.**

- drop python 3.4 and 2.7 support

### 6.0.1 (2020-01-28)

**features** 

- remember HISTORY.md in manifest file

### 7.0.0 (2020-02-12)

**This is not a backwards compatible change.**

- don't json.dumps the body if it's already a str (pr #58)

### 8.0.0 (2020-02-14)

**This is not a backwards compatible change.**

- minimally process standard lambda (dict) responses (pr #59)

### 9.0.0 (2020-04-14)

**This is not a backwards compatible change.**

- add support for scopes #60
- drop support for python 3.5
- drop tox for testing
- use poetry for packaging

### 9.1.0 (2020-04-16)

- Fixed issue with empty dict being returned as is instead of being converted to string #63
- Fixed issue with schema validation for schemas with oneOf element #62

### 9.2.0 (2020-05-11)

- Document exception handling behavior in README #66
- Supporting multiValueHeaders #65
- Reorganize documentation


### 10.0.1 (2020-09-11)

**This is not a backwards compatible change.**

- Use query `schema.properties.query.properties.*` as type lookup for unpacking of query params to right types (including lists/singulars of strings/ints/floats/booleans)
- **not supporting json objects as values in query-params anymore** _use json body instead_ 

### 10.1.0 (2021-01-16)

- add support for base64 encoded body
- fix errrors since readme tests have not been run for a while
- fix int casting (now casts to float first and then int)


### 11.0.0 (2021-04-08)

**This is not a backwards compatible change.**

- on bad json body and load_json==True return 400 instead of 500

### 11.1.0 (2021-08-03)

- catch werkzeug exceptions

### 12.0.0 (2021-09-22)

**This is not a backwards compatible change.**

- add decorators for pre- and post-request handling
- add cors functionality
- add type hints



### 12.0.1 (2022-09-12)

THIS IS THE LAST RELEASE BY CURRENT MAINTAINER, IF YOU WANNA TAKE OVER: MAIL johannes.valbjorn+lambdarest @ the free email service  that google provides

- update dependencies
- use werkzeug.exceptions.NotFound




### 13.0.0 (2023-04-08)

re publish project, new energy

