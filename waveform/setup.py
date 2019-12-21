from setuptools import setup, find_packages

setup(
    name='waveform',
    version='0.0.0',
    #packages=['config','deidentify','to_csv','shellscript','tests'],
    #packages=find_packages(include=['config','config/*','deidentify','deidentify.*','to_csv','shellscript','shellscript.*','tests']),
    #packages=find_packages(),
    #package_data={'config': ['configuration.cfg']},
    include_package_data=True,
    url='',
    license='MIT',
    author='Yu Pan',
    author_email='yupan@mednet.ucla.edu',
    description='',
    # Dependent packages (distributions)
    install_requires = [
                    "pandas",
                    "numpy",
                    "pytest",
                    "vitalfilepy",
                    #"binfilepy",
                   ],
)
