#!/usr/bin/env python3
"""
Setup script for Ruckus Reboot Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ruckus-reboot",
    version="1.0.0",
    author="alekm",
    author_email="alekmurray@gmail.com",  # Add your email if desired
    description="A Python tool to SSH into Ruckus access points and reboot them",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/alekm/ruckus-reboot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ruckus-reboot=ruckus_reboot:main",
            "ruckus-test=test_connection:test_connection",
        ],
    },
    keywords="ruckus, access point, reboot, ssh, network management",
    project_urls={
        "Bug Reports": "https://github.com/alekm/ruckus-reboot/issues",
        "Source": "https://github.com/alekm/ruckus-reboot",
        "Documentation": "https://github.com/alekm/ruckus-reboot#readme",
    },
)
