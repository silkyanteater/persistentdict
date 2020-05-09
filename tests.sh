#!/bin/bash

export PYTHONPATH=$PYTHONPATH:..

poetry run pytest tests
