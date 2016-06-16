#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m'

printf "\n${GREEN}*** Install deps ***${NC}\n"
cd /opt/build/
mkdir framework
pip install framework-0.0.1.tar.gz --target ./framework

printf "\n${GREEN}*** Pack app ***${NC}\n"
cd framework
echo "from framework import cli; cli.main()" >> __main__.py
find . -name "*.pyc" -delete
find . -name "*.egg-info" | xargs rm -rf

rm framework.zip
zip -9mrv framework.zip .
mv framework.zip ../framework.zip_
cd ..
rm -rf framework
chmod +x framework.zip_

printf "\n${GREEN}*** Test zipapp, help message should be outputted ***${NC}\n"
python framework.zip_ --help
