#!/bin/bash
#SBATCH --partition=gpu --gres=gpu:1 --time=10:00:00 --output=decode.out --error=decode.err
#SBATCH --mem=10GB
#SBATCH -c 2

start=`date +%s`
python G2S_beam_decoder.py --model_prefix logs/G2S.$1 \
        --in_path data/little_prince.tok_$2\.json \
        --out_path logs/little_prince_$2\.$1\.tok \
        --mode beam

end=`date +%s`
runtime=$((end-start))
echo $runtime
