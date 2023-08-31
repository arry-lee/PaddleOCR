# This .py is auto generated by the script in the root folder.
from ptocr.config import ConfigModel,_
from ptocr.modules.backbones.mobilenetv3.det_mobilenet_v3 import MobileNetV3
from ptocr.modules.necks.east_fpn import EASTFPN
from ptocr.modules.heads.east import EASTHead
from ptocr.loss.east import EASTLoss
from ptocr.metrics.det import DetMetric
from ptocr.postprocess.east import EASTPostProcess
from torch.optim import Adam
from torch.optim.lr_scheduler import ConstantLR
from ptocr.datasets.simple import SimpleDataSet
from ptocr.transforms.operators import ToCHWImage, DetResizeForTest, KeepKeys, NormalizeImage, DecodeImage
from ptocr.transforms.label_ops import DetLabelEncode
from ptocr.transforms.east_process import EASTProcessTrain
class Model(ConfigModel):
    use_gpu = True
    epoch_num = 10000
    log_window_size = 20
    log_batch_step = 2
    save_model_dir = "./output/east_mv3/"
    save_epoch_step = 1000
    eval_batch_step = [4000, 5000]
    metric_during_train = False
    pretrained_model = "./pretrain_models/MobileNetV3_large_x0_5_pretrained"
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = None
    save_res_path = "./output/det_east/predicts_east.txt"
    model_type = 'det'
    algorithm = 'EAST'
    Transform = None
    Backbone = _(MobileNetV3, scale=0.5, model_name="large")
    Neck = _(EASTFPN, model_name="small")
    Head = _(EASTHead, model_name="small")
    loss = EASTLoss()
    metric = DetMetric(main_indicator="hmean")
    postprocessor = EASTPostProcess(score_thresh=0.8, cover_thresh=0.1, nms_thresh=0.2)
    Optimizer = _(Adam,betas=[0.9, 0.999])
    LRScheduler = _(ConstantLR,)
    class Train:
        Dataset = _(SimpleDataSet, root="./train_data/icdar2015/text_localization/", label_files=['./train_data/icdar2015/text_localization/train_icdar2015_label.txt'], ratio_list=[1.0])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), DetLabelEncode(), EASTProcessTrain(image_shape=[512, 512], background_ratio=0.125, min_crop_side_ratio=0.1, min_text_size=10), KeepKeys(keep_keys=['image', 'score_map', 'geo_map', 'training_mask'])]
        DATALOADER = _(shuffle=True, drop_last=False, batch_size=16, num_workers=8)
    class Eval:
        Dataset = _(SimpleDataSet, root="./train_data/icdar2015/text_localization/", label_files=['./train_data/icdar2015/text_localization/test_icdar2015_label.txt'])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), DetLabelEncode(), DetResizeForTest(limit_side_len=2400, limit_type="max"), NormalizeImage(scale="1./255.", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], order="hwc"), ToCHWImage(), KeepKeys(keep_keys=['image', 'shape', 'polys', 'ignore_tags'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=1, num_workers=2)
