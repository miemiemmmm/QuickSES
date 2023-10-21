#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <omp.h>

#include "cuda_runtime.h"
#include "SmoothMesh.h"
#include "CudaSurf.h"

namespace py = pybind11;

py::tuple get_surf(py::array_t<float> xyzr, float grid_resolution) {
  py::buffer_info buf = xyzr.request();
  float *ptr = (float *) buf.ptr;
  int N = buf.shape[0];
  int M = buf.shape[1];

  for (int i = 0; i < N; i++){
    std::cout << ptr[i*M] << " " << ptr[i*M+1] << " " << ptr[i*M+2] << " " << ptr[i*M+3] << std::endl;
  }
  std::cout << "CPP: number of atoms: " << N << " Number of dims: " << M << "grid_resolution: " << grid_resolution << std::endl;

  std::vector<MeshData> resultMeshes = get_mesh_by_xyzr(ptr, N, M);

  std::vector<float> vertices_vec;
  std::vector<int> faces_vec;
  for (int m = 0; m < resultMeshes.size(); m++) {
    MeshData mesh = resultMeshes[m];
    for (int i = 0; i < mesh.NVertices; i++) {
      vertices_vec.push_back(static_cast<float>(mesh.vertices[i].x));
      vertices_vec.push_back(static_cast<float>(mesh.vertices[i].y));
      vertices_vec.push_back(static_cast<float>(mesh.vertices[i].z));
    }
  }

  unsigned int cumulVert = 0;
  for (int m = 0; m < resultMeshes.size(); m++) {
    MeshData mesh = resultMeshes[m];
    for (int i = 0; i < mesh.NTriangles; i++) {
      faces_vec.push_back(static_cast<int>(mesh.triangles[i].y) + cumulVert);
      faces_vec.push_back(static_cast<int>(mesh.triangles[i].x) + cumulVert);
      faces_vec.push_back(static_cast<int>(mesh.triangles[i].z) + cumulVert);
    }
    cumulVert += mesh.NVertices;
  };
  py::array_t<float> vertices({static_cast<int>(vertices_vec.size()/3), 3}, vertices_vec.data());
  py::array_t<int> faces({static_cast<int>(faces_vec.size()/3), 3}, faces_vec.data());
  return py::make_tuple(vertices, faces);
}

PYBIND11_MODULE(surface, m) {
  m.def("get_surf", &get_surf,
    py::arg("xyzr"),
    py::arg("grid_resolution") = 0.35,
    "Compute cosine similarity between two vectors"
  );
}

/*
Compile command:
g++ -std=c++17 -O3 -shared -fPIC -fopenmp -I$(echo ${CONDA_PREFIX}/include/python3.9) -I/MieT5/BetaPose/external/pybind11/include -I/MieT5/BetaPose/external testicp.cpp icp.cpp baseutils.cpp -o testicp$(python3-config --extension-suffix)
g++ -fPIC -std=c++17 -O3 -shared -I$(echo ${CONDA_PREFIX}/include/python3.9) -I/MieT5/BetaPose/external/pybind11/include -I/MieT5/BetaPose/external surface_pybind.cpp CudaSurf.o SmoothMesh.o cpdb/utils.o cpdb/cpdb.o -o surface$(python3-config --extension-suffix) -Icpdb/ -I/usr/local/cuda/include/ -lcudart -L/usr/local/cuda/lib64/
python -c "import surface; import numpy as np; coord = np.zeros((10,4)); coord[:,0] = np.linspace(0,100,10);  coord[:,3] = np.linspace(1, 2, 10); coord=np.array(coord, dtype=np.float32); print(coord); ret = surface.get_surf(coord, 0.01); print(ret); import nearl.features.fingerprint; nearl.features.fingerprint.write_ply(ret[0], triangles=ret[1],filename='testpybind.ply')" && view3d testpybind.ply
*/

