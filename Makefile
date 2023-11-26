# Modify this to change the target architecture
#NVCCFLAGS += -gencode=arch=compute_50,code=sm_50 \
#             -gencode=arch=compute_50,code=compute_50 \
#             -gencode=arch=compute_52,code=sm_52 \
#             -gencode=arch=compute_60,code=sm_60 \
#             -gencode=arch=compute_61,code=sm_61 \
#             -gencode=arch=compute_70,code=sm_70 \
#             -gencode=arch=compute_75,code=sm_75 \
#             -gencode=arch=compute_75,code=compute_75

NVCC=nvcc
NVCCFLAGS=-use_fast_math -O3 --compiler-options "-fPIC" -I.
CUDARUNTIME=-I/usr/local/cuda/include/ -lcudart -L/usr/local/cuda/lib64/

CC=g++
CFLAGS=-O3 -fPIC
PYFLAGS=-I/home/yzhang/mamba/envs/mlenv/include/python3.9 -I.

# Using NVCC with pybind11 causes implicit failure
QuickSES: CudaSurf.o cpdb/cpdb.o cpdb/utils.o SmoothMesh.o
	$(CC) -o QuickSES cpdb/cpdb.o cpdb/utils.o SmoothMesh.o CudaSurf.o $(CFLAGS) $(CUDARUNTIME)

siesta.so: CudaSurf.o cpdb/cpdb.o cpdb/utils.o ObjFormats.o SmoothMesh.o
	$(CC) -shared -fPIC -o siesta.so SiESTA.cpp cpdb/cpdb.o cpdb/utils.o SmoothMesh.o CudaSurf.o ObjFormats.o $(CFLAGS) $(CUDARUNTIME) $(PYFLAGS)

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
	python -c """import siesta; \
	ret = siesta.pdb_to_xyzr('4bso.pdb'); print(ret); \
	ret_str = siesta.pdb_to_ply_string('4bso.pdb'); print(ret_str); \
	"""

install:
	python -m build && pip install -v dist/siesta-surf-0.0.1.tar.gz

