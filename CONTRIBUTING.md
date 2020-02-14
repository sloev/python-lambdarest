# Wanna contribute?

Welcome to our happy country of Lambdarest!

Lambdarest is heavily created in collaboration and we value all contributions.

## Are you having issues?
Create issues or pull requests, no real guidelines given here.

If you feel like it, take a look around and see if the issue was posted before, but if not, thats ok too!

## Have you made a PR?

A maintainer will review and take care of version bumping and release etc.

I am sure we can all work together and get your work released!

## Development how-to

There is two ways of running the lint+tests both of them require the install of the dependencies mentioned in [`dev_requirements.txt`](dev_requirements.txt)


### 1. Run for current python version

```
$ make setup test
```

which 

* Installs test and lint dependencies
* runs **black** and **pytest**

for the current python version.

### 2. Run for all supported versions

This uses **tox** and pyenv to run tests for all versions.

Start by [installing pyenv](https://github.com/pyenv/pyenv#installation) and then run the following commands to install supported python versions and run **pytest** and **black** using **tox**

```
$ make setup-all tox
```


### Linting

Be sure to see if linting is correct before commiting. The following make target fixes linting issues and makes you aware of errors

```
$ make fix-lint
```