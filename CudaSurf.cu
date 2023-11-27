/*MIT License

Copyright (c) 2019 Xavier Martinez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
#include <algorithm>
#include <cctype>
#include <fstream>
#include <functional>
#include <iostream>
#include <iterator>
#include <locale>
#include <math.h>
#include <map>
#include <memory>
#include <stdlib.h>
#include <stdio.h>
#include <sstream>
#include <string.h>
#include <vector>

#include <cpdb/cpdb.h>
#include "args.hxx"
#include "Kernels.cu"
#include "SmoothMesh.h"
#include "CudaSurf.h"
#include "ObjFormats.h"

#include "cuda_runtime.h"
#include <thrust/scan.h>
#include <thrust/device_ptr.h>
#include <thrust/sequence.h>
#include <thrust/binary_search.h>
#include <thrust/sort.h>
#include <thrust/unique.h>
#include <thrust/count.h>

using namespace std;

int SLICE = 300;
float probeRadius = PROBERADIUS;
float gridResolutionNeighbor;
float gridResolutionSES = 0.5f;
int laplacianSmoothSteps = 1;
string outputFilePath = "output.obj";
string inputFilePath = "";
std::map<char, float> radiusDic;
void initRadiusDic() {
    float factor = 1.0f;
    radiusDic['O'] = 1.52f * factor;
    radiusDic['C'] = 1.70f * factor;
    radiusDic['N'] = 1.55f * factor;
    radiusDic['H'] = 1.20f * factor;
    radiusDic['S'] = 2.27f * factor;
    radiusDic['P'] = 1.80f * factor;
    radiusDic['X'] = 1.40f * factor;
}


unsigned int getMinMax(chain *C, float3 *minVal, float3 *maxVal, float *maxAtom) {
    atom *A = NULL;
    unsigned int N = 0;


    A = &C->residues[0].atoms[0];
    float3 vmin, vmax, coords;

    vmin.x = vmin.y = vmin.z = 100000.0f;
    vmax.x = vmax.y = vmax.z = -100000.0f;
    *maxAtom = 0.0f;
    while (A != NULL) {
        coords = A->coor;
        vmin.x = std::min(vmin.x, coords.x);
        vmin.y = std::min(vmin.y, coords.y);
        vmin.z = std::min(vmin.z, coords.z);

        vmax.x = std::max(vmax.x, coords.x);
        vmax.y = std::max(vmax.y, coords.y);
        vmax.z = std::max(vmax.z, coords.z);

        float atomRad;
        if (radiusDic.count(A->element[0]))
            atomRad = radiusDic[A->element[0]];
        else
            atomRad = radiusDic['X'];
        *maxAtom = std::max(*maxAtom, atomRad);
        N++;
        A = A->next;
    }
    *minVal = vmin;
    *maxVal = vmax;
    return N;
}


unsigned int getMinMax(pdb *P, float3 *minVal, float3 *maxVal, float *maxAtom) {
    atom *A = NULL;
    unsigned int N = 0;
    chain *C = NULL;
    *maxAtom = 0.0f;
    float3 vmin, vmax, coords;

    vmin.x = vmin.y = vmin.z = 100000.0f;
    vmax.x = vmax.y = vmax.z = -100000.0f;

    for (int chainId = 0; chainId < P->size; chainId++) {
        C = &P->chains[chainId];

        A = &C->residues[0].atoms[0];

        while (A != NULL) {
            coords = A->coor;
            vmin.x = std::min(vmin.x, coords.x);
            vmin.y = std::min(vmin.y, coords.y);
            vmin.z = std::min(vmin.z, coords.z);

            vmax.x = std::max(vmax.x, coords.x);
            vmax.y = std::max(vmax.y, coords.y);
            vmax.z = std::max(vmax.z, coords.z);

            float atomRad;
            if (radiusDic.count(A->element[0]))
                atomRad = radiusDic[A->element[0]];
            else
                atomRad = radiusDic['X'];
            *maxAtom = std::max(*maxAtom, atomRad);
            N++;
            A = A->next;
        }
    }
    *minVal = vmin;
    *maxVal = vmax;
    return N;
}


void getMinMax(float3 *positions, float *radii, unsigned int N, float3 *minVal, float3 *maxVal, float *maxAtom) {
    *maxAtom = 0.0f;
    float3 vmin, vmax, coords;

    vmin.x = vmin.y = vmin.z = 100000.0f;
    vmax.x = vmax.y = vmax.z = -100000.0f;

    for (unsigned int a = 0; a < N; a++) {
        coords = positions[a];
        vmin.x = std::min(vmin.x, coords.x);
        vmin.y = std::min(vmin.y, coords.y);
        vmin.z = std::min(vmin.z, coords.z);

        vmax.x = std::max(vmax.x, coords.x);
        vmax.y = std::max(vmax.y, coords.y);
        vmax.z = std::max(vmax.z, coords.z);

        float atomRad = radii[a];
        *maxAtom = std::max(*maxAtom, atomRad);
    }
    *minVal = vmin;
    *maxVal = vmax;
}


float4 *getArrayAtomPosRad(chain *C, unsigned int N) {
    float4 *result = new float4[N];
    atom *A = NULL;
    int id = 0;
    A = &C->residues[0].atoms[0];
    float3 coords;
    while (A != NULL) {
        coords = A->coor;

        float atomRad = radiusDic[A->element[0]];
        result[id].x = coords.x;
        result[id].y = coords.y;
        result[id].z = coords.z;
        result[id].w = atomRad;
        id++;
        A = A->next;
    }

    return result;
}


float4 *getArrayAtomPosRad(pdb *P, unsigned int N) {
    chain *C = NULL;
    atom *A = NULL;
    float4 *result = new float4[N];
    // float4 *result;
    int id = 0;

    for (int chainId = 0; chainId < P->size; chainId++) {
        C = &P->chains[chainId];

        A = &C->residues[0].atoms[0];
        float3 coords;
        while (A != NULL) {
            coords = A->coor;

            float atomRad = radiusDic[A->element[0]];
            result[id].x = coords.x;
            result[id].y = coords.y;
            result[id].z = coords.z;
            result[id].w = atomRad;
            id++;
            A = A->next;
        }
    }
    return result;
}


float4 *getArrayAtomPosRad(float3 *positions, float *radii, unsigned int N) {
    float4 *result = (float4 *)malloc(sizeof(float4) * N);
    int id = 0;

    for (int a = 0; a < N; a++) {
        float3 coords = positions[a];
        float atomRad = radii[a];
        result[id].x = coords.x;
        result[id].y = coords.y;
        result[id].z = coords.z;
        result[id].w = atomRad;
        id++;
    }
    return result;
}


float computeMaxDist(float3 minVal, float3 maxVal, float maxAtomRad) {
    return std::max(maxVal.x - minVal.x, std::max(maxVal.y - minVal.y, maxVal.z - minVal.z)) + (2 * maxAtomRad) + (4 * probeRadius);
}

void writeToObj(const string &fileName, const vector<int> &meshTriSizes, const vector<int> &meshVertSizes,
                const vector<float3*> &Allvertices, const vector<int3*> &AllTriangles) {

#if MEASURETIME
    std::clock_t start = std::clock();
#endif

    FILE *fptr;
    if ((fptr = fopen(fileName.c_str(), "w")) == NULL) {
        fprintf(stderr, "Failed to open output file\n");
        exit(-1);
    }
    for (int m = 0; m < meshTriSizes.size(); m++) {
        for (int i = 0; i < meshVertSizes[m]; i++) {
            float3 vert = Allvertices[m][i];
            fprintf(fptr, "v %.3f %.3f %.3f\n", vert.x, vert.y, vert.z);
        }
    }

    fprintf(fptr, "\n");
    unsigned int cumulMesh = 0;
    for (int m = 0; m < meshTriSizes.size(); m++) {
        int ntri = meshTriSizes[m];
        for (int i = 0; i < ntri; i++) {
            if(AllTriangles[m][i].x != AllTriangles[m][i].y && AllTriangles[m][i].x != AllTriangles[m][i].z && AllTriangles[m][i].y != AllTriangles[m][i].z){
                fprintf(fptr, "f %d %d %d\n", cumulMesh + AllTriangles[m][i].y + 1, cumulMesh + AllTriangles[m][i].x + 1, cumulMesh + AllTriangles[m][i].z + 1);
            }
        }
        cumulMesh += meshVertSizes[m];
    }

    fclose(fptr);

#if MEASURETIME
    std::cerr << "Time for writting " << (std::clock() - start) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << std::endl;
#endif
}


void writeToPly(const string &fileName, std::vector<MeshData> meshes) {
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


void writeToObj(const string &fileName, const MeshData &mesh) {
#if MEASURETIME
    std::clock_t start = std::clock();
#endif

    FILE *fptr;
    if ((fptr = fopen(fileName.c_str(), "w")) == NULL) {
        fprintf(stderr, "Failed to open output file\n");
        exit(-1);
    }

    for (int i = 0; i < mesh.NVertices; i++) {
        float3 vert = mesh.vertices[i];
        fprintf(fptr, "v %.3f %.3f %.3f\n", vert.x, vert.y, vert.z);

    }

    fprintf(fptr, "\n");
    for (int i = 0; i < mesh.NTriangles; i++) {
        fprintf(fptr, "f %d %d %d\n", mesh.triangles[i].y + 1, mesh.triangles[i].x + 1, mesh.triangles[i].z + 1);
    }
    fclose(fptr);
#if MEASURETIME
    std::cerr << "Time for writting " << (std::clock() - start) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << std::endl;
#endif
}


void writeToObj(const string &fileName, std::vector<MeshData> meshes) {
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


MeshData computeMarchingCubes(int3 sliceGridSESDim, int cutMC, int sliceNbCellSES, float *cudaGridValues, uint2* vertPerCell,
                              unsigned int *compactedVoxels, int3 gridSESDim, float4 originGridSESDx, int3 offset, float4 *cudaSortedAtomPosRad,
                              int2 *cellStartEnd, int3 gridNeighborDim, float4 originGridNeighborDx, int rangeSearchRefine) {
    
    unsigned long int memAlloc = 0;
    memsetCudaUInt2 <<< (sliceNbCellSES + NBTHREADS - 1) / NBTHREADS, NBTHREADS >>> (vertPerCell, make_uint2(0, 0), sliceNbCellSES);

    MeshData result;
    float iso = 0.0f;
    dim3 localWorkSize(cutMC, cutMC, cutMC);
    dim3 globalWorkSize((sliceGridSESDim.x + cutMC - 1) / cutMC, (sliceGridSESDim.y + cutMC - 1) / cutMC, (sliceGridSESDim.z + cutMC - 1) / cutMC);


    countVertexPerCell <<< globalWorkSize , localWorkSize >>>(iso, sliceGridSESDim, cudaGridValues, vertPerCell, rangeSearchRefine, offset);
    gpuErrchk( cudaPeekAtLastError() );

    uint2 lastElement, lastScanElement;
    gpuErrchk(cudaMemcpy((void *) &lastElement, (void *)(vertPerCell + sliceNbCellSES - 1), sizeof(uint2), cudaMemcpyDeviceToHost));

    thrust::exclusive_scan(thrust::device_ptr<uint2>(vertPerCell),
                           thrust::device_ptr<uint2>(vertPerCell + sliceNbCellSES),
                           thrust::device_ptr<uint2>(vertPerCell),
                           make_uint2(0, 0), add_uint2());

    gpuErrchk(cudaMemcpy((void *) &lastScanElement, (void *) (vertPerCell + sliceNbCellSES - 1), sizeof(uint2), cudaMemcpyDeviceToHost));

    unsigned int totalVoxels = lastElement.y + lastScanElement.y;
    unsigned int totalVerts = lastElement.x + lastScanElement.x;

    float3 *cudaVertices;
    gpuErrchk(cudaMalloc(&cudaVertices, sizeof(float3) * totalVerts));
    memAlloc += sizeof(float3) * totalVerts;

    globalWorkSize = dim3( (sliceGridSESDim.x + localWorkSize.x - 1) / localWorkSize.x, (sliceGridSESDim.y + localWorkSize.y - 1) / localWorkSize.y, (sliceGridSESDim.z + localWorkSize.z - 1) / localWorkSize.z );

    compactVoxels <<< globalWorkSize, localWorkSize>>>(compactedVoxels, vertPerCell, lastElement.y, sliceNbCellSES, sliceNbCellSES + 1, sliceGridSESDim, rangeSearchRefine, offset);
    gpuErrchk( cudaPeekAtLastError() );

    unsigned int totalVoxsqr3 = (unsigned int )ceil((totalVoxels + NBTHREADS - 1) / NBTHREADS);
    globalWorkSize = dim3(totalVoxsqr3, 1, 1);
    if (totalVoxsqr3 == 0) {
        return result;
    }

    generateTriangleVerticesSMEM <<< globalWorkSize, NBTHREADS>>>(cudaVertices, compactedVoxels, vertPerCell, cudaGridValues, originGridSESDx,
            iso, totalVoxels, totalVerts - 3, sliceGridSESDim, offset);

    gpuErrchk( cudaPeekAtLastError() );


    //Weld vertices
    float3 *vertOri;
    int *cudaTri;
    int *cudaAtomIdPerVert;

    int global = (unsigned int )ceil((totalVerts + NBTHREADS - 1) / NBTHREADS);
    groupVertices <<< global, NBTHREADS >>>(cudaVertices, totalVerts, EPSILON);
    gpuErrchk( cudaPeekAtLastError() );

    gpuErrchk(cudaMalloc(&vertOri, sizeof(float3) * totalVerts));
    gpuErrchk(cudaMemcpy(vertOri, cudaVertices, sizeof(float3) * totalVerts, cudaMemcpyDeviceToDevice));
    gpuErrchk(cudaMalloc(&cudaTri, sizeof(int) * totalVerts));

    memAlloc += sizeof(float3) * totalVerts;
    memAlloc += sizeof(int) * totalVerts;
    

    thrust::device_ptr<float3> vertThrust(cudaVertices);
    thrust::sort(vertThrust, vertThrust + totalVerts, sort_float3());

    thrust::device_ptr<float3> last = thrust::unique(vertThrust, vertThrust + totalVerts, samefloat3());

    unsigned int newtotalVerts = last - vertThrust;

    thrust::device_ptr<float3> vertOriThrust(vertOri);
    thrust::device_ptr<int> triThrust(cudaTri);
    thrust::lower_bound(vertThrust, last, vertOriThrust, vertOriThrust + totalVerts, triThrust, lessf3<float3>());
    gpuErrchk( cudaPeekAtLastError() );

    gpuErrchk(cudaMalloc(&cudaAtomIdPerVert, sizeof(int) * newtotalVerts));
    memAlloc += sizeof(int) * newtotalVerts;

    global = (unsigned int )ceil((newtotalVerts + NBTHREADS - 1) / NBTHREADS);

    //Look for atoms around vertices => could be done a way smarter way during the MC step
    closestAtomPerVertex<<<global, NBTHREADS >>>(cudaAtomIdPerVert, cudaVertices, newtotalVerts, gridNeighborDim,
                                    originGridNeighborDx, originGridSESDx, cellStartEnd, cudaSortedAtomPosRad);

    gpuErrchk( cudaPeekAtLastError() );

#if DEBUG_MODE
    cerr << "MC allocation = "<< memAlloc / 1000000.0f << " Mo" << endl;
#endif

    int Ntriangles = totalVerts / 3;

    result.vertices = (float3 *) malloc(sizeof(float3) * newtotalVerts);
    result.triangles = (int3 *) malloc(sizeof(int3) * Ntriangles);
    result.atomIdPerVert = (int *) malloc(sizeof(int) * newtotalVerts);
    result.NVertices = newtotalVerts;
    result.NTriangles = Ntriangles;

    int *tmpTri = (int *)malloc(sizeof(int) * totalVerts);

    gpuErrchk(cudaMemcpy(result.vertices, cudaVertices, sizeof(float3)*newtotalVerts, cudaMemcpyDeviceToHost));
    gpuErrchk(cudaMemcpy(result.atomIdPerVert, cudaAtomIdPerVert, sizeof(int) * newtotalVerts, cudaMemcpyDeviceToHost));
    gpuErrchk(cudaMemcpy(tmpTri, cudaTri, sizeof(int)*totalVerts, cudaMemcpyDeviceToHost));

    //Store the triangle in a 3d vector
    for (int i = 0; i < Ntriangles; i++) {
        result.triangles[i].x = tmpTri[i * 3 + 0];
        result.triangles[i].y = tmpTri[i * 3 + 1];
        result.triangles[i].z = tmpTri[i * 3 + 2];
    }
    free(tmpTri);

    gpuErrchk(cudaFree(cudaVertices));
    gpuErrchk(cudaFree(vertOri));
    gpuErrchk(cudaFree(cudaTri));
    gpuErrchk(cudaFree(cudaAtomIdPerVert));

    return result;
}


std::vector<MeshData> computeSlicedSES(float3 positions[], float radii[], unsigned int N, float resoSES, int doSmoothing = 1) {
#if MEASURETIME
    std::clock_t startSES = std::clock();
#endif

    //Record a mesh per slice
    std::vector<MeshData> resultMeshes;
    float3 minVal, maxVal;
    float maxAtomRad = 0.0;

    getMinMax(positions, radii, N, &minVal, &maxVal, &maxAtomRad);

    if (N <= 1) {
        cerr << "Failed to parse the PDB or empty PDB file" << endl;
        return resultMeshes;
    }

    float4 *atomPosRad = getArrayAtomPosRad(positions, radii, N);
    float maxDist = computeMaxDist(minVal, maxVal, maxAtomRad);

    gridResolutionNeighbor = probeRadius + maxAtomRad;

    //Grid is a cube
    float3 originGridNeighbor = {
        minVal.x - maxAtomRad - 2 * probeRadius,
        minVal.y - maxAtomRad - 2 * probeRadius,
        minVal.z - maxAtomRad - 2 * probeRadius
    };

    int gridNeighborSize = (int)ceil(maxDist / gridResolutionNeighbor);

    int3 gridNeighborDim = {gridNeighborSize, gridNeighborSize, gridNeighborSize};

    int gridSESSize = (int)ceil(maxDist / resoSES);

    int3 gridSESDim = {gridSESSize, gridSESSize, gridSESSize};

    float4 originGridNeighborDx = {
        originGridNeighbor.x,
        originGridNeighbor.y,
        originGridNeighbor.z,
        gridResolutionNeighbor
    };

    float4 originGridSESDx = {
        originGridNeighborDx.x,
        originGridNeighborDx.y,
        originGridNeighborDx.z,
        resoSES
    };

    unsigned int nbcellsNeighbor = gridNeighborDim.x * gridNeighborDim.y * gridNeighborDim.z;
    // unsigned int nbcellsSES = gridSESDim.x * gridSESDim.y * gridSESDim.z;

    float4 *cudaAtomPosRad;
    float4 *cudaSortedAtomPosRad;
    int2 *cudaHashIndex;
    int2 *cellStartEnd;
    float *cudaGridValues;
    int *cudaFillCheck;

    //Marching cubes data
    uint2* vertPerCell;
    unsigned int *compactedVoxels;

    gpuErrchk(cudaMalloc((void **)&cudaAtomPosRad , sizeof(float4) * N));
    gpuErrchk(cudaMalloc((void **)&cudaSortedAtomPosRad , sizeof(float4) * N));
    gpuErrchk(cudaMalloc((void **)&cudaHashIndex, sizeof(int2) * N));
    gpuErrchk(cudaMalloc((void**)&cellStartEnd, sizeof(int2) * nbcellsNeighbor));

    //-------------- Step 1 : Insert atoms in neighbor cells -----------------

    //Copy atom positions and radii to GPU
    gpuErrchk(cudaMemcpy(cudaAtomPosRad, atomPosRad, sizeof(float4) * N, cudaMemcpyHostToDevice));

    //Compute atom cell ids
    hashAtoms <<< N, NBTHREADS >>>(N, cudaAtomPosRad, gridNeighborDim, originGridNeighborDx, cudaHashIndex, N);

    gpuErrchk( cudaPeekAtLastError() );

    //Sort atoms cell id
    compare_int2 cmp;
    thrust::device_ptr<int2> D_beg = thrust::device_pointer_cast(cudaHashIndex);
    thrust::sort(D_beg, D_beg + N, cmp);
    gpuErrchk( cudaPeekAtLastError() );

    memsetCudaInt2 <<< (nbcellsNeighbor + NBTHREADS - 1) / NBTHREADS, NBTHREADS >>> (cellStartEnd, make_int2(EMPTYCELL, EMPTYCELL), nbcellsNeighbor);

    //Reorder atoms positions and radii and fill cellStartEnd
    sortCell <<< N , NBTHREADS>>>(N, cudaAtomPosRad, cudaHashIndex, cudaSortedAtomPosRad, cellStartEnd);

    gpuErrchk( cudaPeekAtLastError() );
    gpuErrchk( cudaFree(cudaAtomPosRad) );


    //-------------- Step 2 : Compute points of the grid outside or inside the surface -----------------
    //Use slices of the grid to avoid allocating large amount of data
    int rangeSearchRefine = (int)ceil(PROBERADIUS / resoSES);
    int sliceSmallSize = min(SLICE , gridSESSize);
    int sliceSize = min(SLICE + 2 * rangeSearchRefine, gridSESSize);
    // int sliceSmallNbCellSES = sliceSmallSize * sliceSmallSize * sliceSmallSize;
    int sliceNbCellSES = sliceSize * sliceSize * sliceSize;
    // int3 sliceGridSESDim = make_int3(sliceSmallSize, sliceSmallSize, sliceSmallSize);
    int3 fullSliceGridSESDim = make_int3(sliceSize, sliceSize, sliceSize);

    gpuErrchk(cudaMalloc((void **)&cudaGridValues, sizeof(float) * sliceNbCellSES));
    gpuErrchk(cudaMalloc((void **)&cudaFillCheck, sizeof(int) * sliceNbCellSES));

    gpuErrchk( cudaMalloc(&vertPerCell, sizeof(uint2) * sliceNbCellSES) );
    gpuErrchk( cudaMalloc(&compactedVoxels, sizeof(unsigned int) * sliceNbCellSES) );

    gpuErrchk( cudaPeekAtLastError() );

#if DEBUG_MODE
    cerr << "#atoms : "<<N<<endl;
    cerr << "Allocating " << (( (sizeof(int) + sizeof(float)) * sliceNbCellSES + 3 * sizeof(int) * sliceNbCellSES) +  2 * sizeof(float4) * N +
                            sizeof(int2) * N + sizeof(int2) * nbcellsNeighbor )/ 1000000.0f << " Mo" << endl;
    cerr << "Full size grid = " << gridSESSize << " x " << gridSESSize << " x " << gridSESSize << endl;
#endif

    int3 offset = {0, 0, 0};
    int cut = 8;

    for (int i = 0; i < gridSESSize; i += sliceSmallSize) {
        offset.x = i;
        for (int j = 0; j < gridSESSize; j += sliceSmallSize) {
            offset.y = j;
            for (int k = 0; k < gridSESSize; k += sliceSmallSize) {
                offset.z = k;
                // cerr << "-----------------------------\nStarting : " << offset.x << " / " << offset.y << " / " << offset.z << endl;

                memsetCudaFloat <<< (sliceNbCellSES + NBTHREADS - 1) / NBTHREADS, NBTHREADS >>> (cudaGridValues, probeRadius, sliceNbCellSES);
                memsetCudaInt <<< (sliceNbCellSES + NBTHREADS - 1) / NBTHREADS, NBTHREADS >>> (cudaFillCheck, EMPTYCELL, sliceNbCellSES);

                dim3 localWorkSize(cut, cut, cut);
                // dim3 globalWorkSize((sliceSmallSize + cut - 1) / cut, (sliceSmallSize + cut - 1) / cut, (sliceSmallSize + cut - 1) / cut);
                dim3 globalWorkSize((sliceSize + cut - 1) / cut, (sliceSize + cut - 1) / cut, (sliceSize + cut - 1) / cut);

                int3 reducedOffset = make_int3(max(0, offset.x - rangeSearchRefine),
                                               max(0, offset.y - rangeSearchRefine),
                                               max(0, offset.z - rangeSearchRefine));

                probeIntersection <<< globalWorkSize, localWorkSize >>>(cudaFillCheck, cudaHashIndex, gridNeighborDim, originGridNeighborDx,
                        gridSESDim, fullSliceGridSESDim, originGridSESDx, cellStartEnd,
                        cudaSortedAtomPosRad, cudaGridValues, /*offset*/ reducedOffset, N, sliceNbCellSES);


                gpuErrchk( cudaPeekAtLastError() );
                gpuErrchk( cudaDeviceSynchronize() );

                //Count cells at the border, cells that will be used in the refinement step
                thrust::device_ptr<int> fillThrust(cudaFillCheck);
                thrust::sort(fillThrust, fillThrust + sliceNbCellSES);

                unsigned int notEmptyCells = thrust::count_if(thrust::device, fillThrust, fillThrust + sliceNbCellSES, is_notempty());


                if (notEmptyCells == 0) {
                    // cerr << "Empty cells !!!" << endl;
                    continue;
                }

                localWorkSize = dim3(NBTHREADS, 1.0f,  1.0f);

                //Too long execution of this kernel triggers the watchdog timer => cut it
                int tranche = min(notEmptyCells, 65536 / 8 * NBTHREADS);

                const int nbStream = 4;
                cudaStream_t streams[nbStream];
                for (int i = 0; i < nbStream; i++)
                    cudaStreamCreate(&(streams[i]));
                int idStream = 0;

                for (unsigned int o = 0; o < notEmptyCells; o += tranche) {

                    globalWorkSize = dim3((tranche + NBTHREADS - 1) / NBTHREADS, 1.0f, 1.0f);
                    // cerr <<o<< " Launch (" << globalWorkSize.x << ", "<<globalWorkSize.y<<", "<<globalWorkSize.z<<") x ("<<localWorkSize.x<<", "<<localWorkSize.y<<", 1.0)" << endl;

                    distanceFieldRefine <<< globalWorkSize, localWorkSize, 0, streams[idStream]>>> (cudaFillCheck, cudaHashIndex, gridNeighborDim, originGridNeighborDx,
                            gridSESDim, fullSliceGridSESDim, originGridSESDx, cellStartEnd,
                            cudaSortedAtomPosRad, cudaGridValues, N, notEmptyCells, reducedOffset, o);

                    idStream++;
                    if (idStream == nbStream)
                        idStream = 0;
                }

                gpuErrchk( cudaPeekAtLastError() );
                gpuErrchk( cudaDeviceSynchronize() );
                for (int i = 0; i < nbStream; i++)
                    cudaStreamDestroy(streams[i]);
                //Reset grid values that are outside of the slice
                //Marching cubes
                MeshData mesh = computeMarchingCubes(fullSliceGridSESDim, cut, sliceNbCellSES, cudaGridValues,
                                                     vertPerCell, compactedVoxels, gridSESDim, originGridSESDx, reducedOffset,
                                                     cudaSortedAtomPosRad, cellStartEnd, gridNeighborDim, originGridNeighborDx, rangeSearchRefine);

                smoothMeshLaplacian(doSmoothing, mesh);
                resultMeshes.push_back(mesh);
            }
        }
    }

    cudaFree(cudaSortedAtomPosRad);
    cudaFree(cudaHashIndex);
    cudaFree(cellStartEnd);
    cudaFree(cudaGridValues);
    cudaFree(cudaFillCheck);
    cudaFree(vertPerCell);
    cudaFree(compactedVoxels);

    free(atomPosRad);

#if MEASURETIME
    std::cout << "Time Measure: " << MEASURETIME << " ";
    std::cerr << "Time for computing SES " << (std::clock() - startSES) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << std::endl;
#endif
    return resultMeshes;
}


extern "C"{
    int NTriangles;
    int NVertices;
    int *globalTriangles;
    float3 *globalVertices;
    int *globalIdAtomPerVert;
}


API void API_computeSES(float resoSES, float3 *atomPos, float *atomRad, unsigned int N, float3 *out_vertices,
    unsigned int *NVert, int *out_triangles, unsigned int *NTri, int doSmoothing) {
    *NVert = 0;
    *NTri = 0;
    std::vector<MeshData> resultMeshes = computeSlicedSES(atomPos, atomRad, N, resoSES, doSmoothing);

    unsigned int totalVerts = 0;
    unsigned int totalTris = 0;

    for (int i = 0; i < resultMeshes.size(); i++) {
        totalVerts += resultMeshes[i].NVertices;
        totalTris += resultMeshes[i].NTriangles*3;
    }
    globalVertices = (float3 *)malloc(sizeof(float3) * totalVerts);
    globalTriangles = (int *)malloc(sizeof(int) * totalTris);
    globalIdAtomPerVert = (int *)malloc(sizeof(int) * totalVerts);

    unsigned int cumulVert = 0;
    unsigned int curIdV = 0;
    unsigned int curIdT = 0;

    for (int i = 0;i < resultMeshes.size(); i++) {
        for (int v = 0; v < resultMeshes[i].NVertices; v++) {
            globalVertices[curIdV] = resultMeshes[i].vertices[v];
            globalIdAtomPerVert[curIdV] = resultMeshes[i].atomIdPerVert[v];
            curIdV++;
        }
        for(int t = 0; t < resultMeshes[i].NTriangles; t++){
            globalTriangles[curIdT++] = resultMeshes[i].triangles[t].x + cumulVert;
            globalTriangles[curIdT++] = resultMeshes[i].triangles[t].y + cumulVert;
            globalTriangles[curIdT++] = resultMeshes[i].triangles[t].z + cumulVert;
        }
        cumulVert += resultMeshes[i].NVertices;
    }

    *NVert = totalVerts;
    *NTri = totalTris;
    NTriangles = totalTris;
    NVertices = totalVerts;
}


extern "C"{
    API int *API_getTriangles(bool invertTriangles = false){
        if(invertTriangles){
            for(unsigned int t = 0; t < NTriangles / 3; t++){
                int save = globalTriangles[t * 3];
                globalTriangles[t * 3] = globalTriangles[t * 3 + 1];
                globalTriangles[t * 3 + 1] = save;
            }
        }
        return globalTriangles;
    }
    API float3 *API_getVertices(){
        return globalVertices;
    }
    API int *API_getAtomIdPerVert(){
        return globalIdAtomPerVert;
    }

    API void API_freeMesh() {
        free(globalVertices);
        free(globalTriangles);
        free(globalIdAtomPerVert);
    }
}


int main(int argc, const char * argv[]) {
    args::ArgumentParser parser("QuickSES, SES mesh generation using GPU", "");
    args::Group groupMandatory(parser, "", args::Group::Validators::All);
    args::Group groupOptional(parser,  "", args::Group::Validators::DontCare);
    args::ValueFlag<string> inFile(groupMandatory, "input.pdb", "Input PDB file", {'i'});
    args::ValueFlag<string> outFile(groupMandatory, "output.obj", "Output OBJ mesh file", {'o'});
    args::ValueFlag<int> smoothTimes(groupOptional, "smooth factor", "(1) Times to run Laplacian smoothing step.", {'l'});
    args::ValueFlag<float> voxelSize(groupOptional, "voxel size", "(0.5) Voxel size in Angstrom. Defines the quality of the mesh.", {'v'});
    args::ValueFlag<int> slice(groupOptional, "slice size", "(300) Size of the sub-grid. Defines the quantity of GPU memory needed.", {'s'});
    args::HelpFlag help(groupOptional, "help", "   Display this help menu", {'h', "help"});

    try {
        parser.ParseCLI(argc, argv);
    }
    catch (args::Help) {
        std::cerr << parser;
        return 0;
    }
    catch (args::ParseError e) {
        std::cerr << e.what() << std::endl;
        std::cerr << parser;
        return -1;
    }
    catch (args::ValidationError e) {
        // std::cerr << e.what() << std::endl;
        std::cerr << "Usage: " << parser;
        return -1;
    }

    if (inFile) { inputFilePath = args::get(inFile); }
    if (outFile) { outputFilePath = args::get(outFile); }
    if (smoothTimes) { laplacianSmoothSteps = args::get(smoothTimes); }
    if (voxelSize) { gridResolutionSES = args::get(voxelSize); }
    if (slice) {SLICE = args::get(slice); }

    std::clock_t startparse = std::clock();

    initRadiusDic();

    pdb *P;
    P = initPDB();

    parsePDB((char *)inputFilePath.c_str(), P, (char *)"");

    cerr << "Grid resolution = " << gridResolutionSES << endl;
    std::cerr << "Time for parse " << (std::clock() - startparse) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << std::endl;

    unsigned int N = 0;
    std::vector<float3> atomPos;
    std::vector<float> atomRadii;

    atom *A = NULL;
    chain *C = NULL;

    for (int chainId = 0; chainId < P->size; chainId++) {
        C = &P->chains[chainId];
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

    std::vector<MeshData> resultMeshes = computeSlicedSES(&atomPos[0], &atomRadii[0], N, gridResolutionSES, laplacianSmoothSteps);
    // std::vector<MeshData> resultMeshes = computeSlicedSESCPU(P);

    //Write to OBJ
    writeToObj(outputFilePath, resultMeshes);
    // writeToPly(outputFilePath, resultMeshes);
    freePDB(P);
    return 0;
}

std::vector<MeshData> get_mesh_by_xyzr(float *ptr, int N, int M, float grid_spacing, int smooth_steps, int slice_size){
  std::vector<float3> atomPos;
  std::vector<float> atomRadii;
  for (int i = 0; i < N; i++){
    atomPos.push_back(make_float3(ptr[i*M], ptr[i*M+1], ptr[i*M+2]));
    atomRadii.push_back(ptr[i*M+3]);
  }
  SLICE = slice_size;
  std::vector<MeshData> resultMeshes = computeSlicedSES(&atomPos[0], &atomRadii[0], N, grid_spacing, smooth_steps);
  return resultMeshes;
}
