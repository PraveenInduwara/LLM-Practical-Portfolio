# Lab 04: Fine-Tuning an Instruction Model

## Objective

Use Hugging Face Transformers and TRL to adapt a small instruction-tuned causal language model to computer-shop support questions. Train only LoRA adapter parameters, use 4-bit QLoRA when a CUDA GPU is available, compare the original and adapted model on the same unseen questions, and save the adapter for later use.

## Practical information

- **Domain:** Computer shop support
- **Environment:** Google Colab with a GPU runtime recommended
- **Libraries:** `transformers`, `datasets`, `peft`, `trl`, `accelerate`, and `bitsandbytes`
- **Notebook:** [fine_tune_computer_shop_lora.ipynb](notebooks/fine_tune_computer_shop_lora.ipynb)
- **Models:** Qwen/Qwen2.5-0.5B-Instruct when the detected CUDA GPU has at least 8 GiB VRAM; otherwise HuggingFaceTB/SmolLM2-360M-Instruct. It enables NF4 QLoRA only when CUDA compute capability is at least 6.0 (the bitsandbytes NF4 minimum); otherwise it uses standard LoRA, with CPU training clearly marked as slow. For mixed precision, it uses bfloat16 only on compute capability 8.0 or higher and float16 on older CUDA GPUs.

## Tasks and implementation

The notebook installs the required libraries, reports the CUDA GPU model and VRAM when available, and records whether it uses 4-bit NF4 QLoRA or standard LoRA. It creates 36 original domain question-and-answer examples, reserving eight examples for evaluation. It applies each model's chat template, configures LoRA, and fine-tunes with TRL's `SFTTrainer`.

The notebook evaluates loss and perplexity, compares original and fine-tuned answers on held-out and new questions, saves the answer comparisons, and packages the adapter, tokenizer, run record, and comparisons into a downloadable ZIP.

## Results and evidence

**Run status:** Completed in Google Colab.

| Measurement | Result |
| --- | --- |
| GPU | Tesla T4, 14.56 GiB VRAM |
| Base model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Fine-tuning method | LoRA with 4-bit NF4 QLoRA |
| Compute dtype | float16 |
| Dataset split | 28 training pairs; 8 held-out evaluation pairs |
| Trainable parameters | 4,399,104 of 498,431,872 (0.8826%) |
| Evaluation loss | 1.5966 |
| Evaluation perplexity | 4.9364 |
| Mean token accuracy | 0.6591 |
| Evaluation entropy | 1.6985 |

The Colab run compared the base and fine-tuned models on the same eight held-out questions and three additional questions absent from the dataset. The supplied ZIP contains the trained adapter, adapter configuration, tokenizer files, and run record. The notebook now also saves the comparison table to `heldout_comparison.csv` and the extra prompt answers to `unseen_prompt_comparison.json` inside the downloadable adapter bundle.

The dataset is small and hand-written for demonstrating the workflow; the metrics and examples are not evidence of production-level support quality.

## Observations and learning outcomes

The notebook is designed to demonstrate how LoRA reduces the number of trainable parameters, how 4-bit quantization can lower GPU memory use, and how held-out questions help compare the base and adapted model. The small dataset is a workflow demonstration; it is not enough to establish reliable real-world support quality.

## Run instructions

1. Open the notebook in Google Colab.
2. Select Runtime > Change runtime type > T4 GPU (or another available GPU), then run cells in order.
3. The final cell displays the metrics and answer comparisons, then downloads an adapter ZIP with the CSV and JSON comparison records.
4. Download the saved adapter/run record before the Colab session ends. Do not commit a full base model checkpoint.

## References

- [TRL SFTTrainer documentation](https://huggingface.co/docs/trl/sft_trainer)
- [TRL PEFT and QLoRA integration](https://huggingface.co/docs/trl/peft_integration)
- [bitsandbytes installation and hardware support](https://huggingface.co/docs/bitsandbytes/installation)
- [Qwen2.5-0.5B-Instruct model page](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
- [SmolLM2-360M-Instruct model page](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct)
