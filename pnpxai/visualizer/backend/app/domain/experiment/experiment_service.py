from torch.utils.data import DataLoader
import plotly.express as px
import numpy as np


class ExperimentService:
    @classmethod
    def get_inputs_list(cls, experiment):
        data = experiment.data
        if isinstance(data, DataLoader):
            data = data.dataset

        data = list(map(experiment.input_extractor, data))

        return data

    @classmethod
    def get_task_formatted_inputs(cls, experiment, inputs=None):
        inputs = inputs or cls.get_inputs_list(experiment)
        if experiment.is_image_task:
            inputs = cls._format_image_inputs(
                inputs, experiment.input_visualizer)

        return inputs

    @classmethod
    def _format_image_inputs(cls, inputs, visualizer=None):
        formatted = []
        for datum in inputs:
            datum: np.ndarray = datum.cpu()
            # Scale to RGB, if between 0 and 1
            if datum.max() <= 1 and datum.min() >= 0:
                datum = (datum * 255).astype(int)

            if visualizer is not None:
                datum = visualizer(datum)
                fig = px.imshow(datum)

            formatted.append(fig.to_dict())

        return formatted

    @classmethod
    def run(cls, experiment, inputs=None, explainers=None):
        experiment.run(inputs, explainers)

        return experiment