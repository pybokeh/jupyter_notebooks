#!/bin/bash
# Get the scheduler name from EFS
scheduler=$(cat /data/.scheduler)
echo "Setting scheduler name to $scheduler"
export DASK_SCHEDULER_ADDRESS="tcp://$scheduler:8786"

# Start the notebook server
start.sh jupyter lab
