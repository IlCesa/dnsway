import setuptools
from os import path


dir = path.abspath(path.dirname(__file__))
with open(path.join(dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
   name='dnsway',
   version='1.0.3',
   description='A Simple Implementation of the RFC1035 DNS Memo.',
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='Giovanni Cesarano',
   author_email='giovanni.cesarano99@gmail.com',
   url='https://github.com/IlCesa',
   packages=setuptools.find_packages(exclude="tests"), 
   license='MIT',
   install_requires=[], #external packages as dependencies
   platforms=["any"],
   python_requires=">=3.8"
)