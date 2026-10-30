# -*- coding: utf-8 -*-
"""rsna_report_labels - 从放射报告文本抽取 12 病灶弱标签(多语言规则抽取器)

本文件由 top_kernels/rsna-knee-baseline-v1.ipynb 的抽取器(cells 6-11)原样移植,
负责把 4407 份多语言 MRI 放射报告转成 12 病灶的证据分数 + 置信度。

为什么存在:官方 gold 只有 58 study,社区"软标签"数据集 98.7% 是字面 0.5 死值
(零增量信息),导致 BCE 梯度约 0、loss 恒 0.693、模型学不动(2026-09-06 实证)。
报告文本里才有真正的信号——本抽取器即信号源。

用法(与 rsna_v3.load_labels 集成,零挂载,纯 CPU):
    import rsna_report_labels as R
    table = R.build_pseudo_table(train_df)   # StudyInstanceUID + pseudo_<12>(分数或 NaN)

输出语义(每个 (study, finding) 格):
    1) n_pos>0               -> soft 目标 = 证据分数(0.72~0.95,按严重度/重复分级)
    2) n_pos==0 and n_neg>0  -> soft 目标 = 证据分数(0.04~0.20,否定次数越多越低)
    3) 沉默 / 不确定         -> NaN(不进损失,由 KneeDataset valid 掩码排除)
    4) 官方 gold 由 load_labels 优先覆盖,本表只填空缺格。
"""
import pandas as pd

# --- 以下为社区抽取器原样移植(勿改词典) ---
# source: top_kernels/rsna-knee-baseline-v1.ipynb cells 6-11 (rule extractor section)
# normalise -> segment -> scope; nine languages pooled; stem+side proximity fallback;
# assertion/negation/hedge polarity per clause; graded severity scoring.


import re
import unicodedata

TARGETS = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]


# Turkish dotted/dotless i must be folded before casefolding, otherwise "İZLENMEZ"
# and "izlenmez" diverge. ß and the Croatian/Serbian d-with-stroke likewise.
_PRE = str.maketrans({
    "ı": "i", "İ": "i", "I": "i", "ß": "ss", "đ": "d", "Đ": "d",
    "ø": "o", "Ø": "o", "æ": "ae", "Æ": "ae",
})


def normalize(text: str) -> str:
    """Fold case, diacritics and separators; keep Greek and Cyrillic letters.

    NFKD decomposition strips Latin accents and Greek tonos alike (ά -> α), which is what
    we want: reports are inconsistent about accents. It also maps the MICRO SIGN U+00B5
    to a real mu, which matters because most Greek reports here use the wrong codepoint.
    """
    if not isinstance(text, str):
        return ""
    text = text.translate(_PRE).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("­", "")                    # soft hyphen
    text = re.sub(r"[_\-/\\]+", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text


_SENT_SPLIT = re.compile(r"(?<=[.;!?])\s+|\n+")


def clauses(text: str):
    """Split into clauses, then attach `header:` lines to the value that follows.

    A report line reading `Fractures :` followed by `Aucune.` is one statement. Splitting
    on punctuation alone separates the anatomy from its negation and flips the label.
    """
    norm = normalize(text)
    raw = [c.strip() for c in _SENT_SPLIT.split(norm) if c and c.strip()]

    merged = []
    for i, c in enumerate(raw):
        # A fragment ending in a colon is a heading for the next fragment. Structured
        # English reports write long ones - "lateral compartment (meniscus, collateral
        # ligament complex, cartilage):" is eight words - so the cap is generous.
        #
        # A merged heading must NOT also stand alone. On its own it carries the anatomy
        # word with no negation in scope, so `Fractures :` / `Aucune.` asserted a fracture
        # off the heading while the joined clause correctly read the denial. The joined
        # clause is a superset of the heading, so nothing is lost by dropping it; a
        # heading with no value beneath it is not merged and still stands.
        if c.endswith(":") and len(c.split()) <= 14 and i + 1 < len(raw):
            merged.append(c + " " + raw[i + 1])
        else:
            merged.append(c)
    # Comma-separated enumerations inside a long clause hide separate assertions.
    out = []
    for c in merged:
        out.append(c)
        if len(c.split()) > 25:
            out.extend(p.strip() for p in c.split(",") if len(p.split()) > 2)
    return out


def _rx(*alts: str) -> re.Pattern:
    return re.compile("|".join(alts))


NEGATION = _rx(
    # en
    r"\bno\b", r"\bnot\b", r"\bwithout\b", r"\bnegative for\b", r"\babsence\b",
    r"\bno evidence\b", r"\bunremarkable\b", r"\bfree of\b", r"\bnone\b", r"\bnil\b",
    # es
    r"\bsin\b", r"\bno hay\b", r"\bausencia\b", r"\bausentes?\b",
    # fr
    r"\bpas de\b", r"\bsans\b", r"\baucune?\b", r"\babsence\b",
    # nl
    r"\bgeen\b", r"\bzonder\b", r"\bniet\b",
    # de
    r"\bkeine?\b", r"\bohne\b", r"\bnicht\b",
    # tr
    r"\byok\b", r"\byoktur\b", r"izlenmemekte", r"saptanmadi", r"\bdegil\b",
    r"gozlenmemekte", r"mevcut degil", r"eslik etmiyor", r"\bizlenmedi\b",
    # hr / sr / bs
    r"\bnema\b", r"\bbez\b", r"\bnisu\b", r"\bnije\b",
    # el (accents already stripped)
    r"\bδεν\b", r"\bχωρις\b", r"ουδεν",
    # bg / ru
    r"\bбез\b", r"\bне\b", r"липсва", r"\bняма\b",
)

NORMALITY = _rx(
    r"\bnormal", r"\bintact\b", r"\bpreserved\b", r"\bwithin normal limits\b",
    r"limites normales", r"\bconservad", r"\bintegr", r"\bnormales\b",
    r"\bdoga(l|ll)\b", r"korunmus", r"\bnormaldir\b", r"olagan",
    r"\buredn", r"\bocuvan", r"\bodrzan", r"\bintakt",
    r"φυσιολογικ", r"ακεραι",
    r"unauffallig", r"regelrecht", r"\bintakt\b",
    r"нормал", r"запазен", r"съхранен", r"\bбез особености\b",
    r"\bgaaf\b", r"\bnormaal\b",
)

UNCERTAIN = _rx(
    r"\bpossible\b", r"\bprobable\b", r"\bsuspicious\b", r"\bsuspected\b",
    r"cannot (be )?exclude", r"\bmay\b", r"\bquestionable\b", r"\bequivocal\b",
    r"\bposible\b", r"sin criterios categoricos", r"\bdudos",
    r"\bmuhtemel\b", r"\bolasi\b", r"\bsupheli\b", r"\bizlenim",
    r"\bmoguce\b", r"\bvjerojatno\b", r"\bsumnja\b",
    r"πιθαν", r"υποπτ",
    r"\bmoglich", r"\bverdachtig", r"\bfraglich", r"\bV\.a\.\b",
    r"\bвъзможно\b", r"\bвероятно\b", r"суспект",
    r"\bmogelijk\b", r"\bverdacht\b",
)

# Pathology vocabulary shared by the paired rules.
TEAR = _rx(
    r"\btear", r"\btorn\b", r"\brupture", r"\bdisruption\b", r"discontinuit",
    r"\bavuls",
    r"\brotura\b", r"\broturas\b", r"\bruptura", r"\bdesgarro", r"\broto\b",
    r"\bdechirure", r"\bdechire",
    r"\bscheur", r"\bruptuur", r"gescheurd",
    r"riss(bildung|e|es)?\b", r"einriss", r"\bruptur", r"zerreiss", r"\blasion",
    r"\byirtik", r"\byirtig", r"\bkopma\b", r"butunluk kaybi", r"\brupturu\b",
    r"\bpuknuce", r"\bruptur", r"\bprekid\b", r"\bpukotin",
    r"ρηξη", r"ρηξις", r"ρηγμα",
    r"руптура", r"разкъсв", r"разрив", r"скъсв",
)

DEGEN = _rx(
    r"degenerat", r"\bmucoid\b", r"\bmyxoid\b", r"\bfray", r"\bfissur",
    r"dejeneratif", r"\bmukoid\b", r"degenerativn", r"εκφυλ", r"дегенерат",
    r"\bμυξοειδ", r"\bμυξωδ",
    r"\bmuco ?ide\b", r"aufgefasert",
)

INJURY = _rx(
    r"\binjur", r"\bsprain", r"\blesion", r"\blasion", r"\bedema\b", r"\boedema\b",
    r"\bodem\b", r"\bedem\b", r"\bοιδημα", r"\bодем", r"\bедем", r"\bstrain\b",
    r"\bhigh signal\b", r"\bsignal alteration\b", r"\bhiperintens", r"\bhyperintens",
    r"aumento de senal", r"alteracion de senal", r"cambio de senal",
    r"\bsignalanhebung", r"\bsignalalteration", r"verhoogd signaal", r"sinyal artis",
    r"αυξημενο σημα", r"повишен сигнал",
    r"\bthicken", r"\bzadebljanje\b", r"\bverdikking\b", r"\bdistenzij",
    r"\blaksite\b", r"\blaxity\b", r"\bpartial\b", r"\bparcijaln", r"\bparcial",
    r"\bpartiel", r"\bpartiell",
)


ANAT = {
    "ACL": _rx(
        r"anterior cruciate", r"\bacl\b",
        r"cruzado anterior", r"\blca\b",
        r"croise anterieur",
        r"voorste kruisband", r"\bvkb\b",
        r"vorderes kreuzband", r"vorderen kreuzband", r"vordere kreuzband",
        r"on capraz", r"\bocb\b",
        r"prednji krizni", r"prednjeg krizn",
        r"προσθι[οα][^ ]* χιαστ", r"προσθιου χιαστου", r"χιαστο[^ ]* συνδεσμ",
        # "χιαστοι και πλαγιοι συνδεσμοι" separates the adjective from its noun, so the
        # adjective stem has to stand alone. Greek marks cruciate with it unambiguously.
        r"\bχιαστ\w*",
        r"предна кръстна", r"предната кръстна",
        # Plural, unqualified: reports routinely clear both cruciates in one clause
        # ("Ligamentos cruzados y colaterales dentro de limites normales"), so the
        # plural form has to match without a side qualifier or the whole clause is lost.
        r"cruciate ligaments", r"ligamentos cruzados", r"ligaments croises",
        r"kruisbanden", r"kreuzbander", r"capraz baglar", r"krizn[a-z]* ligament[a-z]*",
        r"χιαστοι συνδεσμ", r"χιαστων συνδεσμ", r"кръстните връзки", r"кръстни връзки",
    ),
    "MCL": _rx(
        r"medial collateral", r"\bmcl\b", r"tibial collateral",
        r"colateral medial", r"colateral interno", r"\blcm\b",
        r"collateral medial", r"collateral interne",
        r"mediale collaterale", r"binnenband", r"\b(mediale|laterale) banden\b",
        r"\bcollaterale banden\b",
        r"innenband", r"mediales? kollateral",
        r"\bic yan bag", r"medial kollateral", r"\biyb\b",
        r"medijalni kolateraln", r"medijalnog kolateraln",
        r"εσω πλαγι", r"εσωτερικο πλαγι", r"\bπλαγι\w* συνδεσμ", r"\bπλαγιοι\b",
        r"медиален колатерал", r"вътрешна странична", r"\bколатерал\w*",
        # Same plural pattern as the cruciates.
        # "Ligamentos cruzados y colaterales" separates the noun from its adjective, so
        # the adjective has to stand alone as a cue.
        r"\bcolaterales\b", r"\bcollateraux\b", r"\bcollateralen\b", r"\bkolateralni\b",
        r"collateral ligaments", r"ligamentos colaterales", r"ligaments collateraux",
        r"collaterale banden", r"kollateralbander", r"seitenbander", r"yan baglar",
        r"kolateraln[a-z]* ligament[a-z]*", r"πλαγιοι συνδεσμ", r"πλαγιων συνδεσμ",
        r"колатерални връзки", r"страничните връзки",
    ),
    "Medial Meniscus": _rx(
        r"medial meniscus", r"\bmm\b(?= tear)", r"medial menisc",
        r"menisco medial", r"menisco interno",
        r"menisque medial", r"menisque interne",
        r"mediale meniscus", r"binnenmeniscus",
        r"innenmeniskus", r"medialen? meniskus", r"innenmeniskushinterhorn",
        r"medyal menisk", r"\bic menisk",
        r"medijalni meniskus", r"medijalnog meniskusa", r"medijalnom meniskusu",
        r"εσω μηνισκ", r"μηνισκ[^ ]* του εσω", r"εσω διαμερισμα[^.]{0,40}μηνισκ",
        r"медиалния менискус", r"медиален менискус", r"вътрешния менискус",
    ),
    "Lateral Meniscus": _rx(
        r"lateral meniscus", r"lateral menisc",
        r"menisco lateral", r"menisco externo",
        r"menisque lateral", r"menisque externe",
        r"laterale meniscus", r"buitenmeniscus",
        r"aussenmeniskus", r"lateralen? meniskus",
        r"lateral menisk", r"\bdis menisk",
        r"lateralni meniskus", r"lateralnog meniskusa", r"lateralnom meniskusu",
        r"εξω μηνισκ", r"μηνισκ[^ ]* του εξω", r"εξω διαμερισμα[^.]{0,40}μηνισκ",
        r"латералния менискус", r"латерален менискус", r"външния менискус",
    ),
}

# Osteoarthritis is rarely written as "osteoarthritis". It is written as cartilage loss,
# chondropathy grade, joint space narrowing, or osteophytes - scoped to a compartment.
OA_EVIDENCE = _rx(
    r"osteoarthrit", r"\barthros", r"\bgonarthros", r"\bosteoarthros",
    r"chondropath", r"chondromalac", r"condropat", r"condromalac",
    r"cartilage loss", r"cartilage thinning", r"chondral (loss|defect|ulcer|thinning)",
    r"osteophyt", r"osteofit", r"osteofyt", r"osteofito", r"osteophyten",
    r"joint space narrowing", r"pinzamiento articular",
    r"kikirdak kayb", r"kikirdak incelme", r"kondropati", r"kondral",
    r"kraakbeen(lijden|verlies)", r"gonartrose", r"artrose",
    r"knorpel(verlust|schaden|defekt)", r"arthrose", r"gonarthrose",
    r"hrskavic", r"hondromalac", r"artroz", r"osteoartrit",
    r"χονδρ[^ ]*παθ", r"αρθριτ", r"αρθρωσ", r"οστεοφυτ",
    r"αρθρικου χονδρου", r"εξαλειψη του αρθρικου χονδρου",
    r"артроз", r"хондропат", r"остеофит", r"хрущял[^.]{0,30}(изтън|увред|дефект)",
    r"ulcera[s]? condral", r"cartilago[^.]{0,25}(perdida|adelgaz)",
    r"icrs grade", r"outerbridge",
)

COMPARTMENT = {
    "Medial OA": _rx(
        r"medial (femorotibial|tibiofemoral|compartment)",
        r"compartimento femorotibial medial", r"femorotibial interno",
        r"mediaal femorotibiaal", r"mediale femorotibial",
        r"medial femorotibial", r"medialen kompartiment", r"innere[sn]? kompartiment",
        r"medyal femorotibial", r"ic kompartman", r"medyal kompartman",
        r"medijaln[^ ]* (femorotibi|odjelj|kompartm)",
        r"εσω διαμερισμα", r"εσω κνημιαι", r"εσω μηριαι",
        r"медиалн[^ ]* (компартм|отдел|тибиал|феморотиб)",
        r"medial (femoral|tibial) (condyle|plateau)", r"condilo femoral medial",
        r"medialen? (femurkondyl|tibiaplateau)", r"mediale femorale condyl",
    ),
    "Lateral OA": _rx(
        r"lateral (femorotibial|tibiofemoral|compartment)",
        r"compartimento femorotibial lateral", r"femorotibial externo",
        r"lateraal femorotibiaal", r"laterale femorotibial",
        r"lateral femorotibial", r"lateralen kompartiment", r"aussere[sn]? kompartiment",
        r"lateral femorotibial", r"dis kompartman", r"lateral kompartman",
        r"lateraln[^ ]* (femorotibi|odjelj|kompartm)",
        r"εξω διαμερισμα", r"εξω κνημιαι", r"εξω μηριαι",
        r"латералн[^ ]* (компартм|отдел|тибиал|феморотиб)",
        r"lateral (femoral|tibial) (condyle|plateau)", r"condilo femoral lateral",
        r"lateralen? (femurkondyl|tibiaplateau)", r"laterale femorale condyl",
    ),
    "PF OA": _rx(
        r"patellofemoral", r"femoropatellar", r"femoropatelar", r"patelofemoral",
        r"retropatellar", r"retrorotulian", r"\btrochlea", r"\btroclea", r"\btroklea",
        r"\bpatella\b", r"\bpatellar\b", r"\brotulian", r"\brotula\b", r"\bpatele\b",
        r"\bpatellae?\b", r"patellofemoraal", r"femoropatellair",
        r"επιγονατιδ", r"μηροεπιγονατιδ", r"τροχιλ",
        r"пател", r"феморопател", r"тролх",
        r"anterior compartment", r"compartimento anterior", r"prednj[^ ]* odjeljk",
    ),
}

# Self-declaring findings: the term itself is the finding.
DIRECT = {
    "Effusion": _rx(
        r"\beffusion", r"joint fluid", r"intra ?articular fluid", r"\bhydrops\b",
        r"derrame articular", r"\bderrame\b", r"liquido articular",
        r"epanchement",
        r"gewrichtsvocht", r"\bvocht\b", r"\bhydrops\b", r"gewrichtseffusie",
        r"gelenkerguss", r"\berguss\b", r"gelenksergu",
        # "diz eklemi ici sivi miktari ... artmis" and "eklem icerisinde yaygin sivi
        # artisi" both occur; the noun takes a possessive suffix, so `eklem ` alone
        # misses. Match the stem plus any suffix.
        r"eklem\w* ic\w* sivi", r"efuzyon", r"eklem sivisi",
        r"sivi (miktari|artisi|birikimi)", r"sivi artis", r"\bsivi\b[^.]{0,25}artmis",
        r"\bizljev", r"\bizliv", r"zglobn[^ ]* tekucin", r"\bhidrops\b",
        r"αρθρικ[^ ]* υγρ", r"υγρου ενδαρθρικα", r"ενδαρθρικ[^ ]* υγρ", r"ποσοτητα υγρου",
        r"ενδαρθρικ", r"αρθρικη συλλογη", r"υγρο στην αρθρωση", r"υγρου στην αρθρωση",
        r"ставен излив", r"излив", r"ставна течност", r"синовиална течност",
    ),
    "Synovitis": _rx(
        r"synovit", r"sinovit", r"synovial (thickening|proliferation|hypertroph)",
        r"synovitis", r"synoviale? (verdikking|proliferatie)",
        r"synovialitis", r"synovialis(verdickung|proliferation)",
        r"sinovijalitis", r"sinovitis", r"zadebljanje sinovij",
        r"υμενιτιδα", r"συνοβιτιδα", r"υμενικ[^ ]* υπερτροφ", r"αρθρικου υμεν",
        r"синовит", r"синовиал[^ ]* (задебел|пролифер)",
        r"verdikkingen van (het )?synovium", r"pannus",
    ),
    "Baker's": _rx(
        r"baker", r"popliteal cyst", r"quiste popliteo", r"quistes popliteos",
        r"kyste poplite", r"popliteale? cyst", r"poplitealzyste", r"bakerzyste",
        r"popliteal kist", r"\bbakerova\b", r"poplitealn[^ ]* cist",
        r"κυστη baker", r"πολυχωρη συνοβιακη κυστη", r"κυστη του baker",
        r"киста на бейкър", r"бейкърова киста", r"поплитеална киста",
        r"gastrocnemio ?semimembranos", r"gastrocnemius semimembranosus burs",
    ),
    "Contusion": _rx(
        r"\bcontusion", r"bone bruise", r"bone marrow (o?edema|contusion)",
        r"\bkontuz", r"medular bone o?edema", r"marrow o?edema",
        r"contusion osea", r"edema oseo", r"edema de medula osea",
        r"oedeme osseux", r"contusion osseuse",
        r"botcontusie", r"botoedeem", r"beenmergoedeem", r"botmergoedeem",
        r"knochenmarkodem", r"knochenodem", r"kontusion", r"bone bruise",
        r"kemik kontuzyonu", r"kemik iligi odemi", r"kemik odemi",
        r"kostani edem", r"edem kosti", r"kontuzij",
        r"οστεομυελικ[^ ]* οιδημα", r"οστικο οιδημα", r"μυελικο οιδημα",
        r"костномозъчен едем", r"костен едем", r"контузионен",
    ),
    "Fracture": _rx(
        r"\bfractur", r"\bfract\b",
        r"\bfractura", r"\bfracturas\b",
        r"\bfractuur", r"\bbreuk\b",
        r"\bfraktur", r"\bbruch\b",
        r"\bkirik\b", r"\bkirigi\b", r"\bkirik\b",
        r"\bfraktur", r"\bprijelom", r"impresijsk[^ ]* fraktur",
        r"καταγμα", r"καταγματ",
        r"фрактур", r"счупван", r"фисур",
        r"insufficiency fracture", r"stress fracture", r"avulsion fracture",
        r"subchondral fracture", r"subkondral kiri",
    ),
}

# Terms that look like a finding but are not the finding being scored.
DECOY = {
    # `no fracture` is deliberately absent: a decoy skips the clause, so listing it here
    # turned the commonest English denial into silence, and the study then pulled on the
    # fracture head with the weight of a report that never mentioned fractures at all.
    # `microfractur` is a surgical procedure and `fracture risk` a prediction; both stay.
    "Fracture": _rx(r"microfractur", r"\bfracture (risk|prophyla)"),
    "Baker's": _rx(r"meniscal cyst", r"quiste meniscal", r"ganglion"),
}

PAIRED = {"ACL", "MCL", "Medial Meniscus", "Lateral Meniscus"}
OA_TARGETS = {"Medial OA", "Lateral OA", "PF OA"}


STEM_MENISCUS = _rx(r"menisc\w*", r"menisk\w*", r"μηνισκ\w*", r"мениск\w*")
STEM_CRUCIATE = _rx(r"cruciate", r"cruzado", r"croise", r"kruisband", r"kreuzband",
                    r"capraz bag\w*", r"krizn\w*", r"χιαστ\w*", r"кръстн\w*",
                    r"\bacl\b", r"\bpcl\b", r"\blca\b", r"\blcp\b", r"\bvkb\b",
                    r"\bhkb\b", r"\bocb\b", r"\bacb\b")
STEM_COLLATERAL = _rx(r"collateral\w*", r"colateral\w*", r"kollateral\w*",
                      r"collaterale\w*", r"kolateraln\w*", r"yan bag\w*",
                      r"πλαγι\w*", r"колатерал\w*", r"странич\w*",
                      r"innenband\w*", r"aussenband\w*", r"binnenband\w*",
                      r"\bmcl\b", r"\blcl\b", r"\blcm\b", r"\biyb\b")

SIDE_MEDIAL = _rx(r"\bmedial\w*", r"\bmedyal\w*", r"\bmedijaln\w*", r"\bmediaal\w*",
                  r"\bmediale\w*", r"\bintern[oa]\w*", r"\binterne\w*", r"\binnen\w*",
                  r"\bic\b", r"\bunutarnj\w*", r"\bεσω\w*", r"\bεσωτερικ\w*",
                  r"\bмедиал\w*", r"\bвътреш\w*", r"\btibial collateral\b",
                  r"\bbinnen\w*", r"\bmediaal\b")
SIDE_LATERAL = _rx(r"\blateral\w*", r"\bextern[oa]\w*", r"\bexterne\w*", r"\bdis\b",
                   r"\blateraln\w*", r"\baussen\w*", r"\bbuiten\w*", r"\bεξω\w*",
                   r"\bεξωτερικ\w*", r"\bлатерал\w*", r"\bвъншн\w*",
                   r"\bfibular collateral\b", r"\bvanjsk\w*")
SIDE_ANTERIOR = _rx(r"\banterior\w*", r"\bant\b", r"\bon\b", r"\bprednj\w*",
                    r"\bvorder\w*", r"\bvoorste\b", r"\bπροσθι\w*", r"\bпредн\w*",
                    r"\banteriyor\w*", r"\bavant\b", r"\bant[eé]rieur\w*")

# The contrary of SIDE_ANTERIOR, needed only to stop a side-blind cruciate cue firing on
# the posterior ligament. It is never used to assert a target - there is no PCL target -
# so it is deliberately narrow: `posterior horn` is one of the commonest phrases in a
# knee report and must not be read as a cruciate qualifier, which is why the guard below
# tests proximity to the cruciate stem rather than presence in the clause.
SIDE_POSTERIOR = _rx(r"\bposterior\w*", r"\bpost[eé]rieur\w*", r"\bposteriore\w*",
                     r"\bhinter\w*", r"\bachterste\b", r"\barka\b", r"\bstraznj\w*",
                     r"\bzadnj\w*", r"\bοπισθι\w*", r"\bзадн\w*", r"\bpostero\w*")

# Fracture is the target whose stem varies most across the corpus.
STEM_FRACTURE = _rx(r"fractur\w*", r"fraktur\w*", r"fractuur\w*", r"\bfract\b",
                    r"kiri[kgğ]\w*", r"prijelom\w*", r"lom kosti", r"\bbreuk\w*",
                    r"\bbruch\w*", r"καταγμα\w*", r"καταγματ\w*", r"фрактур\w*",
                    # NOT a bare `fissur\w*`: "fisuras condrales" and "full thickness
                    # fissures in the articular cartilage" describe cartilage, not bone.
                    # The stem has to be anchored to a bone word to mean a fracture.
                    r"счупван\w*", r"fisur\w* (osea|oseas|kost)", r"fissur\w* kost")

STEM_OA_COMPARTMENT = _rx(r"compartment\w*", r"compartimento\w*", r"compartiment\w*",
                          r"kompartman\w*", r"kompartiment\w*", r"odjelj\w*",
                          r"διαμερισμα\w*", r"компартм\w*", r"\bотдел\w*",
                          r"femorotibial\w*", r"femorotibiaal\w*", r"tibiofemoral\w*",
                          r"femoro tibial\w*", r"κνημιαι\w*", r"μηριαι\w*",
                          r"femoral condyl\w*", r"tibial plateau\w*",
                          r"condilo femoral", r"platillo tibial", r"tibiaplateau\w*",
                          r"femurkondyl\w*", r"femoralne? kondil\w*",
                          r"tibijaln\w* plato", r"femoral kondil\w*",
                          r"tibia plato", r"tibyal plato")


def _distance(clause: str, stem_rx: re.Pattern, qual_rx: re.Pattern, window: int = 55):
    """Characters from the nearest stem to the nearest qualifier, or None if none is near.

    Character windows rather than token windows, because word order differs: English
    puts the side before the noun, Greek and Bulgarian often after, and Turkish
    attaches it as a separate preceding adjective.

    A distance rather than a yes. Presence is enough to decide that a qualifier applies
    to a structure, but not enough to decide which of two qualifiers applies: a knee
    report says "anterior horn" and "posterior horn" constantly, so any window wide
    enough to catch a real side word also catches an unrelated one, and two rules that
    both answer "yes" cannot be told apart. Comparing how far away they are can.
    """
    best = None
    for m in stem_rx.finditer(clause):
        lo = max(0, m.start() - window)
        hi = min(len(clause), m.end() + window)
        for q in qual_rx.finditer(clause[lo:hi]):
            qs, qe = lo + q.start(), lo + q.end()
            d = 0 if qs < m.end() and qe > m.start() else \
                min(abs(m.start() - qe), abs(qs - m.end()))
            best = d if best is None else min(best, d)
    return best


def _near(clause: str, stem_rx: re.Pattern, qual_rx: re.Pattern, window: int = 55):
    """True if a stem match has a qualifier within `window` characters either side."""
    return _distance(clause, stem_rx, qual_rx, window) is not None
    return False


# concept -> (stem, side) pairs used in addition to the phrase lexicons above
STEM_RULES = {
    "ACL": (STEM_CRUCIATE, SIDE_ANTERIOR),
    "MCL": (STEM_COLLATERAL, SIDE_MEDIAL),
    "Medial Meniscus": (STEM_MENISCUS, SIDE_MEDIAL),
    "Lateral Meniscus": (STEM_MENISCUS, SIDE_LATERAL),
    "Medial OA": (STEM_OA_COMPARTMENT, SIDE_MEDIAL),
    "Lateral OA": (STEM_OA_COMPARTMENT, SIDE_LATERAL),
}


SEV_LOW = _rx(
    r"\bsmall\b", r"\bminimal\b", r"\btrace\b", r"\bmild\b", r"\bslight\b",
    r"\btiny\b", r"\bscant\b", r"\bmimimal\b", r"\bdiscrete\b", r"\bfocal\b",
    r"\bleve\b", r"\bminim", r"\bpeque", r"\bligero\b", r"\bescaso\b", r"\bdiscreto\b",
    r"\bhafif\b", r"\bminimal\b", r"\baz miktarda\b", r"\bsilik\b",
    r"\bmanja\b", r"\bmanji\b", r"\bblago\b", r"\bdiskretn", r"\bmalo\b",
    r"\bgering", r"\bdiskret", r"\bkleine?r?\b", r"\bwenig\b", r"\bzarte?\b",
    r"\bbeperkte?\b", r"\bgeringe\b", r"\bweinig\b", r"\blichte?\b",
    r"\bηπι", r"\bμικρ", r"\bελαχιστ",
    r"\bминимал", r"\bлек", r"\bмалк", r"\bнеголям",
)

SEV_HIGH = _rx(
    r"\blarge\b", r"\bmarked\b", r"\bmassive\b", r"\bsevere\b", r"\bextensive\b",
    r"\bmoderate\b", r"\bgross\b", r"\bsignificant\b", r"\babundant\b", r"\btense\b",
    r"\bmoderad", r"\bimportante\b", r"\bsevera?\b", r"\bmarcad", r"\bcuantios",
    r"\bbelirgin\b", r"\byaygin\b", r"\bileri\b", r"\bciddi\b", r"\bbol\b",
    r"\bopsezan\b", r"\bveliki\b", r"\bizrazit", r"\bznacajn", r"\bumjeren",
    r"\bausgepragt", r"\bdeutlich", r"\bmassiv", r"\bmassig", r"\bgross",
    r"\buitgebreid", r"\bgevorderd", r"\bveel\b", r"\bmatige?\b",
    r"\bμετρι", r"\bμεγαλ", r"\bεκτεταμεν", r"\bευμεγεθ", r"\bσοβαρ",
    r"\bголям", r"\bизразен", r"\bзначим", r"\bумерен", r"\bобилен",
)

# OA is often asserted for the whole joint rather than per compartment
# ("tricompartmental osteoarthritis", "gonarthrose", "incipient OA of all three
# compartments"). Those statements are evidence for all three OA targets.
GLOBAL_OA = _rx(
    r"tri ?compartment", r"all three compartment", r"global(ised)? (oa|osteoarthrit)",
    r"\bgonarthros", r"\bgonartros", r"\bgonarthrose", r"\bgonartrose",
    r"osteoarthritis of the knee", r"artrosis (de |)(la )?rodilla", r"knee osteoarthrit",
    r"\bdiz osteoartrit", r"\bgonartroz", r"artroza koljena",
    r"οστεοαρθριτιδα", r"αρθριτιδα του γονατος",
    r"артроза на колянната", r"гонартроз",
    r"degenerative joint disease", r"\bdjd\b",
)

# A bare "bone marrow oedema" is not a contusion when it sits under a cartilage
# defect: subchondral oedema beneath a worn compartment is reactive degenerative signal,
# and reading it as a bruise turns every osteoarthritic knee into a trauma case.
DEGENERATIVE_MARROW = _rx(
    r"subchondral", r"subcondral", r"subkondral", r"supkondraln", r"subchondraln",
    r"υποχονδρι", r"субхондрал", r"subchondrale?",
    r"\bcyst", r"\bquist", r"\bzyste\b", r"\bcistic", r"reactive", r"reactivo",
)

TRAUMA = _rx(
    r"\bbruise\b", r"\bcontusion", r"\bkontuz", r"\bcontusion osea\b",
    r"\btrauma", r"\bimpaction\b", r"\bpivot shift\b", r"\bkissing\b",
    r"\bacute\b", r"\bagudo\b", r"\bakut", r"\bpivot kaymasi\b",
    r"\bcontusion osseuse\b", r"\bbone bruise\b", r"\bbotcontusie\b",
    r"\bконтузион", r"\bμωλωπ", r"\bkontuzij",
)


def _polarity(clause: str, anchor_end: int) -> str:
    """Classify one clause as positive, negative or uncertain for a matched term.

    Scope is the whole clause. Clause segmentation already keeps statements short, and
    a window in characters mis-scopes badly across languages with different word orders -
    Turkish puts its negator at the end of the sentence, English at the front.
    """
    if UNCERTAIN.search(clause):
        return "uncertain"
    if NEGATION.search(clause):
        return "negative"
    if NORMALITY.search(clause):
        # "meniscus normal" negates; "normal ... but tear" does not.
        if TEAR.search(clause) or re.search(r"\bgrade [34]\b", clause):
            return "positive"
        return "negative"
    return "positive"


class _Matcher:
    """Phrase lexicon first, stem+side proximity as the fallback.

    Exposes `.search` so it drops into the same slot as a compiled pattern.
    """

    def __init__(self, phrase_rx, stem=None, side=None, window=55, contrary=None):
        self.phrase_rx = phrase_rx
        self.stem = stem
        self.side = side
        self.window = window
        self.contrary = contrary

    def search(self, clause):
        m = self.phrase_rx.search(clause)
        if m is not None and not self._wrong_side(clause):
            return m
        if self.stem is not None and _near(clause, self.stem, self.side, self.window):
            return self.stem.search(clause)
        return None

    def _wrong_side(self, clause):
        """True when the clause names the other member of this structure's pair.

        Some cues in the lexicon are side-blind by design: Greek separates the adjective
        from its noun ("cruciate and collateral ligaments"), so the bare adjective stem
        has to stand alone or the clause is lost. That stem then also matches the
        posterior cruciate and the lateral collateral, neither of which is a target here,
        and a positive outranks every negative in the scorer - so one PCL clause was
        enough to override an explicit "the ACL is normal".

        The test is proximity to the structure's own stem, not presence in the clause.
        "Posterior horn of the medial meniscus" appears in a large share of knee reports
        and says nothing about a cruciate; only a qualifier sitting beside the ligament
        word is one. A clause naming both sides keeps the match, because it does mention
        this target.
        """
        if self.contrary is None or self.stem is None:
            return False
        other = _distance(clause, self.stem, self.contrary, self.window)
        if other is None:
            return False
        own = _distance(clause, self.stem, self.side, self.window)
        # Not "is the other side mentioned" but "is it the nearer of the two". A clause
        # reading "tear of the posterior horn of the medial meniscus; the cruciate
        # ligaments are intact" mentions posterior, and under a presence test that was
        # enough to suppress the cruciate cue - which is the opposite of the intent,
        # since the clause does describe the ligaments. Ties go to keeping the match:
        # a clause naming both sides does mention this one.
        return own is None or other < own


# Which cue, if it sits beside the structure's stem, means the clause is about the other
# member of the pair. Only the two structures with a side-blind cue need one.
CONTRARY = {"ACL": SIDE_POSTERIOR, "MCL": SIDE_LATERAL}

ANAT_MATCH = {
    tgt: _Matcher(ANAT[tgt], *STEM_RULES[tgt], contrary=CONTRARY.get(tgt))
    for tgt in PAIRED
}
COMPARTMENT_MATCH = {
    "Medial OA": _Matcher(COMPARTMENT["Medial OA"], *STEM_RULES["Medial OA"]),
    "Lateral OA": _Matcher(COMPARTMENT["Lateral OA"], *STEM_RULES["Lateral OA"]),
    "PF OA": _Matcher(COMPARTMENT["PF OA"]),
}
DIRECT_MATCH = {
    tgt: _Matcher(_rx(rx.pattern, STEM_FRACTURE.pattern) if tgt == "Fracture" else rx)
    for tgt, rx in DIRECT.items()
}


def _severity(clause: str) -> float:
    """Weight one positive mention by how emphatic the sentence is.

    Ordered, not calibrated. A "moderate effusion" must outrank a "trace effusion" and
    both must outrank silence; the absolute numbers do not matter to AUC.
    """
    high = SEV_HIGH.search(clause) is not None
    low = SEV_LOW.search(clause) is not None
    if high and not low:
        return 1.0
    if low and not high:
        return 0.45
    return 0.75                       # unqualified mention


def _score_clauses(cls, anat_rx, path_rx=None, decoy_rx=None, context_penalty=None,
                   context_bonus=None):
    """Accumulate graded evidence over clauses for one target.

    Returns (score, confidence, n_pos, n_neg). Positives are graded by severity and by
    optional context regexes; negatives only matter when nothing positive was found,
    because reports assert normality for every structure they check.
    """
    n_pos = n_neg = n_unc = 0
    best = 0.0
    for c in cls:
        m = anat_rx.search(c)
        if not m:
            continue
        if decoy_rx is not None and decoy_rx.search(c):
            continue
        if path_rx is not None and not path_rx.search(c):
            if NORMALITY.search(c) and not NEGATION.search(c):
                n_neg += 1
            continue
        pol = _polarity(c, m.end())
        if pol == "positive":
            n_pos += 1
            w = _severity(c)
            if context_penalty is not None and context_penalty.search(c):
                w *= 0.45
            if context_bonus is not None and context_bonus.search(c):
                w = min(1.0, w * 1.35)
            best = max(best, w)
        elif pol == "negative":
            n_neg += 1
        else:
            n_unc += 1
            best = max(best, 0.30)

    if n_pos or n_unc:
        # 0.52 .. 0.95, ordered by the strongest single mention, nudged by repetition.
        score = min(0.95, 0.50 + 0.42 * best + 0.03 * min(n_pos, 3))
        conf = min(1.0, 0.55 + 0.15 * n_pos)
    elif n_neg:
        score = max(0.04, 0.20 - 0.04 * n_neg)
        conf = min(0.9, 0.45 + 0.12 * n_neg)
    else:
        score, conf = 0.28, 0.05          # silence sits above asserted-negative
    return score, conf, n_pos, n_neg


def extract(report: str) -> dict:
    """Extract twelve (score, confidence) pairs from one report."""
    cls = clauses(report)
    out = {}
    path_paired = _rx(TEAR.pattern, DEGEN.pattern, INJURY.pattern)

    for tgt in TARGETS:
        if tgt in PAIRED:
            s, c, npos, nneg = _score_clauses(cls, ANAT_MATCH[tgt], path_paired)
        elif tgt in OA_TARGETS:
            s, c, npos, nneg = _score_clauses(cls, COMPARTMENT_MATCH[tgt], OA_EVIDENCE)
        elif tgt == "Contusion":
            # Reactive subchondral oedema under a cartilage defect is osteoarthritis,
            # not a bruise. Explicit trauma wording pushes the other way.
            s, c, npos, nneg = _score_clauses(cls, DIRECT_MATCH[tgt], None, DECOY.get(tgt),
                                              context_penalty=DEGENERATIVE_MARROW,
                                              context_bonus=TRAUMA)
        else:
            s, c, npos, nneg = _score_clauses(cls, DIRECT_MATCH[tgt], None, DECOY.get(tgt))
        out[tgt] = s
        out[tgt + "__conf"] = c
        out[tgt + "__npos"] = npos
        out[tgt + "__nneg"] = nneg

    # --- cross-target corrections ------------------------------------------ #
    # A whole-joint osteoarthritis statement is evidence for every compartment that was
    # not separately assessed. Without this, "incipient OA of all three compartments"
    # scores zero on all three OA targets.
    g_hits = [c for c in cls if GLOBAL_OA.search(c) and _polarity(c, 0) == "positive"]
    if g_hits:
        gscore = 0.50 + 0.42 * max(_severity(c) for c in g_hits)
        for tgt in OA_TARGETS:
            if out[tgt + "__npos"] == 0 and out[tgt + "__nneg"] == 0:
                out[tgt] = max(out[tgt], gscore * 0.92)
                out[tgt + "__conf"] = max(out[tgt + "__conf"], 0.4)

    # Synovitis is frequently visible on the images and absent from the text, so silence
    # is weak evidence of absence here in a way it is not for other findings. Effusion is
    # its most reliable textual proxy - the two share a mechanism - so a silent synovitis
    # inherits a fraction of the effusion evidence instead of falling to the floor.
    if out["Synovitis__npos"] == 0 and out["Synovitis__nneg"] == 0:
        out["Synovitis"] = max(out["Synovitis"], 0.28 + 0.45 * (out["Effusion"] - 0.28))

    return out


# ================= 集成 API(本仓库新增,非移植代码) =================


def report_score_to_target(res: dict, tgt: str):
    """把 extract() 的一个目标结果映射为 BCE soft 目标(或 NaN)。

    n_pos>0 -> 证据分数(阳性,0.72~0.95)
    n_pos==0 且 n_neg>0 -> 证据分数(阴性,0.04~0.20)
    其余(沉默/不确定)-> NaN:该格不进损失
    """
    npos = res.get(tgt + "__npos", 0)
    nneg = res.get(tgt + "__nneg", 0)
    if npos > 0:
        return float(res[tgt])
    if nneg > 0:
        return float(res[tgt])
    return float("nan")


def _extract_cached(reports):
    return [extract(r) for r in reports]


def build_pseudo_table(train_df, report_col="Report", verbose=True):
    """从 train_df 的放射报告生成伪标签表(StudyInstanceUID + pseudo_<12>)。

    返回 DataFrame;分数列 float,无证据格为 NaN。
    官方 gold 由 load_labels 优先覆盖,此处不掺和。
    """
    reports = train_df[report_col].fillna("").tolist()
    uids = train_df["StudyInstanceUID"].tolist()
    res = _extract_cached(reports)
    rows = {}
    cnt = {t: [0, 0, 0] for t in TARGETS}   # [pos, neg, nan]
    for t in TARGETS:
        vals = []
        for r in res:
            v = report_score_to_target(r, t)
            if pd.isna(v):
                cnt[t][2] += 1
            elif v > 0.5:
                cnt[t][0] += 1
            else:
                cnt[t][1] += 1
            vals.append(v)
        rows["pseudo_" + t] = vals
    out = pd.DataFrame({"StudyInstanceUID": uids, **rows})
    if verbose:
        print(f"[标签] 报告抽取器(rsna_report_labels):{len(uids)} study,"
              f"零挂载纯 CPU;每病灶 pos/neg/无证据:")
        for t in TARGETS:
            p, n, z = cnt[t]
            print(f"  {t:18s} pos={p:5d} neg={n:5d} 无证据={z:5d}"
                  f" 覆盖={(p+n)/len(uids)*100:5.1f}%")
    return out


if __name__ == "__main__":
    # CPU sanity:python rsna_report_labels.py
    df = pd.read_csv("train.csv", nrows=200)
    tab = build_pseudo_table(df, verbose=True)
    print(tab.head(6).to_string())
