import os
import sys
import argparse
from tqdm import tqdm
from subprocess import Popen
from Setting import DATASET, QP
import warnings

def uploadReport(srcPath: str, settingName: str, qp, seqName: str) -> str:
    dstPath = f"/work_d/HM16.22/results/{settingName}-{qp}/report/{seqName}.csv"
    command = f"sshpass -p 3395  rsync -azh -e 'ssh -oStrictHostKeyChecking=no' --rsync-path='mkdir -p {os.path.dirname(dstPath)} && rsync' {srcPath}  pc3395@192.168.1.11:{dstPath}"

    return command


def run_command(command: str):
    process = Popen(command, universal_newlines=True, shell=True)
    process.wait()

    return command


def main(argv):

    parser = argparse.ArgumentParser(description="Set the root of dataset and for save")
    parser.add_argument('--reportRoots', type=str, nargs='+', required=True, help="Path for results")
    args = parser.parse_args(argv)

    datasets = DATASET
    qpValues = QP

    command_list = []
    for reportRoot in args.reportRoots:
        for qp in qpValues:
            for seqs in datasets.values():
                for seqName in seqs.keys():
                    reportPath = os.path.join(reportRoot, 'report', f"qp={qp}", f"{seqName}.csv")
                    
                    if os.path.isfile(reportPath):
                        command_list.append(
                            uploadReport(
                                srcPath = reportPath, 
                                settingName = os.path.basename(os.path.dirname(reportRoot)), 
                                qp = qp, 
                                seqName = seqName,
                        ))
                    else:
                        warnings.warn(f"{reportPath} doesn't exist, please check your setting!!")
                    
    for command in command_list:
        print(f"{command}")
        run_command(command)


if __name__ == "__main__":
    main(sys.argv[1:])
