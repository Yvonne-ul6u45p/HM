#!/bin/bash

python generateSeqCfg.py --datasetRoot /mnt/sdb/Datasets/TestVideo/raw_video_1080 --saveRoot ../randomaccess_main_full/
python hm.py --codingCfg ../HM/cfg/encoder_randomaccess_main.cfg --cfgRoot ../randomaccess_main_full/
python toPng.py --cfgRoot ../randomaccess_main_full/ --export ../randomaccess_main_full/