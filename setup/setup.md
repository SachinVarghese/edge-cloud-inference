# Setup

1. Setup k8s cluster

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
helm upgrade --install minio minio/minio --set accessKey="minioadmin" --set secretKey="minioadmin" --namespace minio-system  --version 8.0.8
kubectl apply -f manifests/miniovirtualservice.yaml
```