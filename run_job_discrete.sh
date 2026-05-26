#!/bin/bash -l
#
# SLURM array worker for the discrete (finite mass) model.
# Configure cluster settings in cluster_config.sh (see cluster_config.example.sh).

#SBATCH -p PARTITION_NAME
#SBATCH --mem=32G
#SBATCH -o slurm-%A_%a.out
#SBATCH -e slurm-%A_%a.err

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

if [[ -f cluster_config.sh ]]; then
  # shellcheck source=/dev/null
  source cluster_config.sh
fi

if [[ -n "${CONDA_SH:-}" && -f "${CONDA_SH}" ]]; then
  # shellcheck source=/dev/null
  source "${CONDA_SH}"
  conda activate "${CONDA_ENV:-dedalus3}"
fi

MA_FILE="ma_list.txt"
MA_VALUES=($(<"$MA_FILE"))
VALUE=${MA_VALUES[$SLURM_ARRAY_TASK_ID]}

INDEX_RECORD="index_record.txt"
PYTHON_SCRIPT="simulate_discrete.py"
touch "$INDEX_RECORD"

declare -A EXISTING_VALUES
while read -r INDEX VAL; do
  EXISTING_VALUES["$VAL"]="$INDEX"
done < "$INDEX_RECORD"

if [[ -n "${EXISTING_VALUES[$VALUE]:-}" ]]; then
  echo "Skipping value $VALUE (already simulated)"
  exit 0
fi

LOCKFILE=".index_lock"
exec 9>"$LOCKFILE"
flock 9

if [[ -s "$INDEX_RECORD" ]]; then
  LAST_INDEX=$(awk 'END{print $1}' "$INDEX_RECORD")
else
  LAST_INDEX=0
fi
INDEX=$((LAST_INDEX + 1))
echo "$INDEX $VALUE" >> "$INDEX_RECORD"

flock -u 9

echo "Running simulation for Ma=$VALUE (index $INDEX)"
python "$PYTHON_SCRIPT" "$VALUE" "$INDEX"
