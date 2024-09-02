import abc
import sys
import warnings
from typing import Optional, Union, Callable, Tuple

import copy
import torch
from torch import nn

from pnpxai.core._types import ExplanationType
from pnpxai.explainers import GradCam
from pnpxai.explainers.base import Explainer
from pnpxai.explainers.utils.postprocess import PostProcessor

# Ensure compatibility with Python 2/3
ABC = abc.ABC if sys.version_info >= (3, 4) else abc.ABCMeta(str('ABC'), (), {})

NON_DISPLAYED_ATTRS = [
    'model',
    'explainer',
    'device',
    'prob_fn',
    'pred_fn',
]

class Metric(ABC):
    """
    An abstract base class representing a metric used to evaluate explanations generated
    by an explainer for a given model. The metric is typically used to assess the quality or
    effectiveness of attribution-based explanations.

    Parameters:
        model (nn.Module): The model to be explained.
        explainer (Optional[Explainer], optional): 
            The explainer used to generate explanations for the model. Defaults to None.
        **kwargs: 
            Additional keyword arguments.
    """

    SUPPORTED_EXPLANATION_TYPE: ExplanationType = "attribution"

    def __init__(
        self,
        model: nn.Module,
        explainer: Optional[Explainer] = None,
        **kwargs
    ):
        self.model = model.eval()  # Set the model to evaluation mode
        self.explainer = explainer
        self.device = next(model.parameters()).device  # Determine the device used by the model

    def __repr__(self):
        """
        Provides a string representation of the Metric object, displaying its attributes.

        Returns:
            str: A string representation of the Metric object.
        """
        displayed_attrs = ', '.join([
            f'{k}={v}' for k, v in self.__dict__.items()
            if k not in NON_DISPLAYED_ATTRS and v is not None
        ])
        return f"{self.__class__.__name__}({displayed_attrs})"

    def copy(self):
        """
        Creates a shallow copy of the Metric object.

        Returns:
            Metric: A copy of the Metric object.
        """
        return copy.copy(self)

    def set_explainer(self, explainer: Explainer):
        """
        Sets the explainer for the metric, ensuring it is associated with the same model.
        """
        assert self.model is explainer.model, 'Must have same model of metric.'
        clone = self.copy()
        clone.explainer = explainer
        return clone

    def set_kwargs(self, **kwargs):
        """
        Sets additional attributes for the Metric object using keyword arguments.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def evaluate(
        self,
        inputs: Union[torch.Tensor, None],
        targets: Union[torch.Tensor, None],
        attributions: Union[torch.Tensor, None],
        **kwargs
    ) -> torch.Tensor:
        """
        Abstract method to evaluate the metric based on inputs, targets, and attributions.

        Parameters:
            inputs (Union[torch.Tensor, None]): 
                The input data for the model.
            targets (Union[torch.Tensor, None]): 
                The target labels for the input data.
            attributions (Union[torch.Tensor, None]): 
                The attributions generated by the explainer.
            **kwargs: 
                Additional keyword arguments.

        Returns:
            torch.Tensor: The result of the metric evaluation.
        """
        raise NotImplementedError
