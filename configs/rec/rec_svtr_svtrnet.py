# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel,_
from ptocr.modules.backbones.rec_svtrnet import SVTRNet
from ptocr.modules.necks.rnn import SequenceEncoder
from ptocr.modules.heads.rec_ctc_head import CTCHead
from ptocr.loss.rec_ctc_loss import CTCLoss
from ptocr.metrics.rec_metric import RecMetric
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from ptocr.postprocess.rec_postprocess import CTCLabelDecode
from ptocr.datasets.simple_dataset import SimpleDataSet
from ptocr.datasets.imaug.operators import DecodeImage, KeepKeys
from ptocr.datasets.imaug.rec_img_aug import RecConAug, SVTRRecResizeImg, RecAug
from ptocr.datasets.imaug.label_ops import CTCLabelEncode
class Model(ConfigModel):
    use_gpu = True
    epoch_num = 100
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/rec/svtr_ch_all/"
    save_epoch_step = 10
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
    save_res_path = "./output/rec/predicts_svtr_tiny_ch_all.txt"
    model_type = 'rec'
    algorithm = 'SVTR'
    Transform = None
    Backbone = _(SVTRNet, img_size=[32, 320], out_char_num=40, out_channels=96, patch_merging="Conv", embed_dim=[64, 128, 256], depth=[3, 6, 3], num_heads=[2, 4, 8], mixer=['Local', 'Local', 'Local', 'Local', 'Local', 'Local', 'Global', 'Global', 'Global', 'Global', 'Global', 'Global'], local_mixer=[[7, 11], [7, 11], [7, 11]], last_stage=True, prenorm=False)
    Neck = _(SequenceEncoder, encoder_type="reshape")
    Head = _(CTCHead, )
    loss = CTCLoss()
    metric = RecMetric(main_indicator="acc")
    Optimizer = _(AdamW,beta1=0.9, beta2=0.99, epsilon=1e-08, weight_decay=0.05, no_weight_decay_name="norm pos_embed", one_dim_param_no_weight_decay=True, lr=0.0005)
    LRScheduler = _(CosineAnnealingWarmRestarts,T_0=2)
    PostProcessor = _(CTCLabelDecode,)
    class Train:
        Dataset = _(SimpleDataSet, data_dir="./train_data", label_file_list=['./train_data/train_list.txt'], ext_op_transform_idx=1)
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), RecConAug(prob=0.5, ext_data_num=2, image_shape=[32, 320, 3]), RecAug(), CTCLabelEncode(), SVTRRecResizeImg(image_shape=[3, 32, 320], padding=True), KeepKeys(keep_keys=['image', 'label', 'length'])]
        DATALOADER = _(shuffle=True, batch_size=256, drop_last=True, num_workers=8)
    class Eval:
        Dataset = _(SimpleDataSet, data_dir="./train_data", label_file_list=['./train_data/val_list.txt'])
        transforms = _[DecodeImage(img_mode="BGR", channel_first=False), CTCLabelEncode(), SVTRRecResizeImg(image_shape=[3, 32, 320], padding=True), KeepKeys(keep_keys=['image', 'label', 'length'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=256, num_workers=2)
