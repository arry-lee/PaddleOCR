# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel, _
from ppocr.modeling.backbones.det_mobilenet_v3 import MobileNetV3
from ppocr.modeling.necks.fpn import FPN
from ppocr.modeling.heads.det_pse_head import PSEHead
from ppocr.losses.det_pse_loss import PSELoss
from ppocr.metrics.det_metric import DetMetric
from torch.optim import Adam
from torch.optim.lr_scheduler import StepLR
from torch.nn import PSEPostProcess
from ppocr.data.simple_dataset import SimpleDataSet
from ppocr.data.imaug.operators import DecodeImage, KeepKeys, NormalizeImage, DetResizeForTest, ToCHWImage
from ppocr.data.imaug.label_ops import DetLabelEncode
from ppocr.data.imaug.ColorJitter import ColorJitter
from ppocr.data.imaug.iaa_augment import IaaAugment
from ppocr.data.imaug.make_pse_gt import MakePseGt
from ppocr.data.imaug.random_crop_data import RandomCropImgMask


class Model(ConfigModel):
    use_gpu = True
    epoch_num = 600
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/det_mv3_pse/"
    save_epoch_step = 600
    eval_batch_step = [0, 63]
    metric_during_train = False
    pretrained_model = "./pretrain_models/MobileNetV3_large_x0_5_pretrained"
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_en/img_10.jpg"
    save_res_path = "./output/det_pse/predicts_pse.txt"
    model_type = "det"
    algorithm = "PSE"
    Transform = None
    Backbone = _(MobileNetV3, scale=0.5, model_name="large")
    Neck = _(FPN, out_channels=96)
    Head = _(PSEHead, hidden_dim=96, out_channels=7)
    loss = PSELoss(alpha=0.7, ohem_ratio=3, kernel_sample_mask="pred", reduction="none")
    metric = DetMetric(main_indicator="hmean")
    Optimizer = _(Adam, betas=[0.9, 0.999], lr=0.001)
    LRScheduler = _(StepLR, step_size=200, gamma=0.1)
    PostProcessor = _(PSEPostProcess, thresh=0, box_thresh=0.85, min_area=16, box_type="quad", scale=1)

    class Train:
        Dataset = _(
            SimpleDataSet,
            data_dir="./train_data/icdar2015/text_localization/",
            label_file_list=["./train_data/icdar2015/text_localization/train_icdar2015_label.txt"],
            ratio_list=[1.0],
        )
        transforms = _[
            DecodeImage(img_mode="BGR", channel_first=False),
            DetLabelEncode(),
            ColorJitter(brightness=0.12549019607843137, saturation=0.5),
            IaaAugment(
                augmenter_args=[
                    {"type": "Resize", "args": {"size": [0.5, 3]}},
                    {"type": "Fliplr", "args": {"p": 0.5}},
                    {"type": "Affine", "args": {"rotate": [-10, 10]}},
                ]
            ),
            MakePseGt(kernel_num=7, min_shrink_ratio=0.4, size=640),
            RandomCropImgMask(
                size=[640, 640], main_key="gt_text", crop_keys=["image", "gt_text", "gt_kernels", "mask"]
            ),
            NormalizeImage(scale="1./255.", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], order="hwc"),
            ToCHWImage(),
            KeepKeys(keep_keys=["image", "gt_text", "gt_kernels", "mask"]),
        ]
        DATALOADER = _(shuffle=True, drop_last=False, batch_size=16, num_workers=8)

    class Eval:
        Dataset = _(
            SimpleDataSet,
            data_dir="./train_data/icdar2015/text_localization/",
            label_file_list=["./train_data/icdar2015/text_localization/test_icdar2015_label.txt"],
            ratio_list=[1.0],
        )
        transforms = _[
            DecodeImage(img_mode="BGR", channel_first=False),
            DetLabelEncode(),
            DetResizeForTest(limit_side_len=736, limit_type="min"),
            NormalizeImage(scale="1./255.", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], order="hwc"),
            ToCHWImage(),
            KeepKeys(keep_keys=["image", "shape", "polys", "ignore_tags"]),
        ]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=1, num_workers=8)
