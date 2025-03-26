#!/bin/bash

echo "SSH to minikube to create the folder to mount!"
minikube ssh "mkdir -p /home/docker/data"

# Create a basic storage class
echo "Creating storage class..."
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: a8s-storage
  namespace: a8s
provisioner: k8s.io/minikube-hostpath
reclaimPolicy: Delete
volumeBindingMode: Immediate
EOF

# Create a PV
echo "Creating PV..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: a8s-pv
  namespace: a8s
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: a8s-storage
  local:
    path: /home/docker/data
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - minikube
EOF

# Create a PVC
echo "Creating PVC..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: a8s-pvc
  namespace: a8s
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: a8s-storage
EOF
