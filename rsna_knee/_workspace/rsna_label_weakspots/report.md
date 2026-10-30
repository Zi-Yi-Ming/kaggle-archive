# 标签弱项分析：报告抽取器 vs 官方 gold

train n=4407; gold 仅 58/4407

## Gold 对齐诊断（仅 58 例官方标注）

| label | gold_n | pseudo有效 | agree | pos漏抓 | neg误报 | silent_on_gold_pos |
|---|---:|---:|---:|---:|---:|---:|
| ACL | 58 | 48 | posOK=24/24 | miss=0 | neg_on_pos=0 | silent_on_gold_pos=0 |
| MCL | 58 | 45 | posOK=9/9 | miss=0 | neg_on_pos=0 | silent_on_gold_pos=0 |
| Medial Meniscus | 58 | 46 | posOK=23/26 | miss=3 | neg_on_pos=0 | silent_on_gold_pos=3 |
| Lateral Meniscus | 58 | 42 | posOK=18/23 | miss=5 | neg_on_pos=1 | silent_on_gold_pos=4 |
| Medial OA | 58 | 15 | posOK=9/15 | miss=6 | neg_on_pos=1 | silent_on_gold_pos=5 |
| Lateral OA | 58 | 11 | posOK=6/11 | miss=5 | neg_on_pos=0 | silent_on_gold_pos=5 |
| PF OA | 58 | 37 | posOK=14/21 | miss=7 | neg_on_pos=2 | silent_on_gold_pos=5 |
| Effusion | 58 | 55 | posOK=31/35 | miss=4 | neg_on_pos=3 | silent_on_gold_pos=1 |
| Synovitis | 58 | 15 | posOK=10/27 | miss=17 | neg_on_pos=1 | silent_on_gold_pos=16 |
| Baker's | 58 | 25 | posOK=10/12 | miss=2 | neg_on_pos=0 | silent_on_gold_pos=2 |
| Contusion | 58 | 34 | posOK=15/19 | miss=4 | neg_on_pos=0 | silent_on_gold_pos=4 |
| Fracture | 58 | 25 | posOK=12/18 | miss=6 | neg_on_pos=1 | silent_on_gold_pos=5 |

## 全量覆盖与正负比

| label | eff_cov | pos | neg | silent | pos/neg |
|---|---:|---:|---:|---:|---:|
| ACL | 71.7% | 988 | 2174 | 1245 | 0.45 |
| MCL | 72.5% | 579 | 2616 | 1212 | 0.22 |
| Medial Meniscus | 74.5% | 1816 | 1466 | 1125 | 1.24 |
| Lateral Meniscus | 69.2% | 814 | 2237 | 1356 | 0.36 |
| Medial OA | 24.5% | 666 | 414 | 3327 | 1.61 |
| Lateral OA | 21.7% | 419 | 536 | 3452 | 0.78 |
| PF OA | 60.9% | 1162 | 1520 | 1725 | 0.76 |
| Effusion | 84.3% | 2375 | 1338 | 694 | 1.78 |
| Synovitis | 11.8% | 493 | 25 | 3889 | 19.72 |
| Baker's | 44.7% | 1083 | 885 | 2439 | 1.22 |
| Contusion | 36.6% | 1045 | 569 | 2793 | 1.84 |
| Fracture | 20.0% | 292 | 590 | 3525 | 0.49 |

## Gold 阳性但抽取器沉默/否定的报告片段（弱标签）

### 错误语言分布（gold 阳性 × 抽取失败）
- ('Synovitis', 'en/other', 'silent'): 11
- ('Lateral OA', 'en/other', 'silent'): 5
- ('Medial OA', 'en/other', 'silent'): 4
- ('PF OA', 'en/other', 'silent'): 3
- ('Contusion', 'en/other', 'silent'): 3
- ('Effusion', 'tr', 'neg'): 3
- ('Medial Meniscus', 'en/other', 'silent'): 3
- ('Synovitis', 'tr', 'silent'): 2
- ('Fracture', 'en/other', 'silent'): 2
- ('Synovitis', 'pl', 'silent'): 1
- ('Synovitis', 'en/other', 'neg'): 1
- ('Synovitis', 'ru', 'silent'): 1
- ('Synovitis', 'de', 'silent'): 1
- ('Medial OA', 'en/other', 'neg'): 1
- ('Medial OA', 'tr', 'silent'): 1
- ('PF OA', 'tr', 'neg'): 1
- ('PF OA', 'de', 'silent'): 1
- ('PF OA', 'ru', 'neg'): 1
- ('PF OA', 'fr', 'silent'): 1
- ('Fracture', 'en/other', 'neg'): 1
- ('Fracture', 'pl', 'silent'): 1
- ('Fracture', 'tr', 'silent'): 1
- ('Fracture', 'de', 'silent'): 1
- ('Contusion', 'ru', 'silent'): 1
- ('Effusion', 'en/other', 'silent'): 1

### 弱标签失败样例（报告前 400 字）

#### Synovitis
- kind=silent gold=1.0 pseudo=None
  Exam Type: MRI KNEE RIGHT WO CONTRAST Exam Date and Time: [DATE] [TIME] Indication: 2 years of pain with walking up and down the stairs twisting and squatting. Comparison: No relevant prior studies available for comparison.  TECHNIQUE: MRI of the right knee was performed on a 1.5 Tesla system body coil in three planes (axial, sagittal, and coronal), using a standard non-contrast protocol.  FINDING
- kind=silent gold=1.0 pseudo=None
   In the medial compartment, the meniscus is not torn and there is no focal chondrosis or chondral injury.      The lateral compartment, there is complex tear (main radial and longitudinal vertical component) at the posterior horn of the lateral meniscus. There is no focal chondrosis or chondral injury.      The patellofemoral joint, the patellar and trochlear cartilage appears congruent without ch
- kind=silent gold=1.0 pseudo=None
  Técnica: RMN de la rodilla. Resultados: Fricción de la banda iliotibial. Síndrome de pinzamiento de la almohadilla grasa de Hoffa. Condropatía rotuliana. Impresión: Fricción de la banda iliotibial. Síndrome de pinzamiento de la almohadilla grasa de Hoffa. Condropatía rotuliana.

#### Medial OA
- kind=silent gold=1.0 pseudo=None
  Exam Type: MRI KNEE RIGHT WO CONTRAST Exam Date and Time: [DATE] [TIME] Indication: Pain Comparison: No relevant prior studies available for comparison.  TECHNIQUE: MRI of the right knee was performed on a 3.0 Tesla system with a dedicated knee coil in three planes (axial, sagittal, and coronal), using a standard non-contrast protocol.  FINDINGS: OSSEOUS STRUCTURES: Alignment is anatomic. Subchond
- kind=silent gold=1.0 pseudo=None
  Technique: MRI of the knee. ACL normal. MCL normal. Medial meniscus tear. Lateral meniscus tear. Incipient OA of all three compartmens.  Baker's cyst present. Large effusion. Insufficient fracture of medial femoral condyl with adjacent bone marrow oedema. Conclusion: Medial meniscus tear. Lateral meniscus tear. Incipient OA of all three compartmens.  Baker's cyst present. Large effusion. Medial co
- kind=neg_on_pos gold=1.0 pseudo=0.12000000000000001
  Exam Type: MRI KNEE LEFT WO CONTRAST Exam Date and Time: [DATE] [TIME] Indication: Pain. Comparison: [REDACTED].  TECHNIQUE: MRI of the lumbar knee was performed on a 3.0 Tesla system with a dedicated knee coil in three planes (axial, sagittal, and coronal), using a standard non-contrast protocol.  FINDINGS: OSSEOUS STRUCTURES: Minimal degenerative subchondral bone marrow edema is present at the l

#### Lateral OA
- kind=silent gold=1.0 pseudo=None
  Technique: MRI of the knee. ACL normal. MCL normal. Medial meniscus tear. Lateral meniscus tear. Incipient OA of all three compartmens.  Baker's cyst present. Large effusion. Insufficient fracture of medial femoral condyl with adjacent bone marrow oedema. Conclusion: Medial meniscus tear. Lateral meniscus tear. Incipient OA of all three compartmens.  Baker's cyst present. Large effusion. Medial co
- kind=silent gold=1.0 pseudo=None
  MRI right knee  INDICATION: Assess ligamentous injury  There is a vertical tear in the periphery of the posterior horn of the medial meniscus. No lateral meniscal tear. Complete rupture of the ACL. Complete rupture of the PCL. Extensor mechanism intact. Complete rupture of the MCL at the level of the medial jointline. The proximal fibers are squiggly. IT band intact. High-grade partial tear of the
- kind=silent gold=1.0 pseudo=None
   In the medial compartment, there is radial tear at the posterior root of the medial meniscus. There is displaced meniscal fragment into the medial gutter. There is diffuse high grade and low grade chondrosis (less than and more than 50% thickness cartilage loss) along weightbaring medial femoral condyle and medial tibial plateau. There is subchondral edema. Osteophytes are present.      The later

#### PF OA
- kind=silent gold=1.0 pseudo=None
  Technique: MRI of the knee. ACL normal. MCL normal. Medial meniscus tear. Lateral meniscus tear. Incipient OA of all three compartmens.  Baker's cyst present. Large effusion. Insufficient fracture of medial femoral condyl with adjacent bone marrow oedema. Conclusion: Medial meniscus tear. Lateral meniscus tear. Incipient OA of all three compartmens.  Baker's cyst present. Large effusion. Medial co
- kind=neg_on_pos gold=1.0 pseudo=0.12000000000000001
  SAĞ DİZ MRG. Tetkik protokolü: Çok düzlemli, çok sekanslı. Bulgular: Lateral menisküs normal. Medial menisküs ekstrüde görünümde olup posterior hornunda yırtık ile uyumlu sinyal değişiklikleri mevcuttur. Arka çapraz bağ, çm çapraz bağ , lateral ve medial kollateral ligaman normaldir.Medial kollateral ligaman çevresinde sıvı artışı izlenmiştir. Distal kuadriseps ve patellar tendonlar normaldir. Pat
- kind=silent gold=1.0 pseudo=None
  Technique: MRI of the knee. ACL normal. MCL normal. Medial meniscus mucoid degeneration. Lateral meniscus normal. OA of medial compartment. No baker's cyst. Effusion with synovitis. Conclusion: OA of medial compartment. Effusion with synovitis.

#### Fracture
- kind=neg_on_pos gold=1.0 pseudo=0.12000000000000001
  Exam Type: MRI KNEE RIGHT WO CONTRAST Exam Date and Time: [DATE] [TIME] Indication: Pain Comparison: No relevant prior studies available for comparison.  TECHNIQUE: MRI of the right knee was performed on a 3.0 Tesla system with a dedicated knee coil in three planes (axial, sagittal, and coronal), using a standard non-contrast protocol.  FINDINGS: OSSEOUS STRUCTURES: Alignment is anatomic. Subchond
- kind=silent gold=1.0 pseudo=None
  Técnica: RMN de la rodilla. Resultados: Rotura del LCA. Rotura parcial del LCM. Rotura de menisco interno y lateral. Derrame. Contusiones óseas femorotibiales. Impresión: Rotura del LCA. Rotura parcial del LCM. Rotura de menisco interno y lateral. Derrame. Contusiones óseas femorotibiales.
- kind=silent gold=1.0 pseudo=None
  No evidence of knee effusion. Normal medial and lateral menisci. No evidence of tears.  ACL is ruptured. There is mild anterior translation of the lateral tibial plateau in relation to femur.  Normal PCL, MCL and LCL. Normal extensor mechanism.  The tibiofemoral and patellofemoral articular cartilage is normal. A bone contusion is noted in the posterolateral corner of the lateral tibial plateau.  

#### Contusion
- kind=silent gold=1.0 pseudo=None
  ΜΑΓΝΗΤΙΚΗ ΤΟΜΟΓΡΑΦΙΑ ∆ΕΞΙΟΥ ΓΟΝΑΤΟΣ Τεχνική: Η εξέταση έγινε µε ακολουθίες παλµών Τ1, PD fs και Τ2*. Ευρήµατα: - Εκτεταµένο οίδηµα του οστικού µυελού στην εγγύς µετάφυση/επίφυση της κνήµης παριστά οστικό µώλωπα στο πλαίσιο της αναφερόµενης κάκωσης. - Οιδηµατώδης απεικόνιση του πρόσθιου χιαστού συνδέσµου µε ασυνέχεια των ινών του στο πλαίσιο υφολικής (σχεδόν πλήρους) ρήξης. - Οιδηµατώδης απεικόνιση
- kind=silent gold=1.0 pseudo=None
  COMPARISON:None.  CLINICAL HISTORY:Left knee pain and swelling after fall. Medial joint line pain. Suspected bone contusion/meniscal tear.  PROCEDURE:Multisequence, multiplanar unenhanced MRI of the left knee according to routine protocol.  IMAGING FINDINGS:  Nondiagnostic scout localizing images reviewed.  The lateral meniscus is intact. The medial meniscus is intact.  High-grade partial-thicknes
- kind=silent gold=1.0 pseudo=None
  МР находка: МР данни за ставен излив. Изобразява се остеохондрална фрактура в областта на медиалния кондил на бедрената кост. Фрактурата се представя като хипоинтензна линия с дъговидна форма. Налице е костно-мозъчен едем в костта, както и депресия на медиалното плато. В този участък се изобразява и изтъняване на артикулиращия хрущял на кондила на протежение от около 9 мм. Костно-мозъчен едем е на

## 关键词探针：全量报告中弱标签相关词 vs 抽取覆盖
- Synovitis: regex_hit_reports=1860 | extractor_eff=518 | hit_and_covered=0 | hit_but_silent=0
- Medial OA: regex_hit_reports=1593 | extractor_eff=1080 | hit_and_covered=0 | hit_but_silent=0
- Fracture: regex_hit_reports=1157 | extractor_eff=882 | hit_and_covered=0 | hit_but_silent=0

## 抽取器自带统计（build_pseudo_table verbose 已在 coverage 跑过）
结论候选写入 conclusions.md
