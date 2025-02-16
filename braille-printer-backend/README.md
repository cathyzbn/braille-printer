# braille-printer

# Installation Guide

## Prerequisites
Ensure you have `pipenv` installed. If not, install it using:
```sh
pip install --user pipenv
```

## Creating a Virtual Environment
To initialize a `pipenv` environment, run:
```sh
pipenv install
```
This will:
- Create a virtual environment (if one does not exist).
- Install dependencies listed in `Pipfile`.

### Installing Dependencies
To install dependencies:
```sh
pipenv install <package-name>
```
For example, to install `requests`:
```sh
pipenv install requests
```
To install development dependencies:
```sh
pipenv install --dev <package-name>
```

### Running the Virtual Environment Shell
To activate the virtual environment:
```sh
pipenv shell
```
To exit the shell, use:
```sh
exit
```
