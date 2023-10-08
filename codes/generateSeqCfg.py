import os
import argparse
from Datasets import DATASET

def getCfg(binName, recName, srcName, frameRate, width, height, frameNum, qp):
    
    cfg =   "#======== Profile definition ==============\n" \
            "#======== File I/O =====================\n" \
            f"BitstreamFile                 : {binName}\n" \
            f"ReconFile                     : {recName}\n" \
            f"InputFile                     : {srcName}\n" \
            "InputBitDepth                 : 8           # Input bitdepth\n" \
            "InputChromaFormat             : 420         # Ratio of luminance to chrominance samples\n" \
            "ChromaFormatIDC               : 420                                        \n" \
            f"FrameRate                     : {frameRate} # Frame Rate per second\n" \
            "FrameSkip                     : 0           # Number of frames to be skipped in input\n" \
            f"SourceWidth                   : {width}     # Input  frame width\n" \
            f"SourceHeight                  : {height}    # Input  frame height\n" \
            f"FramesToBeEncoded             : {frameNum}  # Number of frames to be coded\n" \
            "\n" \
            "#======== Others =======================\n" \
            f"QP                            : {qp}        # Quantization parameter(0-51)\n" \
            "Level                         : 4.1\n" \
                "InternalBitDepth                : 8\n"

    return cfg

def exportCfg(cfgName, cfg):
    with open(cfgName, 'w') as f:
        f.write(cfg)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Set the root of dataset and for save")
    parser.add_argument('--datasetRoot', type=str, default="/home/pc3447/Datasets/")
    parser.add_argument('--saveRoot', type=str, required=True)
    args = parser.parse_args()

    datasets = DATASET
    
    args.datasetRoot = os.path.abspath(args.datasetRoot)
    os.makedirs(args.saveRoot, exist_ok=True)

    qpValues = [19]

    for datasetName, seqs in datasets.items():
        for qp in qpValues:
            savePath = os.path.abspath(os.path.join(args.saveRoot, datasetName, f"qp={qp}"))
            os.makedirs(savePath, exist_ok=True)

            for seqName, seq in seqs.items():
                saveFolder = os.path.join(savePath, seqName)
                os.makedirs(saveFolder, exist_ok=True)

                width, height = seq["frameWH"]
                if datasetName != "CLIC2022_YUV420":
                    name = f"{seqName}_{width}x{height}_{seq['frameRate']}" 
                else:
                    name = seqName

                binName = os.path.join(saveFolder, name + '.bin')
                recName = os.path.join(saveFolder, name + '.yuv')
                srcName = os.path.join(args.datasetRoot, datasetName, name + '.yuv')
                cfg = getCfg(binName, recName, srcName, seq["frameRate"], width, height, seq["frameNum"], qp)
                
                cfgName = os.path.join(saveFolder, name + '.cfg')
                exportCfg(cfgName, cfg)

