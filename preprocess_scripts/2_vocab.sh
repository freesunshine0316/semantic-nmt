#!/bin/bash
#SBATCH --time=2:00:00 --output=out.txt --error=err.txt
#SBATCH --mem=2GB
#SBATCH -c 2

echo -e "<unk>\n<s>\n</s>" > $2
python get_vocab.py < $1 | cut -f1 -d ' ' >> $2

