#!/bin/bash
#SBATCH -J srl_large_2 --partition=gpu --gres=gpu:2 -C K80 --time=5-00:00:00 --output=train.out_2 --error=train.err_2
#SBATCH --mem=100GB
#SBATCH -c 5

python src/G2S_trainer.py --config_path logs/G2S.base_2.config.json

