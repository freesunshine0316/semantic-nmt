#!/bin/bash
#SBATCH -J linamr_large --partition=gpu --gres=gpu:2 -C K80 --time=5-00:00:00 --output=train.out --error=train.err
#SBATCH --mem=90GB
#SBATCH -c 5

python src/G2S_trainer.py --config_path logs/G2S.base.config.json

