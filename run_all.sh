#!/bin/bash

# Use the below command if getting any error!
# sed -i 's/\r$//' run_all.sh

set -e

echo "=== STARTING FULL PROJECT WORKFLOW ==="
echo ""

# Cleaning Old Results
echo "Cleaning Old Results"
rm -rf m5out_cores/
rm -rf m5out_ca/
rm -rf m5out_cs/
rm -rf output_plots/


# Running All Simulation Experiments
echo "=== Running Core Scaling Experiment ==="
bash ./core_scaling.sh &

echo "=== Running Associativity Experiment ==="
bash ./cache_associativity_scaling.sh &

echo "=== Running Cache Size Experiment ==="
bash ./cache_size_scaling.sh &

echo "=== Waiting For All Simulations To Complete ==="
wait

echo "=== All Simulations Complete! ==="
echo ""

# Generating Plots
echo "Running Plotting Script"
python3 final_plot.py

echo ""
echo "------------------------------------------------"
echo "=== WORKFLOW COMPLETE ==="
echo "Find All Plots In 'output_plots' Directory"
