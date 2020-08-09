#!/usr/bin/env python3
from __future__ import print_function
import os
import subprocess
import sys
import re
import random
import pprint as pp

if len(sys.argv) < 4:
    print("expected 3 arguments: mat_dir b_size_mb cwd")
    exit(1)

mats_dir = sys.argv[1]
b_size = int(sys.argv[2]) * 1024 * 1024
cwd = sys.argv[3]

def gen_matrix_kernels(file_name):
    print("Generating and Compiling", file_name, file=sys.stderr)
    result = {"mat_file": file_name}
    compout = subprocess.Popen(
        ["./generate_and_compile.sh", file_name],
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
    
    return result["a_unique"]

def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


mat_paths = sum([[os.path.join(dir, file) for file in files] for dir, _, files in os.walk(mats_dir)], [])
mat_paths.sort(key=natural_keys)
num_unique = []

for mat_path in mat_paths:
    uniq = gen_matrix_kernels(mat_path)
    if uniq > 120:
        print(mat_path)
    else:
        num_unique.append(uniq)

print("List of number of unique constants {}".format(num_unique))
print("Average number of unique constants {}".format(sum(num_unique)/len(num_unique)))
print("Min number of unique constants {}".format(min(num_unique)))
print("Max number of unique constants {}".format(max(num_unique)))
