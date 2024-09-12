# import siesta_src as src
from . import siesta_src as src
import numpy as np


def pdb_to_xyzr(pdb_file):
  """
  Convert pdb file to xyzr array

  Args:
    pdb_file (str): path to pdb file

  """
  return src.pdb_to_xyzr(pdb_file)

def xyzr_to_surf(xyzr, grid_size=0.5, smooth_step=0, slice_number=300):
  """
  Convert xyzr array to surface 

  Args:
    xyzr (numpy.array): xyzr array
    grid_size (float): grid size
    smooth_step (int): smooth step
    slice_number (int): slice number

  Returns:
    tuple: (vertices, faces)
  """
  xyzr = np.ascontiguousarray(xyzr, dtype=np.float32)
  return src.xyzr_to_surf(xyzr, grid_size, smooth_step, slice_number)


def pdb_to_surf(pdb_file, grid_size=0.5, smooth_step=0, slice_number=300):
  """
  Convert pdb file to surface

  Args:
    pdb_file (str): path to pdb file
    grid_size (float): grid size
    smooth_step (int): smooth step
    slice_number (int): slice number

  Returns:
    tuple: (vertices, faces)
  """
  return src.pdb_to_surf(pdb_file, grid_size, smooth_step, slice_number)

def xyzr_to_string(xyzr, output_format="ply", grid_size=0.5, smooth_step=0, slice_number=300):
  """
  Convert xyzr array to string

  Args:
    xyzr (numpy.array): xyzr array
    output_format (str): output format
    grid_size (float): grid size
    smooth_step (int): smooth step
    slice_number (int): slice number

  Returns:
    str: string
  """
  xyzr = np.ascontiguousarray(xyzr, dtype=np.float32)
  return src.xyzr_to_string(xyzr, output_format, grid_size, smooth_step, slice_number)

def pdb_to_string(pdb_file, output_format="ply", grid_size=0.5, smooth_step=0, slice_number=300):
  """
  Convert pdb file to string

  Args:
    pdb_file (str): path to pdb file
    output_format (str): output format
    grid_size (float): grid size
    smooth_step (int): smooth step
    slice_number (int): slice number

  Returns:
    str: string
  """
  return src.pdb_to_string(pdb_file, output_format, grid_size, smooth_step, slice_number)

def xyzr_to_file(xyzr, file_name, output_format="ply", grid_size=0.5, smooth_step=0, slice_number=300):
  """
  Convert xyzr array to file

  Args:
    xyzr (numpy.array): xyzr array
    file_name (str): output file name
    output_format (str): output format
    grid_size (float): grid size
    smooth_step (int): smooth step
    slice_number (int): slice number
  """
  xyzr = np.ascontiguousarray(xyzr, dtype=np.float32)
  return src.xyzr_to_file(xyzr, file_name, output_format, grid_size, smooth_step, slice_number)

def pdb_to_file(pdb_file, output_file, output_format="ply", grid_size=0.5, smooth_step=0, slice_number=300):
  """
  Convert pdb file to file

  Args:
    pdb_file (str): path to pdb file
    output_file (str): output file name
    output_format (str): output format
    grid_size (float): grid size
    smooth_step (int): smooth step
    slice_number (int): slice number
  """
  return src.pdb_to_file(pdb_file, output_file, output_format, grid_size, smooth_step, slice_number)

