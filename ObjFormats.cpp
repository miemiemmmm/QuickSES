#include "ObjFormats.h"
#include "SmoothMesh.h"

std::string mesh_to_ply_string(std::vector<MeshData> &meshes){
#if MEASURETIME
  std::clock_t start = std::clock();
#endif
  std::string ply_string = "";
  ply_string += "ply\n";
  ply_string += "format ascii 1.0\n";
  ply_string += "comment author: Yang Zhang (y.zhang@bioc.uzh.ch)\n";
  ply_string += "element vertex " + std::to_string(meshes[0].NVertices) + "\n";
  ply_string += "property float x\n";
  ply_string += "property float y\n";
  ply_string += "property float z\n";
  ply_string += "element face " + std::to_string(meshes[0].NTriangles) + "\n";
  ply_string += "property list uchar int vertex_indices\n";
  ply_string += "end_header\n";
  unsigned int cumulVert = 0;
  for (int m = 0; m < meshes.size(); m++) {
    MeshData mesh = meshes[m];
    for (int i = 0; i < mesh.NVertices; i++) {
      float3 vert = mesh.vertices[i];
      ply_string += std::to_string(vert.x) + " " + std::to_string(vert.y) + " " + std::to_string(vert.z) + "\n";
    }
  }
  ply_string += "\n";
  for (int m = 0; m < meshes.size(); m++) {
    MeshData mesh = meshes[m];
    for (int i = 0; i < mesh.NTriangles; i++) {
      ply_string += "3 " + std::to_string(cumulVert + mesh.triangles[i].y) + " " + std::to_string(cumulVert + mesh.triangles[i].x) + " " + std::to_string(cumulVert + mesh.triangles[i].z) + "\n";
    }
    cumulVert += mesh.NVertices;
  }
#if MEASURETIME
  std::cerr << "Time for writting " << (std::clock() - start) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << std::endl;
#endif
  return ply_string;
}

std::string mesh_to_obj_string(std::vector<MeshData> &meshes){
#if MEASURETIME
  std::clock_t start = std::clock();
#endif
  std::string obj_string = "";
  unsigned int cumulVert = 0;
  for (int m = 0; m < meshes.size(); m++) {
    MeshData mesh = meshes[m];
    for (int i = 0; i < mesh.NVertices; i++) {
      float3 vert = mesh.vertices[i];
      obj_string += "v " + std::to_string(vert.x) + " " + std::to_string(vert.y) + " " + std::to_string(vert.z) + "\n";
    }
  }
  obj_string += "\n";
  for (int m = 0; m < meshes.size(); m++) {
    MeshData mesh = meshes[m];
    for (int i = 0; i < mesh.NTriangles; i++) {
      obj_string += "f " + std::to_string(cumulVert + mesh.triangles[i].y + 1) + " " + std::to_string(cumulVert + mesh.triangles[i].x + 1) + " " + std::to_string(cumulVert + mesh.triangles[i].z + 1) + "\n";
    }
    cumulVert += mesh.NVertices;
  }
#if MEASURETIME
  std::cerr << "Time for writting " << (std::clock() - start) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << std::endl;
#endif
  return obj_string;
}


void mesh_to_obj_file(const std::string &fileName, std::vector<MeshData> &meshes){
#if MEASURETIME
    std::clock_t start = std::clock();
#endif

    FILE *fptr;
    if ((fptr = fopen(fileName.c_str(), "w")) == NULL) {
        fprintf(stderr, "Failed to open output file\n");
        exit(-1);
    }
    unsigned int cumulVert = 0;
    for (int m = 0; m < meshes.size(); m++) {
        MeshData mesh = meshes[m];
        // smoothMeshLaplacian(2, mesh);
        for (int i = 0; i < mesh.NVertices; i++) {
            float3 vert = mesh.vertices[i];
            fprintf(fptr, "v %.3f %.3f %.3f\n", vert.x, vert.y, vert.z );
        }
    }
    fprintf(fptr, "\n");
    for (int m = 0; m < meshes.size(); m++) {
        MeshData mesh = meshes[m];

        for (int i = 0; i < mesh.NTriangles; i++) {
            fprintf(fptr, "f %d %d %d\n", cumulVert + mesh.triangles[i].y + 1, cumulVert + mesh.triangles[i].x + 1, cumulVert + mesh.triangles[i].z + 1);
        }
        cumulVert += mesh.NVertices;
    }
    fclose(fptr);
#if MEASURETIME
    std::cerr << "Time for writting " << (std::clock() - start) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << std::endl;
#endif
}

void mesh_to_ply_file(const std::string &fileName, std::vector<MeshData> &meshes) {
  FILE *fptr;
  if ((fptr = fopen(fileName.c_str(), "w")) == NULL) {
    fprintf(stderr, "Failed to open output file\n");
    exit(-1);
  }
  fprintf(fptr, "ply\n");
  fprintf(fptr, "format ascii 1.0\n");
  fprintf(fptr, "comment author: Yang Zhang (y.zhang@bioc.uzh.ch)\n");
  fprintf(fptr, "element vertex %d\n", meshes[0].NVertices);
  fprintf(fptr, "property float x\n");
  fprintf(fptr, "property float y\n");
  fprintf(fptr, "property float z\n");
  fprintf(fptr, "element face %d\n", meshes[0].NTriangles);
//  fprintf(fptr, "property list uchar int vertex_index\n");
  fprintf(fptr, "property list uchar int vertex_indices\n");

  fprintf(fptr, "end_header\n");
  unsigned int cumulVert = 0;
  for (int m = 0; m < meshes.size(); m++) {
    MeshData mesh = meshes[m];
//    smoothMeshLaplacian(2, mesh);
    for (int i = 0; i < mesh.NVertices; i++) {
      float3 vert = mesh.vertices[i];
      fprintf(fptr, "%.3f %.3f %.3f\n", vert.x, vert.y, vert.z);
    }
  }
  fprintf(fptr, "\n");
  for (int m = 0; m < meshes.size(); m++) {
    MeshData mesh = meshes[m];
    for (int i = 0; i < mesh.NTriangles; i++) {
      fprintf(fptr, "3 %d %d %d\n", cumulVert + mesh.triangles[i].y, cumulVert + mesh.triangles[i].x, cumulVert + mesh.triangles[i].z);
    }
    cumulVert += mesh.NVertices;
  }
  fclose(fptr);
}

