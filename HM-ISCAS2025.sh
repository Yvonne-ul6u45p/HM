#!/bin/bash

# python3 generateSeqCfg.py --datasetRoot ~/Datasets/TestVideo/raw_video_1080/ --saveRoot ../results/HM_randomaccess_main_YUV420_I32Full/ --intra_period 32
# python3 generateSeqCfg.py --datasetRoot ~/Datasets/TestVideo/raw_video_1080/ --saveRoot ../results/HM_lowdelay_main_YUV420_I32Full/ --intra_period 32
# python3 generateSeqCfg.py --datasetRoot ~/Datasets/TestVideo/raw_video_1080/ --saveRoot ../results/HM_lowdelay_main_YUV420_InfFull/ --intra_period -1

# python3 HM-v2.py --codingCfg ../cfg/encoder_randomaccess_main.cfg ../cfg/encoder_lowdelay_main.cfg ../cfg/encoder_lowdelay_main.cfg --cfgRoot ../results/HM_randomaccess_main_YUV420_I32Full/ ../results/HM_lowdelay_main_YUV420_I32Full/ ../results/HM_lowdelay_main_YUV420_InfFull/ --taskMax 6

# python3 computeMetrics.py --datasetRoot ~/Datasets/TestVideo/raw_video_1080/ --recRoot ../results/HM_randomaccess_main_YUV420_I32Full/ --saveRoot ../results/HM_randomaccess_main_YUV420_I32Full/
# python3 computeMetrics.py --datasetRoot ~/Datasets/TestVideo/raw_video_1080/ --recRoot ../results/HM_lowdelay_main_YUV420_I32Full/ --saveRoot ../results/HM_lowdelay_main_YUV420_I32Full/
# python3 computeMetrics.py --datasetRoot ~/Datasets/TestVideo/raw_video_1080/ --recRoot ../results/HM_lowdelay_main_YUV420_InfFull/ --saveRoot ../results/HM_lowdelay_main_YUV420_InfFull/

python3 uploadReport.py --reportRoots ../results/HM_randomaccess_main_YUV420_I32Full/ ../results/HM_lowdelay_main_YUV420_I32Full/ ../results/HM_lowdelay_main_YUV420_InfFull/
