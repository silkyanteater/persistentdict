#!/bin/bash

export DBFILE=test.db

export PYTHONPATH=$PYTHONPATH:..

poetry run pytest tests
