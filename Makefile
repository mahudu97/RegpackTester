CFLAGS = -std=c11 -O3 -pthread -qopenmp

GIMMIK_CFLAGS += -std=c11 -O3 -pthread -fopenmp
GIMMIK_CFLAGS += -mavx512f -mavx512cd -mavx512vl -mavx512dq -mavx512bw -mfma
GIMMIK_CFLAGS += -march=skylake-avx512
GIMMIK_CFLAGS += -qopt-zmm-usage=high

CFLAGS_XSMM_REFERENCE = -I XSMM_REFERENCE_DIR/include -I./../OpenBlas-build/include
CFLAGS_XSMM_CUSTOM = -I XSMM_CUSTOM_DIR/include -I./../OpenBlas-build/include

GIMMIK_CFLAGS = -I./bin/generated_kernels

LDFLAGS_XSMM_REFERENCE =-L./../libxsmm_reference/lib -lxsmmnoblas -lxsmm -lpthread -lrt -ldl -lm -lc
LDFLAGS_XSMM_CUSTOM =-L./../libxsmm_custom/lib -lxsmmnoblas -lxsmm -lpthread -lrt -ldl -lm -lc
LDFLAGS_XSMM_REFERENCE +=-L./../OpenBlas-build/lib -lopenblas
LDFLAGS_XSMM_CUSTOM +=-L./../OpenBlas-build/lib -lopenblas

CXX = gcc
GIMMIK_CXX = icc

bin/benchmark_xsmm_reference : src/benchmark/xsmm_reference.c src/common.c
	$(CXX) $(CFLAGS) $(CFLAGS_XSMM_REFERENCE) $^ $(LDFLAGS_XSMM_REFERENCE) -o $@

bin/benchmark_xsmm_custom : src/CFLAGS_XSMM_CUSTOM/xsmm_custom.c src/common.c
	$(CXX) $(CFLAGS) ${CFLAGS_XSMM_CUSTOM} $^ $(LDFLAGS_XSMM_CUSTOM) -o $@

bin/benchmark_gimmik : src/benchmark/gimmik.c src/common.c
	$(GIMMIK_CXX) $(GIMMIK_CFLAGS) $^ -o $@

clean :
	rm -rf bin
