Release History
---------------

2.0.0 (2017-03-4)
+++++++++++++++++++

**This is not a backwards compatible change.**

First OSS release

features:
- now json is divided into ["json"]["body"] for post body and ["json"]["query"] for json loaded query params
- jsonschema validation gets whole ["json"] object so remember to change your schemas/code!!!



1.0.1 (2017-02-24)
+++++++++++++++++++

**This is not a backwards compatible change.**

First OSS release

features:
- dispatching handler for individual HTTP methods
- (optional) jsonschema validation for endpoints
- automatic wrapping of responses
