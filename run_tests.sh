#!/bin/bash

echo "Testing OpenAI Gym..."
python tests/test_gymie.py

echo "Testing Gym Retro..."
python tests/test_gymie_retro.py

echo "Testing Unity ML-Agents..."
python tests/test_gymie_unity.py
