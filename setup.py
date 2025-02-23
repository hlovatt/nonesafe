import setuptools

import nonesafe


def read_text(file_name: str) -> str:
    with open(file_name, "r") as fh:
        return fh.read()


setuptools.setup(
    name="nonesafe",
    version="0.1.6",
    url=nonesafe.__repository__,
    license="MIT License",  # Can only have one line `license`; setuptools bug.
    author=nonesafe.__author__,
    author_email="howard.lovatt@gmail.com",
    description="``nonesafe``: safe to read, write, and read/modify/write ``dicts`` from external data",
    long_description=read_text("README.rst"),
    long_description_content_type="text/x-rst",
    py_modules=["nonesafe"],
    platforms=["any"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
