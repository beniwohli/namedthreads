from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib

with open('README.md') as f:
    long_description = f.read()

setup(
    name="namedthreads",
    version="1.0",
    url="https://github.com/beniwohli/namedthreads",
    license="BSD",
    platforms=['OS Independent'],
    description="Patch to propagate Python thread names to system thread names",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Benjamin Wohlwend",
    author_email="piquadrat@gmail.com",
    install_requires=[],
    include_package_data=True,  # Accept all data files and directories matched by MANIFEST.in or found in source control.
    py_modules=["namedthreads"],
    data_files = [(get_python_lib(prefix=''), ['namedthreads-init.pth'])],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)