echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
#docker push fadude/instapy-config:latest
#docker push fadude/instapy-auth:latest
#docker push fadude/instapy-socket:latest
#docker push fadude/instapy-client:latest
docker push fadude/upstream-instapy-client-arm64:latest
docker push fadude/upstream-instapy-ctrl-arm64:latest
