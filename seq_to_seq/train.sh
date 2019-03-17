#!/bin/bash
#SBATCH -J seq_large --partition=gpu --gres=gpu:1 -C K80 --time=5-00:00:00 --output=train.out_dev13_a800l50_lr5e4_l21e8 --error=train.err_dev13_a800l50_lr5e4_l21e8
#SBATCH --mem=45GB
#SBATCH -c 5

python NP2P_trainer.py --config_path logs/NP2P.dev13_a800l50_lr5e4_l21e8.config.json

