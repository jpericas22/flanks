#!/bin/bash
#minikube addons enable registry
#minikube service api --url
docker rm -f flanks_api_registry > /dev/null || true
docker run --name flanks_api_registry -d --rm -it --network=host alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:$(minikube ip):5000"
docker-compose build
docker-compose push
mkdir -p k8s
kompose convert -o ./k8s
echo "finished building kubectl config"
echo "press 'd' to run 'kubectl apply -f ./k8s' or any key to bypass"
while : ; do
read -n 1 k <&1
if [[ $k = d ]] ; then
printf "\n"
kubectl apply -f ./k8s
break
else
break
fi
done
printf "\n\n"
echo "Press 'q' when deploy has finished"
while : ; do
read -n 1 k <&1
if [[ $k = q ]] ; then
printf "\nStopping registry port forwading\n"
docker stop flanks_api_registry > /dev/null || true
break
fi
done