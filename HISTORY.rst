Release History
---------------

2.1.0 (2017-03-06)
+++++++++++++++++++

**bugfixes**
- empty body and queryStringParameters are tolerated

**features**
- query parameters arrays are now supported
- array items are tried casted to numbers, defaulted to strings (see last README example)
- more tests


2.0.0 (2017-03-04)
+++++++++++++++++++

**This is not a backwards compatible change.**

**features**
- now json is divided into ["json"]["body"] for post body and ["json"]["query"] for json loaded query params
- jsonschema validation gets whole ["json"] object so remember to change your schemas/code!!!



1.0.1 (2017-02-24)
+++++++++++++++++++

**This is not a backwards compatible change.**

First OSS release

**features**
- dispatching handler for individual HTTP methods
- (optional) jsonschema validation for endpoints
- automatic wrapping of responses
