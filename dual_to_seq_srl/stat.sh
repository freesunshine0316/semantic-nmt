#!/bin/bash
#SBATCH --time=20:00:00 --output=stat.out --error=stat.err
#SBATCH --mem=30GB
#SBATCH -c 2

python data_stat.py

