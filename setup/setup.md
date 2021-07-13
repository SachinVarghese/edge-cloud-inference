# Setup

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
helm upgrade --install seldon-core seldon-core-operator     --repo https://storage.googleapis.com/seldon-charts     --set usageMetrics.enabled=true     --namespace seldon-system     --set istio.enabled=true
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

7. Run edge device

```sh
sudo ./kubeedge-v1.7.1-linux-amd64/edge/edgecore --config ./edge-core/edge.yaml
```