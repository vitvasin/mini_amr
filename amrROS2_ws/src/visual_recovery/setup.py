from setuptools import find_packages, setup

package_name = 'visual_recovery'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/recovery.launch.py', 'launch/relocalization_system.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='smr',
    maintainer_email='smr@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'recovery_node = visual_recovery.recovery_node:main',
        ],
    },
)
