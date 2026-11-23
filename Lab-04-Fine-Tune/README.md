# Lab 04: Fine-Tuning with LoRA / QLoRA

## Objective

Fine-tune a small instruction-tuned causal language model for computer-shop support using PEFT LoRA, TRL supervised fine-tuning, and 4-bit NF4 QLoRA on a compatible GPU. Compare the original and fine-tuned models on identical held-out and unseen questions.

## Implementation

Run [fine_tune_computer_shop_lora.ipynb](notebooks/fine_tune_computer_shop_lora.ipynb) in Google Colab with a GPU runtime. It installs Transformers, Datasets, PEFT, TRL, Accelerate, bitsandbytes, and Gradio; records GPU model and memory; selects Qwen2.5-0.5B-Instruct or the smaller SmolLM2-360M-Instruct based on available memory; and configures 4-bit NF4 QLoRA with PEFT and TRL SFTTrainer.

The included run used a **Tesla T4 (14.56 GiB, compute capability 7.5)**, **Qwen/Qwen2.5-0.5B-Instruct**, and **4-bit NF4 QLoRA**. A GPU helps by accelerating the parallel matrix operations and providing high-bandwidth memory used in model training.

The notebook creates 36 computer-shop Q&A pairs, with 28 training examples and 8 held-out examples. It trains on prompt/completion columns with completion-only loss, evaluates the fine-tuned model, compares base and fine-tuned answers on the same 8 held-out questions and 3 additional unseen questions, saves/reloads the adapter, and launches a Gradio chatbot using the fine-tuned model.

## Results

The supplied run record reports completion-only evaluation loss **2.9040**, mean token accuracy **0.3750**, and perplexity **18.25** (calculated as exp(eval_loss)). The training log from the Colab run shows training loss declining from 2.476 to 2.352 and validation loss from 3.021 to 2.904 over three epochs. These are language-model token prediction metrics; they do not establish response correctness.

The comparison files show **mixed answer quality**. The fine-tuned model gives a more appropriate answer to the deleted-file recovery question, but also produces incorrect or unsafe advice on some held-out questions (including cleaning desktop dust and shutting down nightly), and its unseen no-picture troubleshooting answer is not relevant. The current results therefore document a completed fine-tuning exercise, not a reliable support assistant. Review each answer before using it as guidance.

## Observations

- The loss values improved over three epochs, but this only indicates better next-token prediction on the training/evaluation format; it does not guarantee correct support answers.
- Comparing the base and adapted models on the same held-out and unseen questions exposed mixed behavior: one answer improved, while other answers were irrelevant, incorrect, or unsafe.
- The 28 training examples and eight held-out examples are too small to support broad conclusions about computer-support performance.
- Quantized adapter training made the experiment possible on the available GPU, but the base-model weights are still required to load the adapter and reproduce inference.

## Results and saved adapter

- [Run record](results/fine_tuning_run_record.json)
- [Held-out comparison (8 questions)](results/heldout_comparison.csv)
- [Unseen-question comparison (3 questions)](results/unseen_prompt_comparison.json)
- [Saved PEFT adapter and tokenizer](results/adapter/)

The model base weights are not included; load the named base model before loading the adapter. The archive supplied by Colab did not include a full per-step training history, so this README records only the epoch values shown in the run output.

## Chatbot

After the evaluation/export cell completes, run the final **Ask the fine-tuned model in a chat window** cell. It starts a Gradio chatbot with the fine-tuned model and prints a temporary public share link. Anyone with the link can access it while the Colab runtime is active. The chatbot can produce incorrect answers; it is a demonstration and should not be used to make repair decisions.

## Run steps

1. Open the notebook in Colab, select **Runtime > Change runtime type > T4 GPU**, then use **Runtime > Disconnect and delete runtime** before a clean run to clear stale CPU-only bitsandbytes libraries.
2. Reconnect to the T4 GPU and run every cell in order. Check that the GPU and NF4 CUDA preflight are detected before model download.
3. Review the held-out/unseen comparisons and run the chatbot cell. The current run artifacts from the supplied Colab ZIP are stored under results/. If you rerun Colab, download the new results ZIP and replace these checked-in artifacts after reviewing them.

The small hand-written dataset is for demonstrating the fine-tuning workflow and is too small to establish general support quality.

## Learning Outcomes

- Configured parameter-efficient fine-tuning with LoRA/QLoRA, 4-bit NF4 quantization, and supervised fine-tuning tools on a GPU runtime.
- Separated training examples from held-out questions and compared the base and adapted models on matching held-out and unseen prompts.
- Interpreted loss, token accuracy, and perplexity as language-model metrics rather than direct measures of answer correctness.
- Learned to inspect individual responses for relevance and safety and to preserve the base-model name, adapter configuration, and run artifacts needed for reuse.
