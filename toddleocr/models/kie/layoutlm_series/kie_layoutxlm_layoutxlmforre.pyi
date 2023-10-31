# This .pyi is auto generated by the script in the root folder.
# only for cache,use .py for changes
from toddleocr.config import _, ConfigModel
from toddleocr.datasets.simple import SimpleDataSet
from toddleocr.loss.basic import LossFromOutput
from toddleocr.metrics.vqa import VQAReTokenMetric
from toddleocr.modules.backbones.vqa_layoutlm import LayoutXLMForRe
from toddleocr.postprocess.vqa import VQAReTokenLayoutLMPostProcess
from toddleocr.transforms.label_ops import VQATokenLabelEncode
from toddleocr.transforms.operators import (
    DecodeImage,
    KeepKeys,
    NormalizeImage,
    Resize,
    ToCHWImage,
)
from toddleocr.transforms.vqa.token.vqa_re_convert import TensorizeEntitiesRelations
from toddleocr.transforms.vqa.token.vqa_token_chunk import VQAReTokenChunk
from toddleocr.transforms.vqa.token.vqa_token_pad import VQATokenPad
from toddleocr.transforms.vqa.token.vqa_token_relation import VQAReTokenRelation
from torch.optim import AdamW
from torch.optim.lr_scheduler import ConstantLR

class Model(ConfigModel):
    use_gpu = True
    epoch_num = 130
    log_window_size = 10
    log_batch_step = 10
    save_model_dir = None
    save_epoch_step = 2000
    eval_batch_step = [0, 19]
    metric_during_train = False
    save_infer_dir = None
    use_visualdl = False
    seed = 2022
    pretrained_model = None
    model_type = "kie"
    algorithm = "LayoutXLM"
    Transform = None
    Backbone = _(LayoutXLMForRe, pretrained=True, checkpoints=None)
    loss = LossFromOutput(key="loss", reduction="mean")
    metric = VQAReTokenMetric(main_indicator="hmean")
    postprocessor = VQAReTokenLayoutLMPostProcess()
    Optimizer = _(AdamW, beta1=0.9, beta2=0.999, clip_norm=10, lr=5e-05)
    LRScheduler = _(ConstantLR, warmup_epoch=10)

    class Data:
        dataset = SimpleDataSet
        root: "train_data/XFUND/zh_val/image" = "train_data/XFUND/zh_train/image"
        label_file_list: "train_data/XFUND/zh_val/val.json" = (
            "train_data/XFUND/zh_train/train.json"
        )

    class Loader:
        shuffle: False = True
        drop_last = False
        batch_size: 8 = 2
        num_workers = 8
    Transforms = _[
        DecodeImage(img_mode="RGB", channel_first=False),
        VQATokenLabelEncode(
            contains_re=True,
            algorithm="LayoutXLM",
            class_path="train_data/XFUND/class_list_xfun.txt",
        ) : ...,
        VQATokenPad(max_seq_len=512, return_attention_mask=True),
        VQAReTokenRelation(),
        VQAReTokenChunk(max_seq_len=512),
        TensorizeEntitiesRelations(),
        Resize(size=[224, 224]),
        NormalizeImage(
            scale=1,
            mean=[123.675, 116.28, 103.53],
            std=[58.395, 57.12, 57.375],
            order="hwc",
        ),
        ToCHWImage(),
        KeepKeys(
            "input_ids",
            "bbox",
            "attention_mask",
            "token_type_ids",
            "image",
            "entities",
            "relations",
        ) : ...,
    ]
