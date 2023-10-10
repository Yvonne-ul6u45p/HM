import os
import argparse
from tqdm import tqdm
from subprocess import Popen, PIPE
from Setting import DATASET


def convertYUV420VideoToPNGImages(videoName: str, frameWH: tuple, numFrame: int, saveFolder: str, outName: str) -> None:
    w, h = frameWH
    command = f"ffmpeg -pix_fmt yuv420p -s {w}x{h} -i {videoName} -vframes {numFrame} {os.path.join(saveFolder, 'frame_%d.png')} > {outName}"
    return Popen(command, universal_newlines=True, shell=True, stdout=PIPE, stderr=PIPE)

if __name__ == "__main__":      
    datasets = DATASET

    parser = argparse.ArgumentParser(description="Select which dataset to decode to png")
    parser.add_argument('--dataRoot', type=str, required=True)
    args = parser.parse_args()

    for datasetName, seqs in datasets.items():
        qpProcesses = []
        for seqName, seq in seqs.items():
            cfgPath = os.path.join(args.dataRoot, datasetName)
            width, height = seq["frameWH"]
            if datasetName != "CLIC2022_YUV420" and datasetName != "ISCAS2023_YUV420":
                name = f"{seqName}_{width}x{height}_{seq['frameRate']}" 
            else:
                name = seqName

            videoName = os.path.join(cfgPath, name + '.yuv')
            outName = os.path.join(cfgPath, name + '_png.out')
            saveFolder = os.path.join(cfgPath, seqName)

            os.makedirs(saveFolder, exist_ok=True)
            # print(videoName, outName, saveFolder)
            # print(seq['frameWH'], seq['frameNum'])
            
            qpProcesses.append(convertYUV420VideoToPNGImages(videoName, seq['frameWH'], seq['frameNum'], saveFolder, outName))
        
    # print("Wait...")
    for p in qpProcesses:
        p.wait()
    # print("Done")
