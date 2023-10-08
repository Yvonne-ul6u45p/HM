#!/bin/bash

python generateSeqCfg.py --datasetRoot ~/Datasets/ --saveRoot ../randomaccess_main_full/
python hm.py --codingCfg ../HM/cfg/encoder_randomaccess_main.cfg --cfgRoot ../randomaccess_main_full/
python toPng.py --cfgRoot ../randomaccess_main_full/ --export ../randomaccess_main_full/
python3 checkframe.py --cfgRoot ../randomaccess_main_full
python compute_metrics.py --datasetRoot ~/Datasets/ --savePath ../randomaccess_main_full --recRoot ../randomaccess_main_full