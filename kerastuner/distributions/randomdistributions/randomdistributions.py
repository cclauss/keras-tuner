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

from kerastuner import distributions
from kerastuner.abstractions.display import fatal
import random
from numpy import linspace, logspace


class RandomDistributions(distributions.Distributions):
    """Random distributions

    Args:
        hyperparameters_config (dict): hyperparameters dict describing
        the search space. Often refered as hparams. Generated using
        DummyDistributions() in Tuner()
    """

    def __init__(self, hyperparameters_config):
        super(RandomDistributions, self).__init__('RandomDistributions',
                                                  hyperparameters_config)

    def Fixed(self, name, value, group="default"):
        """Return a fixed selected value
        Args:
            name (str): name of the parameter
            value: value of the parameter
            group (str): Optional logical grouping of the parameters
        Returns:
            fixed value
        """
        self._record_hyperparameter(name, value, group)
        return value

    def Boolean(self, name, group="default"):
        """Return a random Boolean value.
        Args:
            name (str): name of the parameter
            group (str): Optional logical grouping of the parameters
        Returns:
            an Boolean
        """
        value = random.choice([False, True])
        self._record_hyperparameter(name, value, group)
        return value

    def Choice(self, name, selection, group="default"):
        """Return a random value from an explicit list of choice.
        Args:
            name (str): name of the parameter
            selection (list): list of explicit choices
            group (str): Optional logical group name this parameter belongs to
        Returns:
            an element of the list provided
        """
        value = random.choice(selection)
        if isinstance(selection[0], int):
            value = int(value)
        elif isinstance(selection[0], float):
            value = float(value)
        elif isinstance(selection[0], str):
            value = str(value)
        else:
            Exception('unknown type')
        self._record_hyperparameter(name, value, group)
        return value

    def Range(self, name, start, stop, increment=1, group='default'):
        """Return a random value from a range.
        Args:
            name (str): name of the parameter
            start (int/float): lower bound of the range
            stop (int/float): upper bound of the range
            increment (int/float): incremental step
        Returns:
            an element of the range
        """
        my_range = list(range(start, stop, increment))
        value = random.choice(my_range)
        self._record_hyperparameter(name, value, group)
        return value

    def Logarithmic(self, name, start, stop, num_buckets, precision=0,
                    group='default'):
        """Return a random value from a range which is logarithmically divided.
        Args:
            name (str): name of the parameter
            start (int/float): lower bound of the range
            stop (int/float): upper bound of the range
            num_buckets (int): into how many buckets to divided the range in
            precision (int): For float range. Round the result rounded to the
                            nth decimal if needed. 0 means not rounded
        Returns:
            an element of the range
        """
        my_range = logspace(start, stop, num_buckets)
        value = random.choice(my_range)
        self._record_hyperparameter(name, value, group)
        return value

    def Linear(self, name, start, stop, num_buckets, precision=0,
               group='default'):
        """Return a random value from a range which is linearly divided.
        Args:
            name (str): name of the parameter
            start (int/float): lower bound of the range
            stop (int/float): upper bound of the range
            num_buckets (int): into how many buckets to divided the range in
            precision (int): For float range. Round the result rounded to the
                            nth decimal if needed. 0 means not rounded
        Returns:
            an element of the range
        """
        my_range = linspace(start, stop, num_buckets)
        value = random.choice(my_range)
        if precision:
            value = round(value, precision)
        self._record_hyperparameter(name, value, group)
        return value
