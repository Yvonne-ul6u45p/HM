import os
import sys
import argparse
from tqdm import tqdm
from subprocess import Popen, PIPE
from Setting import DATASET, QP
from concurrent.futures import ProcessPoolExecutor, as_completed


def runHMcodec(codingCfg: str, seqCfg: str, outName: str) -> None:
    command = f"./TAppEncoderStatic -c {codingCfg} -c {seqCfg} > {outName}"
    # print("Run command: ", command)
    return command


def run_command(command: str):
    process = Popen(command, universal_newlines=True, shell=True, stdout=PIPE, stderr=PIPE)
    process.wait()

    return command


def main(argv):

    parser = argparse.ArgumentParser(description="Set the root of dataset and for save")
    parser.add_argument('--codingCfg', type=str, nargs='+', required=True, help="Path of cfg/encoder_lowdelay_main_rext.cfg")
    parser.add_argument('--cfgRoot', type=str, nargs='+', required=True, help="Path for save the cfg files and results")
    parser.add_argument('--taskMax', type=int, required=True, help="MAX number of sequences being compressed at the same time, recommended to be less than the number of CPU cores.")
    args = parser.parse_args(argv)

    datasets = DATASET
    qpValues = QP

    qpProcesses = []
    for (codingCfg, cfgRoot) in zip(args.codingCfg, args.cfgRoot):
        for qp in qpValues:
            for datasetName, seqs in datasets.items():
                for seqName, seq in seqs.items():
                    cfgPath = os.path.join(cfgRoot, datasetName, f"qp={qp}", seqName)
                    if datasetName == "CLIC2022_YUV420":
                        name = seqName
                    else:
                        name = seq['vi_name']

                    cfgName = os.path.join(cfgPath, name + '.cfg')
                    outName = os.path.join(cfgPath, name + '.out')
                    qpProcesses.append(runHMcodec(codingCfg, cfgName, outName))
    # print(f"{qpProcesses=}")

    with tqdm(total=len(qpProcesses), unit='seq', desc='seqs') as pbar:
        with ProcessPoolExecutor(max_workers=args.taskMax) as executor:
            futures = {executor.submit(run_command, single_command): single_command for single_command in qpProcesses}
            for future in as_completed(futures):
                command = futures[future]
                try:
                    result = future.result()
                    tqdm.write(f'Command "{result}" completed')
                except Exception as e:
                    tqdm.write(f'Command "{command}" generated an exception: {e}')
                pbar.update(1)


if __name__ == "__main__":
    main(sys.argv[1:])
