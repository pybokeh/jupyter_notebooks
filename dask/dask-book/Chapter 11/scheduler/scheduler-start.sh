#!/bin/bash

# Write the hostname of the scheduler to the EFS system
hostname=$(hostname)
echo "Setting scheduler hostname to $hostname"
hostname > /data/.scheduler

# Start the scheduler
echo "Starting Dask Scheduler..."
dask-scheduler
