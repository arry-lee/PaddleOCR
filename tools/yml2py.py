import os.path
from collections import defaultdict

import torch
import yaml
from ptocr import hub as self


def hub(name, model_type=None):
    """
    Get model from model zoo.
    Args:
        name (str): model name in model zoo.
        model_type (str): model type.
    Returns:
        model (nn.Module): model.
    """
    module_dict = self.module_dict
    if name in module_dict:
        if len(module_dict[name]) == 1:
            return module_dict[name][0]
        else:
            if model_type is not None:
                for one in module_dict[name]:
                    if one.rsplit(".", 1)[1].startswith(model_type.lower()):
                        return one
    if hasattr(torch.optim, name):
        return "torch.optim"
    elif hasattr(torch.optim.lr_scheduler, name):
        return "torch.optim.lr_scheduler"
    return "torch.nn"


def squizee(imports):
    x = defaultdict(set)
    for i in imports:
        l, r = i.rsplit(" ", 1)
        x[l].add(r)
    lines = []
    for k, v in x.items():
        lines.append(f"{k} {', '.join(v)}")
    return lines


def yaml2py(old_file):
    path = os.path.dirname(os.path.abspath(old_file))

    with open(old_file, "r") as f:
        yml_data = yaml.safe_load(f)

    g = yml_data["Global"]
    m = yml_data["Model"]
    # print(yml_data)

    imports = ["from configs.config import ConfigModel,_"]

    mode = m.pop("model_type")
    algo = m.pop("algorithm")
    lines = ["class Model(ConfigModel):"]
    for key, value in g.items():
        if isinstance(value, str):
            value = f'"{value}"'
        lines.append(f"    {key} = {value}")

    lines.append(f"    model_type = '{mode}'")
    lines.append(f"    algorithm = '{algo}'")
    backbone = m["Backbone"]["class"]
    for key, value in m.items():
        if isinstance(value, str):
            value = f'"{value}"'
        elif isinstance(value, dict):
            class_ = value.pop("class")

            imports.append(f"from {hub(class_, mode)} import {class_}")
            kw = []
            for k, v in value.items():
                if isinstance(v, str):
                    v = f'"{v}"'
                kw.append(f"{k}={v}")
            kw = ", ".join(kw)
            value = f"_({class_}, {kw})"

        lines.append(f"    {key} = {value}")

    for n in ["Loss", "Metric"]:
        l = yml_data[n]
        cls = l.pop("class")
        imports.append(f"from {hub(cls, mode)} import {cls}")
        kw = []
        for k, v in l.items():
            if isinstance(v, str):
                v = f'"{v}"'
            kw.append(f"{k}={v}")
        kw = ", ".join(kw)
        lines.append(f"    {n.lower()} = {cls}({kw})")

    for n in ["Optimizer", "LRScheduler", "PostProcessor"]:
        l = yml_data[n]
        if l == None:
            v = "None"
        else:
            cls = l.pop("class")
            imports.append(f"from {hub(cls, mode)} import {cls}")
            kw = []
            for k, v in l.items():
                if isinstance(v, str):
                    v = f'"{v}"'
                kw.append(f"{k}={v}")
            kw = ", ".join(kw)
            v = f"_({cls},{kw})"
        lines.append(f"    {n} = {v}")

    for t in ["Train", "Eval"]:
        lines.append(f"    class {t}:")
        d = yml_data[t]
        ds = d["Dataset"]
        trs = ds.pop("transforms", None)
        cls = ds.pop("class")
        imports.append(f"from {hub(cls, mode)} import {cls}")
        kw = []
        for k, v in ds.items():
            if isinstance(v, str):
                v = f'"{v}"'
            kw.append(f"{k}={v}")
        kw = ", ".join(kw)
        lines.append(f"        Dataset = _({cls}, {kw})")
        if trs != None:
            vs = []
            for i in trs:
                if i is not None:
                    cls = i.pop("class")
                    imports.append(f"from {hub(cls, mode)} import {cls}")
                    kw = []
                    for k, v in i.items():
                        if isinstance(v, str):
                            v = f'"{v}"'
                        kw.append(f"{k}={v}")
                    kw = f"{cls}({', '.join(kw)})"
                else:
                    kw = "None"
                vs.append(kw)
            vs = ", ".join(vs)
            lines.append(f"        transforms = _[{vs}]")
        else:
            lines.append(f"        transforms = None")

        dl = d["DataLoader"]
        # cls = dl.pop('class')
        kw = []
        for k, v in dl.items():
            if isinstance(v, str):
                v = f'"{v}"'
            kw.append(f"{k}={v}")
        kw = ", ".join(kw)
        lines.append(f"        DATALOADER = _({kw})")

    # print('\n'.join(lines))

    explain = ["# This .py is auto generated by the script in the root folder."]

    lines = explain + squizee(imports) + lines

    filename = os.path.join(path, f"{mode}_{algo}_{backbone}.py".lower())

    with open(filename, "w") as f:
        f.write("\n".join(lines))


def convert_yml_to_yaml(folder_path):
    # 遍历文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".yml"):
                # 构造旧文件路径和新文件路径
                old_file = os.path.join(root, filename)
                try:
                    yaml2py(old_file)
                except Exception as e:
                    print(e)
                    print(old_file)


if __name__ == "__main__":
    convert_yml_to_yaml(".")

# load D:\dev\github\PaddleOCR\ppocr\module_map.yml
# 'Backbone'
# .\det\ch_PP-OCRv2\ch_PP-OCRv2_det_cml.yml
# 'Backbone'
# .\det\ch_PP-OCRv2\ch_PP-OCRv2_det_distill.yml
# 'Backbone'
# .\det\ch_PP-OCRv2\ch_PP-OCRv2_det_dml.yml
# 'Backbone'
# .\det\ch_PP-OCRv3\ch_PP-OCRv3_det_cml.yml
# 'Backbone'
# .\det\ch_PP-OCRv3\ch_PP-OCRv3_det_dml.yml
# 'class'
# .\kie\layoutlm_series\re_layoutlmv2_xfund_zh.yml
# 'class'
# .\kie\layoutlm_series\re_layoutxlm_xfund_zh.yml
# 'class'
# .\kie\vi_layoutxlm\re_vi_layoutxlm_xfund_zh.yml
# 'Backbone'
# .\kie\vi_layoutxlm\re_vi_layoutxlm_xfund_zh_udml.yml
# 'Backbone'
# .\kie\vi_layoutxlm\ser_vi_layoutxlm_xfund_zh_udml.yml
# 'Backbone'
# .\rec\ch_PP-OCRv2\ch_PP-OCRv2_rec_distillation.yml
# 'Backbone'
# .\rec\PP-OCRv3\ch_PP-OCRv3_rec_distillation.yml
# 'Backbone'
# .\sr\sr_telescope.yml
# 'Backbone'
# .\sr\sr_tsrn_transformer_strock.yml
