# This .pyi is auto generated by the script in the root folder.
# only for cache,use .py for changes
from toddleocr.config import _, ConfigModel
from toddleocr.datasets.simple import SimpleDataSet
from toddleocr.loss.ctc import CTCLoss
from toddleocr.metrics.rec import RecMetric
from toddleocr.modules.backbones.rec_svtrnet import SVTRNet
from toddleocr.modules.heads.ctc import CTCHead
from toddleocr.modules.necks.rnn import SequenceEncoder
from toddleocr.postprocess.rec import CTCLabelDecode
from toddleocr.transforms.label_ops import CTCLabelEncode
from toddleocr.transforms.operators import DecodeImage, KeepKeys
from toddleocr.transforms.rec_img_aug import RecAug, RecConAug, SVTRRecResizeImg
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts

class Model(ConfigModel):
    use_gpu = True
    epoch_num = 100
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = None
    save_epoch_step = 10
    eval_batch_step = [0, 2000]
    metric_during_train = True
    pretrained_model = None
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    character_dict_path = "toddleocr/utils/ppocr_keys_v1.txt"
    max_text_length = 25
    infer_mode = False
    use_space_char = True
    model_type = "rec"
    algorithm = "SVTR"
    Transform = None
    Backbone = _(
        SVTRNet,
        img_size=[32, 320],
        out_char_num=40,
        out_channels=96,
        patch_merging="Conv",
        embed_dim=[64, 128, 256],
        depth=[3, 6, 3],
        num_heads=[2, 4, 8],
        mixer=[
            "Local",
            "Local",
            "Local",
            "Local",
            "Local",
            "Local",
            "Global",
            "Global",
            "Global",
            "Global",
            "Global",
            "Global",
        ],
        local_mixer=[[7, 11], [7, 11], [7, 11]],
        last_stage=True,
        prenorm=False,
    )
    Neck = _(SequenceEncoder, encoder_type="reshape")
    Head = _(
        CTCHead,
    )
    loss = CTCLoss()
    metric = RecMetric(main_indicator="acc")
    postprocessor = CTCLabelDecode()
    Optimizer = _(
        AdamW,
        beta1=0.9,
        beta2=0.99,
        eps=1e-08,
        weight_decay=0.05,
        no_weight_decay_name="norm pos_embed",
        one_dim_param_no_weight_decay=True,
        lr=0.0005,
    )
    LRScheduler = _(CosineAnnealingWarmRestarts, T_0=2)

    class Data:
        dataset = SimpleDataSet
        root = "train_data"
        label_file_list: "val_list.txt" = "train_list.txt"

    class Loader:
        shuffle: False = True
        drop_last: False = True
        batch_size = 256
        num_workers: 2 = 8
    Transforms = _[
        DecodeImage(img_mode="BGR", channel_first=False),
        RecConAug(prob=0.5, ext_data_num=2, image_shape=[32, 320, 3]) :,
        RecAug() :,
        CTCLabelEncode() : ...,
        SVTRRecResizeImg(image_shape=[3, 32, 320], padding=True),
        KeepKeys("image", "label", "length") : ...,
    ]
