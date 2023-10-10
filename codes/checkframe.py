import os, argparse
from tqdm import tqdm
from Setting import DATASET, QP

parser = argparse.ArgumentParser(description="Select which dataset to decode to png")
parser.add_argument('--cfgRoot', type=str, required=True)
args = parser.parse_args()

datasets = DATASET

qpValues = QP

check=True
Wrong_seq=[]

for qp in tqdm(qpValues):
	for datasetName, seqs in datasets.items():
		root = os.path.join(args.cfgRoot, datasetName, f'qp={qp}')
		for seqName, seq in seqs.items():
			path = os.path.join(root, seqName, 'rgb')
			# print(seqName, len(os.listdir(path)), seq)
			
			if len(os.listdir(path)) != seq['frameNum']:
				check=False
				Wrong_seq.append(f"{path}")

if check:
    print("Correct")
else:
    print("Wrong Seq:")
    for path in Wrong_seq:
        print(path)
