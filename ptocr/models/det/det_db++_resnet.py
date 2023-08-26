# This .py is auto generated by the script in the root folder.
from ptocr.config import ConfigModel,_
from ptocr.modules.backbones.resnet.det_resnet import ResNet
from ptocr.modules.necks.db_fpn import DBFPN
from ptocr.modules.heads.db import DBHead
from ptocr.loss.db import DBLoss
from ptocr.metrics.det import DetMetric
from ptocr.postprocess.db import DBPostProcess
from torch.optim import SGD
from torch.optim.lr_scheduler import PolynomialLR
from ptocr.datasets.simple import SimpleDataSet
from ptocr.transforms.operators import ToCHWImage, DetResizeForTest, KeepKeys, NormalizeImage, DecodeImage
from ptocr.transforms.label_ops import DetLabelEncode
from ptocr.transforms.iaa_augment import IaaAugment
from ptocr.transforms.random_crop_data import EastRandomCropData
from ptocr.transforms.make_shrink_map import MakeShrinkMap
from ptocr.transforms.make_border_map import MakeBorderMap
class Model(ConfigModel):
    debug = False
    use_gpu = True
    epoch_num = 1000
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/det_r50_td_tr/"
    save_epoch_step = 200
    eval_batch_step = [0, 2000]
    metric_during_train = False
    pretrained_model = "./pretrain_models/ResNet50_dcn_asf_synthtext_pretrained"
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_en/img_10.jpg"
    save_res_path = "./checkpoints/det_db/predicts_db.txt"
    model_type = 'det'
    algorithm = 'DB++'
    Transform = None
    Backbone = _(ResNet, layers=50, dcn_stage=[False, True, True, True])
    Neck = _(DBFPN, out_channels=256, use_asf=True)
    Head = _(DBHead, k=50)
    loss = DBLoss(balance_loss=True, main_loss_type="BCELoss", alpha=5, beta=10, ohem_ratio=3)
    metric = DetMetric(main_indicator="hmean")
    postprocessor = DBPostProcess(thresh=0.3, box_thresh=0.5, max_candidates=1000, unclip_ratio=1.5, det_box_type="quad")
    Optimizer = _(SGD,momentum=0.9, lr=0.007, weight_decay=0.0001)
    LRScheduler = _(PolynomialLR,total_iters=1000, power=0.9)
    class Train:
        Dataset = _(SimpleDataSet, root="./train_data/", label_file_list=['./train_data/TD_TR/TD500/train_gt_labels.txt', './train_data/TD_TR/TR400/gt_labels.txt'], ratio_list=[1.0, 1.0])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), DetLabelEncode(), IaaAugment(augmenter_args=[{'type': 'Fliplr', 'args': {'p': 0.5}}, {'type': 'Affine', 'args': {'rotate': [-10, 10]}}, {'type': 'Resize', 'args': {'size': [0.5, 3]}}]), EastRandomCropData(size=[640, 640], max_tries=10, keep_ratio=True), MakeShrinkMap(shrink_ratio=0.4, min_text_size=8), MakeBorderMap(shrink_ratio=0.4, thresh_min=0.3, thresh_max=0.7), NormalizeImage(scale="1./255.", mean=[0.48109378172549, 0.45752457890196, 0.40787054090196], std=[1.0, 1.0, 1.0], order="hwc"), ToCHWImage(), KeepKeys(keep_keys=['image', 'threshold_map', 'threshold_mask', 'shrink_map', 'shrink_mask'])]
        DATALOADER = _(shuffle=True, drop_last=False, batch_size=4, num_workers=8)
    class Eval:
        Dataset = _(SimpleDataSet, root="./train_data/", label_file_list=['./train_data/TD_TR/TD500/test_gt_labels.txt'])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), DetLabelEncode(), DetResizeForTest(image_shape=[736, 736], keep_ratio=True), NormalizeImage(scale="1./255.", mean=[0.48109378172549, 0.45752457890196, 0.40787054090196], std=[1.0, 1.0, 1.0], order="hwc"), ToCHWImage(), KeepKeys(keep_keys=['image', 'shape', 'polys', 'ignore_tags'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=1, num_workers=2)