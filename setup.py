from setuptools import setup, find_packages

setup(
    name='electricity-bill-extractor',  # Replace with your project name
    version='0.1.0',  # Initial version
    author="Genzoic",  # Replace with your name
    author_email="Shreyas.joshi@genzoic.com",  # Replace with your email
    description='A tool to extract information from electricity bills in PDF format',
    #long_description=open('README.md').read(),  # Optional: Ensure you have a README.md
    #long_description_content_type='text/markdown',
    url="https://github.com/shrey-genzoic/switch_agent",  # Replace with your GitHub URL
    packages=find_packages(),  # Automatically include all sub-packages
    python_requires='>=3.6',  # Minimum Python version requirement
    install_requires=[  # List dependencies from requirements.txt
        'pdf2image',
        'opencv-python',
        'openai',
        'langchain',
        'langchain_groq',
        'python-dotenv',
        'pydantic',
        'requests',  # If your project makes HTTP requests
        'setuptools',  # A good practice to include for packaging
    ],
    classifiers=[  # Optional: Helps categorize your project on PyPI
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,  # To include non-Python files (like .env)
    zip_safe=False,  # Whether the project can be reliably used if installed as a .egg
)
