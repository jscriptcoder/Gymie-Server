#!/bin/bash

echo "Publishing package..."
python -m twine upload --repository pypi dist/*
