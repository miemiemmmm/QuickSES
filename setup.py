from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
import sys
import setuptools
import subprocess
import shutil


class CustomInstall(install):
	def run(self):
		print("---->> Running custom install")
		subprocess.check_call(["make", "clean"])
		subprocess.check_call(["make", "QuickSES", "siesta.so"])
		subprocess.check_call(["pwd"])
		subprocess.check_call(["find", "."])
		cwd = os.path.abspath(os.getcwd())
		shutil.copy2("siesta.so", os.path.join(cwd, "siesta"))
		shutil.copy2("QuickSES", os.path.join(cwd, "siesta"))
		super().run()


setup(
	name='SiESTA-Surf',
	version='0.1',
	author='Yang Zhang',
	author_email='y.zhang@bioc.uzh.ch',
	description='A Python package with C++ extension',
	cmdclass={'install': CustomInstall},
	packages=['siesta'],
	package_data={"siesta": ['./siesta.so']},
	zip_safe=False,
)

