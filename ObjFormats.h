#include <string>
#include <vector>
#include "SmoothMesh.h"

// Return string of the object
std::string mesh_to_ply_string(std::vector<MeshData> &meshes);

std::string mesh_to_obj_string(std::vector<MeshData> &meshes);

std::string mesh_to_off_string(std::vector<MeshData> &meshes);

// Directly write to file
void mesh_to_obj_file(const std::string &fileName, std::vector<MeshData> &meshes);

void mesh_to_ply_file(const std::string &fileName, std::vector<MeshData> &meshes);

void mesh_to_off_file(const std::string &fileName, std::vector<MeshData> &meshes);

