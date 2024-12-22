import setuptools


setuptools.setup(
   name='dnsway',
   version='1.0.0',
   description='A Simple Implementation of the RFC1035 DNS Memo.',
   long_description="sciao belo",
   author='Giovanni Cesarano',
   author_email='giovanni.cesarano99@gmail.com',
   url='https://github.com/IlCesa',
   packages=setuptools.find_packages(exclude="tests"), 
   license='MIT',
   install_requires=[], #external packages as dependencies
   platforms=["any"],
   python_requires=">=3.8"
)