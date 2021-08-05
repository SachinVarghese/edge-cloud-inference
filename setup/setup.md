## Setup

1. Setup k8s cluster

```sh
kind create cluster --config=./cluster/kind.yaml
```

2. Install Istio

```sh
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.10.2 TARGET_ARCH=x86_64 sh -
./istio-1.10.2/bin/istioctl install --set profile=demo -y
```

3. Install Seldon Core

```sh
kubectl apply -f https://raw.githubusercontent.com/SeldonIO/seldon-core/master/notebooks/resources/seldon-gateway.yaml
kubectl create namespace seldon-system
helm upgrade --install seldon-core seldon-core-operator     --repo https://storage.googleapis.com/seldon-charts     --set usageMetrics.enabled=true     --namespace seldon-system     --set istio.enabled=true --set storageInitializer.image=sachinmv31/rclone-storage-minio-initializer:latest
```

4. Install Minio

```sh
kubectl create ns minio-system
helm repo add minio https://helm.min.io/
helm upgrade --install minio minio/minio --set accessKey="minioadmin" --set secretKey="minioadmin" --namespace minio-system  --version 8.0.8 --set service.type="LoadBalancer"
```

5. Download and Kubeedge Cloud Core

```sh
wget https://github.com/kubeedge/kubeedge/releases/download/v1.7.1/kubeedge-v1.7.1-linux-amd64.tar.gz
tar -xvzf kubeedge-v1.7.1-linux-amd64.tar.gz

kubectl create ns kubeedge
helm upgrade --install kubeedge ./charts/kubeedge/ --namespace kubeedge --recreate-pods
```

6. Configure Edge Device and connect to cloud by fetching cloud secret and update edge config at `edgecore.yaml` and update the loadbalancer IP and recreate cloud core secrets in the kubeedge namespace as needed.

```sh
./kubeedge-v1.7.1-linux-amd64/edge/edgecore --minconfig > ./edge-core/edge.yaml
kubectl get secret -n kubeedge tokensecret -o=jsonpath='{.data.tokendata}' | base64 -d
```

7. Update host resolution in `/etc/resolv.conf` and run edge device

```
nameserver 8.8.8.8
nameserver 8.8.4.4
```

```sh
sudo ./kubeedge-v1.7.1-linux-amd64/edge/edgecore --config ./edge-core/edge.yaml
```

8. Test Setup

```sh
kubectl apply -f manifests/iris-model.yaml -n production
```

9. Make a prediction on the edge side

```sh
docker run --rm curlimages/curl:7.78.0 -XPOST http://172.17.0.2:9000/api/v0.1/predictions -s  -H "Content-Type: application/json" -d '{"data":{"ndarray":[[0.3,0.6,4.2,3.1]]}}'

```

10. Dependant on https://github.com/kubeedge/kubeedge/pull/2230 So build custom rclone image for storage init

```sh
docker build -t sachinmv31/rclone-storage-minio-initializer storageInit
docker push sachinmv31/rclone-storage-minio-initializer
```

Re-configure Seldon Core

```sh
helm upgrade --install seldon-core seldon-core-operator     --repo https://storage.googleapis.com/seldon-charts     --set usageMetrics.enabled=true     --namespace seldon-system     --set istio.enabled=true --set storageInitializer.image=sachinmv31/rclone-storage-minio-initializer:latest
```

11. Apply new loadbalancer service

```
kubectl apply -n production -f manifests/cloud-svc.yaml
export CLOUD_LB_IP=$(kubectl get svc -n production cloud-model-svc -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

12. Update host aliases in volume mount of the joint classifier container `/var/lib/edged/pods/${PODID}/etc-hosts`

```
172.17.0.2    edge-model
$CLOUD_LB_IP  cloud-model
```
