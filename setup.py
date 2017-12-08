#!/usr/bin/env python3

"""Setup script."""

from setuptools import setup

setup(
    name="CulinaryApp",
    version="0.0.0",
    author="Dmitry Karpov, Vyacheslav Trifonov etc",
    author_email="dimakarp1996@yandex.ru",
    url="https://github.com/dimakarp1996/CulinaryApp",
    license="MIT",
    packages=[
        "CulinaryApp",
        "bs4",
        "lxml",
        "requests",
        "re",
        "urllib.request",
        "pandas",
        "os",
        "Levenshtein"
    ],
    install_requires=[
    ],
    setup_requires=[
        "pytest-runner",
        "pytest-pycodestyle",
        "pytest-cov",
    ],
    tests_require=[
        "pytest",
        "pycodestyle",
        "mock"
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'console_scripts': ['CulinaryApp=CulinaryApp.CulinaryApp:main'],
    }
)
