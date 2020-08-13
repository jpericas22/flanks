#!/bin/sh
old_api_version="extensions\/v1beta1"
new_api_version="networking\.k8s\.io\/v1"

docker rm -f flanks_api_registry || true
docker run --name flanks_api_registry -d --rm -it --network=host alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:$(minikube ip):5000"
docker-compose build
docker-compose push
mkdir -p k8s
kompose convert -o ./k8s
#sed -i -e "s/${old_api_version}/${new_api_version}/g" ./k8s/*-networkpolicy.yaml
echo 'finished building kubectl config'
echo 'run "kubectl apply -f ./k8s"'