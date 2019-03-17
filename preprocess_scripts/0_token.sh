#!/bin/bash
#SBATCH --time=10:00:00 --output=out.txt --error=err.txt
#SBATCH --mem=20GB
#SBATCH -c 20

/home/lsong10/ws/exp.nmt/mosesdecoder/scripts/tokenizer/tokenizer_PTB.perl -l en -threads 2 < $1\.en > $1\.tok.en
/home/lsong10/ws/exp.nmt/mosesdecoder/scripts/tokenizer/tokenizer_PTB.perl -l de -threads 2 < $1\.de > $1\.tok.de 

