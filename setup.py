import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gymie",
    version="0.0.1",
    author="Francisco Ramos",
    author_email="francisco.ramos@researchlab.ai",
    description="WebSocket server that exposes an API to train AI agents on OpenAI Gym and gym-api-like Environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jscriptcoder/Gymie-Server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
