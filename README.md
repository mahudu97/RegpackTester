# RegpackTester
Compares performance of LIBXSMM versions (and to GiMMiK).

Process is scripted from code generation all the way to plotting. (Generate/get matrices before-hand)

Made to compare the Register Packing addition to LIBXSMM small-sparse A operator MM routine.

## Requirements
 - An AVX-512 CPU
 - GCC
 - Python
 - numpy, matplotlib
 - Reference LIBXSSM in "./../libxsmm_reference"
 - Custom LIBXSSM in "./../libxsmm_custom"
 - OpenBlas build in "./../OpenBlas-build"
 - If also testing GiMMiK:
    - ICC
    - GiMMiK in "./../GiMMiK" and installed

## Flow
Checkout to the commits you want to test in reference and custom LIBXSMMs.

Run `./scripts/benchmark.sh` with the following options
  - If also testing GiMMiK:
    - -g : 1 (Default is 0)
  - -o : log output dir
  - -p : plot output dir
  - -m : source matrix suite dir
  - -t : type of matrix suite (pyfr or synth)
  - -n : number of benchmark runs (Default is 3)
  - -d : if reference XSMM is dense routine (1) (Default is 0)
  - -s : skip benchmark process, plot a previous run
    - Other options above still required
    - Default is 0 (don't skip)
    - Provide the timestamp of the previous run you want to plot

## Hardcoded values
- Block alignment = 48
  - src/benchmark/common.h
  - src/plots/tools.py

- XEON_8175M Stats
  - src/plots/cpu_stats.py
