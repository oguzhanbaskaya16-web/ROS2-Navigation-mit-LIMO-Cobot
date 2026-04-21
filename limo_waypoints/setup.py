from setuptools import setup

package_name = 'limo_waypoints'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='agilex',
    maintainer_email='agilex@example.com',
    description='Waypoint navigation for LIMO with Nav2',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'waypoint_navigator = limo_waypoints.waypoint_navigator:main',
            'pickplace_navigator = limo_waypoints.pickplace_navigator:main',
            # hier können später weitere nodes gespeichert werden...
        ],
    },
)