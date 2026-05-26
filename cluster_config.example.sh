# Copy this file to cluster_config.sh and edit for your HPC environment.
# cluster_config.sh is listed in .gitignore so local paths are not committed.

# SLURM partition / QoS (used by submit scripts via sbatch --export)
export SLURM_PARTITION="${SLURM_PARTITION:-normal}"

# Memory per array task
export SLURM_MEM="${SLURM_MEM:-32G}"

# Conda / Python environment with Dedalus 3 installed
export CONDA_SH="${CONDA_SH:-/path/to/miniforge/etc/profile.d/conda.sh}"
export CONDA_ENV="${CONDA_ENV:-dedalus3}"

# Optional: module loads before activating conda (uncomment and edit)
# module load miniforge
