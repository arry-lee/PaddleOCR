# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel, _
from ppocr.modeling.backbones.rec_resnet_vd import ResNet
from ppocr.modeling.necks.rnn import SequenceEncoder
from ppocr.modeling.heads.rec_ctc_head import CTCHead
from ppocr.losses.rec_ctc_loss import CTCLoss
from ppocr.metrics.rec_metric import RecMetric
from torch.optim import Adam
from ppocr.postprocess.rec_postprocess import CTCLabelDecode
from ppocr.data.lmdb_dataset import LMDBDataSet
from ppocr.data.imaug.operators import KeepKeys, DecodeImage
from ppocr.data.imaug.label_ops import CTCLabelEncode
from ppocr.data.imaug.rec_img_aug import RecResizeImg


class Model(ConfigModel):
    use_gpu = True
    epoch_num = 72
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/rec/r34_vd_none_none_ctc/"
    save_epoch_step = 3
    eval_batch_step = [0, 2000]
    metric_during_train = True
    pretrained_model = None
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = "doc/imgs_words_en/word_10.png"
    character_dict_path = None
    max_text_length = 25
    infer_mode = False
    use_space_char = False
    save_res_path = "./output/rec/predicts_r34_vd_none_none_ctc.txt"
    model_type = "rec"
    algorithm = "Rosetta"
    Backbone = _(ResNet, layers=34)
    Neck = _(SequenceEncoder, encoder_type="reshape")
    Head = _(CTCHead, fc_decay=0.0004)
    loss = CTCLoss()
    metric = RecMetric(main_indicator="acc")
    Optimizer = _(Adam, betas=[0.9, 0.999], lr=0.0005)
    LRScheduler = None
    PostProcessor = _(
        CTCLabelDecode,
    )

    class Train:
        Dataset = _(LMDBDataSet, data_dir="./train_data/data_lmdb_release/training/")
        transforms = _[
            DecodeImage(img_mode="BGR", channel_first=False),
            CTCLabelEncode(),
            RecResizeImg(image_shape=[3, 32, 100]),
            KeepKeys(keep_keys=["image", "label", "length"]),
        ]
        DATALOADER = _(shuffle=True, batch_size=256, drop_last=True, num_workers=8)

    class Eval:
        Dataset = _(LMDBDataSet, data_dir="./train_data/data_lmdb_release/validation/")
        transforms = _[
            DecodeImage(img_mode="BGR", channel_first=False),
            CTCLabelEncode(),
            RecResizeImg(image_shape=[3, 32, 100]),
            KeepKeys(keep_keys=["image", "label", "length"]),
        ]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=256, num_workers=4)
