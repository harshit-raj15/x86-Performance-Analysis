#!/bin/bash

echo "--- Starting Cache Associativity Scaling Experiment ---"

# Paths
GEM5_ROOT=$(dirname $(dirname $(pwd)))
GEM5_BIN="$GEM5_ROOT/build/X86/gem5.opt"

export PYTHONPATH=$PYTHONPATH:$(pwd)/..

PROJECT_DIR=$(pwd)
SIM_SCRIPT="$PROJECT_DIR/se.py"
WORKLOAD="$PROJECT_DIR/sort_algorithm_binary"

# Parameters
CPU_TYPE="AtomicSimpleCPU"
CPU_COUNT=8
L1D_SIZE="64kB"
L1I_SIZE="16kB"
L2_SIZE="256kB"

# Parameters to vary
ASSOC_COUNTS=(1 2 4 8)

# Run Loop
for assoc in "${ASSOC_COUNTS[@]}"; do
  echo "-------------------------------------"
  echo "--- Running: 8 cores, L1D/L2 Assoc=$assoc ---"
  echo "-------------------------------------"

  $GEM5_BIN $SIM_SCRIPT \
    --cpu-type=$CPU_TYPE \
    -c $WORKLOAD \
    --num-cpus=$CPU_COUNT \
    --caches \
    --l2cache \
    --l1d_size=$L1D_SIZE \
    --l1i_size=$L1I_SIZE \
    --l2_size=$L2_SIZE \
    --l1d_assoc=$assoc \
    --l2_assoc=$assoc

  cp ./m5out/stats.txt ./m5out/stats_assoc_${assoc}.txt

  mkdir -p ./m5out/stats_assoc_${assoc}
  
  for file in ./m5out/*; do
    if [[ -f "$file" && $(basename "$file") != stats_* ]]; then
      mv "$file" "./m5out/stats_assoc_${assoc}/"
    fi
  done

  echo "--- Finished: Assoc=$assoc. Stats saved to m5out/stats_assoc_${assoc}.txt ---"
done

echo "--- All Cache Associativity Simulations Complete ---"
