#!/usr/bin/env bash

if [ "$1" = "test" ]
then
	# Special "test" keyword runs tests
	cd "$HOME"/myapp/app && python -m unittest discover -v
else
	# All other commands execute as normal
	exec "$@"
fi
