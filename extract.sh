#!/bin/bash

CUDA_VISIBLE_DEVICES=1 \
swift infer \
    --ckpt_dir ./model/stage1/zeroshot/1b-sft \
    --custom_val_dataset_path your_path \
    --show_dataset_sample 100
