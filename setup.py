"""Setup for gea XBlock."""

import os
from setuptools import setup, find_packages


def package_data(pkg, roots):
    """Generic function to find package_data.
    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))
    return {pkg: data}


setup(
    name='edx-gea',
    version='0.1',
    description='edx-gea XBlock',   # TODO: write a better description.
    author="FUN",
    url="https://github.com/openfun/edx-gea",
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'edx_gea = edx_gea:GradeExternalActivityXBlock',
        ]
    },
    package_data=package_data("edx_gea", ["static", "public", ]),
)
