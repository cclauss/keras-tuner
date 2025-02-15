# Copyright 2019 The Keras Tuner Authors
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import pytest
import numpy as np
from kerastuner.engine.metric import Metric
from kerastuner.collections import MetricsCollection


@pytest.fixture()
def mc():
    return MetricsCollection()


def test_metric_name_add(mc):
    mc.add('binary_accuracy')
    metric = mc.get('binary_accuracy')
    assert isinstance(metric, Metric)
    assert metric.direction == 'max'
    assert metric.name == 'binary_accuracy'


def test_metric_obj_add(mc):
    mm = Metric('test', 'min')
    mc.add(mm)
    metric = mc.get('test')
    assert isinstance(metric, Metric)
    assert metric.direction == 'min'
    assert metric.name == 'test'
    assert mm == metric


def test_add_invalid_name(mc):
    with pytest.raises(ValueError):
        mc.add('invalid')


def test_duplicate_name(mc):
    mc.add('loss')
    with pytest.raises(ValueError):
        mc.add('loss')


def test_duplicate_obj(mc):
    mm = Metric('acc', 'min')
    mc.add(mm)
    with pytest.raises(ValueError):
        mc.add(mm)


def test_get_metrics(mc):
    mc.add('loss')
    mc.add('binary_accuracy')
    mc.add('val_binary_accuracy')
    metrics = mc.to_list()
    assert len(metrics) == 3
    # ensure metrics are properly sorted
    assert metrics[0].name == 'binary_accuracy'
    assert metrics[1].name == 'loss'
    assert metrics[2].name == 'val_binary_accuracy'


def test_update_min(mc):
    mc.add('loss')
    # check if update tell us it improved
    assert mc.update('loss', 10)
    # check if update tell us it didn't improve
    assert not mc.update('loss', 12)
    mm = mc.get('loss')
    assert mm.get_best_value() == 10
    assert mm.get_last_value() == 12


def test_update_max(mc):
    mc.add('accuracy')
    # check if update tell us it improved
    assert mc.update('accuracy', 10)
    # check if update tell us it didn't improve
    assert mc.update('accuracy', 12)
    mm = mc.get('accuracy')
    assert mm.get_best_value() == 12
    assert mm.get_last_value() == 12


def test_to_dict(mc):
    mc.add('loss')
    mc.add('accuracy')
    mc.add('val_loss')

    mc.update('loss', 1)
    mc.update('accuracy', 2)
    mc.update('val_loss', 3)

    config = mc.to_dict()
    assert config['accuracy'].name == 'accuracy'
    assert config['accuracy'].get_best_value() == 2
    assert len(config) == 3


def test_serialization(mc):
    mc.add('loss')
    arr = np.asarray([0.1, 0.2], dtype=np.float32)
    mc.update('loss', arr[0])
    config = mc.to_config()
    assert config == json.loads(json.dumps(config))


def test_alias(mc):
    mc.add('acc')
    mm = mc.get('acc')
    assert mm.name == 'accuracy'
    mm2 = mc.get('accuracy')
    assert mm2.name == 'accuracy'
    assert mm == mm2


def test_alias_update(mc):
    mc.add('accuracy')
    mc.update('acc', 14)
    mc.update('acc', 12)
    mm = mc.get('acc')
    assert mm.history == [14, 12]
    assert mm.get_best_value() == 14
    assert mm.get_last_value() == 12


def test_set_objective(mc):
    mc.add('loss')
    mc.add('binary_accuracy')
    mc.add('val_binary_accuracy')
    mm = mc.get('binary_accuracy')
    assert not mm.is_objective
    mc.set_objective('val_binary_accuracy')
    mm = mc.get('val_binary_accuracy')
    assert mm.is_objective


def test_set_invalid_objective(mc):
    with pytest.raises(ValueError):
        mc.set_objective('3713')


def test_set_shortand_objective(mc):
    mc.add('accuracy')
    mc.set_objective('acc')
    assert mc._objective_name == 'accuracy'


def test_set_shortand_val_objective(mc):
    mc.add('val_accuracy')
    mc.set_objective('val_acc')
    assert mc._objective_name == 'val_accuracy'


def test_objective_special_acc_aliasing(mc):
    # only on some TF version the metric is the instanciation of the accuracy
    mc.add('binary_accuracy')
    mc.set_objective('acc')
    assert mc._objective_name == 'binary_accuracy'


def test_objective_special_acc_aliasing2(mc):
    # only on some TF version the metric is the instanciation of the accuracy
    mc.add('val_binary_accuracy')
    mc.set_objective('val_acc')
    assert mc._objective_name == 'val_binary_accuracy'


def test_objective_special_acc_aliasing3(mc):
    # only on some TF version the metric is the instanciation of the accuracy
    mc.add('binary_accuracy')
    mc.add('val_binary_accuracy')
    mc.add('loss')
    mc.set_objective('val_acc')
    assert mc._objective_name == 'val_binary_accuracy'


def test_objective_invalid_special_acc_aliasing(mc):
    # only on some TF version the metric is the instanciation of the accuracy
    mc.add('binary_accuracy')
    with pytest.raises(ValueError):
        mc.set_objective('val_acc')


def test_objective_invalid_special_acc_aliasing2(mc):
    # only on some TF version the metric is the instanciation of the accuracy
    mc.add('val_binary_accuracy')
    with pytest.raises(ValueError):
        mc.set_objective('acc')


def test_double_objective(mc):
    mc.add('loss')
    mc.add('accuracy')
    mc.set_objective('accuracy')
    with pytest.raises(ValueError):
        mc.set_objective('loss')


def test_from_config_to_config(mc):
    m = Metric("loss", "min")
    mc = MetricsCollection()
    mc.add(m)
    mc.update("loss", .5)

    config = mc.to_config()
    mc2 = MetricsCollection.from_config(config)
    mcl = mc.to_list()
    mc2l = mc2.to_list()

    assert mc2._objective_name == mc._objective_name
    for idx in range(len(mcl)):
        assert mcl[idx].name == mc2l[idx].name
        assert mcl[idx].get_last_value() == mc2l[idx].get_last_value()


def test_from_config_to_config_no_val():
    m = Metric("loss", "min")
    mc = MetricsCollection()
    mc.add(m)
    mc.update("loss", .5)

    config = mc.to_config()
    mc2 = MetricsCollection.from_config(config, with_values=False)
    mcl = mc.to_list()
    mc2l = mc2.to_list()

    assert mc2._objective_name == mc._objective_name
    assert len(mcl) == 1
    assert len(mc2l) == 1

    assert mcl[0].get_last_value() == .5
    assert mc2l[0].get_last_value() is None
