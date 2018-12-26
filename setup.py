import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name                            = "ibkr_api"                                                    ,
    version                         = "0.0.0"                                                       ,
    author                          = "David Orkin"                                                 ,
    author_email                    = "orange.cardinal@gmail.com"                                   ,
    description                     = "OFFICIALLY the best, unofficial python IBKR API Clients"     ,
    long_description                = long_description                                              ,
    long_description_content_type   = "text/markdown"                                               ,
    url                             = "https://github.com/OrangeCardinal/ibkr_api"                  ,
    packages                        = setuptools.find_packages()                                    ,
    classifiers=[
        "Programming Language :: Python :: 3"                                       ,
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"  ,
        "Operating System :: OS Independent"                                        ,
    ],
)