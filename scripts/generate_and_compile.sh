#!/usr/bin/env bash

export LD_LIBRARY_PATH=~/OpenBlas-build/lib:$LD_LIBRARY_PATH

make clean
mkdir -p bin/generated_kernels

FILENAME=$1
TEST_GIMMIK=$2

python3 scripts/py/generate_c_kernels.py $FILENAME $TEST_GIMMIK

make bin/benchmark_xsmm_reference
make bin/benchmark_xsmm_custom

if [ $TEST_GIMMIK -eq 1 ] then
  make bin/benchmark_gimmik
fi
