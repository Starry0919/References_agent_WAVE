<!-- Page 1 -->

Progress and Opportunities of Foundation Models in Bioinformatics
Qing Li1, Zhihang Hu1, Yixuan Wang1, Lei Li1, Yimin Fan1, Irwin King1, Le Song2,*, Yu Li1,*
1Department of Computer Science and Engineering, Chinese University of Hong Kong, Hong Kong SAR, China
2BioMap, Beijing, China
Abstract
Bioinformatics has witnessed a paradigm shift with the increasing integration of artificial intelligence (AI), particularly
through the adoption of foundation models (FMs). These AI techniques have rapidly advanced, addressing historical
challenges in bioinformatics such as the scarcity of annotated data and the presence of data noise. FMs are particularly
adept at handling large-scale, unlabeled data, a common scenario in biological contexts due to the time-consuming
and costly nature of experimentally determining labeled data. This characteristic has allowed FMs to excel and achieve
notable results in various downstream validation tasks, demonstrating their ability to represent diverse biological
entities effectively. Undoubtedly, FMs have ushered in a new era in computational biology, especially in the realm of
deep learning. The primary goal of this survey is to conduct a systematic investigation and summary of FMs in
bioinformatics, tracing their evolution, current research status, and the methodologies employed. Central to our focus
is the application of FMs to specific biological problems, aiming to guide the research community in choosing
appropriate FMs for their research needs. These downstream specialized tasks include sequence analysis, structure
prediction, function annotation, and multimodal integration. In each section, we delve into the specifics of the problem
at hand. We compare the structures and advancements of FMs against traditional methods, emphasizing their
applications across different biological domains. Furthermore, the review analyses challenges and limitations faced
by FMs in biology, such as data noise, model explainability, and potential biases. This analysis provides a theoretical
foundation for understanding why certain FMs might underperform in specific tasks. Finally, we outline potential
development paths and strategies for FMs in future biological research, setting the stage for continued innovation and
application in this rapidly evolving field. This comprehensive review serves not only as an academic resource but also
as a roadmap for future explorations and applications of FMs in biology.
Bioinformatics brings efforts to discovering meaningful insights from amino acid sequences, protein structures, single-cell
transcriptomics, bio-medical text and images, and other diverse biological data. These efforts facilitate crucial applications
such as disease detection, drug design, novel therapy discovery, etc., but have limited generalizability and may need substantial
customization on specific datasets over decades [Hughes et al., 2011; Bommasani et al., 2021]. On the contrary, artificial
intelligence (AI), powered by increasing data availability and computational resources, offers an alternative approach [Topol
et al., 2019] to obtain characteristics of biological insights by integrating deep learning mechanisms such as multilayer
perceptron (MLP) for nonlinear features [Park et al., 2016], convolutional neural network (CNN) for image features [Wang et
al., 2018], recurrent neural network (RNN) for time series features [Shen et al., 2021], transformer for natural language features
[Whalen et al., 2016], graph neural network (GCN) for features represented as graph [Forster et al., 2022], and graph attention
network (GAT) targets graph features with distinct attention [Dong et al., 2022]. Foundation models focus on pre-training
large-scale models from massive data to obtain generalizable features that can be easily adapted to downstream tasks in a fine-
tuned, few-shot, or zero-shot manner and can significantly boost performance, thus giving them growing attention and
popularity in the field of AI [Mahmud et al., 2018]. Currently, general purpose FMs consist of digital data of different modes
pre-trained and finetuned for computer applications of interest (Fig. 1(i)). They have been firmly established as the state-of-
the-art approach for question answering [Wiggins et al., 2022], video games [Baker et al., 2022], AI education [Tack et al.,
2022], medical AI [Moor et al., 2023], and other applications in computer science.
Recently, foundation models have deciphered immense potential in bioinformatics. A key strength of FMs lies in their
capacity to learn dependable representations of intricate biological datasets. This is facilitated by data-intensive pre-training, a
process that researchers can easily utilize for various downstream tasks with limited data through fine-tuning mechanisms (e.g.,
transfer learning for varying scale biological targets on a pre-trained foundation model), which makes it easier for researchers
*Correspondence to: liyu@cse.cuhk.edu.hk (Y. L.) and songle@biomap.com (L. S.).
1

---

<!-- Page 2 -->

(ii) Foundation Models in Bioinformatics
Biological Datasets Foundation Models Core Biological Problems
Sequence Analysis
RNA
Sequenced Genome Phylodynamics
Annotated
DNA
Protein-protein Interactions
Structure Construction
Genome
Protein Secondary Structure
Unsupervised Pre-trained FMs
Protein 3D Structure
Input
Function Prediction
Protein Novel Data
Generation
Knowledge Graph / Networks
Figure. 1 Foundation Models (FMs) in Artificial Intelligence and Bioinformatics. (i) Foundation models in artificial
intelligence. General purpose FMs are mainly pre-trained on diverse digital data and finetuned for extensive computer
applications such as question-answering systems, image design, and computer games. (ii) Foundation models in
bioinformatics. FMs in bioinformatics mainly focus on core biological problems including biological sequence analysis,
biological structure construction, and biological function prediction on both labeled and unlabeled biological datasets. They
can be pre-trained (supervised, semi-supervised, unsupervised) on multiple phases of biological data for various downstream
tasks. Based on the pretraining architectures of the foundation model, they can be classified into supervised FMs to capture
complex patterns and relationships within the labeled data, and unsupervised FMs to generate new representations not observed
in the unannotated training data. (iii) Deep learning modules. Deep learning modules are the cornerstone in building deep
learning methods, such as multi-layer perception (MLP), convolutional neural network (CNN), AutoEncoder, graph
convolutional network (GCN), and transformer (dash arrows represent low attention). Notably, the GCN particularly effective
for analyzing undirected graphs has not been employed in FMs. All these deep learning modules can be trained in an end-to-
end manner and improve computational efficiency by the parallel processing mechanism.
2
gninraeL
peeD
seludoM
Supervised Pre-trained FMs
Input Label
A
B
Association Prediction
gninraeL
peeD
seludoM
(i) Foundation Models in Artificial Intelligence
Digital data of different modes Computer Applications
L si o t r a e m m e i t p , s c u o m ns d e o c l t o e r t ur Pre-trained Module Finetuned Module Nat P u r r o al c L es a s n i g n u g age
adipiscing elit, sed do
eiusmod tempor
incididunt ut labore et
dolore magna aliqua.
Texts Graphs/Networks Design Game
Computer Vision
Video
Images Audio Question Answering
Classification
Regression
TF TF
Target gene Enhancer Promoter
Gene Regulation Diagram
Cell Type Annotation
(iii) Deep Learning Modules
Multi-layer Perception Convolutional Neural Network Graph Convolutional Neural Network AutoEncoder Transformer
...
...
...
RNA Secondary Structure
Single Cell
RNA 3D Structure
Unannotated

---

<!-- Page 3 -->

Deep Learning
Foundation Model
Foundation Model in Bioinformatics
In c t D o ro n e 2 f c d e 0 i e u p r 0 s p c 6 t A t e i o E D n L G 2 0 A 1 N 4 D 20 A 1 N A 5 2 le 0 x 1 N 6 R e 2 e t T 0 s r 1 N a 6 n e 2 t s 0 f 1 o 7 r G 2 m 0 C R 1 e N r 7 e 2 s 0 N 1 e 7 G 2 X 0 A t 1 T 8 2 C 0 B B 2 1 E T 0 9 R 19 T SimC U L B R n B i i V o io m t L B e e x E K d t R B i - c B T i a o E l m B R L e T d U ic R C a B l L F t I e l P o x r t e L n E V c n e D M fo N rm A E D P S e r N o M r A te - B B i 1 n D B i b E o N i E R o A L m T te E e x C d t i R T ca N R R l S A A N s i c n - A F B g B M l E e io R B c m T e io l e l B di A c G B B a R e R l i E T o n t B R e m o P x m T i C e m t - d e o a i C c g P a R a e l r G o P te t N r P e x o i r t 2 n t o , G te P P P G i B T n r r N e o E o 2 n t e t R e e e t i w i f T n n o - o rm rk B P P er r i r i o o m o m G t a e G e e g in n d M e, i c x A v a T i I l d r t i P e e m o r x o o t t , P e M G B in i L e o d M m t - e P e x C d a t L L i H P c A M a y ro l P B e G t n E e i e o a i - n n D m D o N B e m M d A e ic S a D A l N i G m A e a B n g o E e m R S e T i s n c - g b 2 G l i e o P m c T P P e e r o l o d l r t i t e c S U i a n T P l n , r t i o e - T t x M N e r t i G a u n o n c e I B s l n f e o i o o o m B r t m m i i d e o e e e B d r i G E c s a R c e l G n T t o P e m x T t e
2000 2020 2021 2022 2023
2 G 0 P 0 U 9 Al 2 p 0 h 1 a 6 Go Alp 2 h 0 a 2 F 0 old Alp 2 h 0 a 2 F 1 old2 Ch 2 a 0 tG 22 PT G 20 P 2 T 3 4 FMs in Bioinformatics Supervised Model
Growth A top standard An improved protein An efficient protein A large language AI A large language model FMs in Artificial Intelligence Semi-supervised Model
Go robot structure DL predictor structure DL predictor model for human for both text and image
Milestone using amino acid with atomic level text QA interactive tasks Deep Learning Models Unsupervised Model
characteristics accuracy
Figure. 2 Timeline for FMs in Bioinformatics and Their Background in Deep Learning. FMs in bioinformatics coincided
with the rise of deep learning, gaining significant momentum as these models demonstrated remarkable achievements in the
era of big data. Pioneering milestones such as Alpha Go, the first robot to meet top standards, significantly enriched the field
of deep learning. Subsequent developments, including AlphaFold and AlphaFold2, revolutionized protein structure prediction
from biological sequences. The introduction of GPT4 marked a turning point, triggering a surge in the application of FMs.
These efforts boosted FMs (supervised FMs, semi-supervised FMs, unsupervised FMs) in bioinformatics showing promising
results in solving domain exploration, sequence construction, function prediction, and multimodal integration to acquire salient
biological sequence, structure, function, and other complex information for practical applications in biology.
Table 1 Biological Problems and Their Associated Data in Biological FMs. The table provides an overview of five distinct
problems in bioinformatics solved by biological FMs: domain exploration, sequence analysis, structure construction, function
prediction, and multimodal problems. These problems involve one or more categories of biological data, including DNA, RNA,
proteins, single cell genomics (scGenomics), knowledge graphs/networks, and biological text/images. Domain-specific
problems primarily focus on biological text/images/video. Core biological problems (sequence analysis, structure construction,
function prediction) involve genes and mutations, biological phenomena data, and their relation and interactions. Multimodal
integration biological problems may use multiple data types, e.g. biomedical text/images and proteins.
Problems Domain Sequence Structure Function Multimodal
Data exploration analysis construction prediction problems
DNA √ √
RNA √ √
Protein √ √ √ √
scGenomics √ √ √ √
KGs/Net. √ √
Text/Image √ √ √
to employ pre-trained embeddings acquired from others to solve their targeting problems. In terms of reproducibility,
supervised and semi-supervised FMs offer more robust generalizations in the translation of experimental inputs to outputs.
Their flexibility and robustness surpass traditional methods, providing advantages for researchers to decipher complex
biological systems. Moreover, unsupervised FMs can significantly enhance biological performance by deeply probing a
plethora of underutilized resources that are either unannotated or laden with noise [Rao et al., 2021; Forster et al., 2022]. The
robust and reliable capabilities, strong exploration and exploitation capacity, and flexible adaptability to diverse downstream
tasks make FMs a compelling approach to address biological challenges, e.g., unknown 3D structures or function annotations
prediction from sequences [Sapoval et al., 2022], rare disease discovery from limited task-specific data [Theodoris et al., 2023],
and other analyses on noise interference data, overlapped data, or other unexplored data in bioinformatics.
Although FMs have been widely employed in many research fields and industry applications, there is still a lack of a thorough
comprehension of FMs in bioinformatics. Indeed, previous approaches commonly rely on general domains of
text/image/video/graph to analyze targets with the help of natural language processing, image processing, or graph learning
methods [Zou et al., 2019]. Unfortunately, the utility of these methods is often constrained for biological researchers. Typically,
there exist at least three critical challenges associated with the application of FMs in AI for addressing biological problems.
3

---

<!-- Page 4 -->

Firstly, general purpose FMs that are mainly constructed by task-specific approaches for a particular downstream task without
expertise requirements often lead to notoriously model overfitting in bioinformatics. Secondly, most FMs rely heavily on large-
scale training datasets, making them inflexible and untrusted when analyzing shifted datasets for significant biological
applications [Uhlmann et al., 2022]. As depicted in the futility theorem, the predicted results of binding sites may not be
functional in vivo, even though they bind to the vitro sequence with higher possibility [Wasserman et al., 2004]. At times,
specific biological problem-solving necessitates the incorporation of specialized insights derived from knowledge in the
biological domain. Finally, non-linear deep features derived from FMs in AI for biological tasks may encounter challenges in
terms of biological interpretability and model reliability, owing to their intricate structures and the diverse nature of biological
targets.
In this context, a review that encapsulates the cutting-edge applications of FMs in bioinformatics is valuable and necessary
to bridge the existing gap in a comprehensive understanding of these models, shedding light on their operational mechanisms,
the contributions they have made, and the challenges and opportunities they present for future explorations. Macromolecules
are fundamental to addressing core biological problems, including sequence analysis, structure construction, and function
prediction. In response to these problems, we provide a comprehensive survey of foundation models in bioinformatics. These
FMs are trained in a supervised or unsupervised manner and can be applied to downstream applications like domain exploration,
core biological problems, and multimodal integration biological problems. These problems are intricately linked with biological
data: DNA, RNA, proteins, and single cell genomics, as well as knowledge graphs/networks, and text/image data, shown in
Table 1. Additionally, the evolution of FMs in bioinformatics presented in Fig. 2 emphasizes their development of network
structures in deep learning, general purpose FMs, and FMs in bioinformatics with significant milestones.
This review delivers a thorough understanding of recent developments and challenges associated with foundation models
that emphasize a sound grasp of biological issues. Except for the domain shift foundation models from general domains to
biological domains, they primarily focus on three core biological problems: sequence analysis, structure construction and
prediction, and function prediction, which play a crucial role in analyzing the sequence, structure, and function of biological
targets. Multimodal integration biological problems, such as multi-modality analysis, may involve multiple types of biological
data to further enhance their performance. The review concludes by discussing potential directions in light of current challenges
and opportunities. Overall, we review recent foundation models in bioinformatics through the following subsections (i)
foundation model architectures, (ii) biological foundation models for five kinds of biological problems on top of introducing
distinct problems and datasets, data preprocessing, and down-stream tasks, (iii) challenges and opportunities, (iv) conclusions.
Foundation model architectures
Foundation models (FMs) are large, pre-trained AI systems that can be effectively generalized across a wide range of
domains and tasks [Bommasani et al., 2022]. The advent of general purpose foundation models has been most prominently
observed in the field of natural language processing (NLP) [Dai et al., 2015, Howard et al., 2018, Dong et al., 2019]. This
development has subsequently permeated into computer vision and other areas of deep learning [Long et al., 2015, Xie et al.,
2017, Yuan et al., 2021]. In bioinformatics, FMs trained on massive biological data through supervised, unsupervised, or semi-
supervised machine learning strategies offer an unprecedented prediction ability via finetuning mechanisms with limited data.
Based on pretraining strategies, FMs in bioinformatics can be divided into two main categories: supervised FMs that construct
specific embeddings to capture complex patterns and relationships within the labeled data, and unsupervised FMs that mainly
concentrate on various downstream tasks to generate new representations not been observed in the unannotated training data.
Notably, some FMs composed of both supervised and unsupervised pretraining mechanisms noted as semi-supervised FMs are
elucidated in the supervised pre-trained FMs. Moreover, FMs could also be classified into discriminative and generative models
according to the model task. The architectures of the supervised pre-trained FMs and unsupervised pre-trained FMs are
introduced as follows.
Supervised pre-trained FMs. Traditional AI-based models focus on training different types of neural networks to extract
and identify insightful features of training data. They usually train the model in an end-to-end process to solve only one kind
of task each time, such as classifying COVID-19 from chest CT images in a supervised learning process [Pathak et al., 2022].
In this context, supervised learning that necessitates preliminary human intervention for the appropriate labeling of input and
output data in linear classifiers, support vector machines, decision trees, random forests, etc., is essential for understanding
complex biological processes in normal and disease states, which in turn facilitate therapeutic target identification and
biological problem-solving. Based on these machine learning mechanisms, supervised pre-trained FMs pre-train the model
accurately for supervised classification or regression tasks. For instance, Enformer predicts promoter-enhancer interactions
directly from DNA sequences with a large amount of information flow in CNN [Avsec et al., 2021].
Semi-supervised learning techniques, such as autoencoders, contrastive learning, and self-training, are conventionally trained
on data sets with a limited number of annotations. For example, as an image-text semi-supervised foundation model, CoCa pre-
4

---

<!-- Page 5 -->

trains both visions with zero-shot image classification and vision-language with contrastive objectives on noisy image-text
pairs by dual-encoder pretraining models [Yu et al., 2022]. The divergence between supervised and semi-supervised pre-trained
models is primarily determined by the volume of annotations necessary to attain the anticipated results. Nevertheless, both
supervised and semi-supervised pre-trained FMs possess the capability to update and pre-train neural networks via a back-
propagation pipeline, leveraging the statistical outcomes of target variables and their estimated counterparts.
Unsupervised pre-trained FMs. Unsupervised learning can directly identify unlabeled input data with human intervention
only for the output validation. For example, MPNet provides a permuted language modeling that inherits the merit of masked
language modeling and maintains the dependency among predicted tokens [Song et al., 2020]. BioKG builds a biological
knowledge graph compiled from open biological databases to extract a unique set of relations and support relational learning
model tasks [Walsh et al., 2020]. Thereby, unsupervised pre-trained FMs enable dimensionality reduction for more information
representation, or more accurate association generation to support more restrictive downstream tasks [Moor et al., 2023].
The primary tasks of unsupervised FMs can be directed into two categories: generation/recovery tasks, and understanding
tasks. Generation tasks targeting generate novel data with certain properties from unannotated inputs, e.g., ProtGPT2 [Ferruz
et al., 2022] generates protein sequences that exhibit amino acid and disorder properties comparable to those found in natural
proteins, yet remain distinct from the existing protein space. Recover tasks can filter the noise of corrupted data and recover
their original ones, e.g., ProteinBERT [Brandes et al., 2022] recovering the uncorrupted data from the received corrupted inputs
performed by randomly replacing tokens and adding random false annotations to force the model to predict annotations from
sequence alone. Understanding tasks aims at predicting correlations and associations of inputs such as contact prediction. For
instance, DNABERT [Ji et al., 2021] is pre-trained on non-overlap splitting and random sampling human genome data where
15 percent of k-mers are masked in sequence during the first 100k steps and 20 percent in the rest 20k steps.
The conventional progress of unsupervised FMs is implemented via masking strategies in pretraining. The xTrimoPGLM
[Chen et al., 2023] employs four distinctive strategies of masking to redesign the sequence of complementarity determining
region 3 (CDR3): CDR3 short masking, whole masking, random mutation, and random retrieval. ProtST [Xu et al., 2023]
fusions both mask prediction and representation alignment into the pretraining task to model the paired protein sequences and
text descriptions. Unsupervised foundation models can adaptively manage large amounts of heterogeneous targets. While they
behave like generative models during the training phase, they are commonly used as discriminant models in finetuning for
downstream tasks whose goal is to predict the label for a given input.
Compared with the application of the supervised learning method AlphaFold on Protein Data Bank (PDB) data achieved a
high degree of accuracy [Senior et al., 2020], AlphaFold 2, an unsupervised foundation model, has taken this a step further by
incorporating a technique similar to noisy student self-distillation with an enhanced level of accuracy. This milestone comes
with emerging unsupervised pre-trained FMs highlighting their employment in bioinformatics. For instance, CLAPE-DB
combines a pre-trained protein language model and constructive learning to predict DNA binding residues in an unsupervised
manner [Liu et al., 2023]. With the merit of exploring long-range unknown classes, unsupervised pre-trained FMs can generate
meaningful associations of genes that partake in a variety of functional relationships, like shared bioprocess annotations and
co-complex participations. HyenaDNA uses a sequence length scheduling technique to stabilize model pretraining and
leverages longer context to adapt to novel tasks [Nguyen et al., 2023]. Remarkably, the choice of pretraining strategies holds
paramount importance for obtaining optimal performance overshadowing the need for innovative model architecture [Azher et
al., 2023].
Foundation models for biological problems
To implement FMs in bioinformatics appropriately, biological problems and datasets together with relevant data
preprocessing and downstream tasks in biology will be elucidated at first. As this review concentrates on biological
macromolecules (including DNA, RNA, protein), single cell genomics, knowledge graphs/networks, and text/images,
foundation models illustrated in this part are generally employed to solve problems in macromolecule biology. Along with
pretraining architectures, foundation models are classified into supervised models, which capture intricate patterns within
annotated data, and unsupervised models, which generate novel representations unseen in the unannotated training data. In the
realm of bioinformatics, we introduce foundation models as versatile tools capable of addressing practical biological problems,
including domain exploration, sequence analysis, structure construction, function prediction, and multimodal integration. Each
of these areas represents a unique challenge within the field of bioinformatics, and the application of FMs provides innovative
approaches to these complex issues. Recent FMs in bioinformatics are summarized in Table 2.
Biological problems and datasets. FMs can solve practical biological problems that fall within five categories: domain
exploration, sequence analysis, structure construction, function prediction, and multimodal integration. Core biological
problems are sequence analysis, structure construction, and function prediction. Sequence analysis obtains salient gene
5

---

<!-- Page 6 -->

information, such as the information of binding sites (commonly encoded as position weight matrices (PWMs)), protein-protein
interaction (PPIs), gene expression, etc., from gene and mutation sequence data DNA, RNA (in which each of four kinds of
nucleotides is encoded as a one-hot vector like [1, 0, 0, 0]), protein, and genome (the complex of all the genetic information of
an organism). Indeed, the information obtained from these models can be utilized to analyze various downstream tasks. For
instance, gene expression embodies the functional regulation process of cells. The differences observed between single cell
genomics pave the way for the discovery of new cell types. Similarly, Protein-Protein Interactions (PPIs) and their analogs
(such as protein-nucleic acid interactions, protein-ligand interactions, protein-small molecule interactions, etc.) encapsulate the
physical binding information between them, providing valuable insights into their interactions. Sequential data are often
included as annotations of higher-level data that further contain their synergistic or catalytic interactions.
Structure construction focuses on predicting the structures of proteins and RNA from the secondary structure to the
quaternary structure based on the primary structure linear sequences of amino acids in a peptide or protein; the secondary
structure contains a-helix, b-sheet with three strands, b-bend, W-loop, random coil architecture, and topology targets; the
tertiary structure has hydrogen bonds, hydrophobic interactions, and tertiary contacts; and the quaternary structure represents
complex molecule structure. As these structures can be represented by statistical information among amino acid residues
[Senior et al., 2020], many structure construction efforts are made on amino acids in DNA, single cell genomics, and
homologous protein families. Moreover, biological sequence data with different positions may have different functions. In this
context, they can also be categorized under multiple sequence alignment (MSA) [Sapoval et al., 2022].
Function prediction related to biomedicine enables understanding functions of targets such as proteins and variants to predict
polypharmacy side-effects, etc. Core biological data for solving this problem are proteins, individual genes, and their spatial
interactions commonly encapsulated within knowledge graphs or networks. These networks represent various information
indicated as gene interaction networks, disease pathways, patient networks, and networks that capture similarities between cells.
Notably, the prediction of biological function is intrinsically linked to the outcomes of gene expression analysis, given that
protein functionality is influenced by the degree of gene expression.
Domain exploration involves parsing biological problems by transforming the principles of natural language analysis and
computer vision domains into biological areas. Hence, biomedical text like BioBERT [Lee et al., 2020] and 2D and 3D
biomedical images such as microscopy images [Uhlmann et al., 2022] make up major data in solving domain-specific problems.
Multimodal integration biological problems can map multiple types of biological data encompassing multi-omics and
morphological histology data, etc.
Data preprocessing. Data preprocessing is paramount to ensure satisfactory performance before building a model. Original
biological datasets may contain multiple inconsistencies caused by varying purposes and acquisition technologies preventing
them from being analyzed directly. Adoption of appropriately curated and preprocessed data without exorbitant data overlap,
data deficiency, noise interference, or other unexplored data can improve model computational efficiency and representative
ability with better model performance. Examples include doublet removal (without duplicate articles), cell-cycle variance
removal, data imputation and denoising, dimensionality reduction (reducing the sequence similarity), representation learning,
batch effect removal, normalization, background correction, etc.
Doublet removal can avoid mapping duplicate overlapping data with different identifiers or different data that share the same
identifying barcode, which plays a significant role in constructing a unique set of relations between entities [Walsh et al., 2020,
Bernstein et al., 2020]. Cell-cycle variance removal focuses on removing vain variations in gene expression between cells
emerging along the cell cycle by subtracting out the cell cycle influence [Brendel et al., 2022]. It is intractable for data
imputation and denoising because only 6-30% of values can be captured under different chemistry versions and depths, and to
decipher “true” and “false” (called “dropout”) zeros in more than 70% missing values is a guarantee for further identification.
To a certain degree, these data can be refined by leveraging similarities with other datasets, or through the construction of
multiple sub-neural networks for imputation [Arisdakessian et al., 2019]. Dimensionality reduction of wide gene expression
profiles represented in high feature dimensions, also known as representation learning, aims at the construction of embeddings
that facilitate the identification of data elements. Systematic variations specific to each batch tend to raise challenges in data
integration and lead to significant data wastage. Tran et al. compared benchmarks of batch effect removal methods such as
seGen (variational auto-encoders neural network model and latent space), Scanorama (mutual nearest neighbor and panoramic
stitching), and MND-ResNet (residual neural network for calibration) to effectively reduce the variations and batch effects in
data captured with different times, types of equipment, or technologies [Tran et al., 2020]. Therefore, customized fine-tuning
can correct sequencing batches from multiple datasets [Cui et al., 2023]. Protein data can be compared on a common scale by
normalization to adjust the measurements [Clement et al., 2021], and background correction aims to correct for any background
noise in the protein data [Mowoe et al., 2022].
With preprocessed biological data, the data analysis model can be efficiently employed and mitigate or even eliminate
obstacles in biological tasks such as doublet detection and cell-cycle variance annotation. As a result, the judicious utilization
of biological data and their corresponding embeddings can significantly enhance the performance of downstream tasks.
6

---

<!-- Page 7 -->

Downstream tasks. In bioinformatics, the analysis of downstream tasks is permitted to evolve through the application of
fine-tuning strategies that are desired for accurate performance in analyzing biological problems of interest based on pre-trained
biological knowledge in FMs. Fine-tuning can greatly reduce computational time and barriers to their implementation and is
capable of solving biological tasks related to sequence analysis, structure construction, function prediction, domain exploration,
and multimodal integration.
For sequence analysis, besides traditional sequence alignment analysis [Hong et al., 2021], homology detection [Steinegger
et al., 2019], and molecular evolutionary genetics analysis (MEGA) tasks [Stecher et al., 2020], there are promoter interaction
prediction, enhancer-promoter interactions prediction, variants identification, variant effect prediction, signal peptide
prediction, gene dosage sensitivity predictions, genetic perturbation prediction, protein understanding, DNA replication,
stability prediction, etc. Promoter prediction identifies promoter regions of motifs in transcription start sites of genome-wide
sequences. Non-promoter region samples can then be constructed by shuffling and keeping different parts of split promoter
sequences with matching lengths. Enhancer-promoter interactions (EPIs) prediction is essential in cell differentiation and can
interpret non-coding mutation with potential pathogenicity [Chen et al., 2022]. EPIs are determined by chromatin conformation
and, thereby can be inferred by chromatin conformation capture-based (3C-based) techniques or other genetic approaches. In
addition, the promoters and enhancers are also known as initial and distal regulatory elements respectively [Novakovsky et al.,
2023].
Variant identification discloses human diseases and traits by distinguishing casual from non-casual variants [Avsec et al.,
2021]. Variant effect prediction focuses on determining functional important variants and giving priorities to them [Dalla-Torre
et al., 2023]. Signal peptide prediction is a binary protein sequence analysis that predicts their presence and locates their
cleavage sites [Brandes et al., 2022]. Gene dosage sensitivity predictions present genes that are sensitive to changes in their
dosage interpreting copy number variants in genetic diagnosis [Theodoris et al., 2022]. Genetic perturbation prediction aims to
forecast perturbed original values or perturbed gene expression values in certain tasks [Cui et al., 2023]. Protein understanding
requires accurate representation at the residue level or protein level to understand biological information encoded within
proteins [Chen et al., 2023]. The process of DNA replication is governed by specific initiation and termination sites, with the
function of the origin of replication being modulated by epigenetic factors. This intricate process can be studied at a population
level by leveraging non-transformed, highly proliferative, and karyotypically stable pluripotent stem cells [Ding et al., 2021].
Stability prediction calls for statistical representations of protein informatics such as natural language-inspired representations
[Madani et al., 2023].
Structure construction commonly performs secondary or tertiary structure prediction in downstream tasks. Secondary
structure prediction was originally achieved by thermodynamic and alignment methods to determine the homologous sequences
and their alignments [Chen et al., 2022]. 3D structures, by contrast, need further exploration due to the lack of 3D structure
data, which may be constructed on the raised deep learning method. Moreover, other tasks related to DNA, RNA, protein, and
genomics such as predicting DNA binding residues, protein-RNA binding preference, protein-ligand binding pose, splicing
junction prediction, neuropeptide cleavage, genome structure and evolution, gene network, etc., underlie the discovery of their
structure information as well. Predicting DNA and RNA binding proteins is essential for analyzing genetic variants [Alipanahi
et al., 2015]. Transcription factors (TFs) are binding proteins in regulate gene expression that can bind motifs (specific DNA
sequences) to regulate transcription. Generally, pathogenic functional variants in complex neurodegenerative diseases occur
with the change of TF binding intensities [Wang et al., 2018]. Protein-protein interaction prediction aims at revealing bindings
between proteins with transient or stable physical connections. Protein-small molecules and protein-nucleic acid interactions
are significant prediction tasks that dominate organism activities [Liu et al., 2023].
Splicing junction prediction is crucial for protein synthesis and genetic disease identification, whose variant effects can be
predicted with the integration of process-specific scores [Rentzsch et al., 2021]. Neuropeptide cleavage is one of the post-
translational modification binary prediction tasks where the maturation of neuropeptides occurs associated with molecule
variability for behavioral and physiological states [Brandes et al., 2022]. Genome structure represents genome regulatory
element secondary structures, and evolution denotes the evolutionary trend of virus variants [Chen et al., 2022]. Gene network
prediction can map networks based on learned connections between genes. Recently, a transfer learning method has been
proposed to learn the connection with limited task-specific data showing a promising analysis for rare diseases [Theodoris et
al., 2023].
Function prediction captures various properties of RNA/protein/gene functions, discoveries (novel) cell type, functional
genetic variants, and functional modules, and describes gene expression regulation, in silico treatment analysis, fitness
landscape inference, trajectory inference, etc. Functional properties prediction performs the classification of RNA/protein/gene
into several functional groups. For instance, Gene function prediction, from classifying gene and protein functions to analyzing
genome-wide experimental data with multiple statistical tests, relies on the coverage and accuracy of the annotation data such
as Gene Ontology (GO) annotation data [Mi et al., 2019]. Cell type annotation describes heterogeneity in tissues following cell
clustering for further investigation insights into biology and pathology [Cui et al., 2023]. Functional genetic variants
7

---

<!-- Page 8 -->

identification probes functional variants located inside regions of interest and subsequently repeated prediction with altered
alleles [Ji et al., 2021]. Functional module detection inputs from networks and functional features to protein complexes and
evaluates the overlap of the predicted module and known complex [Forster et al., 2022].
Gene expression regulation models a biological process where the genetic blueprint within a gene is harnessed to synthesize
a functional product. Chromatin state analysis is commonly used for detecting annotation and regulation of the genome and for
further nucleosome-level function prediction with gene expression and other related data [Ernst et al., 2011]. Gene expression
profile facilitates therapeutic discovery through gene expression similarities measured by distance metric and clinical
importance evaluating a certain gene on the gene expression level, e.g., finding a tumor gene compared with normal groups
[Tang et al., 2017]. In silico treatment is applied to model human disease by detecting candidate therapeutic targets such as
cardiomyopathy and determining the related genes [Theodoris et al.,2022]. Fitness landscape inference is developed to map
protein fitness under given environments and navigate their residue mutation effect in evolutionary trajectories [Xu et al., 2023].
Trajectory inference also known as pseudo-time analysis predicts the order or “progress” ranging from the original to the end
cell state for single cells from genome-wide omics data [Saelens et al., 2019]. Noticeably, cell ordering, topology, stability, and
usability of trajectory inference methods highly depend on the dimension of the dataset and the topology of the trajectory.
Domain exploration leverages biomedical text, images, video, etc., for biological domain-specific analysis such as name
entity recognition, medical image extraction, medical complementary [Lee et al., 2020], etc. Prevalent text processing techniques
of natural language processing (NLP) make numerous efforts to push the progress of mining biomedical text for name entity
recognition, relation extraction, sentence similarity, document classification, natural language inference, evidence-based medical
information extraction, abstractive summarization, question answering, multiple-choice question answering, etc. Analyzing
terms and expressions in the biological domain corpus is pivotal for these tasks. For instance, relation extraction on PubMed
enables the discovery of chemical-protein interactions where the majority of relation instances consist of single sentences. In
medical vision, they specialize in visual recognition, image captioning, and medical image segmentation. Other domain-specific
analyses focus on the medical complementary and alternative, for instance, grounded radiology reports, bedside decision support,
augmented procedures, etc.
Multimodal integration deciphers manifold biological understanding across data modalities such as cross-modal retrieval,
and multi-modal understanding. Besides the aforementioned downstream analysis tasks, many other tasks are not listed or
remain to be further studied employing FMs, such as chemical-genetic interaction prediction and other modality-relevant tasks
for future biological problems.
FMs for biological domain exploration. Modeling in domain knowledge has long been explored by foundation models in
the area of natural language processing and computer vision [Liu et al., 2023, Kaddour et al., 2023]. A series of methods such
as BERT [Devlin et al., 2019], K-BERT [Liu et al., 2020], GPT 3 [Brown et al., 2020], Dragon [Yasunaga et al., 2022] etc.,
utilized FMs to map text, images, knowledge graphs, or their combined data such as Wikidata [Denny et al., 2014],
BoogCorputs [Zhu et al., 2016], and ConceptNet [Robyn et al., 2017] to curate comprehensive language and their
complementary domain representation information. Along this line, biomedical text, images, and knowledge graphs/networks
could be analyzed in the same way by transforming the text, image, or graph domain into the biological domains to solve
domain shift biological problems.
Interpreting the semantic-level biological information encoded within biological text for DNA, RNA, and proteins has been
a pivotal objective for FMs in biological domain exploration. BioBERT [Lee et al., 2020], Med-PaLM [Singhal et al., 2023],
BioBLECTRA [Raj Kanakarajan et al., 2021], BLURB [Gu et al., 2021], BioBART [Yuan et al., 2022], etc., enable to shift the
general domain into the biological domain by efficient tokenizer learned from unsupervised pretraining, thereby decoding
potential biological operations and functions. BioBERT identifies a multitude of domain-specific proper nouns in biomedical
texts leveraging its final layer representations to compute token-level BIO2 probabilities exclusively. It also employs sentence
classification via a single output layer using BERT’s [CLS] token representation for relation extraction (RE) and SQuAD the
same architecture as BERT [Rajpurkar et al., 2016] for the question-answering (QA) task. With minimal architectural
modifications, BioBERT accomplishes these tasks by pre-training BERT on large-scale biomedical corpora, including PubMed
[Fiorini et al., 2018] which contains terms and expressions not included in general domain corpus and performs better in
biomedical text mining. Similarly, equipping an FM with a prompt tuning that navigates it towards yielding a desired outcome
is essential in the exploration of the biological domain. This procedure involves few-shot or zero-shot learning on various
biological datasets. Med-PaLM combines seven professional medical question-answering datasets (MMLU clinical topics,
LiveQA, MedicationQA, MedQA, MedMCQA, PubMedQA, HealthSearchQA) for aligning the model to new domains using a
few exemplars. BioBLECTRA pre-trained on PubMed and PMC full-text articles introduces a replaced token prediction
pretraining task with a generator and discriminator network. BLURB pretrains a biomedical language model from scratch on
unannotated biomedicine text for a wide range of biomedical NLP tasks, eliminating the need for complex tagging schemes.
Lastly, BioBART is a bidirectional and auto-regressive generative language model designed specifically for biomedical natural
language generation tasks, complete with corresponding data. After exploring the biological domain for biomedical tasks such
8

---

<!-- Page 9 -->

as name recognition and relation extraction, etc., downstream tasks in biological domain exploration such as biomedical question
answering can then be achieved together via task-specific fine-tuning in BioBERT, or parameter-efficient approaches in Med-
PaLM.
Besides these biological text-based domain-shift explorations, FMs also incorporate multiple modalities of data, such as image,
graph, and video samples with both genes- and cell-level biological insights to improve the representation ability in various
downstream tasks. Here are semi-supervised learning models CoCa [Yu et al., 2022], and unsupervised learning models such
as GMAI [Moor et al., 2023] and MSA [Wu et al.,2023]. CoCa builds an image encoder and unimodal text decoder for
multimodal pre-training on biological images and text respectively. A pre-trained CoCa model can be utilized for video action
recognition tasks using individually processing multiple frames of a video through the shared image encoder. MSA
breakthroughs the lack of training data without inferior performance in medical image segmentation by a medical-specific
domain knowledge integrated adaptation technique, which fine-tunes only 5% around the parameters of the fundamental model
for various downstream tasks. GMAI is easy to adapt to new tasks due to the acceptance of inputs and production of outputs
with varying combinations of data modalities (including biomedical text, graph, and video). With minimal or no task-specific
annotated data, GMAI can perform a wide array of tasks, including constructing a comprehensive perspective of a patient's health
status by integrating various modalities, from unstructured symptom descriptions to continuous glucose monitor readings and
patient-supplied medication logs. Downstream tasks related to visual, vision-language, and multimodal understanding could be
perfectly accomplished by zero-shot transfer, frozen feature evaluation, or fine-tuning based on one of the two modules or their
combination, i.e. target-specific fine-tuning.
In the context of a biological domain-shift, pre-trained FMs exhibit competitive efficacy in biological explorations tasks,
such as biomedical text mining (including named entity recognition, relation extraction, and question answering), PICO
(Participants, Interventions, Comparisons and Outcomes entities) extraction, and vision-language extraction, comparable to
those of general domain FMs employed in natural language processing and computer vision. For example, BioBERT [Lee et
al., 2020] (pre-trained on biological PubMed abstracts of 4.5 billion words and PubMedd Central full-text articles of 13.5
billion words) outperforms general domain foundation model BERT [Devlin et al., 2019] (pre-trained on Wikipedia text of 2.5
billion words and BooksCorpus of 0.8 billion words) on various biomedical downstream tasks such as biomedical question
answering task improved by 12.24% MRR, biomedical relation extraction improved by 2.80% F1 score, and entity recognition
improved by 0.62% F1 score. BioBLECTRA pre-trained from scratch on PubMed abstracts and PubMedBERT achieves the
superior performance of mean test results on all datasets in BLURB, which is finetuned on six biomedical text mining tasks
(NER, PICO, Relation Extraction, Sentence Similarity, Document Classification, Question Answering). For publicly available
NCBI-Disease, it acquires 89.38% mean test results (evaluation metrics F1 entity-level for NER, Macro F1 word-level for PICO,
Macro F1 for Relation Extraction and Document Classification, Pearson for Sentence Similarity, Accuracy for the rest) than the
Base 88.2%. Besides pretraining mechanisms, finetuning is another key strategy in biological FMs. Compared with the
ImageNet classification accuracy of CoCa (90.6%) when frozen the parameters, the performance of CoCa with the finetuning
strategy is increased to 91.0 % which is higher than other image-text FMs including ALIGN (88.6%) [Jia et al., 2021], Florence
(90.1%) [Yuan et al., 2021], and MetaPseudoLabels (90.2%) [Pham et al., 2021].
Model capacity is pivotal to biological domain exploration as well. Medical question answering accuracy on MedQA
(questions about US medical licensing exam) of MedPaLM is 67.6% with 540 billion model parameters surpasses that of state-
of-the-art (SOTA) FM methods PubMedBERT (38.1%, 100M) [Gu et al., 2021], DRAGON (47.5%, 360M) [Yasunaga et al.,
2022], and PubMed GPT (50.3%, 2.7B) [Bolton et al., 2022]. MSA fine-tuned part of the model achieves the best results
compared with SOTA segmentation methods with the average Dice Score of 0.893 and 0.883 on datasets AMOS and BTCV
respectively. BioBART obtains competitive performance on biomedical summarization datasets exceeding BART large for
1.93/1.31/2.1 on Rouge-1/2/L on MeQSum. However, there is still a domain-shifting problem when pre-trained on biomedical
scientific articles of PubMed for BioBART. Noticeably, the lack of a standard dataset for training and different training splits
could result in lower scores. Additionally, the large scale of the model can also bring technical obstacles.
FMs for biological sequence analysis. Biological sequence analysis is one of the most important research directions in
biology, handling exponentially growing sequence data related to genes, mutations, and various biological phenomena to
forecast promoter regions, enhancer regions, cis-regulatory elements, splice sites, and transcription factor binding sites, among
other downstream tasks related to biological sequences. Traditional models typically train identifiers using handcrafted features,
necessitating an extra step of manual feature extraction. In contrast, recent works can tackle specialized tasks such as scoring
variant influences, predicting gene expression, and even unseen tasks from unknown sequences leveraging implicit medical
knowledge from foundation models. They provide superior prediction results of various tasks with the constraints of correlated
biological theory such as the rationale of the identification of the genomic variants is that true transcription factor binding sites
are more likely located with other transcription factor binding sites.
Genome-wide association studies (GWAS) have been instrumental in providing crucial biological understanding across a
multitude of species. And deciphering the language of non-coding DNA to understand how DNA sequence encodes phenotypes
9

---

<!-- Page 10 -->

is a major problem for the next phase of genome biology research. Supervised foundation model Enformer [Avsec et al., 2021]
improves gene expression prediction accuracy, noncoding variant effect prediction, and candidate enhancer prioritization from
DNA sequence through integrating long-range interactions in a larger receptive field. The tripartite structure of Enformer has
seven convolutional blocks with pooling, eleven transformer blocks, and a final segment that includes a cropping layer and
pointwise convolutions that diverge into two organism-specific network heads. Due to the existence of polysemy and distant
semantic relationships of non-coding DNA especially in data-scarce scenarios, gene regulatory code is highly complex.
DNABERT [Ji et al., 2021] pre-trained model for proximal promoter region identification, and subsequently fine-tuned two
models, DNABERT-Prom-300 and DNABERT-Prom-scan, using TATA and non-TATA human promoters of 10,000 base pairs
in length from the Eukaryotic Promoter Database (EPDnew). It pre-trained bidirectional encoder representation to capture a
global and transferrable understanding of DNA sequences after fine-tuning small task-specific annotated data to visualize
semantic relationships. When dealing with sequences that extend beyond 512 in length, DNABERT segments them into
manageable parts and combines their representations to yield the final composite representation. To further improve its
efficiency, DNABERT-2 [Zhou et al., 2023] presents enhancements including a skilled tokenizer and strategies to handle input
length limitations, thereby optimizing time and memory consumption while boosting model capabilities. Specifically, it treats
DNA sequences as sentences and k-mer nucleotides as words, and substitutes k-mer tokenization with a statistics-based data
compression algorithm noted byte pair encoding (BPE). This strategic modification enables it to establish a state-of-the-art
model for multi-species genome classification that operates with 21× fewer parameters and requires approximately 56× less
GPU time. When extracting semantic-level genome representations, existing processes tend to rely on manual design and
generate unsatisfactory representations instead of refined ones which demand costly database explorations. In response to solve
this problem, CLAPE-DB [Liu et al., 2023] leverages pre-training and contrastive learning on vast unannotated data in an
unsupervised manner with the ability to handle imbalanced data. After pretraining on the Hear Atlas ECs32, Geneformer
[Theodoris et al., 2022] enables the separation of N1 downstream targets and non-targets without any perturbation data. By
gene dimension self-attention mechanisms, scGPT [Cui et al., 2023] can encode intricate interactions between perturbed genes
and others to overcome the experimental infeasibility in the vast potential gene perturbation space.
The universal genetic code illuminates the translation of DNA into proteins, a process primarily governed by the vast
information contained within the genome rather than mere sequential order. Self-supervised learning foundation method
HyenaDNA [Nguyen et al., 2023] leverages genome sequences across various data lengths and model sizes to overcome this
problem. Pre-trained on the human reference genome it can handle context lengths of up to 1 million tokens at the single
nucleotide level, representing an increase of up to 500 times over previous dense attention-based models. Protein sequences
across large protein families could be generated through language models. They can enhance the performance of protein
sequence downstream tasks such as predicting protein stability, detecting remote homology, and forecasting secondary structure.
Nucleotide Transformer [Dalla-Torre et al., 2023] incorporates information from 3,202 diverse human genomes and 850
genomes from a broad spectrum of species, encompassing both model and non-model organisms. It shows that increased
diversity enhances performance compared with increased model size.
The synthesis of proteins presents vast application possibilities in biological areas such as pharmaceutical design and protein
engineering. ProGen [Madani et al., 2023] succeeded in generating a million artificial sequences after the fine-tuning process
using the curated lysozyme dataset. It pre-trains a protein language model on 280 million raw protein sequences with additional
control tags specifying protein properties to generate artificial proteins across multiple families and functions. Interactions
between proteins and DNA are pivotal to vital biological processes such as replication, transcription, and splicing.
xTrimoPGLM [Chen et al., 2023] pre-trains a transformer framework with 100 billion parameters to address protein
understanding and generation tasks with joint optimization of the two types of objectives. This approach employs a trainable
multilayer perceptron (MLP) as a probe to scrutinize pre-trained representations, providing an efficient means to discern the type
of protein information. Notably, during the probing phase, the parameters of pre-trained PLMs remain the same, while training
solely on the MLP. Systematic prioritization obtained from sequence-based CNN instead of the binary outcome can accurately
predict the TF binding intensities and measure the impact of non-coding variants on transcription factors. Furthermore,
ProteinBERT [Brandes et al., 2022] enables meticulous fine-tuning across an extensive spectrum of protein-related tasks in a
remarkably short span of minutes. Impressively, it demonstrated results on stability prediction that were closely aligned with
the pinnacle of contemporary research. ProtGPT2 [Ferruz et al., 2022] generates sequences with prevalent disorders across
datasets displaying 48.64%, 39.70, and 11.66% alpha-helical, beta-sheet, and coil contents, which is comparable to the natural
space with the 45.19%, 41.87%, and 12.93%.
The accurate identification of splice sites is pivotal for guaranteeing precise protein translation. Among these endeavors,
DNABERT outperforms SliceFinder [Wang et al., 2019] on benchmark data with superior performance 0.923 of multiclass
accuracy, 0.919 F1 score, and 0.871 MCC than SliceFinder which reported an accuracy of 0.833, an F1 score of 0.828, and an
MCC of 0.724. Nucleotide Transformer was noted in the prediction of splice sites, where the disparity between the top-
performing probing and fine-tuned models was approximately 20%. In functional variants prediction, ProGen aligned more
accurately with the experimentally measured assay data from protein datasets CM and MDH with an AUC of 0.94 than the
10

---

<!-- Page 11 -->

sequence generation methods from the studies that were specifically designed for these families such as ProteinGan [Repecka
et al., 2021] with an AUC of 0.87. Proper functional scores could help the classification of disease-related non-coding variants.
In comparison to the recently published GenomicBenchmarks [Gresova et al., 2022], which encompasses eight regulatory
element prediction datasets, HyenaDNA establishes a new state-of-the-art across all datasets. Notably, it surpasses previous
benchmarks by substantial margins, achieving an improvement of up to 20 percentage points in the task of human enhancer
identification.
Protein sequences, akin to natural languages, are comprehensive information repositories, encapsulating structure and
function in their amino acid sequence with unparalleled efficiency, and the pretrained foundation model can be adapted for
accurately predicting their structure. ProtGPT datasets exhibit a comparable distribution of ordered and disordered regions
across the two datasets IUPred3 and ordered content. Notably, the proportion of ordered amino acids in the ProtGPT2 and
natural datasets are 79.71% and 82.59%, respectively, underscoring the similarity in their composition. Specifically, foundation
model xTrimoPGLM achieved a 0.961 TM score in predicting VH and VL structure in antibodies, which is higher than
AlphaFold2 (0.951) and other advanced methods including OmegaFold [Wu et al., 2022] (0.946), ESMFold [Lin et al., 2023]
(0.943), IgFold [Ruffolo et al., 2023] (0.945) and xTrimoAbFold [Wang et al., 2022] (0.958). While we do not foresee FMs
generating an entirely different distribution or domain (such as inventing a new fold that triggers an unnatural reaction), they
do have the capability to considerably expand the variety of sequences sampled by evolution, thereby enhancing model
performance.
FMs for biological structure construction. Comprehending biological secondary and 3D structures is crucial for medical
treatments, such as vaccine development through the determination of mRNA structure. The task of predicting these structures
poses a significant challenge for biologists, necessitating concerted efforts to improve our understanding of biological folding
rules and enhance the precision of structure prediction models. Traditional biological structure construction depends on physics-
based methods such as cryogenic electron microscopy, thermodynamic methods helped by experimentally measured
thermodynamic parameters, and alignment-based methods [Sato et al., 2021, Ding et al., 2023]. Due to the high costs of wet
lab experiments and the structural instability of genes like RNA, painstaking efforts have been surged in the development of
computational methods. Recent foundational models make great breakthroughs in biological structure construction. They
enable the establishment of a learned, RNA/protein-specific neural network to predict secondary structure accurately from its
sequence and refine the predicted structure by the manipulation of tokens, the embedding of position. In practice, modeling
protein structure hinges on the integration of representational data with annotations in tasks. For 3D structures, more strict
constraints and implementation of pre-training tasks contribute to obtaining precise structures. In this case, a higher dimensional
representation of the distance and interactions between tertiary inter-nucleotide pairs might be required.
Reconstruction of structures from sequence data is a major challenge by their labor-intensive and time-consuming
characteristics. This challenge is amplified by the limited biological structure datasets [Skinnider et al., 2020]. To overcome
this problem, AlphaFold [Senior et al., 2020], a supervised deep learning method, obtains the distance map and torsion
distribution between pairs of residues from protein sequences for an efficient protein structure prediction. Foundation model
AlphaFold2 [Jumper et al., 2021] further improves the accuracy with a certain noisy student self-distillation approach, generates
a new dataset of predicted structures, and predicts the structure of diverse sequences from Uniclust30. Without directly using
structure data in PDB datasets, they jointly employ multiple sequence alignments (MSAs) and structure features to obtain final
constructions. ProteinBERT [Brandes et al., 2022] recovers uncorrupted data from the corrupted inputs by randomly replacing
tokens and adding random false annotations to force the model to predict annotations from sequence alone. It obtains superior
performance covering diverse protein properties including protein structure, post-translational modifications, and biophysical
attributes. ProGen [Madani et al., 2023] utilizes a protein language model trained on millions of raw protein sequences to
generate artificial proteins with a structural divergence that is conducive to predicting protein secondary structure.
Compared with traditional linear regression methods shaped to hidden representations using annotated data to predict the
secondary structure, or shaped two separate linear projections of sequence position pairs for tertiary structure, ESM-1b [Rives
et al., 2021], an unsupervised foundation model, trains a deep contextual language model on 86 billion amino acids across 250
million protein sequences, which enables a scale combination in data and model capacity. NetSurf supplants the conventional
logistic regression linear layer with a deep neural network in predicting secondary structures [Klausen et al., 2019].
xTrimoPGLM unravels secondary structures of proteins depending on the classification task on helices, strands, and various
turns like coils. CLAPE-DB [Yufan et al., 2023] combines the pre-trained protein language model ProtBert [Elnaggar et al.,
2021] and constructive learning that discovers a representation space to predict ligand-binding sites of a protein sequence.
HyenaDNA adds gradient checkpointing to predict chromatin profiles including transcription factor binding profiles, DNase I-
hypersensitive sites, and histone marks, which reduces the memory footprint by 3x.
For tertiary structure, we can extract a binary contact map from the hidden representations of sequences, which offers an
alternative to the conventional method that applies two distinct linear projections to hidden representations. FMs, by contrast,
can directly predict 3D structures and positions of biological targets. ProtGPT2 [Ferruz et al., 2022] was found to generate
11

---

<!-- Page 12 -->

protein sequences that not only mirror the amino acid and disorder characteristics of natural proteins but also carve out a unique
niche within the existing protein landscape. Uni-MoI [Zhou et al., 2023] predict 3D positions for various downstream tasks like
molecular property prediction and molecular conformation generation by two pre-trained models: a molecular model, pre-
trained using 209 million molecular conformations, and a pocket model, pre-trained with 3 million candidate protein pocket
data. According to the stationary-action principle [Richard et al., 2017], it completes self-supervised pre-training on selected
positions with minimal delta positions from random positions instead of using a masking strategy to recover the correct 3D
position.
Rapid prediction of protein structure is indispensable for protein design and examination of allelic variation or disease
mutations. RGN2 [Chowdhury et al., 2022] achieves a remarkable reduction in computation time by up to 106-fold
outperforming AlphaFold2 in the analysis of orphan proteins and various classes of designed proteins. It utilizes the Frenet-
Serret formulas to embed a reference frame at each Cα carbon, then the backbone can be easily constructed by a series of
transformations, i.e., a protein language model AminoBERT. Emerging FMs have been proposed to learn the distinctive
representations of non-coding RNAs, which align with downstream secondary/3D structure prediction, SARS-CoV-2 genome
structure and evolution prediction, protein-RNA binding preference modeling, and gene expression regulation modeling. RNA-
FM [Chen et al., 2022] adopts self-supervised learning taking advantage of 23 million non-coding RNA sequences to infer
their sequential and evolutionary structural information on a large amount of unannotated data for higher generalizability and
performance. It leverages four Evoformers as its foundational structure, and further stacks on top to an Equivariant Graph
Neural Network (EGNN), serving as a predictor of 3D atomic coordinates. Noticeable, pre-training mechanisms in recent works
play a crucial role in structure construction. Guo et al. [Guo et al., 2022] propose a self-supervised pre-training model to learn
hierarchical structure embeddings from protein tertiary structures to improve predicting efficiency. Moreover, McDermott et
al. [McDermott et al., 2023] impose relational structure constraints on the pre-training framework and take a pre-training graph
as an auxiliary input, whose performance is supported by theoretical results.
Foundation models in the construction of biological structures significantly transcend the boundaries of traditional structure
prediction. RNA-FM achieves 94.1% and 70.4% of F1 score on ArchieveII600 and bpRNATS0 respectively, which surpasses
SPORT-RNA [Singh et al., 2019] by 22.8% and 7.5% and is notably higher than the SOTA UFold [Fu et al., 2022] by 3.4%
and 4.0% respectively. RGN2 exhibits superior performance over other methods when applied to proteins that are rich in single
helices and bends, or those that feature hydrogen-bonded turns interspersed with helices. ESM-1b indicates that incorporating
features obtained by the transformer results in an absolute accuracy improvement of 0.9% and 2.5% respectively compared
with the HMM profiles used by NetSurf [Klausen et al., 2019] on the CB513 test set for secondary structure prediction. This
suggests that transformer features provide information that is not captured by the MSA-derived features. Moreover, the
integration of supplementary information can provide practical solutions that are essential for enhancing our comprehension of
biological structure. For example, AlphaFold combines bioinformatics and physical approaches to build components from PDB
data, which enables handling mission physical context in challenging cases like intertwined homomers.
As for 3D pose prediction of protein-ligand complexes, Uni-Mol predicts 80.35% of binding poses with an RMSD less than
or equal to 2Å, better than popular docking methods such as Vinardo (62.81%), Autodock Vina (64.56%), and Smina (65.26%).
On the RNAcontack Test80 dataset, 3D closeness prediction of RNA-FM achieves a superior of 0.88 in the Top-10 long-range
top precision. This performance is significantly superior compared to other methods which typically fall within a range of 0.48
to 0.68. When dealing with small-scale data tasks, RNA-FM confirms that the transfer learning employing pre-trained
parameters of ResNet32 on bpRNA-1m enables improvement of the task performance by another 20 points than simple
ResNet32 with RNA-FM. Furthermore, when dealing with large-scale data tasks, fine-tuning RNA-FM together with
downstream modules enables higher performance. RNA-FM 3D distance prediction attains a PMCC of 0.8313 when combining
sequence encoding, MSA covariances, and RNA-FM embeddings higher than that of combining sequence encoding, MSA
covariances, and secondary structures (0.8218 PMCC).
The potential of FMs extend beyond structure prediction, offering practical solutions for tasks integral to their application in
gene expression, such as the identification of binding sites for transcription factor proteins. CLAPE-DB demonstrates superior
performance with AUC values of 0.871 and 0.881 on two benchmark datasets, TE46 and TE129 in DNA-binding sites
prediction. It outperforms the latest advanced sequence-based models, including DNAPred [Zhu et al., 2019] with AUC values
of 0.845 and 0.730, NCBRPred [Zhang et al., 2021] with AUC values of 0.823 and 0.713, and SVMnuc [Su et al., 2019] with
AUC values of 0.812 and 0.715. More types can be further identified with increasing genomic profiling data and 3D genome
contact maps.
FMs for biological function prediction. Biological functions maintained a high attention towards intronic regions of genes
contribute greatly to complicated disease understanding. Traditional function prediction models mainly classify targets into one
or more categories of collected function datasets such as Gene Ontology (GO) [Ashburner et al., 2000] that describes function
by hierarchical ontologies including molecular functional (MF), biological process (BP), and cellular component (CC) [Mi et
al., 2019, Gligorijević et al., 2021, Kulmanov et al., 2022]. Although GO has more than 50,000 classes, existent function
12

---

<!-- Page 13 -->

taxonomy is immature, incomplete, and imbalanced, hence remain challenges in predicting them correctly in a complex large
space even assisted with biological features. Furthermore, as highly variable genes (HVGs) are mainly selected from the
expression variance across the entire dataset, there is a potential of missing crucial genes of less common cell types. Here,
biological function prediction FMs could break the dilemma and be resilient to data noise and variability.
For example, Geneformer [Christina et al., 2023], a context-aware, attention-based deep learning model pre-trained on a
corpus of 29.9 million transcriptomes, can accurately predict disease genes and their targets, and can be fine-tuned for a variety
of downstream tasks related to chromatin and network dynamics using only a small number of task-specific training examples.
All genes are reorganized based on their gene expression and fed into the transformer for training, in which pre-trained model
could be commonly applied to cardiomyopathy disease modeling, pinpointed therapeutic targets and their experimental
suppression led to significant improvement in cardiomyocyte contraction in an iPSC-based model. The attention heads are
learned in an unsupervised manner for distinct class prediction without previous biological function knowledge of any gene.
Indeed, biological knowledge graphs and networks provide a robust foundation for relational learning models such as
interlinked identifiers, thereby enhancing our understanding of complex biological systems [Walsh et al., 2020]. Altered data
can also be employed as a semi-supervised way to generate detailed representations for function predictions. DNABERT [Zhou
et al., 2023] provides an accurate prediction of functional genetic variant candidates for around 700 million short variants in
dbSNP on selected variants only in high-attention regions and repeats the predictions based on altered allele sequences.
xTrimoPGLM [Chen et al., 2023] provides four distinctive masking strategies to redesign the selected sequence and evaluates
the implications of a synthesized protein sequence associated with a specific biological function. For instance, the task of
antibiotic resistance predicts whether a protein sequence exhibits sensitivity to a particular bacterium. ProtST [Xu et al., 2023]
proposes an unsupervised multimodal integration pretraining framework on both protein sequences and biomedical texts,
outperforming the sequence-based model ESM-1b [Rives et al., 2021] on protein function annotation. RNA-FM [Chen et al.,
2022] leveraging embeddings pre-trained on ncRNAs to model the function of the 5’ untranslated region in mRNA showing its
ability to handle non-coding sequences.
Existing methods necessitate the pre-processing of raw data through the selection or manipulation of genes, such as HVG
selection, manual selection of marker genes, and PCA. This is primarily due to their limited ability to efficiently model high-
dimensional data. To overcome this challenge, scBERT [Yang et al., 2022] pre-trained on large-scale unannotated scRNA-seq
data in a self-supervised learning manner to overcome the batch effect, enlarge sequence length, and improve the model’s
generalizability employing Performer [Choromanski et al., 2020], a matrix decomposition transformer. Foundation model
scGPT [Cui et al., 2023] employs an in-memory data structure tailored specifically for non-sequential omic data, enabling the
storage of hundreds of datasets and facilitating rapid access to manage large-scale data. It pre-trains over 10 million cells stored
by the in-memory data structure and converts all expression counts into relative values by a novel value binning technique. It
also offers reusable fine-tuning pipelines and objectives, specifically designed for a range of downstream tasks including cell
type annotation, gene network inference, multiomic integration, and perturbation prediction, facilitating users to effortlessly
apply the pre-trained model. While pre-training on extensive unannotated data can yield transferable knowledge for
downstream tasks, it’s crucial to acknowledge the divergence that exists between the pre-training and fine-tuning stages.
Specifically, the optimization objectives of downstream tasks could be shifted according to the task. L2P-GNN [Lu et al., 2021]
employs a dual adaptation mechanism at both node and graph levels to encode local and global information, thereby enabling
the optimization objectives of downstream tasks to be tailored to the task at hand and facilitating biological function prediction
using 88,000 annotated subgraphs for a 40-binary classification task.
Another limitation of available training data is the imbalance and extremely highly similar subtypes result in the inferior
performance of the SOTA method. For example, the cell type annotation on the Zheng68k peripheral blood mononuclear cell
(PBMCs) dataset could not achieve an accuracy surpassing 0.71. By contrast, FM scBERT acquires 0.759 on cell type
annotation in the same situation. Meanwhile, scBERT enables capturing long-range interactions and achieves higher
performance on both known and unknown classes whose accuracy of unknown class is 0.329 compared with that of SciBet [Li
et al., 2020] (0.174) and scmap_cluster [Kiselev et al., 2018] (0.174) and known class prediction accuracy is 0.942 compared
with that of SciBet (0.784) and scmap_cluster (0.666). The rank value encoding sometimes provides a straightforward way to
understand the transcriptome, i.e., gene expression, which helps the model focus on genes that are important in distinguishing
different cell states. Genomeformer mapping the network hierarchy with large amounts of transcriptional perturbation data
significantly boosts the prediction of central versus peripheral factors (AUC 0.81) compared to other methods (AUC 0.59-0.69).
Significantly, data quality will be mirrored in the performance of individual input networks. Although the functional tasks,
which are tied to the distribution of pre-trained data, have not yet surpassed structural tasks in terms of improvements, biological
function prediction FMs outperform baselines by a large margin and acquire higher accuracy.
FMs for multimodal integration biological problems. Recently, language understanding research indicate that the text
corpora pre-trained model is surprisingly effective at the task of image synthesis, which brings a perspective on multimodal
analysis [Saharia et al., 2022]. Traditional biological models mainly focus on unimodal information, and have difficulties in
13

---

<!-- Page 14 -->

handling multimodal data or multi-level data [Cao et al., 2022, Ciciani et al., 2022, Xu et al., 2023]. While foundation models
enable a more general understanding of targets by semi-supervised and self-supervised pre-training, for example, they are also
vulnerable to perturbation and need a specific fine-tuning approach. Multimodal integration enables a deeper understanding of
diverse topics, assisting in leveraging medical data for accurate diagnosis, treatment recommendations, and medical research
support. Thus, it holds significance for multimodal integration in histology diagnostic imaging and genomics molecular profile
data, etc., for a systematic study of biological samples [Chen et al., 2022]. CoCa [Yu et al. 2022] introduces a contrastive loss
on image-text embeddings and a captioning loss on multimodal decoder outputs for image-text involving tasks such as
crossmodal retrieval and multimodal understanding. scGPT [Cui et al., 2023] enables multi-omics prediction through
generative AI with the integration of expression and new condition tokens to extend the embedding architecture to multiple
modalities, batches, and states. Specifically, protein sequences together with their textual property descriptions achieve the end
goal of protein representation learning: protein function acquisition. ProtST [Xu et al., 2023] improves the original
representational capacity of the protein language model with protein data of varying granularities and properties through the
application of multimodal representation alignment and multimodal mask prediction.
In the future, it is important for biological foundation models to incorporate more diversity data, temporal data, perturbation
data, etc. For example, KGs analysis suffers from low accuracy due to the data unbalance problem in that the richer entities
own more relations and information but the scarce ones will not be fully represented with limited information. A possible
solution, even if it would possibly raise prices on model designing and training, would be to incorporate varying forms of
biological data such as sequence data, structure data, chemical compounds, etc. With the appropriate use of exponentially
growing biological data and advanced foundation models, both clinically and biologically expected outcomes could be obtained.
Challenges and Opportunities
Despite the remarkable progress made in bioinformatics, foundation models still face some challenges in solving biological
Data noise and sparsity Training efficiency Social influence Challenges
Increasing data diversity Model explainability
Long sequence length Evaluation standard
Multimodality
Opportunities
Various Feasible applications
Boosting of foundation models Hormonal therapy
Growth in available biological data
Surgery Immunotherapy
Drug discovery
RRNNAA DDNNAA SSiinnggllee CCeell
Bone marrow Radiotherapy
transplant Online
healthcare
GGenome Protein GGraphs Pre-trained Finetuned Chemotherapy Personalized therapy
Figure. 3 Challenges and Opportunities in Applying Foundation Models for Biological Problems. FMs for solving
biological problems have been met with challenges related to biological data, model structures, and their social influence, which
in return catalyzes opportunities in bioinformatics due to the increasing availability of biological data, the enhancement of
foundation models, and their diverse real-world applications. From the top of Fig. 3, the challenges encompass data noise and
sparsity, increasing data diversity, long sequence length, and multimodality in biological data collecting; training efficiency,
model explainability, and evaluation standards in model design and construction; and social influences such as ethics and
fairness, privacy restriction, potential misuse, and social bias. Conversely, at the bottom of Fig. 3, opportunities are emerging
with the growth of biological data types and volumes, including RNA, DNA, single cell genomics, protein, and knowledge
graphs/networks; the enhancement of foundation models, particularly pre-trained mechanisms; and a wide range of applications
spanning surgery, hormonal therapy, immunotherapy, radiotherapy, personalized therapy, chemotherapy, bone marrow
transplant, drug discovery, and online healthcare. These developments signal a promising trajectory for the application of FMs
in bioinformatics.
14

---

<!-- Page 15 -->

problems. Biological data containing complex information in living organisms represented with various data scales, different
styles, and multiple data types bring a lot of challenges to FMs [Ruiz et al., 2021]. Employing deep learning modules in FMs
is also a double-edged sword [Eraslan et al., 2019]. It makes large biological data analysis possible but requires a great deal of
computing resources, conceives a massive of model parameters, and has low explainability and reliability. These challenges
and potential opportunities for promising biological areas illustrated in Fig. 3 are presented separately as follows.
Challenges
Data noise and sparsity. One of the key goals of FMs is to extract embeddings for downstream analysis or support other
biological problems [Poli et al., 2023, Jeliazkov et al., 2023]. However, it is still challenging for them to tackle sparse data or
corrupted noise data. The sparsity of biological data is mainly caused by data collection deficiencies, e.g., data captured under
different chemistry versions and depths, and unbalanced research concentrating on popular phenomena and generating entities
that are already rich. Noises and biases usually appear in different selection strategies, experiment conditions, etc. These entities
are unavailable for biological downstream tasks, especially relational discovery tasks. For example, there will be an indirect
data leakage when a relational model designed to extract information about drug-drug combination interactions wants to take
drug-protein interactions as the extra supporting data, even when they are targeting the same protein, i.e. they are truly related
[Walsh et al., 2020]. Although some of the FMs indicate such an issue could be relieved with a careful review of these data
and deep investigation of the phenomenon, they are still vulnerable to data corruption that exists in the current evaluation sets
or future capture scenarios in the real world. Therefore, we suggest incorporating different forms of biological data to make up
for the unexplored data, enhance the model representation ability, and understand the entities that are under-represented.
Increasing data diversity. Another obstacle in bioinformatics for FMs is the increasing data diversity in evolution. On the
one hand, increasing data diversity has the potential to improve model performance efficiently without the need to increase
model capacity [Rives et al., 2021]. On the other hand, diversity with task-unrelated data in a real-world situation can hardly
be transferred to downstream tasks [Wang et al., 2019, Wang et al., 2022]. Along this line, if foundation models could generate
new sequences that are biologically active or pseudo-samples of previous classes and transfer their knowledge to design new
proteins with different functions, they could both condense the biological statistics and optimize the biological problem-solving
ability for special tasks. Improving the robustness might be another direction to help FMs overcome the barriers that hinder the
implementation of increasing diversity. Although simply adding bias to FMs may improve their performance, their capacity to
exploit deeper and broader features is also limited. Therefore, we could provide higher capacity FMs for increasing data
diversity to perform better in bioinformatics.
Long sequence length. Biological sequence provides great potential in solving various biological problems, but the long
sequence length raises huge challenges in training models. There are around 3 billion nucleotides in a single human, 5 million
in the bacterial, and 30 thousand in the virus, these long sequence lengths bring an extreme gradient variance thereby improving
the instability and reducing the efficiency when training a model. The essential reason for the correlation between long
sequences and training instability has not been completely deciphered. Motivated by Sortformer [Press et al., 2020], Li et al.
[Li et al., 2022] attempt to enable stable training with reduced cost by improving data efficiency. They try to overcome the
stability-efficiency dilemma through a sequence length warmup method which trains the model from short sequences to longer
length sequences gradually with larger training batch sizes and learning rates. However, the varying lengths of sequences
implemented in this method are directly obtained by truncation and sacrifice the information of dropped data. Causal
relationships, prerequisites, or other significant factors have not been sufficiently represented and certified, which could be
further improved by leveraging data localization, structure, function, or other chemical and biological rules and relations.
Thereby, longer sequence lengths and higher dimensional gene maps could be easily adopted in analyzing biological problems.
Multimodality. Experimentally, models with higher capacity yield better understanding and representation. However, it is
not the decisive factor influencing the performance in downstream task analysis. In bioinformatics, there are multiple types of
data (text, image, multi-dimension structure, molecule, etc.) acquired from varying scale biological targets (DNA, RNA, protein,
single cell genomics, etc.) and different recording technologies with different annotations, which brings the multimodality
challenge for FMs. Specifically, different representations of the same gene from different inputs instead of the same
representation are substantially enriched in alpha cells and suitable for the cell type annotation downstream task [Yang et al.,
2022]. Multimodality refers to the integration of multiple types of biological data, such as scRNA-seq, scATAC-seq, and ChIP-
seq. However, the challenge lies in the uneven data availability across these modalities, with scRNA-seq having more data
compared to scATAC-seq and ChIP-seq. This disparity poses significant challenges for comprehensive multimodal analysis.
To generate accurate representations from diverse multimodal biological data, the FMs should pay more attention to both
feature-level and semantic-level training strategies to unify the biological knowledge. For instance, despite their similar model
15

---

<!-- Page 16 -->

capacity, Transformers, a deep learning structure commonly employed in FMs, exhibit superior prediction capabilities
compared to LSTMs [Zhou et al., 2021]. Therefore, exploiting the inherent representing strengths of FMs is significant for
more diverse and complex features to tackle different tasks.
Training efficiency. Pre-training is a crucial step for most of the FMs to maintain coherence within each shot, which in turn
affects the overall quality of a summary. However, their high computational costs on huge amounts of data remain a large
barrier to their implementation (e.g., AlphaFold2 needs several weeks of training on up to 200 GPUs). To improve the efficiency
in analyzing big data, previous approaches, for instance, leverage attention mechanisms such as FlashAttention [Dao et al.,
2022] and Multi-query attention [Ainslie et al., 2023], quantization [Yao et al., 2022], kernels [Hijma et al., 2023], sparse
activation [Xu et al., 2023], and other advanced mechanisms to reduce the model’s training and detection time. Similarly,
substantial redundant computations could be cut down in FMs with advanced technologies in terms of removing unimportant
parameters, reducing memory consumption, enhancing convergence rate, paralleling data, and fully utilizing the generative and
adaptive capabilities of models [Sato et al., 2021]. In general, more efforts could be made along this line to improve the
efficiency of foundation models made already.
Model explainability. It is also challenging to provide interpretability of FMs in each step and acquisitions with logical
evidence in bioinformatics. Clear and strong explainability and interpretability are significant factors of highly comparative
prediction accuracy enabling a wide range of biomedical and healthcare applications to explain the model and results to
consumers and researchers [Cui et al., 2022]. Some efforts have been made to explain them in biological applications such as
scBERT, which explains the contribution of genes and their interactions by attention weights of the self-attention mechanism
in the model for gene exploration and decision-making tasks. Thereby the top genes could be visualized by the weights and
analyzed in the following stages [Yang et al., 2022]. However, this work relies only on structural results, which neither indicate
the importance of each node nor explain the reason for reliable results obtained by the model. We envision that FMs
dramatically improve interpretability and explainability by incorporating knowledge graphs and networks to narrow the gap
between FMs and experts for solving more complex biological problems.
Evaluation standard. The design of traditional AI-based models for a specific task in computer vision or natural language
processing makes it easy to evaluate the results as the model performance fits the predefined metrics. However, foundation
models face various downstream tasks as well as unseen tasks, making it uniquely challenging to anticipate all of the modes
and set an evaluation standard for these methods. Current qualitative evaluations mainly focus on certain modules such as
Machine Reading Comprehension (MRC) within a complete QA pipeline, instead of a previously unseen task, e.g., diagnosing
disease in a brain MRI [Moor et al., 2023]. Moreover, the general domain evaluation takes no account of the effects of rich
biological regulations such as biomedical synonymous relationships [Jin et al., 2022]. To evaluate the model performance and
output quality that convey model uncertainty accurately, which in turn prevents the occurrence of overly confident assertions,
biological knowledge of radiology, pathology, oncology, and other specialties might be required.
Social influence. As foundation models allow researchers and consumers to receive help across the medical treatment and
health sciences for improved medical research, human health, and ecological and social environments, serious challenges have
emerged due to the adverse effects of ethics and fairness, privacy restriction, potential misuse, and social bias, etc [Weidinger
et al., 2021, Yu et al., 2022]. For example, gathering biological data in an open environment is the key to biological research,
however, data sharing presents an enormous challenge for researchers whose data lies at the center of their experiments usually
restricted to privacy [Kaddour et al., 2023]. Moreover, over-reliance on models harms patients and may cause disease
misdiagnosis from health disparity[Vyas et al., 2020, Eneanya et al., 2022]. Along this line, we suggest the endeavors of FMs
to build quality assessments for various tasks and utilization. Besides these challenges, social support (beneficial to society) for
both biological data and FMs is an essential factor that directly affects their development process and speed. Hence, it is
necessary to ensure the security of models, the privacy of patients, and the safety of both ecological and social environments,
and take exploration with legal and ethical guarantees.
Opportunities
Biological data. Due to the exponential growth in available biological data, e.g., for RNA secondary structure prediction
there are bpRNA-1m [Danaee et al., 2018] (102318 sequences from 2588 RNA families), RNAStralign [Tan et al., 2017]
(30451 sequences from 8 RNA families), ArchiveII [Sloma et al., 2016] (3975 sequences from 10 RNA families), the
performance of FMs on downstream tasks is expected to boost. Furthermore, incorporating diverse forms of biological data,
such as sequence data, structure data, and chemical compounds, could potentially enhance the model's capabilities and
robustness to noise and outliers. Besides simple datasets, e.g., CellxGene Single-Cell Datasets [Hyman et al., 2022] in sequence
16

---

<!-- Page 17 -->

analysis, and augmentation datasets, e.g., ProtDecribe [Xu et al., 2023] (enhance protein sequences with textual descriptions
of their functions) in function construction, there is a huge amount of data that has not fully utilized by FMs, which could bring
new insights and understanding of important directions. Complex combinations of biological information or conditional data,
for instance, have not yet been widely analyzed in FMs. Specifically, multibiomics data containing microorganisms and
material in surroundings offers the potential to understand the information flow that is fundamental to disease processes [Hasin
et al., 2017]. Additional related information could also be beneficial for biological problem-solving [Fu et al., 2022]. For
instance, AlphaFold, a leading model in the field, combines bioinformatics and physical approaches to build components from
Protein Data Bank (PDB) data. This approach enables it to handle physically challenging contexts, such as intertwined
homomers. With the right application of biological data and advanced foundation models, we could achieve outcomes that meet
both clinical and biological expectations. Thereby, we can enhance FMs towards a specific target, such as the structural features,
and optimize the related tasks in a way that does not affect the target. After this optimization process, for example, to optimize
the structural features in FMs providing information that is not captured by the MSA-derived features [Chen et al., 2022], we
can expect improved results.
Foundation models architecture. Supervised learning in traditional methods depends heavily on a large volume of labeled
data and tends to have limited generation capabilities. As a result, foundation models have emerged as an alternative approach.
Due to the similarity between biological data in bioinformatics and digital data in fields like natural language processing and
computer vision, the application of FMs in bioinformatics become straightforward and convenient. It adopts pre-trained, and
fine-tuned, few-shot, or zero-shot learning manner to obtain a comprehensive biological map or establish the model within such
a diverse environment remains a challenge. Transitioning from a derivable approach to a multi-focus framework also presents
difficulties. In this respect, we can discuss FMs from two perspectives. When biological data and model size are controllable,
we might design different strategies for different data and tasks. On the other hand, when dealing with particularly large models
that contain extensive biological information and a massive number of parameters, ensuring quick and stable learning becomes
a crucial factor. Despite these feasible efforts, the current cognitive abilities of FMs still fall short of expectations.
Understanding biological processes, such as predicting how proteins fold, remains a complex problem in bioinformatics. To
this end, developing new training strategies for FMs is of paramount significance.
Feasible applications. In the field of bioinformatics, FMs provide several opportunities for disease understanding, drug
discovery, online healthcare, etc. For disease understanding, especially the therapy of cancers, exploring the detailed landscape
of the microenvironment from different perspectives is significant. For example, the study combined both scRNA-seq and
spatial transcriptome (ST) facilitate to the analysis of complex tumor. However, effectively microenvironment (TME) in
colorectal (CRC) and to understand the crosstalk between tumor-infiltrating fibroblasts and myeloid cells involved in CRC
[Peng et al., 2023]. Along this line, FMs could further introduce the multi-modal deep learning model exploring scRNA-seq,
spatial transcriptome, bulk RNA-seq, and other information from basic experiments to provide the physiological function of
targets and gradually replace the analytical ideas of building cancer prognosis models.
The obstacles faced in drug discovery mainly emerged in biological target identification bound to treat and disease, which
typically requires years of extensive customization and experiments [Schneider et al., 2018]. FMs that enable in-depth analysis
of biological targets such as genes, proteins, and molecules and provide their sequence, structure, and function information and
representations have great potential to boost this discovery process. By providing a wide search space where corresponding
phenomena (e.g., polypharmacy side-effects, viral mutations) could also be discovered, they will impact therapeutic design and
bring success in discovering new drugs without paying extra time and money in wet lab experiments for insurance [Huang et
al., 2021]. Moreover, given a patient’s genetics, genome, and health history, drugs of personalized medicine could be designed
by FMs. They benefit drug prediction from medical images to gene and molecular measurements across multimodal data of
patients [Capobianco et al., 2022]. In the following clinical trials, drug and treatment problems can be tracked by them as well
from potential failures prediction and eligible patient matching, etc [Liu et al., 2021, Moon et al., 2023].
Traditional healthcare and biomedicine services are mainly provided directly by health workers and doctors with the help of
expensive tests and equipment, which wastes a lot of resources and time in the diagnosis of rare and emergent diseases
[Gamache et al., 2018]. FMs, a lightweight computer mechanism enabling online health care, can be recognized as central
storage in bioinformatics to provide a massive of medical knowledge for professional diagnosis, scientific therapies, and
healthcare administration without the expensive consumption of medical resources. Online healthcare provides the potential
for FMs to be the backbone of any healthcare system and greatly reduce the impact of urgent pandemic crises (e.g., COVID-
19) [Kocher et al., 2021]. Their applications, such as question-answering systems and healthcare assistive robots, can help users
acquire salient medical information when dealing with obstacles they may face [Demner-Fushman et al., 2020]. Their
understanding of diseases can support both doctors and biological researchers to improve their efficiency and make the most
of the medical data and resources [Wornow et al., 2023]. As a result, online health care achieved by FMs is a promising direction
for consumers, researchers, and governments.
17

---

<!-- Page 18 -->

Conclusions
To conclude, foundation models are advanced and efficient in solving biological problems including but not limited to three
core biological problems: biological sequence analysis, biological structure construction, and biological function prediction on
various downstream tasks. Other problems like biological domain exploration and multimodal problems are also analyzed and
compared with traditional methods. Challenges and opportunities across biological data, foundation models, and social
influence to provide an efficient way to maintain the advantages of FMs while solving emerging biological problems better are
attached in the end.
Ethical Statement
There are no ethical issues.
Acknowledgments
The work described in this paper was partially supported by a grant from the Research Grants Council of the Hong Kong
Special Administrative Region, China [Project No.: CUHK 24204023], and a grant from Innovation and Technology
Commission of the Hong Kong Special Administrative Region, China [Project No.: GHP/065/21SZ].
References
[Hughes et al., 2011] Hughes J P, Rees S, Kalindjian S B, and Karen L Philpott. Principles of early drug discovery. British
journal of pharmacology[J], 2011, 162(6): 1239-1249.
[Bommasani et al., 2021] Bommasani D A, Hudson E, Adeli E, Altman R, Arora S, Arx S, Bernstein M S, and Bohg J et al.
On the opportunities and risks of foundation models. arXiv preprint arXiv:2108.07258, 2021.
[Topol et al., 2019] Topol E J. High-performance medicine: the convergence of human and artificial intelligence[J]. Nature
Medicine, 2019, 25(1): 44-56.
[Park et al., 2016] Park Y S, Lek S. Artificial neural networks: Multilayer perceptron for ecological
modeling[M]//Developments in environmental modeling. Elsevier, 2016, 28: 123-140.
[Wang et al., 2018] Wang M, Tai C E W, and Wei L. DeFine: deep convolutional neural networks accurately quantify intensities
of transcription factor-DNA binding and facilitate evaluation of functional non-coding variants. Nucleic acids research,
2018, 46(11): e69-e69.
[Shen et al., 2021] Shen J, Liu F, Tu Y, et al. Finding gene network topologies for given biological function with recurrent
neural network[J]. Nature Communications, 2021, 12(1): 3125.
[Whalen et al., 2016] Whalen S, Truty R M, Pollard K S. Enhancer–promoter interactions are encoded by complex genomic
signatures on looping chromatin[J]. Nature Genetics, 2016, 48(5): 488-496.
[Forster et al., 2022] Forster D T, Li S C, Yashiroda Y, Yoshimura M, Li Z, Isuhuaylas L A V, Itto-Nakama K, Yamanaka D,
Ohya Y, Osada H, Wang B, Bader G D, and Boone C. BIONIC: biological network integration using convolutions[J].
Nature Methods, 2022, 19(10): 1250-1261.
[Dong et al., 2022] Dong K and Zhang S. Deciphering spatial domains from spatially resolved transcriptomics with an adaptive
graph attention auto-encoder[J]. Nature Communications, 2022, 13(1): 1739.
[Mahmud et al., 2018] Mahmud M, Kaiser M S, Hussain A, and Vassanelli S. Applications of deep learning and reinforcement
learning to biological data[J]. IEEE Transactions on neural networks and learning systems, 2018, 29(6): 2063-2079.
[Wiggins et al., 2022] Wiggins W F, Tejani A S. On the opportunities and risks of foundation models for natural language
processing in radiology[J]. Radiology: Artificial Intelligence, 2022, 4(4): e220119.
[Baker et al., 2022] Baker B, Akkaya I, Zhokov P, Huizinga J, Tang J, Ecoffet A, Houghton B, Sampedro R, and Clune J.
Video pretraining (vpt): Learning to act by watching unlabeled online videos[J]. Advances in Neural Information Processing
Systems, 2022, 35: 24639-24654.
[Tack et al., 2022] Tack A, Piech C. The AI teacher test: Measuring the pedagogical ability of blender and GPT-3 in educational
dialogues[J]. arXiv preprint arXiv:2205.07540, 2022.
[Moor et al., 2023] Moor M, Banerjee O, Abad Z S H, Krumholz H M, Leskovec J, Topol E J, and Rajpurkar P. Foundation
models for generalist medical artificial intelligence[J]. Nature, 2023, 616(7956): 259-265.
18

---

<!-- Page 19 -->

[Rao et al., 2021] Rao R M, Liu J, Verkuil R, Meier J, Canny J, Abbeel P, Sercu T, and Rives A. MSA transformer[C].
International Conference on Machine Learning. PMLR, 2021: 8844-8856.
[Sapoval et al., 2022] Sapoval N, Aghazadeh A, Nute M G, Antunes D A, Balaji. A, Baraniuk R, Barberan C J, Dannenfelser
R, Dun C, Edrisi M, Elworth R A L, Kille B, Kyrillidis A, Nakhleh L, Wolfe C R, Yan Z, Yao V, and Treangen T J. Current
progress and open challenges for applying deep learning across the biosciences[J]. Nature Communications, 2022, 13(1):
1728.
[Theodoris et al., 2023] Christina V Theodoris, Ling Xiao, Anant Chopra, Chaffin M D, Al Sayed Z R, Hill M C, Mantineo H,
Brydon E M, Zeng Z, Liu X S, and Ellinor P T. Transfer learning enables predictions in network biology. Nature,
618(7965):616-624, 2023.
[Zou et al., 2019] Zou J, Huss M, Abid A, Mohammadi P, Torkamani A, and Telenti A. A primer on deep learning in
genomics[J]. Nature Genetics, 2019, 51(1): 12-18.
[Uhlmann et al., 2022] Uhlmann V, Donati L, and Sage D. A Practical Guide to Supervised Deep Learning for Bioimage
Analysis: Challenges and good practices[J]. IEEE Signal Processing Magazine, 2022, 39(2): 73-86.
[Wasserman et al., 2004] Wasserman W W and Sandelin A. Applied bioinformatics for the identification of regulatory
elements[J]. Nature Reviews Genetics, 2004, 5(4): 276-287.
[Bommasani et al., 2021] Bommasani R, Hudson D A, Adeli E, et al. On the opportunities and risks of foundation models[J].
arXiv preprint arXiv:2108.07258, 2021.
[Dai et al., 2015] Dai A M, Le Q V. Semi-supervised sequence learning[J]. Advances in neural information processing systems,
2015, 28.
[Howard et al., 2018] Howard J, Ruder S. Universal language model fine-tuning for text classification[J]. arXiv preprint
arXiv:1801.06146, 2018.
[Dong et al., 2019] Dong L, Yang N, Wang W, Wei F, Liu X et al. Unified language model pre-training for natural language
understanding and generation[J]. Advances in neural information processing systems, 2019, 32.
[Long et al., 2015] Long M, Cao Y, Wang J, and Jordan M. Learning transferable features with deep adaptation networks[C].
International conference on machine learning. PMLR, 2015: 97-105.
[Xie et al., 2017] Xie S, Girshick R, Dollár P, Tu Z, and He K. Aggregated residual transformations for deep neural networks[C].
Proceedings of the IEEE conference on computer vision and pattern recognition. 2017: 1492-1500.
[Yuan et al., 2021] Yuan L, Chen D, Chen Y L, Codella N, Dai X Y, et al. Florence: A new foundation model for computer
vision[J]. arXiv preprint arXiv:2111.11432, 2021.
[Pathak et al., 2022] Pathak Y, Shukla P K, Tiwari A, Stalin S, Singh S, and Shukla P K. Deep transfer learning based
classification model for COVID-19 disease[J]. Irbm, 2022, 43(2): 87-92.
[Avsec et al., 2021] Avsec Ž, Agarwal V, Visentin D, Ledsam J R, Grabska-Barwinska A, Taylor K R, Assael Y, Jumper J,
Kohli P, and Kelley D R. Effective gene expression prediction from sequence by integrating long-range interactions[J].
Nature Methods, 2021, 18(10): 1196-1203.
[Yu et al., 2022] Yu J, Wang Z, Vasudevan V, Yeung L, Seyedhosseini M, and Wu Y. Coca: Contrastive captioners are image-
text foundation models. arXiv preprint arXiv:2205.01917, 2022.
[Song et al., 2020] Song K, Tan X, Qin T, et al. Mpnet: Masked and permuted pre-training for language understanding[J].
Advances in Neural Information Processing Systems, 2020, 33: 16857-16867.
[Walsh et al., 2020] Walsh B, Mohamed S K, and Nováček V. Biokg: A knowledge graph for relational learning on biological
data[C]. Proceedings of the 29th ACM International Conference on Information & Knowledge Management. 2020: 3173-
3180.
[Ferruz et al., 2022] Ferruz N, Schmidt S, Höcker B. ProtGPT2 is a deep unsupervised language model for protein design[J].
Nature Communications, 2022, 13(1): 4348.
[Brandes et al., 2022] Nadav Brandes, Dan Ofer, Yam Peleg, Nadav Rappoport, and Michal Linial. ProteinBERT: a universal
deep-learning model of protein sequence and function [J]. Bioinformatics, 2022, 38(8): 2102-2110.
[Ji et al., 2021] Ji Y, Zhou Z, Liu H, and Davuluri R V. DNABERT: pre-trained Bidirectional Encoder Representations from
Transformers model for DNA-language in genome [J]. Bioinformatics, 2021, 37(15): 2112-2120.
19

---

<!-- Page 20 -->

[Chen et al., 2023] Chen B, Cheng X, Geng Y, Li S, Zeng X, Wang B, Gong J, Liu C, Zeng A, Dong Y, Tang J and Song L.
xTrimoPGLM: Unified 100B-Scale Pre-trained Transformer for Deciphering the Language of Protein[J]. bioRxiv, 2023:
2023.07. 05.547496.
[Xu et al., 2023] Xu M, Yuan X, Miret S and Tang J. Protst: Multi-modality learning of protein sequences and biomedical
texts[J]. arXiv preprint arXiv:2301.12040, 2023.
[Senior et al., 2020] Senior A W, Evans R, Jumper J, Kirkpatrick J, Sifre L, Green T, Qin C, et al. Improved protein structure
prediction using potentials from deep learning[J]. Nature, 2020, 577(7792): 706-710.
[Liu et al., 2023] Yufan Liu and Boxue Tian. Protein-DNA binding sites prediction based on pre-trained protein language
model and contrastive learning, Briefings in Bioinformatics, 2024, 25(1).
[Nguyen et al., 2023] Nguyen E, Poli M, Faizi M, Thomas A, Sykes C, Wornow M, Patel A, Rabideau C, Massaroli S, Bengio
Y, Ermon S, Baccus S A, and Ré C. Hyenadna: Long-range genomic sequence modeling at single nucleotide resolution[J].
arXiv preprint arXiv:2306.15794, 2023.
[Azher et al., 2023] Azher Z L, Suvarna A, Chen J Q, et al. Assessment of emerging pretraining strategies in interpretable
multimodal deep learning for cancer prognostication[J]. BioData Mining, 2023, 16(1): 23.
[Sapoval et al., 2022] Sapoval N, Aghazadeh A, Nute M G, et al. Current progress and open challenges for applying deep
learning across the biosciences[J]. Nature Communications, 2022, 13(1): 1728.
[Lee et al., 2020] Lee J, Yoon W, Kim S, So C H, and Kang J. BioBERT: a pre-trained biomedical language representation
model for biomedical text mining[J]. Bioinformatics, 2020, 36(4): 1234-1240.
[Bernstein et al., 2020] Bernstein N J, Fong N L, Lam I, Roy M A, Hendrickson D G, and Kelley D R. Solo: doublet
identification in single-cell RNA-seq via semi-supervised deep learning[J]. Cell Systems, 2020, 11(1): 95-101. e5.
[Brendel et al., 2022] Brendel M, Su C, Bai Z, Zhang H, Elemento O, and Wang F. Application of Deep Learning on Single-
cell RNA Sequencing Data Analysis: A Review[J]. Genomics, Proteomics & Bioinformatics, 2022.
[Arisdakessian et al., 2019] Arisdakessian C, Poirion O, Yunits B, Zhu X, Garmire L X. DeepImpute: an accurate, fast, and
scalable deep neural network method to impute single-cell RNA-seq data. Genome Biology. 2019, 20(1):211.
[Tran et al., 2020] Tran H T N, Ang K S, Chevrier M, Zhang X, Lee N Y S, Goh M, and Chen J. A benchmark of batch-effect
correction methods for single-cell RNA sequencing data [J]. Genome biology, 2020, 21: 1-32.
[Cui et al., 2023] Cui H, Wang C, Maan H, Pang K, Luo F, and Wang B. scGPT: Towards Building a Foundation Model for
Single-Cell Multi-omics Using Generative AI[J]. bioRxiv, 2023: 2023.04. 30.538439.
[Clement et al., 2021] Clement L. Statistical Methods for Quantitative MS-based Proteomics: Part I. Preprocessing[J].
[Mowoe et al., 2022] Mowoe, M.O., Garnett, S., Lennard, K. et al. Pro-MAP: a robust pipeline for the pre-processing of single
channel protein microarray data. BMC Bioinformatics. 2022, 23: 534.
[Hong et al., 2021] Hong L, Sun S, Zheng L, Tan Q X, and Li Y. fastmsa: Accelerating multiple sequence alignment with dense
retrieval on protein language[J]. bioRxiv, 2021: 2021.12. 20.473431.
[Steinegger et al., 2019] Steinegger M, Meier M, Mirdita M, Vöhringer H, Haunsberger S J, and Söding J. HH-suite3 for fast
remote homology detection and deep protein annotation[J]. BMC Bioinformatics, 2019, 20(1): 1-15.
[Stecher et al., 2020] Stecher G, Tamura K, and Kumar S. Molecular evolutionary genetics analysis (MEGA) for macOS[J].
Molecular biology and evolution, 2020, 37(4): 1237-1239.
[Chen et al., 2022] Ken Chen, Huiying Zhao, and Yuedong Yang. Capturing large genomic contexts for accurately predicting
enhancer-promoter interactions. Briefings in Bioinformatics, 2022, 23(2):bbab577.
[Novakovsky et al., 2023] Novakovsky G, Dexter N, Libbrecht M W, Wasserman W W, and Mostafavi S. Obtaining genetics
insights from deep learning via explainable artificial intelligence[J]. Nature Reviews Genetics, 2023, 24(2): 125-137.
[Dalla-Torre et al., 2023] Dalla-Torre H, Gonzalez L, Mendoza J, Carranza N, Grzywaczewski A, Oteri F, Dallago C, Trop
E, Sirelkhatim H, Richard G, Skwark M, Beguir K, Lopez M and Pierrot T. The Nucleotide Transformer: Building and
evaluating robust foundation models for human genomics. bioRxiv, 2023.
[Ding et al., 2021] Ding Q, Edwards M M, Wang N, Zhu X, Bracci A N, Hulke M L, Hu Y, Hsiao J, Charvet C J, Ghosh S,
Handsaker R E, Eggan K, Merkle F T, GGerhardt J, Egli D, Clark A G, and Koren A. The genetic architecture of DNA
replication timing in human pluripotent stem cells[J]. Nature Communications, 2021, 12(1): 6746.
20

---

<!-- Page 21 -->

[Madani et al., 2023] Ali Madani, Ben Krause, Eric R. Greene, Subu Subramanian, Benjamin P. Mohr, James M. Holton, Jose
Luis Olmos Jr., Caiming Xiong, Zachary Z. Sun, Richard Socher, James S. Fraser, and Nikhil Naik. Large language models
generate functional protein sequences across diverse families[J]. Nature Biotechnology, 2023: 1-8.
[Chen et al., 2022] Chen J, Hu Z, Sun S, et al. Interpretable RNA foundation model from unannotated data for highly accurate
RNA structure and function predictions[J]. bioRxiv, 2022: 2022.08. 06.503062.
[Alipanahi et al., 2015] Alipanahi B, Delong A, Weirauch M T, and Frey B J. Predicting the sequence specificities of DNA-
and RNA-binding proteins by deep learning[J]. Nature Biotechnology, 2015, 33(8): 831-838.
[Liu et al., 2023] Liu P, Yuan W, Fu J, Jiang Z, Hayashi H, and Neubig G. Pre-train, prompt, and predict: A systematic survey
of prompting methods in natural language processing[J]. ACM Computing Surveys, 2023, 55(9): 1-35.
[Rentzsch et al., 2021] Rentzsch P, Schubach M, Shendure J, Kircher M. CADD-Splice—improving genome-wide variant
effect prediction using deep learning-derived splice scores[J]. Genome medicine, 2021, 13(1): 1-12.
[Mi et al., 2019] Mi H, Muruganujan A, Huang X, et al. Protocol Update for large-scale genome and gene function analysis
with the PANTHER classification system (v. 14.0)[J]. Nature Protocols, 2019, 14(3): 703-721.
[Ernst et al., 2011] Ernst J, Kheradpour P, Mikkelsen T S, Shoresh N, Ward L D, Epstein C B, Zhang X, Wang L, Issner R,
Coyne M, Ku M, Durham T, Kellis M, and Bernstein B E. Mapping and analysis of chromatin state dynamics in nine human
cell types[J]. Nature, 2011, 473(7345): 43-49.
[Tang et al., 2017] Tang Z, Li C, Kang B, Gao G, Li C, and Zhang Z. GEPIA: a web server for cancer and normal gene
expression profiling and interactive analyses[J]. Nucleic acids research, 2017, 45(W1): W98-W102.
[Xu et al., 2023] Xu H, Elbayad M, Murray K, Maillard J, and Goswami V. Towards Being Parameter-Efficient: A Stratified
Sparsely Activated Transformer with Dynamic Capacity[J]. arXiv preprint arXiv:2305.02176, 2023.
[Saelens et al., 2019] Saelens W, Cannoodt R, Todorov H, Saeys Y. A comparison of single-cell trajectory inference methods[J].
Nature Biotechnology, 2019, 37(5): 547-554.
[Kaddour et al., 2023] Kaddour J, Harris J, Mozes M, Bradley H, Raileanu R, and McHardy R. Challenges and applications of
large language models[J]. arXiv preprint arXiv:2307.10169, 2023.
[Devlin et al., 2019] Devlin J, Chang M W, Lee K, and Toutanova K. Bert: Pre-training of deep bidirectional transformers for
language understanding. In Proceedings of the 2019 Conference of the North American Chapter of the Association for
Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), pages 4171–4186.
[Liu et al., 2020] Liu W, Zhou P, Zhao Z, Wang Z, Ju Q, Deng H, and Wang P. K-bert: Enabling language representation with
knowledge graph[C] Proceedings of the AAAI Conference on Artificial Intelligence. 2020, 34(03): 2901-2908.
[Brown et al., 2020] Brown T, Mann B, Ryder N, Subbiah M, Kaplan J, Dhariwal P, Neelakantan A, Shyam P, Sastry G, Askell
A, Agarwal S, Voss A, Krueger G, Henighan T, Child R, Ramesh A, Ziegler D, Wu J, Winter C, Hesse C, Chen M, Sigler
E, Litwin M, Gray S, Chess B, Clark J, Berner C, McCandlish S, Radford A, Sutskever I, and Amodei D. Language models
are few-shot learners[J]. Advances in neural information processing systems, 2020, 33: 1877-1901.
[Yasunaga et al., 2022] Yasunaga M, Bosselut A, Ren H, Zhang X, Manning C, Liang P, and Leskovec J. Deep bidirectional
language-knowledge graph pretraining[J]. Advances in Neural Information Processing Systems, 2022, 35: 37309-37323.
[Denny et al., 2014] Denny Vrandecˇic ́ and Markus Krötzsch. Wikidata: A free collaborative knowledgebase.
Communications of the ACM, 2014.
[Zhu et al., 2016] Yukun Zhu, Ryan Kiros, Rich Zemel, Ruslan Salakhutdinov, Raquel Urtasun, Antonio Torralba and Sanja
Fidler. Aligning books and movies: Towards story-like visual explanations by watching movies and reading books[C].
Proceedings of the IEEE international conference on computer vision. 2015: 19-27.
[Robyn et al., 2017] Robyn Speer, Joshua Chin, and Catherine Havasi. Conceptnet 5.5: An open multilingual graph of general
knowledge[C]. Proceedings of the AAAI conference on artificial intelligence. 2017, 31(1).
[Singhal et al., 2023] Singhal K, Azizi S, Tu T, Mahdavi S, Wei J, Chung H, Scales N, Tanwani A, Lewis H, Pfohl S, Payne P,
Seneviratne M, Gamble P, Kelly C, Babiker A, Schärli N, Chowdhery A, Mansfield P, Fushman D, Arcas B, Webster D,
Corrado G, Matias Y, Chou K, Gottweis J, Tomasev N, Liu Y, Rajkomar A, Barral J, Semturs C, Karthikesalingam A and
Natarajan V. Large language models encode clinical knowledge[J]. Nature, 2023.
[Raj Kanakarajan et al., 2021] Raj Kanakarajan K, Kundumani B, and Sankarasubbu M. BioELECTRA: pretrained biomedical
text encoder using discriminators[C] Proceedings of the 20th Workshop on Biomedical Language Processing. 2021: 143-
154.
21

---

<!-- Page 22 -->

[Gu et al., 2021] Gu Y, Tinn R, Cheng H, Lucas M, Usuyama N, Liu X, Naumann T, Gao J, and Poon H. Domain-specific
language model pretraining for biomedical natural language processing[J]. ACM Transactions on Computing for Healthcare
(HEALTH), 2021, 3(1): 1-23.
[Yuan et al., 2022] Yuan H, Yuan Z, Gan R, Zhang J, Xie Y, and Yu S. BioBART: Pretraining and evaluation of a biomedical
generative language model[J]. arXiv preprint arXiv:2204.03905, 2022.
[Rajpurkar et al., 2016] Rajpurkar P, Zhang J, Lopyrev K, and Liang P. Squad: 100,000+ questions for machine comprehension
of text[J]. arXiv preprint arXiv:1606.05250, 2016.
[Fiorini et al., 2018] Fiorini N, Leaman R, Lipman D J, and Lu Z. How user intelligence is improving PubMed[J]. Nature
Biotechnology, 2018, 36(10): 937-945.
[Wu et al.,2023] Wu J, Fu R, Fang H, Liu Y, Wang Z, Xu Y, and Jin Y. Medical sam adapter: Adapting segment anything
model for medical image segmentation[J]. arXiv preprint arXiv:2304.12620, 2023.
[Jia et al., 2021] Jia C, Yang Y, Xia Y, Chen Y T, Parekh Z, Pham H, Le Q V, Sung Y, Li Z, and Duerig T. Scaling up visual
and vision-language representation learning with noisy text supervision[C]. International conference on machine learning.
PMLR, 2021: 4904-4916.
[Yuan et al., 2021] Yuan L, Chen D, Chen Y L, Codella N, Dai X, et al. Florence: A new foundation model for computer
vision[J]. arXiv preprint arXiv:2111.11432, 2021.
[Pham et al., 2021] Hieu Pham, Zihang Dai, Qizhe Xie, and Quoc V Le. Meta pseudo labels. In Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition, pages 11557-11568, 2021.
[Bolton et al., 2022] Bolton E, Hall D, Yasunaga M, et al. Stanford crfm introduces pubmedgpt 2.7 b[J]. 2022.
[Zhou et al., 2023] Zhou Z, Ji Y, Li W, Dutta P, Davuluri R, and Liu H. DNABERT-2: Efficient Foundation Model and
Benchmark For Multi-Species Genome[J]. arXiv preprint arXiv:2306.15006, 2023.
[Zhou et al., 2023] Zhou G, Gao Z, Ding Q, Zheng H, Xu H, Wei Z, Zhang L, and Ke G. Uni-Mol: a universal 3D molecular
representation learning framework[C]. International Conference on Learning Representations, 2023.
[Wang et al., 2019] Wang R, Wang Z, Wang J, Li S. SpliceFinder: ab initio prediction of splice sites using convolutional neural
network[J]. BMC Bioinformatics, 2019, 20: 1-13.
[Repecka et al., 2021] Repecka D, Jauniskis V, Karpus L, Rembeza E, Rokaitis I, Zrimec J, Poviloniene S, Rokaitis I,
Laurynenas A, Abuajwa W, Savolainen O, Meskys R, Engqvist M K M, and Zelezniak A. Expanding functional protein
sequence spaces using generative adversarial networks[J]. Nature Machine Intelligence, 2021, 3(4): 324-333.
[Gresova et al., 2022] K. Gresova, V. Martinek, D. Cechak, P. Simecek, and P. Alexiou. Genomic Benchmarks: A collection
of datasets for genomic sequence classification. bioRxiv, 2022.
[Wu et al., 2022] Wu R, Ding F, Wang R, Shen R, Zhang X, Luo S, Su C, Wu Z, Xie Q, Berger B, Ma J, and Peng J. High-
resolution de novo structure prediction from primary sequence[J]. BioRxiv, 2022: 2022.07. 21.500999.
[Lin et al., 2023] Lin Z, Akin H, Rao R, Hie B L, Zhu Z, Lu W, Smetanin N, Verkuil R, Kabeli O, Shmueli Y, Costa A S,
Fazel-Zarandi M, Sercu T, Candido S, and Rives A. Evolutionary-scale prediction of atomic-level protein structure with a
language model[J]. Science, 2023, 379(6637): 1123-1130.
[Ruffolo et al., 2023] Ruffolo J A, Chu L S, Mahajan S P, and Gray J J. Fast, accurate antibody structure prediction from deep
learning on massive set of natural antibodies[J]. Nature Communications, 2023, 14(1): 2389.
[Wang et al., 2022] Wang Y, Xumeng Gong, Li S, Yang B, Sun Y, Chuan Shi, Wang Y, Yang C, Li H, and Song L. xtrimoabfold:
De novo antibody structure prediction without msa. ArXiv, abs/2212.00735, 2022.
[Sato et al., 2021] Sato K, Akiyama M, and Sakakibara Y. RNA secondary structure prediction using deep learning with
thermodynamic integration[J]. Nature Communications, 2021, 12(1): 941.
[Skinnider et al., 2020] Skinnider M, Johnston C, Gunabalasingam M, Merwin N, Kieliszek, MacLellan B, Li H, Ranieri M,
Webster A, Cao M, Pfeifle A, Spencer N, To Q, Wallace D, Dejong C and Magarvey N. Comprehensive prediction of
secondary metabolite structure and biological activity from microbial genome sequences[J]. Nature Communications, 2020,
11(1): 6058.
[Jumper et al., 2021] Jumper J, Evans R, Pritzel A, Green T, Figurnov M, Ronneberger O, Tunyasuvunakool K, Bates R, Žídek
A, Potapenko A, Bridgland A, Meyer C, Kohl S, Ballard A, Cowie A, Paredes B, Nikolov S, Jain R, Adler J, Back T,
Petersen S, Reiman D, Clancy E, Zielinski M, Steinegger M, Pacholska M, Berghammer T, Bodenstein S, Silver D, Vinyals
22

---

<!-- Page 23 -->

O, Senior A, Kavukcuoglu K, Kohli P, and Hassabis D. Highly accurate protein structure prediction with AlphaFold[J].
Nature, 2021, 596(7873): 583-589.
[Rives et al., 2021] Rives A, Meier J, Sercu T, Goyal S, Lin Z, Liu J, Guo D, Ott M, Zitnick C L, Ma J, and Fergus R. Biological
structure and function emerge from scaling unsupervised learning to 250 million protein sequences. Proceedings of the
National Academy of Sciences, 2021, 118(15): e2016239118.
[Klausen et al., 2019] Klausen M S, Jespersen M C, Nielsen H, Jensen K K, Jurtz V I, Soenderby C, Sommer M O A, Winther
O, Nielsen M, Petersen B, and Marcatili P. NetSurfP‐2.0: Improved prediction of protein structural features by integrated
deep learning [J]. Proteins: Structure, Function, and Bioinformatics, 2019, 87(6): 520-527.
[Yufan et al., 2023] Yufan Liu and Boxue Tian. Protein-DNA binding sites prediction based on pre-trained protein language
model and contrastive learning [J]. arXiv preprint arXiv:2306.15912, 2023.
[Elnaggar et al., 2021] Elnaggar A, Heinzinger M, Dallago C, Rehawi G, Wang Y, Jones L, Gibbs T, Feher T, Angerer
C, Steinegger M, Bhowmik D, Rost B. Prottrans: Toward understanding the language of life through self-supervised
learning[J]. IEEE transactions on pattern analysis and machine intelligence, 2021, 44(10): 7112-7127.
[Richard et al., 2017] Richard Feynman. The Character of Physical Law, with new foreword. MIT Press, 2017.
[Chowdhury et al., 2022] Chowdhury R, Bouatta N, Biswas S, Floristean C, Kharkar A, Roy K, Rochereau C, Ahdritz G, Zhang
J, Church G, Sorger P, and AlQuraishi M. Single-sequence protein structure prediction using a language model and deep
learning[J]. Nature Biotechnology, 2022, 40(11): 1617-1623.
[Guo et al., 2022] Guo Y, Wu J, Ma H, and Huang J. Self-supervised pre-training for protein embeddings using tertiary
structures[C]. Proceedings of the AAAI Conference on Artificial Intelligence. 2022, 36(6): 6801-6809.
[McDermott et al., 2023] McDermott M, Yap B, Szolovits P and Zitnik M. Structure-inducing pre-training[J]. Nature Machine
Intelligence, 2023: 1-10.
[Singh et al., 2019] Singh J, Hanson J, Paliwal K, and Zhou Y. RNA secondary structure prediction using an ensemble of two-
dimensional deep neural networks and transfer learning[J]. Nature Communications, 2019, 10(1): 5407.
[Fu et al., 2022] Fu L, Cao Y, Wu J, Peng Q, Nie Q, and Xie X. UFold: fast and accurate RNA secondary structure prediction
with deep learning[J]. Nucleic acids research, 2022, 50(3): e14-e14.
[Zhu et al., 2019] Zhu Y H, Hu J, Song X N, Yu D J. DNAPred: accurate identification of DNA-binding sites from protein
sequence by ensembled hyperplane-distance-based support vector machines[J]. Journal of chemical information and
modeling, 2019, 59(6): 3057-3071.
[Zhang et al., 2021] Zhang J, Chen Q, Liu B. NCBRPred: predicting nucleic acid binding residues in proteins based on
multilabel learning[J]. Briefings in bioinformatics, 2021, 22(5): bbaa397.
[Su et al., 2019] Su H, Liu M, Sun S, Peng Z, and Yang J. Improving the prediction of protein-nucleic acids binding residues
via multiple sequence profiles and the consensus of complementary methods[J]. Bioinformatics, 2019, 35(6): 930-936.
[Ashburner et al., 2000] Ashburner M, Ball C, Blake J, Botstein D, Butler H, Cherry J, Davis A, Dolinski K, Dwight S, Eppig
J, Harris M, Hill D, Tarver L, Kasarskis A, Lewis S, Matese J, Richardson J, Ringwald M, Rubin G and Sherlock G. Gene
ontology: tool for the unification of biology[J]. Nature Genetics, 2000, 25(1): 25-29.
[Gligorijević et al., 2021] Gligorijević V, Renfrew P D, Kosciolek T, Leman J, Berenberg D, Vatanen T, Chandler C, Taylor
B, Fisk I, Vlamakis H, Xavier R, Knight R, Cho K, and Bonneau R. Structure-based protein function prediction using graph
convolutional networks[J]. Nature Communications, 2021, 12(1): 3168.
[Kulmanov et al., 2022] Kulmanov M, Hoehndorf R. DeepGOZero: improving protein function prediction from sequence and
zero-shot learning based on ontology axioms[J]. Bioinformatics, 2022, 38(Supplement_1): i238-i245.
[Christina et al., 2023] Christina V. Theodoris, Ling Xiao, Anant Chopra, Mark D. Chaffin, Zeina R. Al Sayed, Matthew C.
Hill, Helene Mantineo, Elizabeth M. Brydon, Zexian Zeng, X. Shirley Liu, and Patrick T. Ellinor. Transfer learning enables
predictions in network biology. Nature, 618(7965):616-624, June 2023.
[Yang et al., 2022] Yang F, Wang W, Wang F, Fang Y, Tang D, Huang J, Lu H, and Yao J. scBERT as a large-scale pre-trained
deep language model for cell type annotation of single-cell RNA-seq data[J]. Nature Machine Intelligence, 2022, 4(10):
852-866.
[Choromanski et al., 2020] Choromanski K, Likhosherstov V, Dohan D, Song X, Gane A, Sarlos T, Hawkins P, Davis J,
Mohiuddin A, Kaiser L, Belanger D, Colwell L, and Weller A. Rethinking attention with performers. arXiv preprint
arXiv:2009.14794, 2020.
23

---

<!-- Page 24 -->

[Lu et al., 2021] Lu Y, Jiang X, Fang Y, and Shi C. Learning to pre-train graph neural networks[C]. Proceedings of the AAAI
conference on artificial intelligence. 2021, 35(5): 4276-4284.
[Li et al., 2020] Li C, Liu B, Kang B, Liu Z, Chen C, Ren X, and Zhang Z. SciBet as a portable and fast single cell type
identifier[J]. Nature Communications, 2020, 11(1): 1818.
[Kiselev et al., 2018] Kiselev V Y, Yiu A, Hemberg M. scmap: projection of single-cell RNA-seq data across data sets[J].
Nature Methods, 2018, 15(5): 359-362.
[Saharia et al., 2022] Saharia C, Chan W, Saxena S, Li L, Whang J, Denton E, Ghasemipour S, Ayan B, Mahdavi S, Lopes R,
Salimans T, Ho J, Fleet D and Norouzi M. Photorealistic text-to-image diffusion models with deep language
understanding[J]. Advances in Neural Information Processing Systems, 2022, 35: 36479-36494.
[Cao et al., 2022] Zhi-Jie Cao and Ge Gao. “Multi-omics single-cell data integration and regulatory inference with graph-linked
embedding”. In: Nature Biotechnology 40.10 (2022), pp. 1458-1466.
[Ciciani et al., 2022] Ciciani M, Demozzi M, Pedrazzoli E, Visentin E, Pezzè L, Signorini L, Miguez A, Zolfo M, Asnicar F,
Casini A, Cereseto A, and Segata N. Automated identification of sequence-tailored Cas9 proteins using massive
metagenomic data[J]. Nature Communications, 2022, 13(1): 6474.
[C] Ruiz C, Zitnik M, and Leskovec J. Identification of disease treatment mechanisms through the multiscale interactome[J].
Nature Communications, 2021, 12(1):1796.
[Eraslan et al., 2019] Eraslan G, Avsec Ž, Gagneur J, Theis F J. Deep learning: new computational modeling techniques for
genomics[J]. Nature Reviews Genetics, 2019, 20(7): 389-403.
[Poli et al., 2023] Poli M, Massaroli S, Nguyen E, Fu D, Dao T, Baccus S, Bengio Y, Ermon S, and Ré C. Hyena hierarchy:
Towards larger convolutional language models[J]. arXiv preprint arXiv:2302.10866, 2023.
[Jeliazkov et al., 2023] Jeliazkov J R, del Alamo D, and Karpiak J D. Esmfold hallucinates native-like protein sequences[J].
arXiv preprint arXiv:2305.23.541774.
[Wang et al., 2019] Wang Z, Dai Z, Póczos B, and Carbonell J. Characterizing and avoiding negative transfer[C]. Proceedings
of the IEEE/CVF conference on computer vision and pattern recognition, 2019: 11293–11302.
[Wang et al., 2022] Wang H, Kaddour J, Liu S, Tang J, Kusner M, Lasenby J, and Liu Q. Evaluating self-supervised learning
for molecular graph embeddings[J]. arXiv preprint arXiv:2206.08005, 2022.
[Press et al., 2020] Press O, Smith N A, and Lewis M. Shortformer: Better language modeling using shorter inputs. arXiv
preprint arXiv:2012.15832, 2020.
[Li et al., 2022] Li C, Zhang M, He Y. The stability-efficiency dilemma: Investigating sequence length warmup for training
GPT models[J]. Advances in Neural Information Processing Systems, 2022, 35: 26736-26750.
[Zhou et al., 2021] Zhou H, Zhang S, Peng J, Zhang S, Li J, Xiong H, and Zhang W. Informer: Beyond efficient transformer
for long sequence time-series forecasting[C]. Proceedings of the AAAI conference on artificial intelligence. 2021, 35(12):
11106-11115.
[Dao et al., 2022] Tri Dao, Dan Fu, Stefano Ermon, Atri Rudra, and Christopher Ré. Flashattention: Fast and memory-efficient
exact attention with io-awareness. Advances in Neural Information Processing Systems, 35:16344-16359, 2022.
[Ainslie et al., 2023] Ainslie J, Lee-Thorp J, de Jong M, Zemlyanskiy Y, Lebrón F, and Sanghai S. GQA: Training Generalized
Multi-Query Transformer Models from Multi-Head Checkpoints[J]. arXiv preprint arXiv:2305.13245, 2023.
[Yao et al., 2022] Yao Z, Yazdani Aminabadi R, Zhang M, M., Wu X, Li C, and He Y. Zeroquant: Efficient and affordable
post-training quantization for large-scale transformers[J]. Advances in Neural Information Processing Systems, 2022, 35:
27168-27183.
[Hijma et al., 2023] Hijma P, Heldens S, Sclocco A, Van Werkhoven B, and Bal H E. Optimization techniques for GPU
programming[J]. ACM Computing Surveys, 2023, 55(11): 1-81.
[Cui et al., 2022] Cui P, and Athey S. Stable learning establishes some common ground between causal inference and machine
learning[J]. Nature Machine Intelligence, 2022, 4(2): 110-115.
[Jin et al., 2022] Jin Q, Yuan Z, Xiong G, Yu Q, Ying H, Tan C, Chen M, Huang S, Liu X, and Yu S. Biomedical question
answering: a survey of approaches and challenges[J]. ACM Computing Surveys (CSUR), 2022, 55(2): 1-36.
[Weidinger et al., 2021] Weidinger L, Mellor J, Rauh M, Griffin C, Uesato J, Huang P S, Cheng M, Glaese M, Balle B,
Kasirzadeh A, Kenton Z, Hawkins W, Stepleton T, Biles C, Birhane A, Haas J, Rimell L, Hendricks L A, Isaac W, Legassick
24

---

<!-- Page 25 -->

S, Irving G, and Gabriel I. Ethical and social risks of harm from language models[J]. arXiv preprint arXiv:2112.04359,
2021.
[Vyas et al., 2020] Vyas D A, Eisenstein L G, Jones D S. Hidden in plain sight-reconsidering the use of race correction in
clinical algorithms[J]. New England Journal of Medicine, 2020, 383(9): 874-882.
[Eneanya et al., 2022] Eneanya N D, Boulware L E, Tsai J, Bruce M A, Ford C L, Harris C, Morales L S, Ryan M J, Reese P
P, Thorpe Jr. R J, Morse M, Walker V, Arogundade F A, Lopes A A, and Norris K C. Health inequities and the inappropriate
use of race in nephrology[J]. Nature Reviews Nephrology, 2022, 18(2): 84-94.
[Danaee et al., 2018] Danaee P, Rouches M, Wiley M, Deng D, Huang L, and Hendrix D, bpRNA: large-scale automated
annotation and analysis of RNA secondary structure[J]. Nucleic acids research, 2018, 46(11): 5381-5394.
[Tan et al., 2017] Tan Z, Fu Y, Sharma G, and Mathews D H. TurboFold II: RNA structural alignment and secondary structure
prediction informed by multiple homologs[J]. Nucleic acids research, 2017, 45(20): 11570-11581.
[Sloma et al., 2016] Sloma M F, Mathews D H. Exact calculation of loop formation probability identifies folding motifs in
RNA secondary structures[J]. RNA, 2016, 22(12): 1808-1818.
[Hyman et al., 2022] Hyman L, Sbalzarini I F, Quake S, and Günther U. Corvo: Visualizing CellxGene Single-Cell Datasets
in Virtual Reality[J]. arXiv preprint arXiv:2212.00519, 2022.
[Hasin et al., 2017] Hasin Y, Seldin M, Lusis A. Multi-omics approaches to disease[J]. Genome biology, 2017, 18(1): 1-15.
[Peng et al., 2023] Peng Z, Ren Z, Tong Z, Zhu Y, Zhu Y, and Hu K. Interactions between MFAP5+ fibroblasts and tumor-
infiltrating myeloid cells shape the malignant microenvironment of colorectal cancer[J]. Journal of Translational Medicine,
2023, 21(1): 1-20.
[Schneider et al., 2018] Schneider G. Automating drug discovery[J]. Nature Reviews Drug Discovery, 2018, 17(2): 97-113.
[Huang et al., 2021] Huang K, Fu T, Gao W, Zhao Y, Roohani Y, Leskovec J, Coley C W, Xiao C, Sun J, and Zitnik M.
Therapeutics data commons: Machine learning datasets and tasks for drug discovery and development[J]. arXiv preprint
arXiv:2102.09548, 2021.
[Capobianco et al., 2022] Capobianco E. High-dimensional role of AI and machine learning in cancer research[J]. British
journal of cancer, 2022, 126(4): 523-532.
[Liu et al., 2021] Liu R, Rizzo S, Whipple S, Pal N, Pineda A L, Lu M, Arnieri B, Lu Y, Capra W, Copping R, and Zou J.
Evaluating eligibility criteria of oncology trials using real-world data and AI[J]. Nature, 2021, 592(7855): 629-633.
[Moon et al., 2023] Moon I, LoPiccolo J, Baca S C, Sholl L M, Kehl K L, Hassett M J, Liu D, Schrag D, and Gusev A. Machine
learning for genetics-based classification and treatment response prediction in cancer of unknown primary[J]. Nature
Medicine, 2023: 1-11.
[Gamache et al., 2018] Gamache R, Kharrazi H, and Weiner J P. Public and population health informatics: the bridging of big
data to benefit communities[J]. Yearbook of medical informatics, 2018, 27(01): 199-206.
[Kocher et al., 2021] Kocher R P. Reducing administrative waste in the US health care system[J]. JAMA, 2021, 325(5): 427-
428.
[Demner-Fushman et al., 2020] Demner-Fushman D, Mrabet Y, Ben Abacha A. Consumer health information and question
answering: helping consumers find answers to their health-related information needs[J]. Journal of the American Medical
Informatics Association, 2020, 27(2): 194-201.
[Wornow et al., 2023] Wornow M, Xu Y, Thapa R, Patel B, Steinberg E, Fleming S, Pfeffer M A, Fries J, and Shah N H. The
shaky foundations of large language models and foundation models for electronic health records[J]. npj Digital Medicine,
2023, 6(1): 135.
25

---

<!-- Page 26 -->

Table 2 A summary of foundation models in bioinformatics. The table summarizes the model categories, targets, deep module type, and technical advancement of foundation
models for tackling biological problems (DE: Domain Exploration, SA: Sequence Analysis, SC: Structure Construction, FP: Function Prediction, and MP: Multimodal Problems).
FMs are categorized by their pretraining paradigms: supervised learning, semi-supervised learning, and unsupervised learning. Target biological data types include DNA, RNA,
protein, single cell genomics (scGenomics), biomedical text/image/video, and knowledge graph/network. Various deep modules enhance the performance or interpretability of FMs,
such as MLP: multilayer perceptron, CNN: convolutional neural network, and Transformer.
Model Name Biological Model Category Targets Deep Module Type Technical Advancement Author Name,
Problem Publication Year
BioBERT DE Unsupervised Biomedical Transformer Adapt for biomedical corpora by pre-trained BERT on large-scale Lee et al., 2020
learning text biomedical corpora
BioELECTRA DE Unsupervised Biomedical Transformer A biomedical domain-specific language model introducing a replaced Kanakarajan et al.,
learning text token prediction pretraining task with generator and discriminator 2021
network
BLURB DE Unsupervised Biomedical Transformer Pretrain biomedical language model from scratch for a wide range of Gu et al., 2021
learning text biomedical NLP tasks instead of using complex tagging schemes
BioBART DE Unsupervised Biomedical Transformer A bidirectional and auto-regressive generative language model for Yuan et al., 2022
learning text biomedical natural language generation tasks along with corresponding
data
CoCa DE, MP Semi- Biomedical Transformer Use a contrastive loss on image-text embeddings and a captioning loss on Yu et al., 2022
supervised text, image multimodal decoder outputs for image-text involving tasks
learning
Med-PaLM DE Unsupervised Biomedical Transformer Introduce HealthSearchQA dataset, propose a human evaluation Karan et al., 2023
learning text framework, and present instruction prompt tuning for aligning LLMs to
new domains using a few exemplars
MSA DE Unsupervised Biomedical MLP A medical image segmentation model that fine-tunes the pre-trained SAM Wu et al., 2023
learning graph by integrating the medical specific domain knowledge
GMAI DE Unsupervised Biomedical Transformer Adapt to new tasks due to the acceptance of inputs and production of Moor et al., 2023
learning text, graph, outputs with varying combinations of data modalities
video.
DNABERT SA, FP Unsupervised DNA Transformer Use pre-trained bidirectional encoder representation to capture a global Ji et al., 2021
learning and transferrable understanding of genomic DNA sequences
Enformer SA Supervised DNA Transformer Use a larger receptive field to improve gene expression and promoter- Avsec et al., 2021
learning enhancer interactions prediction
HyenaDNA SA, SC Unsupervised DNA MLP | CNN Use a sequence length scheduling technique to stabilize training, and Nguyen et al.,
learning leverage longer context length to adapt to novel tasks 2023
Nucleotide SA Unsupervised DNA Transformer Build and pre-train foundational language models in genomics, across Dalla-Torre et al.,
Transformer learning different genomic datasets and parameter sizes 2023
ProteinBERT SA, SC Unsupervised Protein Transformer Pretrain protein language model with gene ontology annotation Brandes et al.,
learning prediction task for both local and global representations 2022
DNABERT-2 SA, FP Unsupervised DNA Transformer Adapt Byte Pair Encoding (BPE) to improve computational efficiency, Zhou et al., 2023
learning and employ multiple strategies to overcome input length constraints
26

---

<!-- Page 27 -->

Table 2 A summary of foundation models in bioinformatics. (continued)
Model Name Biological Model Category Targets Deep Module Type Technical Advancement Author Name,
Problem Publication Year
ProtGPT2 SA, SC Unsupervised Protein Transformer A generative language model trained on protein space to learn the protein Ferruz et al., 2022
learning language and produce sequences to sample any region
ProGen SA, SC Unsupervised Protein CNN | Transformer A protein language model trained on millions of raw protein sequences Madani et al., 2023
learning that generate artificial proteins across multiple families and functions
xTrimoPGLM SA, SC, FP Unsupervised Protein CNN | Transformer A pre-training framework to address protein understanding and generation Chen et al., 2023
learning tasks with joint optimization of the two types of objectives
CLAPE-DB SA, SC Unsupervised Protein CNN Combines pre-trained protein language model and constructive learning Liu et al., 2023
learning to predict DNA binding residues
Geneformer SA, FP Unsupervised scGenomics Transformer A context-aware, attention-based deep learning model pre-trained on a Theodoris et al.,
learning large-scale corpus and can be transferred to diverse fine-tuning tasks 2022
scGPT SA, SC, FP Unsupervised scGenomics Transformer A single cell foundation model through generative pre-training on over 10 Cui et al., 2023
learning million cells stored by an in-memory data structure
ESM-1b SC, FP Unsupervised Protein Transformer Use unsupervised deep language model to acquire protein structure and Rives et al., 2021
learning function directly from sequences
AlphaFold2 SC Unsupervised Protein Transformer Improve the AlphaFold by employing an SE(3)-equivariant transformer Jumper et al., 2021
learning with an attention mechanism to represent their interactions and distances
RGN2 SC Unsupervised Protein Transformer Combine a differentiable recurrent geometric network (RGN) with a Chowdhury et al.,
learning transformer-based AminoBERT protein language model to generate 2022
backbone structures from unaligned proteins before refinement
Uni-Mol SC Unsupervised Protein Transformer A 3D position predict model by a 3D molecular pre-training framework Zhou et al., 2023
learning along with the candidate protein pre-training for various downstream tasks
RNA-FM SC, FP Unsupervised RNA Transformer Use self-supervised learning to train 23 million non-coding RNA Chen et al., 2022
learning sequences and infer their sequential and evolutionary information
UNI-RNA SC, FP Unsupervised RNA Transformer A context-aware foundation model pre-trained on an unprecedented scale Wang et al., 2023
learning of RNA sequences unraveling evolutionary and structural information
scFoundation FP Unsupervised scGenomics Transformer An extensive single-cell foundation model pre-trained on a dataset of Hao et al., 2023
learning over 50 million single-cell data points with 100 million parameters
scHyena FP Unsupervised scGenomics Transformer A full-length scRNA-seq analysis in the brain by a linear adaptor layer Oh et al., 2023
learning and a bidirectional Hyena operator without losing raw data information
scBERT FP Unsupervised scGenomics Transformer Use self-supervised learning on large-scale unlabeled scRNA-seq data to Yang et al., 2022
learning improve the model’s generalizability and overcome the batch effect
ProtST FP, MP Unsupervised Protein, CNN | Transformer A pre-trained framework with three tasks of both protein and biomedical Xu et al., 2023
learning biomedical text to boost protein sequence understanding
text
27
