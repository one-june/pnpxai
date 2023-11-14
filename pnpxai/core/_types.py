from torch.utils.data import DataLoader, Dataset
from torch import Tensor, nn
from typing import Optional, Union, Sequence, Dict, Any, Callable
from dataclasses import dataclass

TensorSequence = Union[DataLoader, Dataset, Sequence[Tensor]]
DataSource = Union[TensorSequence, Tensor]

Model = nn.Module  # TODO: List other model types in Union[Type1, Type2, ...]


@dataclass
class Args:
    args: Sequence[Any]
    kwargs: Dict[str, Any]

    def __post_init__(self):
        self.args = self.args or []
        self.kwargs = self.kwargs or {}

