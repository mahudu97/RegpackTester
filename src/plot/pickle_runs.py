from ast import literal_eval as eval
import pickle
import sys
import os

if len(sys.argv) < 6:
    print("expected 5 arguments: mat_type n_runs log_dir timestamp test_gimmik")
    exit(1)

mat_type = sys.argv[1] # "pyfr" of "synth"
n_runs = int(sys.argv[2])
log_dir = sys.argv[3]
timestamp = sys.argv[4]
test_gimmik = sys.argv[5]

runs = []
for _ in range(n_runs):
    runs.append({})

if mat_type == "pyfr":
    types = ["hex", "quad", "tet", "tri"]
elif mat_type == "synth":
    types = ["vary_row/q_16", "vary_row/q_64",
	         "vary_col/q_16", "vary_col/q_64",
             "vary_density/q_16", "vary_density/q_64",
             "vary_unique"]

for i, run in enumerate(runs):
    for t in types:
        log_file = os.path.join(log_dir,"run_{}_{}.out".format(timestamp, i+1))
        out_file = "./bin/log_data/run_{}_{}.out".format(timestamp, i+1)

        with open(log_file) as f:
            run[t] = {}
            run[t]['a_cols'] = []
            run[t]['a_nonzero'] = []
            run[t]['a_rows'] = []
            run[t]['a_size'] = []
            run[t]['a_unique'] = []
            run[t]['density'] = []
            run[t]['mat_file'] = []
            run[t]['speedup_avg_over_ref'] = []
            run[t]['speedup_best_over_ref'] = []
            run[t]['xsmm_custom_avg'] = []
            run[t]['xsmm_custom_best'] = []
            run[t]['xsmm_reference_avg'] = []
            run[t]['xsmm_reference_best'] = []
            if test_gimmik == "1":
                run[t]['speedup_avg_over_gim'] = []
                run[t]['speedup_best_over_gim'] = []
                run[t]['gimmik_avg'] = []
                run[t]['gimmik_best'] = []

            for line in f:
                if '{' in line and t in line:
                    res = eval(line)
                    run[t]['a_cols'].append(res['a_cols'])
                    run[t]['a_nonzero'].append(res['a_nonzero'])
                    run[t]['a_rows'].append(res['a_rows'])
                    run[t]['a_size'].append(res['a_size'])
                    run[t]['a_unique'].append(res['a_unique'])
                    run[t]['density'].append(res['density'])
                    run[t]['mat_file'].append(res['mat_file'])
                    run[t]['speedup_avg_over_ref'].append(res['speedup_avg_over_ref'])
                    run[t]['speedup_best_over_ref'].append(res['speedup_best_over_ref'])
                    run[t]['xsmm_custom_avg'].append(res['xsmm_custom_avg'])
                    run[t]['xsmm_custom_best'].append(res['xsmm_custom_best'])
                    run[t]['xsmm_reference_avg'].append(res['xsmm_reference_avg'])
                    run[t]['xsmm_reference_best'].append(res['xsmm_reference_best'])
                    if test_gimmik == "1":
                        run[t]['speedup_avg_over_gim'].append(res['speedup_avg_over_gim'])
                        run[t]['speedup_best_over_gim'].append(res['speedup_best_over_gim'])
                        run[t]['gimmik_avg'].append(res['gimmik_avg'])
                        run[t]['gimmik_best'].append(res['gimmik_best'])

    with open(out_file, "wb") as f:
        pickle.dump(run, f)
