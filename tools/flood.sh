#!/bin/bash

for a in `seq 25`; do
	curl -d "wooot$a" http://localhost:9000/ &
done
