#!/bin/bash

if [[ -z "$1" ]]; then
    echo "Part is missing: major|minor|patch"
    exit 0
fi

echo "Bumping version and tagging..."
bump2version $1

echo "Pushing tag..."
git push --tags

echo "Building package..."
rm -rf dist
python setup.py sdist bdist_wheel
