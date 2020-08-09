#!/usr/bin/env bash

export LD_LIBRARY_PATH=~/OpenBlas-build/lib:$LD_LIBRARY_PATH

if [ $3 -eq 0 ] # xsmm
then
  nice -20 taskset -c 0 bin/benchmark_xsmm_reference $1 $2
  nice -20 taskset -c 0 bin/benchmark_xsmm_custom $1 $2
elif [ $3 -eq 1 ]; # gimmik
then
  nice -20 taskset -c 0 bin/benchmark_gimmik $1 $2
fi
