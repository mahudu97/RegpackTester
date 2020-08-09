#!/usr/bin/env python
# coding: utf-8

import pickle
import os
import numpy as np

AVX_512_WIDTH = 8

AVX512_FLOPS_PER_CYCLE = 8*2 # DP FMA
NUM_AVX512_UNITS = 2
AVX512_FREQ = 2.4 # All Cores Active AVX512 Boost (GHz)
XEON_8175M_PEAK_FLOPS = AVX512_FREQ * NUM_AVX512_UNITS * AVX512_FLOPS_PER_CYCLE
XEON_8175M_PEAK_BW = 13.5163 # GB/s

B_TARGET_PANEL_WIDTH = 48

def clean(matrix, tol=1e-10):
    arr = matrix.copy()

    # Flush small elements to zero
    arr[np.abs(arr) < tol] = 0

    # Coalesce similar elements
    if arr.size > 1:
        amfl = np.abs(arr.flat)
        amix = np.argsort(amfl)

        i, ix = 0, amix[0]
        for j, jx in enumerate(amix[1:], start=1):
            if amfl[jx] - amfl[ix] >= tol:
                if j - i > 1:
                    amfl[amix[i:j]] = np.median(amfl[amix[i:j]])
                i, ix = j, jx

        if i != j:
            amfl[amix[i:]] = np.median(amfl[amix[i:]])

        # Fix up the signs and assign
        arr.flat = np.copysign(amfl, arr.flat)

    return arr

def basic_flops(mat, b_cols):
    # A and B dimensions
    mat_a_dims = mat.shape
    mat_b_dims = (mat_a_dims[1], b_cols)

    # below count would be repeated across panels of B
    num_panels = b_cols/AVX_512_WIDTH

    # ijk loop skipping 0s
    # assume SIMD version - 8 wide FMA
    flops = 0
    for row in mat:
        for el in row:
            if el != 0:
                # can add load of B here
                flops += 16 # 8 wide DP FMA
        # can add store count here

    return (flops * num_panels) # for whole mat mul

def calc_FLOPS(mat_paths, block_alignment):
    mat_flops = {}
    for mat_path in mat_paths:
        with open(mat_path) as f:
            test_mat = clean(np.loadtxt(f))
        flops_per_panel = basic_flops(test_mat, block_alignment)
        mat_flops[mat_path] = flops_per_panel
    return mat_flops

def load_benchmark_data(n_runs, log_data_dir, timestamp):
    runs = []
    for i in range(1,n_runs+1):
        run_file = os.path.join(log_data_dir, "run_{}_{}.out".format(timestamp, i))
        with open(run_file, "rb") as f:
            runs.append( pickle.load(f) )
    return runs

# trait is from a run: i.e run["quad"] for pyfr mats
def sort_values(x_term, trait, mat_flops, b_num_col, gimmik, t='best'):
    _NUM_PANELS = b_num_col / B_TARGET_PANEL_WIDTH

    custom_x, custom_y = [], []
    ref_x, ref_y = [], []
    if gimmik == "1":
        gimmik_x, gimmik_y = [], []

    for i, u in enumerate(trait[x_term]):
        FLOPS_PER_PANEL = mat_flops[trait['mat_file'][i]]

        time_per_panel_custom = (trait['xsmm_custom_'+t][i]*1e-3)/_NUM_PANELS
        time_per_panel_ref   = (trait['xsmm_reference_'+t][i]*1e-3)/_NUM_PANELS

        custom_x.append(u)
        custom_y.append(FLOPS_PER_PANEL / time_per_panel_custom)
        ref_x.append(u)
        ref_y.append(FLOPS_PER_PANEL / time_per_panel_ref)

        if gimmik == "1":
            time_per_panel_gimmik = (trait['gimmik_'+t][i]*1e-3)/_NUM_PANELS
            gimmik_x.append(u)
            gimmik_y.append(FLOPS_PER_PANEL / time_per_panel_gimmik)

    old_len = len(custom_y)

    custom_y = [x for _,x in sorted(zip(custom_x, custom_y))]
    custom_x.sort()
    assert(old_len == len(custom_y))

    ref_y = [x for _,x in sorted(zip(ref_x, ref_y))]
    ref_x.sort()

    if gimmik == "1":
        gimmik_y = [x for _,x in sorted(zip(gimmik_x, gimmik_y))]
        gimmik_x.sort()

    if gimmik == "1":
        return custom_x, custom_y, ref_x, ref_y. gimmik_x, gimmik_y
    else:
        return custom_x, custom_y, ref_x, ref_y

# sort_values(x_term, run, mat_flops, b_num_col, gimmik, t='best'):
def get_perf(runs, shape, x_term, mat_flops, b_num_col, gimmik, t='best'):
    if gimmik == "1":
        custom_x1, custom_y1, _, ref_y1, _, gimmik_y1 = \
            sort_values(x_term, runs[0][shape], mat_flops, b_num_col, gimmik, t)
        _, custom_y2, _, ref_y2, _, gimmik_y2 = \
            sort_values(x_term, runs[1][shape], mat_flops, b_num_col, gimmik, t)
        _, custom_y3, _, ref_y3, _, gimmik_y3 = \
            sort_values(x_term, runs[2][shape], mat_flops, b_num_col, gimmik, t)

        custom_y_avg = [sum(elem)/len(elem) for elem in zip(custom_y1, custom_y2, custom_y3)]
        ref_y_avg = [sum(elem)/len(elem) for elem in zip(ref_y1, ref_y2, ref_y3)]
        gimmik_y_avg = [sum(elem)/len(elem) for elem in zip(gimmik_y1, gimmik_y2, gimmik_y3)]

        return custom_x1, custom_y_avg, ref_y_avg, gimmik_y_avg

    else:
        custom_x1, custom_y1, _, ref_y1 = \
            sort_values(x_term, runs[0][shape], mat_flops, b_num_col, gimmik, t)
        _, custom_y2, _, ref_y2 = \
            sort_values(x_term, runs[1][shape], mat_flops, b_num_col, gimmik, t)
        _, custom_y3, _, ref_y3 = \
            sort_values(x_term, runs[2][shape], mat_flops, b_num_col, gimmik, t)

        custom_y_avg = [sum(elem)/len(elem) for elem in zip(custom_y1, custom_y2, custom_y3)]
        ref_y_avg = [sum(elem)/len(elem) for elem in zip(ref_y1, ref_y2, ref_y3)]

        return custom_x1, custom_y_avg, ref_y_avg
