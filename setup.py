import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-uploadfield",
    version="0.0.1",
    author="Yury Lapshinov",
    author_email="y.raagin@gmail.com",
    description="Uploading files in django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raagin/django-uploadfield",
    packages=setuptools.find_packages(),
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    python_requires='>=3',
    install_requires=[
        'django-filebrowser>=3.13',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
