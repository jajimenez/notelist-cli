# Notelist CLI
Notelist CLI is a command line interface for the Notelist API written in
Python.

#### Project information:
- Version: 0.1.0
- Required Notelist API version: 0.7.0
- Author: Jose A. Jimenez (jajimenezcarm@gmail.com)
- License: MIT License
- Repository: https://github.com/jajimenez/notelist-cli

## How to install

You can download and install Notelist CLI from the **PyPI** repository with
**PIP**:

```bash
pip install notelist
```

## How to build

To generate the **built package** and the **source archive**, run the following commands (the *wheel* Python package is required for generating the built
package):

```bash
python setup.py bdist_wheel sdist
```

## How to use

Once Notelist CLI is installed, run the `notelist-cli` or `notelist-cli --help` 
command to see the help information:

```bash
notelist-cli
```

First, set the Notelist API URL to connect to. For example:

```bash
notelist-cli config --apiurl http://localhost:5000
```

Then, log in with your username and password of the Notelist API (the username
and the password will be prompted):

```bash
notelist-cli auth login
```

Now, you can run any of the CLI commands:

* `notelist-cli admin`
* `notelist-cli auth`
* `notelist-cli config`
* `notelist-cli note`
* `notelist-cli notebook`
* `notelist-cli search`
* `notelist-cli user`

To see the help information of any specific command, run the command followed
by the `--help` option. For example:

```bash
notelist-cli notebook --help
```

To log out, run the following command:

```bash
notelist-cli auth logout
```
