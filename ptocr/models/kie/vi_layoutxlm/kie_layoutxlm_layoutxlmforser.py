# This .py is auto generated by the script in the root folder.
from ptocr.config import ConfigModel,_
from ptocr.modules.backbones.vqa_layoutlm import LayoutXLMForSer
from ptocr.loss.vqa_token_layoutlm import VQASerTokenLayoutLMLoss
from ptocr.metrics.vqa import VQASerTokenMetric
from ptocr.postprocess.vqa import VQASerTokenLayoutLMPostProcess
from torch.optim import AdamW
from torch.optim.lr_scheduler import PolynomialLR
from ptocr.datasets.simple import SimpleDataSet
from ptocr.transforms.operators import ToCHWImage, KeepKeys, NormalizeImage, DecodeImage, Resize
from ptocr.transforms.label_ops import VQATokenLabelEncode
from ptocr.transforms.vqa.token.vqa_token_pad import VQATokenPad
from ptocr.transforms.vqa.token.vqa_token_chunk import VQASerTokenChunk
class Model(ConfigModel):
    use_gpu = True
    epoch_num = 200
    log_window_size = 10
    log_batch_step = 10
    save_model_dir = "./output/ser_vi_layoutxlm_xfund_zh"
    save_epoch_step = 2000
    eval_batch_step = [0, 19]
    metric_during_train = False
    save_infer_dir = None
    use_visualdl = False
    seed = 2022
    infer_img = "ppstructure/docs/kie/input/zh_val_42.jpg"
    save_res_path = "./output/ser/xfund_zh/res"
    kie_rec_model_dir = None
    kie_det_model_dir = None
    model_type = 'kie'
    algorithm = 'LayoutXLM'
    Transform = None
    Backbone = _(LayoutXLMForSer, pretrained=True, checkpoints=None, mode="vi", num_classes=7)
    loss = VQASerTokenLayoutLMLoss(num_classes=7, key="backbone_out")
    metric = VQASerTokenMetric(main_indicator="hmean")
    postprocessor = VQASerTokenLayoutLMPostProcess(class_path="train_data/XFUND/class_list_xfun.txt")
    Optimizer = _(AdamW,beta1=0.9, beta2=0.999, lr=5e-05)
    LRScheduler = _(PolynomialLR,total_iters=200, warmup_epoch=2)
    class Train:
        Dataset = _(SimpleDataSet, root="train_data/XFUND/zh_train/image", label_file_list=['train_data/XFUND/zh_train/train.json'], ratio_list=[1.0])
        transforms = _[DecodeImage(img_mode="RGB", channel_first=False), VQATokenLabelEncode(contains_re=False, algorithm="LayoutXLM", class_path="train_data/XFUND/class_list_xfun.txt", use_textline_bbox_info=True, order_method="tb-yx"), VQATokenPad(max_seq_len=512, return_attention_mask=True), VQASerTokenChunk(max_seq_len=512), Resize(size=[224, 224]), NormalizeImage(scale=1, mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], order="hwc"), ToCHWImage(), KeepKeys(keep_keys=['input_ids', 'bbox', 'attention_mask', 'token_type_ids', 'image', 'labels'])]
        DATALOADER = _(shuffle=True, drop_last=False, batch_size=8, num_workers=4)
    class Eval:
        Dataset = _(SimpleDataSet, root="train_data/XFUND/zh_val/image", label_file_list=['train_data/XFUND/zh_val/val.json'])
        transforms = _[DecodeImage(img_mode="RGB", channel_first=False), VQATokenLabelEncode(contains_re=False, algorithm="LayoutXLM", class_path="train_data/XFUND/class_list_xfun.txt", use_textline_bbox_info=True, order_method="tb-yx"), VQATokenPad(max_seq_len=512, return_attention_mask=True), VQASerTokenChunk(max_seq_len=512), Resize(size=[224, 224]), NormalizeImage(scale=1, mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], order="hwc"), ToCHWImage(), KeepKeys(keep_keys=['input_ids', 'bbox', 'attention_mask', 'token_type_ids', 'image', 'labels'])]
        DATALOADER = _(shuffle=False, drop_last=False, batch_size=8, num_workers=4)