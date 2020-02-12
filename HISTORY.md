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