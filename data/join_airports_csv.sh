#!/bin/sh
# Reassemble data/airports.csv from its parts (split for upload size limits).
# Run from the repository root:  sh data/join_airports_csv.sh
cat data/airports.csv.part-* > data/airports.csv
echo "Wrote data/airports.csv"
