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

The notebook evaluates loss and perplexity, compares original and fine-tuned answers to the same held-out questions, then asks both models additional questions absent from the dataset. It saves the adapter, tokenizer, and a JSON run record in the runtime. In Colab, download those artifacts before ending the session; the runtime's temporary files are not automatically committed to this repository.

## Results and evidence

**Run status:** Notebook prepared; it has not yet been run in a Colab runtime. No GPU model, VRAM, training metrics, perplexity, or generated answers are reported here until the notebook is executed.

After running, add the Colab GPU name and VRAM, selected model, training/evaluation loss, perplexity, and a few representative before/after answers here. Put screenshots in `screenshots/` and explain each one here.

## Observations and learning outcomes

The notebook is designed to demonstrate how LoRA reduces the number of trainable parameters, how 4-bit quantization can lower GPU memory use, and how held-out questions help compare the base and adapted model. The small dataset is a workflow demonstration; it is not enough to establish reliable real-world support quality.

## Run instructions

1. Open the notebook in Google Colab.
2. Select Runtime > Change runtime type > T4 GPU (or another available GPU), then run cells in order.
3. Keep the printed hardware details, metrics, comparison table, and sample answers for this README.
4. Download the saved adapter/run record before the Colab session ends. Do not commit a full base model checkpoint.

## References

- [TRL SFTTrainer documentation](https://huggingface.co/docs/trl/sft_trainer)
- [TRL PEFT and QLoRA integration](https://huggingface.co/docs/trl/peft_integration)
- [bitsandbytes installation and hardware support](https://huggingface.co/docs/bitsandbytes/installation)
- [Qwen2.5-0.5B-Instruct model page](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
- [SmolLM2-360M-Instruct model page](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct)
