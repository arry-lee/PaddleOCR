# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel,_
from ptocr.modules.backbones.rec_mv1_enhance import MobileNetV1Enhance
from ptocr.modules.heads.cls_head import ClsHead
from ptocr.loss.cls import ClsLoss
from ptocr.metrics.cls import ClsMetric
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from ptocr.postprocess.cls import ClsPostProcess
from ptocr.datasets.simple_dataset import SimpleDataSet
from ptocr.datasets.imaug.operators import DecodeImage, KeepKeys
from ptocr.datasets.imaug.rec_img_aug import BaseDataAugmentation
from ptocr.datasets.imaug.randaugment import RandAugment
from ptocr.datasets.imaug.ssl_img_aug import SSLRotateResize
class Model(ConfigModel):
    debug = False
    use_gpu = True
    epoch_num = 100
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/rec_ppocr_v3_rotnet"
    save_epoch_step = 3
    eval_batch_step = [0, 2000]
    metric_during_train = True
    pretrained_model = None
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_words/ch/word_1.jpg"
    character_dict_path = "ppocr/utils/ppocr_keys_v1.txt"
    max_text_length = 25
    infer_mode = False
    use_space_char = True
    save_res_path = "./output/rec/predicts_chinese_lite_v2.0.txt"
    model_type = 'cls'
    algorithm = 'CLS'
    Transform = None
    Backbone = _(MobileNetV1Enhance, scale=0.5, last_conv_stride=[1, 2], last_pool_type="avg")
    Neck = None
    Head = _(ClsHead, class_dim=4)
    loss = ClsLoss(main_indicator="acc")
    metric = ClsMetric(main_indicator="acc")
    Optimizer = _(Adam,betas=[0.9, 0.999], lr=0.001)
    LRScheduler = _(CosineAnnealingLR,)
    PostProcessor = _(ClsPostProcess,)
    class Train:
        Dataset = _(SimpleDataSet, data_dir="./train_data", label_file_list=['./train_data/train_list.txt'])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), BaseDataAugmentation(), RandAugment(), SSLRotateResize(image_shape=[3, 48, 320]), KeepKeys(keep_keys=['image', 'label'])]
        DATALOADER = _(collate_fn="SSLRotateCollate", shuffle=True, batch_size=32, drop_last=True, num_workers=8)
    class Eval:
        Dataset = _(SimpleDataSet, data_dir="./train_data", label_file_list=['./train_data/val_list.txt'])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), SSLRotateResize(image_shape=[3, 48, 320]), KeepKeys(keep_keys=['image', 'label'])]
        DATALOADER = _(collate_fn="SSLRotateCollate", shuffle=False, drop_last=False, batch_size=64, num_workers=8)
