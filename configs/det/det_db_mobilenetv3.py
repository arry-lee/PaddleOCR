# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel,_
from ptocr.modules.backbones.det_mobilenet_v3 import MobileNetV3
from ptocr.modules.necks.db_fpn import DBFPN
from ptocr.modules.heads.det_db_head import DBHead
from ptocr.loss.det_db_loss import DBLoss
from ptocr.metrics.det_metric import DetMetric
from torch.optim import Adam
from torch.optim.lr_scheduler import ConstantLR
from ptocr.postprocess.db_postprocess import DBPostProcess
from ptocr.datasets.simple_dataset import SimpleDataSet
from ptocr.datasets.imaug.operators import DecodeImage, KeepKeys, ToCHWImage, DetResizeForTest, NormalizeImage
from ptocr.datasets.imaug.label_ops import DetLabelEncode
from ptocr.datasets.imaug.iaa_augment import IaaAugment
from ptocr.datasets.imaug.random_crop_data import EastRandomCropData
from ptocr.datasets.imaug.make_border_map import MakeBorderMap
from ptocr.datasets.imaug.make_shrink_map import MakeShrinkMap
class Model(ConfigModel):
    use_gpu = True
    use_xpu = False
    use_mlu = False
    epoch_num = 1200
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/db_mv3/"
    save_epoch_step = 1200
    eval_batch_step = [0, 2000]
    metric_during_train = False
    pretrained_model = "./pretrain_models/MobileNetV3_large_x0_5_pretrained"
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_en/img_10.jpg"
    save_res_path = "./output/det_db/predicts_db.txt"
    model_type = 'det'
    algorithm = 'DB'
    Transform = None
    Backbone = _(MobileNetV3, scale=0.5, model_name="large")
    Neck = _(DBFPN, out_channels=256)
    Head = _(DBHead, k=50)
    loss = DBLoss(balance_loss=True, main_loss_type="DiceLoss", alpha=5, beta=10, ohem_ratio=3)
    metric = DetMetric(main_indicator="hmean")
    Optimizer = _(Adam,betas=[0.9, 0.999], lr=0.001)
    LRScheduler = _(ConstantLR,)
    PostProcessor = _(DBPostProcess,thresh=0.3, box_thresh=0.6, max_candidates=1000, unclip_ratio=1.5)
    class Train:
        Dataset = _(SimpleDataSet, data_dir="./train_data/icdar2015/text_localization/", label_file_list=['./train_data/icdar2015/text_localization/train_icdar2015_label.txt'], ratio_list=[1.0])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), DetLabelEncode(), IaaAugment(augmenter_args=[{'type': 'Fliplr', 'args': {'p': 0.5}}, {'type': 'Affine', 'args': {'rotate': [-10, 10]}}, {'type': 'Resize', 'args': {'size': [0.5, 3]}}]), EastRandomCropData(size=[640, 640], max_tries=50, keep_ratio=True), MakeBorderMap(shrink_ratio=0.4, thresh_min=0.3, thresh_max=0.7), MakeShrinkMap(shrink_ratio=0.4, min_text_size=8), NormalizeImage(scale="1./255.", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], order="hwc"), ToCHWImage(), KeepKeys(keep_keys=['image', 'threshold_map', 'threshold_mask', 'shrink_map', 'shrink_mask'])]
        DATALOADER = _(shuffle=True, drop_last=False, batch_size=16, num_workers=8, use_shared_memory=True)
    class Eval:
        Dataset = _(SimpleDataSet, data_dir="./train_data/icdar2015/text_localization/", label_file_list=['./train_data/icdar2015/text_localization/test_icdar2015_label.txt'])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), DetLabelEncode(), DetResizeForTest(image_shape=[736, 1280]), NormalizeImage(scale="1./255.", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], order="hwc"), ToCHWImage(), KeepKeys(keep_keys=['image', 'shape', 'polys', 'ignore_tags'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=1, num_workers=8, use_shared_memory=True)
