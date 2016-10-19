from setuptools import setup

setup(
    name='btlejuice',
    version='1.0',
    description='BtleJuice MitM framework Python bindings',
    author='Damien Cauquil',
    author_email='damien.cauquil@digitalsecurity.fr',
    license='MIT',
    packages=['btlejuice','btlejuice.socketIO_client'],
    url='https://github.com/DigitalSecurity/btlejuice-python-bindings',
    install_requires=[
        'six',
        'websocket'
    ]
)
