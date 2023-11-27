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

#ifndef MEASURETIME
#define MEASURETIME 1
#endif

#ifndef DEBUG_MODE
#define DEBUG_MODE 0
#endif

#define MAX_VERTICES 15


#if defined(__unix__) || defined(__linux__) || defined(__APPLE__) || defined(__MACH__)
#define OS_UNIX
#endif

#if defined(__APPLE__) || defined(__MACH__)
#define OS_OSX
#endif

#if defined(_MSC_VER)
#define OS_WINDOWS
#endif

//
// API export macro
//
#if defined(OS_OSX)
#define API __attribute__((visibility("default")))
#elif defined(OS_WINDOWS)
#define API __declspec(dllexport)
#else
#define API
#endif

#include "SmoothMesh.h"


#define gpuErrchk(ans) { gpuAssert((ans), __FILE__, __LINE__); }
inline void gpuAssert(cudaError_t code, const char *file, int line, bool abort = true)
{
    if (code != cudaSuccess)
    {
        fprintf(stderr, "GPUassert: %s %s %d\n", cudaGetErrorString(code), file, line);
        if (abort) exit(code);
    }
}

#ifndef INCLUDED_MAIN
#define INCLUDED_MAIN


std::vector<MeshData> computeSlicedSES(float3 positions[], float radii[], unsigned int N, float resoSES, int doSmoothing);
std::vector<MeshData> get_mesh_by_xyzr(float *ptr, int N, int M, float grid_spacing=0.2, int smooth_steps = 10, int slice_size = 800);
#endif

extern "C" {

    API void API_computeSES(float resoSES, float3 *atomPos, float *atomRad, unsigned int N, float3 *out_vertices,
        unsigned int *NVert, int *out_triangles, unsigned int *NTri, int doSmoothing);
    API int* API_getTriangles(bool invertTriangles);
    API float3 *API_getVertices();
    API void API_freeMesh();
    API int *API_getAtomIdPerVert();
}