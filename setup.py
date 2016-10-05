"""gaq_helper installation script.
"""
import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = ''
try:
    README = open(os.path.join(here, "README.md")).read()
    README = README.split("\n\n", 1)[0] + "\n"
except:
    pass

requires = [
    "metadata_utils >=0.0.2",
]

setup(
    name="gaq_hub",
    version="0.1.1",
    description="Lightweight Google Analytics support",
    long_description=README,
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pylons",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="web pylons",
    author="Jonathan Vanasco",
    author_email="jonathan@findmeon.com",
    url="https://github.com/jvanasco/gaq_hub",
    license="MIT",
    py_modules=['gaq_hub'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require = requires,
    install_requires = requires,
    test_suite="tests",
)
