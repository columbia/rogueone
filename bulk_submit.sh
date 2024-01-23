#!/bin/bash

# To be run from the Moto login node in order to create
# nodes that start up and start accepting jobs
# By default starts 1 node with a 30 minute timeout

AMOUNT=${1:-1}

for ((i=1; i<=AMOUNT; i++)); do

	current_date=$(date +"%Y-%m-%d-%H")
	random_string=$(< /dev/urandom tr -dc A-Za-z0-9 | head -c8)
	folder="nodes/${current_date}_${random_string}"
	mkdir $folder
	sbatch --output="$folder/slurm-%j.out" --error="$folder/slurm-%j.err" script.sh "$folder"
done
