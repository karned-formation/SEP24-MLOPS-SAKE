#!/bin/bash
python src/config_transform_as_env.py  python src/config_transform_as_env.py 
cat .env_mlops_sake >> .env
docker-compose up --build