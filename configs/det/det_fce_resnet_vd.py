# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel,_
from ptocr.modules.backbones.det_resnet_vd import ResNet_vd
from ptocr.modules.necks.fce_fpn import FCEFPN
from ptocr.modules.heads.det_fce_head import FCEHead
from ptocr.loss.fce import FCELoss
from ptocr.metrics.det import DetFCEMetric
from torch.optim import Adam
from torch.optim.lr_scheduler import ConstantLR
from ptocr.postprocess.fce import FCEPostProcess
from ptocr.datasets.simple_dataset import SimpleDataSet
from ptocr.datasets.imaug.operators import DecodeImage, KeepKeys, ToCHWImage, DetResizeForTest, NormalizeImage, Pad
from ptocr.datasets.imaug.label_ops import DetLabelEncode
from ptocr.datasets.imaug.ColorJitter import ColorJitter
from ptocr.datasets.imaug.fce_aug import RandomRotatePolyInstances, RandomCropPolyInstances, SquareResizePad, RandomCropFlip, RandomScaling
from ptocr.datasets.imaug.iaa_augment import IaaAugment
from ptocr.datasets.imaug.fce_targets import FCENetTargets
class Model(ConfigModel):
    use_gpu = True
    epoch_num = 1500
    log_window_size = 20
    log_batch_step = 20
    save_model_dir = "./output/det_r50_dcn_fce_ctw/"
    save_epoch_step = 100
    eval_batch_step = [0, 835]
    metric_during_train = False
    pretrained_model = "./pretrain_models/ResNet50_vd_ssld_pretrained"
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_en/img_10.jpg"
    save_res_path = "./output/det_fce/predicts_fce.txt"
    model_type = 'det'
    algorithm = 'FCE'
    Transform = None
    Backbone = _(ResNet_vd, layers=50, dcn_stage=[False, True, True, True], out_indices=[1, 2, 3])
    Neck = _(FCEFPN, out_channels=256, has_extra_convs=False, extra_stage=0)
    Head = _(FCEHead, fourier_degree=5)
    loss = FCELoss(fourier_degree=5, num_sample=50)
    metric = DetFCEMetric(main_indicator="hmean")
    Optimizer = _(Adam,betas=[0.9, 0.999], lr=0.0001)
    LRScheduler = _(ConstantLR,)
    PostProcessor = _(FCEPostProcess,scales=[8, 16, 32], alpha=1.0, beta=1.0, fourier_degree=5, box_type="poly")
    class Train:
        Dataset = _(SimpleDataSet, data_dir="./train_data/ctw1500/imgs/", label_file_list=['./train_data/ctw1500/imgs/training.txt'])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False, ignore_orientation=True), DetLabelEncode(), ColorJitter(brightness=0.142, saturation=0.5, contrast=0.5), RandomScaling(), RandomCropFlip(crop_ratio=0.5), RandomCropPolyInstances(crop_ratio=0.8, min_side_ratio=0.3), RandomRotatePolyInstances(rotate_ratio=0.5, max_angle=30, pad_with_fixed_color=False), SquareResizePad(target_size=800, pad_ratio=0.6), IaaAugment(augmenter_args=[{'type': 'Fliplr', 'args': {'p': 0.5}}]), FCENetTargets(fourier_degree=5), NormalizeImage(scale="1./255.", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], order="hwc"), ToCHWImage(), KeepKeys(keep_keys=['image', 'p3_maps', 'p4_maps', 'p5_maps'])]
        DATALOADER = _(shuffle=True, drop_last=False, batch_size=6, num_workers=8)
    class Eval:
        Dataset = _(SimpleDataSet, data_dir="./train_data/ctw1500/imgs/", label_file_list=['./train_data/ctw1500/imgs/test.txt'])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False, ignore_orientation=True), DetLabelEncode(), DetResizeForTest(limit_type="min", limit_side_len=736), NormalizeImage(scale="1./255.", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], order="hwc"), Pad(), ToCHWImage(), KeepKeys(keep_keys=['image', 'shape', 'polys', 'ignore_tags'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=1, num_workers=2)
