#!/bin/bash
#SBATCH --partition=gpu --gres=gpu:1 --time=10:00:00 --output=decode.out --error=decode.err
#SBATCH --mem=10GB
#SBATCH -c 2

start=`date +%s`
python NP2P_beam_decoder.py --model_prefix logs/NP2P.$1 \
        --in_path data/newstest$2\.tok_allbpe.json \
        --out_path logs/newstest$2\.$1\.tok \
        --mode beam

end=`date +%s`
runtime=$((end-start))
echo $runtime
