# Modify this to change the target architecture
#NVCCFLAGS += -gencode=arch=compute_50,code=sm_50 \
#             -gencode=arch=compute_50,code=compute_50 \
#             -gencode=arch=compute_52,code=sm_52 \
#             -gencode=arch=compute_60,code=sm_60 \
#             -gencode=arch=compute_61,code=sm_61 \
#             -gencode=arch=compute_70,code=sm_70 \
#             -gencode=arch=compute_75,code=sm_75 \
#             -gencode=arch=compute_75,code=compute_75

CUDA_HOME ?= /usr/local/cuda
CUDA_COMPUTE_CAPABILITY ?= sm_80

PYTHON_INC := $(shell python3 -c "import sysconfig; print(sysconfig.get_path('include'))")
PYBIND_INC := $(shell python3 -c "import pybind11; print(pybind11.get_include())")

NVCC=nvcc
NVCCFLAGS=-use_fast_math -O3 --compiler-options "-fPIC" -I. -DMEASURETIME=0 --std=c++17 -arch=$(CUDA_COMPUTE_CAPABILITY)
CUDARUNTIME=-I$(CUDA_HOME)/include/ -lcudart -L$(CUDA_HOME)/lib64/ -DMEASURETIME=0

CC=g++
CFLAGS=-O3 -fPIC
PYFLAGS=-I$(PYTHON_INC) -I. -I$(PYBIND_INC)

# Using NVCC with pybind11 causes implicit failure
QuickSES: CudaSurf.o cpdb/cpdb.o cpdb/utils.o SmoothMesh.o
	$(CC) -o QuickSES cpdb/cpdb.o cpdb/utils.o SmoothMesh.o CudaSurf.o $(CFLAGS) $(CUDARUNTIME)

siesta_src: CudaSurf.o cpdb/cpdb.o cpdb/utils.o ObjFormats.o SmoothMesh.o
	$(CC) -shared -fPIC -o siesta_src.so SiESTA.cpp cpdb/cpdb.o cpdb/utils.o SmoothMesh.o CudaSurf.o ObjFormats.o $(CFLAGS) $(CUDARUNTIME) $(PYFLAGS)

CudaSurf.o: CudaSurf.cu
	$(NVCC) -c -o CudaSurf.o CudaSurf.cu $(NVCCFLAGS)

SmoothMesh.o: SmoothMesh.cpp
	$(CC) -c -o SmoothMesh.o SmoothMesh.cpp $(CFLAGS) $(CUDARUNTIME)

cpdb/utils.o: cpdb/utils.cpp
	$(CC) -c -o cpdb/utils.o cpdb/utils.cpp $(CFLAGS) $(CUDARUNTIME)

cpdb/cpdb.o: cpdb/cpdb.cpp
	$(CC) -c -o cpdb/cpdb.o cpdb/cpdb.cpp $(CFLAGS) $(CUDARUNTIME)

ObjFormats.o: ObjFormats.cpp
	$(CC) -c -o ObjFormats.o ObjFormats.cpp $(CFLAGS) $(CUDARUNTIME)

clean:
	rm -f *.o QuickSES siesta.so
	rm -f cpdb/*.o

test:
	cd /tmp && wget https://files.rcsb.org/download/4kng.pdb -O test.pdb -o /dev/null && python -c """import siesta; \
	xyzr = siesta.pdb_to_xyzr('test.pdb'); print(f'The PDB have {xyzr.shape[0]} atoms'); \
	ret  = siesta.xyzr_to_surf(xyzr); print(f'The surface have {ret[0].shape[0]} vertices, {ret[1].shape[0]} faces'); \
	retstr = siesta.pdb_to_string('test.pdb'); print(f'Returned PLY string lengthed {retstr.__len__()}'); \
	siesta.pdb_to_file('test.pdb', 'test.ply'); \
	siesta.xyzr_to_file(xyzr, 'test.ply'); \
	""" && viewobj test.ply && rm test.pdb test.ply && echo "Test passed"

install:
	make clean && python -m build && pip install --force-reinstall -v dist/siesta_surf-0.0.2-py3-none-any.whl
