import os
import csv
import argparse
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from math import log10
import torch.nn as nn
from Setting import DATASET, QP

from torchvision.utils import save_image
from torchvision import transforms
from torchvision.datasets.folder import default_loader as imgloader


class Read_YUV_Video():
    def __init__(self, file_path, srcFormat, dstFormat, W_H, frame_num, interpolation='bilinear'):
        """
        Args:
            file_path (str): video path
            srcFormat (str): yuv sub sampling format for input video, 444, 420
            dstFormat (str): yuv sub sampling format for out video, 444, 420
            W_H (tuple):  (W, H)
            frame_num (int): frame number to read
        """

        self.file_path = file_path
        self.files = open(file_path, "rb")
        self.srcFormat = srcFormat
        self.dstFormat = dstFormat
        self.W, self.H = W_H
        self.frame_num = frame_num
        self.interpolation = interpolation
        self.iter_cnt = 1
        
        # Y components
        self.y_size = self.H * self.W
        
        # UV components
        self.scale = 1 if srcFormat == '444' else 2
        self.uv_size = self.H * self.W * 2 if srcFormat == '444' else self.H // self.scale * self.W // self.scale * 2
        
        # check video frame number
        self.check_video_sanity(file_path)
        
    def read_one_frame(self):
        if self.iter_cnt > self.frame_num:
            raise f"Access frame out of range. Accessing {self.iter_cnt}th frame, but frame range set to {self.frame_num} !!!"
        
        self.iter_cnt += 1
        
        Y = self.files.read(self.y_size)
        UV = self.files.read(self.uv_size)
        Y = np.frombuffer(Y, dtype=np.uint8).reshape(1, self.H, self.W)
        UV = np.frombuffer(UV, dtype=np.uint8).reshape(2, self.H // self.scale, self.W // self.scale)
        Y = Y.astype(np.float32) / 255
        UV = UV.astype(np.float32) / 255

        Y = torch.from_numpy(Y).type(torch.FloatTensor)    
        UV = torch.from_numpy(UV).type(torch.FloatTensor)  
        
        if self.srcFormat == self.dstFormat:
            return Y, UV
        elif self.srcFormat == '420' and self.dstFormat == '444':
            UV = F.interpolate(UV.unsqueeze(0), scale_factor=2, mode=self.interpolation)[0]
            return Y, UV
        elif self.srcFormat == '444' and self.dstFormat == '420':
            UV = F.interpolate(UV.unsqueeze(0), scale_factor=1/2, mode=self.interpolation)[0]
            return Y, UV
        else:
            raise NotImplementedError
        
    def check_video_sanity(self, file_path):
        total_size = Path(file_path).stat().st_size
        if total_size < (self.y_size + self.uv_size) * self.frame_num:
            raise IndexError(f"Video file {file_path} didn't be compressed properly, it should contain {self.frame_num} frames !!!")


class MetricType():
    def __init__(self, metric='psnr'):
        self.criterion = nn.MSELoss(reduction='none') 

    def mse2psnr(self, mse, data_range=1.):
        """PSNR for numpy mse"""
        return 20 * log10(data_range) - 10 * log10(mse)
    
    def compute_PSNR_YUV(self, rec_y, rec_uv, raw_y, raw_uv):
        
        yuv_mse, y_mse, u_mse, v_mse = self.compute_mse(rec_y, rec_uv, raw_y, raw_uv)
        y_psnr = self.mse2psnr(y_mse)
        u_psnr = self.mse2psnr(u_mse)
        v_psnr = self.mse2psnr(v_mse)

        return (y_psnr * 6 + u_psnr + v_psnr) / 8, y_psnr, u_psnr, v_psnr

    def compute_mse(self, rec_y, rec_uv, raw_y, raw_uv):

        rec_u = rec_uv[0]
        rec_v = rec_uv[1]
        
        raw_u = raw_uv[0]
        raw_v = raw_uv[1]
        
        y_mse = self.criterion(rec_y, raw_y).mean()
        u_mse = self.criterion(rec_u, raw_u).mean()
        v_mse = self.criterion(rec_v, raw_v).mean()
        
        return (y_mse * 6 + u_mse + v_mse) / 8, y_mse, u_mse, v_mse 


def Compute_RD_PerSequence(recName, outName, srcName, reportPath, W_H=(1920, 1080), frameNum=96, srcFormat='420', dstFormat='420', metric='psnr'):

    def getBits(outName, length=96):
        bits = [0] * length
        with open(outName, 'r') as f:
            lines = f.read().split('\n')
            for line in lines:
                if "POC" in line:
                    idx = int(line.split("TId:")[0].split()[1].strip())
                    if idx < length:
                        bits[idx] = int(line.split(")")[-1].split("bits")[0].strip())
        return bits
    

    rec_video = Read_YUV_Video(file_path=recName, srcFormat=srcFormat, dstFormat=dstFormat, W_H=W_H, frame_num=frameNum) 
    raw_video = Read_YUV_Video(file_path=srcName, srcFormat=srcFormat, dstFormat=dstFormat, W_H=W_H, frame_num=frameNum)  
    Metric = MetricType(metric=metric)
    
    bits_profile = [ i / (W_H[0] * W_H[1]) for i in getBits(outName, length=frameNum)]
    

    columns = ['frame', 'YUV-PSNR', 'Rate', 'Y-PSNR', 'U-PSNR', 'V-PSNR']
    
    with open(reportPath, 'w', newline='') as report:
        writer = csv.writer(report, delimiter=',')
        writer.writerow(columns)
            
        for idx in range(frameNum):
            rec_y, rec_uv = rec_video.read_one_frame()
            raw_y, raw_uv = raw_video.read_one_frame()
            
            YUV_PSNR, Y_PSNR, U_PSNR, V_PSNR = Metric.compute_PSNR_YUV(rec_y, rec_uv, raw_y, raw_uv)
            writer.writerow([f'frame_{idx + 1}', YUV_PSNR, bits_profile[idx], Y_PSNR, U_PSNR, V_PSNR])


if __name__ == '__main__':
    print('Remember to check Dataset Profile is as expected !!!')

    parser = argparse.ArgumentParser(description="Compute the metrics between reconstruction and ground truth")
    parser.add_argument('--datasetRoot', type=str, required=True)
    parser.add_argument('--recRoot', type=str, required=True)
    parser.add_argument('--saveRoot', type=str, required=True)
    parser.add_argument('--srcFormat', type=str, default="420")
    parser.add_argument('--dstFormat', type=str, default="420")
    parser.add_argument('--metric', type=str, default="psnr")
    parser.add_argument('--frameNum', type=int, default=-1)
    args = parser.parse_args()
    
    datasets = DATASET
    qpValues = QP
    
    os.makedirs(args.saveRoot, exist_ok=True)
    
    for datasetName, seqs in datasets.items():
        for qp in qpValues:
            savePath = os.path.join(args.saveRoot, 'report', f"qp={qp}")
            os.makedirs(savePath, exist_ok=True)
            for seqName, seqInfo in seqs.items():
                if args.frameNum > 0:
                    frameNum = args.frameNum
                else:
                    frameNum = seqInfo['frameNum']

                if 'alias' in seqInfo:
                    reportPath = os.path.join(savePath, f"{seqInfo['alias']}.csv")
                else:
                    reportPath = os.path.join(savePath, f"{seqName}.csv")

                Compute_RD_PerSequence(
                    recName = os.path.join(args.recRoot, datasetName, f"qp={qp}", seqName, f"{seqInfo['vi_name']}.yuv"),
                    outName = os.path.join(args.recRoot, datasetName, f"qp={qp}", seqName, f"{seqInfo['vi_name']}.out"),
                    srcName = os.path.join(args.datasetRoot, datasetName, seqName, f"{seqInfo['vi_name']}.yuv"),
                    reportPath = reportPath,
                    W_H = seqInfo['frameWH'],
                    frameNum = frameNum,
                    srcFormat = args.srcFormat,
                    dstFormat = args.dstFormat,
                    metric = args.metric,
                )
