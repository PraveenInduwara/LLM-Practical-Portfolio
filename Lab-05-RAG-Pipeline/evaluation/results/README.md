# Evaluation results

The result folders contain two separately measured runs:

- `../metrics.json`, `../question_results.csv`, `../manual_review.json`: 10-question comparison on the six-page Lab 5 sheet.
- `handbook_sample/`: 8-question comparison on the first 50 physical pages of the official 210-page Sri Lankan UGC admissions handbook.

For the sample, parent-child scored 0.938 Recall@5, 1.000 MRR, 0.663 required-fact lexical coverage, and 7/8 fully correct answers (0.875 strict accuracy). Fixed-size scored 5/8 fully correct; section-aware scored 4/8. Inline `[S#]` markers appeared in 3/8 fixed, 4/8 section-aware, and 4/8 parent-child answers. The app also shows retrieved sources in its evidence panel.

The handbook sample is not a full 210-page evaluation. Full indexing was stopped due to CPU runtime and produced no results. Required-fact coverage is a lexical proxy, not correctness. See `group-activity/technical_report.md` for run settings, limitations, and interpretation.
