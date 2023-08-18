from torch import nn


class BaseModel(nn.Module):
    def __init__(self, in_channels, backbone, neck, head, return_all_feats=False):
        super().__init__()
        if backbone:
            self.backbone = backbone(in_channels=in_channels)
            in_channels = self.backbone.out_channels
        if neck:
            self.neck = neck(in_channels=in_channels)
            in_channels = self.neck.out_channels
        if head:
            self.head = head(in_channels=in_channels)
        self.return_all_feats = return_all_feats

    def forward(self, x):
        out_dict = {}
        for module_name, module in self.named_children():
            x = module(x)
            if isinstance(x, dict):
                out_dict.update(x)
            else:
                out_dict[f"{module_name}_out"] = x
        if self.return_all_feats:
            if self.training:
                return out_dict
            elif isinstance(x, dict):
                return x
            else:
                return {list(out_dict.keys())[-1]: x}
        else:
            return x
