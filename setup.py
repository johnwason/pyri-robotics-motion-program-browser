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
        'pyri.robotics_motion_program_browser.components': ['*.html']
    },
    zip_safe=False,
    install_requires=[
        'pyri-common',        
        'importlib-resources',        
    ],
    entry_points = {
        'pyri.plugins.webui_browser_panel': ['pyri-robotics-motion-program-browser=pyri.robotics_motion_program_browser.panels.robotics_mp_panels:get_webui_browser_panel_factory'],
        'pyri.plugins.webui_browser_component': ['pyri-robotics-motion-program-browser=pyri.robotics_motion_program_browser.components.robotics_mp_components:get_webui_browser_component_factory'],
        'pyri.plugins.webui_browser_plugin_init': ['pyri-robotics-motion-program-browser=pyri.robotics_motion_program_browser.robotics_mp_plugin_init:get_webui_browser_plugin_init_factory'],
    }
)