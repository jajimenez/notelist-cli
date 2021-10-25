"""Notelist CLI Setup script."""

import setuptools as st


if __name__ == "__main__":
    with open("README.md") as f:
        long_desc = f.read()

    st.setup(
        name="notelist-cli",
        version="0.1.0",
        description="Command line interface for the Notelist API",
        author="Jose A. Jimenez",
        author_email="jajimenezcarm@gmail.com",
        license="MIT",
        long_description=long_desc,
        long_description_content_type="text/markdown",
        url="https://github.com/jajimenez/notelist-cli",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "License :: OSI Approved :: MIT License"
        ],
        python_requires=">=3.9.0",
        install_requires=[
            "click==8.0.3",
            "requests==2.26.0",
            "userconf==0.4.0"
        ],
        packages=[
            "notelist_cli"
        ],
        package_dir={
            "notelist_cli": "src/notelist_cli"
        },
        entry_points={
            "console_scripts": [
                "notelist-cli=notelist_cli:main"
            ]
        }
    )
