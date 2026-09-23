---
title: How far do measurement correlations reach in a cluster state?
date: 2026-09-22
summary: Measuring a 1D cluster state in a tilted basis correlates distant outcomes. An exact matrix-product-state calculation shows how far those correlations reach.
draft: true
---

The 1D cluster state is the workhorse of measurement-based quantum computing. Its stabilizers are $Z_{i-1}X_iZ_{i+1}$, and in the computational basis its amplitudes are just signs:

$$
\psi(x_1,\dots,x_N) = 2^{-N/2}\,(-1)^{\sum_i x_i x_{i+1}}.
$$

Measure every qubit in the $Z$ basis and you get independent, uniformly random bits. The same happens in the $X$ basis. Tilt the measurement basis to an angle $\theta$ somewhere in between, though, and the outcomes become correlated. For my thesis I wanted to know how far those correlations reach. The answer tells you how much memory a model needs to reproduce the distribution one site at a time, which is exactly how autoregressive neural networks such as RNNs generate samples.

## Measuring "how far"

Take a block of consecutive outcomes $X_0, X_1, \dots, X_{m+1}$. The conditional mutual information

$$
I_m = I(X_0 : X_{m+1} \mid X_1, \dots, X_m)
$$

is what the two ends still share once you know everything in between. If $I_m$ decays like $e^{-m/\xi}$, a model that looks back about $\xi$ sites already captures most of the dependence.

## Computing it exactly

The cluster state is a matrix product state with bond dimension 2, so there is no need to sample. Rotating each physical leg by $R_y(\theta)$ gives one $2\times2$ matrix $B^x$ per outcome $x$. The Born-rule transfer matrix is $E = \sum_x \bar B^x \otimes B^x$, and the probability of any block follows from its dominant left and right eigenvectors. For $m$ up to 12 I simply enumerate all $2^{m+2}$ bitstrings; a scan over 31 angles takes about 20 seconds on a laptop.

To be sure the transfer-matrix code is right, the tests compare it with a brute-force calculation on an explicit state vector. The probabilities agree to $10^{-12}$.

## What comes out

![log10 of the conditional mutual information versus buffer size m and angle theta](cmi-heatmap.png)

Three things stand out.

- $I_0 = 0$ at every angle: neighbouring outcomes are always independent. Correlations only appear once there is at least one site in between.
- At small $\theta$ the CMI drops by many orders of magnitude within a few sites. The fitted decay length grows from about 0.2 sites at $\theta = 0.05$ to about 2 sites at $\theta = \pi/4$, and passes 10 sites near $\theta \approx 1.3$.
- Close to $\pi/2$, odd and even $m$ separate and the decay becomes very slow, until at exactly $\pi/2$ everything vanishes again. Here a single exponential no longer describes the data, which is a good reminder to look at the raw $I_m$ before trusting a fitted length.

## Next

In the thesis I compare these lengths with how well RNN and RBM wavefunctions learn the same distributions. That comparison deserves a post of its own.

The code is [cluster_mps_cmi_length_scan.py](https://github.com/HelioXv022/nqs_project/blob/main/scripts/cluster_state/cluster_mps_cmi_length_scan.py) in my [nqs_project](https://github.com/HelioXv022/nqs_project) repository.
