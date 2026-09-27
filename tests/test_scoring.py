import numpy as np
import pytest
from src.scoring import to_percentage, fuse_scores


def test_to_percentage_scales_correctly():
    scores = np.array([0.0, 0.5, 1.0])
    result = to_percentage(scores)
    assert list(result) == [0.0, 50.0, 100.0]


def test_to_percentage_clips_out_of_range():
    scores = np.array([-0.2, 1.5])
    result = to_percentage(scores)
    assert result[0] == 0.0
    assert result[1] == 100.0


def test_fuse_scores_weighted_average():
    final = fuse_scores([100], [0], [0], weights={"tfidf": 1.0, "semantic": 0.0, "bert": 0.0})
    assert final[0] == 100.0


def test_fuse_scores_requires_weights_sum_to_one():
    with pytest.raises(AssertionError):
        fuse_scores([100], [0], [0], weights={"tfidf": 0.5, "semantic": 0.5, "bert": 0.5})
