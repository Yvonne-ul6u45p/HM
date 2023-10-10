import os
import argparse
from tqdm import tqdm
from subprocess import Popen, PIPE
from Setting import DATASET, QP

def runHMcodec(codingCfg: str, seqCfg: str, outName: str) -> None:
    command = f"TAppEncoderStaticd -c {codingCfg} -c {seqCfg} > {outName}"
    print("hm.py\tRun command: ", command)
    return Popen(command, universal_newlines=True, shell=True, stdout=PIPE, stderr=PIPE)


if __name__ == "__main__":      

    parser = argparse.ArgumentParser(description="Set the root of dataset and for save")
    parser.add_argument('--codingCfg', type=str, required=True)
    parser.add_argument('--cfgRoot', type=str, required=True)
    args = parser.parse_args()

    datasets = DATASET

    qpValues = QP

    qpProcesses = []
    for qp in tqdm(qpValues):
        for datasetName, seqs in datasets.items():
            for seqName, seq in seqs.items():
                cfgPath = os.path.join(args.cfgRoot, datasetName, f"qp={qp}", seqName)
                width, height = seq["frameWH"]
                if datasetName != "CLIC2022_YUV420" and datasetName != "ISCAS2023_YUV420":
                    name = f"{seqName}_{width}x{height}_{seq['frameRate']}" 
                else:
                    name = seqName

                cfgName = os.path.join(cfgPath, name + '.cfg')
                outName = os.path.join(cfgPath, name + '.out')
                qpProcesses.append(runHMcodec(args.codingCfg, cfgName, outName))

        # print("Wait...")
        for p in qpProcesses:
            p.wait()
        # print("Done")
