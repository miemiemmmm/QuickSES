import subprocess
import os
import argparse
# find Get the QuickSES executable in the main directory

def parse():
	# Parse the command line arguments for QuickSES executable
	parser = argparse.ArgumentParser(description="QuickSES command line tool")
	parser.add_argument("-i", "--input", help="Input PDB file")
	parser.add_argument("-o", "--output", help="Output OBJ mesh file")
	parser.add_argument("-l", "--laplacian", default=1, type=int, help="Times to run Laplacian smoothing step")
	parser.add_argument("-v", "--voxel", default=0.5, type=float, help="Voxel size in Angstrom. Defines the quality of the mesh")
	parser.add_argument("-s", "--slice", default=300, type=int, help="Size of the sub-grid. Defines the quantity of GPU memory needed")
 	parser.add_argument("-h", "--help", default=false, type=bool,  help="Show help message")
	args = parser.parse_args()
	return args

def run_quickses():
	file_dir = os.path.dirname(os.path.realpath(__file__))
	QuickSES = os.path.abspath(file_dir + "/../QuickSES")
	if not os.path.exists(QuickSES):
		raise Exception("QuickSES executable not found")

	args = parse()
	if args.help:
		msg = "Usage: \n QuickSES -i input.pdb -o output.obj -l 1 -v 0.5 -s 300 \n -i input.pdb: Input PDB file \n -o output.obj: Output OBJ mesh file \n -l 1: Times to run Laplacian smoothing step \n -v 0.5: Voxel size in Angstrom. Defines the quality of the mesh \n -s 300: Size of the sub-grid. Defines the quantity of GPU memory needed"
		print(msg)
		return 0

	print(args)
	command = [QuickSES]
	if args.input:
		command += ["-i", args.input]
	else:
		raise Exception("Input PDB file not specified")
	if args.output:
		command += ["-o", args.output]
	else:
		raise Exception("Output object file not specified")
	if args.laplacian:
		command += ["-l", str(args.laplacian)]
	if args.voxel:
		command += ["-v", str(args.voxel)]
	if args.slice:
		command += ["-s", str(args.slice)]
	print("Final command: ", " ".join(command))

	subprocess.run(command)
	print("###########################")
	print("QuickSES finished successfully")
	return 0

