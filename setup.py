from pathlib import Path
from setuptools import setup

README = (Path(__file__).parent / 'README.md').read_text()

setup(
    name='code-writer',
    version='1.0.1',
    description='Library with convenience functions for generating code.',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Ken Elkabany',
    author_email='ken@elkabany.com',
    license='MIT',
    url='https://www.github.com/braincore/code-writer',
    packages=['code_writer'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Code Generators',
    ],
)
