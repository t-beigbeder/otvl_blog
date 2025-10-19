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

This is explained in the following section.

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
a taint mark a given node as forbidding scheduling or even execution to any pod
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
In the case of GPUs, Kubernetes accepts vendor-specific resources  

## Further information

- to be completed

And also:

- [For your ears and your mind](https://tricky.bandcamp.com/album/out-the-way)
