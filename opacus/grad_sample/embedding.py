#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

from typing import Dict

import torch
import torch.nn as nn

from .utils import register_grad_sampler


@register_grad_sampler(nn.Embedding)
def compute_embedding_grad_sample(
    layer: nn.Embedding, A: torch.Tensor, B: torch.Tensor
) -> Dict[torch.Tensor, torch.Tensor]:
    """
    Computes per sample gradients for ``nn.Embedding`` layer.

    Args:
        layer: Layer
        A: Activations
        B: Backpropagations
    """
    saved = torch.backends.cudnn.deterministic
    torch.backends.cudnn.deterministic = True

    batch_size = A.shape[0]
    index = (
        A.unsqueeze(-1)
        .expand(*A.shape, layer.embedding_dim)
        .reshape(batch_size, -1, layer.embedding_dim)
    )
    grad_sample = torch.zeros(
        batch_size, *layer.weight.shape, device=layer.weight.device
    )
    grad_sample.scatter_add_(1, index, B.reshape(batch_size, -1, layer.embedding_dim))
    torch.backends.cudnn.deterministic = saved

    return {layer.weight: grad_sample}
