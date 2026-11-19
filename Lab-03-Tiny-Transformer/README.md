# Lab 03: Tiny Transformer

## Objective

Build and train a small Transformer language model on TinyStories to learn character-level next-token prediction, measure validation performance, and generate story text.

## Dataset

The notebook streams 20,000 shuffled records from the [roneneldan/TinyStories dataset on Hugging Face](https://huggingface.co/datasets/roneneldan/TinyStories). It splits these by story into 18,000 training stories and 2,000 validation stories and does not commit the full corpus. TinyStories is provided under [CDLA-Sharing-1.0](https://cdla.dev/sharing-1-0/).

## Implementation

The practical is in [tiny_transformer_from_scratch.ipynb](notebooks/tiny_transformer_from_scratch.ipynb). It covers data exploration, character-level tokenization, shifted input and target sequences, causal multi-head self-attention, embeddings, feed-forward layers, residual connections, LayerNorm, cross-entropy, AdamW, validation monitoring, perplexity, sampling, settings comparison, and checkpoint saving/reloading.

The main configuration uses a 128-character context, 128-dimensional embeddings, 4 heads, 4 Transformer layers, batch size 32, and 5,000 optimizer updates. The smaller comparison uses 2 layers and 4 heads for 1,500 updates.

## Results

| Configuration | Parameters | Validation loss | Character perplexity |
|---|---:|---:|---:|
| 4 layers, 4 heads, 5,000 steps | 821,888 | 1.119 | 3.06 |
| 2 layers, 4 heads, 1,500 steps | 245,280 | 1.727 | 5.62 |

The 5,000-step model's loss decreased through training. Its generated samples contain recognizable story elements and simple event sequences, but still have spelling and grammar errors and sometimes lose coherence. This is a small character-level model trained from scratch, so the outputs are promising for the practical but are not consistently polished stories. See [generated samples](results/generated_stories.md).

## Results and Evidence

- [Training and validation loss curve](results/training_loss.svg)
- [Loss history](results/training_loss.csv)
- [Combined training history](results/all_training_loss.csv)
- [Settings comparison](results/settings_comparison.csv)
- [Generated story samples](results/generated_stories.md)
- [Model configuration](results/tiny_transformer_config.json)
- [Saved model checkpoint](results/tiny_transformer.pt)

The Colab run artifacts were produced with a T4 GPU. The checkpoint stores the model state, configuration, character vocabulary, and random seed.

## Learning Outcomes

This practical shows how a text stream becomes next-character training examples and how masked self-attention, position information, and feed-forward layers combine to predict the next character. It also demonstrates validation monitoring, perplexity, model-size comparisons, prompt-based generation, and saving a model for reuse.

## Running the Notebook

Open the notebook in Google Colab, select **Runtime > Change runtime type > T4 GPU**, then choose **Runtime > Restart session** and **Runtime > Run all**. It streams 20,000 records and runs the main model for 5,000 updates plus a smaller comparison run.