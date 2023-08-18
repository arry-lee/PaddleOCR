# This .py is auto generated by the script in the root folder.
from ptocr.config import ConfigModel,_
from ptocr.modules.transforms.tps import TPS
from ptocr.modules.backbones.mobilenetv3.rec_mobilenet_v3 import MobileNetV3
from ptocr.modules.necks.rnn import SequenceEncoder
from ptocr.modules.heads.att import AttentionHead
from ptocr.loss.att import AttentionLoss
from ptocr.metrics.rec import RecMetric
from torch.optim import Adam
from torch.optim.lr_scheduler import ConstantLR
from ptocr.postprocess.rec import AttnLabelDecode
from ptocr.datasets.lmdb import LMDBDataSet
from ptocr.transforms.operators import DecodeImage, KeepKeys
from ptocr.transforms.label_ops import AttnLabelEncode
from ptocr.transforms.rec_img_aug import RecResizeImg
class Model(ConfigModel):
    use_gpu = True
    epoch_num = 72
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/rec/rec_mv3_tps_bilstm_att/"
    save_epoch_step = 3
    eval_batch_step = [0, 2000]
    metric_during_train = True
    pretrained_model = None
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_words/ch/word_1.jpg"
    character_dict_path = None
    max_text_length = 25
    infer_mode = False
    use_space_char = False
    save_res_path = "./output/rec/predicts_mv3_tps_bilstm_att.txt"
    model_type = 'rec'
    algorithm = 'RARE'
    Transform = _(TPS, num_fiducial=20, loc_lr=0.1, model_name="small")
    Backbone = _(MobileNetV3, scale=0.5, model_name="large")
    Neck = _(SequenceEncoder, encoder_type="rnn", hidden_size=96)
    Head = _(AttentionHead, hidden_size=96)
    loss = AttentionLoss()
    metric = RecMetric(main_indicator="acc")
    Optimizer = _(Adam,betas=[0.9, 0.999], lr=0.0005)
    LRScheduler = _(ConstantLR,)
    PostProcessor = _(AttnLabelDecode,)
    class Train:
        Dataset = _(LMDBDataSet, data_dir="./train_data/data_lmdb_release/training/")
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), AttnLabelEncode(), RecResizeImg(image_shape=[3, 32, 100]), KeepKeys(keep_keys=['image', 'label', 'length'])]
        DATALOADER = _(shuffle=True, batch_size=256, drop_last=True, num_workers=8)
    class Eval:
        Dataset = _(LMDBDataSet, data_dir="./train_data/data_lmdb_release/validation/")
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), AttnLabelEncode(), RecResizeImg(image_shape=[3, 32, 100]), KeepKeys(keep_keys=['image', 'label', 'length'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=256, num_workers=1)
