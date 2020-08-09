#!/bin/bash

WD=$(pwd)

XSMM_REFERENCE_DIR=./../libxsmm_reference
XSMM_CUSTOM_DIR=./../libxsmm_custom
GIMMIK_DIR=./../GiMMiK

B_NUM_COL=192000

while getopts ":g:t:" opt; do
  case $opt in
    g) TEST_GIMMIK="${OPTARG:-$0}"
    ;;
    m) MATS_DIR="$OPTARG"
    t) MAT_TYPE="$OPTARG" # pyfr or synth
    ;;
    o) LOG_DIR="$OPTARG"
    p) PLOT_DIR="$OPTARG"
    ;;
    n) N_RUNS="${OPTARG:-$3}"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

echo "Building LIBXSMM libraries"
cd $XSMM_REFERENCE_DIR
make realclean
make -j
cd $XSMM_CUSTOM_DIR
make realclean
make -j

TIMESTAMP="$(date +"%T")"
echo "Using $TIMESTAMP to stamp log and plot files"

cd $WD

# Perform N benchmark runs
for i in {1..$N_RUNS}
do
  echo "Starting benchmark run $i"
  python3 src/benchmark.py $MATS_DIR $WD $B_NUM_COL $TEST_GIMMIK $ > $LOG_DIR/run_${TIMESTAMP}_$i.out 2> $LOG_DIR/run_${TIMESTAMP}_$i.err
  echo "Finished benchmark run $i"
done

# Sort log data and pickle for plotting
mkdir -p bin/log_data
python3 src/plot/pickle_runs.py $MAT_TYPE $N_RUNS $LOG_DIR $TIMESTAMP $TEST_GIMMIK

# Plot
if [ $MAT_TYPE == "pyfr" ]
then
  # plot normal
  # plot roofline 
elif [ $MAT_TYPE == "synth" ]
then
  # plot normal
  # plot roofline
fi