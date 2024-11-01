# GEIC: Universal and Multilingual Named Entity Recognition with Large Language Models
This repository is supplement material for the paper: GEIC: Universal and Multilingual Named Entity Recognition with Large Language Models  
<!-- 📖: [![paper](https://img.shields.io/badge/arXiv-Paper-blue.svg)](https://arxiv.org/abs/2409.11022) &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; -->

## 💓Update!
* AnythingNER is disclosed now! Please download it from Huggingface for train and evaluation!

* We add more GEIC format existing datasets and also the format for fine-tuning and inferrence based on SWIFT! You can test CascadeNER easier!

* We provide a demo.py now. You can test your own sentence in a very simple way!

* We discover a problem that as SWIFT has been updated and some parameters has been changed, so please use the old version (according to requirements.txt)

## 📚 Features
* This repository includes CascadeNER and AnythingNER, our NER framework and our dataset

* CascadeNER is the first universal and multilingual NER framework with SLMs, which supports both few-shot and zero-shot scenarios and achieves SOTA performance on low-resource and fine-grained datasets

* AnythingNER is the first multilingual and fine-grained datasets designed for NER with LLMs, especially GEIC, with a novel dynamic categorization system


## 📈 Quantitive Result:

<p align="center">
  <img src="figure/english.png" width="90%"/>
</p>
<p align="center">
  <img src="figure/multilingual.png" width="90%"/>
</p>

## 📌 Prerequisites

1. `conda create -n cascadener python=3.10`
2. `pip install -r requirements.txt`
3. You may also use a standard environment for [SWIFT](https://github.com/modelscope/ms-swift).
4. Download the fine-tuned [extractor](https://huggingface.co/CascadeNER/models_for_CascadeNER/tree/main) and [classifier](https://huggingface.co/CascadeNER/models_for_CascadeNER/tree/main), and place them into the corresponding paths. Both models are fine-tuned based on QWEN2-1.5B.
5. You may also download [AnythingNER](https://huggingface.co/datasets/CascadeNER/AnythingNER/tree/main) and [other GEIC format dataset](https://huggingface.co/datasets/CascadeNER/AnythingNER/tree/main) to train your own model.

## 🌟 Usage
* Train: please use [SWIFT](https://github.com/modelscope/ms-swift) for model training. We strongly recommend Qwen2 and Gemma for your base models. You may use follow the examples in any `train.json` from GEIC format dataset in huggingface to get the format of train sets. We now provide a example in `./AnythingNER/example.json`

* First, prepare your own dataset in GEIC format for infer and use `./AnythingNER/transformation/stage1_trans.py` to get input file for inferrence. You may also use the datasets we provided in GEIC format.

* Second, change your own paths in `infer.py` and `extract.sh`, including two model paths, dataset path, category path, and output path.

* Last, run `infer.py` and your will receive the results.

* Eval: If you want to evaluate our framework, please use `evaluate.py`. You can use the dataset in GEIC format other the results to evaluate.

## ❤️ Acknowledgement
* We thank QwenLM for opening source their [Qwen](https://github.com/QwenLM/Qwen) model for us
* We thank ModelScope for opening source their [SWIFT](https://github.com/modelscope/ms-swift) framework for us
* We thank teams of CoNLL2003, CrossNER, FewNERD, MultiCoNER and PAN-X for opening source their datasets
