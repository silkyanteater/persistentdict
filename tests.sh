#!/bin/bash

export PYTHONPATH=$PYTHONPATH:../persistentdict

poetry run pytest tests
