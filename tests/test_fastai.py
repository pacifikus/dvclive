import os

import pytest
from fastai.tabular.all import (
    Categorify,
    FillMissing,
    Normalize,
    TabularDataLoaders,
    URLs,
    accuracy,
    tabular_learner,
    untar_data,
)

import dvclive
from dvclive.fastai import DvcLiveCallback

# pylint: disable=redefined-outer-name, unused-argument


@pytest.fixture
def data_loader():
    path = untar_data(URLs.ADULT_SAMPLE)

    dls = TabularDataLoaders.from_csv(
        path / "adult.csv",
        path=path,
        y_names="salary",
        cat_names=[
            "workclass",
            "education",
            "marital-status",
            "occupation",
            "relationship",
            "race",
        ],
        cont_names=["age", "fnlwgt", "education-num"],
        procs=[Categorify, FillMissing, Normalize],
    )
    return dls


def test_fastai_callback(tmp_dir, data_loader):
    dvclive.init("dvc_logs")

    learn = tabular_learner(data_loader, metrics=accuracy)
    learn.model_dir = os.path.abspath("./")
    learn.fit_one_cycle(2, cbs=[DvcLiveCallback("model")])

    assert os.path.exists("dvc_logs")

    train_path = tmp_dir / "dvc_logs/train"
    valid_path = tmp_dir / "dvc_logs/valid"

    assert train_path.is_dir()
    assert valid_path.is_dir()
    assert (tmp_dir / "dvc_logs/accuracy.tsv").exists()


def test_fastai_model_file(tmp_dir, data_loader):
    dvclive.init("dvc_logs")

    learn = tabular_learner(data_loader, metrics=accuracy)
    learn.model_dir = os.path.abspath("./")
    learn.fit_one_cycle(2, cbs=[DvcLiveCallback("model")])
    assert (tmp_dir / "model.pth").is_file()
