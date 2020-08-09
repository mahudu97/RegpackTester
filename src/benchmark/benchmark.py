#!/usr/bin/env python3
from __future__ import print_function
import os
import subprocess
import sys
import re
import random
import pprint as pp

if len(sys.argv) < 5:
    print("expected 4 arguments: mat_dir cwd b_num_col test_gimmik")
    exit(1)

mats_dir = sys.argv[1]
cwd = sys.argv[2]
B_NUM_COL = sys.argv[3]
test_gimmik = sys.argv[4]

def benchmark_matrix(file_name, num_col_b, gimmik):
    print("Generating and Compiling", file_name, file=sys.stderr)
    result = {"mat_file": file_name}
    compout = subprocess.Popen(
        ["./scripts/generate_and_compile.sh", file_name, gimmik],
        stdout=subprocess.PIPE, cwd=cwd
    )
    for line in compout.stdout.readlines():
        strline = line.decode('utf-8')
        if "INFO" in strline:
            [head, const] = strline.split(":")
            if "size of" in head:
                result["a_size"] = int(const)
            elif "number of constants" in head:
                result["a_nonzero"] = int(const)
            elif "number of unique constants" in head:
                result["a_unique"] = int(const)
            elif "number of rows" in head:
                result["a_rows"] = int(const)
            elif "number of columns" in head:
                result["a_cols"] = int(const)
            elif "alpha" in head:
                result["alpha"] = float(const)
            elif "beta" in head:
                result["beta"] = float(const)
    result["density"] = result["a_nonzero"] / result["a_size"]

    print("Running", file_name, file=sys.stderr)
    benchmark_cmd = ["./scripts/bin_benchmark.sh", str(num_col_b), str(random.randint(0, 2**31)), str(gimmik)]
    runout = subprocess.Popen(
        benchmark_cmd,
        stdout=subprocess.PIPE
    )
    for line in runout.stdout.readlines():
        strline = line.decode('utf-8')
        if "execution time" in strline:
            [engine, stat, _, _, time] = strline.split(" ")
            if "xsmm-reference" in engine:
                if "best" in stat:
                    result["xsmm_reference_best"] = float(time)
                elif "avg" in stat:
                    result["xsmm_reference_avg"] = float(time)
            elif "xsmm-custom" in engine:
                if "best" in stat:
                    result["xsmm_custom_best"] = float(time)
                elif "avg" in stat:
                    result["xsmm_custom_avg"] = float(time)
            elif "gimmik" in engine:
                if "best" in stat:
                    result["gimmik_best"] = float(time)
                elif "avg" in stat:
                    result["gimmik_avg"] = float(time)

    result["speedup_best_over_ref"] = result["xsmm_reference_best"] / result["xsmm_custom_best"]
    result["speedup_avg_over_ref"] = result["xsmm_reference_avg"] / result["xsmm_custom_avg"]
    if gimmik == "1": 
        result["speedup_best_over_gim"] = result["gimmik_best"] / result["xsmm_custom_best"]
        result["speedup_avg_over_gim"] = result["gimmik_avg"] / result["xsmm_custom_avg"]

    print("Finished running in", str(min(result["xsmm_reference_best"], \
        result["xsmm_custom_best"], result["gimmik_best"])) + "ms", file=sys.stderr)

    pp.pprint(result, compact=True, width=1000)

    if gimmik == "1": 
        return result["speedup_best_over_ref"], result["speedup_avg_over_ref"], \
            result["speedup_best_over_gim"], result["speedup_avg_over_gim"]
    else:
        return result["speedup_best_over_ref"], result["speedup_avg_over_ref"]

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


mat_paths = sum([[os.path.join(dir, file) for file in files] for dir, _, files in os.walk(mats_dir)], [])
mat_paths.sort(key=natural_keys)

speedups_best_over_ref = []
speedups_avg_over_ref = []
speedups_best_over_gim = []
speedups_avg_over_gim = []

for mat_path in mat_paths:
    if test_gimmik == "0":
        best, avg = benchmark_matrix(mat_path, B_NUM_COL, test_gimmik)
        speedups_best_over_ref.append(best)
        speedups_avg_over_ref.append(avg)
    else:
        best_over_ref, avg_ovr_ref, best_over_gim, best_over_gim = benchmark_matrix(mat_path, B_NUM_COL, test_gimmik)
        speedups_best_over_ref.append(best_over_ref)
        speedups_avg_over_ref.append(avg_ovr_ref)
        speedups_best_over_gim.append(best_over_gim)
        speedups_avg_over_gim.append(best_over_gim)

print("Average speedup (best) of custom over reference {}".format(sum(speedups_best_over_ref)/len(speedups_best_over_ref)))
print("Average speedup (iqr avg) of custom over reference {}".format(sum(speedups_avg_over_ref)/len(speedups_avg_over_ref)))
if test_gimmik == "1":
    print("Average speedup (best) of custom over GiMMiK {}".format(sum(speedups_best_over_gim)/len(speedups_best_over_gim)))
    print("Average speedup (iqr avg) of custom over GiMMiK {}".format(sum(speedups_avg_over_gim)/len(speedups_avg_over_gim)))
