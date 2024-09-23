# GEIC: Universal and Multilingual Named Entity Recognition with Large Language Models
This repository is supplement material for the paper: GEIC: Universal and Multilingual Named Entity Recognition with Large Language Models
This repository includes CascadeNER and AnythingNER, our NER framework and our dataset
CascadeNER is the first universal and multilingual NER framework with SLMs, which supports both few-shot and zero-shot scenarios and achieves SOTA performance on low-resource and fine-grained datasets
AnythingNER is the first multilingual and fine-grained datasets designed for NER with LLMs, especially GEIC, with a novel dynamic categorization system
📖: [![paper](https://img.shields.io/badge/arXiv-Paper-<COLOR>.svg)]() &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;

## 📚 Features
* 

* 

* 
<!-- <p align="center">
  <img src="Figure/example.png" width="75%"/>
</p>
<p align="center">
  <img src="Figure/artitecture_sum.png" width="75%"/>
</p> -->

## 📈 Quantitive Result:

<p align="center">
  <img src="figure/english.png" width="90%"/>
</p>
<p align="center">
  <img src="figure/multilingual.png" width="90%"/>
</p>
## 📌 Prerequesties
1. `conda create -n cascadener python=3.10`
2. `pip install -r requirements.txt`
3. you may also use a standard environment for [SWIFT](https://github.com/modelscope/ms-swift)
4. download finetuned [extractor] and [classifier](https://huggingface.co/CascadeNER/models_for_CascadeNER/tree/main), and put them into corresponding path. Both model are fine-tuned based on QWEN2-1.5B.

## 🌟 Usage
<!-- * First, download finetuned [InternVL-4B](https://huggingface.co/BIGBench/InternVL-4B-bench) and [qwen1-5b](https://huggingface.co/VersusDebias/VersusDebias/tree/main), and put them into `./model`

* Second, change `model` in `gam.py` to your generator model. If your model is not on the list, you can change `model` to your model name mannually (make sure your workflow `{model}.json` is under `./workflow`). Change `server_address` in `gam.py` to the address of your own Comfyui and run Comfyui independently. Change `epoch` (default 5) to a quarter of the number of the original array (default 20) in `./tools/orgin_array.py`. Then, you may run `gam.py` to use GAM. The results will be stored in `./GAM_result`.

* Third, change `model` in `result_select.py` to the generator model used in GAM and run `result_select.py` to select the best result of each prompt from GAM. The result will be stored in `./GAM_result`.

* Last, change `original_prompt_path` in `dgm.py` to the prompts (in .txt file) you want to debias. Change `generator_model` to your generator model (notice that this generator model can be different to the one in GAM part). Change `ground_truth` to your ground truth path. Then you may run `dgm.py` to generate the debiased prompts of your own prompts and the images based on these debiased prompts. The result will be stored in `./prompt` and `./Debiased_Image`.

* Eval: If you want to evaluate our framework in few-shot or zero-shot scenarios, follow the instruction in `dgm.py`, `eval_align.py` and `eval_result.py` to modify them. Then, run these three files in order of `dgm.py`, `eval_align.py` and `eval_result.py`. The result will be stored in `./align` and `./evaluate` -->

## ❤️ Acknowledgement
* We thank QwenLM for opening source their [Qwen](https://github.com/QwenLM/Qwen) model for us
* We thank ModelScope for opening source their [SWIFT](https://github.com/modelscope/ms-swift) framework for us
* We thank teams of CoNLL2003, CrossNER, FewNERD, MultiCoNER and PAN-X for opening source their datasets
