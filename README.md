# marangoni-surfacing

Code accompanying the paper *Marangoni Surfacing*: Dedalus 3 simulations of subsurface Marangoni propulsion and Jupyter notebooks for post-processing.

## Layout

| File | Role |
|------|------|
| `simulate_discrete.py` | Finite initial solute mass (discrete source) |
| `simulate_continuous.py` | Continuous solute injection at the body |
| `submit_job_discrete.sh` / `submit_job_continuous.sh` | Build `ma_list.txt` and submit a SLURM array |
| `run_job_discrete.sh` / `run_job_continuous.sh` | Array task: assign run index, call the matching simulator |
| `MS_DF_batch_proccessing.ipynb` | Post-process discrete runs |
| `MS_DC_batch_proccessing.ipynb` | Post-process continuous runs |
| `MS_comparative.ipynb` | Compare discrete vs continuous results |

Each simulation writes Dedalus snapshot directories (`snapshots{N}/` or `snapshots_cts{N}/`) and appends to `index_record.txt` (columns: `index Ma`).

## Requirements

- [Dedalus 3](https://dedalus-project.org/) (Python 3.10+)
- `numpy`, `h5py`, `matplotlib` for notebooks
- SLURM (optional) for cluster batch submission

## Cluster setup

1. Copy `cluster_config.example.sh` to `cluster_config.sh` and set your conda path, environment name, and (if needed) module loads.
2. In `run_job_discrete.sh` and `run_job_continuous.sh`, replace `#SBATCH -p PARTITION_NAME` with your partition and adjust `#SBATCH --mem` if needed.
3. Edit `MA_VALUES` in the `submit_job_*.sh` scripts for your parameter sweep.
4. From the repository directory (or a dedicated run directory):

   ```bash
   bash submit_job_discrete.sh
   # or
   bash submit_job_continuous.sh
   ```

Runs can also be executed locally:

```bash
python simulate_discrete.py 1000 1
```

## Post-processing

Place `index_record.txt` and snapshot folders in the working directory of the notebook (or set `RESULTS_DIR` at the top of each notebook). Open the relevant notebook and run all cells.

For `MS_comparative.ipynb`, discrete and continuous outputs can live in separate directories; set `RESULTS_DIR_FINITE` and `RESULTS_DIR_CONTINUOUS` in the first code cell.

## License

MIT License — see [LICENSE](LICENSE).
