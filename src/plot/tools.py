#!/usr/bin/env python
# coding: utf-8

import pickle
import os
import numpy as np

from .cpu_stats import AVX_512_WIDTH

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
def get_perf(runs, n_runs, shape, x_term, mat_flops, b_num_col, gimmik, t='best'):
    if gimmik == "1":
        custom_x, custom_y, ref_y, gimmik_y = [], [], [], []
        for i in range(n_runs):
            cx1, cy1, _, ry1, _, gy1 = \
                sort_values(x_term, runs[i][shape], mat_flops, b_num_col, gimmik, t)
            custom_x.append(cx1)
            custom_y.append(cy1)
            ref_y.append(ry1)
            gimmik_y.append(gy1)

        custom_y_avg = [sum(elem)/len(elem) for elem in zip(custom_y)]
        ref_y_avg = [sum(elem)/len(elem) for elem in zip(ref_y)]
        gimmik_y_avg = [sum(elem)/len(elem) for elem in zip(gimmik_y)]

        return custom_x, custom_y_avg, ref_y_avg, gimmik_y_avg

    else:
        custom_x, custom_y, ref_y = [], [], []
        for i in range(n_runs):
            cx1, cy1, _, ry1, _ = \
                sort_values(x_term, runs[i][shape], mat_flops, b_num_col, gimmik, t)
            custom_x.append(cx1)
            custom_y.append(cy1)
            ref_y.append(ry1)

        custom_y_avg = [sum(elem)/len(elem) for elem in zip(custom_y)]
        ref_y_avg = [sum(elem)/len(elem) for elem in zip(ref_y)]

        return custom_x, custom_y_avg, ref_y_avg

# trait is a list formed from runs: i.e run["quad"] for pyfr mats
def calc_GFLOPs(mat_FLOPS, mat_names, trait, b_num_col, gimmik, t='best'):
    _NUM_PANELS = b_num_col / B_TARGET_PANEL_WIDTH

    custom_GFLOPs = []
    ref_GFLOPs = []
    if gimmik:
        gimmik_GFLOPs = []

    for i, mat_name in enumerate(mat_names):
        _FLOPS_PER_PANEL = mat_FLOPS[mat_name]
        custom_inner = []
        ref_inner = []
        if gimmik:
            gimmik_inner = []

        for run in trait:
            # *1e-3 for ms to s
            time_per_panel_custom = (run['xsmm_custom_'+t][i]*1e-3)/_NUM_PANELS
            custom_inner.append(_FLOPS_PER_PANEL / time_per_panel_custom)

            time_per_panel_ref   = (run['xsmm_reference_'+t][i]*1e-3)/_NUM_PANELS
            ref_inner.append(_FLOPS_PER_PANEL / time_per_panel_ref)

            if gimmik:
                time_per_panel_gimmik = (run['gimmik_'+t][i]*1e-3)/_NUM_PANELS
                gimmik_inner.append(_FLOPS_PER_PANEL / time_per_panel_gimmik)

        custom_avg = sum(custom_inner) / len(custom_inner)
        custom_GFLOPs.append(custom_avg / 1e9)

        ref_avg = sum(ref_inner) / len(ref_inner)
        ref_GFLOPs.append(ref_avg / 1e9)

        if gimmik:
            gimmik_avg = sum(gimmik_inner) / len(gimmik_inner)
            gimmik_GFLOPs.append(gimmik_avg / 1e9)

    if gimmik:
        return custom_GFLOPs, ref_GFLOPs, gimmik_GFLOPs
    else:
        return custom_GFLOPs, ref_GFLOPs

def _calc_mem_spMM_beta_0(mat):
    # dont count A load
    num_panels = B_TARGET_PANEL_WIDTH/AVX_512_WIDTH
    # beta = 0
    mem = 0

    # load B
    for col in mat.T:
        has_A = False
        for el in col:
            if el != 0:
                has_A = True
        # at least one A - load stride of B into cache
        if has_A:
            mem += 8*8

    # store C
    for row in mat:
        has_A = False
        for el in row:
            if el != 0:
                has_A = True
        # at least one A - store a C stride
        if has_A:
            mem += 8*8

    return (mem * num_panels)# + mem_A # dont repeat A load

def _calc_mem_dense_beta_0(mat):
    # dont count A load
    num_panels = B_TARGET_PANEL_WIDTH/AVX_512_WIDTH
    # beta = 0
    mem = 0

    # load B
    for _ in mat.T:
        mem += 8*8

    # store C
    for _ in mat:
        mem += 8*8

    return (mem * num_panels)# + mem_A # dont repeat A load

# returns AIs for XSMM SpMM, dense, (and GiMMiK)
def get_AIs(mat_paths, gimmik):
    spMM_AIs, dense_AIs = [], []

    for mat_path in mat_paths:
        with open(mat_path) as f:
            test_mat = clean(np.loadtxt(f))
            flops_per_panel = basic_flops(test_mat, B_TARGET_PANEL_WIDTH)
            spmm_mem_per_panel = _calc_mem_spMM_beta_0(test_mat)
            dense_mem_per_panel = _calc_mem_dense_beta_0(test_mat)
            spMM_AIs.append( flops_per_panel / spmm_mem_per_panel )
            dense_AIs.append( flops_per_panel / dense_mem_per_panel )

    if gimmik:
        # gimmik has same AI as xsmm SpMM
        return spMM_AIs, dense_AIs, spMM_AIs
    else:
        return spMM_AIs, dense_AIs
