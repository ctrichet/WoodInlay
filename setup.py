#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   setup.py                                                   !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2026/02/12 22:58:57 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2026/02/12 22:58:57 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
from setuptools import setup, find_packages

setup(
    name="JediCut",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15",
        "PyMuPDF>=1.22",  # pour fitz
        "numpy>=1.23",
        "shapely>=2.0",
        "svg.path>=3.0",  # pour from svg.path import parse_path
        "scipy>=1.10",
        "svgpathtools>=1.5",  # si certaines fonctions utilisent svgpathtools
        "Pillow>=9.5",  # si image.open est utilisé
    ],
    entry_points={
        "console_scripts": [
            "jedicut=app:main",  # app.py doit avoir une fonction main()
        ],
    },
    python_requires=">=3.8",
)
