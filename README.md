# SiESTA-Surf

<img src="SiEST-Surf_LOGO.png" style="">

<h1 style="color:red">
NOTE: This repository is still under construction. Please use it with caution.
</h1>

This tool utilizes CUDA for GPU-based computation of molecular Solvent Excluded Surface meshes. 
It features a 3D uniform grid for constant-time access to atom neighbors and incorporates a CUDA-implemented Marching Cubes algorithm, as well as a GPU-based method for welding mesh vertices.

This repository is developed based on [QuickSES](https://github.com/nezix/QuickSES) with an extra Python API.




## Installation
To successfully compile SiESTA, nvcc is required from the NVIDIA CUDA toolkit.  

This will call  to create a QuickSES executable and its python API.

### PyPI
```bash
$> pip install siesta-surf
```

### Source distribution
```bash
$> wget http://www.placeholder/for/url/to/siesta-surf-0.0.1.tar.gz
$> pip install -v siesta-surf-0.0.1.tar.gz 
```

### Manual installation
```bash
$> git clone https://github.com/miemiemmmm/SiESTA.git
$> cd SiESTA
$> make install 
```


## Quick test
```bash
$> wget https://files.rcsb.org/download/4bso.pdb
$> python3 -c """import siesta as sst; 
xyzr = sst.pdb_to_xyzr('4bso.pdb'); 
print('Convert PDB to XYZR: ', xyzr.shape);
ply_str = sst.pdb_to_ply_string('4bso.pdb'); 
print('Convert PDB to PLY string: ', ply_str);
"""
# QuickSES program
$> QuickSES -i 4bso.pdb -o 4bso_Surface.obj -v 0.2 
```


## Usage
### Python API
This API focuses on converting any structural file formats (e.g. PDB, sdf, mol2 etc.) to 3D surface triangle mesh.
You could either use the API to convert the structures to vertices and faces as numpy array.
You could also directly convert it to 3D surface triangle mesh. Currently supported object file formats are ply and obj.

```Python
import siesta as sst

```
 



### QuickSES 
```bash
$> QuickSES -h   # view help
$> QuickSES -i 4bso.pdb -o 4bso_Surface.obj -v 0.2 
```
The default resolution is set to 0.5 Å but can be changed at runtime using -v argument.
 of the slice that defines how much memory QuickSES uses can be changed using -s argument.

For the other useage of QuickSES, please see its original repository[QuickSES](https://github.com/nezix/QuickSES).

### viewobj
If you have [Open3D](http://www.open3d.org/) installed in your python environment, you can use viewobj to visualize the surface mesh or the common supported structure files.
```bash
$> viewobj 4bso_Surface.obj
```


## Useful links
[Original QuickSES repository](https://github.com/nezix/QuickSES)

[Cite QuickSES](https://hal.archives-ouvertes.fr/hal-02370900/document)

[Algorithm implemented in QuickSES](https://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.100/institut/Papers/viscom/2017/hermosilla17ses.pdf)

[Parsing PDB files](https://github.com/vegadj/cpdb)

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
