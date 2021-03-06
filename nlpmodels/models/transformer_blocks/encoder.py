"""
This module contains the Encoder layer and composite encoder stack (made of many encoder layers) for the
Transformer model class.
"""

from copy import deepcopy

import torch
import torch.nn as nn

from nlpmodels.models.transformer_blocks.attention import MultiHeadedAttention
from nlpmodels.models.transformer_blocks.sublayers import AddAndNormWithDropoutLayer, \
    PositionWiseFFNLayer


class EncoderBlock(nn.Module):
    """
    The Encoder block of the Transformer (encoder-decoder).
    This is repeated sequentially N times inside the Encoder stack.

    Takes as input the embedding(source) /encoder[l-1] and source mask for self-attention.

    Computes  x -> self_attn -> addNorm -> src_attn -> FFN -> addNorm.
    """

    def __init__(self, size: int, self_attention: MultiHeadedAttention,
                 feed_forward: PositionWiseFFNLayer,
                 dropout: float):
        """
        Args:
            size (int):
                This hyper-parameter is used for the BatchNorm layers.
            self_attention (MultiHeadedAttention):
                The multi-headed attention layer that is used for self-attention.
            feed_forward (PositionWiseFFNLayer):
                The feed forward layer applied after attention for further transformation.
            dropout (float):
                Hyper-parameter used in drop-out regularization in training.
        """
        super(EncoderBlock, self).__init__()
        self._size = size
        # (1) self-attention
        self._self_attention = self_attention
        # (2) add + norm layer
        self._add_norm_layer_1 = AddAndNormWithDropoutLayer(size, dropout)
        # (3) FFN
        self._feed_forward = feed_forward
        # (4) add + norm layer
        self._add_norm_layer_2 = AddAndNormWithDropoutLayer(size, dropout)

    @property
    def size(self) -> int:
        """
        Returns:
            _size parameter.
        """
        return self._size

    def forward(self, values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """
        Main function call for encoder block.
        maps values -> self_attn -> addNorm -> FFN -> addNorm.
        Args:
            values (torch.Tensor): Either embedding(src) or encoder[l-1] output.
            mask (torch.Tensor): Masking source so model doesn't see padding.
        """
        values = self._add_norm_layer_1(values, lambda x: self._self_attention(x, x, x, mask))
        values = self._add_norm_layer_2(values, self._feed_forward)
        return values


class CompositeEncoder(nn.Module):
    """
    The encoder stack of the Transformer.
    Pass the input through N encoder blocks then Add+Norm layer the output.
    """

    def __init__(self, layer: EncoderBlock, num_layers: int):
        """
        Args:
            layer (EncoderBlock):layer to be sequentially repeated num_layers times.
            num_layers (int): Number of layers in the encoder block.
        """
        super(CompositeEncoder, self).__init__()
        self._layers = nn.ModuleList([deepcopy(layer)] * num_layers)
        self._add_norm = nn.BatchNorm1d(layer.size, momentum=None, affine=False)

    def forward(self, values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """
        Main function call for Encoder block.
        Takes in embedding(src), target_mask, source, source_mask, and encoder output.

        Args:
            values (torch.Tensor): Either embedding(src) or encoder[l-1] output.
            mask (torch.Tensor): Masking source so model doesn't see padding.
        Returns:
            encoder output to be used as input into decoder block.
        """
        for layer in self._layers:
            values = layer(values, mask)
        return self._add_norm(values)
