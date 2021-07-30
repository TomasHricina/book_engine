from setuptools import find_packages, setup

setup(
    name='book_engine',
    # packages=find_packages(),
    version='0.1.0',
    description='Book recommendation engine',
    author='Tomas Hricina',
    license='MIT',
    packages=['book_engine',
    'book_engine.data',
    'book_engine.docs',
    'book_engine.src'],
    include_package_data=True,

)
