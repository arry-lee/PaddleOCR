# copyright (c) 2019 PaddlePaddle Authors. All Rights Reserve.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import torch
from torch import nn
import torch.nn.functional as F
from torch import ParamAttr


def get_bias_attr(k):
    stdv = 1.0 / math.sqrt(k * 1.0)
    initializer = torch.nn.initializer.Uniform(-stdv, stdv)
    bias_attr = ParamAttr(initializer=initializer)
    return bias_attr


class Head(nn.Module):
    def __init__(self, in_channels, kernel_list=[3, 2, 2], **kwargs):
        super(Head, self).__init__()

        self.conv1 = nn.Conv2d(
            in_channels=in_channels,
            out_channels=in_channels // 4,
            kernel_size=kernel_list[0],
            padding=int(kernel_list[0] // 2),
            weight_attr=ParamAttr(),
            bias_attr=False)
        self.conv_bn1 = nn.BatchNorm2d(
            num_channels=in_channels // 4,
            param_attr=ParamAttr(
                initializer=torch.nn.initializer.Constant(value=1.0)),
            bias_attr=ParamAttr(
                initializer=torch.nn.initializer.Constant(value=1e-4)),
            act='relu')
        self.conv2 = nn.Conv2DTranspose(
            in_channels=in_channels // 4,
            out_channels=in_channels // 4,
            kernel_size=kernel_list[1],
            stride=2,
            weight_attr=ParamAttr(
                initializer=torch.nn.initializer.KaimingUniform()),
            bias_attr=get_bias_attr(in_channels // 4))
        self.conv_bn2 = nn.BatchNorm2d(
            num_channels=in_channels // 4,
            param_attr=ParamAttr(
                initializer=torch.nn.initializer.Constant(value=1.0)),
            bias_attr=ParamAttr(
                initializer=torch.nn.initializer.Constant(value=1e-4)),
            act="relu")
        self.conv3 = nn.Conv2DTranspose(
            in_channels=in_channels // 4,
            out_channels=1,
            kernel_size=kernel_list[2],
            stride=2,
            weight_attr=ParamAttr(
                initializer=torch.nn.initializer.KaimingUniform()),
            bias_attr=get_bias_attr(in_channels // 4), )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv_bn1(x)
        x = self.conv2(x)
        x = self.conv_bn2(x)
        x = self.conv3(x)
        x = F.sigmoid(x)
        return x


class DBHead(nn.Module):
    """
    Differentiable Binarization (DB) for text detection:
        see https://arxiv.org/abs/1911.08947
    args:
        params(dict): super parameters for build DB network
    """

    def __init__(self, in_channels, k=50, **kwargs):
        super(DBHead, self).__init__()
        self.k = k
        self.binarize = Head(in_channels, **kwargs)
        self.thresh = Head(in_channels, **kwargs)

    def step_function(self, x, y):
        return torch.reciprocal(1 + torch.exp(-self.k * (x - y)))

    def forward(self, x, targets=None):
        shrink_maps = self.binarize(x)
        if not self.training:
            return {'maps': shrink_maps}

        threshold_maps = self.thresh(x)
        binary_maps = self.step_function(shrink_maps, threshold_maps)
        y = torch.concat([shrink_maps, threshold_maps, binary_maps], axis=1)
        return {'maps': y}
