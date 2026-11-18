# Lab 03: Tiny Transformer

## Objective

Build and train a small Transformer language model on TinyStories to learn character-level next-token prediction, measure validation performance, and generate story text.

## Dataset

The notebook loads the [roneneldan/TinyStories dataset on Hugging Face](https://huggingface.co/datasets/roneneldan/TinyStories) with streaming enabled and uses a 300-story subset. It does not download or commit the full dataset. The 300 sampled stories had a median length of 802.5 characters (range: 387–1,225). The subset is split by story into 240 training stories and 60 validation stories. TinyStories is provided under [CDLA-Sharing-1.0](https://cdla.dev/sharing-1-0/); the executed notebook retains dataset attribution and displays only a few sample stories.

## Implementation

The complete, executed practical is in [tiny_transformer_from_scratch.ipynb](notebooks/tiny_transformer_from_scratch.ipynb). It includes:

1. Loading and inspecting several stories, their text lengths, and structure.
2. Character-level tokenization and shifted input/target sequences for next-character prediction.
3. A causal Transformer with token and positional embeddings, masked multi-head self-attention, feed-forward layers, residual connections, LayerNorm, and dropout.
4. Parameter initialization, cross-entropy loss, AdamW optimization, backpropagation, and gradient clipping.
5. Training and validation loss logging, a loss curve, validation loss and perplexity evaluation.
6. Prompt-based story generation, a model-setting comparison, and checkpoint saving/reloading.

The baseline uses a 64-character context, 64-dimensional embeddings, 4 attention heads, 2 Transformer layers, batch size 32, and 8 epochs of 25 updates. Character vocabulary size was 71. The settings comparison keeps training duration fixed at 8 epochs and changes to 2 heads and 1 layer.

## Results

| Configuration | Parameters | Validation loss | Perplexity |
|---|---:|---:|---:|
| 2 layers, 4 heads, 8 epochs | 108,736 | 2.391 | 10.93 |
| 1 layer, 2 heads, 8 epochs | 58,752 | 2.382 | 10.83 |

The smaller configuration used about half as many parameters and had a similar validation loss on this subset. Perplexity is calculated as the exponential of cross-entropy loss. Generated text is still rough and only partly readable after this short training run; these scores and samples demonstrate the workflow, not a production-quality story model.

## Results and Evidence

- [Training and validation loss curve](results/training_loss.svg)
- [Loss history by epoch](results/training_loss.csv)
- [Settings comparison](results/settings_comparison.csv)
- [Generated story samples](results/generated_stories.md)
- [Saved model checkpoint](results/tiny_transformer.pt)
- [Model configuration](results/tiny_transformer_config.json)

The checkpoint includes model parameters, architecture configuration, and the character vocabulary. The notebook reloads it and generates another sample to demonstrate future use.

## Performance Mechanisms

The implementation uses a causal mask to prevent future-token leakage, residual connections and pre-LayerNorm for stable gradient flow, dropout and AdamW weight decay for regularization, gradient clipping to limit unstable updates, and mini-batches with AdamW for efficient optimization. Held-out validation loss and perplexity are monitored to compare generalization across configurations.

## Learning Outcomes

This practical shows how character streams become next-token training examples and how masked self-attention, position information, and feed-forward layers combine to predict the next character. It also demonstrates how to monitor validation loss, interpret perplexity, compare model capacity, generate from a prompt, and save a model for reuse.

## Running the Notebook

Install PyTorch, Hugging Face Datasets, NumPy, Pandas, and Matplotlib, then run the notebook cells in order. It streams 300 examples from Hugging Face by default; no full dataset download is needed.

