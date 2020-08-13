#!/bin/bash
#minikube addons enable registry
#minikube service api --url
echo "press 'c' to enable minikube registry addon or press any key to continue"
while : ; do
read -n 1 k <&1
if [[ $k = c ]] ; then
printf "\n"
minikube addons enable registry
break
else
printf "\n\n"
break
fi
done
docker rm -f flanks_api_registry &> /dev/null
docker run --name flanks_api_registry -d --rm -it --network=host alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:$(minikube ip):5000"
docker-compose build
docker-compose push
mkdir -p k8s
kompose convert -o ./k8s
echo "finished building kubectl config"
echo "press 'c' to run 'kubectl apply -f ./k8s' or press any key to continue"
while : ; do
read -n 1 k <&1
if [[ $k = c ]] ; then
printf "\n"
kubectl apply -f ./k8s
break
else
break
fi
done
printf "\n\n"
echo "Press 'c' when deploy has finished"
while : ; do
read -n 1 k <&1
if [[ $k = c ]] ; then
printf "\nStopping registry port forwading\n"
docker stop flanks_api_registry &> /dev/null
break
fi
done