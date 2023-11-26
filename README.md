# SiESTA-Surf

<img src="SiEST-Surf_LOGO.png" style="">

<h1 style="color:red">
NOTE: This repository is still under construction. Please use it with caution.
</h1>

This tool utilizes CUDA for GPU-based computation of molecular Solvent Excluded Surface meshes. 
It features a 3D uniform grid for constant-time access to atom neighbors and incorporates a CUDA-implemented Marching Cubes algorithm, as well as a GPU-based method for welding mesh vertices.

This repository is developed based on [QuickSES](https://github.com/nezix/QuickSES) with an extra Python API.

[//]: # (and some bug fixes.)
[//]: # (## Example)
[//]: # (```bash)
[//]: # ($> wget https://files.rcsb.org/download/1KX2.pdb)
[//]: # ($> ./QuickSES -i 1KX2.pdb -o 1KX2_Surface.obj -v 0.2)
[//]: # (```)


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
$> make clean && make QuickSES siesta.so 
```


## Quick test
```bash
$> wget https://files.rcsb.org/download/4bso.pdb
$> python3 -c """import siesta; 
xyzr = siesta.pdb_to_xyzr('4bso.pdb'); 
print('Convert PDB to XYZR: ', xyzr.shape);
ply_str = siesta.pdb_to_ply_string('4bso.pdb'); 
print('Convert PDB to PLY string: ', ply_str);
"""
```

## Usage

```Python
import siesta as sst

```


The default resolution is set to 0.5 Å but can be changed at runtime using -v argument.

The size of the slice that defines how much memory QuickSES uses can be changed using -s argument.

The tool can also be used as a library by sending an array of positions and an array of radius per atom (see API_* functions).



## Useful links
[Original QuickSES repository](https://github.com/nezix/QuickSES)

[Cite QuickSES](https://hal.archives-ouvertes.fr/hal-02370900/document)

[Algorithm implemented in QuickSES](https://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.100/institut/Papers/viscom/2017/hermosilla17ses.pdf)

[Parsing PDB files](https://github.com/vegadj/cpdb)

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
