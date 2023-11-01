# This .pyi is auto generated by the script in the root folder.
# only for cache,use .py for changes
from toddleocr.config import _, ConfigModel
from toddleocr.datasets.simple import SimpleDataSet
from toddleocr.loss.drrg import DRRGLoss
from toddleocr.metrics.det import DetFCEMetric
from toddleocr.modules.backbones.resnet.det_resnet_vd import ResNet_vd
from toddleocr.modules.heads.drrg import DRRGHead
from toddleocr.modules.necks.fpn_unet import FPN_UNet
from toddleocr.postprocess.drrg import DRRGPostprocess
from toddleocr.transforms.ColorJitter import ColorJitter
from toddleocr.transforms.drrg_targets import DRRGTargets
from toddleocr.transforms.fce_aug import (
    RandomCropFlip,
    RandomCropPolyInstances,
    RandomRotatePolyInstances,
    RandomScaling,
    SquareResizePad,
)
from toddleocr.transforms.iaa_augment import IaaAugment
from toddleocr.transforms.label_ops import DetLabelEncode
from toddleocr.transforms.operators import (
    DecodeImage,
    DetResizeForTest,
    KeepKeys,
    NormalizeImage,
    Pad,
    ToCHWImage,
)
from torch.optim import SGD
from torch.optim.lr_scheduler import PolynomialLR

class Model(ConfigModel):
    use_gpu = True
    epoch_num = 1200
    log_window_size = 20
    log_batch_step = 5
    save_model_dir = None
    save_epoch_step = 100
    eval_batch_step = [37800, 1260]
    metric_during_train = False
    pretrained_model = None
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    model_type = "det"
    algorithm = "DRRG"
    Transform = None
    Backbone = _(ResNet_vd, layers=50)
    Neck = _(FPN_UNet, in_channels=[256, 512, 1024, 2048], out_channels=32)
    Head = _(DRRGHead, in_channels=32, text_region_thr=0.3, center_region_thr=0.4)
    loss = DRRGLoss()
    metric = DetFCEMetric(main_indicator="hmean")
    postprocessor = DRRGPostprocess(link_thr=0.8)
    Optimizer = _(SGD, momentum=0.9, lr=0.028, weight_decay=0.0001)
    LRScheduler = _(PolynomialLR, total_iters=1200, power=0.9)

    class Data:
        dataset = SimpleDataSet
        root = "train_data/ctw1500/imgs/"
        label_file_list: "test.txt" = "training.txt"

    class Loader:
        shuffle: False = True
        drop_last = False
        batch_size: 1 = 4
        num_workers: 2 = 8
    Transforms = _[
        DecodeImage(img_mode="BGR", channel_first=False, ignore_orientation=True),
        DetLabelEncode() : ...,
        ColorJitter(brightness=0.12549019607843137, saturation=0.5) :,
        RandomScaling() :,
        RandomCropFlip(crop_ratio=0.5) :,
        RandomCropPolyInstances(crop_ratio=0.8, min_side_ratio=0.3) :,
        RandomRotatePolyInstances(
            rotate_ratio=0.5, max_angle=60, pad_with_fixed_color=False
        ) :,
        SquareResizePad(target_size=800, pad_ratio=0.6) :,
        IaaAugment(augmenter_args=[{"type": "Fliplr", "args": {"p": 0.5}}]) :,
        DRRGTargets() :,
        : DetResizeForTest(limit_type="min", limit_side_len=640),
        NormalizeImage(
            scale="1./255.",
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
            order="hwc",
        ),
        : Pad(),
        ToCHWImage(),
        KeepKeys(
            "image",
            "gt_text_mask",
            "gt_center_region_mask",
            "gt_mask",
            "gt_top_height_map",
            "gt_bot_height_map",
            "gt_sin_map",
            "gt_cos_map",
            "gt_comp_attribs",
        ) : KeepKeys("image", "shape", "polys", "ignore_tags") : ...,
    ]