#!/bin/bash

python3 generateSeqCfg.py --datasetRoot ~/Datasets/ --saveRoot ../randomaccess_main_full/
python3 hm.py --codingCfg ../HM/cfg/encoder_randomaccess_main.cfg --cfgRoot ../randomaccess_main_full/
python3 toPng.py --cfgRoot ../randomaccess_main_full/ --export ../randomaccess_main_full/
python3 checkframe.py --cfgRoot ../randomaccess_main_full
python3 datasettoPNG.py --dataRoot ~/Datasets/
python compute_metrics.py --datasetRoot ~/Datasets/ --savePath ../randomaccess_main_full --recRoot ../randomaccess_main_full