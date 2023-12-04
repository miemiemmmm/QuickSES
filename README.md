# SiESTA-Surf

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/708106751.svg)](https://zenodo.org/doi/10.5281/zenodo.10252504)

<img src="Images/SiESTA-Surf_LOGO.png" style="">



# ⚠️ NOTE: This repository is still under construction. Please use it with caution. ⚠️

SiESTA-Surf is a Python API to utilizes CUDA for GPU-based computation of molecular solvent excluded surface (SES). 
This repository is developed based on [QuickSES](https://github.com/nezix/QuickSES).
It features a 3D uniform grid for constant-time access to atom neighbors and incorporates a CUDA-implemented Marching Cubes algorithm, as well as a GPU-based method for welding mesh vertices.


## Installation
The nvcc compiler from the NVIDIA CUDA toolkit is required to successfully compile SiESTA. 
It will install the python package siesta-surf, as well as two console programs: 

**QuickSES** to output surface mesh from input PDB. 

**viewobj** to view simple structures (as ball+stick model) or objects surfaces. 

### PyPI (Will be available soon)
```bash
$ pip install siesta-surf
```

### Install from Source distribution
```bash
$ wget https://github.com/miemiemmmm/SiESTA/releases/download/v0.0.1/siesta-surf-v0.0.1.tar.gz
$ pip install -v siesta-surf-0.0.1.tar.gz 
```

### Manual installation
```bash
$ git clone https://github.com/miemiemmmm/SiESTA.git
$ cd SiESTA
$ make install 
```


## Quick test
```bash
$ wget https://files.rcsb.org/download/4bso.pdb
$ python3 -c """import siesta; 
xyzr = siesta.pdb_to_xyzr('4bso.pdb'); print('Test1: Converted PDB to XYZR array: ', type(xyzr), xyzr.shape);
siesta.pdb_to_file('4bso.pdb', '4bso_pysurf.obj', format='obj', grid_size=0.3);
print('Test2: Surface mesh saved to 4bso_pysurf.obj');
ply_str = siesta.pdb_to_string('4bso.pdb'); 
print('Test3: Generated the surface mesh string from PDB file: ', len(ply_str), [ply for ply in ply_str.split('\n') if 'element' in ply]) 
siesta.xyzr_to_file(xyzr, '4bso_pysurf.ply', format='ply', grid_size=0.25);
print('Test4: Surface mesh computed from the previously computed XYZR array saved to 4bso_pysurf.ply');
""" 
# QuickSES console program
$ QuickSES -i 4bso.pdb -o 4bso_surface.obj -v 0.2 
# viewobj console program
$ viewobj 4bso_pysurf.obj 4bso_pysurf.ply   # View the python generated surface mesh
$ viewobj 4bso_surface.obj 4bso.pdb -w 1    # View the QuickSES generated surface mesh
```


## Usage
### Python API
This API focuses on converting any structural file formats (e.g. PDB, sdf, mol2 etc.) to 3D surface triangle mesh.
You could either use the API to convert the structures to vertices and faces as numpy array.
You could also directly convert it to 3D surface triangle mesh. Currently supported object file formats are ply and obj.

Current available functions:
----------------------------------------------------------------

> #### siesta.pdb_to_xyzr(pdb_file_name:str) -> np.ndarray
Compute the xyzr array from pdb file
##### Parameters:
- pdb_file_name: str
##### Returns:
- xyzr: np.ndarray shaped (N,4)

#### The following surface generation functions accept "grid_size", "smooth_step", "slice_number" as optional arguments to control the quality of mesh.

> #### siesta.pdb_to_file(pdb_file_name:str, output_file_name:str, format:str='ply') -> None
Generate the surface to file from pdb file
##### Parameters:
- pdb_file_name: str
- output_file_name: str
- format: str, optional, default: 'ply'
##### Returns:
- None

> #### siesta.pdb_to_string(pdb_file_name:str, format:str='ply') -> str
Get the string of surface mesh from pdb file
##### Parameters:
- pdb_file_name: str
- format: str, optional, default: 'ply'
##### Returns: surface_string: str
- surface_string: str

> #### siesta.pdb_to_surf(pdb_file_name:str) -> tuple(vertices, faces)
Compute the vertices and faces from pdb file
##### Parameters:
- pdb_file_name: str
##### Returns:
- surface_tuple: tuple(vertices, faces)

> #### siesta.xyzr_to_file(np.array xyzr, str output_file_name, format:str='ply') -> None 
Generate the surface file from xyzr array
##### Parameters:
- xyzr: np.ndarray shaped (N,4)
- output_file_name: str
- format: str, optional, default: 'ply'
##### Returns:
- None

> #### siesta.xyzr_to_string(np.array xyzr, format:str='ply') -> str
Generate surface object as string from xyzr array
##### Parameters:
- xyzr: np.ndarray shaped (N,4)
- format: str, optional, default: 'ply'
##### Returns:
- surface_string: str

> #### siesta.xyzr_to_surf(np.array xyzr) -> tuple(vertices, faces)
Compute the vertices and faces from xyzr array
##### Parameters:
- xyzr: np.ndarray shaped (N,4)
##### Returns:
- surface_tuple: tuple(vertices, faces)

----------------------------------------------------------------

### QuickSES mini-program
```bash
$ QuickSES -h   # view help
$ QuickSES -i 4bso.pdb -o 4bso_surface.obj -v 0.2 
```
The default resolution is set to 0.5 Å but can be changed at runtime using -v argument. 
The size of the slice that defines how much memory QuickSES uses can be changed using -s argument.
For the other usage of QuickSES, please refer to its original repository [QuickSES](https://github.com/nezix/QuickSES).

----------------------------------------------------------------

### viewobj mini-program
If you have [Open3D](http://www.open3d.org/) installed in your python environment, you can use **viewobj** to visualize the surface mesh and some commonlu used structure files.



```bash
$ viewobj -h  # view help
$ viewobj 4bso_surface.obj -w 1    # show the surface mesh as wireframe 
```

Current supported format includes:

<table style="width: 600px">
<tr><td colspan="2" style="text-align: center; font-weight: bolder;">Structural formats</td></tr>
<tr><td>Protein Data Bank (PDB) format</td><td>.pdb</td></tr>
<tr><td>Sybyl Mol2</td><td>.mol2</td></tr>
<tr><td>MDL SDF</td><td>.sdf</td></tr>
<tr><td>Coord+Radius (XYZR)</td><td>.xyzr</td></tr>
<tr><td colspan="2" style="text-align: center; font-weight: bolder;">Mesh formats</td></tr>
<tr><td>Polygon File Format (Default output format)</td><td>.ply</td></tr>
<tr><td>Wavefront OBJ format</td><td>.obj</td></tr>
<tr><td>Object File Format</td><td>.off</td></tr>
</table>

----------------------------------------------------------------

## Acknowledgments
This project is based on [QuickSES](https://github.com/nezix/QuickSES) by [Xavier Martinez](https://github.com/nezix).
Without these open source projects, this project would not be possible.

Check these links to cite the [QuickSES](https://hal.archives-ouvertes.fr/hal-02370900/document) and the implemented GPU-based SES computation [algorithm](https://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.100/institut/Papers/viscom/2017/hermosilla17ses.pdf). 
[CPDB](https://github.com/vegadj/cpdb) is used for parsing PDB files. 

[Pybind11](https://github.com/pybind/pybind11) is used for wrapping C++/CUDA code to Python API.

The [LOGO](Images/SiESTA-Surf_LOGO.png) is designed by [DALL·E 3](https://openai.com/dall-e-3).

