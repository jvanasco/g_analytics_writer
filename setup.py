"""gaq_helper installation script.
"""
import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.txt")).read()
README = README.split("\n\n", 1)[0] + "\n"

requires = []

setup(name="gaq_hub",
      version="0.0.7",
      description="Lightweight Google Analytics support",
      long_description=README,
      classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pylons",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        ],
      keywords="web pylons",
      py_modules=['gaq_hub'],
      author="Jonathan Vanasco",
      author_email="jonathan@findmeon.com",
      url="https://github.com/jvanasco/gaq_hub",
      license="MIT",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      tests_require = requires,
      install_requires = requires,
      test_suite="tests",
      )

