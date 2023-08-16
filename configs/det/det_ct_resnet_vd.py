# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel, _
from ppocr.modeling.backbones.det_resnet_vd import ResNet_vd
from ppocr.modeling.necks.ct_fpn import CTFPN
from torch.nn import (
    Linear,
    GroupRandomCropPadding,
    CT_Head,
    GroupRandomHorizontalFlip,
    ScaleAlignedShort,
    GroupRandomRotate,
    MakeCentripetalShift,
    MakeShrink,
    RandomScale,
)
from ppocr.losses.det_ct_loss import CTLoss
from ppocr.metrics.ct_metric import CTMetric
from torch.optim import Adam
from ppocr.postprocess.ct_postprocess import CTPostProcess
from ppocr.data.simple_dataset import SimpleDataSet
from ppocr.data.imaug.operators import KeepKeys, NormalizeImage, DecodeImage, ToCHWImage
from ppocr.data.imaug.label_ops import CTLabelEncode
from ppocr.data.imaug.ColorJitter import ColorJitter


class Model(ConfigModel):
    use_gpu = True
    epoch_num = 600
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/det_ct/"
    save_epoch_step = 10
    eval_batch_step = [0, 1000]
    metric_during_train = False
    pretrained_model = "./pretrain_models/ResNet18_vd_pretrained.pdparams"
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_en/img623.jpg"
    save_res_path = "./output/det_ct/predicts_ct.txt"
    model_type = "det"
    algorithm = "CT"
    Transform = None
    Backbone = _(ResNet_vd, layers=18)
    Neck = _(
        CTFPN,
    )
    Head = _(CT_Head, in_channels=512, hidden_dim=128, num_classes=3)
    loss = CTLoss()
    metric = CTMetric(main_indicator="f_score")
    Optimizer = _(Adam, lr=0.001)
    LRScheduler = _(Linear, end_lr=0.0, epochs=600, step_each_epoch=1254, power=0.9)
    PostProcessor = _(CTPostProcess, box_type="poly")

    class Train:
        Dataset = _(
            SimpleDataSet,
            data_dir="./train_data/total_text/train",
            label_file_list=["./train_data/total_text/train/train.txt"],
            ratio_list=[1.0],
        )
        transforms = _[
            DecodeImage(img_mode="RGB", channel_first=False),
            CTLabelEncode(),
            RandomScale(),
            MakeShrink(),
            GroupRandomHorizontalFlip(),
            GroupRandomRotate(),
            GroupRandomCropPadding(),
            MakeCentripetalShift(),
            ColorJitter(brightness=0.125, saturation=0.5),
            ToCHWImage(),
            NormalizeImage(),
            KeepKeys(
                keep_keys=[
                    "image",
                    "gt_kernel",
                    "training_mask",
                    "gt_instance",
                    "gt_kernel_instance",
                    "training_mask_distance",
                    "gt_distance",
                ]
            ),
        ]
        DATALOADER = _(shuffle=True, drop_last=True, batch_size=4, num_workers=8)

    class Eval:
        Dataset = _(
            SimpleDataSet,
            data_dir="./train_data/total_text/test",
            label_file_list=["./train_data/total_text/test/test.txt"],
            ratio_list=[1.0],
        )
        transforms = _[
            DecodeImage(img_mode="RGB", channel_first=False),
            CTLabelEncode(),
            ScaleAlignedShort(),
            NormalizeImage(order="hwc"),
            ToCHWImage(),
            KeepKeys(keep_keys=["image", "shape", "polys", "texts"]),
        ]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=1, num_workers=2)
