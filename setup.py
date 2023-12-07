from setuptools import setup, find_packages

setup(
    name="speech_analysis",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "praat-parselmouth",
        "moviepy",
        "opencv-python",
        "pandas"
    ],
    entry_points={
        'console_scripts': [
            'speech_analysis=speech_analysis:main',
        ],
    },
    author="Mario Kuzmanov & Raúl Sánchez",
    author_email="mario.kuzmanov@student.uni-tuebingen.de & raul@um.es ",
    description="A tool to extract speech metrics from a video and save to a CSV file.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/daedalusLAB/speech_analysis",
)