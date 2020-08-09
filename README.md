# RegpackTester

## Requirements
 - An AVX-512 CPU
 - GCC
 - Python
 - numpy, matplotlib
 - git
 - Reference LIBXSSM in "./../libxsmm_reference"
 - Custom LIBXSSM in "./../libxsmm_custom"
 - OpenBlas build in "./../OpenBlas-build"
 - If also testing GiMMiK:
  - ICC
  - GiMMiK in "./../GiMMiK" and installed

## Flow
  Run `./scripts/benchmark.sh` with the following options
    - Checkout to the commits you want to test in reference and custom LIBXSMMs.
    - If also testing GiMMiK:
      - -g : 1 (Default is 0)
    - o : log output dir
    - p : plot output dir
    - m : source matrix suite dir
    - t : type of matrix suite (pyfr or synth)
    - n : number of benchmark runs (Default is 3)
