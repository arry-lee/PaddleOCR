# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.





import json
import os
import sys

import numpy as np

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, "..")))

os.environ["FLAGS_allocator_strategy"] = "auto_growth"

import torch

from ppocr.data import create_operators, transform
from ppocr.modeling.architectures import build_model
from ppocr.postprocess import build_post_process
from ppocr.utils.save_load import load_model
from ppocr.utils.utility import get_image_file_list
import tools.program as program


def main():
    global_config = config["Global"]

    # build post process
    post_process_class = build_post_process(config["PostProcessor"], global_config)

    # build model
    if hasattr(post_process_class, "character"):
        char_num = len(getattr(post_process_class, "character"))
        if config["Model"]["algorithm"] in [
            "Distillation",
        ]:  # distillation model
            for key in config["Model"]["Models"]:
                if config["Model"]["Models"][key]["Head"]["name"] == "MultiHead":  # for multi head
                    out_channels_list = {}
                    if config["PostProcessor"]["name"] == "DistillationSARLabelDecode":
                        char_num = char_num - 2
                    out_channels_list["CTCLabelDecode"] = char_num
                    out_channels_list["SARLabelDecode"] = char_num + 2
                    config["Model"]["Models"][key]["Head"]["out_channels_list"] = out_channels_list
                else:
                    config["Model"]["Models"][key]["Head"]["out_channels"] = char_num
        elif config["Model"]["Head"]["name"] == "MultiHead":  # for multi head loss
            out_channels_list = {}
            if config["PostProcessor"]["name"] == "SARLabelDecode":
                char_num = char_num - 2
            out_channels_list["CTCLabelDecode"] = char_num
            out_channels_list["SARLabelDecode"] = char_num + 2
            config["Model"]["Head"]["out_channels_list"] = out_channels_list
        else:  # base rec model
            config["Model"]["Head"]["out_channels"] = char_num

    model = build_model(config["Model"])

    load_model(config, model)

    # create data ops
    transforms = []
    for op in config["Eval"]["Dataset"]["transforms"]:
        op_name = list(op)[0]
        if "Label" in op_name:
            continue
        elif op_name in ["RecResizeImg"]:
            op[op_name]["infer_mode"] = True
        elif op_name == "KeepKeys":
            if config["Model"]["algorithm"] == "SRN":
                op[op_name]["keep_keys"] = [
                    "image",
                    "encoder_word_pos",
                    "gsrm_word_pos",
                    "gsrm_slf_attn_bias1",
                    "gsrm_slf_attn_bias2",
                ]
            elif config["Model"]["algorithm"] == "SAR":
                op[op_name]["keep_keys"] = ["image", "valid_ratio"]
            elif config["Model"]["algorithm"] == "RobustScanner":
                op[op_name]["keep_keys"] = ["image", "valid_ratio", "word_positons"]
            else:
                op[op_name]["keep_keys"] = ["image"]
        transforms.append(op)
    global_config["infer_mode"] = True
    ops = create_operators(transforms, global_config)

    save_res_path = config["Global"].get("save_res_path", "./output/rec/predicts_rec.txt")
    if not os.path.exists(os.path.dirname(save_res_path)):
        os.makedirs(os.path.dirname(save_res_path))

    model.eval()

    with open(save_res_path, "w") as fout:
        for file in get_image_file_list(config["Global"]["infer_img"]):
            logger.info("infer_img: {}".format(file))
            with open(file, "rb") as f:
                img = f.read()
                data = {"image": img}
            batch = transform(data, ops)
            if config["Model"]["algorithm"] == "SRN":
                encoder_word_pos_list = np.expand_dims(batch[1], axis=0)
                gsrm_word_pos_list = np.expand_dims(batch[2], axis=0)
                gsrm_slf_attn_bias1_list = np.expand_dims(batch[3], axis=0)
                gsrm_slf_attn_bias2_list = np.expand_dims(batch[4], axis=0)

                others = [
                    torch.Tensor(encoder_word_pos_list),
                    torch.Tensor(gsrm_word_pos_list),
                    torch.Tensor(gsrm_slf_attn_bias1_list),
                    torch.Tensor(gsrm_slf_attn_bias2_list),
                ]
            if config["Model"]["algorithm"] == "SAR":
                valid_ratio = np.expand_dims(batch[-1], axis=0)
                img_metas = [torch.Tensor(valid_ratio)]
            if config["Model"]["algorithm"] == "RobustScanner":
                valid_ratio = np.expand_dims(batch[1], axis=0)
                word_positons = np.expand_dims(batch[2], axis=0)
                img_metas = [
                    torch.Tensor(valid_ratio),
                    torch.Tensor(word_positons),
                ]
            if config["Model"]["algorithm"] == "CAN":
                image_mask = torch.ones((np.expand_dims(batch[0], dim=0).shape), dtype=torch.float32)
                label = torch.ones((1, 36), dtype=torch.int64)
            images = np.expand_dims(batch[0], axis=0)
            images = torch.Tensor(images)
            if config["Model"]["algorithm"] == "SRN":
                preds = model(images, others)
            elif config["Model"]["algorithm"] == "SAR":
                preds = model(images, img_metas)
            elif config["Model"]["algorithm"] == "RobustScanner":
                preds = model(images, img_metas)
            elif config["Model"]["algorithm"] == "CAN":
                preds = model([images, image_mask, label])
            else:
                preds = model(images)
            post_result = post_process_class(preds)
            info = None
            if isinstance(post_result, dict):
                rec_info = dict()
                for key in post_result:
                    if len(post_result[key][0]) >= 2:
                        rec_info[key] = {
                            "label": post_result[key][0][0],
                            "score": float(post_result[key][0][1]),
                        }
                info = json.dumps(rec_info, ensure_ascii=False)
            elif isinstance(post_result, list) and isinstance(post_result[0], int):
                # for RFLearning CNT branch
                info = str(post_result[0])
            else:
                if len(post_result[0]) >= 2:
                    info = post_result[0][0] + "\t" + str(post_result[0][1])

            if info is not None:
                logger.info("\t result: {}".format(info))
                fout.write(file + "\t" + info + "\n")
    logger.info("success!")


if __name__ == "__main__":
    config, device, logger, vdl_writer = program.preprocess()
    main()
