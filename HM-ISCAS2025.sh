#!/bin/bash

python3 generateSeqCfg.py --datasetRoot ~/Datasets/TestVideo/raw_video_1080/ --saveRoot ../results/HM_randomaccess_main_YUV420_I32Full/ --intra_period 32

python3 HM-v2.py --codingCfg ../cfg/encoder_randomaccess_main.cfg --cfgRoot ../results/HM_randomaccess_main_YUV420_I32Full/ --taskMax 6

python3 computeMetrics.py --datasetRoot ~/Datasets/TestVideo/raw_video_1080/ --recRoot ../results/HM_randomaccess_main_YUV420_I32Full/ --saveRoot ../results/HM_randomaccess_main_YUV420_I32Full/

python3 uploadReport.py --reportRoots ../results/HM_randomaccess_main_YUV420_I32Full/
