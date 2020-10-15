#!/bin/bash

if [[ -z "$1" ]]; then
    echo "Current version is missing"
    exit 0
fi

if [[ -z "$2" ]]; then
    echo "Part is missing: major|minor|patch"
    exit 0
fi

rm -rf dist
bumpversion --current-version $1 $2 gymie/__init__.py
python setup.py sdist bdist_wheel
