# UGC handbook source

The experiment uses the University Grants Commission of Sri Lanka, *University Admissions Handbook 2025/2026* (210 pages). Official public source:

https://www.ugc.ac.lk/downloads/admissions/Handbook_2025_26/student_handbook_english.pdf

The PDF itself is excluded from this public repository because redistribution permissions are unclear. To recreate the local evaluation excerpt, download it to this folder as `UGC_University_Admissions_Handbook_2025-2026.pdf`, then from the Lab 5 project directory run:

```powershell
python scripts\prepare_handbook_sample.py
```

This generates the first 50 physical pages under `data/evaluation_corpus/handbook_sample/`. The 8-question dataset and recorded results refer to that 50-page excerpt. The complete 210-page book was not evaluated because indexing exceeded the practical CPU runtime.

SHA-256 of the source PDF used for the recorded experiment: `8B9CC7B24ED2A10ED19C22A1E12D0A9336C0DB15F1623EA2ACA35334E005C93D`.
