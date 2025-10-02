from setuptools import find_packages, setup

package_name = 'battery_management'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install configuration files
        ('share/' + package_name + '/config', [
            'config/battery_manager.yaml',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='emr',
    maintainer_email='vasin22315@hotmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'battery_manager_node = battery_management.battery_manager_node:main',
        ],
    },
)
