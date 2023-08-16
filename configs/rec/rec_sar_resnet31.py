# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel,_
from ptocr.modules.backbones.rec_resnet_31 import ResNet31
from ptocr.modules.heads.rec_sar_head import SARHead
from ptocr.loss.rec_sar_loss import SARLoss
from ptocr.metrics.rec_metric import RecMetric
from torch.optim import Adam
from ptocr.optim.lr_scheduler import PiecewiseLR
from ptocr.postprocess.rec_postprocess import SARLabelDecode
from ptocr.datasets.simple_dataset import SimpleDataSet
from ptocr.datasets.imaug.operators import DecodeImage, KeepKeys
from ptocr.datasets.imaug.label_ops import SARLabelEncode
from ptocr.datasets.imaug.rec_img_aug import SARRecResizeImg
from ptocr.datasets.lmdb_dataset import LMDBDataSet
class Model(ConfigModel):
    use_gpu = True
    epoch_num = 5
    log_window_size = 20
    log_batch_step = 20
    save_model_dir = "./sar_rec"
    save_epoch_step = 1
    eval_batch_step = [0, 2000]
    metric_during_train = True
    pretrained_model = None
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = None
    character_dict_path = "ppocr/utils/dict90.txt"
    max_text_length = 30
    infer_mode = False
    use_space_char = False
    rm_symbol = True
    save_res_path = "./output/rec/predicts_sar.txt"
    model_type = 'rec'
    algorithm = 'SAR'
    Transform = None
    Backbone = _(ResNet31, )
    Head = _(SARHead, )
    loss = SARLoss()
    metric = RecMetric()
    Optimizer = _(Adam,betas=[0.9, 0.999])
    LRScheduler = _(PiecewiseLR,decay_epochs=[3, 4], values=[0.001, 0.0001, 1e-05])
    PostProcessor = _(SARLabelDecode,)
    class Train:
        Dataset = _(SimpleDataSet, label_file_list=['./train_data/train_list.txt'], data_dir="./train_data/", ratio_list=1.0)
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), SARLabelEncode(), SARRecResizeImg(image_shape=[3, 48, 48, 160], width_downsample_ratio=0.25), KeepKeys(keep_keys=['image', 'label', 'valid_ratio'])]
        DATALOADER = _(shuffle=True, batch_size=64, drop_last=True, num_workers=8, use_shared_memory=False)
    class Eval:
        Dataset = _(LMDBDataSet, data_dir="./train_data/data_lmdb_release/evaluation/")
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), SARLabelEncode(), SARRecResizeImg(image_shape=[3, 48, 48, 160], width_downsample_ratio=0.25), KeepKeys(keep_keys=['image', 'label', 'valid_ratio'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=64, num_workers=4, use_shared_memory=False)
