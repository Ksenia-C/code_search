from setuptools import setup, find_packages

setup(
    name='codesearch',
    version='0.1.0',
    packages=find_packages(include='codesearch'),
    include_package_data=True,
    install_requires=[
        'Cython>=0.29.15',
        'joblib>=0.14.1',
        'Pygments>=2.5.2',
        'PyStemmer>=1.3.0',
        'tqdm>=4.43.0',
        'tree_sitter>=0.2.1',
        'Click>=8.0.3',
        'elasticsearch==7.16.3',
        'pandas>=1.4.0',
        'cytoolz>=0.10.1',
        'pyarrow>=6.0.1',
        'python-dotenv>=0.19.2'
    ],
    entry_points={
        'console_scripts': [
            'cs = codesearch.cmd.run:cs',
        ],
    },
)