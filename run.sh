#!/bin/sh

BASE="`dirname $0`"

python $BASE/wowopt.py "$@" | python $BASE/ui.py
