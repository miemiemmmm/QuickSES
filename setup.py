from setuptools import setup, find_packages
from setuptools.command.install import install
import sys, os, subprocess, shutil


class InstallSiESTA(install):
	def run(self):
		print("---->> Compiling QuickSES and siesta.so...")
		subprocess.check_call(["make", "QuickSES", "siesta.so"])
		cwd = os.getcwd()
		shutil.copy2("siesta.so", os.path.join(cwd, "build/lib/siesta/"))
		shutil.copy2("QuickSES", "build/lib/siesta/")
		super().run()


setup(
	cmdclass={'install': InstallSiESTA},
	packages=find_packages(),
	package_data={"siesta": ['siesta/siesta.so']},
	zip_safe=False,
)
