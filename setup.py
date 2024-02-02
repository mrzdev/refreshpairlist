import setuptools

setuptools.setup(
    name='refreshpairlist',
    version='0.0.3',
    author='mrzdev',
    description='Dynamic Pairlist for FreqAI (freqtrade)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        "requests-ratelimiter>=0.4.2",
        "schedule>=1.2.1"
    ],
    entry_points={
        'console_scripts': ['refreshpairlist = refreshpairlist.__main__:main']
    }
)
