import setuptools

setuptools.setup(
    name='whatsgoingon',    
    version='0.1',
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
        'flask',
    ]
)
