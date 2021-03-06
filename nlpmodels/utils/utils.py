"""
This module contains a handful of helper functions used throughout the repo.
"""
from typing import List

import numpy as np
import torch
import torch.nn as nn


def set_seed_everywhere():
    """
    Function to setting seeds everywhere.
    The only correct answer for the seed is 42.
    """
    seed = 42
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_cosine_similar(target_word: str, word_to_idx: dict, embeddings: torch.Tensor) -> List:
    """
    Function for calculating cosine similarities across dictionary versus target word, descending order.
        Args:
            target_word (str): token of interest
            word_to_idx (dict): word to index map
            embeddings (torch.Tensor): embedding vectors
        Returns:
            returns a list of (token, cosine_similarity) pairs.
    """
    cos = nn.CosineSimilarity(dim=0)
    word_embedding = embeddings[word_to_idx[target_word.lower()]]
    distances = []
    for word, index in word_to_idx.items():
        if word in ('<MASK>', target_word, '<UNK>'):
            continue
        distances.append((word, cos(word_embedding, embeddings[index])))

    results = sorted(distances, key=lambda x: x[1], reverse=True)
    return results
