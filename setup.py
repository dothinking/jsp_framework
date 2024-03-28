'''Setup file.'''
import os
from setuptools import find_packages, setup


EXCLUDE_FROM_PACKAGES = ["build", "dist", "test"]


def get_version(fname):
    '''Read version number from version.txt, otherwise alpha version.'''
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as f:
            version = f.readline().strip()
    else:
        version = 'alpha'
    return version


def load_long_description(fname):
    '''Load README.md for long description.'''
    with open(fname, 'r', encoding='utf-8') as f:
        long_description = f.read()
    return long_description

def load_requirements(fname):
    '''Load requirements.txt.'''
    try:
        # pip >= 10.0
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip < 10.0
        from pip.req import parse_requirements

    reqs = parse_requirements(fname, session=False)
    try:
        requirements = [str(ir.requirement) for ir in reqs]
    except AttributeError:
        requirements = [str(ir.req) for ir in reqs]

    return requirements


setup(
    name="jsp",
    version=get_version('version.txt'),
    keywords=["job-shop", "job-shop-scheduling", "job-shop-scheduling-problem"],
    description="A framework for solving job-shop scheduling problem.",
    long_description=load_long_description('README.md'),
    long_description_content_type='text/markdown',
    license="Apache License 2.0",
    author="dothinking",
    author_email="train8808@gmail.com",
    url="https://github.com/dothinking/jsp_framework",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    zip_safe=False,
    install_requires=load_requirements("requirements.txt"),
    python_requires=">=3.6"
)
