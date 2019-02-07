=======
History
=======

0.1.0 (2016-11-09)
------------------

* First release on gemfury

0.1.1 (2016-11-09)
------------------

* change names

0.1.2 (2016-11-09)
------------------

* fix issue with  401-retry

0.1.3 (2016-11-10)
------------------

* add dependencies to setup.py

0.1.4 (2016-11-11)
------------------

* cli tool

0.1.5 (2016-11-11)
------------------

* fix apikey url query param error

0.1.6 (2016-11-11)
------------------

* introduce different token_issuer_host thatn api_host

0.1.7 (2016-12-06)
------------------

* Introduce context_getter on session object, defaulted to holding CorrelationId=random_uuid

1.0.0 (2017-02-01)
------------------

* first release as oss, major refactoring of inner machinery (session objects, retry policies, cli, tests etc)

1.1.0 (2017-06-12)
------------------

* fixed logging so it does not use root logger. according to best practices mentioned in http://pythonsweetness.tumblr.com/post/67394619015/use-of-logging-package-from-within-a-library
* removed dependency on httpretty since it is not supporting py3

2.0.0 (2017-09-29)
------------------

* DEPRECATED: create_session is getting deprecated, use trustpilot.client.default_session.setup instead
* now able to query public endpoints without being authenticated

2.1.0 (2017-10-05)
------------------

* fixed issue in cli.post & cli.put where 'content_type' should be 'content-type'

3.0.0 (2018-01-18)
------------------

DELETED DO NOT USE!!

* add async-client


3.0.1 (2018-01-18)
------------------

* removed prints
* made async_client retry on unauthorized

4.0.0 (2018-06-06)
------------------

* drop support for Python 3.3


4.0.1 (2018-06-06)
------------------

* Switch to non-deprecated session object for utility method calls

4.0.2 (2018-10-30)
------------------

* Upgrade requests to 2.20.0

5.0.0 (2019-01-04)
------------------

* Update to authentication methods

5.0.1 (2019-02-04)
------------------

* Fix documentation formatting

6.0.0 (2019-02-06)
------------------

* reorganize code
* add user-agent header
* get access_token with async call in async_client
