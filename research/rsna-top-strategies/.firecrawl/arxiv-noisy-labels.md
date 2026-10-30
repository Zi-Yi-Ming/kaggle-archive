Title:

Content selection saved. Describe the issue below:

Description:

![](https://arxiv.org/static/base/1.0.1/images/icons/smileybones-small.svg)arXiv is now an independent nonprofit! [Learn more](https://info.arxiv.org/about) ×

[License: arXiv.org perpetual non-exclusive license](https://info.arxiv.org/help/license/index.html#licenses-available)

arXiv:2512.09315v1 \[cs.CV\] 10 Dec 2025

# Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook

Yuan Ma
s2420410@jaist.ac.jp

organization=Japan Advanced Institute of Science and Technology,
city=Nomi,
country=Japan

organization=University College London,
city=London,
country=United Kingdom

organization=The Hong Kong University of Science and Technology,
city=Hong Kong,
country=China

organization=University of Toyama,
city=Toyama,
country=Japan

organization=Monash University,
city=Melbourne,
country=Australia

Junlin Hou
csejlhou@ust.hk
Chao Zhang
zhang@eng.u-toyama.ac.jp
Yukun Zhou
yukun.zhou.19@ucl.ac.uk
Zongyuan Ge
Zongyuan.Ge@monash.edu
Haoran Xie
xie@jaist.ac.jp
Lie Ju
lie.ju@ucl.ac.uk

###### Abstract

Learning from noisy labels remains a major challenge in medical image analysis, where annotation demands expert knowledge and substantial inter-observer variability often leads to inconsistent or erroneous labels.
Despite extensive research on learning with noisy labels (LNL), the robustness of existing methods in medical imaging has not been systematically assessed.
To address this gap, we introduce LNMBench, a comprehensive benchmark for Label Noise in Medical imaging.
LNMBench encompasses 10 representative methods evaluated across 7 datasets, 6 imaging modalities, and 3 noise patterns, establishing a unified and reproducible framework for robustness evaluation under realistic conditions.
Comprehensive experiments reveal that the performance of existing LNL methods degrades substantially under high and real-world noise, highlighting the persistent challenges of class imbalance and domain variability in medical data.
Motivated by these findings, we further propose a simple yet effective improvement to enhance model robustness under such conditions.
The LNMBench codebase is publicly released to facilitate standardized evaluation, promote reproducible research, and provide practical insights for developing noise-resilient algorithms in both research and real-world medical applications.
The codebase is publicly available on https://github.com/myyy777/LNMBench.

###### keywords

Label noise, Benchmark, Retinal diseases, Skin lesions, Thoracic diseases

††corresponding: Corresponding author††These authors contributed equally to this work.

![Refer to caption](https://arxiv.org/html/2512.09315v1/teaser.png)(a)Overview of LNMBench.

(b)Overall rank of LNMBench.

(c)Symmetric noise.

(d)Instance-dependent noise.

(e)Real-world noise.

Figure 1: (a) We present a systematic benchmark for learning with noisy labels in medical image analysis, encompassing 3 noise patterns, 7 datasets from 6 imaging modalities, and 10 representative methods. Integrating both synthetic and real-world noise across balanced and imbalanced datasets, the benchmark provides a unified and reproducible framework that evaluates not only classification accuracy but also robustness-oriented metrics such as estimation error for matrix estimation methods. (b) Overall rank of LNMBench. (c) Overall results of LNL methods under symmetric noise. (d) Overall results of LNL methods under instance-dependent noise. (e) Overall results of LNL methods under real-world noise.

## 1 Introduction

Deep learning has become the dominant paradigm in computer vision because of its ability to learn expressive feature representations from large-scale annotated datasets.
The performance of deep neural networks (DNNs) is heavily dependent on the quality and quantity of annotated data.
As a result, robust learning under label noise has attracted considerable attention.
In recent years, a wide range of LNL methods have been developed \[ [37](https://arxiv.org/html/2512.09315v1#bib.bib37 ""), [38](https://arxiv.org/html/2512.09315v1#bib.bib38 ""), [2](https://arxiv.org/html/2512.09315v1#bib.bib2 ""), [33](https://arxiv.org/html/2512.09315v1#bib.bib33 "")\].
Several works aim to model the label corruption process explicitly, typically by estimating a noise transition matrix that reflects the probability of label flips \[ [46](https://arxiv.org/html/2512.09315v1#bib.bib46 ""), [25](https://arxiv.org/html/2512.09315v1#bib.bib25 "")\].
Robust loss functions and regularization methods have been proposed to reduce the impact of incorrect supervision during optimization \[ [40](https://arxiv.org/html/2512.09315v1#bib.bib40 ""), [30](https://arxiv.org/html/2512.09315v1#bib.bib30 "")\].
A common strategy for LNL is to select potentially clean samples for training, often based on the small-loss criterion, which assumes that clean examples tend to yield lower loss in early training stages \[ [9](https://arxiv.org/html/2512.09315v1#bib.bib9 ""), [49](https://arxiv.org/html/2512.09315v1#bib.bib49 "")\].
In addition, semi-supervised learning methods \[ [24](https://arxiv.org/html/2512.09315v1#bib.bib24 ""), [22](https://arxiv.org/html/2512.09315v1#bib.bib22 "")\] further build upon sample selection by leveraging the selected clean data as labeled examples and treating the remaining uncertain data as unlabeled, thereby improving robustness through consistency regularization and pseudo labeling.
These methods have achieved promising results on natural images but lack a systematic evaluation on medical images.

In medical imaging, label noise is particularly prevalent, as annotation requires specialized expertise, and variations in doctors’ experience as well as inter-annotator variability may result in inconsistent or even incorrect labels.
Therefore, learning from noisy labels has long been recognized as an important problem in medical imaging domain \[ [47](https://arxiv.org/html/2512.09315v1#bib.bib47 ""), [12](https://arxiv.org/html/2512.09315v1#bib.bib12 ""), [34](https://arxiv.org/html/2512.09315v1#bib.bib34 ""), [7](https://arxiv.org/html/2512.09315v1#bib.bib7 ""), [35](https://arxiv.org/html/2512.09315v1#bib.bib35 "")\].
Early studies attempted to address the label noise problem in medical image analysis through noise-robust regularization methods \[ [4](https://arxiv.org/html/2512.09315v1#bib.bib4 ""), [47](https://arxiv.org/html/2512.09315v1#bib.bib47 "")\].
For instance, Dgain et al. \[ [4](https://arxiv.org/html/2512.09315v1#bib.bib4 "")\] proposed a neural network training strategy that explicitly models label noise within the architecture, and demonstrated its effectiveness on breast microcalcification classification from multi-view mammograms, outperforming standard training methods.
In a comprehensive survey, Karimi et al. \[ [18](https://arxiv.org/html/2512.09315v1#bib.bib18 "")\] discussed the challenges posed by label noise in deep learning for medical imaging, emphasizing its prevalence, negative impact on performance, and possible mitigation strategies.
Recently, LNL methods have focused on mitigating the effects of label noise by selecting or weighting samples that are likely to be correctly labeled \[ [15](https://arxiv.org/html/2512.09315v1#bib.bib15 ""), [12](https://arxiv.org/html/2512.09315v1#bib.bib12 ""), [19](https://arxiv.org/html/2512.09315v1#bib.bib19 "")\].
Specifically, Ju et al. \[ [15](https://arxiv.org/html/2512.09315v1#bib.bib15 "")\] proposed a dual-uncertainty estimation and curriculum boosting framework to address the inter-observer disagreement inherent in medical image annotation.
Most of these studies are designed for specific datasets, use different evaluation metrics, and are not released for broader use.
Therefore, conducting fair, systematic, and publicly accessible comparisons is essential for evaluating and advancing LNL methods in medical imaging.

To address this gap, we establish LNMBench, a comprehensive benchmark that systematically evaluates 10 representative LNL methods on 7 medical imaging datasets (see Fig. [1](https://arxiv.org/html/2512.09315v1#S0.F1 "Figure 1 ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).
LNMBench is organized around the progression from noise patterns to datasets, methods, and evaluation, aiming to provide a holistic understanding of how existing algorithms perform under various noise conditions in medical imaging.
We categorize label noise into two major sources: synthetic and real-world.
To evaluate performance across diverse imaging modalities and class distributions, we adopt seven medical datasets, including pathology slides, dermatology images, fundus photography, microscope images, CT and chest X-rays.
LNMBench covers both balanced datasets (PathMNIST \[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\]), which provide reference performance under approximately symmetric class distributions, and imbalanced datasets (DermaMNIST, BloodMNIST, and OrganCMNIST \[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\]), which reflect the inherent class imbalance characteristic of medical imaging \[ [17](https://arxiv.org/html/2512.09315v1#bib.bib17 "")\].
We inject synthetic noise at different ratios to both groups.
To assess model robustness under real clinical conditions, we introduce real-world noisy datasets, DRTiD \[ [13](https://arxiv.org/html/2512.09315v1#bib.bib13 "")\], Kaggle DR+ \[ [15](https://arxiv.org/html/2512.09315v1#bib.bib15 "")\], and CheXpert \[ [14](https://arxiv.org/html/2512.09315v1#bib.bib14 "")\] that contain clinically sourced label noise.
LNMBench covers widely used LNL methods and one specifically designed for class imbalanced data.
For evaluation, we report classification accuracy as well as robustness-oriented metrics, such as the clean ratio and coverage ratio for sample selection–based methods.
Experimental results demonstrate that current LNL methods are inadequate for effectively addressing label noise in medical imaging, particularly in high and real-world noise (see Fig. [1](https://arxiv.org/html/2512.09315v1#S0.F1 "Figure 1 ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).
In addition, we reveal the impact of class imbalance on the performance of sample selection based methods.
Based on extensive experimental results, we rank the methods in LNMBench by their classification accuracy across diverse noise patterns and provide an overall performance comparison (see Fig. [1](https://arxiv.org/html/2512.09315v1#S0.F1 "Figure 1 ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).
Building on these insights, we summarize the limitations of existing methods and outline potential directions for future research.
To address real-world challenges in medical image analysis, we propose MedSSL, a general strategy applicable to semi-supervised methods.
Specifically, MedSSL incorporates label smoothing in warm-up stage, introduces a regularization term during training, and employs class-specific thresholds for adaptive sample selection.
Experimental results demonstrate that MedSSL improves the performance of semi-supervised methods on real-world noisy datasets.

Our main contributions from this work are summarized as follows:

- •


We introduced a systematic benchmark for LNL methods in medical image analysis, encompassing 3 noise patterns, 7 medical datasets spanning from 6 medical domains, and 10 representative methods. This benchmark provided a standardized foundation for evaluating robustness under diverse conditions and offers valuable insights for future research.

- •


We ranked the methods in LNMBench by their classification accuracy across various noise patterns.
Furthermore, we provided a comprehensive analysis of the strengths and weaknesses of existing methods, and outline potential directions for future research.
Our findings and insights will inspire the development of more effective LNL methods for medical data.

- •


We developed a well-structured and user-friendly codebase for LNL, which supports 10 LNL methods and allows flexible substitution of backbone networks and evaluation metrics.


## 2 Related Work

### 2.1 Learning with Noisy Labels

Learning with noisy labels has received extensive attention in recent years.
Existing methods can be broadly categorized into noise transition matrix estimation, noise-robust regularization, sample selection, and semi-supervised methods.

Noise transition matrix estimation methods aim to infer clean label distributions from noisy observations and reduce the adverse effects of label corruption.
Early method \[ [37](https://arxiv.org/html/2512.09315v1#bib.bib37 "")\] modeled label noise by introducing a learnable noise adaptation layer, typically implemented as a linear transformation placed above the softmax output to approximate the label transition process.
T-Revision \[ [46](https://arxiv.org/html/2512.09315v1#bib.bib46 "")\] proposed a transition matrix estimation strategy without relying on anchor points.
However, due to the lack of reliable anchor points in real-world datasets, these methods failed to deliver satisfactory performance.
Recently, researchers have attempted to estimate instance-dependent transition matrices \[ [25](https://arxiv.org/html/2512.09315v1#bib.bib25 ""), [27](https://arxiv.org/html/2512.09315v1#bib.bib27 "")\], allowing the noise modeling to vary across samples which improves robustness in more realistic noisy scenarios.

Noise-robust regularization methods \[ [40](https://arxiv.org/html/2512.09315v1#bib.bib40 ""), [11](https://arxiv.org/html/2512.09315v1#bib.bib11 "")\] aim to enhance noise robustness by constraining the model’s capacity to memorize incorrect labels.
Many works modify loss function for robustness to noisy labels.
SCE \[ [40](https://arxiv.org/html/2512.09315v1#bib.bib40 "")\] introduces a combination of Cross Entropy and Reverse Cross Entropy to address both overfitting to noisy labels and underfitting on hard classes, enhancing robustness in noisy label scenarios.
In addition to designing robust losses, recent studies also explore parameter-level strategies to mitigate the impact of noisy labels.
CDR \[ [44](https://arxiv.org/html/2512.09315v1#bib.bib44 "")\] further mitigates noise memorization by identifying critical parameters responsible for fitting clean data and applying targeted regularization, while suppressing updates to non-critical parameters associated with noisy labels.
Beyond loss and parameter-level strategies, some methods improve robustness by directly regularizing the labels \[ [20](https://arxiv.org/html/2512.09315v1#bib.bib20 ""), [30](https://arxiv.org/html/2512.09315v1#bib.bib30 "")\].
Label smoothing \[ [30](https://arxiv.org/html/2512.09315v1#bib.bib30 "")\] explores whether the regularization skill of label smoothing is still practical in the presence of label noise.
These methods are highly flexible and easily integrated with other noise-robust techniques, but they often fall short under severe noise conditions.

Sample selection methods aim to find out those samples whose labels are likely to be corrupted \[ [41](https://arxiv.org/html/2512.09315v1#bib.bib41 ""), [43](https://arxiv.org/html/2512.09315v1#bib.bib43 "")\].
Most sample selection strategies conducted noisy label processing by selecting clean samples through a ”small-loss” strategy.
Co-teaching \[ [9](https://arxiv.org/html/2512.09315v1#bib.bib9 "")\] is a representative sample selection method that trains two networks simultaneously and lets them exchange small-loss instances in each mini-batch to update their own parameters.
Co-teaching+ \[ [49](https://arxiv.org/html/2512.09315v1#bib.bib49 "")\] extends Co-teaching by introducing a disagreement strategy, where two networks update only on samples with divergent predictions, thus enhancing robustness to high noise by mitigating network consensus on corrupted labels.
These sample selection methods effectively reduce the negative impact of noisy labels by identifying and training on likely clean samples, thereby enhancing model robustness.
However, they typically rely on prior knowledge of the noise rate, which limits their applicability in practice.

Semi-supervised methods build upon sample selection approaches by treating the identified noisy samples as unlabeled data, and leveraging model predictions as pseudo-labels for subsequent loss calculation \[ [33](https://arxiv.org/html/2512.09315v1#bib.bib33 ""), [50](https://arxiv.org/html/2512.09315v1#bib.bib50 ""), [1](https://arxiv.org/html/2512.09315v1#bib.bib1 "")\].
DivideMix \[ [22](https://arxiv.org/html/2512.09315v1#bib.bib22 "")\] uses a Gaussian Mixture Model (GMM) to divide samples into clean and noisy sets based on loss, and trains the model with a mix of supervised and semi-supervised learning to reduce the impact of label noise.
DISC \[ [24](https://arxiv.org/html/2512.09315v1#bib.bib24 "")\] introduces a dynamic instance-specific strategy for learning with noisy labels by leveraging two-view confidence estimation and per-instance memorization strength.
Semi-supervised learning-based methods fully exploit the training dataset.
However, due to their reliance on model confidence or memorization heuristics, these methods still struggle to correctly handle hard samples.

### 2.2 Medical Image Analysis with Noisy Labels

In medical image analysis, several attempts have been made to tackle the challenge of learning from label noise \[ [26](https://arxiv.org/html/2512.09315v1#bib.bib26 ""), [6](https://arxiv.org/html/2512.09315v1#bib.bib6 "")\].
For instance, Dgani et al. \[ [4](https://arxiv.org/html/2512.09315v1#bib.bib4 "")\] modeled label noise within neural networks to improve mammogram classification.
Similarly, Xue et al. \[ [47](https://arxiv.org/html/2512.09315v1#bib.bib47 "")\] proposed an iterative learning framework with uncertainty based sample mining and re-weighting to handle noisy labels in skin lesion classification.
Pham et al. \[ [34](https://arxiv.org/html/2512.09315v1#bib.bib34 "")\] proposed a CNN-based framework with label smoothing to improve thoracic disease classification on the CheXpert dataset \[ [14](https://arxiv.org/html/2512.09315v1#bib.bib14 "")\].
Ghesu et al. \[ [7](https://arxiv.org/html/2512.09315v1#bib.bib7 "")\] proposed uncertainty-driven bootstrapping to filter training samples with the highest predictive uncertainty, thereby improving robustness and accuracy on the ChestX-Ray8 dataset \[ [39](https://arxiv.org/html/2512.09315v1#bib.bib39 "")\].
Ju et al. \[ [15](https://arxiv.org/html/2512.09315v1#bib.bib15 "")\] proposed a dual-uncertainty estimation and curriculum boosting framework to address disagreement and single target label noise in medical image classification.
Some researchers \[ [21](https://arxiv.org/html/2512.09315v1#bib.bib21 "")\] have also investigated label noise in imbalanced medical datasets and proposed multi-stage noise removal frameworks to jointly address label noise, class imbalance, and class hardness.
Hou et al. \[ [12](https://arxiv.org/html/2512.09315v1#bib.bib12 "")\] proposed QMix, a framework for robust disease diagnosis under mixed noise by jointly separating mislabeled and low-quality samples and applying quality-aware semi-supervised training, achieving state-of-the-art results on retinal datasets.
Most of these studies are designed for specific datasets and are not released for broader use.
However, the lack of publicly available and standardized implementations makes it difficult to compare methods fairly, highlighting the importance of establishing a unified benchmark.

### 2.3 Benchmarks for Medical Image

As most existing approaches are designed and tested on natural image datasets, their effectiveness on medical images remains unclear.
This motivates the need for a dedicated benchmark in the medical imaging domain to ensure proper evaluation and reliable comparisons.
Therefore, many researchers have attempted to establish fair benchmarks for medical images in various fields \[ [28](https://arxiv.org/html/2512.09315v1#bib.bib28 ""), [36](https://arxiv.org/html/2512.09315v1#bib.bib36 ""), [8](https://arxiv.org/html/2512.09315v1#bib.bib8 "")\].
Menze et al. \[ [32](https://arxiv.org/html/2512.09315v1#bib.bib32 "")\] introduced the BRATS benchmark, a standardized dataset and evaluation framework for brain tumor segmentation using multi-contrast MRI scans.
MedMNIST v2 \[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\] is a large-scale and lightweight benchmark dataset that covers a diverse set of 2D and 3D biomedical images.
It is designed to enable standardized evaluation across various medical imaging modalities and classification tasks.
MONICA \[ [16](https://arxiv.org/html/2512.09315v1#bib.bib16 "")\] is a comprehensive and unified benchmark for long-tailed learning in medical image analysis.
It implements over 30 methods and evaluates them on 12 datasets across 6 medical domains, addressing the lack of standardized benchmarks in this area.

Recent studies have attempted to construct benchmarks for investigating label noise in medical imaging \[ [31](https://arxiv.org/html/2512.09315v1#bib.bib31 "")\].
Karmi et al. \[ [18](https://arxiv.org/html/2512.09315v1#bib.bib18 "")\] conducted a comprehensive review on label noise in deep learning for medical image analysis, highlighting its overlooked impact and providing experimental insights and practical recommendations for mitigating different types of label noise in medical datasets.
Ju et al.  \[ [15](https://arxiv.org/html/2512.09315v1#bib.bib15 "")\] were the first to propose a unified evaluation framework with consistent hyperparameter settings for systematically comparing different label noise learning methods in the medical image domain.
Several studies have made commendable efforts to establish benchmarks for learning with label noise in the medical imaging domain.
However, they are evaluated only on specific datasets, cover a limited range of representative methods, and lack systematic analyses of existing challenges and potential research directions.
Therefore, we propose a standardized benchmark to systematically evaluate label noise learning methods under diverse medical imaging scenarios and identify key challenges for future research.

## 3 Definition and Preliminaries

The goal of this paper is to systematically investigate the effectiveness of representative LNL methods in handling annotation noise within medical image classification tasks.
In this section, we first introduce the definition of the label noise problem.
We then describe the noise patterns used in our study.
Finally, we provide a brief introduction to the evaluation metrics.

### 3.1 Definition of Label Noise

We focus on the problem of label noise in image classification.
Label noise refers to errors in the annotated labels of training samples, leading to discrepancies between the observed label and the underlying true class.
In a kk-class classification problem, we are provided with a training dataset
D={(xi,yi)}i=1N,D=\\{(x\_{i},y\_{i})\\}\_{i=1}^{N},
where xi∈Xx\_{i}\\in X is the ii-th image in the feature space XX, and yi∈Yy\_{i}\\in Y is its corresponding observed label in the label space YY.
Due to noise in the annotation process, the observed label yiy\_{i} may differ from the true label yi∗∈Y∗y\_{i}^{\*}\\in Y^{\*}.
We denote the probability distribution of class yy for an input xx as p⁡(y\|x)p(y\|x), satisfying ∑i=1kp⁡(yi\|x)=1\\sum\_{i=1}^{k}p(y\_{i}\|x)=1.
The goal of a classification task is to learn a mapping function f:X→Yf:X\\to Y that minimizes the empirical risk RR\[ [3](https://arxiv.org/html/2512.09315v1#bib.bib3 "")\].

|     |     |     |     |
| --- | --- | --- | --- |
|  | R=𝔼(x,y)∈D​\[L⁡(f⁡(x),y)\]=𝔼x,yx​\[L⁡(f⁡(x),yx)\],R=\\mathbb{E}\_{(x,y)\\in D}\\big\[L(f(x),y)\\big\]=\\mathbb{E}\_{x,y\_{x}}\\big\[L(f(x),y\_{x})\\big\], |  | (1) |

where LL is the loss function and the expectation 𝔼\\mathbb{E} is taken over the data distribution.
However, in the presence of label noise, the empirical risk is no longer noise-tolerant, as the computation of the loss involves incorrect labels.
As a result, deep neural networks may overfit these noisy labels, leading to corrupted feature representations and degraded generalization performance.

### 3.2 Noise Patterns

Instance-independent label noise refers to a noise pattern where the label corruption process does not depend on the input instance features, but only on the original class label.
Two representative types of this noise are symmetric and asymmetric label noise.
We model label noise using a transition matrix τ∈ℝk×k\\tau\\in\\mathbb{R}^{k\\times k}, where τi​j\\tau\_{ij} denotes the probability that a sample with true label ii is observed as label jj, and kk represents the total number of classes. Let 𝒜\\mathcal{A} denote the set of all class indices, η\\eta denote the noise rate.
Symmetric noise is modeled by randomly choosing a label from all classes
including the ground truth label, which means
∀j∈𝒜,τi​j=ηk−1\\forall j\\in\\mathcal{A},\\;\\tau\_{ij}=\\tfrac{\\eta}{k-1}.
In asymmetric noise, the ground truth label is not included in the label
flipping options, where i≠ji\\neq j,
τi​j=ηk−1\\tau\_{ij}=\\tfrac{\\eta}{k-1}.
In contrast to symmetric noise, asymmetric noise represents a noise process where the ground truth label is flipped into one specific label whose class is closer to the true label.
We adopt symmetric noise in our benchmark because it provides a controlled and widely used corruption pattern, enabling systematic evaluation and fair comparison across different methods.

Instance-dependent label noise refers to a more realistic type of label corruption where the noise generation process depends on the input data features.
Even among instances belonging to the same class, significant variations in visual can lead to different probabilities of being mislabeled.
As a result, the label flipping probability is not uniform across instances, but rather highly conditioned on each specific sample.
This property makes instance dependent noise better suited for modeling real world annotation errors.
A commonly used approach to generate instance-dependent label noise is to assign each sample a flipping probability based on its input features, and then compute a probability distribution over classes by projecting the features onto randomly sampled vectors \[ [45](https://arxiv.org/html/2512.09315v1#bib.bib45 "")\].
A noisy label is then sampled from this distribution.
This method allows different instances from the same class to have different flipping behaviors.
However, the direction vectors are sampled randomly, so the synthetic noise may not be suitable for simulating the types of errors made by human experts.

To address this limitation, we introduce a new instance-dependent label noise generation strategy that leverages model predictions and uncertainty to construct more realistic label noise (see Algorithm [1](https://arxiv.org/html/2512.09315v1#alg1 "In 3.2 Noise Patterns ‣ 3 Definition and Preliminaries ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).
Let ff be a network trained on a clean reference set, yielding soft predictions p⁡(j∣x)p(j\\mid x).
For each training sample (xi,yi)(x\_{i},y\_{i}), we mask the ground-truth class and renormalize the remaining probabilities to obtain a mislabeling distribution π(⋅∣xi)\\pi(\\cdot\\mid x\_{i}).
Given a sample-specific flip rate qi∈\[0,1\]q\_{i}\\in\[0,1\] (with mean η\\eta), the per-instance transition is

|     |     |     |
| --- | --- | --- |
|  | Ti​(xi)=(1−qi)​𝐞yi+qi​π​(xi),T\_{i}(x\_{i})=(1-q\_{i})\\,\\mathbf{e}\_{y\_{i}}+q\_{i}\\,\\pi(x\_{i}), |  |

where 𝐞yi\\mathbf{e}\_{y\_{i}} is the one-hot vector corresponding to the true class yiy\_{i}.
The noisy label is then drawn as y~i∼Categorical⁡(Ti​(xi))\\tilde{y}\_{i}\\sim\\mathrm{Categorical}\\big(T\_{i}(x\_{i})\\big).
This formulation produces feature-conditioned, heterogeneous flips that better reflect realistic annotation errors.

Algorithm 1Instance-dependent Label Noise Generation

Input: Test set DtestD\_{\\text{test}}; Train set Dtrain={(xi,yi)}i=1ND\_{\\text{train}}=\\{(x\_{i},y\_{i})\\}\_{i=1}^{N}; noise rate η\\eta.

Step 1: Train a clean model

Train a classifer ff on clean test set DtestD\_{\\text{test}};

Step 2: Generate instance-dependent noisy labels

Sample instance flip rates qq from truncated normal distribution 𝒩⁡(η,0.12,\[0,1\])\\mathcal{N}(\\eta,0.1^{2},\[0,1\]);

Fori=1,2,…,Ni=1,2,\\dots,Ndo

z=f⁡(xi)z=f(x\_{i})

zyi=−∞z\_{y\_{i}}=-\\infty

p=qi×softmax⁡(z)p=q\_{i}\\times\\mathrm{softmax}(z)

p~yi=1−qi\\tilde{p}\_{y\_{i}}=1-q\_{i}

Sample a noisy label yiy\_{i} from the label space

according to probabilities pp

End for

Output: Noisy samples D~={(xi,y~i)}i=1N\\tilde{D}=\\{(x\_{i},\\tilde{y}\_{i})\\}\_{i=1}^{N}

Real-world label noise refers to the annotation errors that naturally arise when datasets are labeled by human annotators.
Previous synthetic label noise models, while useful for controlled experiments, fall short in capturing the complexity of real-world annotation errors \[ [42](https://arxiv.org/html/2512.09315v1#bib.bib42 "")\].
Medical datasets often involve ambiguous cases and limited expert consensus, making label noise more subtle and difficult to replicate through simple simulations.
Therefore, evaluating label noise learning methods on real-world medical datasets where annotation uncertainty reflects actual clinical practice is more meaningful for assessing their true effectiveness.

### 3.3 Robust Metrics under LNL

Checkpoint selection under label noise is a challenging problem because models often learn meaningful patterns in early epochs but eventually overfit noisy labels.
Most existing studies \[ [15](https://arxiv.org/html/2512.09315v1#bib.bib15 ""), [12](https://arxiv.org/html/2512.09315v1#bib.bib12 "")\] evaluate performance using either the best test accuracy (B), which reflects the upper bound of model capacity, or the average test accuracy over the last few epochs (L), which captures training stability.
However, both require access to the test set and therefore do not reflect realistic model selection.
To approximate practical conditions, we further consider validation-selected accuracy (V), defined as the test accuracy at the epoch where the noisy validation accuracy is maximized. Reporting V allows us to assess whether checkpoint selection based on a noisy validation set is reliable.
By comparing V against B and L, we quantify the gap between practical selection and ideal or stable performance.
In this work, we report all three metrics (B, L, V) to ensure comparability with prior studies and to provide direct evidence of the reliability of noisy validation-based selection.
Each experiment is repeated with three random seeds, and averaged results are reported for robustness.

Table 1: Performance comparison under different noise types on PathMNIST. Bold indicates the best result

|     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Dataset |  | PathMNIST |  |  |  |  |  |
| Noise type |  | Sym-20% | Sym-50% | Sym-90% | Idn-20% | Idn-50% | Idn-90% |
|  | B | 94.40 ± 0.37 | 93.82 ± 0.91 | 13.42 ± 1.82 | 93.34 ± 1.24 | 76.63 ± 4.24 | 20.77 ± 1.88 |
| CE | V | 91.34 ± 3.34 | 92.99 ± 1.66 | 9.69 ± 2.05 | 93.39 ± 1.24 | 76.34 ± 4.38 | 11.14 ± 2.79 |
|  | L | 84.01 ± 0.85 | 52.25 ± 1.93 | 10.21 ± 0.93 | 86.00 ± 0.61 | 56.54 ± 0.36 | 15.13 ± 1.10 |
| T-Revision | B | 96.13 ±\\pm 0.91 | 91.23 ±\\pm 0.35 | 8.25 ±\\pm 1.63 | 91.63 ±\\pm 0.33 | 74.09 ±\\pm 0.72 | 23.50 ±\\pm 1.68 |
|  | V | 94.87 ±\\pm 0.84 | 87.23 ±\\pm 0.77 | 8.25 ±\\pm 1.13 | 91.51 ±\\pm 0.56 | 63.40 ±\\pm 0.90 | 11.34 ±\\pm 1.53 |
|  | L | 85.30 ±\\pm 0.79 | 52.37 ±\\pm 0.65 | 8.25 ±\\pm 1.87 | 87.06 ±\\pm 0.91 | 53.13 ±\\pm 0.44 | 11.17 ±\\pm 0.96 |
| VolMinNet | B | 96.16 ±\\pm 0.49 | 92.97 ±\\pm 0.37 | 15.81 ±\\pm 1.53 | 91.53 ±\\pm 0.35 | 77.18 ±\\pm 1.20 | 17.92 ±\\pm 2.55 |
|  | V | 96.03 ±\\pm 0.23 | 92.81 ±\\pm 0.68 | 6.59 ±\\pm 0.92 | 90.78 ±\\pm 0.87 | 72.17 ±\\pm 0.38 | 13.50 ±\\pm 1.77 |
|  | L | 88.01 ±\\pm 0.88 | 56.92 ±\\pm 0.69 | 9.53 ±\\pm 0.99 | 84.63 ±\\pm 0.87 | 54.03 ±\\pm 0.54 | 13.63 ±\\pm 1.10 |
| SCE | B | 94.94 ±\\pm 0.31 | 94.60 ±\\pm 1.10 | 11.18 ±\\pm 3.28 | 95.10 ±\\pm 0.45 | 90.36 ±\\pm 0.72 | 16.44 ±\\pm 4.23 |
|  | V | 94.42 ±\\pm 1.52 | 94.31 ±\\pm 0.79 | 8.21 ±\\pm 2.31 | 95.10 ±\\pm 0.89 | 90.35 ±\\pm 0.85 | 7.89 ±\\pm 2.17 |
|  | L | 90.94 ±\\pm 0.71 | 58.84 ±\\pm 1.38 | 7.50 ±\\pm 2.55 | 87.37 ±\\pm 2.54 | 56.23 ±\\pm 2.75 | 16.23 ±\\pm 2.43 |
| CDR | B | 94.79 ±\\pm 0.47 | 95.15 ±\\pm 0.86 | 11.47 ±\\pm 1.94 | 95.07 ±\\pm 0.54 | 81.66 ±\\pm 0.25 | 20.85 ±\\pm 1.21 |
|  | V | 91.64 ±\\pm 0.29 | 94.97±\\pm 0.81 | 11.47 ±\\pm 1.14 | 94.81 ±\\pm 0.24 | 81.66 ±\\pm 0.35 | 7.66 ±\\pm 1.88 |
|  | L | 89.73 ±\\pm 0.14 | 57.94 ±\\pm 2.11 | 10.23 ±\\pm 1.39 | 89.25 ±\\pm 0.28 | 59.10 ±\\pm 1.72 | 15.84 ±\\pm 2.01 |
| Co-teaching | B | 93.76 ±\\pm 0.66 | 92.78 ±\\pm 0.09 | 16.57 ±\\pm 2.37 | 94.14 ±\\pm 0.46 | 91.93 ±\\pm 0.97 | 25.20 ±\\pm 0.87 |
|  | V | 89.55 ±\\pm 1.56 | 87.67 ±\\pm 5.00 | 5.52 ±\\pm 3.53 | 90.34 ±\\pm 3.30 | 89.63 ±\\pm 1.33 | 17.34 ±\\pm 1.79 |
|  | L | 89.63 ±\\pm 0.78 | 82.79 ±\\pm 0.57 | 8.82 ±\\pm 3.28 | 90.49 ±\\pm 0.77 | 86.54 ±\\pm 0.97 | 15.50 ±\\pm 5.89 |
| Co-teaching+ | B | 93.50 ±\\pm 0.39 | 93.39 ±\\pm 1.37 | 16.21 ±\\pm 1.89 | 94.00 ±\\pm 0.37 | 82.63 ±\\pm 5.82 | 29.52 ±\\pm 2.15 |
|  | V | 90.85 ±\\pm 1.78 | 92.26 ±\\pm 1.16 | 11.71 ±\\pm 1.21 | 92.21 ±\\pm 1.14 | 81.28 ±\\pm 7.91 | 14.49 ±\\pm 1.41 |
|  | L | 91.13 ±\\pm 1.34 | 91.87 ±\\pm 0.98 | 10.81 ±\\pm 0.85 | 92.30 ±\\pm 0.27 | 66.09 ±\\pm 8.35 | 20.17 ±\\pm 1.17 |
| CoDis | B | 94.66 ±\\pm 0.57 | 94.40 ±\\pm 1.94 | 24.53 ±\\pm 2.48 | 93.51 ±\\pm 0.67 | 91.84 ±\\pm 1.32 | 26.21 ±\\pm 3.28 |
|  | V | 92.44 ±\\pm 1.13 | 88.30 ±\\pm 1.11 | 2.26 ±\\pm 1.49 | 93.48 ±\\pm 1.26 | 87.72 ±\\pm 1.18 | 15.26 ±\\pm 1.08 |
|  | L | 89.19 ±\\pm 1.32 | 80.09 ±\\pm 1.76 | 1.58 ±\\pm 2.71 | 87.58 ±\\pm 1.31 | 86.07 ±\\pm 1.73 | 13.61 ±\\pm 2.56 |
| JoCoR | B | 92.03 ±\\pm 0.61 | 91.17 ±\\pm 1.25 | 16.26 ±\\pm 3.09 | 92.16 ±\\pm 1.60 | 81.33 ±\\pm 3.77 | 24.93 ±\\pm 2.74 |
|  | V | 88.19 ±\\pm 0.91 | 89.96 ±\\pm 0.84 | 7.22 ±\\pm 5.07 | 90.09 ±\\pm 1.24 | 71.05 ±\\pm 3.63 | 12.55 ±\\pm 1.07 |
|  | L | 83.10 ±\\pm 0.31 | 49.84 ±\\pm 1.12 | 8.37 ±\\pm 3.07 | 82.57 ±\\pm 1.41 | 54.49 ±\\pm 0.90 | 15.99 ±\\pm 0.89 |
|  | B | 94.14 ±\\pm 0.79 | 93.80 ±\\pm 1.27 | 19.09 ±\\pm 2.31 | 93.28 ±\\pm 0.55 | 86.83 ±\\pm 0.68 | 18.98 ±\\pm 4.35 |
| DISC | V | 88.72 ±\\pm 0.97 | 90.43 ±\\pm 2.01 | 9.16 ±\\pm 1.64 | 88.19 ±\\pm 2.49 | 84.14 ±\\pm 2.61 | 4.69 ±\\pm 0.60 |
|  | L | 87.76 ±\\pm 1.03 | 90.58 ±\\pm 3.01 | 5.80 ±\\pm 6.11 | 87.98 ±\\pm 1.98 | 82.11 ±\\pm 2.76 | 4.76 ±\\pm 0.67 |
|  | B | 95.79 ±\\pm 0.40 | 95.26 ±\\pm 0.47 | 12.52 ±\\pm 0.10 | 96.13 ±\\pm 0.65 | 92.29 ±\\pm 0.11 | 16.02 ±\\pm 1.49 |
| DivideMix | V | 93.86 ±\\pm 0.37 | 90.18 ±\\pm 2.23 | 5.37 ±\\pm 4.26 | 92.85 ±\\pm 1.03 | 88.38 ±\\pm 0.56 | 11.52 ±\\pm 1.52 |
|  | L | 91.39 ±\\pm 0.33 | 91.29 ±\\pm 0.05 | 7.02 ±\\pm 2.21 | 90.33 ±\\pm 0.27 | 82.35 ±\\pm 2.96 | 7.66 ±\\pm 3.41 |

(a)PathMNIST

(b)DermaMNIST

(c)BloodMNIST

(d)OrganCMNIST

(e)DRTiD

(f)KaggleDR+

(g)CheXpert

Figure 2: Overview of class distributions across the datasets utilized in LNMBench.

## 4 Experiments

We present extensive experiments to evaluate the robustness of representative LNL methods on medical image classification tasks.
We aim to examine their effectiveness under different noise types, ratios, and dataset characteristics.
In Section [4.1](https://arxiv.org/html/2512.09315v1#S4.SS1 "4.1 Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), we introduce the datasets used in LNMBench.
Section [4.2](https://arxiv.org/html/2512.09315v1#S4.SS2 "4.2 Comparative Study ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook") provides description of the evaluated methods.
Section [4.3](https://arxiv.org/html/2512.09315v1#S4.SS3 "4.3 Implementation Details ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook") presents the implementation details of our experiments.
In Section [4.4](https://arxiv.org/html/2512.09315v1#S4.SS4 "4.4 Experimental Result Overview ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), we summarize the overall experimental results.
Section [4.5](https://arxiv.org/html/2512.09315v1#S4.SS5 "4.5 Results on Balanced Benchmark Dataset under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook") reports the results on balanced datasets with three ratios of symmetric and instance-dependent noise.
Section [4.6](https://arxiv.org/html/2512.09315v1#S4.SS6 "4.6 Results on Imbalanced Datasets under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook") reports the results on imbalanced datasets with three ratios of instance-dependent noise.
Section [4.7](https://arxiv.org/html/2512.09315v1#S4.SS7 "4.7 Results on Real-world Noisy Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook") reports the results on real-world imbalanced noisy datasets.
Section [4.8](https://arxiv.org/html/2512.09315v1#S4.SS8 "4.8 Summary ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook") discusses the key challenges identified in current methods and provides insights for future research directions.

### 4.1 Datasets

As shown in the Fig. [2](https://arxiv.org/html/2512.09315v1#S3.F2 "Figure 2 ‣ 3.3 Robust Metrics under LNL ‣ 3 Definition and Preliminaries ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), we illustrate the class distributions of the datasets utilized in LNMBench.
To systematically assess robustness, we consider three evaluation regimes. First, we use the near-balanced benchmark PathMNIST \[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\] to establish reference performance under approximately symmetric class distributions.
Second, given that class imbalance is pervasive in medical imaging, we include DermaMNIST, BloodMNIST, and OrganCMNIST \[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\] to examine performance under realistic distribution skew.
For these two groups, we inject synthetic noise (symmetric and instance-dependent).
Finally, we evaluate external validity under clinically sourced label noise using the real-world noise datasets DRTiD \[ [13](https://arxiv.org/html/2512.09315v1#bib.bib13 "")\], Kaggle DR+ \[ [15](https://arxiv.org/html/2512.09315v1#bib.bib15 "")\], and CheXpert \[ [14](https://arxiv.org/html/2512.09315v1#bib.bib14 "")\].

#### 4.1.1 Balanced Dataset

PathMNIST \[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\] is derived from colorectal cancer histology slides and consists of hematoxylin and eosin stained tissue patches for a nine-class classification task.
Each sample is a 224×224224\\times 224 RGB image cropped from whole-slide scans.
The dataset contains 107,180 images, officially divided into 89,996 training, 10,004 validation, and 7,180 test samples.

#### 4.1.2 Imbalanced Datasets

DermaMNIST\[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\] contains 10,015 dermatoscopic images of common pigmented skin lesions (size 224×224224\\times 224), categorized into seven classes.
The official split includes 7,008 training, 1,002 validation, and 2,005 test images.
BloodMNIST\[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\] consists of 17,092 microscopy images of peripheral blood cells.
The dataset is officially divided into 11,959 training, 1,712 validation, and 3,421 test samples.
We use the 224×224224\\times 224 RGB version for consistency.
OrganCMNIST\[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\], derived from LiTS abdominal CT scans, comprises 23,660 coronal-view slices labeled into eleven organ classes.
It includes 13,000 training, 2,392 validation, and 8,268 test images, all resized to 224×224224\\times 224.

#### 4.1.3 Real-world Noisy Datasets

DRTiD\[ [13](https://arxiv.org/html/2512.09315v1#bib.bib13 "")\] is a real-world diabetic retinopathy dataset comprising 3,100 fundus images collected from community screening, with resolutions ranging from 1,444×1,4441,444\\times 1,444 to 3,058×3,0003,058\\times 3,000 pixels.
We split the dataset into 1,600 training, 400 validation, and 1,100 test images.
Initial annotations from community healthcare workers serve as noisy labels, while expert consensus following the International Clinical Diabetic Retinopathy (ICDR) Scale provides the clean ground truth across five severity levels: normal, mild NPDR, moderate NPDR, severe NPDR, and proliferative DR (PDR).
The Kaggle Diabetic Retinopathy (DR) dataset originally contains 88,702 fundus photographs from 44,351 patients (one image per eye) for five-class DR severity classification: normal, mild NPDR, moderate NPDR, severe NPDR, and PDR.
Ju et al. \[ [15](https://arxiv.org/html/2512.09315v1#bib.bib15 "")\] later re-annotated this dataset with assistance from over ten ophthalmologists, releasing the Kaggle DR+, which we adopt in this work to ensure higher annotation quality.
CheXpert\[ [14](https://arxiv.org/html/2512.09315v1#bib.bib14 "")\] consists of 224,316 chest radiographs from 65,240 patients, with structured labels automatically extracted from radiology reports.
Among the 14 available observations, we select five clinically important and prevalent conditions: Atelectasis, Cardiomegaly, Consolidation, Edema, and Pleural Effusion.
Following standard practice, uncertain labels are treated as negative, and multi-label samples are removed to retain only single-label cases for training.
The official test set was independently annotated by eight board-certified radiologists, with binarization rules treating present and uncertain likely as positive, and absent and uncertain unlikely as negative.

### 4.2 Comparative Study

Our benchmark comprises 10 representative LNL methods together with the cross-entropy (CE) baseline for comparison.
The evaluated methods can be categorized into four groups: noise transition matrix estimation methods (T-Revision \[ [46](https://arxiv.org/html/2512.09315v1#bib.bib46 "")\] and VolMinNet \[ [23](https://arxiv.org/html/2512.09315v1#bib.bib23 "")\]), noise-robust regularization methods (SCE \[ [40](https://arxiv.org/html/2512.09315v1#bib.bib40 "")\] and CDR \[ [44](https://arxiv.org/html/2512.09315v1#bib.bib44 "")\]), traditional sample selection methods (Co-teaching \[ [9](https://arxiv.org/html/2512.09315v1#bib.bib9 "")\], Co-teaching+ \[ [49](https://arxiv.org/html/2512.09315v1#bib.bib49 "")\], CoDis \[ [43](https://arxiv.org/html/2512.09315v1#bib.bib43 "")\] and JoCoR \[ [41](https://arxiv.org/html/2512.09315v1#bib.bib41 "")\]), semi-supervised methods (DISC \[ [24](https://arxiv.org/html/2512.09315v1#bib.bib24 "")\] and DivideMix \[ [22](https://arxiv.org/html/2512.09315v1#bib.bib22 "")\]).

- •


T-Revision\[ [46](https://arxiv.org/html/2512.09315v1#bib.bib46 "")\] learns label transition matrices without relying on exact anchor points by introducing a learnable slack variable, enabling more robust classifiers under label noise.

- •


VolMinNet\[ [23](https://arxiv.org/html/2512.09315v1#bib.bib23 "")\] estimates the label transition matrix without the anchor point assumption by jointly optimizing the cross-entropy loss and the volume of the simplex formed by the matrix columns.

- •


SCE\[ [40](https://arxiv.org/html/2512.09315v1#bib.bib40 "")\] combines standard cross-entropy with a reversed cross-entropy loss to tolerate both underfitting on clean data and overfitting on noisy labels.

- •


CDR\[ [44](https://arxiv.org/html/2512.09315v1#bib.bib44 "")\] leverages the lottery ticket hypothesis to separate clean-label–fitting and noise-fitting parameters, applying different updates to enhance clean label memorization in early training.

- •


Co-teaching\[ [9](https://arxiv.org/html/2512.09315v1#bib.bib9 "")\] trains two networks simultaneously and lets each network select small-loss samples to train its peer, reducing the impact of noisy labels.

- •


Co-teaching+\[ [49](https://arxiv.org/html/2512.09315v1#bib.bib49 "")\] improves upon Co-teaching by incorporating disagreement-based sample selection, which enhances the robustness of the two networks in extremely noisy scenarios.

- •


CoDis\[ [43](https://arxiv.org/html/2512.09315v1#bib.bib43 "")\] mitigates class imbalance by mining likely-clean samples that exhibit large prediction-probability discrepancies between two jointly trained networks, thereby preserving model divergence.

- •


JoCoR\[ [41](https://arxiv.org/html/2512.09315v1#bib.bib41 "")\] jointly optimizes two networks using a shared loss function that balances classification loss and prediction consistency, encouraging agreement on clean samples.

- •


DISC\[ [24](https://arxiv.org/html/2512.09315v1#bib.bib24 "")\] dynamically divides training samples into clean, hard, and purified subsets based on two-view consistency, and applies tailored regularization strategies to each subset to enhance robustness against label noise.

- •


DivideMix\[ [22](https://arxiv.org/html/2512.09315v1#bib.bib22 "")\] fits a Gaussian Mixture Model (GMM) on the training losses to separate clean and noisy samples, then applies semi-supervised learning with MixMatch for robust training.


### 4.3 Implementation Details

As most existing LNL methods are implemented with ResNet50 \[ [10](https://arxiv.org/html/2512.09315v1#bib.bib10 "")\] as the backbone, we adopt ResNet-50 for fair comparison, while our codebase also supports mainstream backbones, including transformer-based architectures such as ViT \[ [5](https://arxiv.org/html/2512.09315v1#bib.bib5 "")\].
The batch size is set to 128 for PathMNIST, DermaMNIST, BloodMNIST and OrganCMNIST \[ [48](https://arxiv.org/html/2512.09315v1#bib.bib48 "")\].
For DRTiD \[ [13](https://arxiv.org/html/2512.09315v1#bib.bib13 "")\] and Kaggle DR+ \[ [15](https://arxiv.org/html/2512.09315v1#bib.bib15 "")\], all fundus images are resized to 512×512512\\times 512 before training, and the batch size is reduced to 16.
For CheXpert \[ [14](https://arxiv.org/html/2512.09315v1#bib.bib14 "")\], all fundus images are resized to 224×224224\\times 224 before training, and the batch size is 128.
For each method, we adopt the optimizer and learning rate settings recommended in their original methods to preserve their optimal training configurations.
All experiments are conducted on a single machine equipped with four NVIDIA A6000 GPUs.
To ensure reproducibility, each experiment is repeated with three different random seeds, and the averaged results are reported.

### 4.4 Experimental Result Overview

To obtain a stable and fair comparison, we report the average classification accuracy over the last 5 epochs for each method under three noise patterns: symmetric noise, instance-dependent noise, and real-world noise.
Based on these results, we rank all methods according to their average performance, and further compute the mean accuracy across the three noise patterns to provide an overall measure of robustness (see Fig. [1](https://arxiv.org/html/2512.09315v1#S0.F1 "Figure 1 ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).
Overall, Co-teaching and DISC achieved the highest average classification accuracy under all noise patterns.
Co-teaching+ and DivideMix achieved the highest average classification accuracy under symmetric noise.
Co-teaching and CoDis achieved the highest average classification accuracy under instance-dependent noise.
The noise-robust regularization methods (SCE and CDR) achieved the highest average classification accuracy under real-world noise.

### 4.5 Results on Balanced Benchmark Dataset under Synthetic Noise

In this section, we evaluate LNL methods on the relatively balanced PathMNIST, considering both symmetric noise and instance-dependent noise.

#### 4.5.1 Quantitative Results

Table [1](https://arxiv.org/html/2512.09315v1#S3.T1 "Table 1 ‣ 3.3 Robust Metrics under LNL ‣ 3 Definition and Preliminaries ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook") summarizes the quantitative results of 10 representative LNL methods on the PathMNIST under symmetric and instance-dependent noise settings, with 3 different noise rates: 20%, 50%, and 90%.

All methods exhibit good performance under Sym-20%.
Under Sym-50%, both transition matrix based (T-revision and VolMinNet) and regularization methods (SCE and CDR) exhibit performance degradation.
In particular, we find a substantial discrepancy between the V and L accuracies for these methods, indicating a tendency to overfit noisy labels in the later stages of training.
Most sample selection and semi-supervised methods continue to perform well under Sym-50%, with the exception of JoCoR.
At Sym-90%, all methods experience significant performance degradation.

In the more realistic and challenging instance-dependent noise setting, performance declines significantly across all methods as the noise rate increases.
At Idn-20%, most methods still retain reasonable performance.
As the noise rate increases to 50%, noise-robust regularization methods and noise transition matrix estimation methods begin to show performance degradation, while Co-teaching, CoDis and semi-supervised methods achieve higher accuracy.
At Idn-90%, all methods exhibit a complete collapse in performance.

In summary, methods relying on regularization or noise transition matrix estimation exhibit limited effectiveness.
In contrast, DISC, DivideMix, CoDis and Co-teaching demonstrate comparatively superior robustness.
In this section, we presented a quantitative comparison of different methods.
Next, we delves into a deeper analysis to understand the underlying reasons behind their performance differences.

(a)Estimation Error

(b)Test Accuracy

Figure 3: Comparison of estimation error and test accuracy under different symmetric noise rates for VolMinNet.

#### 4.5.2 Analysis on Noise Transition Matrix Estimation

Transition matrix estimation methods exhibit a substantial performance gap between symmetric and instance-dependent noise.
Since these methods are specifically designed for instance-independent noise.
For symmetric noise (see Fig. [3](https://arxiv.org/html/2512.09315v1#S4.F3 "Figure 3 ‣ 4.5.1 Quantitative Results ‣ 4.5 Results on Balanced Benchmark Dataset under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")), we observe that for VolMinNet, smaller estimation error of the transition matrix is usually associated with higher test accuracy.
This indicates a strong correlation between estimation quality and classification performance.
However, when the noise rate exceeds 50%, the estimation error grows significantly, resulting in a noticeable drop in classification accuracy.
This demonstrates that these methods fail to resolve the label noise issue, even on balanced dataset.

(a)

(b)

(c)

(d)

Figure 4: Sample selection performance under instance-dependent noise on PathMNIST.
The clean ratio represents the proportion of correctly labeled samples among those selected,
while the coverage ratio represents the proportion of selected clean samples among all clean samples.
(a) Clean ratio at 50% noise.
(b) Coverage ratio at 50% noise.
(c) Clean ratio at 90% noise.
(d) Coverage ratio at 90% noise.

(a)Idn-50%

(b)Idn-90%

Figure 5: The loss distributions of Co-teaching under Idn-50% and Idn-90% on PathMNIST.Table 2: Comparison of different methods on three imbalance datasets under instance-dependent noise. Bold indicates the best result

|     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dataset |  | DermaMNIST |  |  | BloodMNIST |  |  | OrganCMNIST |  |  |
| Noise type |  | Idn-20% | Idn-50% | Idn-90% | Idn-20% | Idn-50% | Idn-90% | Idn-20% | Idn-50% | Idn-90% |
| CE | B | 80.60 ±\\pm 1.15 | 69.63 ±\\pm 3.18 | 22.15 ±\\pm 1.67 | 94.68 ±\\pm 1.35 | 75.15 ±\\pm 1.81 | 17.36 ±\\pm 1.75 | 90.21 ±\\pm 0.98 | 68.17 ±\\pm 1.49 | 27.56 ±\\pm 2.79 |
|  | V | 80.55 ±\\pm 1.57 | 66.53 ±\\pm 4.36 | 17.11 ±\\pm 1.41 | 94.53 ±\\pm 0.48 | 75.15 ±\\pm 1.13 | 2.81 ±\\pm 2.91 | 89.28 ±\\pm 0.97 | 68.13 ±\\pm 1.46 | 15.01 ±\\pm 2.78 |
|  | L | 79.97 ±\\pm 0.33 | 55.43 ±\\pm 0.47 | 16.68 ±\\pm 1.20 | 93.26 ±\\pm 0.86 | 63.79 ±\\pm 1.78 | 7.71 ±\\pm 3.28 | 88.06 ±\\pm 0.78 | 65.80 ±\\pm 1.75 | 14.94 ±\\pm 3.87 |
| T-Revision | B | 73.16 ±\\pm 1.23 | 35.66 ±\\pm 1.61 | 18.65 ±\\pm 1.19 | 96.61 ±\\pm 0.95 | 79.77 ±\\pm 1.05 | 17.36 ±\\pm 1.75 | 89.42 ±\\pm 0.71 | 66.97 ±\\pm 1.35 | 17.12 ±\\pm 1.35 |
|  | V | 71.77 ±\\pm 1.08 | 35.14 ±\\pm 3.71 | 16.08 ±\\pm 1.39 | 93.62 ±\\pm 0.82 | 62.41 ±\\pm 1.63 | 11.64 ±\\pm 2.71 | 89.34 ±\\pm 0.84 | 65.74 ±\\pm 1.85 | 14.82 ±\\pm 1.73 |
|  | L | 72.47 ±\\pm 0.56 | 17.57 ±\\pm 0.79 | 14.17 ±\\pm 1.94 | 93.10 ±\\pm 0.47 | 57.14 ±\\pm 0.65 | 18.15 ±\\pm 2.96 | 89.14 ±\\pm 0.49 | 60.56 ±\\pm 0.64 | 16.33 ±\\pm 2.18 |
| VolMinNet | B | 72.74 ±\\pm 1.52 | 39.63 ±\\pm 3.24 | 19.48 ±\\pm 2.13 | 96.17 ±\\pm 1.46 | 72.70 ±\\pm 1.51 | 19.64 ±\\pm 2.19 | 88.33 ±\\pm 0.93 | 68.79 ±\\pm 1.09 | 24.22 ±\\pm 2.82 |
|  | V | 71.24 ±\\pm 1.48 | 34.99 ±\\pm 2.74 | 15.71 ±\\pm 1.65 | 96.12 ±\\pm 0.95 | 72.71 ±\\pm 1.47 | 8.71 ±\\pm 3.24 | 88.33 ±\\pm 0.62 | 60.03 ±\\pm 2.08 | 13.13 ±\\pm 1.95 |
|  | L | 71.23 ±\\pm 0.79 | 38.14 ±\\pm 1.17 | 15.66 ±\\pm 1.38 | 91.33 ±\\pm 1.13 | 61.53 ±\\pm 1.36 | 8.98 ±\\pm 2.19 | 87.36 ±\\pm 0.72 | 63.46 ±\\pm 1.68 | 11.91 ±\\pm 2.97 |
| SCE | B | 82.18 ±\\pm 0.58 | 71.50 ±\\pm 0.36 | 23.08 ±\\pm 0.71 | 97.12 ±\\pm 1.33 | 86.84 ±\\pm 0.67 | 20.41 ±\\pm 1.22 | 93.17 ±\\pm 0.16 | 81.89 ±\\pm 1.00 | 23.27 ±\\pm 0.69 |
|  | V | 82.54 ±\\pm 0.79 | 67.81 ±\\pm 0.95 | 13.80 ±\\pm 0.53 | 96.02 ±\\pm 1.36 | 76.21 ±\\pm 1.63 | 7.01 ±\\pm 1.62 | 92.21 ±\\pm 1.20 | 80.14 ±\\pm 3.38 | 11.70 ±\\pm 0.96 |
|  | L | 77.35 ±\\pm 0.81 | 57.20 ±\\pm 0.73 | 18.67 ±\\pm 0.86 | 89.62 ±\\pm 0.75 | 50.95 ±\\pm 0.92 | 19.02 ±\\pm 0.16 | 86.06 ±\\pm 0.68 | 55.91 ±\\pm 0.35 | 21.65 ±\\pm 0.25 |
| CDR | B | 82.39 ±\\pm 0.86 | 71.52 ±\\pm 0.57 | 32.62 ±\\pm 0.85 | 96.34 ±\\pm 0.26 | 76.38 ±\\pm 0.83 | 15.16 ±\\pm 0.89 | 91.95 ±\\pm 0.16 | 75.87 ±\\pm 1.19 | 24.56 ±\\pm 2.56 |
|  | V | 82.14 ±\\pm 0.71 | 67.13 ±\\pm 0.34 | 11.87 ±\\pm 0.49 | 95.14 ±\\pm 0.54 | 77.27 ±\\pm 0.43 | 7.97 ±\\pm 0.92 | 90.01 ±\\pm 1.63 | 74.85 ±\\pm 1.01 | 16.76 ±\\pm 1.39 |
|  | L | 81.95 ±\\pm 0.78 | 57.77 ±\\pm 1.14 | 15.80 ±\\pm 0.76 | 95.97 ±\\pm 1.03 | 65.43 ±\\pm 0.79 | 9.32 ±\\pm 0.56 | 91.68 ±\\pm 0.18 | 67.97 ±\\pm 0.40 | 15.63 ±\\pm 0.19 |
| Co-teaching | B | 74.36 ±\\pm 1.41 | 70.07 ±\\pm 0.79 | 20.55 ±\\pm 0.85 | 96.34 ±\\pm 0.19 | 89.27 ±\\pm 2.55 | 17.96 ±\\pm 7.90 | 91.25 ±\\pm 0.07 | 82.64 ±\\pm 1.14 | 11.11 ±\\pm 2.44 |
|  | V | 73.99 ±\\pm 0.89 | 66.23 ±\\pm 1.29 | 11.65 ±\\pm 1.23 | 95.99 ±\\pm 0.44 | 88.68 ±\\pm 3.09 | 11.65 ±\\pm 1.23 | 90.83 ±\\pm 0.36 | 81.92 ±\\pm 1.09 | 21.20 ±\\pm 0.32 |
|  | L | 73.08 ±\\pm 0.48 | 65.65 ±\\pm 0.77 | 11.54 ±\\pm 0.47 | 95.79 ±\\pm 0.35 | 86.15 ±\\pm 2.12 | 7.47 ±\\pm 0.94 | 90.87 ±\\pm 0.07 | 82.09 ±\\pm 1.12 | 14.84 ±\\pm 2.55 |
| Co-teaching+ | B | 72.19 ±\\pm 0.28 | 67.93 ±\\pm 4.18 | 15.28 ±\\pm 3.16 | 94.74 ±\\pm 1.87 | 77.17 ±\\pm 2.00 | 21.40 ±\\pm 5.76 | 88.92 ±\\pm 0.71 | 73.95 ±\\pm 1.46 | 30.78 ±\\pm 6.81 |
|  | V | 72.17 ±\\pm 0.36 | 62.74 ±\\pm 5.47 | 11.59 ±\\pm 2.55 | 94.69 ±\\pm 1.87 | 75.52 ±\\pm 0.89 | 4.74 ±\\pm 0.18 | 88.33 ±\\pm 0.90 | 73.91 ±\\pm 1.46 | 11.63 ±\\pm 2.90 |
|  | L | 66.88 ±\\pm 0.57 | 61.17 ±\\pm 7.11 | 10.97 ±\\pm 1.46 | 91.82 ±\\pm 3.32 | 54.64 ±\\pm 5.82 | 18.18 ±\\pm 5.70 | 88.29 ±\\pm 0.99 | 60.84 ±\\pm 0.97 | 23.20 ±\\pm 8.56 |
| CoDis | B | 74.71 ±\\pm 0.95 | 69.78 ±\\pm 1.34 | 18.68 ±\\pm 2.12 | 95.81 ±\\pm 0.10 | 91.79 ±\\pm 0.99 | 14.20 ±\\pm 3.44 | 90.94 ±\\pm 0.38 | 82.45 ±\\pm 0.13 | 22.34 ±\\pm 5.16 |
|  | V | 74.64 ±\\pm 0.56 | 67.01 ±\\pm 2.68 | 18.59 ±\\pm 1.17 | 95.61 ±\\pm 0.25 | 88.04 ±\\pm 1.97 | 5.62 ±\\pm 2.69 | 90.06 ±\\pm 1.09 | 78.64 ±\\pm 2.15 | 9.57 ±\\pm 0.60 |
|  | L | 72.81 ±\\pm 0.47 | 61.31 ±\\pm 2.35 | 13.15 ±\\pm 1.66 | 95.34 ±\\pm 0.09 | 87.30 ±\\pm 1.48 | 10.70 ±\\pm 2.87 | 90.60 ±\\pm 0.36 | 80.47 ±\\pm 0.53 | 7.65 ±\\pm 2.37 |
| JoCoR | B | 74.14 ±\\pm 1.19 | 66.76 ±\\pm 1.37 | 24.59 ±\\pm 3.64 | 92.86 ±\\pm 0.51 | 71.47 ±\\pm 3.94 | 20.82 ±\\pm 2.56 | 87.96 ±\\pm 0.57 | 75.04 ±\\pm 0.71 | 26.47 ±\\pm 2.84 |
|  | V | 73.04 ±\\pm 1.24 | 66.41 ±\\pm 2.18 | 16.83 ±\\pm 2.81 | 92.68 ±\\pm 0.62 | 70.52 ±\\pm 4.41 | 9.06 ±\\pm 1.58 | 87.57 ±\\pm 0.99 | 74.43 ±\\pm 0.60 | 17.12 ±\\pm 1.58 |
|  | L | 71.78 ±\\pm 0.79 | 53.69 ±\\pm 0.92 | 20.82 ±\\pm 1.12 | 92.14 ±\\pm 0.23 | 63.94 ±\\pm 0.62 | 10.69 ±\\pm 0.64 | 87.56 ±\\pm 0.27 | 63.75 ±\\pm 1.19 | 18.97 ±\\pm 0.39 |
| DISC | B | 80.35 ±\\pm 0.78 | 71.97 ±\\pm 0.58 | 23.69 ±\\pm 2.11 | 98.74 ±\\pm 0.19 | 93.24 ±\\pm 1.34 | 16.83 ±\\pm 6.95 | 89.90 ±\\pm 2.75 | 82.67 ±\\pm 0.86 | 25.00 ±\\pm 3.66 |
|  | V | 80.33 ±\\pm 1.13 | 68.73 ±\\pm 2.14 | 15.16 ±\\pm 3.78 | 98.41 ±\\pm 0.47 | 89.19 ±\\pm 0.52 | 1.91 ±\\pm 0.25 | 88.68 ±\\pm 2.97 | 80.66 ±\\pm 2.14 | 7.81 ±\\pm 1.06 |
|  | L | 79.49 ±\\pm 1.57 | 68.19 ±\\pm 1.15 | 10.97 ±\\pm 1.19 | 98.59 ±\\pm 0.26 | 88.83 ±\\pm 0.82 | 1.76 ±\\pm 0.41 | 88.99 ±\\pm 3.14 | 80.59 ±\\pm 0.14 | 8.14 ±\\pm 1.33 |
| DivideMix | B | 74.96 ±\\pm 0.83 | 66.93 ±\\pm 0.26 | 29.75 ±\\pm 1.85 | 98.32 ±\\pm 0.23 | 84.99 ±\\pm 8.46 | 15.94 ±\\pm 4.45 | 93.20 ±\\pm 0.05 | 83.47 ±\\pm 0.50 | 22.05 ±\\pm 0.12 |
|  | V | 72.37 ±\\pm 1.14 | 66.83 ±\\pm 0.41 | 14.76 ±\\pm 2.13 | 98.06 ±\\pm 0.37 | 90.46 ±\\pm 3.64 | 3.82 ±\\pm 0.48 | 92.58 ±\\pm 0.09 | 82.25 ±\\pm 1.36 | 15.26 ±\\pm 1.48 |
|  | L | 66.72 ±\\pm 0.39 | 66.86 ±\\pm 0.77 | 13.19 ±\\pm 3.38 | 97.58 ±\\pm 0.62 | 81.16 ±\\pm 3.74 | 5.42 ±\\pm 4.77 | 92.44 ±\\pm 0.24 | 76.78 ±\\pm 0.90 | 6.73 ±\\pm 0.71 |

#### 4.5.3 Analysis on Sample Selection

Next, we focus on sample selection and semi-supervised methods, which have been effective under instance dependent noise.
The sample selection methods in LNMBench are all derived from the Co-teaching, adopting the small-loss strategy in which the proportion of selected samples is determined by the known noise rate.
Next, we take the Co-teaching method as an example to analyze how the small-loss strategy performs under varying noise rates.
As shown in Fig. [5](https://arxiv.org/html/2512.09315v1#S4.F5 "Figure 5 ‣ 4.5.2 Analysis on Noise Transition Matrix Estimation ‣ 4.5 Results on Balanced Benchmark Dataset under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), most clean samples exhibit lower losses than noisy ones, making it feasible to distinguish them via the small-loss criterion under Idn-50%.
However, when the noise rate increases to 90%, the model rapidly overfit noisy labels, causing noisy samples to also present small losses.
Consequently, as shown in Fig [4](https://arxiv.org/html/2512.09315v1#S4.F4 "Figure 4 ‣ 4.5.2 Analysis on Noise Transition Matrix Estimation ‣ 4.5 Results on Balanced Benchmark Dataset under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), under Idn-50%, Co-teaching is able to select training samples with a high clean ratio while retaining nearly all clean samples, which leads to relatively high classification accuracy.
In contrast, under Idn-90%, the method fails to identify clean samples, resulting in significant performance degradation.

Under Idn-50% on the PathMNIST, we observed that a considerable proportion of noisy samples were still included in the clean set of DISC and DivideMix.
They also maintain a reasonably good classification accuracy, which indicates that the semi-supervised strategy can enhance the model’s robustness to label noise.
For Disc, this phenomenon mainly arises because some noisy samples, once incorrectly fitted by the model, gradually achieve higher prediction scores on their observed labels.
As the confidence threshold is dynamically updated during training, these scores eventually exceed the selection criterion, leading to their erroneous inclusion in the clean set.
DivideMix also adopts the small-loss strategy but does not use the noise rate as a threshold, which leads to fitting part of the noisy labels during the selection process.
As a result, the clean set inevitably contains some noisy samples.

Findings: Noise-robust regularization methods and transition matrix estimation methods are only effective under low noise ratio.
For PathMNIST with known noise rates, Co-teaching and CoDis, which based on small loss selection shows superior capability in identifying clean samples.
Semi-supervised methods do not rely on the known noise rate for sample selection, and therefore their selection ability is less effective, it effectively mitigates the impact of noisy labels through its semi-supervised learning strategy.
However, in real-world scenarios the noise rate is typically unknown, which makes such semi-supervised methods more practical.

### 4.6 Results on Imbalanced Datasets under Synthetic Noise

This section examines how class imbalance affects the robustness of LNL methods (see Table [2](https://arxiv.org/html/2512.09315v1#S4.T2 "Table 2 ‣ 4.5.2 Analysis on Noise Transition Matrix Estimation ‣ 4.5 Results on Balanced Benchmark Dataset under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).
We evaluate on three class imbalanced medical imaging datasets with instance-dependent noise (DermaMNIST, BloodMNIST, and OrganCMNIST.
We omit symmetric noise in this section, as it is less realistic in practice.

#### 4.6.1 Quantitative Results

For BloodMNIST, all methods attain high accuracy under Idn-20%.
Under Idn-50%, only Co-teaching, CoDis, and semi-supervised methods achieve high accuracy.
Under Idn-90%, all methods deteriorate to very low accuracy.
These methods exhibit the same trend on OrganCMNIST as on BloodMNIST.
For DermaMNIST, CDR achieves the highest accuracy under the Idn-20% setting, but suffers a substantial performance drop at Idn-50%.
Under Idn-50%, DISC attains the best results, followed closely by DivideMix and Co-teaching.
Under Idn-90%, all methods fail to maintain satisfactory performance.
Notably, under Idn-20%, both sample selection and semi-supervised methods perform worse than the standard CE baseline, whereas at Idn-50% they surpass CE.

To further investigate the underlying causes of this performance reversal on DermaMNIST, we present per-class accuracy results for four representative methods and CE (see Fig. [6(a)](https://arxiv.org/html/2512.09315v1#S4.F6.sf1 "In Figure 6 ‣ 4.6.1 Quantitative Results ‣ 4.6 Results on Imbalanced Datasets under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).
At Idn-20% setting, CDR consistently outperforms CE across all classes.
In contrast, DISC, CoDis and Co-teaching underperform CE in most classes except for class 5, which is the majority class in DermaMNIST.
At Idn-50%, CDR exhibits performance degradation across all classes, further confirming that regularization based methods fail under high noise levels (see Fig. [6(b)](https://arxiv.org/html/2512.09315v1#S4.F6.sf2 "In Figure 6 ‣ 4.6.1 Quantitative Results ‣ 4.6 Results on Imbalanced Datasets under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).
Meanwhile, DISC, CoDis and Co-teaching still underperform CE in most classes except for class 5.
These results suggest that sample selection based methods are ineffective on the DermaMNIST.

(a)Idn20%

(b)Idn50%

Figure 6: Per-class accuracy of representative methods under Idn-20% and Idn-50% on DermaMNIST.

(a)

(b)

(c)

(d)

Figure 7: Per-class performance comparison of Co-teaching and DISC methods on DermMNIST dataset with Idn-20% noise.
(a) Clean ratio of Co-teaching. (b) Coverage ratio of Co-teaching. (c) Clean ratio of DISC. (d) Coverage ratio of DISC.

#### 4.6.2 Why the Sample Selection Strategy Fails?

Next, we further investigate the reasons for the failure of sample selection methods, using DISC and Co-teaching under Idn-20% as examples.

Small loss strategy: As shown in the Fig. [7](https://arxiv.org/html/2512.09315v1#S4.F7 "Figure 7 ‣ 4.6.1 Quantitative Results ‣ 4.6 Results on Imbalanced Datasets under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), the Co-teaching method retains almost all clean samples of class 5 for training, thereby achieving high accuracy on this class.
In contrast, for class 3 and class 6, the method discards all clean samples at an early stage of training, resulting in zero accuracy for these classes.
For the remaining classes, most clean samples are retained for training.
However, their low clean ratios indicate that many noisy samples are also included, which leads to reduced classification accuracy.
The observed phenomenon can be explained by the distribution of losses across classes (see Fig. [8](https://arxiv.org/html/2512.09315v1#S4.F8 "Figure 8 ‣ 4.6.2 Why the Sample Selection Strategy Fails? ‣ 4.6 Results on Imbalanced Datasets under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).
For the majority class (class 5), clean samples tend to have significantly lower losses than noisy samples.
In contrast, for minority classes, some clean samples exhibit higher losses than noisy ones, with clean samples in classes 3 and 6 having losses exceeding those of most noisy samples.

Dynamic instance-specific selection: As shown in the Fig. [7](https://arxiv.org/html/2512.09315v1#S4.F7 "Figure 7 ‣ 4.6.1 Quantitative Results ‣ 4.6 Results on Imbalanced Datasets under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), the DISC method retains almost all clean samples of class 5 for training.
In contrast, the method discards all clean samples at an early stage of training for class 3.
For the remaining classes, although the clean ratio of the training samples is relatively high, the number of clean samples used for training decreases over time, leading to a decline in the model’s generalization capability.
This phenomenon occurs because the model fits noisy labels in the early stage of training, which lowers its confidence in clean labels and results in some clean samples being excluded from the training set.

Figure 8:
Violin plots of per-class clean sample losses and the overall noisy sample loss distribution for Co-teaching under Idn-20% on DermaMNIST.
Figure 9:
Epoch wise ratios of clean class 5 samples in the clean set and the purified set of DISC, normalized by the total number of samples under Idn-20% on DermaMNIST. The clean set refers to the subset of samples selected by the model as clean, while the purified set refers to the subset of excluded samples whose labels are reassigned by the model.

#### 4.6.3 Effect of the Correction Mechanism

We also observe that, although the Co-teaching method selects almost all clean samples from class 5 for training, its accuracy on this class is only comparable to that of standard CE under Idn-20%.
This is because many noisy samples with low losses are selected into the clean set, including a substantial portion of class 5 samples that are incorrectly assigned noisy labels.
It is noteworthy that the DISC method achieves the highest accuracy on class 5, as it not only selects clean samples but also corrects the labels of noisy samples.
As shown in the Fig. [9](https://arxiv.org/html/2512.09315v1#S4.F9 "Figure 9 ‣ 4.6.2 Why the Sample Selection Strategy Fails? ‣ 4.6 Results on Imbalanced Datasets under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), the clean set refers to the subset of samples selected by the model as clean, while the purified set refers to the subset of excluded samples whose labels are reassigned by the model.
We present the proportion of clean samples in the clean set and the purified set for class 5 relative to the total number of this class.
It can be observed that nearly all samples in this class are trained with correct labels.

Table 3: Performance comparison under instance-dependent noise on ImPathMNIST. Bold indicates the best result.

|     |     |     |     |
| --- | --- | --- | --- |
| Dataset |  | ImPathMNIST |  |
| Noise type |  | Idn-20% | Idn-50% |
|  | B | 88.19 ±\\pm 1.25 | 70.71 ±\\pm 1.87 |
| CE | V | 88.19 ±\\pm 1.25 | 70.68 ±\\pm 1.92 |
|  | L | 82.53 ±\\pm 1.43 | 55.24 ±\\pm 2.38 |
|  | B | 88.51 ±\\pm 0.38 | 80.12 ±\\pm 0.51 |
| SCE | V | 88.05 ±\\pm 0.67 | 73.24 ±\\pm 0.83 |
|  | L | 78.62 ±\\pm 2.58 | 55.34 ±\\pm 2.79 |
|  | B | 88.01 ±\\pm 0.65 | 80.71 ±\\pm 0.98 |
| CDR | V | 87.76 ±\\pm 0.28 | 80.71 ±\\pm 0.72 |
|  | L | 87.13 ±\\pm 0.43 | 60.76 ±\\pm 1.14 |
|  | B | 90.29 ±\\pm 0.45 | 76.34 ±\\pm 1.28 |
| Co-teaching | V | 90.23 ±\\pm 0.63 | 75.89 ±\\pm 0.94 |
|  | L | 87.58 ±\\pm 0.98 | 70.99 ±\\pm 1.02 |
|  | B | 89.38 ±\\pm 0.72 | 79.88 ±\\pm 1.16 |
| CoDis | V | 88.69 ±\\pm 1.08 | 72.13 ±\\pm 1.09 |
|  | L | 86.16 ±\\pm 1.02 | 71.85 ±\\pm 0.65 |
|  | B | 91.45 ±\\pm 0.38 | 80.70 ±\\pm 0.93 |
| DISC | V | 91.45 ±\\pm 0.41 | 77.42 ±\\pm 1.12 |
|  | L | 88.23 ±\\pm 1.24 | 72.04 ±\\pm 1.48 |
|  | B | 93.25 ±\\pm 0.95 | 79.16 ±\\pm 1.52 |
| DivideMix | V | 93.24 ±\\pm 0.34 | 74.09 ±\\pm 0.81 |
|  | L | 83.99 ±\\pm 1.42 | 70.40 ±\\pm 1.88 |

#### 4.6.4 Impact of Class Imbalance on LNL

To investigate the impact of class imbalance on LNL methods, we construct a long tailed version of the PathMNIST, denoted as ImPathMNIST.
Following the setting in \[ [29](https://arxiv.org/html/2512.09315v1#bib.bib29 "")\], we simulate a long-tailed distribution by downsampling each class according to an exponential decay rule.
Given kk classes and an imbalance ratio r=N0Nk−1r=\\frac{N\_{0}}{N\_{k-1}}, where N0N\_{0} is the number of samples in the most frequent (head) class, the number of samples for class j∈\[0,k)j\\in\[0,k) is calculated as:\
\
|     |     |     |     |\
| --- | --- | --- | --- |\
|  | Nj=N0⋅r−jk−1N\_{j}=N\_{0}\\cdot r^{-\\frac{j}{k-1}} |  | (2) |\
\
We use the number of samples in class 0 as N0N\_{0}, and set r=100r=100 to create the long-tailed distribution. For each class, we randomly select the top NjN\_{j} samples to form the final training set. This setting allows us to systematically evaluate the robustness of label noise methods under severe class imbalance.\
In this experiment, we excluded T-Revision, VolMinNet, JoCoR and Co-teaching+ due to their inferior performance.\
As shown in the Table [3](https://arxiv.org/html/2512.09315v1#S4.T3 "Table 3 ‣ 4.6.3 Effect of the Correction Mechanism ‣ 4.6 Results on Imbalanced Datasets under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), all methods, except SCE, outperform CE under both Idn-20% and Idn-50%.\
DISC achieves the best overall performance.\
As shown in the Fig. [10](https://arxiv.org/html/2512.09315v1#S4.F10 "Figure 10 ‣ 4.6.4 Impact of Class Imbalance on LNL ‣ 4.6 Results on Imbalanced Datasets under Synthetic Noise ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), we compare the per-class accuracy of CE and Co-teaching, DISC and CDR under Idn-20% with PathMNIST and ImPathMNIST.\
For PathMNIST, all methods outperform CE in every class.\
For ImPathMNIST, although DISC and Co-teaching achieve higher overall accuracy than CE, their performance on minority classes is inferior.\
In contrast, CDR consistently surpasses CE across all classes.\
These results indicate that the effectiveness of sample selection-based methods is sensitive to class imbalance.\
\
Findings:\
Based on sample selection methods rely on the model’s loss or confidence to select clean samples.\
However, in imbalanced datasets, some clean samples from minority classes exhibit higher losses than noisy samples during the early training stage, preventing them from being selected.\
This further limits the model’s ability to learn minority classes.\
Consequently, their performance on imbalanced datasets can be even worse than that of standard CE model.\
In addition, the correction mechanism enables the model to utilize noisy samples by relabeling them, leading to more complete and accurate training compared to pure sample selection methods.\
\
(a)PathMNIST\
\
(b)ImPathMNIST\
\
Figure 10: Per-class classification accuracy of four methods on (a) PathMNIST and (b) ImPathMNIST.\
\
### 4.7 Results on Real-world Noisy Datasets\
\
In this section, we evaluate the performance of LNL methods on real-world noisy datasets (see Table. [4](https://arxiv.org/html/2512.09315v1#S4.T4 "Table 4 ‣ 4.7.1 DRTiD ‣ 4.7 Results on Real-world Noisy Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook")).\
Specifically, we select two retinal image datasets, DRTid and Kaggle DR+, as well as a CT image dataset, CheXpert.\
\
#### 4.7.1 DRTiD\
\
As shown in Table [4](https://arxiv.org/html/2512.09315v1#S4.T4 "Table 4 ‣ 4.7.1 DRTiD ‣ 4.7 Results on Real-world Noisy Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), only SCE achieves higher performance than CE in terms of L, whereas all other methods underperform compared to CE.\
Sample selection based methods perform poorly on DRTiD, and CDR exhibits a performance gap of 15.45% between V and L.\
As shown in Fig. [11(a)](https://arxiv.org/html/2512.09315v1#S4.F11.sf1 "In Figure 11 ‣ 4.7.1 DRTiD ‣ 4.7 Results on Real-world Noisy Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), we further report the per-class accuracy of three representative methods and CE.\
SCE outperforms CE in every class except class 5.\
DISC is only effective on class 0, achieving the highest accuracy for this class while yielding near zero accuracy for all other classes.\
Co-teaching method achieves comparable accuracy to CE on the first three classes but fails completely on the last two classes.\
\
Table 4: Performance comparison on real-world noisy datasets.\
Bold indicates the best result,\
underline indicates the second best,\
and double underline indicates the third best.\
\
|     |     |     |     |     |\
| --- | --- | --- | --- | --- |\
|  |  | Real-world Datasets |  |  |\
| Dataset |  | DRTID | Kaggle DR+ | CheXpert |\
| CE | B | 61.46 ±\\pm 1.23 | 70.73 ±\\pm 1.42 | 43.07 ±\\pm 2.47 |\
|  | V | 59.36 ±\\pm 2.12 | 67.17 ±\\pm 1.71 | 34.31 ±\\pm 2.98 |\
|  | L | 46.36 ±\\pm 1.26 | 65.59 ±\\pm 1.85 | 37.08 ±\\pm 1.19 |\
| T-Revision | B | 54.24 ±\\pm 1.37 | 58.42 ±\\pm 1.61 | 40.52 ±\\pm 2.31 |\
|  | V | 53.63 ±\\pm 3.26 | 58.20 ±\\pm 1.35 | 35.76 ±\\pm 1.14 |\
|  | L | 40.18 ±\\pm 1.98 | 57.77 ±\\pm 0.97 | 33.57 ±\\pm 1.63 |\
| VolMinNet | B | 59.47 ±\\pm 0.66 | 61.62 ±\\pm 1.35 | 39.42 ±\\pm 2.58 |\
|  | V | 47.73 ±\\pm 1.79 | 57.39 ±\\pm 2.47 | 39.42 ±\\pm 1.72 |\
|  | L | 47.51 ±\\pm 0.77 | 54.19 ±\\pm 2.43 | 28.61 ±\\pm 1.49 |\
| SCE | B | 58.85 ±\\pm 0.68 | 66.13 ±\\pm 0.81 | 48.96 ±\\pm 1.54 |\
|  | V | 55.07 ±\\pm 0.76 | 65.50 ±\\pm 0.74 | 38.24 ±\\pm 1.72 |\
|  | L | 56.01 ±\\pm 0.95 | 65.86 ±\\pm 0.79 | 40.46 ±\\pm 1.48 |\
| CDR | B | 54.09 ±\\pm 0.82 | 70.19 ±\\pm 0.67 | 42.33 ±\\pm 1.41 |\
|  | V | 52.55 ±\\pm 0.58 | 67.49 ±\\pm 0.93 | 35.77 ±\\pm 1.27 |\
|  | L | 50.78 ±\\pm 1.37 | 67.93 ±\\pm 0.59 | 37.96 ±\\pm 2.16 |\
| Co-teaching | B | 48.18 ±\\pm 1.34 | 62.90 ±\\pm 1.63 | 37.22 ±\\pm 2.18 |\
|  | V | 36.86 ±\\pm 1.67 | 62.80 ±\\pm 0.74 | 35.76 ±\\pm 2.35 |\
|  | L | 38.25 ±\\pm 1.25 | 62.35 ±\\pm 0.89 | 35.33 ±\\pm 2.27 |\
| Co-teaching+ | B | 49.31 ±\\pm 1.26 | 53.99 ±\\pm 1.31 | 28.10 ±\\pm 1.37 |\
|  | V | 45.18 ±\\pm 2.74 | 53.28 ±\\pm 0.98 | 27.31 ±\\pm 1.45 |\
|  | L | 46.75 ±\\pm 2.13 | 51.48 ±\\pm 2.16 | 19.71 ±\\pm 2.19 |\
| CoDis | B | 49.64 ±\\pm 2.06 | 53.99 ±\\pm 2.85 | 37.72 ±\\pm 3.85 |\
|  | V | 42.57 ±\\pm 5.75 | 51.03 ±\\pm 2.48 | 35.95 ±\\pm 2.26 |\
|  | L | 41.80 ±\\pm 5.35 | 52.14 ±\\pm 2.38 | 34.26 ±\\pm 2.44 |\
| JoCoR | B | 47.09 ±\\pm 1.25 | 64.97 ±\\pm 1.84 | 39.78 ±\\pm 1.92 |\
|  | V | 44.28 ±\\pm 0.98 | 62.44 ±\\pm 1.06 | 33.94 ±\\pm 1.16 |\
|  | L | 41.26 ±\\pm 1.31 | 63.13 ±\\pm 0.71 | 35.04 ±\\pm 1.65 |\
| DISC | B | 48.18 ±\\pm 0.42 | 55.17 ±\\pm 0.87 | 40.15 ±\\pm 1.57 |\
|  | V | 44.27 ±\\pm 0.74 | 53.88 ±\\pm 1.08 | 33.57 ±\\pm 1.11 |\
|  | L | 45.22 ±\\pm 0.67 | 54.00 ±\\pm 0.61 | 31.39 ±\\pm 0.93 |\
| DivideMix | B | 53.64 ±\\pm 0.73 | 67.39 ±\\pm 0.36 | 33.58 ±\\pm 1.35 |\
|  | V | 52.73 ±\\pm 0.66 | 67.39 ±\\pm 0.83 | 33.58 ±\\pm 0.97 |\
|  | L | 41.09 ±\\pm 0.94 | 54.00 ±\\pm 0.86 | 21.17 ±\\pm 0.71 |\
| DivideMix+MedSSL | B | 59.50 ±\\pm 1.86 | 65.53 ±\\pm 1.42 | 41.06 ±\\pm 1.69 |\
|  | V | 56.95 ±\\pm 1.86 | 62.73 ±\\pm 1.48 | 38.20 ±\\pm 0.54 |\
|  | L | 50.73 ±\\pm 0.77 | 63.13 ±\\pm 1.95 | 35.01 ±\\pm 1.19 |\
| DISC+MedSSL | B | 62.61 ±\\pm 1.94 | 69.17 ±\\pm 0.63 | 44.95 ±\\pm 1.98 |\
|  | V | 58.24 ±\\pm 1.68 | 68.90 ±\\pm 0.95 | 41.16 ±\\pm 1.25 |\
|  | L | 57.18 ±\\pm 0.79 | 68.47 ±\\pm 1.03 | 40.71 ±\\pm 1.28 |\
\
(a)\
\
(b)\
\
(c)\
\
Figure 11: Per-class classification accuracy of four methods on (a) DRTiD (b) Kaggle DR+ and (c) CheXpert.\
\
#### 4.7.2 Kaggle DR+\
\
As shown in Table [4](https://arxiv.org/html/2512.09315v1#S4.T4 "Table 4 ‣ 4.7.1 DRTiD ‣ 4.7 Results on Real-world Noisy Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), only SCE and CDR achieve slightly better performance than CE on Kaggle DR+.\
Sample selection based methods perform poorly on Kaggle DR+.\
As shown in Fig. [11(b)](https://arxiv.org/html/2512.09315v1#S4.F11.sf2 "In Figure 11 ‣ 4.7.1 DRTiD ‣ 4.7 Results on Real-world Noisy Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), we further report the per-class accuracy of three representative methods and CE.\
All methods surpass CE only in class 0, while in other classes their performance falls behind CE.\
DISC is only effective on class 0, achieving the highest accuracy for this class while yielding near zero accuracy for all other classes.\
Co-teaching achieves comparable accuracy to CE on the class 0 but fails completely on the other classes.\
Although SCE achieves better performance than the other two methods on minority classes, its performance remains inferior to that of CE.\
Due to the lack of ground-truth labels, we refrain from performing further analysis on this dataset.\
\
#### 4.7.3 CheXpert\
\
As shown in Table [4](https://arxiv.org/html/2512.09315v1#S4.T4 "Table 4 ‣ 4.7.1 DRTiD ‣ 4.7 Results on Real-world Noisy Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), only SCE and CDR achieve slightly better performance than CE on CheXpert.\
Sample selection based methods perform poorly on the CheXpert.\
We further report the per-class accuracy of three representative methods and CE.\
All methods achieve the highest accuracy on class 4, which is the majority class.\
As shown in Fig. [11(c)](https://arxiv.org/html/2512.09315v1#S4.F11.sf3 "In Figure 11 ‣ 4.7.1 DRTiD ‣ 4.7 Results on Real-world Noisy Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), the accuracy of these three methods exceeds that of CE only for class 4.\
We also notice that some methods yield zero accuracy on certain classes, further suggesting that existing label noise approaches are not well suited for real-world noisy data.\
\
Findings: Current LNL methods perform poorly on real-world medical datasets, in some cases even underperforming standard CE model.\
Moreover, semi-supervised methods that perform well on synthetic noisy datasets often fail to achieve comparable performance on real-world noisy medical datasets.\
\
### 4.8 Summary\
\
Our experiments highlight several limitations of existing LNL methods in medical imaging.\
\
- •\
\
\
Pure sample-selection methods offer limited practical value since they assume access to the noise rate, which is rarely available in deployment.\
Both sample selection and semi-supervised methods are further affected by class imbalance, where minority-class examples are often misclassified as noise.\
\
- •\
\
\
Noise-robust regularization methods are only effective under low noise levels, and transition matrix estimation methods, typically designed for class-conditional noise.\
\
- •\
\
\
Existing methods fail under severe noise conditions, including high noise levels and real-world noise.\
\
- •\
\
\
There is a shortage of real-world noisy datasets with reliable ground-truth labels.\
Such resources are essential to analyze why current methods fail under real-world medical noise conditions.\
\
\
Therefore, future research could benefit from the following directions.\
\
- •\
\
\
Future research should focus on designing more effective sample selection strategy to alleviate the impact of class imbalance and severe noise.\
In particular, purified label strategies hold promise, as they can not only support semi-supervised training but also serve as a means of data cleansing, which is especially valuable in medical image analysis.\
\
- •\
\
\
Unlike anchor-based methods that produce a class-conditional transition matrix, instance-dependent transition matrix estimation approaches estimate a transition matrix for each individual sample, thereby capturing sample-specific noise characteristics.\
\
- •\
\
\
Both methods can be further enhanced by incorporating noise-robust regularization techniques to improve stability and generalization.\
\
\
## 5 MedSSL\
\
Motivated by these findings, we next focus on improving semi-supervised methods \[ [24](https://arxiv.org/html/2512.09315v1#bib.bib24 ""), [22](https://arxiv.org/html/2512.09315v1#bib.bib22 "")\] to more effectively address label noise in medical image analysis.\
From the above experiments, we observe three major challenge.\
First, models tend to overfit noisy labels at warm-up stage.\
Second, the methods can inadvertently admit noisy samples into the clean set.\
Third, under class imbalance, minority-class examples, being few and harder to learn, are often misjudged as noise and excluded from the clean set.\
Specifically, previous methods penalize over-confident predictions by adding a negative-entropy regularizer to the cross entropy loss \[ [22](https://arxiv.org/html/2512.09315v1#bib.bib22 "")\] to prevent rapid overfitting to noisy labels during warm-up stage.\
\
|     |     |     |     |\
| --- | --- | --- | --- |\
|  | ℋ=−∑k=0Kp(k∣x)logp(k∣x),\\mathcal{H}=-\\sum\_{k=0}^{K}p(k\\mid x)\\,\\log p(k\\mid x), |  | (3) |\
\
where KK denotes the number of classes and p⁡(k∣x)p(k\\mid x) is the model’s predicted probability that sample xx belongs to class kk.\
While the negative-entropy regularizer effectively prevents overfitting to noisy labels during warm-up, it tends to delay confident predictions for minority classes, thereby amplifying the adverse effects of class imbalance in the early stage.\
Therefore, we employ label smoothing to mitigate overfitting to noisy labels in warm-up stage.\
We observe that regularization methods can effectively suppress the influence of noisy labels during training.\
Therefore, we introduce Reverse Cross-Entropy (RCE) \[ [40](https://arxiv.org/html/2512.09315v1#bib.bib40 "")\] into the clean set objective.\
The RCE loss is defined as:\
\
|     |     |     |     |\
| --- | --- | --- | --- |\
|  | Lr​c​e(x)=−∑k=1Kp(k∣x)logq(k∣x),L\_{rce}(x)=-\\sum\_{k=1}^{K}p(k\\mid x)\\,\\log q(k\\mid x), |  | (4) |\
\
where KK is the number of classes; p⁡(k∣x)p(k\\mid x) is the model’s predicted probability that sample xx belongs to class kk, q⁡(k∣x)q(k\\mid x) is the target label distribution for xx.\
\
|     |     |     |     |\
| --- | --- | --- | --- |\
|  | Lc=Lc​e+Lr​c​e,L\_{c}=L\_{ce}+L\_{rce}, |  | (5) |\
\
In semi-supervised methods, confidence-based thresholding is commonly employed to construct the clean set.\
However, since majority classes tend to achieve higher prediction confidence while minority classes exhibit lower confidence, using a unified threshold biases the clean set towards majority classes and excludes most of the minority-class samples.\
Let nkn\_{k} be the number of samples in class kk (k∈{1,…,K}k\\in\\{1,\\dots,K\\}), and let nminn\_{\\min} and nmaxn\_{\\max} denote the minimum and maximum class counts, respectively. We first obtain a log-scale normalized factor:\
\
|     |     |     |     |\
| --- | --- | --- | --- |\
|  | αk=log⁡nk−log⁡nminlog⁡nmax−log⁡nmin+ε,αk∈\[0,1),\\alpha\_{k}\\;=\\;\\frac{\\log n\_{k}-\\log n\_{\\min}}{\\log n\_{\\max}-\\log n\_{\\min}+\\varepsilon}\\,,\\qquad\\alpha\_{k}\\in\[0,1)\\,, |  | (6) |\
\
where ε>0\\varepsilon>0 is a small constant for numerical stability.\
Given two bounds λhead\\lambda\_{\\text{head}} (for head classes) and λtail\\lambda\_{\\text{tail}} (for tail classes), the threshold for class kk is\
\
|     |     |     |     |\
| --- | --- | --- | --- |\
|  | λk=λhead−(λhead−λtail)​αk.\\lambda\_{k}\\;=\\;\\lambda\_{\\text{head}}\\;-\\;\\bigl(\\lambda\_{\\text{head}}-\\lambda\_{\\text{tail}}\\bigr)\\,\\alpha\_{k}\\,. |  | (7) |\
\
We evaluate our modifications on three real-world noisy datasets.\
As shown in Table [4](https://arxiv.org/html/2512.09315v1#S4.T4 "Table 4 ‣ 4.7.1 DRTiD ‣ 4.7 Results on Real-world Noisy Datasets ‣ 4 Experiments ‣ Benchmarking Real-World Medical Image Classification with Noisy Labels: Challenges, Practice, and Outlook"), the modified DISC achieves the highest accuracy across all three datasets.\
Although the modified DivideMix \[ [22](https://arxiv.org/html/2512.09315v1#bib.bib22 "")\] still underperforms compared to the regularization method and standard CE, it nonetheless shows substantial improvements over its original version.\
This is mainly because DivideMix \[ [22](https://arxiv.org/html/2512.09315v1#bib.bib22 "")\] relies on the small-loss strategy to select clean samples, and our previous experiments have demonstrated that this strategy is susceptible to class imbalance.\
For instance, on DRTiD \[ [13](https://arxiv.org/html/2512.09315v1#bib.bib13 "")\], the L metric improves by 9.64% after our modification.\
Although our modifications bring improvements, the overall performance on real-world noisy medical datasets is still limited.\
This suggests that semi-supervised strategies for LNL methods in medical imaging have considerable room for further improvement.\
\
## 6 Conclusion\
\
We built LNMBench of LNL methods for medical image analysis and evaluated them on both synthetic and real-world datasets.\
We revealed the limitations of existing approaches, showing that they remain inadequate for real-world medical scenarios, particularly under real-world noise and high ratio noise.\
By providing these insights together with our open-source implementation, we aim to support the community and inspire future research on robust learning with noisy labels in medical imaging.\
Guided by these findings, we further introduce a semi-supervised approach with minor modifications to mitigate clean set contamination and improve performance on minority classes in medical imaging.\
\
Limitations and Future Works This study has several limitations. First, due to the lack of publicly available implementations, we did not include label-noise learning methods specifically designed for medical datasets in our benchmark. Second, our proposed modifications only led to marginal improvements over existing semi-supervised methods.\
Future work will expand the benchmark to include real-world noisy medical datasets, more specialized LNL methods for medical images, and diversified evaluation metrics.\
We also aim to maintain LNMBench as an open, evolving platform to foster fair and reproducible research in this field.\
\
## Acknowledgements\
\
This work is supported by JST SPRING JPMJSP2102 and JST BOOST JPMJBY24D6.\
\
## References\
\
- \[1\]\
Chen, M., Cheng, H., Du, Y., Xu, M., Jiang, W., Wang, C., 2023.\
\
Two wrongs don’t make a right: Combating confirmation bias in learning with label noise, in: Proceedings of the AAAI Conference on Artificial Intelligence, pp. 14765–14773.\
\
- \[2\]\
Chen, P., Liao, B.B., Chen, G., Zhang, S., 2019.\
\
Understanding and utilizing deep neural networks trained with noisy labels, in: International conference on machine learning, PMLR. pp. 1062–1070.\
\
- \[3\]\
Cordeiro, F.R., Carneiro, G., 2020.\
\
A survey on deep learning with noisy labels: How to train your model when you cannot trust on the annotations?, in: 2020 33rd SIBGRAPI conference on graphics, patterns and images (SIBGRAPI), IEEE. pp. 9–16.\
\
- \[4\]\
Dgani, Y., Greenspan, H., Goldberger, J., 2018.\
\
Training a neural network based on unreliable human annotation of medical images, in: 2018 IEEE 15th International symposium on biomedical imaging (ISBI 2018), IEEE. pp. 39–42.\
\
- \[5\]\
Dosovitskiy, A., 2020.\
\
An image is worth 16x16 words: Transformers for image recognition at scale.\
\
arXiv preprint arXiv:2010.11929 .\
\
- \[6\]\
Gehlot, S., Gupta, A., Gupta, R., 2021.\
\
A cnn-based unified framework utilizing projection loss in unison with label noise handling for multiple myeloma cancer diagnosis.\
\
Medical Image Analysis 72, 102099.\
\
- \[7\]\
Ghesu, F.C., Georgescu, B., Gibson, E., Guendel, S., Kalra, M.K., Singh, R., Digumarthy, S.R., Grbic, S., Comaniciu, D., 2019.\
\
Quantifying and leveraging classification uncertainty for chest radiograph assessment, in: International conference on medical image computing and computer-assisted intervention, Springer. pp. 676–684.\
\
- \[8\]\
Gutbrod, M., Rauber, D., Nunes, D.W., Palm, C., 2025.\
\
Openmibood: Open medical imaging benchmarks for out-of-distribution detection, in: Proceedings of the Computer Vision and Pattern Recognition Conference, pp. 25874–25886.\
\
- \[9\]\
Han, B., Yao, Q., Yu, X., Niu, G., Xu, M., Hu, W., Tsang, I., Sugiyama, M., 2018.\
\
Co-teaching: Robust training of deep neural networks with extremely noisy labels.\
\
Advances in neural information processing systems 31.\
\
- \[10\]\
He, K., Zhang, X., Ren, S., Sun, J., 2016.\
\
Deep residual learning for image recognition, in: Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 770–778.\
\
- \[11\]\
Hendrycks, D., Lee, K., Mazeika, M., 2019.\
\
Using pre-training can improve model robustness and uncertainty, in: International conference on machine learning, PMLR. pp. 2712–2721.\
\
- \[12\]\
Hou, J., Xu, J., Feng, R., Chen, H., 2025.\
\
Qmix: Quality-aware learning with mixed noise for robust retinal disease diagnosis.\
\
IEEE Transactions on Medical Imaging .\
\
- \[13\]\
Hou, J., Xu, J., Xiao, F., Zhao, R.W., Zhang, Y., Zou, H., Lu, L., Xue, W., Feng, R., 2022.\
\
Cross-field transformer for diabetic retinopathy grading on two-field fundus images, in: 2022 IEEE International Conference on Bioinformatics and Biomedicine (BIBM), IEEE Computer Society. pp. 985–990.\
\
- \[14\]\
Johnson, A.E., Pollard, T.J., Greenbaum, N.R., Lungren, M.P., Deng, C.y., Peng, Y., Lu, Z., Mark, R.G., Berkowitz, S.J., Horng, S., 2019.\
\
Mimic-cxr-jpg, a large publicly available database of labeled chest radiographs.\
\
arXiv preprint arXiv:1901.07042 .\
\
- \[15\]\
Ju, L., Wang, X., Wang, L., Mahapatra, D., Zhao, X., Zhou, Q., Liu, T., Ge, Z., 2022.\
\
Improving medical images classification with label noise using dual-uncertainty estimation.\
\
IEEE transactions on medical imaging 41, 1533–1546.\
\
- \[16\]\
Ju, L., Yan, S., Zhou, Y., Nan, Y., Xing, X., Duan, P., Ge, Z., 2024.\
\
Monica: Benchmarking on long-tailed medical image classification.\
\
arXiv preprint arXiv:2410.02010 .\
\
- \[17\]\
Ju, L., Yu, Z., Wang, L., Zhao, X., Wang, X., Bonnington, P., Ge, Z., 2023.\
\
Hierarchical knowledge guided learning for real-world retinal disease recognition.\
\
IEEE Transactions on Medical Imaging 43, 335–350.\
\
- \[18\]\
Karimi, D., Dou, H., Warfield, S.K., Gholipour, A., 2020.\
\
Deep learning with noisy labels: Exploring techniques and remedies in medical image analysis.\
\
Medical image analysis 65, 101759.\
\
- \[19\]\
Khanal, B., Bhattarai, B., Khanal, B., Linte, C.A., 2023.\
\
Improving medical image classification in noisy labels using only self-supervised pretraining, in: MICCAI Workshop on Data Engineering in Medical Imaging, Springer. pp. 78–90.\
\
- \[20\]\
Ko, J., Yi, B., Yun, S.Y., 2023.\
\
A gift from label smoothing: robust training with adaptive label smoothing via auxiliary classifier under label noise, in: Proceedings of the AAAI Conference on Artificial Intelligence, pp. 8325–8333.\
\
- \[21\]\
Li, J., Cao, H., Wang, J., Liu, F., Dou, Q., Chen, G., Heng, P.A., 2023a.\
\
Learning robust classifier for imbalanced medical image dataset with noisy labels by minimizing invariant risk, in: International Conference on Medical Image Computing and Computer-Assisted Intervention, Springer. pp. 306–316.\
\
- \[22\]\
Li, J., Socher, R., Hoi, S.C., 2020.\
\
Dividemix: Learning with noisy labels as semi-supervised learning.\
\
arXiv preprint arXiv:2002.07394 .\
\
- \[23\]\
Li, X., Liu, T., Han, B., Niu, G., Sugiyama, M., 2021.\
\
Provably end-to-end label-noise learning without anchor points, in: International conference on machine learning, PMLR. pp. 6403–6413.\
\
- \[24\]\
Li, Y., Han, H., Shan, S., Chen, X., 2023b.\
\
Disc: Learning from noisy labels via dynamic instance-specific selection and correction, in: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 24070–24079.\
\
- \[25\]\
Liao, Z., Hu, S., Xie, Y., Xia, Y., 2025a.\
\
Instance-dependent label distribution estimation for learning with label noise.\
\
International Journal of Computer Vision 133, 2568–2580.\
\
- \[26\]\
Liao, Z., Hu, S., Zhang, Y., Xia, Y., 2025b.\
\
Unleashing the potential of open-set noisy samples against label noise for medical image classification.\
\
Medical Image Analysis , 103702.\
\
- \[27\]\
Lin, Y., Yao, Y., Liu, T., 2024.\
\
Learning the latent causal structure for modeling label noise.\
\
Advances in Neural Information Processing Systems 37, 120549–120577.\
\
- \[28\]\
Litjens, G., Kooi, T., Bejnordi, B.E., Setio, A.A.A., Ciompi, F., Ghafoorian, M., Van Der Laak, J.A., Van Ginneken, B., Sánchez, C.I., 2017.\
\
A survey on deep learning in medical image analysis.\
\
Medical image analysis 42, 60–88.\
\
- \[29\]\
Liu, Z., Miao, Z., Zhan, X., Wang, J., Gong, B., Yu, S.X., 2019.\
\
Large-scale long-tailed recognition in an open world, in: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 2537–2546.\
\
- \[30\]\
Lukasik, M., Bhojanapalli, S., Menon, A., Kumar, S., 2020.\
\
Does label smoothing mitigate label noise?, in: International Conference on Machine Learning, PMLR. pp. 6448–6458.\
\
- \[31\]\
Mehrtens, H.A., Kurz, A., Bucher, T.C., Brinker, T.J., 2023.\
\
Benchmarking common uncertainty estimation methods with histopathological images under domain shift and label noise.\
\
Medical image analysis 89, 102914.\
\
- \[32\]\
Menze, B.H., Jakab, A., Bauer, S., Kalpathy-Cramer, J., Farahani, K., Kirby, J., Burren, Y., Porz, N., Slotboom, J., Wiest, R., et al., 2014.\
\
The multimodal brain tumor image segmentation benchmark (brats).\
\
IEEE transactions on medical imaging 34, 1993–2024.\
\
- \[33\]\
Nguyen, D.T., Mummadi, C.K., Ngo, T.P.N., Nguyen, T.H.P., Beggel, L., Brox, T., 2019.\
\
Self: Learning to filter noisy labels with self-ensembling.\
\
arXiv preprint arXiv:1910.01842 .\
\
- \[34\]\
Pham, H.H., Le, T.T., Tran, D.Q., Ngo, D.T., Nguyen, H.Q., 2021.\
\
Interpreting chest x-rays via cnns that exploit hierarchical disease dependencies and uncertainty labels.\
\
Neurocomputing 437, 186–194.\
\
- \[35\]\
Shi, J., Zhang, K., Guo, C., Yang, Y., Xu, Y., Wu, J., 2024.\
\
A survey of label-noise deep learning for medical image analysis.\
\
Medical image analysis 95, 103166.\
\
- \[36\]\
Shin, H.C., Roth, H.R., Gao, M., Lu, L., Xu, Z., Nogues, I., Yao, J., Mollura, D., Summers, R.M., 2016.\
\
Deep convolutional neural networks for computer-aided detection: Cnn architectures, dataset characteristics and transfer learning.\
\
IEEE transactions on medical imaging 35, 1285–1298.\
\
- \[37\]\
Sukhbaatar, S., Bruna, J., Paluri, M., Bourdev, L., Fergus, R., 2014.\
\
Training convolutional networks with noisy labels.\
\
arXiv preprint arXiv:1406.2080 .\
\
- \[38\]\
Tanno, R., Saeedi, A., Sankaranarayanan, S., Alexander, D.C., Silberman, N., 2019.\
\
Learning from noisy labels by regularized estimation of annotator confusion, in: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 11244–11253.\
\
- \[39\]\
Wang, X., Peng, Y., Lu, L., Lu, Z., Bagheri, M., Summers, R.M., 2017.\
\
Chestx-ray8: Hospital-scale chest x-ray database and benchmarks on weakly-supervised classification and localization of common thorax diseases, in: Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 2097–2106.\
\
- \[40\]\
Wang, Y., Ma, X., Chen, Z., Luo, Y., Yi, J., Bailey, J., 2019.\
\
Symmetric cross entropy for robust learning with noisy labels, in: Proceedings of the IEEE/CVF international conference on computer vision, pp. 322–330.\
\
- \[41\]\
Wei, H., Feng, L., Chen, X., An, B., 2020.\
\
Combating noisy labels by agreement: A joint training method with co-regularization, in: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 13726–13735.\
\
- \[42\]\
Wei, J., Zhu, Z., Cheng, H., Liu, T., Niu, G., Liu, Y., 2021.\
\
Learning with noisy labels revisited: A study using real-world human annotations.\
\
arXiv preprint arXiv:2110.12088 .\
\
- \[43\]\
Xia, X., Han, B., Zhan, Y., Yu, J., Gong, M., Gong, C., Liu, T., 2023.\
\
Combating noisy labels with sample selection by mining high-discrepancy examples, in: Proceedings of the IEEE/CVF international conference on computer vision, pp. 1833–1843.\
\
- \[44\]\
Xia, X., Liu, T., Han, B., Gong, C., Wang, N., Ge, Z., Chang, Y., 2020a.\
\
Robust early-learning: Hindering the memorization of noisy labels, in: International conference on learning representations.\
\
- \[45\]\
Xia, X., Liu, T., Han, B., Wang, N., Gong, M., Liu, H., Niu, G., Tao, D., Sugiyama, M., 2020b.\
\
Part-dependent label noise: Towards instance-dependent label noise.\
\
Advances in neural information processing systems 33, 7597–7610.\
\
- \[46\]\
Xia, X., Liu, T., Wang, N., Han, B., Gong, C., Niu, G., Sugiyama, M., 2019.\
\
Are anchor points really indispensable in label-noise learning?\
\
Advances in neural information processing systems 32.\
\
- \[47\]\
Xue, C., Dou, Q., Shi, X., Chen, H., Heng, P.A., 2019.\
\
Robust learning at noisy labeled medical images: Applied to skin lesion classification, in: 2019 IEEE 16th International symposium on biomedical imaging (ISBI 2019), IEEE. pp. 1280–1283.\
\
- \[48\]\
Yang, J., Shi, R., Wei, D., Liu, Z., Zhao, L., Ke, B., Pfister, H., Ni, B., 2023.\
\
Medmnist v2-a large-scale lightweight benchmark for 2d and 3d biomedical image classification.\
\
Scientific Data 10, 41.\
\
- \[49\]\
Yu, X., Han, B., Yao, J., Niu, G., Tsang, I., Sugiyama, M., 2019.\
\
How does disagreement help generalization against label corruption?, in: International conference on machine learning, PMLR. pp. 7164–7173.\
\
- \[50\]\
Zhou, T., Wang, S., Bilmes, J., 2020.\
\
Robust curriculum learning: from clean label detection to noisy label self-correction, in: International conference on learning representations.