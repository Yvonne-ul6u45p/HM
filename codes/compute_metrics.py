import sys
sys.path.append('../../torchDVC/util')
import os
import argparse
import torch
import numpy as np
import matplotlib
import csv
from glob import glob
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from tqdm import tqdm
from PIL import Image
from subprocess import Popen, PIPE
from psnr import psnr as psnr_fn
from ssim import MS_SSIM
from vision import imgloader, rgb_transform
from torch.utils.data import Dataset as torchData
from torch.utils.data import DataLoader
from warnings import warn
from Setting import DATASET, QP

msssim_fn = MS_SSIM(data_range=1.)

def computeRateOfEncodeVideo(videoName: str, frameWH: tuple, frameNum: int, frameRate: int, biasBits: int) -> tuple:
    sizeInBits = os.path.getsize(videoName) * 8 - biasBits
    
    w, h = frameWH
    bpp = sizeInBits / (frameNum * w * h)

    durationInSecond = frameNum / frameRate
    bps = sizeInBits  / durationInSecond

    return bpp, bps

@torch.no_grad()
def computeQualityOfDecodedImages(frameNum: int, targetImageFolder: str, decodeImageFolder: str) -> tuple:
    sumPSNR = 0
    sumMSSSIM = 0

    class frameDataset(torchData):
        def __init__(self, frameNum, targetImageFolder, decodeImageFolder):
            super().__init__()
            self.frameNum = frameNum
            self.targetImageFolder = targetImageFolder
            self.decodeImageFolder = decodeImageFolder
            
        def __len__(self):
            return self.frameNum

        def __getitem__(self, index):
            frameIdx = index + 1
            targetFrameName = os.path.join(self.targetImageFolder, f"frame_{frameIdx}.png")
            decodeFrameName = os.path.join(self.decodeImageFolder, f"frame_{frameIdx}.png")
        
            targetFrame = rgb_transform(imgloader(targetFrameName))
            decodeFrame = rgb_transform(imgloader(decodeFrameName))

            return frameIdx, targetFrame, decodeFrame

    def getBits(logName, length):
        bits = [0] * length
        with open(logName, 'r') as f:
            lines = f.read().split('\n')
            for line in lines:
                if "POC" in line:
                    idx = int(line.split("TId:")[0].split()[1].strip())
                    if idx < frameNum:
                        bits[idx] = int(line.split(")")[-1].split("bits")[0].strip())
        return bits

    logfile = glob(os.path.join(os.path.dirname(decodeImageFolder), "*.out"))
    logfile = [f for f in logfile if not "_png" in f][0]
    bits = getBits(logfile, frameNum)

    report = open(os.path.join(os.path.dirname(decodeImageFolder), "report.csv"), 'w', newline='')
    writer = csv.writer(report, delimiter=',')
    writer.writerow(['frame', 'PSNR', 'MS-SSIM', 'rate'])

    frameLoader = DataLoader(frameDataset(frameNum, targetImageFolder, decodeImageFolder),
                             batch_size=1,
                             num_workers=8,
                             shuffle=False)

    for frameIdx, targetFrame, decodeFrame in tqdm(frameLoader, total=frameNum):
        targetFrame = targetFrame
        decodeFrame = decodeFrame
        psnrOfImage = psnr_fn(targetFrame, decodeFrame, data_range=1.) # for per pixel average of all sequence
        msssimOfImage = msssim_fn(targetFrame, decodeFrame)
        rateOfImage = bits[frameIdx - 1] / (targetFrame.size(-2) * targetFrame.size(-1))

        # assert not torch.isnan(msssimOfImage), f"Frame {frameIdx} in {decodeImageFolder} has nan MS-SSIM value"

        writer.writerow([int(frameIdx), float(psnrOfImage), float(msssimOfImage), rateOfImage])
        #writer.writerow([int(frameIdx.cpu()), float(psnrOfImage), None, rateOfImage])

        sumPSNR += psnrOfImage
        sumMSSSIM += msssimOfImage

    averagePSNR = sumPSNR / frameNum
    averageMSSSIM = sumMSSSIM / frameNum
    report.close()

    return averagePSNR, float(averageMSSSIM.cpu())

def recordValuesTo(filename: str, videoName: str, frameNum: int, bps: float, bpp: float, psnr: float, msssim: float, last=False) -> None:
    file = open(filename, "a")
    file.write(f"Name: {videoName:<20} (num = {frameNum:4d})\t")
    file.write(f"MBps: {bps / 1e6:8.4f}\t")
    file.write(f"Bpp: {bpp:7.4f}\t")
    file.write(f"PSNR: {psnr:7.4f}\t")
    file.write(f"MS-SSIM: {msssim:6.4f}\n")
    if last:
        file.write("===========================\n")
    file.close()

if __name__ == "__main__":      
    datasets = DATASET
    
    parser = argparse.ArgumentParser(description="Select which dataset to test on x265 codec")
    parser.add_argument('--datasetRoot', type=str, default="/home/pc3447/Datasets/")
    parser.add_argument('--recRoot', type=str, default="./LDP")
    parser.add_argument('--savePath', type=str, required=True)
    parser.add_argument('--dropLast', action="store_true")
    args = parser.parse_args()
    qpValues = QP
    
    for qp in tqdm(qpValues):
        txtName = os.path.join(args.savePath, f"brief_summary_{qp}.txt")

        for datasetName, seqs in datasets.items():
            totalFrameNum = 0
            totalBps = totalBpp = totalPsnr = totalMsssim = 0.
            
            for seqName, seq in seqs.items():
                frameWH = seq['frameWH']
                frameNum = seq['frameNum']
                frameRate = seq['frameRate']
                w, h = frameWH

                recPath = os.path.join(args.recRoot, datasetName, f"qp={qp}", seqName)
                tarFrameFolder = os.path.join(args.datasetRoot, datasetName, seqName)
                if datasetName != "CLIC2022_YUV420" and datasetName != "ISCAS2023_YUV420":
                    recName = f"{seqName}_{w}x{h}_{frameRate}"
                else: 
                    recName = seqName
            
                logName = os.path.join(recPath, recName + ".out")
                
                if args.dropLast:
                    frameNum -= 1
                    with open(logName, 'r') as f:
                        lines = f.read().split('\n')
                        for line in lines:
                            if "POC" in line and f"{frameNum} TId: " in line:
                                # warn(f"Drop '{line}'")
                                biasBits = int(line.split(")")[-1].split("bits")[0].strip())
                                break
                        else:
                            raise ValueError("Can't find tail case")
                else:
                    biasBits = 0
        
                # get rate
                binName = os.path.join(recPath, recName + ".bin")
                bpp, bps = computeRateOfEncodeVideo(binName, frameWH, frameNum, frameRate, biasBits)

                recFrameFolder = os.path.join(recPath, 'rgb')
                psnr, msssim = computeQualityOfDecodedImages(frameNum, tarFrameFolder, recFrameFolder)
                recordValuesTo(txtName, seqName, frameNum, bps, bpp, psnr, msssim)

                totalFrameNum += frameNum
                totalBps += bps * frameNum
                totalBpp += bpp * frameNum
                totalPsnr += psnr * frameNum
                totalMsssim += msssim * frameNum
            
            averageBps = totalBps / totalFrameNum
            averageBpp = totalBpp / totalFrameNum
            averagePsnr = totalPsnr / totalFrameNum
            averageMsssim = totalMsssim / totalFrameNum
            recordValuesTo(txtName, datasetName, totalFrameNum, averageBps, averageBpp, averagePsnr, averageMsssim, last=True)
