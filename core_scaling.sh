#!/bin/bash

echo "--- Starting Core Scaling Experiment ---"

# Paths
GEM5_ROOT=$(dirname $(dirname $(pwd)))
GEM5_BIN="$GEM5_ROOT/build/X86/gem5.opt"

export PYTHONPATH=$PYTHONPATH:$(pwd)/..

OUTPUT_DIR="m5out_cores"
PROJECT_DIR=$(pwd)
SIM_SCRIPT="$PROJECT_DIR/se.py"
WORKLOAD="$PROJECT_DIR/sort_algorithm_binary"

# Parameters
CPU_TYPE="O3CPU"
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

  $GEM5_BIN --outdir=$OUTPUT_DIR $SIM_SCRIPT \
    --cpu-type=$CPU_TYPE \
    -c $WORKLOAD \
    --num-cpus=$cpus \
    --caches \
    --l2cache \
    --l1d_size=$L1D_SIZE \
    --l1i_size=$L1I_SIZE \
    --l2_size=$L2_SIZE

  cp ./m5out_cores/stats.txt ./m5out_cores/stats_cores_${cpus}.txt
  
  mkdir -p ./m5out_cores/stats_cores_${cpus}
  
  for file in ./m5out_cores/*; do
    if [[ -f "$file" && $(basename "$file") != stats_* ]]; then
      mv "$file" "./m5out_cores/stats_cores_${cpus}/"
    fi
  done

  echo "--- Finished: $cpus cores. Stats saved to m5out_cores/stats_cores_${cpus}.txt ---"
done

echo "--- All Core Scaling Simulations Complete ---"
