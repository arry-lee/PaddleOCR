# copyright (c) 2021 PaddlePaddle Authors. All Rights Reserve.
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

__all__ = [
    "NLPBaseModel",
    "LayoutLMv2ForSer",
    "LayoutXLMForRe",
    "LayoutXLMForSer",
    "LayoutLMv2ForRe",
    "LayoutLMForSer",
]

from transformers import (
    LayoutLMForTokenClassification,
    LayoutLMModel,
    # LayoutLMv2ForRelationExtraction,
    LayoutLMv2ForTokenClassification,
    LayoutLMv2Model,
    # LayoutXLMForRelationExtraction,
    # LayoutXLMForTokenClassification,
    # LayoutXLMModel,
)
from ..layoutlmft.models.layoutlmv2 import LayoutLMv2ForRelationExtraction
from ..layoutlmft.models.layoutxlm import LayoutXLMForRelationExtraction,LayoutXLMForTokenClassification,LayoutXLMModel
from torch import nn


pretrained_model_dict = {
    LayoutXLMModel: {
        "Global": "layoutxlm-base-uncased",
        "vi": "vi-layoutxlm-base-uncased",
    },
    LayoutLMModel: {
        "Global": "layoutlm-base-uncased",
    },
    LayoutLMv2Model: {
        "Global": "layoutlmv2-base-uncased",
        "vi": "vi-layoutlmv2-base-uncased",
    },
}


class NLPBaseModel(nn.Module):
    def __init__(
        self,
        base_model_class,
        model_class,
        mode="Global",
        type="ser",
        pretrained=True,
        checkpoints=None,
        **kwargs
    ):
        super().__init__()
        if checkpoints is not None:  # load the trained model
            self.model = model_class.from_pretrained(checkpoints)
        else:  # load the pretrained-model
            pretrained_model_name = pretrained_model_dict[base_model_class][mode]
            if pretrained is True:
                base_model = base_model_class.from_pretrained(pretrained_model_name)
            else:
                base_model = base_model_class.from_pretrained(pretrained)
            if type == "ser":
                self.model = model_class.bottom_up(
                    base_model, num_classes=kwargs["num_classes"], dropout=None
                )
            else:
                self.model = model_class.bottom_up(base_model, dropout=None) # fixme
        self.out_channels = 1
        self.use_visual_backbone = True


class LayoutLMForSer(NLPBaseModel):
    def __init__(
        self, num_classes, pretrained=True, checkpoints=None, mode="Global", **kwargs
    ):
        super().__init__(
            LayoutLMModel,
            LayoutLMForTokenClassification,
            mode,
            "ser",
            pretrained,
            checkpoints,
            num_classes=num_classes,
        )
        self.use_visual_backbone = False

    def forward(self, x):
        x = self.model(
            input_ids=x[0],
            bbox=x[1],
            attention_mask=x[2],
            token_type_ids=x[3],
            position_ids=None,
            output_hidden_states=False,
        )
        return x


class LayoutLMv2ForSer(NLPBaseModel):
    def __init__(
        self, num_classes, pretrained=True, checkpoints=None, mode="Global", **kwargs
    ):
        super().__init__(
            LayoutLMv2Model,
            LayoutLMv2ForTokenClassification,
            mode,
            "ser",
            pretrained,
            checkpoints,
            num_classes=num_classes,
        )
        if (
            hasattr(self.model.layoutlmv2, "use_visual_backbone")
            and self.model.layoutlmv2.use_visual_backbone is False
        ):
            self.use_visual_backbone = False

    def forward(self, x):
        if self.use_visual_backbone is True:
            image = x[4]
        else:
            image = None
        x = self.model(
            input_ids=x[0],
            bbox=x[1],
            attention_mask=x[2],
            token_type_ids=x[3],
            image=image,
            position_ids=None,
            head_mask=None,
            labels=None,
        )
        if self.training:
            res = {"backbone_out": x[0]}
            res.update(x[1])
            return res
        else:
            return x


class LayoutXLMForSer(NLPBaseModel):
    def __init__(
        self, num_classes, pretrained=True, checkpoints=None, mode="Global", **kwargs
    ):
        super().__init__(
            LayoutXLMModel,
            LayoutXLMForTokenClassification,
            mode,
            "ser",
            pretrained,
            checkpoints,
            num_classes=num_classes,
        )
        if (
            hasattr(self.model.layoutlmv2, "use_visual_backbone")
            and self.model.layoutlmv2.has_visual_segment_embedding is False
        ):
            self.use_visual_backbone = False

    def forward(self, x):
        if self.use_visual_backbone is True:
            image = x[4]
        else:
            image = None
        x = self.model(
            input_ids=x[0],
            bbox=x[1],
            attention_mask=x[2],
            token_type_ids=x[3],
            image=image,
            position_ids=None,
            head_mask=None,
            labels=None,
        )
        if self.training:
            res = {"backbone_out": x[0]}
            res.update(x[1])
            return res
        else:
            return x


class LayoutLMv2ForRe(NLPBaseModel):
    def __init__(self, pretrained=True, checkpoints=None, mode="Global", **kwargs):
        super().__init__(
            LayoutLMv2Model,
            LayoutLMv2ForRelationExtraction,
            mode,
            "re",
            pretrained,
            checkpoints,
        )
        if (
            hasattr(self.model.layoutlmv2, "use_visual_backbone")
            and self.model.layoutlmv2.use_visual_backbone is False
        ):
            self.use_visual_backbone = False

    def forward(self, x):
        x = self.model(
            input_ids=x[0],
            bbox=x[1],
            attention_mask=x[2],
            token_type_ids=x[3],
            image=x[4],
            position_ids=None,
            head_mask=None,
            labels=None,
            entities=x[5],
            relations=x[6],
        )
        return x


class LayoutXLMForRe(NLPBaseModel):
    def __init__(self, pretrained=True, checkpoints=None, mode="Global", **kwargs):
        super().__init__(
            LayoutXLMModel,
            LayoutXLMForRelationExtraction,
            mode,
            "re",
            pretrained,
            checkpoints,
        )
        if (
            hasattr(self.model.layoutxlm, "use_visual_backbone")
            and self.model.layoutxlm.use_visual_backbone is False
        ):
            self.use_visual_backbone = False

    def forward(self, x):
        if self.use_visual_backbone is True:
            image = x[4]
            entities = x[5]
            relations = x[6]
        else:
            image = None
            entities = x[4]
            relations = x[5]
        x = self.model(
            input_ids=x[0],
            bbox=x[1],
            attention_mask=x[2],
            token_type_ids=x[3],
            image=image,
            position_ids=None,
            head_mask=None,
            labels=None,
            entities=entities,
            relations=relations,
        )
        return x
