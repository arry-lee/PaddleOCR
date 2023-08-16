# This .py is auto generated by the script in the root folder.
from configs.config import ConfigModel, _
from ppocr.modeling.backbones.e2e_resnet_vd_pg import ResNet
from ppocr.modeling.necks.pg_fpn import PGFPN
from ppocr.modeling.heads.e2e_pg_head import PGHead
from ppocr.losses.e2e_pg_loss import PGLoss
from ppocr.metrics.e2e_metric import E2EMetric
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from ppocr.postprocess.pg_postprocess import PGPostProcess
from ppocr.data.pgnet_dataset import PGDataSet
from ppocr.data.imaug.operators import E2EResizeForTest, DecodeImage, KeepKeys, NormalizeImage, ToCHWImage
from ppocr.data.imaug.label_ops import E2ELabelEncodeTest, E2ELabelEncodeTrain
from ppocr.data.imaug.pg_process import PGProcessTrain


class Model(ConfigModel):
    use_gpu = True
    epoch_num = 600
    log_window_size = 20
    log_batch_step = 10
    save_model_dir = "./output/pgnet_r50_vd_totaltext/"
    save_epoch_step = 10
    eval_batch_step = [0, 1000]
    metric_during_train = False
    pretrained_model = None
    checkpoints = None
    save_infer_dir = None
    use_visualdl = False
    infer_img = None
    infer_visual_type = "EN"
    valid_set = "totaltext"
    save_res_path = "./output/pgnet_r50_vd_totaltext/predicts_pgnet.txt"
    character_dict_path = "ppocr/utils/ic15_dict.txt"
    character_type = "EN"
    max_text_length = 50
    max_text_nums = 30
    tcl_len = 64
    model_type = "e2e"
    algorithm = "PGNet"
    Transform = None
    Backbone = _(ResNet, layers=50)
    Neck = _(
        PGFPN,
    )
    Head = _(PGHead, character_dict_path="ppocr/utils/ic15_dict.txt")
    loss = PGLoss(tcl_bs=64, max_text_length=50, max_text_nums=30, pad_num=36)
    metric = E2EMetric(
        mode="A",
        gt_mat_dir="./train_data/total_text/gt",
        character_dict_path="ppocr/utils/ic15_dict.txt",
        main_indicator="f_score_e2e",
    )
    Optimizer = _(Adam, betas=[0.9, 0.999], lr=0.001)
    LRScheduler = _(CosineAnnealingWarmRestarts, T_0=50)
    PostProcessor = _(PGPostProcess, score_thresh=0.5, mode="fast", point_gather_mode="align")

    class Train:
        Dataset = _(
            PGDataSet,
            data_dir="./train_data/total_text/train",
            label_file_list=["./train_data/total_text/train/train.txt"],
            ratio_list=[1.0],
        )
        transforms = _[
            DecodeImage(img_mode="BGR", channel_first=False),
            E2ELabelEncodeTrain(),
            PGProcessTrain(
                batch_size=14,
                use_resize=True,
                use_random_crop=False,
                min_crop_size=24,
                min_text_size=4,
                max_text_size=512,
                point_gather_mode="align",
            ),
            KeepKeys(
                keep_keys=[
                    "images",
                    "tcl_maps",
                    "tcl_label_maps",
                    "border_maps",
                    "direction_maps",
                    "training_masks",
                    "label_list",
                    "pos_list",
                    "pos_mask",
                ]
            ),
        ]
        DATALOADER = _(shuffle=True, drop_last=True, batch_size=14, num_workers=16)

    class Eval:
        Dataset = _(
            PGDataSet,
            data_dir="./train_data/total_text/test",
            label_file_list=["./train_data/total_text/test/test.txt"],
        )
        transforms = _[
            DecodeImage(img_mode="BGR", channel_first=False),
            E2ELabelEncodeTest(),
            E2EResizeForTest(max_side_len=768),
            NormalizeImage(scale="1./255.", mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], order="hwc"),
            ToCHWImage(),
            KeepKeys(keep_keys=["image", "shape", "polys", "texts", "ignore_tags", "img_id"]),
        ]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=1, num_workers=2)
