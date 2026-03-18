from anomalib.models import get_model
import torch
from torchvision import transforms
import cv2
import numpy as np
from omegaconf import OmegaConf
import logging

logger = logging.getLogger()


class AnomalibInference:
    def __init__(self, ckpt_path, cfg_path, cuda=False):
        self.cuda = cuda

        self.device = "cuda" if cuda else "cpu"

        cfg = OmegaConf.load(cfg_path)
        self.model = get_model(cfg.model)
        ckpt = torch.load(ckpt_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(ckpt["state_dict"], strict=False)
        self.model.to(self.device)

        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])

    def _preproess(self, im):
        x = self.transform(im) 
        x = x.unsqueeze(0)
        
        return x

    def infer(self, im):
        x = self._preproess(im)

        with torch.no_grad():
            outputs = self.model(x.to(self.device))

        score = outputs.pred_score.item()
        pred_label = outputs.pred_label.item()
        anomaly_map = outputs.anomaly_map.detach().cpu().numpy()
        mask = outputs.pred_mask.detach().cpu().numpy()

        return score, pred_label, anomaly_map, mask
    