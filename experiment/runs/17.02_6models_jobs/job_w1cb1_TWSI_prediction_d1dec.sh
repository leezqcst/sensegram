#!/bin/bash

#BSUB -J "predict TWSI w1cb1"
#BSUB -eo /work/scratch/kurse/zu66ytyq/thesis/experiment/runs/experiment_17.02_6models_jobs/job_w1cb1_TWSI_prediction_d1dec_err.txt
#BSUB -oo /work/scratch/kurse/zu66ytyq/thesis/experiment/runs/experiment_17.02_6models_jobs/job_w1cb1_TWSI_prediction_d1dec_out.txt
#BSUB -n 16
#BSUB -M 8000
#BSUB -W 400
#BSUB -x
#BSUB -q kurs3

cd /work/scratch/kurse/zu66ytyq/thesis/experiment/
time python3 prediction.py context-eval/data/Dataset-TWSI-2.csv model/corpus_en.norm-sz100-w1-cb1-it1-min20.w2v.senses model/corpus_en.norm-sz100-w1-cb1-it1-min20.w2v.contexts eval/corpus_en.norm-sz100-w1-cb1-it1-min20_TWSI-2_predictions_d1dec.csv -lowercase diff_thr 0.109675991