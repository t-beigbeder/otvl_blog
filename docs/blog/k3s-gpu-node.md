---
ow_article: true
template: article.html
title: Adding a GPU node to a K3s cluster
version: "1.0"
publication_date: "2025/10/17"
summary_heading: "Adding a GPU node to a K3s cluster"
summary: |
    This article is a recipe to integrate a node with a GPU in a K3s cluster.
    It also provides background information and explanations about how the involved components interact and lastly how to leverage such resource in containers.
head_image: ../../assets/images/k3s-gpu-node/portVendres.jpg
head_img_title: Blockhaus near Port-Vendres
---

## Introduction

A GPU-enabled host will enable Data Scientists
to design and test their deep learning models and in the end to train them.
As GPU resources are costly, Kubernetes is often leveraged
to enable their sharing among a community of users,
along with access means to the corresponding workloads.
