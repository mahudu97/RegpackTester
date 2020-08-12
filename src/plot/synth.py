import matplotlib.pyplot as plt
import os
import sys
import numpy as np

from .tools import calc_FLOPS, load_benchmark_data, get_perf, B_TARGET_PANEL_WIDTH

if len(sys.argv) < 7:
    print("expected 6 arguments: mat_dir n_runs b_num_col test_gimmik TIMESTAMP plot_dir")
    exit(1)

MAT_PATH = sys.argv[1]
N_RUNS = sys.argv[2]
B_NUM_COL = sys.argv[3]
TEST_GIMMIK = sys.argv[4]
TIMESTAMP = sys.argv[5]
PLOT_DIR = sys.argv[6]

LOG_DATA_DIR = "./bin/log_data"

mat_paths = sum([[os.path.join(dir, file) for file in files] \
    for dir, _, files in os.walk(MAT_PATH)], [])

mat_flops = calc_FLOPS(mat_paths, B_TARGET_PANEL_WIDTH)

runs = load_benchmark_data(N_RUNS, LOG_DATA_DIR, TIMESTAMP)

def plot(runs, mat_flops, x_term, trait, xlabel, title, save_as, \
    x_logscale=True, set_x_ticks=False):
    global PLOT_DIR
    global B_NUM_COL
    global TEST_GIMMIK

    plt.figure(figsize=(6,5))

    if TEST_GIMMIK == "1":
        x_values, custom_y_avg, ref_y_avg, gimmik_y_avg = \
            get_perf(runs, N_RUNS, trait, x_term, mat_flops, B_NUM_COL, TEST_GIMMIK)
    else:
        x_values, custom_y_avg, ref_y_avg = \
            get_perf(runs, N_RUNS, trait, x_term, mat_flops, B_NUM_COL, TEST_GIMMIK)

        plt.plot(x_values, custom_y_avg, label="Custom LIBXSMM", color="limegreen", marker=".")
        plt.plot(x_values, ref_y_avg, label="Reference LIBXSMM", color="maroon", marker=".")
        if TEST_GIMMIK == "1":
            plt.plot(x_values, gimmik_y_avg, label="GiMMiK", color="orange", marker=".")

    plt.xlabel(xlabel)
    plt.ylabel("Pseudo-FLOP/s")
    plt.yscale("log", basey=10)
    if x_logscale:
        plt.xscale("log", basex=2)
    elif set_x_ticks:
        plt.xticks(x_values)
    plt.title(title)
    plt.legend()
    plt.savefig(os.path.join(PLOT_DIR,"synth/{}_{}.pdf".format(save_as, TIMESTAMP)))

### Vary Rows ###
xlabel="Number of Rows"
x_term="a_rows"
# 16 distinct non-zeros
trait="vary_row/q_16"
title="Number of Rows in A vs Pseudo-FLOP/s (U16)"
save_as="vary_row_16"
plot(runs, mat_flops, x_term, trait, xlabel, title, save_as)
# 64 distinct non-zeros
trait="vary_row/q_64"
title="Number of Rows in A vs Pseudo-FLOP/s (U64)"
save_as="vary_row_64"
plot(runs, mat_flops, x_term, trait, xlabel, title, save_as)

### Vary Columns ###
xlabel="Number of Columns"
x_term="a_cols"
# 16 distinct non-zeros
trait="vary_col/q_16"
title="Number of Columns in A vs Pseudo-FLOP/s (U16)"
save_as="vary_cols_16"
plot(runs, mat_flops, x_term, trait, xlabel, title, save_as)
# 64 distinct non-zeros
trait="vary_col/q_64"
title="Number of Columns in A vs Pseudo-FLOP/s (U64)"
save_as="vary_cols_64"
plot(runs, mat_flops, x_term, trait, xlabel, title, save_as)

### Vary Density ###
xlabel="Density"
x_term="density"
# 16 distinct non-zeros
trait="vary_density/q_16"
title="Density of A vs Pseudo-FLOP/s (U16)"
save_as="vary_density_16"
plot(runs, mat_flops, x_term, trait, xlabel, title, save_as, x_logscale=False)
# 64 distinct non-zeros
trait="vary_density/q_64"
title="Density of A vs Pseudo-FLOP/s (U64)"
save_as="vary_density_64"
plot(runs, mat_flops, x_term, trait, xlabel, title, save_as, x_logscale=False)

### Vary Unique ###
xlabel="Number of Unique Constants"
x_term="a_unique"
trait="vary_unique"
title="Number of Unique Constants in A vs Pseudo-FLOP/s"
save_as="vary_unique"
plot(runs, mat_flops, x_term, trait, xlabel, title, save_as, x_logscale=False, set_x_ticks=True)
