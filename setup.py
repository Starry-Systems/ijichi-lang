from setuptools import setup, find_packages

setup(
    name='ijichi',
    version='1.0.0',
    description='Ijichi: A lightweight indentation-based scripting language with static typing.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'ijichi=ijichi.cli:main',  # assumes `cli.py` has a `main()` function
        ],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Interpreters',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.7',
)
