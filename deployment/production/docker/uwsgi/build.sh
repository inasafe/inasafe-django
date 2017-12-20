#!/usr/bin/env bash
REPO_NAME=kartoza
IMAGE_NAME=inasafe-django_uwsgi
if [ -z $TAG_NAME ]; then
	TAG_NAME=latest
fi

if [ -z $INASAFE_DJANGO_TAG ]; then
	INASAFE_DJANGO_TAG=develop
fi
echo "INASAFE_DJANGO_TAG=${INASAFE_DJANGO_TAG}"

echo "Build: $REPO_NAME/$IMAGE_NAME:$TAG_NAME"

docker build -t ${REPO_NAME}/${IMAGE_NAME} \
	--build-arg INASAFE_DJANGO_TAG=${INASAFE_DJANGO_TAG} .
docker tag ${REPO_NAME}/${IMAGE_NAME}:latest ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME}
docker push ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME}
