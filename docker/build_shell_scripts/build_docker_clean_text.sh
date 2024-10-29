#!/bin/bash
docker image build --build-arg DOCKERFILE_PATH=docker/clean_text -f docker/clean_text/Dockerfile . -t ms-sake-clean-text:1.0
