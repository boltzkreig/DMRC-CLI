from setuptools import setup, find_packages

setup(
        name="DMRC",
        version="1.0",
        description="A Convenient CLI-Frontend for DMRC website",
        author="Boltzkreig",
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            "requests",
            "pyfzf",
            "tcolorpy"
        ],
        entry_point={
            "console_scripts": [
                'DMRC = src.__main__ '
            ]
        },
        python_requires='>=3.10'
)
