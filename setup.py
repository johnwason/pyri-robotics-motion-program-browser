from setuptools import setup, find_packages, find_namespace_packages

setup(
    name='pyri-robotics-motion-program-browser',
    version='0.1.0',
    description='PyRI Teach Pendant WebUI Browser Robotics Motion Program',
    author='John Wason',
    author_email='wason@wasontech.com',
    url='http://pyri.tech',
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    include_package_data=True,
    package_data = {
        'pyri.robotics_motion_program_browser.panels': ['*.html'],
        'pyri.robotics_motion_program_browser.dialogs': ['*.html']
    },
    zip_safe=False,
    install_requires=[
        'pyri-common',        
        'importlib-resources',        
    ],
    entry_points = {
        'pyri.plugins.webui_browser_panel': ['pyri-robotics-motion-program-browser=pyri.robotics_motion_program_browser.panels.robotics_mp_panels:get_webui_browser_panel_factory'],
        'pyri.plugins.webui_browser_variable_dialog': ['pyri-robotics-motion-program-browser=pyri.robotics_motion_program_browser.dialogs.robotics_mp_variable_dialogs:get_webui_browser_variable_dialog_factory']
    }
)