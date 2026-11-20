# Lab 04 run artifacts

These files came from the supplied Colab run archive. See the parent README for evaluation details and limitations.

- fine_tuning_run_record.json: GPU, model, training/evaluation counts and metrics.
- heldout_comparison.csv: base-model, fine-tuned-model, and reference answers for eight held-out questions.
- unseen_prompt_comparison.json: paired answers for three questions not used in the 36-pair dataset.
- adapter/: PEFT adapter weights/configuration and tokenizer files needed with the named base model.

The adapter was saved after a three-epoch T4 run. The answer comparisons show mixed quality, including some inaccurate or unsafe outputs; these files are evidence for the coursework, not a validated support system.