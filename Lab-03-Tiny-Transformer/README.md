# Lab 03: Tiny Transformer Story Generator

## Objective

Build a small character-level Transformer from scratch, train it on the Hugging Face TinyStories dataset, evaluate next-character prediction, generate stories, compare model settings, and save/reload a checkpoint. This practical implements the requested workflow; the generated prose remains a limitation of this small model.

## Dataset and preprocessing

The notebook streams and shuffles 20,000 records from [roneneldan/TinyStories](https://huggingface.co/datasets/roneneldan/TinyStories), explores sample stories and text lengths, then splits records by story into 18,000 training and 2,000 validation examples. It uses a character-level vocabulary and a 128-character context. The full dataset is not committed. TinyStories is provided under [CDLA-Sharing-1.0](https://cdla.dev/sharing-1-0/).

## Implementation

The notebook builds shifted input/target sequences and a causal Transformer with token and positional embeddings, masked multi-head self-attention, feed-forward layers, residual connections, and layer normalization. It trains with cross-entropy and AdamW, records training/validation loss, calculates validation character perplexity, compares a smaller architecture, generates prompt completions, and saves/reloads model weights and vocabulary.

The main configuration is 4 layers, 4 attention heads, 128-dimensional embeddings, batch size 32, context length 128, and 5,000 optimizer steps. The comparison uses 2 layers, 4 heads, 96-dimensional embeddings, and 1,500 steps.

## Results

The supplied Colab run record reports 20,000 sampled stories, 5,000 main-model steps, final full-validation loss **1.1189**, and character perplexity **3.06**. Loss decreases over training (the last logged validation loss at step 5,000 is 1.1349); the full-validation estimate is measured separately over more batches. The smaller model reports validation loss **1.7268** and character perplexity **5.62**, so the main configuration performs better on this validation split.

The saved checkpoint reloads successfully, but the generated samples are **not consistently coherent**. The main sample contains many malformed words and grammar errors, and the smaller model sample is largely unreadable. The reloaded-checkpoint sample has a recognizable opening but still has significant language errors. Therefore, these results complete the requested experiment and provide evidence, but they do not establish that the model reliably writes sensible stories. See [generated_stories.md](results/generated_stories.md), [settings_comparison.csv](results/settings_comparison.csv), and the loss plots in this folder.

## Observations

- Training and validation loss decreased, and the larger configuration scored better on the recorded validation split than the smaller configuration.
- The lower loss and character perplexity did not translate into consistently readable stories. Generated samples still contained malformed words and grammar errors.
- The validation set and generated samples measure different aspects of performance; a prediction metric alone is not enough to judge whether a story is useful.
- Building and running the model required careful handling of sequence shifts, causal masking, context length, and checkpoint vocabulary so that saved weights could be loaded with the matching character mapping.

## Learning Outcomes

- Implemented a character-level causal Transformer with token and positional embeddings, masked self-attention, feed-forward layers, residual connections, and layer normalization.
- Prepared a story-level train/validation split and used cross-entropy loss and character perplexity to compare model configurations.
- Saved and reloaded a checkpoint together with the vocabulary and inspected generated outputs as a separate qualitative evaluation.
- Learned that successful training and a lower validation score do not establish coherent generation; output quality must be reviewed directly against the intended task.

## Story chatbot

After running all notebook cells, run the final **Generate stories from a chat prompt** cell. It opens a Gradio interface where a user enters a story opening and the trained Transformer continues it. The cell prints a temporary share link; anyone who has the link can access the chatbot while the Colab runtime is running. Because this is a small character-level model trained from scratch, the chatbot may produce incoherent text and should be treated as an experiment rather than a reliable story writer.

## Run in Google Colab

Open [tiny_transformer_from_scratch.ipynb](notebooks/tiny_transformer_from_scratch.ipynb), select **Runtime > Change runtime type > T4 GPU**, and run all cells from the top. The notebook installs Gradio for the optional chat interface. The results directory contains the run's loss history, settings comparison, generated samples, plot, configuration, and reloadable checkpoint.
