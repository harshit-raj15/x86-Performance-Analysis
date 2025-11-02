#!/bin/bash

echo "--- Starting Core Scaling Experiment ---"

# Paths
GEM5_ROOT=$(dirname $(dirname $(pwd)))
GEM5_BIN="$GEM5_ROOT/build/X86/gem5.opt"

export PYTHONPATH=$PYTHONPATH:$(pwd)/..

PROJECT_DIR=$(pwd)
SIM_SCRIPT="$PROJECT_DIR/se.py"
WORKLOAD="$PROJECT_DIR/sort_algorithm_binary"

# Parameters
CPU_TYPE="AtomicSimpleCPU"
L1D_SIZE="64kB"
L1I_SIZE="16kB"
L2_SIZE="256kB"

# CPUs to test
CPU_COUNTS=(2 4 8 16)

# Run Loop
for cpus in "${CPU_COUNTS[@]}"; do
  echo "-------------------------------------"
  echo "--- Running: $cpus cores ---"
  echo "-------------------------------------"

  $GEM5_BIN $SIM_SCRIPT \
    --cpu-type=$CPU_TYPE \
    -c $WORKLOAD \
    --num-cpus=$cpus \
    --caches \
    --l2cache \
    --l1d_size=$L1D_SIZE \
    --l1i_size=$L1I_SIZE \
    --l2_size=$L2_SIZE

  mv ./m5out/stats.txt ./m5out/stats_cores_${cpus}.txt

  echo "--- Finished: $cpus cores. Stats saved to m5out/stats_cores_${cpus}.txt ---"
done

echo "--- All Core Scaling Simulations Complete ---"
