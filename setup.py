"""
g_analytics_writer installation script.
"""
import os
import re
from setuptools import setup
from setuptools import find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
long_description = description = "Lightweight Google Analytics support"
with open(os.path.join(HERE, "README.rst")) as fp:
    long_description = fp.read()

# store version in the init.py
with open(os.path.join(HERE, "src", "g_analytics_writer", "__init__.py")) as v_file:
    VERSION = re.compile(r'.*__VERSION__ = "(.*?)"', re.S).match(v_file.read()).group(1)

requires = [
    "metadata_utils>=0.1.0",
    "six",
]
tests_require = [
    "pyramid",
    "webob",  # should be installed by pyramid
]
testing_extras = tests_require + [
    "pytest",
]


setup(
    name="g_analytics_writer",
    version=VERSION,
    description=description,
    long_description=long_description,
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="web pyramid google analytics",
    author="Jonathan Vanasco",
    author_email="jonathan@findmeon.com",
    url="https://github.com/jvanasco/g_analytics_writer",
    license="MIT",
    packages=find_packages(
        where="src",
    ),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=tests_require,
    extras_require={
        "testing": testing_extras,
    },
    test_suite="tests",
)
