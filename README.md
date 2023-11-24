# SiESTA

This tool utilizes CUDA for GPU-based computation of molecular Solvent Excluded Surface meshes. 
It features a 3D uniform grid for constant-time access to atom neighbors and incorporates a CUDA-implemented Marching Cubes algorithm, as well as a GPU-based method for welding mesh vertices.

This repository is developed based on [QuickSES](https://github.com/nezix/QuickSES) with an extra Python API.

[//]: # (and some bug fixes.)
[//]: # (## Example)
[//]: # (```bash)
[//]: # ($> wget https://files.rcsb.org/download/1KX2.pdb)
[//]: # ($> ./QuickSES -i 1KX2.pdb -o 1KX2_Surface.obj -v 0.2)
[//]: # (```)

## Usage

```Python
import siesta as sst

```


The default resolution is set to 0.5 Å but can be changed at runtime using -v argument.

The size of the slice that defines how much memory QuickSES uses can be changed using -s argument.

The tool can also be used as a library by sending an array of positions and an array of radius per atom (see API_* functions).

## Installation
To successfully compile SiESTA, nvcc is required from the NVIDIA CUDA toolkit.  

This will call  to create a QuickSES executable and its python API.

```bash
$> git clone https://github.com/miemiemmmm/QuickSES.git
$> cd QuickSES
$> bash install.sh 
```

## Useful links
[Original QuickSES repository](https://github.com/nezix/QuickSES)

[Cite QuickSES](https://hal.archives-ouvertes.fr/hal-02370900/document)

[Algorithm implemented in QuickSES](https://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.100/institut/Papers/viscom/2017/hermosilla17ses.pdf)

[Parsing PDB files](https://github.com/vegadj/cpdb)

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
