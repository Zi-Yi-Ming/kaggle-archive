train.csv: exists=True size=5690007
test.csv: exists=True size=212
test_series.csv: exists=True size=2213
sample_submission.csv: exists=True size=470
train_series.csv: exists=False size=-

train.csv shape=(4407, 14) cols=['StudyInstanceUID', 'Report', 'ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA', 'PF OA', 'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
non-id cols=['Report', 'ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA', 'PF OA', 'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
  Report: non-null=4407/4407
  ACL: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 34, 1.0: 24}
  MCL: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 49, 1.0: 9}
  Medial Meniscus: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 32, 1.0: 26}
  Lateral Meniscus: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 35, 1.0: 23}
  Medial OA: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 43, 1.0: 15}
  Lateral OA: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 47, 1.0: 11}
  PF OA: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 37, 1.0: 21}
  Effusion: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 1.0: 35, 0.0: 23}
  Synovitis: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 31, 1.0: 27}
  Baker's: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 46, 1.0: 12}
  Contusion: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 39, 1.0: 19}
  Fracture: non-null=58/4407 (1.3%) unique=2 value_counts_head={nan: 4349, 0.0: 40, 1.0: 18}

test.csv shape=(3, 1) cols=['StudyInstanceUID']
                                                   StudyInstanceUID
0  1.2.826.0.1.3680043.8.498.10047035057544427318018579121635276191
1  1.2.826.0.1.3680043.8.498.10062861783145312629332250977456991776
2  1.2.826.0.1.3680043.8.498.10067514707072572280263481548497591402

test_series.csv shape=(15, 5) cols=['StudyInstanceUID', 'SeriesInstanceUID', 'Fluid_Sensitive', 'Fat_Suppression', 'Anatomical_Plane']
test plane counts:
Anatomical_Plane
Sagittal    7
Axial       4
Coronal     4
Name: count, dtype: int64
test studies by plane:
Anatomical_Plane
Axial       3
Coronal     3
Sagittal    3
Name: StudyInstanceUID, dtype: int64
train_series.csv missing locally — plane coverage on train unknown from CSV

found label manifest D:\桌面\Kaggle\rsna_knee\artifacts\exp_002_a3_fold0\label_manifest.json

found label manifest D:\桌面\Kaggle\rsna_knee\artifacts\exp_002_a3\label_manifest.json

=== nearby label-related notes ===
json artifacts\exp_002_a3\label_manifest.json size=499
json artifacts\exp_002_a3_fold0\label_manifest.json size=499
json _out\exp002_a3_final\artifacts\exp_002_a3_fold0\label_manifest.json size=499
json _out\exp002_a3_final2\artifacts\exp_002_a3_fold0\label_manifest.json size=499

sample_submission shape=(3, 13)
                                                   StudyInstanceUID  ACL  MCL  Medial Meniscus  Lateral Meniscus  Medial OA  Lateral OA  PF OA  Effusion  Synovitis  Baker's  Contusion  Fracture
0  1.2.826.0.1.3680043.8.498.10047035057544427318018579121635276191  0.5  0.5              0.5               0.5        0.5         0.5    0.5       0.5        0.5      0.5        0.5       0.5
1  1.2.826.0.1.3680043.8.498.10062861783145312629332250977456991776  0.5  0.5              0.5               0.5        0.5         0.5    0.5       0.5        0.5      0.5        0.5       0.5
2  1.2.826.0.1.3680043.8.498.10067514707072572280263481548497591402  0.5  0.5              0.5               0.5        0.5         0.5    0.5       0.5        0.5      0.5        0.5       0.5
