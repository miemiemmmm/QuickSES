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


// Obtain the mesh vertices and faces from the calculated mesh. Mainly for xyzr_to_surf function
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


////////////////////////////////////////////////////////
// Base function to convert from xyzr to mesh objects //
////////////////////////////////////////////////////////
std::vector<MeshData> xyzr_to_mesh(py::array_t<float> xyzr, float grid_size, int smooth_step, int slice_number){
  py::buffer_info buf = xyzr.request();
  float *ptr = (float *) buf.ptr;
  int N = buf.shape[0];
  int M = buf.shape[1];
  std::vector<MeshData> resultMeshes = get_mesh_by_xyzr(ptr, N, M, grid_size, smooth_step, slice_number);
  return resultMeshes;
}

py::tuple mesh_to_tuple(std::vector<MeshData> &meshes){
  return py::make_tuple(verts_to_array(meshes), faces_to_array(meshes));
}

py::tuple xyzr_to_surf(py::array_t<float> xyzr, float grid_size, int smooth_step, int slice_number) {
  std::vector<MeshData> resultMeshes = xyzr_to_mesh(xyzr, grid_size, smooth_step, slice_number);
  return mesh_to_tuple(resultMeshes);
}

py::tuple pdb_to_surf(std::string &pdb_file, float grid_size, int smooth_step, int slice_number){
  py::array_t<float> xyzr = pdb_to_xyzr(pdb_file);
  py::tuple result = xyzr_to_surf(xyzr, grid_size, smooth_step, slice_number);
  return result;
}


// Use the function from ObjFormats.h to convert the mesh to string/file
// TODO
std::string xyzr_to_string(py::array_t<float> xyzr, std::string &format, float grid_size, int smooth_step, int slice_number){
  std::vector<MeshData> resultMeshes = xyzr_to_mesh(xyzr, grid_size, smooth_step, slice_number);
  if (format == "ply")
    return mesh_to_ply_string(resultMeshes);
  else if (format == "obj")
    return mesh_to_obj_string(resultMeshes);
  else
    std::cerr << "Output format " << format<< " is not supported" << std::endl;
    return "";
}

std::string pdb_to_string(std::string &pdb_file, std::string &format, float grid_size, int smooth_step, int slice_number){
  py::array_t<float> xyzr = pdb_to_xyzr(pdb_file);
  return xyzr_to_string(xyzr, format, grid_size, smooth_step, slice_number);
}


// TODO:
void xyzr_to_file(py::array_t<float> xyzr, std::string &out_file, std::string &format, float grid_size, int smooth_step, int slice_number){
  std::string ply_string = xyzr_to_string(xyzr, format, grid_size, smooth_step, slice_number);
  std::ofstream out(out_file);
  out << ply_string;
  out.close();
}

void pdb_to_file(std::string &pdb_file, std::string &out_file, std::string &format, float grid_size, int smooth_step, int slice_number){
	py::array_t<float> xyzr = pdb_to_xyzr(pdb_file);
  xyzr_to_file(xyzr, out_file, format, grid_size, smooth_step, slice_number);
}


PYBIND11_MODULE(siesta, m) {
  m.def("pdb_to_xyzr",
    &pdb_to_xyzr,
    py::arg("pdb_file")
  );

  m.def("xyzr_to_surf",
    &xyzr_to_surf,					// TODO
    py::arg("xyzr"),
    py::arg("grid_size") = 0.25,
    py::arg("smooth_step") = 10,
    py::arg("slice_number") = 800
  );

  m.def("pdb_to_surf",
    &pdb_to_surf,       // TODO
    py::arg("pdb_file"),
    py::arg("grid_size") = 0.25,
    py::arg("smooth_step") = 10,
    py::arg("slice_number") = 800
  );

  // TODO
  m.def("xyzr_to_string",
		&xyzr_to_string,     // TODO
		py::arg("xyzr"),
		py::arg("format") = "ply",
		py::arg("grid_size") = 0.25,
		py::arg("smooth_step") = 10,
		py::arg("slice_number") = 800
  );

  m.def("pdb_to_string",
    &pdb_to_string,
    py::arg("pdb_file"),
    py::arg("format") = "ply",
    py::arg("grid_size") = 0.25,
    py::arg("smooth_step") = 10,
    py::arg("slice_number") = 800
  );

  m.def("xyzr_to_file",
    &xyzr_to_file,      // TODO
    py::arg("xyzr"),
    py::arg("file_name"),
    py::arg("format") = "ply",
    py::arg("grid_size") = 0.25,
    py::arg("smooth_step") = 10,
    py::arg("slice_number") = 800
  );

  m.def("pdb_to_file",
    &pdb_to_file,
    py::arg("pdb_file"),
    py::arg("out_file"),
    py::arg("format") = "ply",
    py::arg("grid_size") = 0.25,
    py::arg("smooth_step") = 10,
    py::arg("slice_number") = 800
  );

}


/*
Compile command:
g++ -std=c++17 -O3 -shared -fPIC -fopenmp -I$(echo ${CONDA_PREFIX}/include/python3.9) -I/MieT5/BetaPose/external/pybind11/include -I/MieT5/BetaPose/external testicp.cpp icp.cpp baseutils.cpp -o testicp$(python3-config --extension-suffix)
g++ -fPIC -std=c++17 -O3 -shared -I$(echo ${CONDA_PREFIX}/include/python3.9) -I/MieT5/BetaPose/external/pybind11/include -I/MieT5/BetaPose/external surface_pybind.cpp CudaSurf.o SmoothMesh.o cpdb/utils.o cpdb/cpdb.o -o surface$(python3-config --extension-suffix) -Icpdb/ -I/usr/local/cuda/include/ -lcudart -L/usr/local/cuda/lib64/
python -c "import surface; import numpy as np; coord = np.zeros((10,4)); coord[:,0] = np.linspace(0,100,10);  coord[:,3] = np.linspace(1, 2, 10); coord=np.array(coord, dtype=np.float32); print(coord); ret = surface.get_surf(coord, 0.01); print(ret); import nearl.features.fingerprint; nearl.features.fingerprint.write_ply(ret[0], triangles=ret[1],filename='testpybind.ply')" && view3d testpybind.ply
*/


