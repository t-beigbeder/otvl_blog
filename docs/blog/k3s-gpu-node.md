---
ow_article: true
template: article.html
title: Adding a GPU node to a K3s cluster
version: "1.0"
publication_date: "2025/10/17"
summary_heading: "Adding a GPU node to a K3s cluster"
summary: |
    This article details how to integrate a node with a GPU in a K3s cluster,
    while giving related explainations about how the involved components work and interact.
    Lastly, container examples are provided.
    While vendor-specific information is used, the content remains largely general.
head_image: ../../assets/images/k3s-gpu-node/portVendres.jpg
head_img_title: Blockhaus near Port-Vendres
---

## Introduction

A GPU-enabled host is commonly used by Data Scientists
to design and test their deep learning models and in the end to train them.
As GPU resources are costly, Kubernetes is often leveraged
to enable their sharing among a community of users,
along with access means to the corresponding workloads.

In the perspective of self-hosting such a solution,
or simply to better understand off-the-shelf solutions,
this article is a guide through existing documentation
and provides instructions to set up the environment.
It also explains the role of the various components involved
both during the setup and at run-time, and how they interact.

While NVIDIA specific information is used, the content remains as general as possible,
this is a Kubernetes gift.

This is a domain where technology evolves rather quick,
so this article could become partly outdated more quickly than others.

## Read the docs

### The documentation maze

It's a shame that billion-dollars companies sometimes provide documentation so poorly organized.
Many open source projects wouldn't survive if they behaved like that.
And indeed the first recommendation to find our way in the documentation to get started,
is to rely on Kubernetes generic information rather than our GPU vendor's one.
Well, here I talk about NVIDIA, I didn't have to dive into AMD or Intel ones.

So we can start by reading the Kubernetes's documentation page
[Schedule GPUs | Kubernetes](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/),
which is a perfect entry point,
and which by the way provide us a pointer to a NVIDIA
useful document (NVIDIA Device Plugin for Kubernetes), yet not the main one we will use.

As far as NVIDIA is concerned, we will later have to deal with the vendor's entry point:
[NVIDIA Cloud Native Technologies](https://docs.nvidia.com/datacenter/cloud-native/index.html),
and mainly under the "Kubernetes and NVIDIA GPUs" tab, the following references:

- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html)
- [NVIDIA GPU Feature Discovery](https://github.com/NVIDIA/k8s-device-plugin/tree/main/docs/gpu-feature-discovery)
- [NVIDIA Device Plugin for Kubernetes](https://github.com/NVIDIA/k8s-device-plugin), already mentioned above

also important under the "Containers and NVIDIA GPUs" tab:

- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html), under which
- [Architecture overview](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/arch-overview.html)

but they shouldn't be recommended to get started, as we don't understand at first how those components rely to each other.

### Scheduling GPUs with Kubernetes

So our goal is to integrate a node equipped with one or several GPU devices in a Kubernetes cluster,
and to run data science related workloads on it.
Linux containers enable to expose the GPU Linux device to a container running on the same host,
so the code running in such a container can use the GPUs, as a native OS process would.

<img markdown="1" src=../../assets/images/k3s-gpu-node/k8s.png title="Scheduling GPUs with Kubernetes" alt="Scheduling GPUs with Kubernetes schema" class="img-fluid">

Now we know this is technically feasible, we also want:

- to configure the GPU device so that Kubernetes pods can reliably access it
- to control which Kubernetes pod running on the GPU node can access the device
- to control how other pods can be scheduled or not on the same node, as we often want the GPU workload to run as efficiently as possible once scheduled

### Enabling pods to access the GPU

The node and GPU configuration is a shared responsibility between the container runtime level and the Kubernetes control plane.
This is summarized on the schema below:

<img markdown="1" src=../../assets/images/k3s-gpu-node/k8s-gpu.png title="Configuring GPUs with Kubernetes" alt="Configuring GPUs with Kubernetes schema" class="img-fluid">

Without giving all the technical details:

- The [container runtime](https://kubernetes.io/docs/setup/production-environment/container-runtimes/) is wrapped with the vendor's specific
component `NVIDIA container-toolkit` to configure the GPU and the container at container initialization time, see the detailed architecture
[here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/arch-overview.html);
- the [Kubernetes device plugin](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/)
is a component that informs the Kubernetes control plane about the node's GPU status: number, health,
with a vendor's specific implementation
[`NVIDIA k8s-device-plugin`](https://github.com/NVIDIA/k8s-device-plugin?tab=readme-ov-file#about),
it relies on the container runtime, and is implemented in that case as a daemonset.

### Scheduling pods on GPU nodes

There are several features available with Kubernetes to control pod scheduling on specific nodes.
The most straightforward one is based on
[taints and tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/):
a taint marks a given node as forbidding scheduling or even execution of any pod
but one that has the corresponding toleration. Thus a node marked with a kind of GPU taint will only
run pods that need this kind of GPU by providing the corresponding toleration.
For instance:

```shell
kubectl taint nodes node-with-gpu "acme.com/gpu=true:NoSchedule"
```

```yaml
containers:
- name: workload-needing-gpu
  image: "registry/ds-python-gpu:1.0"
#...
tolerations:
- key: "acme.com/gpu"
  operator: Exists
  effect: "NoSchedule"
```

Even if we use other features to control GPU scheduling, corresponding taints are generally required
to avoid the presence of application workloads that don't need GPU.

Another scheduling feature simple to use relies on resources requests.
For instance a container can request main CPU and RAM available on a node to ensure
no other container will be scheduled on the same node.
In the case of GPUs, Kubernetes exposes vendor-specific resources after the device plugin has been installed.
For instance (only limits are needed and meaningful in that case):

```yaml
containers:
- name: workload-needing-gpu
  image: "registry/ds-python-gpu:1.0"
  resources:
    limits:
      acme.com/gpu: 1
```

Kubernetes also defines a service as an add-on:
[Node Feature Discovery](https://kubernetes-sigs.github.io/node-feature-discovery/master/get-started/index.html)
whose purpose is to automatically add labels on nodes based on the hardware they integrate.
In the case of NVIDIA for instance we can find
[here](https://github.com/NVIDIA/k8s-device-plugin/blob/main/docs/gpu-feature-discovery/README.md#generated-labels)
the labels are set when the 
[NVIDIA GPU Feature Discovery](https://github.com/NVIDIA/k8s-device-plugin/tree/main/docs/gpu-feature-discovery)
is deployed.
The service is supposed to enable adding taints to the nodes, likely it is not implemented (or documented?) in the case of NVIDIA.
That's unfortunate, it would be a useful feature.

Such labels can then be leveraged to fine-tune GPU workloads scheduling according the specific hardware requirements.

## GPU support software installation

This section is vendor specific, NVIDIA in that case.
The recommended way to install NVIDIA GPU support in Kubernetes is to use the
[NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html),
which has the ability to install the GPU driver and the Container Toolkit along the way.
However, as the goal here is to get a better understanding of the underlying interactions,
the choice is made to play the steps one by one.

Also, cloud-providers often provide GPU pre-installed images for VMs, not always baqsed on the Linux distribution we want.
Here the examples are based on Debian 12 (old stable) as Debian 13 is not yet supported by the vendor.

<img markdown="1" src=../../assets/images/k3s-gpu-node/gpu-install.png title="GPU support software installation" alt="GPU support software installation schema" class="img-fluid">


### Installing CUDA and the kernel module

Instructions are provided
[here](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Debian&target_version=12&target_type=deb_network)
in the case of Debian 12. For instance:

```shell
export DEBIAN_FRONTEND=noninteractive
cd /tmp && \
wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb && \
dpkg -i cuda-keyring_1.1-1_all.deb && \
rm cuda-keyring_1.1-1_all.deb && \
apt-get update && \
apt-get install -y linux-headers-`uname -r` && \
apt-get install -y software-properties-common && \
add-apt-repository -y contrib && \
apt-get install -y cuda-toolkit-13-0 && \
apt-get install -y nvidia-driver-cuda nvidia-kernel-dkms
```

It is required to restart the system at that point, not obvious if using cloud-init initiated automation.

### Installing the Container Toolkit

Instructions are provided
[here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html),
for instance:

```shell
export DEBIAN_FRONTEND=noninteractive
export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.17.8-1
cd /tmp && \
wget https://nvidia.github.io/libnvidia-container/gpgkey && \
rm -f /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg && \
gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg < gpgkey && \
rm gpgkey && \
wget https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list && \
sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  < nvidia-container-toolkit.list \
  > /etc/apt/sources.list.d/nvidia-container-toolkit.list && \
rm nvidia-container-toolkit.list && \
apt-get update && \
apt-get install -y \
      nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}
```

### Installing K3s and joining a cluster

Instructions are provided [here](https://docs.k3s.io/quick-start).
The GPU node will be an agent and we can use the following for instance:

```shell
curl -sfL https://get.k3s.io | \
  sh -s - agent -s https://cluster-api-server:6443 --token-file /path/to/secrets/k3s_token \
    --node-taint nvidia.com/gpu=true:NoSchedule
```

This will also install a container run-time on the node, by default K3s uses `containerd`.

### Installing the k8s-device-plugin

This is the final step of the installation,
lastly using the
[NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html).
It relies on Helm, among other options, that can be run on any host having access the the cluster API.
Instructions are provided
[here](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html).
In the default case of K3s using `containerd`,
care must be taken to configure the Container Toolkit properly,
for instance:

```shell
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia && \
helm repo update && \
helm install --wait --generate-name \
    -n gpu-operator --create-namespace \
    nvidia/gpu-operator \
    --version=v25.3.4 \
    --set driver.enabled=false \
    --set toolkit.enabled=false \
    --set toolkit.env[0].name=CONTAINERD_CONFIG \
    --set toolkit.env[0].value=/var/lib/rancher/k3s/agent/etc/containerd/config.toml \
    --set toolkit.env[1].name=CONTAINERD_SOCKET \
    --set toolkit.env[1].value=/run/k3s/containerd/containerd.sock
```

## References

- Kubernetes
    - [Schedule GPUs | Kubernetes](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
    - [Node Feature Discovery](https://kubernetes-sigs.github.io/node-feature-discovery/master/get-started/index.html)


- [NVIDIA Cloud Native Technologies](https://docs.nvidia.com/datacenter/cloud-native/index.html)
    - [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html)
    - [Architecture overview](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/arch-overview.html)
    - [NVIDIA Device Plugin for Kubernetes](https://github.com/NVIDIA/k8s-device-plugin)
    - [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html)
    - [NVIDIA GPU Feature Discovery](https://github.com/NVIDIA/k8s-device-plugin/tree/main/docs/gpu-feature-discovery)

And also:

- [For the ears and for the soul](https://tricky.bandcamp.com/album/out-the-way)
