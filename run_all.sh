#!/bin/bash

set -e

echo "=== STARTING FULL PROJECT WORKFLOW ==="
echo ""

# Cleaning Old Results
echo "Cleaning Old Results"
rm -rf m5out/
rm -rf output_plots/

# Running All Simulation Experiments
echo "=== Running Core Scaling Experiment ==="
bash ./run_core_scaling.sh

echo "=== Running Associativity Experiment ==="
bash ./run_assoc_scaling.sh

echo "=== Running Cache Size Experiment ==="
bash ./run_size_scaling.sh

echo "=== All Simulations Complete! ==="
echo ""

# Generating Plots
echo "Running Plotting Script"
python3 final_plot.py

echo ""
echo "------------------------------------------------"
echo "=== WORKFLOW COMPLETE ==="
echo "Find All Plots In 'output_plots' Directory"
