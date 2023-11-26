from setuptools import setup, find_packages
from setuptools.command.install import install
import sys, os, subprocess, shutil, time, glob

class CustomInstall(install):
	def run(self):
		print("---->> Compiling QuickSES and siesta.so...")
		# List files in current directory
		subprocess.check_call(["ls", "-lrt"])
		subprocess.check_call(["find", "siesta"])
		subprocess.check_call(["find", "build"])
		print("---->> Running make in the current directory")
		subprocess.check_call(["pwd"])
		subprocess.check_call(["make", "QuickSES", "siesta.so"])


		cwd = os.getcwd()
		shutil.copy2("siesta.so", os.path.join(cwd, "build/lib/siesta/"))
# 		matching_dirs = glob.glob(os.path.join(cwd, "build/scripts*/"))
# 		print("---->> Matching dirs: ", matching_dirs)
		shutil.copy2("QuickSES", "build/lib/siesta/")

		subprocess.check_call(["ls", "-lrt"])
		subprocess.check_call(["find", "siesta"])
		subprocess.check_call(["find", "build"])

		super().run()


setup(
	cmdclass={'install': CustomInstall},
	packages=find_packages(),
	package_data={"siesta": ['siesta/siesta.so']},
# 	scripts=['QuickSES'],
# 	entry_points = {
# 		'console_scripts': ['QuickSES=siesta.scripts.run_QuickSES:parse'],
# 	},
	zip_safe=False,
)


# 		shutil.copy2("siesta.so", os.path.join(cwd, "build/lib/siesta/"))
# 		shutil.copy2("QuickSES", os.path.join(cwd, "build/lib/siesta/"))