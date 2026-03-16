# Assignment 3 – Setup Guide

This document is the authoritative step-by-step reference for deploying the
multi-user URL shortener from Assignment 2 as containerised services.

**Part 3.1** covers Docker and Docker Compose on a single machine.
**Part 3.2** covers deploying the same images on a three-node Kubernetes cluster.

---

## Architecture Overview

```
                        ┌─────────────────────────────────────────────┐
                        │  Docker network / Kubernetes cluster        │
                        │                                             │
  Client ──► nginx:80 ──┤──► url_shortener:8100 ──► mongodb:27420.    │
                        │                                             │
                        │         auth_service:8101 ──► mongodb:27420 │
                        └─────────────────────────────────────────────┘
```

| Service        | Internal port | External access (Compose) | External access (K8s)   |
|----------------|---------------|--------------------------|-------------------------|
| nginx          | 80            | host port 80             | NodePort 30080          |
| url_shortener  | 8100          | via nginx only           | NodePort 30100          |
| auth_service   | 8101          | via nginx only           | ClusterIP (internal)    |
| mongodb        | 27420         | none                     | ClusterIP (internal)    |

---

## Files used for each part

| File / Directory         | Used in      |
|--------------------------|--------------|
| `url_shortener/`         | 3.1 and 3.2  |
| `auth_service/`          | 3.1 and 3.2  |
| `nginx/nginx.conf`       | 3.1 only     |
| `docker-compose.yml`     | 3.1 only     |
| `k8s/*.yaml`             | 3.2 only     |

---

## Prerequisites

### For Part 3.1 (local machine)

```bash
docker --version        # Docker 24+ recommended
docker compose version  # Compose v2 (built-in plugin, not the legacy docker-compose)
```

Install on Debian/Ubuntu if missing:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable docker
sudo usermod -aG docker "$USER"
# Log out and back in so group membership takes effect
```

> **Debian note** (relevant for the university VMs in Part 3.2): replace
> `ubuntu` with `debian` in the repository URL above.

### For Part 3.2 (university VMs)

Three VMs are required:
- **control** – runs the Kubernetes control plane
- **worker-1** and **worker-2** – run application pods

All commands below that are labelled **[all nodes]** must be run on every VM.

---

## Part 3.1 – Docker Compose

### Step 1 – Navigate to the assignment directory

```bash
cd assignment3/
```

All subsequent Compose commands are relative to this directory.

### Step 2 – Build the images

```bash
docker compose build
```

Docker builds `url_shortener` and `auth_service` images locally. Because
`requirements.txt` is copied before the application code, the pip layer is
cached and subsequent rebuilds (when only Python files change) complete in
seconds rather than minutes.

Expected output (truncated):

```
[+] Building 23.4s (10/10) FINISHED
 => [url_shortener] ...
 => [auth_service]  ...
```

### Step 3 – Start all services

```bash
docker compose up -d
```

The `-d` flag detaches the process so it runs in the background. Compose
starts services in dependency order: MongoDB → auth_service → url_shortener →
nginx.

Verify all four containers are running:

```bash
docker compose ps
```

Expected output:

```
NAME            IMAGE             STATUS          PORTS
mongodb         mongo:7           Up              27017/tcp
auth_service    assignment3-...   Up              8101/tcp
url_shortener   assignment3-...   Up              8100/tcp
nginx           nginx:alpine      Up              0.0.0.0:80->80/tcp
```

### Step 4 – Verify the services work

**Register a user:**

```bash
curl -s -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}' | python3 -m json.tool
```

Expected: `{"message": "User created successfully"}` with HTTP 201.

**Login and capture the token:**

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Token: $TOKEN"
```

**Create a shortened URL:**

```bash
curl -s -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"value": "https://www.example.com"}' | python3 -m json.tool
```

Expected: `{"id": "1"}` with HTTP 201.

**Retrieve all URLs:**

```bash
curl -s http://localhost:8080/ -H "Authorization: $TOKEN" | python3 -m json.tool
```

### Step 5 – Verify persistence across restarts

```bash
# Stop and destroy the containers (but not the named volume)
docker compose down

# Confirm the volume still exists
docker volume ls | grep mongo_data

# Bring everything back up
docker compose up -d

# Login again and retrieve URLs — the data created in Step 4 must still be there
TOKEN=$(curl -s -X POST http://localhost:8080/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -s http://localhost:8080/ -H "Authorization: $TOKEN" | python3 -m json.tool
```

The URLs created before `compose down` must appear in the response. This
confirms the `mongo_data` named volume correctly outlives the container
lifecycle.

### Step 6 – View logs (optional debugging)

```bash
docker compose logs -f url_shortener    # tail URL shortener logs
docker compose logs -f auth_service     # tail auth service logs
docker compose logs mongodb             # MongoDB startup log
```

### Step 7 – Stop the stack

```bash
docker compose down          # stop containers, keep volume
docker compose down -v       # stop containers AND delete volume (data lost)
```

---

## Part 3.2 – Kubernetes

### Phase A – Install Docker and Kubernetes on all three VMs

Run every command in this phase on **all three VMs** unless stated otherwise.

#### A1 – SSH into a VM

```bash
ssh <username>@<vm-ip>
```

#### A2 – Install Docker [all nodes]

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo usermod -aG docker "$USER"
exit          # log out so group membership refreshes
```

Log back in and confirm:

```bash
ssh <username>@<vm-ip>
groups        # 'docker' should appear in the list
```

#### A3 – Install Kubernetes tooling [all nodes]

```bash
sudo apt-get install -y apt-transport-https net-tools curl
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key \
  | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update --allow-unauthenticated
sudo apt-get install -y --allow-unauthenticated kubelet kubectl kubeadm
sudo apt-mark hold kubelet kubectl kubeadm
```

---

### Phase B – Initialise the control node

Run the commands in this phase **on the control VM only**.

#### B1 – Initialise the cluster

```bash
IP=$(ip -4 -o a | grep -i "ens3" | cut -d ' ' -f 2,7 | cut -d '/' -f 1 | awk '{print $2}')
sudo kubeadm init \
  --pod-network-cidr=192.168.0.0/16 \
  --control-plane-endpoint=$IP \
  --apiserver-cert-extra-sans=$IP
```

This takes a few minutes. When it finishes, copy the `kubeadm join ...` command
printed at the end — you will need it in Phase C to join the worker nodes.

#### B2 – Configure kubectl access

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

#### B3 – Configure the kubelet node IP

```bash
sudo echo KUBELET_KUBEADM_ARGS=\"--node-ip=$(ip -4 -o a | grep -i "ens3" \
  | cut -d ' ' -f 2,7 | cut -d '/' -f 1 | awk '{print $2}')\" \
  | sudo tee /var/lib/kubelet/kubeadm-flags.env
sudo systemctl restart kubelet.service
```

#### B4 – Install the Calico network plugin

```bash
kubectl create -f https://docs.projectcalico.org/manifests/tigera-operator.yaml
kubectl create -f https://docs.projectcalico.org/manifests/custom-resources.yaml
```

Watch the nodes come online (Ctrl-C to stop):

```bash
watch kubectl get nodes
```

All nodes will show `NotReady` until the network plugin finishes initialising.
The control node will become `Ready` first.

---

### Phase C – Join the worker nodes

Run the commands in this phase **on each worker VM**, one at a time.

#### C1 – Join the cluster

Paste the `kubeadm join` command you copied in step B1:

```bash
sudo kubeadm join <control-ip>:6443 --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

> If you have lost the join command, regenerate it from the control node:
> `kubeadm token create --print-join-command`

#### C2 – Configure the kubelet node IP

```bash
sudo echo KUBELET_KUBEADM_ARGS=\"--node-ip=$(ip -4 -o a | grep -i "ens3" \
  | cut -d ' ' -f 2,7 | cut -d '/' -f 1 | awk '{print $2}')\" \
  | sudo tee /var/lib/kubelet/kubeadm-flags.env
sudo systemctl restart kubelet.service
```

Repeat C1–C2 for the second worker node.

Verify all three nodes are Ready from the control node:

```bash
kubectl get nodes
```

Expected:

```
NAME        STATUS   ROLES           AGE   VERSION
control     Ready    control-plane   5m    v1.x.y
worker-1    Ready    <none>          2m    v1.x.y
worker-2    Ready    <none>          1m    v1.x.y
```

---

### Phase D – Build and push Docker images

Because the university VMs cannot access your local machine, images must be
pushed to a public registry (Docker Hub) and pulled from there.

#### D1 – Tag and push from your local machine

```bash
cd assignment3/

# Build
docker build -t <your-dockerhub-username>/auth-service:latest   ./auth_service/
docker build -t <your-dockerhub-username>/url-shortener:latest  ./url_shortener/

# Login to Docker Hub
docker login

# Push
docker push <your-dockerhub-username>/auth-service:latest
docker push <your-dockerhub-username>/url-shortener:latest
```

#### D2 – Update the image references in the manifests

Edit `k8s/auth-deployment.yaml` and `k8s/url-shortener-deployment.yaml` and
replace every occurrence of `<your-dockerhub-username>` with your actual Docker
Hub username.

---

### Phase E – Deploy to Kubernetes

Run all `kubectl` commands from the **control node**.

Copy the `k8s/` directory to the control node:

```bash
# From your local machine
scp -r assignment3/k8s/ <username>@<control-ip>:~/
```

#### E1 – Deploy MongoDB with persistent storage

```bash
kubectl apply -f k8s/mongo-pvc.yaml
kubectl apply -f k8s/mongo-deployment.yaml
kubectl apply -f k8s/mongo-service.yaml
```

Wait for MongoDB to be Running:

```bash
kubectl get pods -l app=mongodb
```

#### E2 – Deploy the authentication service

```bash
kubectl apply -f k8s/auth-deployment.yaml
kubectl apply -f k8s/auth-service.yaml
```

#### E3 – Deploy the URL shortener (3 replicas)

```bash
kubectl apply -f k8s/url-shortener-deployment.yaml
kubectl apply -f k8s/url-shortener-service.yaml
```

#### E4 – Deploy nginx (bonus – single entry point)

```bash
kubectl apply -f k8s/nginx-configmap.yaml
kubectl apply -f k8s/nginx-deployment.yaml
kubectl apply -f k8s/nginx-service.yaml
```

#### E5 – Verify all pods are running

```bash
kubectl get pods
kubectl get services
```

Expected pods:

```
NAME                             READY   STATUS    RESTARTS
mongodb-<hash>                   1/1     Running   0
auth-service-<hash>              1/1     Running   0
url-shortener-<hash>-1           1/1     Running   0
url-shortener-<hash>-2           1/1     Running   0
url-shortener-<hash>-3           1/1     Running   0
nginx-<hash>                     1/1     Running   0
```

---

### Phase F – Test the Kubernetes deployment

Replace `<worker-ip>` with the IP address of either worker node.

**Register a user:**

```bash
curl -s -X POST http://<worker-ip>:30080/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}' | python3 -m json.tool
```

**Login:**

```bash
TOKEN=$(curl -s -X POST http://<worker-ip>:30080/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

**Create a URL:**

```bash
curl -s -X POST http://<worker-ip>:30080/ \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"value": "https://www.example.com"}' | python3 -m json.tool
```

**Verify consistent view across replicas:**

To confirm all three replicas share the same database, send several read
requests and check which pod handles each one. First enable pod-name logging
by watching pod logs while making requests, or use:

```bash
# Send 6 GET requests
for i in {1..6}; do
  curl -s http://<worker-ip>:30080/ -H "Authorization: $TOKEN" | python3 -m json.tool
done
```

All responses must return the same list of URL IDs regardless of which replica
serves the request. This demonstrates consistency — the data lives in the
shared MongoDB, not in the pods themselves.

You can also access the URL shortener directly (bypassing nginx):

```bash
curl -s http://<worker-ip>:30100/ -H "Authorization: $TOKEN" | python3 -m json.tool
```

---

### Troubleshooting

#### Inspect pod logs

```bash
kubectl get pods                            # find the pod name
kubectl logs <pod-name>                     # show stdout/stderr
kubectl logs <pod-name> --previous          # logs from a crashed previous run
```

#### Describe a failing pod

```bash
kubectl describe pod <pod-name>             # shows events, image pull errors, etc.
```

#### Restart a pod

```bash
kubectl rollout restart deployment/<name>   # e.g. deployment/url-shortener
```

#### Reset the entire cluster (start over)

Run on **every node**:

```bash
sudo kubeadm reset
sudo rm -rf /etc/cni /var/lib/cni /opt/cni /var/log/calico /var/lib/calico /etc/kubernetes
rm -rf ~/.kube
sudo reboot
```

Then repeat Phase B and onwards.

#### Free up disk space on a VM

```bash
docker system prune -af           # removes unused images and stopped containers
sudo du -h / | sort -rh | head -n 10   # find largest directories
```

---

## Quick-reference cheat sheet

```bash
# --- Docker Compose ---
docker compose build              # build images
docker compose up -d              # start stack in background
docker compose down               # stop stack (keep volume)
docker compose down -v            # stop stack and delete data
docker compose ps                 # list running containers
docker compose logs -f <service>  # tail logs

# --- Kubernetes ---
kubectl get nodes                 # cluster health
kubectl get pods                  # pod status
kubectl get services              # service / port overview
kubectl apply -f k8s/             # deploy / update everything at once
kubectl delete -f k8s/            # tear down all deployments
kubectl logs <pod>                # view logs
kubectl describe pod <pod>        # diagnose issues
watch kubectl get pods            # live pod status
```
