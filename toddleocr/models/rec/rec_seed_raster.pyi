# This .pyi is auto generated by the script in the root folder.
# only for cache,use .py for changes
from toddleocr.config import _, ConfigModel
from toddleocr.datasets.lmdb import LMDBDataSet
from toddleocr.loss.aster import AsterLoss
from toddleocr.metrics.rec import RecMetric
from toddleocr.modules.backbones.resnet.rec_resnet_aster import ResNet_ASTER
from toddleocr.modules.heads.aster import AsterHead
from toddleocr.modules.transforms.stn import STN_ON
from toddleocr.optim.lr_scheduler import PiecewiseLR
from toddleocr.postprocess.rec import SEEDLabelDecode
from toddleocr.transforms.label_ops import SEEDLabelEncode
from toddleocr.transforms.operators import DecodeImage, Fasttext, KeepKeys
from toddleocr.transforms.rec_img_aug import RecResizeImg
from torch.optim import Adadelta

class Model(ConfigModel):
    use_gpu = True
    epoch_num = 6
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = None
    save_epoch_step = 3
    eval_batch_step = [0, 2000]
    metric_during_train = True
    pretrained_model = None
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    character_dict_path = "ppocr/utils/EN_symbol_dict.txt"
    max_text_length = 100
    infer_mode = False
    use_space_char = False
    model_type = "rec"
    algorithm = "SEED"
    Transform = _(
        STN_ON,
        tps_inputsize=[32, 64],
        tps_outputsize=[32, 100],
        num_control_points=20,
        tps_margins=[0.05, 0.05],
        stn_activation="none",
    )
    Backbone = _(
        ResNet_ASTER,
    )
    Head = _(AsterHead, sDim=512, attDim=512, max_len_labels=100)
    loss = AsterLoss()
    metric = RecMetric(main_indicator="acc", is_filter=True)
    postprocessor = SEEDLabelDecode()
    Optimizer = _(Adadelta, weight_deacy=0.0, momentum=0.9)
    LRScheduler = _(PiecewiseLR, decay_epochs=[4, 5], values=[1.0, 0.1, 0.01])

    class Data:
        dataset = LMDBDataSet
        root: "train_data/data_lmdb_release/evaluation/" = (
            "train_data/data_lmdb_release/training/"
        )

    class Loader:
        shuffle: False = True
        drop_last = True
        batch_size = 256
        num_workers: 4 = 6
    Transforms = _[
        Fasttext(path="./cc.en.300.bin") :,
        DecodeImage(img_mode="BGR", channel_first=False),
        SEEDLabelEncode() : ...,
        RecResizeImg(character_dict_path=None, image_shape=[3, 64, 256], padding=False),
        KeepKeys("image", "label", "length", "fast_label") : KeepKeys(
            "image", "label", "length"
        ) : ...,
    ]
