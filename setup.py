from setuptools import setup, find_packages, find_namespace_packages

setup(
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    include_package_data=True,
    package_data = {
        'pyri.robotics_motion_program_browser.panels': ['*.html'],
        'pyri.robotics_motion_program_browser.components': ['*.html']
    },
    zip_safe=False
)