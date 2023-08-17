# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel,_
from ptocr.modules.backbones.rec_nrtr_mtb import MTB
from ptocr.modules.heads.rec_nrtr_head import Transformer
from ptocr.loss.ce import CELoss
from ptocr.metrics.rec import RecMetric
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from ptocr.postprocess.rec import NRTRLabelDecode
from ptocr.datasets.lmdb_dataset import LMDBDataSet
from ptocr.datasets.imaug.operators import DecodeImage, KeepKeys
from ptocr.datasets.imaug.label_ops import NRTRLabelEncode
from ptocr.datasets.imaug.rec_img_aug import GrayRecResizeImg
class Model(ConfigModel):
    use_gpu = True
    epoch_num = 21
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/rec/nrtr/"
    save_epoch_step = 1
    eval_batch_step = [0, 2000]
    metric_during_train = True
    pretrained_model = None
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_words_en/word_10.png"
    character_dict_path = "ppocr/utils/EN_symbol_dict.txt"
    max_text_length = 25
    infer_mode = False
    use_space_char = False
    save_res_path = "./output/rec/predicts_nrtr.txt"
    model_type = 'rec'
    algorithm = 'NRTR'
    in_channels = 1
    Transform = None
    Backbone = _(MTB, cnn_num=2)
    Head = _(Transformer, d_model=512, num_encoder_layers=6, beam_size=-1)
    loss = CELoss(smoothing=True)
    metric = RecMetric(main_indicator="acc")
    Optimizer = _(Adam,betas=[0.9, 0.99], clip_norm=5.0, lr=0.0005)
    LRScheduler = _(CosineAnnealingWarmRestarts,T_0=2)
    PostProcessor = _(NRTRLabelDecode,)
    class Train:
        Dataset = _(LMDBDataSet, data_dir="./train_data/data_lmdb_release/training/")
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), NRTRLabelEncode(), GrayRecResizeImg(image_shape=[100, 32], resize_type="PIL"), KeepKeys(keep_keys=['image', 'label', 'length'])]
        DATALOADER = _(shuffle=True, batch_size=512, drop_last=True, num_workers=8)
    class Eval:
        Dataset = _(LMDBDataSet, data_dir="./train_data/data_lmdb_release/evaluation/")
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), NRTRLabelEncode(), GrayRecResizeImg(image_shape=[100, 32], resize_type="PIL"), KeepKeys(keep_keys=['image', 'label', 'length'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=256, num_workers=4, use_shared_memory=False)
