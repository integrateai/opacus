#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

from typing import Dict, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from .utils import register_grad_sampler


@register_grad_sampler(
    [
        nn.InstanceNorm1d,
        nn.InstanceNorm2d,
        nn.InstanceNorm3d,
    ]
)
def compute_instance_norm_grad_sample(
    layer: Union[
        nn.InstanceNorm1d,
        nn.InstanceNorm2d,
        nn.InstanceNorm3d,
    ],
    A: torch.Tensor,
    B: torch.Tensor,
) -> Dict[torch.Tensor, torch.Tensor]:
    """
    Computes per sample gradients for InstanceNorm layers

    Args:
        layer: Layer
        A: Activations
        B: Backpropagations
    """
    gs = F.instance_norm(A, eps=layer.eps) * B
    ret = {layer.weight: torch.einsum("ni...->ni", gs)}

    if layer.bias is not None:
        ret[layer.bias] = torch.einsum("ni...->ni", B)

    return ret
