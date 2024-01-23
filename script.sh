#!/bin/bash

#SBATCH -A cs
#SBATCH --job-name=rogue_one_runner
#SBATCH -c 1
#SBATCH -t 0-8:04
#SBATCH --mem-per-cpu=2gb
#SBATCH --ntasks-per-node=8

FOLDER=$1
OVERLAY_LOC="$1/overlay.img"

module load singularity
dd if=/dev/zero of=$OVERLAY_LOC bs=1M count=1000 && \
      mkfs.ext3 -F $OVERLAY_LOC
singularity run --overlay $OVERLAY_LOC ro.sif /bin/bash -c "cd /RO && celery -A tasks worker --loglevel=INFO -Ofair -n $$@%h --prefetch-multiplier=1"
