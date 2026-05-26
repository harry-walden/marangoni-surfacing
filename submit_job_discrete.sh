#!/bin/bash
#
# Write the Marangoni-number sweep and submit a SLURM array for the discrete model.
# Edit MA_VALUES for your parameter study; example values are a small subset.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Example sweep (extend or replace for production runs)
MA_VALUES=(1 10 100 1000 10000 100000)

MA_FILE="ma_list.txt"
printf "%s\n" "${MA_VALUES[@]}" > "$MA_FILE"

NUM_VALUES=${#MA_VALUES[@]}
ARRAY_RANGE=$((NUM_VALUES - 1))

echo "Submitting SLURM array job with $NUM_VALUES tasks..."
sbatch --array=0-"$ARRAY_RANGE" run_job_discrete.sh
