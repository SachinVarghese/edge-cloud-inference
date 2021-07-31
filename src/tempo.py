from typing import Tuple

import numpy as np
from src.train import CloudModelFolder, EdgeModelFolder

from tempo.serve.metadata import ModelFramework, RuntimeOptions, KubernetesOptions
from tempo.seldon.k8s import SeldonCoreOptions
from tempo.serve.model import Model
from tempo.serve.pipeline import Pipeline, PipelineModels
from tempo.serve.utils import pipeline

PipelineFolder = "joint-classifier"
EdgePredictionTag = "edge prediction"
CloudPredictionTag = "cloud prediction"

edgeRuntimeOptions = RuntimeOptions()  # Docker Runtime
edgeRuntimeOptions.k8s_options = KubernetesOptions(
    replicas=1, namespace="production", nodeName="edge-compute",
)


cloudRuntimeOptions = SeldonCoreOptions()  # Kubernetes Runtime
cloudRuntimeOptions.k8s_options = KubernetesOptions(
    replicas=2,
    namespace="production",
    nodeName="gke-kubeedge-cloudcore-default-pool-4dbe91a1-v7e5",
)


def get_tempo_artifacts(artifacts_folder: str) -> Tuple[Pipeline, Model, Model]:

    cloud_model = Model(
        name="cloud-model",
        platform=ModelFramework.XGBoost,
        local_folder=f"{artifacts_folder}/{CloudModelFolder}",
        uri="s3://tempo/joint-inference/cloud",
        description="An Cloud based Iris classification model",
        runtime_options=cloudRuntimeOptions,
    )

    edge_model = Model(
        name="edge-model",
        platform=ModelFramework.SKLearn,
        local_folder=f"{artifacts_folder}/{EdgeModelFolder}",
        uri="s3://tempo/joint-inference/edge",
        description="An Edge based Iris classification model",
        runtime_options=edgeRuntimeOptions,
    )

    @pipeline(
        name="joint-classifier",
        uri="s3://tempo/basic/pipeline",
        local_folder=f"{artifacts_folder}/{PipelineFolder}",
        models=PipelineModels(edge_inference=edge_model, cloud_inference=cloud_model),
        description="A pipeline to make an edge based prediction or cloud based joint prediction for Iris classification",
        runtime_options=edgeRuntimeOptions,
    )
    def classifier(payload: np.ndarray) -> Tuple[np.ndarray, str]:
        # Custom Logic for hard example mining based on threshold, IBT, Cross Entropy etc
        res1 = classifier.models.edge_inference(input=payload)
        if res1[0] == 1:
            return res1, EdgePredictionTag
        else:
            return classifier.models.cloud_inference(input=payload), CloudPredictionTag

    return classifier, edge_model, cloud_model
