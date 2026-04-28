#!/bin/bash

set -e

python -m pip install --upgrade pip
pip install -r requirements.txt

TEST_PATH="tests/regressions_tests/apps/$APP_NAME/test_scenarios.py"

if [ -f "$TEST_PATH" ]; then
  pytest "$TEST_PATH"
else
  echo "Test file $TEST_PATH not found. Skipping tests for $APP_NAME."
  exit 0
fi
