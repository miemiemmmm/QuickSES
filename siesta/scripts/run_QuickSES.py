import subprocess, os, argparse


def parse_for_quickses():
	# Parse the command line arguments for QuickSES executable
	parser = argparse.ArgumentParser(description="QuickSES command line tool")
	parser.add_argument("-i", "--input", help="Input PDB file")
	parser.add_argument("-o", "--output", help="Output OBJ mesh file")
	parser.add_argument("-l", "--laplacian", default=1, type=int, help="Times to run Laplacian smoothing step")
	parser.add_argument("-v", "--voxel", default=0.5, type=float, help="Voxel size in Angstrom. Defines the quality of the mesh")
	parser.add_argument("-s", "--slice", default=300, type=int, help="Size of the sub-grid. Defines the quantity of GPU memory needed")
	parser.add_argument("-d", "--debug", default=False, type=bool, help="Print debug information")
	args = parser.parse_args()
	if not args.output.endswith(".obj"):
		raise Exception("Output file must be an OBJ file")
	return parser.parse_args()


def quickses_runner():
	# find Get the QuickSES executable in the main directory
	file_dir = os.path.dirname(os.path.realpath(__file__))
	quickses_bin = os.path.abspath(file_dir + "/../QuickSES")
	if not os.path.exists(quickses_bin):
		raise Exception("QuickSES executable not found")

	# Parse the command line arguments for QuickSES executable
	args = parse_for_quickses()
	command = [quickses_bin]
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

	# Run QuickSES
	subprocess.run(command)
	if os.path.exists(args.output):
		print(">>> QuickSES finished successfully ")
		return 1
	else:
		print(">>> QuickSES failed")
		return 0

