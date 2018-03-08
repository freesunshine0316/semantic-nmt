#!/bin/bash
#SBATCH -J gs2s_13_nocov_bch50_v2 -C K80 --partition=gpu --gres=gpu:1 --time=5-00:00:00 
#SBATCH --output=train.out_13_nocov_bch50_v2 --error=train.err_13_nocov_bch50_v2
#SBATCH --mem=20GB
#SBATCH -c 5

python G2S_trainer.py --config_path config.json

