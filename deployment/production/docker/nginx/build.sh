#!/usr/bin/env bash
REPO_NAME=kartoza
IMAGE_NAME=inasafe-django_nginx
if [ -z $TAG_NAME ]; then
	TAG_NAME=latest
fiop
fi

echo "Build: $REPO_NAME/$IMAGE_NAME:$TAG_NAME"

docker build -t ${REPO_NAME}/${IMAGE_NAME} .
docker tag ${REPO_NAME}/${IMAGE_NAME}:latest ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME}
docker push ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME}
