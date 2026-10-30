[Back to Articles](https://huggingface.co/blog)

# Inside the pipeline that placed 18th in a $77,000 Kaggle knee MRI competition

[Community Article](https://huggingface.co/blog/community)

Published
August 9, 2026

[Upvote \\
\\
-](https://huggingface.co/login?next=%2Fblog%2Fbishnoiyash%2Frsna-competetion)

[![Yash Bishnoi's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/94j9Xh140a-lDMRSLUJPj.png)](https://huggingface.co/bishnoiyash)

[Yash Bishnoi\\
bishnoiyash\\
\\
Follow](https://huggingface.co/bishnoiyash)

**kaggle url: [https://www.kaggle.com/code/yashbishnoi98/rsna-knee-infer-v1](https://www.kaggle.com/code/yashbishnoi98/rsna-knee-infer-v1)**

### Summary:

A full walkthrough, in the order each decision constrains the next, of the DICOM pipeline, the LLM-based report label extractor, and the multi-instance-learning image model behind a public leaderboard rank of 18 (top 2.3% of a fast-growing field) on RSNA's Knee Abnormality Detection competition, including the validation bug that had to be caught and corrected before writing this up honestly.

### Competition write-ups, with the code and the mistakes included

## The problem in one sentence

RSNA's Knee Abnormality Detection competition ($77,000 in prizes, closes October 22, 2026)
asks you to predict 12 binary findings per knee MRI study, scored by macro-averaged ROC AUC.
There are 4,407 training studies, 24,371 DICOM series, roughly 820,000 slices. Only 58 of
those studies come with expert-assigned labels. Every other study has to be labeled from the
free-text radiology report attached to it, written in whichever of about a dozen languages
the reading site used.

That is the whole competition. The image model is the well-trodden 80%. A clean 12-label
target for 4,349 unlabeled studies is the hard 20% that actually decides where you land.
What follows is that pipeline, in the order each decision actually constrains the next: what
the score rewards, where the targets come from, how the images are read and normalized, why
nothing in it ever flips left and right, what model turns twelve slots of evidence into
twelve probabilities, how it is trained and honestly validated, and how it survives a
nine-hour, internet-off inference budget. It produced a public leaderboard score of **0.903**
macro ROC AUC, good for rank **18 of 792** teams (top 2.3%) as of the morning of August 9,
2026\. Both the rank and the team count are live positions on a leaderboard that is still
growing fast (430 teams on day two of submissions, 792 a week and a half later), so treat the
denominator as a snapshot, not a fixed fact. Just as importantly, this is also a walkthrough
of a mistake its own internal validation number had to be caught making before any of this
could be written up honestly.

## 1\. What the score rewards

The metric is the unweighted mean of twelve per-label ROC AUCs, and two consequences follow
before any model gets written. Only ranking matters, not calibration: ROC AUC is invariant
under any strictly increasing transform of a label's scores, so there is no reason to spend
effort on threshold tuning or probability calibration. And averaging model outputs is a safe
way to ensemble: since the metric only cares about order, and sigmoid outputs from
independently trained folds already sit on a comparable scale, a plain mean of several folds'
probabilities is a defensible ensemble with no learned weighting required. That is exactly
what the inference kernel does in section 8.

## 2\. Where the targets come from

Everything downstream depends on this step, so it is worth walking through carefully. 58 of
4,407 training studies carry expert labels. The other 4,349 carry only the original
radiology report. Deriving labels from that text is the actual competition, not a
preprocessing step: every lever downstream (model architecture, augmentation, ensembling)
tops out at whatever ceiling the label quality sets.

`extract_labels.py` sends each report to a locally hosted open-weights model (Qwen3.6-35B,
served through Ollama) with a fixed prompt that spells out, finding by finding, exactly what
counts. Not "does the report mention ACL" but the actual clinical rule: a partial or complete
tear counts, a ruptured post-surgical graft counts, an intact graft does not. Synovitis gets
the widest definition because it is the hardest of the twelve to phrase around: the prompt
explicitly tells the model to also count Hoffa fat pad impingement, plica syndrome, and
friction/impingement syndromes with an inflammatory component, because radiologists describe
synovitis in a dozen indirect ways before they ever write the word. Two of the prompt's rules
apply across all twelve findings without exception: an explicit negation ("no effusion", "sin
rotura", "geen afwijkingen") is 0, and a finding that is never mentioned at all is also 0, on
the assumption that radiologists report positive findings and stay silent on the negative.
Other rules are more contextual: hedged mentions ("possible small tear") are judgment calls,
the Impression/Conclusion section is weighted most heavily, and only current, not chronic or
post-operative, findings count. The model runs at temperature 0 with its own reasoning turned
off, and has to answer in a fixed JSON object with all twelve keys or the response is thrown
out and retried.

The prompt was not written once and trusted. It was validated against the 58 gold studies,
scored, and revised. An early version reached 0.828 mean per-class accuracy against expert
labels; reading the errors showed two specific, fixable patterns rather than random noise.
Synovitis had 14 false negatives, mostly reports that implied inflammation without using the
word, so the definition was broadened. Effusion had 16 false positives, mostly from
"trace" or "some" effusion being read as positive when the annotators sometimes did not agree
it counted, and some of that gap turned out to be annotator inconsistency rather than
extractor error: two different studies in the gold set score the same kind of finding in
opposite directions, one marking "leve derrame" (mild effusion) positive and another marking
"some joint effusion" negative. Contusion was over-calling ordinary degenerative marrow edema
as traumatic bruising, so the rule was sharpened to require a traumatic pattern. Fracture was
missing avulsion and insufficiency fractures, so those got an explicit inclusion list. The
revised prompt reached 0.833 mean accuracy, 0.766 mean F1, at roughly 3 seconds per report,
and was locked in as the primary extractor for the full, unlabeled 4,349-study run.

One number worth sitting with: gold labels here come from an expert re-reading the actual
images, not from the text report, so even a perfect report reader has an intrinsic accuracy
ceiling somewhere around 0.88 to 0.92, because a report and an image do not always agree.
0.833 is closer to that ceiling than it looks at first glance, but it is not at the ceiling,
and that gap is probably the real limiting factor on this whole approach right now, ahead of
anything on the image side.

### 2a. Fusing more than one reader, honestly

The extractor's output is not the only signal that can end up in the final label.
`build_labels.py` supports fusing up to three sources: the primary extractor above, an
optional second-family cross-check model for disagreement resolution, and a third,
independently sourced set of report-derived label probabilities, a public Kaggle dataset from
another competitor ( [pilkwang/rsna-knee-llm-labels](https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels)),
used as a third opinion. Each source's hard vote is weighted by its own measured per-class
accuracy against the 58 gold studies (so a source that is unreliable on Synovitis
specifically gets less say on Synovitis specifically, not blanket-penalized). When every
source's hard vote agrees, the label is an exact 0 or 1. When they disagree, the output is a
soft label: a reliability-weighted average of every vote, so a confident dissent from any one
source can pull a label away from unanimous-looking consensus rather than being silently
overruled. For the labels that actually trained the submitted model, only two of those three
sources were live: the second-family cross-check run had not finished yet, so fusion was the
primary extractor plus the third-party dataset, not all three.

That fusion logic had a bug in the version that actually produced the labels used to train
the model behind this post's leaderboard score, and it is worth stating plainly rather than
smoothing over: an earlier build script truncated the third-opinion source's probabilities
with Python's `int()` before fusing them, which meant a confident positive probability from
that source (as high as 0.94) could never override a primary-negative label, only ever agree
with a primary-positive one. The bug was one-directional and asymmetric, and it was caught in
a full audit after the model had already been trained and submitted. The fusion logic has
since been rewritten to vote symmetrically with no truncation, but the model that actually
landed rank 18 was trained on labels produced before that fix. That is a real limitation of
this specific result, not a hypothetical one, and it is why the next full training run uses
the corrected label file rather than the one this post's number came from.

## 3\. Reading the acquisition

Each study can have anywhere from one to a dozen-plus DICOM series (different planes,
different MRI sequences), and not all of them are equally informative for these twelve
findings. `dataset.py`'s `pick_series` picks up to three: it prefers series flagged
fluid-sensitive (the sequences most informative for fluid, cartilage, and marrow findings),
and tries to get one from each anatomical plane (sagittal, coronal, axial) before filling any
remaining slots from whatever is left. Within each chosen series, `subsample_slices` picks a
fixed number of slices: at training time, evenly spaced positions with a small amount of
random jitter added for augmentation; at evaluation time, exactly evenly spaced with no
randomness, so the same study always gets scored the same way. This selection logic is
shared by training and inference; the inference kernel calls a deterministic mirror of it
(section 8).

## 4\. From DICOM to a training tensor

`etl.py` walks every series directory and reads each `.dcm` file with `pydicom`. Per slice,
it applies `RescaleSlope`/`RescaleIntercept` to get real intensity values, inverts
`MONOCHROME1` images (some scanners store brightness inverted), and reads `InstanceNumber`.
Once every slice in a series has been read, it sorts them by `InstanceNumber` so depth order
is anatomically correct and stacks them into one volume. Each series then gets its own 1st
to 99th percentile intensity window (clipped and rescaled to \[0, 1\]), which matters more
than it sounds: a global fixed window would let one unusually bright or dark series wreck
the contrast for the whole batch. Depth gets center-cropped to 64 slices for series that run
long, and every slice is resized to 288x288 with `cv2.INTER_AREA`. The result is quantized
to `uint8` and written as a compressed `.npz`.

That last step, going from float back down to `uint8`, throws away precision on purpose. The
inference kernel that runs on Kaggle has to reproduce the same windowing, cropping, resizing,
and quantization at test time on DICOMs it has never seen. `infer.py`'s `read_series` follows
the same preprocessing math as `etl.py`, with two real additions rather than a literal copy:
an explicit `pylibjpeg`/`gdcm` decode fallback chain for DICOMs that fail to decode by
default, and a PIL fallback resize path if `cv2` is unavailable, both defensive additions for
a competition environment the training box never has to deal with. The kernel's own README
notes this preprocessing was checked bit-exact against the cached training tensors; that
specific check is not something this post independently re-ran, so take it as documented
rather than re-verified here. Getting this parity wrong in general is one of the more common
silent ways to lose points in a code competition, because your local validation number stays
believable while your test-time predictions quietly degrade.

The full run processed all 24,371 series with zero skips and zero empty reads in 978 seconds
(per `etl_train.log`); the resulting tensor cache is 39GB on disk.

## 5\. Why nothing here ever flips left or right

Five of the twelve labels are laterality-specific (medial versus lateral meniscus, medial
versus lateral OA, MCL). `augment_volume` applies the same random rotation, brightness-gamma
jitter, and slight rescale to every slice in a series, but it never, under any setting,
horizontally flips an image. A horizontal flip would silently swap left and right anatomy
without updating the label to match. It is a one-line decision that would be very easy to get
wrong and very hard to notice once it was wrong, since the training loss would still go down
normally.

## 6\. Turning slices into twelve study-level probabilities

The model itself, `KneeMILModel` in `model.py`, is a multi-instance-learning setup in the
tradition of the original MRNet paper: a shared 2D backbone (`timm`, single input channel
since these are grayscale) is applied to every slice independently, the resulting per-slice
embeddings are pooled into one per-series embedding, and a linear head turns that into 12
logits per series. A study's final prediction is the mean of its series-level logits. The
pooling step supports three options: mean, max, or a learned gated-attention pool (Ilse et
al.'s formulation, where the model learns which slices to weight more heavily rather than
treating them uniformly). Gated attention is the more sophisticated choice and was the
code's default, but the hyperparameter search that picked the winning configuration for this
submission (section 7) landed on plain max-pooling over slices instead, at this backbone
size, this slice count, and this amount of training data. It is a small result but a genuine
one: the fancier pooling mechanism did not win on the evidence, so it was not used.

## 7\. Choosing a configuration honestly

Training uses `GroupKFold` with 5 folds over study IDs (each study is its own group, since
one row is one training example), `BCEWithLogitsLoss` (which accepts the soft, fused labels
from section 2 directly, no thresholding needed), `AdamW`, a short linear warmup followed by
cosine decay, and bf16 mixed precision. Each fold keeps the checkpoint with the best
validation macro-AUC, skipping any label column that happens to be constant within a fold's
validation split, since AUC is undefined there.

The winning configuration itself came out of a hyperparameter search, not a hand-picked
guess: 20 cheap proxy trials on 10% of the data for 2 epochs each, ranked by a blended score
of 0.7 times the proxy's cross-validation AUC plus 0.3 times its score on the 58 gold
studies. The best of those 20 trials scored 0.6811 on that blend and picked
`efficientnet_b3` with K=3 series, T=12 training slices, max-pooling, and medium augmentation
as the winning combination. (A handful of later proxy trials, run after this configuration
was already training at full scale, would edge past 0.6811, but they came too late to change
this decision.) Taking that exact configuration to a full 5-fold, 8-epoch run took roughly
12.4 hours and produced a very different-looking number: 0.8788 blended, made of a clean
cross-validation macro-AUC of 0.8544 and a gold58 macro-AUC of 0.9357. That gap between the
cheap proxy signal and the full-run outcome is real and worth flagging on its own: a
10%-scale, 2-epoch proxy is a rough guide to which configuration is worth taking further, not
a reliable predictor of what the full run will actually score, and treating it as one would
be a mistake.

### 7a. Re-measuring the number that leaked

The 0.9357 gold58 number itself did not survive an audit. It was measured by evaluating
every fold's checkpoint against all 58 gold studies, but each fold's own training split
already contained roughly 46 to 47 of those same 58 studies (about four in five of them), so
most of that number was the model grading questions it had already seen the answer to. Once
caught, the fix was to reconstruct the exact fold splits as they existed at training time and
re-score each gold study only against the checkpoint from the one fold where it had actually
been held out, so every gold study is scored exactly once by a model that never trained on
it. That honest, cross-fitted number came out to 0.8568 macro-AUC, not 0.9357. Interestingly,
it lines up closely with the clean cross-validation score of 0.8544, which is reassuring: the
model's real skill was never far from what the honest numbers say, the original 0.9357 was
just measuring the wrong thing. The current version of the training script now excludes the
58 gold studies from the fold pool entirely by default, so this specific leak cannot happen
again on the next run, but it did happen on the run that produced this submission, and the
number quoted below is the corrected one, not the original.

## 8\. What actually runs on Kaggle: inference under a nine-hour, internet-off budget

RSNA runs this as a code competition: your notebook gets attached to the hidden test set,
internet access is disabled, and you get up to 9 hours of GPU time to score roughly 1,300
studies. `infer.py` has to do everything sections 3 through 7 assume happened offline, live,
inside that budget.

It reproduces the ETL preprocessing exactly, including a decode fallback chain (`pydicom`'s
default handler, then explicit `pylibjpeg`, then `gdcm`) with logging of which handler
actually worked, since compressed DICOM transfer syntaxes are one of the more common ways a
code competition notebook silently fails on hidden data it was never tested against. It
selects series deterministically with the same fluid-sensitive, one-per-plane logic as
training, loads all 5 fold checkpoints, and simply averages their sigmoid outputs, a plain
5-model ensemble with no learned weighting.

Because the real per-study decode-and-inference speed on Kaggle's hardware cannot be
measured perfectly in advance, the kernel tracks its own projected total runtime every 25
studies and degrades in two stages if the projection is going to blow through budget: first
dropping evaluation slices per series from 32 down to 16, and if that is still not enough,
dropping from 5 models in the ensemble down to 3. It also writes a complete, valid
`submission.csv` every 25 studies rather than only at the very end, so a crash or a hard
runtime cutoff still leaves a scoreable file behind, and any study whose DICOMs fail to
decode at all gets a neutral 0.5 prediction on every label rather than crashing the run for
the other 1,299 studies.

## Where it actually landed

| Metric | Value | Source |
| --- | --- | --- |
| Local cross-validation macro-AUC (5-fold, gold excluded) | 0.8544 | `image_model/EXPERIMENTS.md`, run `r1_t10_full` |
| Honest cross-fitted gold58 macro-AUC (leak corrected) | 0.8568 | `analysis/honest_gold58_r1_t10_full.csv`, re-measured after the audit |
| Public Kaggle leaderboard, macro ROC-AUC | 0.903 | Kaggle submission 55361257, scored 2026-08-08 |
| Public leaderboard rank | 18 of 792 teams (top 2.3%) | Official leaderboard export, pulled 2026-08-09 (moving fast: 430 teams two days into submissions) |

That leaderboard score is unaffected by the gold58 leakage bug described above; it comes from
Kaggle scoring the submission against genuinely held-out hidden data, not from any number
computed locally. The bug mattered for model _selection_, not for what the leaderboard
actually measured.

## What this does not show

This is a public leaderboard result, not a final one. The competition runs until October 22,
2026, and the official competition pages explicitly warn that finding prevalence is not
guaranteed to be the same across the training set, the public leaderboard, and the final
private evaluation set, so a public rank of 18 is not a promise of a private rank anywhere
near it.

The label extractor's own accuracy ceiling, roughly 0.83 mean per-class agreement against
expert image re-reads, is probably close to the real limiting factor on this whole approach
right now. Pushing further on image-model architecture alone will run into that ceiling
before it runs into anything else; the more promising next step is a second, independently
trained extractor model merged in as a genuine cross-check rather than a third opinion,
which is in progress but not yet finished.

And, again, plainly: the model that produced the 0.903 score above was trained on labels
built with a fusion bug already described, and validated with a leaked metric already
corrected here. Both are now fixed in the code. Neither has yet been used to train a new full
model. The next submission will be the first real test of whether fixing them actually moves
the leaderboard score, or whether, as the closeness of 0.8544 and 0.8568 suggests, the
underlying model was already about this good.

## Reproducible appendix

The submission notebook is public on Kaggle: [rsna-knee-infer-v1](https://www.kaggle.com/code/yashbishnoi98/rsna-knee-infer-v1).
It will not run standalone outside the competition environment, since it needs the
competition's hidden test data and an attached weights dataset, but the full inference code,
including the adaptive time-budget logic described above, is there to read. A companion
notebook walks through every stage above, sections numbered the same way, with the real
source code for each step inline.

##### Every number in this post traces to a source file in the repository or a live leaderboard pull; see the post itself for exact citations.

More from this author

[**Decoder crowding predicts SAE steering side effects, and it is not just firing frequency**\\
\\
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/94j9Xh140a-lDMRSLUJPj.png)\\
\\
August 7, 2026](https://huggingface.co/blog/bishnoiyash/decoder-crowding-predicts-sae-steering-side-effect)

### Community

EditPreview

Upload images, audio, and videos by dragging in the text input, pasting, or clicking here.

Tap or paste here to upload images

Comment

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fbishnoiyash%2Frsna-competetion) or [log in](https://huggingface.co/login?next=%2Fblog%2Fbishnoiyash%2Frsna-competetion) to comment

[Upvote \\
\\
-](https://huggingface.co/login?next=%2Fblog%2Fbishnoiyash%2Frsna-competetion)