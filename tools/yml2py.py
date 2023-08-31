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
            # print(name,module_dict[name])
            if model_type is not None:
                for one in module_dict[name]:
                    if model_type.lower() in one:
                        return one
    if hasattr(torch.optim, name):
        return "torch.optim"
    elif hasattr(torch.optim.lr_scheduler, name):
        return "torch.optim.lr_scheduler"
    print("model not found in model zoo, please check the name {}".format(name))
    raise


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

    imports = ["from ptocr.config import ConfigModel,_"]

    mode = m.pop("model_type")
    algo = m.pop("algorithm")
    lines = ["class Model(ConfigModel):"]
    g['pretrained_model']=None
    g['save_model_dir'] = None
    for key, value in g.items():
        if key in ['infer_img','save_res_path','Transform']: # skip
            continue

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

    for n in ["Loss", "Metric", "PostProcessor"]:
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

    for n in ["Optimizer", "LRScheduler"]:
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

    trans_train_eval2(imports, lines, mode, yml_data)

    # print('\n'.join(lines))

    explain = [
        "# This .pyi is auto generated by the script in the root folder.",
        "# only for cache,use .py for changes",
    ]

    lines = explain + squizee(imports) + lines

    filename = os.path.join(path, f"{mode}_{algo}_{backbone}.pyi".lower())
    # os.remove(filename)
    new = filename.replace("configs", "models")
    os.makedirs(os.path.dirname(new), exist_ok=True)
    with open(new, "w") as f:
        f.write("\n".join(lines))


def trans_train_eval(imports, lines, mode, yml_data):
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


def trans_train_eval2(imports, lines, mode, yml_data):
    e = yml_data["Eval"]["Dataset"]
    t = yml_data["Train"]["Dataset"]
    lines.append(f"    class Data:")
    cls_e = e.pop("class")
    cls_t = t.pop("class")
    imports.append(f"from {hub(cls_e, mode)} import {cls_e}")
    imports.append(f"from {hub(cls_t, mode)} import {cls_t}")

    trs_e = e.pop("transforms")
    trs_t = t.pop("transforms")

    if cls_e == cls_t:
        lines.append(f"        dataset = {cls_e}")
    else:
        lines.append(f"        dataset:{cls_e} = {cls_t}")
    e_root = e['root']
    t_root = t['root']
    for k in e:
        if isinstance(e[k],str):
            e[k] = f'"{e[k].removeprefix("./")}"'
        if isinstance(t[k],str):
            t[k] = f'"{t[k].removeprefix("./")}"'

        if isinstance(e[k],list):
            e[k]=[f"{i.removeprefix(e_root)}" if isinstance(i,str) else i for i in e[k]]
            if len(e[k])==1:
                e[k]=f'"{e[k][0]}"'

        if isinstance(t[k],list):
            t[k]=[f"{i.removeprefix(t_root)}" if isinstance(i,str) else i for i in t[k]]
            if len(t[k])==1:
                t[k]=f'"{t[k][0]}"'

        if e[k] == t[k]:
            lines.append(f"        {k} = {e[k]}")
        else:
            lines.append(f"        {k}:{e[k]} = {t[k]}")

    e = yml_data["Eval"]["DataLoader"]
    t = yml_data["Train"]["DataLoader"]
    lines.append(f"    class Loader:")
    for k in e:
        if e[k] == t.get(k,e[k]):
            lines.append(f"        {k.replace('use_shared_memory','pin_memory')} = {e[k]}")
        else:
            lines.append(f"        {k.replace('use_shared_memory','pin_memory')}:{e[k]} = {t[k]}")

    lst = []
    for i in trs_t:
        if i is not None:
            cls = i.pop("class")
            imports.append(f"from {hub(cls, mode)} import {cls}")
            if cls == 'KeepKeys':
                kw = [f'"{x}"' for x in i["keep_keys"]]
                kw = f'KeepKeys({",".join(kw)})'
                lst.append(kw)
                continue

            kw = []
            for k, v in i.items():
                if isinstance(v, str):
                    v = f'"{v}"'
                kw.append(f"{k}={v}")
            kw = f"{cls}({', '.join(kw)})"
        else:
            kw = "None"
        lst.append(kw)

    lse = []
    for i in trs_e:
        if i is not None:
            cls = i.pop("class")
            imports.append(f"from {hub(cls, mode)} import {cls}")
            if cls == 'KeepKeys':
                kw = [f'"{x}"' for x in i["keep_keys"]]
                kw = f'KeepKeys({",".join(kw)})'
                lse.append(kw)
                continue
            kw = []
            for k, v in i.items():
                if isinstance(v, str):
                    v = f'"{v}"'
                kw.append(f"{k}={v}")
            kw = f"{cls}({', '.join(kw)})"
        else:
            kw = "None"
        lse.append(kw)

    cls_lst = [i.split("(")[0] for i in lst]
    cls_lse = [i.split("(")[0] for i in lse]

    com = []
    i = j = 0
    while i < len(lst) or j < len(lse):
        if lst[i] == lse[j]:
            com.append(lst[i])
            i += 1
            j += 1
        elif cls_lst[i] == cls_lse[j]:
            com.append(lst[i] + ":" + lse[j])
            i += 1
            j += 1
        else:
            if cls_lst[i] in cls_lse:
                while cls_lse[j] != cls_lst[i]:
                    com.append(":" + lse[j])
                    j += 1
            # elif cls_lse[j] in cls_lst:
            #     while cls_lse[j] != cls_lse[i]:
            else:
                com.append(lst[i] + ":")
                i += 1
    assert i == len(lst) and j == len(lse)
    for i in range(len(com)):
        if 'Label' in com[i]:
            com[i] = com[i]+':...'
        elif 'KeepKey' in com[i]:
            com[i] = com[i]+':...'
    lines.append(f"    Transforms = _[{','.join(com)}]")




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
    convert_yml_to_yaml("../configs")
