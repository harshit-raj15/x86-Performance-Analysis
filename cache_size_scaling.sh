#!/bin/bash

echo "--- Starting Cache Size Scaling Experiment ---"

# --- Paths ---
GEM5_ROOT=$(dirname $(dirname $(pwd)))
GEM5_BIN="$GEM5_ROOT/build/X86/gem5.opt"

export PYTHONPATH=$PYTHONPATH:$(pwd)/..

PROJECT_DIR=$(pwd)
SIM_SCRIPT="$PROJECT_DIR/se.py"
WORKLOAD="$PROJECT_DIR/sort_algorithm_binary"

# --- Parameters ---
CPU_TYPE="AtomicSimpleCPU"
CPU_COUNT=8
L1I_SIZE="16kB"
ASSOC=4

# --- Parameters to vary ---
L1D_SIZES=("16kB" "32kB" "64kB" "128kB")
L2_SIZES=("128kB" "256kB" "512kB" "1MB")

# --- Run Loop ---
for l1 in "${L1D_SIZES[@]}"; do
  for l2 in "${L2_SIZES[@]}"; do
    echo "-------------------------------------"
    echo "--- Running: L1D=$l1, L2=$l2 ---"
    echo "-------------------------------------"

    $GEM5_BIN $SIM_SCRIPT \
      --cpu-type=$CPU_TYPE \
      -c $WORKLOAD \
      --num-cpus=$CPU_COUNT \
      --caches \
      --l2cache \
      --l1d_size=$l1 \
      --l1i_size=$L1I_SIZE \
      --l2_size=$l2 \
      --l1d_assoc=$ASSOC \
      --l2_assoc=$ASSOC

    mv ./m5out/stats.txt ./m5out/stats_size_l1_${l1}_l2_${l2}.txt

    echo "--- Finished: L1D=$l1, L2=$l2. Stats saved to m5out/stats_l1_${l1}_l2_${l2}.txt ---"
  done
done

echo "--- All Cache Size Scaling Simulations Complete ---"
