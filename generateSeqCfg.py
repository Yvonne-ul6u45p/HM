import os
import sys
import argparse
from Setting import DATASET, QP


def getCfg(binName, recName, srcName, frameRate, width, height, frameNum, qp, args):
    
    if args.file_ext == 'yuv':
        cfg =   "#======== Profile definition ==============\n" \
                "#======== File I/O ========================\n" \
               f"BitstreamFile                 : {binName}\n" \
               f"ReconFile                     : {recName}\n" \
               f"InputFile                     : {srcName}\n" \
                "InputBitDepth                 : 8\t\t# Input bitdepth\n" \
                "InputChromaFormat             : 420\t\t# Ratio of luminance to chrominance samples\n" \
                "ChromaFormatIDC               : 420\n" \
               f"FrameRate                     : {frameRate}\t\t# Frame Rate per second\n" \
                "FrameSkip                     : 0\t\t# Number of frames to be skipped in input\n" \
               f"SourceWidth                   : {width} \t# Input frame width\n" \
               f"SourceHeight                  : {height} \t# Input frame height\n" \
               f"FramesToBeEncoded             : {frameNum}\t\t# Number of frames to be coded\n" \
                "\n" \
                "#======== Others ==========================\n" \
               f"QP                            : {qp}\t\t# Quantization parameter(0-51)\n" \
                "Level                         : 4.1\n" \
                "InternalBitDepth              : 8\n" \
               f"IntraPeriod                   : {args.intra_period}"

    elif args.file_ext == 'rgb':
        cfg =   "#======== Profile definition ==============\n" \
                "#======== File I/O ========================\n" \
               f"BitstreamFile                 : {binName}\n" \
               f"ReconFile                     : {recName}\n" \
               f"InputFile                     : {srcName}\n" \
                "InputBitDepth                 : 10\t\t# Input bitdepth\n" \
                "InputChromaFormat             : 444\t\t# Ratio of luminance to chrominance samples\n" \
               f"FrameRate                     : {frameRate}\t\t# Frame Rate per second\n" \
                "FrameSkip                     : 0\t\t# Number of frames to be skipped in input\n" \
               f"SourceWidth                   : {width}\t# Input frame width\n" \
               f"SourceHeight                  : {height}\t# Input frame height\n" \
               f"FramesToBeEncoded             : {frameNum}\t\t# Number of frames to be coded\n" \
               f"InputColourSpaceConvert       : RGBtoGBR\t# Non-normative colour space conversion to apply to input video" \
               f"SNRInternalColourSpace        : 1\t\t# Evaluate SNRs in GBR order" \
               f"OutputInternalColourSpace     : 0\t\t# Convert recon output back to RGB order. Use --OutputColourSpaceConvert GBRtoRGB on decoder to produce a matching output file." \
                "\n" \
                "#======== Others ==========================\n" \
               f"QP                            : {qp}\t\t# Quantization parameter(0-51)\n" \
                "Level                         : 6.2\n" \
               f"IntraPeriod                   : {args.intra_period}"

    return cfg


def exportCfg(cfgName, cfg):
    with open(cfgName, 'w') as f:
        f.write(cfg)


def main(argv):

    parser = argparse.ArgumentParser(description="Set the root of datasets and for save")
    parser.add_argument('--datasetRoot', type=str, required=True, help="Root of datasets")
    parser.add_argument('--saveRoot', type=str, required=True, help="Path for saving the cfg files and results")
    parser.add_argument('--intra_period', type=int, default=32)
    parser.add_argument('--frameNum', type=int, default=-1)
    args = parser.parse_args(argv)

    datasets = DATASET
    qpValues = QP
    
    args.datasetRoot = os.path.abspath(args.datasetRoot)
    os.makedirs(args.saveRoot, exist_ok=True)

    for datasetName, seqs in datasets.items():
        for qp in qpValues:
            savePath = os.path.abspath(os.path.join(args.saveRoot, datasetName, f"qp={qp}"))
            os.makedirs(savePath, exist_ok=True)

            for seqName, seq in seqs.items():
                saveFolder = os.path.join(savePath, seqName)
                os.makedirs(saveFolder, exist_ok=True)

                width, height = seq["frameWH"]
                if datasetName == 'HEVC-RGB':
                    name = seq['vi_name']
                    args.file_ext = 'rgb'
                elif datasetName == "CLIC2022_YUV420":
                    name = seqName
                    args.file_ext = 'yuv'
                else:
                    name = seq['vi_name']
                    args.file_ext = 'yuv'

                binName = os.path.join(saveFolder, name + '.bin')
                recName = os.path.join(saveFolder, name + f'.{args.file_ext}')
                srcName = os.path.join(args.datasetRoot, datasetName, seqName, name + f'.{args.file_ext}')
                print("srcName", srcName)

                if args.frameNum > 0:
                    frameNum = args.frameNum
                else:
                    frameNum = seq["frameNum"]
                
                cfg = getCfg(binName, recName, srcName, seq["frameRate"], width, height, frameNum, qp, args)
                
                cfgName = os.path.join(saveFolder, name + '.cfg')
                exportCfg(cfgName, cfg)


if __name__ == "__main__":
    main(sys.argv[1:])
