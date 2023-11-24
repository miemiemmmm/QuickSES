#include <iostream>
#include <fstream>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cpdb/cpdb.h>
#include <map>

#include "cuda_runtime.h"
#include "CudaSurf.h"
#include "ObjFormats.h"


namespace py = pybind11;

py::array_t<float> verts_to_array(std::vector<MeshData> &meshes){
  std::vector<float> vertices_vec;
  unsigned int cumulVert = 0;
  for (int m = 0; m < meshes.size(); m++) {
    MeshData mesh = meshes[m];
    for (int i = 0; i < mesh.NVertices; i++) {
      vertices_vec.push_back(static_cast<float>(mesh.vertices[i].x));
      vertices_vec.push_back(static_cast<float>(mesh.vertices[i].y));
      vertices_vec.push_back(static_cast<float>(mesh.vertices[i].z));
    }
  }
  py::array_t<float> vertices({static_cast<int>(vertices_vec.size()/3), 3}, vertices_vec.data());
  return vertices;
}

py::array_t<float> faces_to_array(std::vector<MeshData> &meshes){
  std::vector<int> faces_vec;
  unsigned int cumulVert = 0;
  for (int m = 0; m < meshes.size(); m++) {
    MeshData mesh = meshes[m];
    for (int i = 0; i < mesh.NTriangles; i++) {
      faces_vec.push_back(static_cast<int>(mesh.triangles[i].y) + cumulVert);
      faces_vec.push_back(static_cast<int>(mesh.triangles[i].x) + cumulVert);
      faces_vec.push_back(static_cast<int>(mesh.triangles[i].z) + cumulVert);
    }
    cumulVert += mesh.NVertices;
  };
  py::array_t<int> faces({static_cast<int>(faces_vec.size()/3), 3}, faces_vec.data());
  return faces;
}


std::string xyzr_to_ply_string(py::array_t<float> xyzr, float grid_size, int smooth_step, int slice_number){
  py::buffer_info buf = xyzr.request();
  float *ptr = (float *) buf.ptr;
  int N = buf.shape[0];
  int M = buf.shape[1];
  std::vector<MeshData> resultMeshes = get_mesh_by_xyzr(ptr, N, M, grid_size, smooth_step, slice_number);
  return mesh_to_ply_string(resultMeshes);
}

std::string xyzr_to_obj_string(py::array_t<float> xyzr, float grid_size, int smooth_step, int slice_number){
  py::buffer_info buf = xyzr.request();
  float *ptr = (float *) buf.ptr;
  int N = buf.shape[0];
  int M = buf.shape[1];
  std::vector<MeshData> resultMeshes = get_mesh_by_xyzr(ptr, N, M, grid_size, smooth_step, slice_number);
  return mesh_to_obj_string(resultMeshes);
}

py::tuple xyzr_to_surf(py::array_t<float> xyzr, float grid_size, int smooth_step, int slice_number) {
  py::buffer_info buf = xyzr.request();
  float *ptr = (float *) buf.ptr;
  int N = buf.shape[0];
  int M = buf.shape[1];
  std::vector<MeshData> resultMeshes = get_mesh_by_xyzr(ptr, N, M, grid_size, smooth_step, slice_number);
  return py::make_tuple(verts_to_array(resultMeshes), faces_to_array(resultMeshes));
}

py::array_t<float> pdb_to_xyzr(std::string &pdb_file){
  std::map<char, float> radiusDic = {
    {'O', 1.52f}, {'C', 1.70f}, {'N', 1.55f},
    {'H', 1.20f}, {'S', 2.27f}, {'P', 1.80f},
    {'X', 1.40f}
  };
  pdb *Prot;
  Prot = initPDB();
  parsePDB((char *)pdb_file.c_str(), Prot, (char *)"");
  unsigned int N = 0;
  std::vector<float3> atomPos;
  std::vector<float> atomRadii;

  atom *A = NULL;
  chain *C = NULL;

  for (int chainId = 0; chainId < Prot->size; chainId++) {
    C = &Prot->chains[chainId];
    A = &C->residues[0].atoms[0];
    while (A != NULL) {
      float3 coords = A->coor;
      atomPos.push_back(coords);
      float atomRad;
      if (radiusDic.count(A->element[0]))
        atomRad = radiusDic[A->element[0]];
      else
        atomRad = radiusDic['X'];
      atomRadii.push_back(atomRad);
      std::cout << "found atom " << A->element << " " << A->coor.x << " " << A->coor.y << " " << A->coor.z << std::endl;
      N++;
      A = A->next;
    }
  }
  freePDB(Prot);
  float xyzr_data[N*4];
  for (int i = 0; i < N; i++){
    xyzr_data[i*4] = atomPos[i].x;
    xyzr_data[i*4+1] = atomPos[i].y;
    xyzr_data[i*4+2] = atomPos[i].z;
    xyzr_data[i*4+3] = atomRadii[i];
  }
  // NOTE: the shape container should all element be int type (unsigned int triggers a failure)
  py::array_t<float> xyzr({static_cast<int>(N), 4}, xyzr_data);
  return xyzr;
}

std::string pdb_to_ply_string(std::string &pdb_file, float grid_size, int smooth_step, int slice_number){
  py::array_t<float> xyzr = pdb_to_xyzr(pdb_file);
  return xyzr_to_ply_string(xyzr, grid_size, smooth_step, slice_number);
}

void pdb_to_ply_file(std::string &pdb_file, std::string &ply_file, float grid_size, int smooth_step, int slice_number){
	py::array_t<float> xyzr = pdb_to_xyzr(pdb_file);
	std::string ply_string = xyzr_to_ply_string(xyzr, grid_size, smooth_step, slice_number);
	std::ofstream out(ply_file);
	out << ply_string;
	out.close();
}




py::tuple get_surf(py::array_t<float> xyzr, float grid_size, int smooth_step, int slice_number){
  py::buffer_info buf = xyzr.request();
  float *ptr = (float *) buf.ptr;
  int N = buf.shape[0];
  int M = buf.shape[1];

  // Test if the input is correctly passed
  for (int i = 0; i < N; i++){
    std::cout << ptr[i*M] << " " << ptr[i*M+1] << " " << ptr[i*M+2] << " " << ptr[i*M+3] << std::endl;
  }
  std::cout << "CPP: number of atoms: " << N << " Number of dims: " << M << "grid_size: " << grid_size << std::endl;
  std::cout << "slice number" << slice_number << "smooth_step" << smooth_step << std::endl;
  ////////////////////////////

  // Return vector of MeshData
  std::vector<MeshData> resultMeshes = get_mesh_by_xyzr(ptr, N, M, grid_size, smooth_step, slice_number);



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

PYBIND11_MODULE(siesta, m) {
//  m.def("get_surf", &get_surf,
//    py::arg("xyzr"),
//    py::arg("grid_size") = 0.25,
//    py::arg("smooth_step") = 10,
//    py::arg("slice_number") = 800,
//    "Compute cosine similarity between two vectors"
//  );
  m.def("pdb_to_xyzr",
    &pdb_to_xyzr,
    py::arg("pdb_file")
  );
  m.def("pdb_to_ply_string",
    &pdb_to_ply_string,
    py::arg("pdb_file"),
    py::arg("grid_size") = 0.25,
    py::arg("smooth_step") = 10,
    py::arg("slice_number") = 800
  );

}

//make clean && make siesta.so &&
