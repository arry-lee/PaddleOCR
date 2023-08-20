# This .py is auto generated by the script in the root folder.
from ptocr.config import ConfigModel,_
from ptocr.modules.backbones.resnet.rec_resnet_45 import ResNet45
from ptocr.modules.heads.abinet import ABINetHead
from ptocr.loss.ce import CELoss
from ptocr.metrics.rec import RecMetric
from ptocr.postprocess.rec import ABINetLabelDecode
from torch.optim import Adam
from ptocr.optim.lr_scheduler import PiecewiseLR
from ptocr.datasets.lmdb import LMDBDataSet
from ptocr.transforms.operators import KeepKeys, DecodeImage
from ptocr.transforms.rec_img_aug import ABINetRecAug, ABINetRecResizeImg
from ptocr.transforms.label_ops import ABINetLabelEncode
class Model(ConfigModel):
    use_gpu = True
    epoch_num = 10
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/rec/r45_abinet/"
    save_epoch_step = 1
    eval_batch_step = [0, 2000]
    metric_during_train = True
    pretrained_model = "./pretrain_models/abinet_vl_pretrained"
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_words_en/word_10.png"
    character_dict_path = None
    character_type = "en"
    max_text_length = 25
    infer_mode = False
    use_space_char = False
    save_res_path = "./output/rec/predicts_abinet.txt"
    model_type = 'rec'
    algorithm = 'ABINet'
    in_channels = 3
    Transform = None
    Backbone = _(ResNet45, )
    Head = _(ABINetHead, use_lang=True, iter_size=3)
    loss = CELoss(ignore_index=100)
    metric = RecMetric(main_indicator="acc")
    postprocessor = ABINetLabelDecode()
    Optimizer = _(Adam,betas=[0.9, 0.99], clip_norm=20.0)
    LRScheduler = _(PiecewiseLR,decay_epochs=[6], values=[0.0001, 1e-05])
    class Train:
        Dataset = _(LMDBDataSet, root="./train_data/data_lmdb_release/training/")
        transforms = _[DecodeImage(img_mode="RGB", channel_first=False), ABINetRecAug(), ABINetLabelEncode(ignore_index=100), ABINetRecResizeImg(image_shape=[3, 32, 128]), KeepKeys(keep_keys=['image', 'label', 'length'])]
        DATALOADER = _(shuffle=True, batch_size=96, drop_last=True, num_workers=4)
    class Eval:
        Dataset = _(LMDBDataSet, root="./train_data/data_lmdb_release/evaluation/")
        transforms = _[DecodeImage(img_mode="RGB", channel_first=False), ABINetLabelEncode(ignore_index=100), ABINetRecResizeImg(image_shape=[3, 32, 128]), KeepKeys(keep_keys=['image', 'label', 'length'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=256, num_workers=4, pin_memory=False)
