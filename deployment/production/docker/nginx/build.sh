#!/usr/bin/env bash

if [ -z "$REPO_NAME" ]; then
	REPO_NAME=kartoza
fi

if [ -z "$IMAGE_NAME" ]; then
	IMAGE_NAME=inasafe-django_nginx
fi

if [ -z "$TAG_NAME" ]; then
	TAG_NAME=latest
fi

if [ -z "$BUILD_ARGS" ]; then
	BUILD_ARGS="--pull --no-cache"
fi

echo "Build: $REPO_NAME/$IMAGE_NAME:$TAG_NAME"
echo "Build Args: $BUILD_ARGS"

docker build -t ${REPO_NAME}/${IMAGE_NAME} ${BUILD_ARGS} . && \
docker tag ${REPO_NAME}/${IMAGE_NAME}:latest ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME} && \
docker push ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME}
