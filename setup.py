from setuptools import setup, find_packages

setup(
    name="f1-fantasy",
    version="0.1.0",
    packages=find_packages(include=['f1_fantasy', 'f1_fantasy.*']),
    include_package_data=True,
    install_requires=[
        'flask>=3.1.1',
        'flask-security>=5.6.2',
        'flask-sqlalchemy>=3.1.1',
        'flask-migrate>=4.1.0',
        'flask-mailman>=1.1.1',
        'flask-wtf>=1.2.2',
        'fastf1>=3.5.3',
        'pandas>=2.2.3',
        'python-dotenv>=1.1.0',
        'gunicorn>=23.0.0',
    ],
    python_requires='>=3.11',
)

# The rest of the setup.py content (init_db function etc.) should be moved to a separate script
# or kept as is if it's only used for manual setup 