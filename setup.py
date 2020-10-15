import setuptools
import gymie

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gymie",
    version=gymie.__version__,
    author="Francisco Ramos",
    author_email="francisco.ramos@researchlab.ai",
    description="WebSocket server that exposes an API to train AI agents on OpenAI Gym and gym-api-like Environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jscriptcoder/Gymie-Server",
    packages=setuptools.find_packages(),
    install_requires=[
        'eventlet==0.28.0',
        'gym==0.17.3',
        'uuid==1.30',
    ],
    extras_require={
        'box2d': ['box2d-py==2.3.8'],
        'retro': ['gym-retro==0.8.0'],
        'unity': ['mlagents-envs==0.20.0', 'gym-unity==0.20.0'],
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
