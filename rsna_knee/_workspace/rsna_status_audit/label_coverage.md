train studies=4407 reports_nonnull=4407
gold non-null per label:
  ACL                gold=  58
  MCL                gold=  58
  Medial Meniscus    gold=  58
  Lateral Meniscus   gold=  58
  Medial OA          gold=  58
  Lateral OA         gold=  58
  PF OA              gold=  58
  Effusion           gold=  58
  Synovitis          gold=  58
  Baker's            gold=  58
  Contusion          gold=  58
  Fracture           gold=  58

building pseudo table from reports...
pseudo shape=(4407, 13)

=== combined effective labels (gold first, then report fill) ===
  ACL                gold=  58 +fill=3114 => eff=3172 (72.0%) pos= 958 neg=2156 midish=   0
  MCL                gold=  58 +fill=3150 => eff=3208 (72.8%) pos= 564 neg=2586 midish=   0
  Medial Meniscus    gold=  58 +fill=3236 => eff=3294 (74.7%) pos=1785 neg=1451 midish=   0
  Lateral Meniscus   gold=  58 +fill=3009 => eff=3067 (69.6%) pos= 792 neg=2217 midish=   0
  Medial OA          gold=  58 +fill=1065 => eff=1123 (25.5%) pos= 655 neg= 410 midish=   0
  Lateral OA         gold=  58 +fill= 944 => eff=1002 (22.7%) pos= 410 neg= 534 midish=   0
  PF OA              gold=  58 +fill=2645 => eff=2703 (61.3%) pos=1142 neg=1503 midish=   0
  Effusion           gold=  58 +fill=3658 => eff=3716 (84.3%) pos=2329 neg=1329 midish=   0
  Synovitis          gold=  58 +fill= 503 => eff= 561 (12.7%) pos= 479 neg=  24 midish=   0
  Baker's            gold=  58 +fill=1943 => eff=2001 (45.4%) pos=1068 neg= 875 midish=   0
  Contusion          gold=  58 +fill=1580 => eff=1638 (37.2%) pos=1014 neg= 566 midish=   0
  Fracture           gold=  58 +fill= 857 => eff= 915 (20.8%) pos= 275 neg= 582 midish=   0

=== weakest labels by effective coverage ===
  Synovitis          eff= 561 (12.7%) pos=479 neg=24
  Fracture           eff= 915 (20.8%) pos=275 neg=582
  Lateral OA         eff=1002 (22.7%) pos=410 neg=534
  Medial OA          eff=1123 (25.5%) pos=655 neg=410
  Contusion          eff=1638 (37.2%) pos=1014 neg=566
  Baker's            eff=2001 (45.4%) pos=1068 neg=875
  PF OA              eff=2703 (61.3%) pos=1142 neg=1503
  Lateral Meniscus   eff=3067 (69.6%) pos=792 neg=2217
  ACL                eff=3172 (72.0%) pos=958 neg=2156
  MCL                eff=3208 (72.8%) pos=564 neg=2586
  Medial Meniscus    eff=3294 (74.7%) pos=1785 neg=1451
  Effusion           eff=3716 (84.3%) pos=2329 neg=1329

=== decision inputs already measured ===
test_series planes: Axial 3/3 studies, Sagittal 3/3, Coronal 3/3
fold0 S vs C corr=0.47; fold0 vs fold1 same-plane corr~0.83-0.88
LB: fold0 S+C=0.685 BEST; +fold1=0.679; 5-fold sagittal=0.667
EXP-002 A3 Contusion-only label change: 0.659 (worse)
