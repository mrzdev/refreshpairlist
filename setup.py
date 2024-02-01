import setuptools

setuptools.setup(
    name='refreshpairlist',
    version='0.0.1',
    author='mrzdev',
    description='Dynamic Pairlist for FreqAI (freqtrade)',
    install_requires=[
        "requests-ratelimiter>=0.4.2",
        "schedule>=1.2.1"
    ],
    entry_points={
        'console_scripts': ['refreshpairlist = refreshpairlist.__main__:main']
    }
)
