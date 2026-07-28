<!-- Page 1 -->

5202
yaM
61
]IA.sc[
1v01611.5052:viXra
Foundation Models for AI-enabled Biological Design
Asher Moldwin1, Amarda Shehu1
1Department of Computer Science, George Mason University, Fairfax, VA, USA
amoldwin@gmu.edu, amarda@gmu.edu
Abstract plications in health, drug discovery[7], synthetic biology[8],
and material sciences[9]. Notably, David Baker, the third re-
This paper surveys foundation models for AI-enabled bio-
cipient of the 2024 Nobel Prize in Chemistry, was recog-
logical design, focusing on recent developments in applying
nized for pioneering work in protein design.
large-scale, self-supervised models to tasks such as protein
engineering, small molecule design, and genomic sequence While many neural network architectures and machine
design. Though this domain is evolving rapidly, this survey learning methods are being developed for biological de-
presents and discusses a taxonomy of current models and sign, this survey focuses on a particularly promising fron-
methods. The focus is on challenges and solutions in adapting tier: Foundation Models (FMs). These models, capable of
these models for biological applications, including biologi- learning general representations from vast datasets in a task-
cal sequence modeling architectures, controllability in gen- agnostic setting, offer exciting opportunities for biologi-
eration, and multi-modal integration. The survey concludes
cal applications. Our understanding of FMs has evolved in
with a discussion of open problems and future directions, of- recent years, and we adopt a broad definition that aligns
fering concrete next-steps to improve the quality of biological
with the Stanford University Human-Centered AI group’s
sequence generation.
understanding[10] in coining the term: FMs are architecture-
agnostic and defined by their ability to learn from task-
Introduction agnostic pre-training, making them applicable across a range
Natural language processing (NLP) has undergone a recent of tasks. Although some researchers narrowly define FMs
revolution driven by Transformer-based neural networks and as sequential models or strictly equate them with LLMs,
the attention mechanism. These architectures have enabled we take the position that FMs should be considered more
large language models (LLMs) to achieve remarkable per- broadly for their capacity to learn deep representations that
formance on natural language understanding and generation can be leveraged for downstream tasks.
tasks, many of which were once thought to be the exclusive Given the rapid progress in FMs, it is timely to survey
domain of human intelligence. While this transformation in this expanding landscape. These models are quickly trans-
NLP has captured widespread attention, a quieter but equally forming AI research, with new developments appearing al-
significant revolution has been unfolding in the biological most weekly, particularly in biological design applications.
sciences. While this survey cannot be fully comprehensive, it focuses
Advances in molecular biology, particularly in large- on key areas of concentrated activity or where significant
scale data collection initiatives such as the Protein Structure challenges are being articulated and addressed. Specifically,
Initiative[1], the Human Genome Project[2] and structural we examine FMs that, leveraging the analogies between nat-
genomics efforts[3, 4, 5], have paved the way for a new ural language and biological sequences, directly support bi-
era of biological research. The rapid development of next- ological sequence-design tasks; though this focus may be
generation sequencing technologies has led to a wealth of somewhat narrow, we believe it encompasses some of the
widely available genomics, proteomics, and metabolomics most exciting developments in the field.
data. This multi-omics view of organisms has driven break- The survey highlights sequence-based FMs and focuses
throughs such as AlphaFold’s[6] success in solving protein on commonly-applied architectures, such as the Trans-
structure prediction, earning two of its its main authors, former, Diffusion, and State Space Model (SSM) architec-
Demis Hassabis and John Jumper, the 2024 Nobel Prize in tures. While FMs can encompass a broader range of archi-
Chemistry. Perhaps more importantly, these rapid develop- tectures, we concentrate on these three due to their demon-
ments are catalyzing a boom in bioinformatics methodolo- strated success in recent biological design literature. More-
gies for various prediction and generation tasks. over, while FMs can support a variety of prediction and
The aim of this survey is to provide an overview of re- downstream tasks, our focus on biological design narrows
cent contributions to AI-enabled biological design, where our attention to generative tasks, where models not only an-
the goal is to leverage biological data and new methods to alyze existing biological data but also aim to create novel bi-
design and engineer biological entities with impactful ap- ological entities with desired properties. As we will discuss,

---

<!-- Page 2 -->

this type of biological design includes de-novo drug design, thus constrained to left-to-right context, ensuring that
protein engineering, and DNA design through gene-editing. each token attends only to previous tokens: h(l) =
i
Attention(l)(h(l−1), h(l−1), . . . , h(l−1)).
Background and Preliminaries 1 2 i−1
Finally, while the attention mechanism handles depen-
FMs dencies between tokens, applying attention multiple times
While FMs do not imply a specific neural architecture, cer- in parallel at each layer (multihead attention), and stacking
tain architectures are more naturally suited to the paradigm many Transformer layers in a deep network builds the capac-
of representation learning, which is a critical component ity to learn complex and hierarchical relationships in data.
in modern FMs. We begin by formalizing the concept of
State-Space Models (SSMs) State-Space Models (SSMs)
implicit representation learning and illustrate it using a
provide an efficient alternative to Transformers for sequence
decoder-only text-based Transformer, before introducing the
modeling, particularly for tasks requiring long-range depen-
diffusion and SSM-based paradigms.
dencies. While Transformers rely on quadratic self-attention
Given an input sequence X = {x , x , ..., x },
input 1 2 T and increasing memory during inference, SSMs achieve sub-
where each token x belongs to a vocabulary V , a
i quadratic scaling and constant memory by employing a Re-
foundation-model must learn a function to compute an inter-
current Neural Network architecture and using fixed-size
nal representation vector h such that h encodes the
final final hidden states and linear state-space equations. These equa-
necessary information to reliably optimize the pre-training
tions model state evolution over time as h = Ah +
t+1 t
objective for different values of X .
input Bu , with outputs y = Ch + ∆u . Key architectures
t+1 t t t
In deep learning, this function is typically parameter-
like S4[12] enhance SSMs with optimizations for long se-
ized such that it can be represented as a series of ma-
quences, while Mamba[13] employs Selective State Spaces
trix multiplications and nonlinear transformations. Each net-
to learn dynamic versions the A, B and C matrices whose
work layer computes an intermediate representation h (x) =
l values depend on the input token.
σ (W h (x) + b ) where W is the trainable weight matrix
l l−1 l l
layer l, b is the bias vector, and σ is a nonlinear activation Diffusion Modeling Models can forgo attention by in-
l
function. The final output layer maps h to the appropri- stead leveraging diffusion processes wherein noise is it-
final
ate form to compute the loss with respect to ground truth. eratively introduced to the inputs and then a learned re-
verse diffusion process is performed to reconstruct realis-
Transformer Architecture In Transformer
tic inputs. This allows global contextual relationships to
architectures[11], sequences are handled by maintaining
gradually emerge in the outputs of diffusion models over
separate representations for each token at each layer, giving:
(cid:16) (cid:17) many iterations of denoising. Formally, diffusion mod-
h(l) = TransformerLayer(l) h(l−1), h(l−1), . . . , h(l−1) . els progressively add random noise to input data over
i 1 2 T
This allows the model to create contextualized representa- T timesteps, following a Markov process in which each
tions through the attention mechanism, where each token’s timestep’s result depends only on the previous timestep and
representation at layer l depends on the representations of the added noise. The probability of transforming the in-
all tokens from the previous layer. Specifically, for each put x 0 into the noisy state x T after T steps is given by:
token embedding h( i l−1), Transformer attention computes q(x 1:T |x 0 ) =
(cid:81)T
t=1 q(x t |x t−1 ), √ where each transition is de-
attention scores using the query, key, and value projections: fined as: q(x t |x t−1 ) = N (x t ; 1 − β t x t−1 , β t I) with β t
Q = W h(l−1), K = W h(l−1), and V = W h(l−1) for controlling the variance of the added noise at each step.
i q i j k j j v j The reverse process, or “denoising,” mirrors this forward
all j, where W , W , and W are trainable weight matrices.
q k v process, allowing the model to reconstruct the input by
The layer representation h(l) is then computed as a weighted
i removing noise over time. For reverse diffusion, a neural
sum of the values: h(l) = (cid:80)T softmax(Q · K )V . network ϵ is trained to progressively denoise x by re-
i j=1 i j j θ T
In this formulation, attention incurs a computational cost versing the diffusion process at each timestep t. The stan-
during training proportional to the number of input tokens dard training objective is derived from a variational bound
squared, rendering its use for long sequences impractical. on the data liklihood, giving the loss function L(θ) =
Memory usage during inference scales linearly with the se- E (cid:2) ∥ϵ − ϵ (x , t)∥2(cid:3) .
t,x0,ϵ θ t
quence length, as key and value representations for all to- While diffusion models were originally developed for
kens need to be stored, further limiting its efficiency. continuous data, like images, alternative approaches have
To effectively leverage the representational power added adapted this framework to discrete data, such as text. In one
by the inclusion of context, the use of general, self- approach, tokens are mapped into a continuous latent space,
supervised pre-training objectives has proven crucial for where noise is progressively added over T timesteps. The
learning representations that can be repurposed for other reverse process denoises the embeddings step by step, and
downstream tasks. For decoder-only models, the pre- a decoder maps the final latent embeddings back to discrete
training objective is typically autoregressive language tokens. This allows diffusion models to maintain local co-
modeling, where the model predicts the next token in herence while capturing global structure over multiple de-
a sequence given all previous tokens. Formally, the noising steps. Another approach directly applies noise to
model learns to approximate the probability distribu- discrete tokens[14] by either replacing tokens with others
tion P (x |x , x , . . . , x ). The attention mechanism is sampled from the vocabulary[15] or by masking them[16].
i 1 2 i−1

---

<!-- Page 3 -->

In the reverse process, a neural network restores the correct Architectures
token sequence from its noisy version by minimizing the dif-
Transformer Models
ference between the predicted tokens and the ground truth at
each timestep. This iterative denoising process enables dif- Classic Transformer Models
fusion models to generate coherent text, effectively adapting The SMILES representation facilitates using standard Trans-
the diffusion framework to discrete data. former architectures like GPT and XLNet [41] for small-
molecule design, often with minimal modifications and
NLP-optimized hyperparameters. MolGPT [17], MCMG
Biological Design [18], Regression Transformer [42], and Taiga [19] employ
GPT-like architectures but differ in training and controlla-
bility strategies. PLMs like Progen [21], Progen2 [22], and
Biological design encompasses the creation or modifica-
ProtGPT2 [23] also use standard architectures with minor
tion of biological entities for specific functions or proper-
enhancements. For instance, Progen2 incorporates Rotary
ties. Researchers focus on three primary classes of biolog-
Position Embeddings (RoPE [39]) and improved paralleliza-
ical or chemical objects: proteins, DNA/RNA, and small
tion. In contrast, most DNA FMs adopt highly customized
molecules. Different representations of these objects typi-
attention mechanisms or alternative architectures.
cally enable different neural network architectures, with the
Specialized for Biological Design
two main representations being sequence-based and graph-
Transformer-based models often adapt attention mecha-
based. Sequence-based representations are derived from the
nisms to suit biological tasks. Examples include RFDiffu-
chemical formulas, such as representing proteins as se-
sionAllAtom [24], NOS [25], and Evo [26]. RFDiffusionAl-
quences of characters corresponding to the twenty naturally
lAtom extends RoseTTAFold2’s multi-track attention with
occurring amino acids or representing genomic sequences
atomic-level details for protein-molecule complex design.
as strings of the four nucleotide bases. The SMILES rep-
NOS employs an encoder-decoder Transformer for forward
resentation for small molecules captures atoms as well as
and backward diffusion, optimized for antibody design. Evo
bonds and branches. Graph-based representations, on the
uses a hybrid StripedHyena architecture, combining RoPE-
other hand, model the bonds and interactions (e.g., hydro-
based attention with convolutional layers [43], enabling effi-
gen bonds, van der Waals interactions) between atoms or
cient processing of long genomic sequences (up to 131 kilo-
molecular units as edges connecting vertices.
bases) for tasks like CRISPR DNA design.
Biological design combines principles from biology,
chemistry, and computational science to engineer biologi- State Space Models
cal systems. The primary areas of greatest activity are: (1)
Classic SSMs
Protein engineering: Designing novel proteins or modifying
Many SSM architectures struggle to effectively capture rel-
existing ones for enhanced function, stability, or specificity;
evant information between tokens separated by large dis-
(2) Small molecule design: Creating new drug candidates or
tances in the input. This challenge is significant for protein
optimizing existing compounds for improved efficacy and
data, where distant amino acids in the sequence may interact
reduced side effects. Advances toward generating biolog-
through hydrogen bonds, disulfide bridges, or hydrophobic
ically functional small molecules or designing novel pro-
interactions. Likewise, genomic data contain regulatory el-
teins with precise control over properties—such as binding
ements located hundreds of thousands of tokens away from
affinity, solubility, or toxicity—could significantly acceler-
the genes they regulate. A similar challenge exists in mod-
ate therapeutic development by streamlining the identifica-
eling ring closure and branching in small molecules [27],
tion of drug candidates and (3) Genomic sequence design:
though these sequences are considerably shorter.
Engineering DNA sequences for applications in synthetic
Several studies have applied Mamba and S4 architectures
biology, gene therapy, or CRISPR-based genome editing. In
directly to biological tasks and report superior performance.
this survey we focus on how text-based FMs are adapted
However, what qualifies as a fair comparison remains un-
for biological design due to their generative capabilities. We
clear (e.g., should models be compared based on the same
will refer to FMs for these three topics as Chemical Lan-
number of parameters, training time, or inference time?).
guage Models (CLMs), Protein Language Models (PLMs),
The CLM introduced by Ozccelik et al. [27] was the first
and Genomic Language Models (GLMs).
to apply S4 models to SMILES chemical sequences, bench-
marking them against other CLMs such as LSTMs and GPT-
type models for de-novo molecule generation. They demon-
Taxonomy and Survey
strate SSM advantages in generating valid, unique, and novel
molecules.
Figure 1 shows our taxonomy highlighting recent areas of
Various SSM-based protein sequence models have
focus in FMs for Biological Sequence Design. We include
emerged, including ProtMAMBA[28], ProteinMamba [44],
references to papers that address each topic in the leaf nodes
and PTMMamba [45]. ProtMAMBA can autoregressively
of the taxonomy tree, color-coded by the biological domain
generate new protein sequences, with or without condi-
that they discuss.
tional information from homologous sequences. Motivated
Methods aligned with these categories are summarized in by long-range dependencies in proteins, it employs a vari-
Table 1. ant of the ”fill-in-the-middle” pre-training objective [46],

---

<!-- Page 4 -->

[17, 18, 19, 20]
Classic [21, 22, 23, 20]
Transformer Models Specialized
[24, 25] [26]
[27] [28, 29, 26]
Classic
Architectures State Space Models Specialized
[30, 31]
Classic
Diffusion Models Specialized
[32] [33, 24, 25, 34]
[27] [21, 22, 28, 24]
Fine-tuning
[26, 29]
[17, 18, 20]
Conditional
[20, 21, 22, 28, 24]
Generation
[26, 29, 30, 31]
Reinforcement
[19, 18] [35]
Learning
Custom Objec-
[25, 20]
FMs for tive Functions
Controllability
Biological
in Generation
Design
Post-Generation
[27] [29]
Filtering
Numerical Prop-
erty Optimiza- [20] [20]
tion Strategies
Multi-condition
Generation
[32, 18] [25]
and Trade-
off Handling
Sampling Algorithms [23]
Combining Multiple
Forms of Biolog- [24, 34]
ical Sequences
Combining Se-
Multi-
quence and [24, 34, 21, 28]
Modal FMs
Structure Information
Citation Key
Incorporating Natural Small Molecules
Language and [36] [37] [38]
Domain Knowledge Proteins
DNA
;
Figure 1: Taxonomy of recent contributions in FMs for Biological Design. Leaf nodes contain references to the relevant papers,
color coded by the type of biological sequence that they discuss.

---

<!-- Page 5 -->

Table 1: Summary of current FM models for Biological Design.
Model Name Domain Architecture Design Goal Generation Method
MolGPT [17] Small Decoder-only Trans- Control TPSA, QED, SAS, Conditional Autoregressive
Molecule former LogP and molecular scaffolds Generation, pre-trained with
prepended property condition
embeddings
MCMG [18] Small Decoder-only Trans- Control Bioactivity, QED, SAS Same as above, with added re-
Molecule former Distilled into inforcement learning rewarding
RNN low property error
Taiga [19] Small Decoder-only Trans- QED, inhibitory potency Policy gradient reinforcement
Molecule former (plC50) learning rewarding high prop-
erty values
S4 CLM [27] Small S4-based SSM MAPk1 kinase inhibitors fine-tuning for transfer to de-
Molecule sired class
DiffuMol [32] Small Diffusion on embed- LogP, QED, TPSA, SAS, and Noiseless conditional token an-
Molecule dings, Transformer de- scaffolds chors
coder for denoising
Regression Small Decoder-only Trans- Control QED, solubil- Alternating training scheme
Transformer[20] Molecule former (XLNet) ity, lipophilicity for small that switches between property
and molecules, fluorescence, sta- prediction and conditional
Protein bility and Bowan index for sequence generation
proteins
Progen [21] Protein Decoder-only Trans- Proteins associated with spe- Conditional autoregressive gen-
former cific families, biological func- eration and fine-tuning
tions
ProGen2 [22] Protein Decoder-only Trans- Structurally valid proteins, spe- Fine-tuning, and three-residue
former with RoPE[39] cific folds, antibodies motif prompts for antibodies
ProtGPT2 [23] Protein Decoder-only Trans- Novel proteins that are also Autoregressive sampling with
former plausible, mostly globular pro- modified sampling schemes
teins
ProtMamba [28] Protein Mamba-based SSM Homologous proteins, valid Autoregressive with homologs
inpainting-based protein modi- for context, or inpainting using
fications Fill-in-the-Middle
EvoDiff [33] Protein Diffusion with Dilated Proteins from specific families, MSA-conditioned for family-
CNN inpainting functional domains, based, motif-based condition-
generating around motifs ing and inpainting for scaffolds
NOS [25] Protein BERT-based Encoder- Antibodies with high expres- Diffusion, multi property
Decoder sion yield and binding affinity value function, Latent Multi-
Objective Bayesian Optimiza-
tion
RFDiffusionAA [24] Protein Specialized Multi-track Protein binders for small Condition on ligand as fixed
com- attention based archi- molecules, including nucleic noiseless anchor
plexes tecture acids, proteins, and ligand
complexes
MMDIFF [34] DNA One-hot vector for Macromolecular Complexes Joint reverse diffusion with sep-
and discrete sequences, arate loss components for se-
Protein FrameDiff architecture quence and structure
for 3d structure
regLM [29] DNA Based on Hyena- Cis-regulatory elements with Special condition tokens for ac-
DNA[40], SSM-like specified levels of activity or tivity level or cell type, outputs
cell-type specificity filtered using regression model
Evo [26] DNA StripedHyena using at- Nucleotide sequences for Fine-tuning to enable condi-
tention and SSM-like CRISPR systems, function- tioning on special tokens
blocks conserving transposable
elements
DiscDiff [30] DNA 2-stage VAE, with DNA for specific species, gene Conditional generation with
U-net based denoising expression levels, or cell types absorb-escape algorithm
networks
DNA-diffusion [31] DNA U-net backbone Regulatory sequences to con- Conditioning on cell-type la-
trol chromatin accessibility bels

---

<!-- Page 6 -->

which trains the model to predict masked segments of ity—features typically conserved in naturally-evolved pro-
a sequence using both preceding and succeeding amino teins.
acids. This enables more accurate sequence inpainting and We observe hybridizations of classic diffusion and trans-
generation tasks designed to capture long-range depen- former architectures to capture broader biological contexts.
dencies. ProtMAMBAFoundation is proposed for general NOS[25] adapts a BERT-small model encoder-decoder
tasks, such as sequence generation and inpainting, while model to better integrate contextual information in pro-
ProtMAMBAFine-Tuned is designed specifically for in- tein sequences during diffusion, while DiffuMol [32] targets
painting. small-molecule design, incorporating a Transformer decoder
While Mamba and S4 models are well-established in the to generate molecules with desired properties like QED and
State-Space Modeling paradigm, the precise definition of LogP.
SSMs can be ambiguous. Following Benegas et al. [47], In multi-modal data contexts, RFDiffusionAA extends
models based on the Hyena architecture[43] can also be clas- RoseTTAFold All-Atom for diffusion-based generation of
sified as SSMs due to shared features like data-dependent protein-molecule complexes, utilizing both sequence and
gating and long convolutions. Hyena, which generalizes structure. Similarly, MMDIFF [34] introduces joint diffu-
techniques from H3[48], excels in long-range sequence sion across DNA and protein sequences, incorporating dis-
comparisons, making it highly effective for DNA model- tinct loss components for sequence and structural modali-
ing. In the realm of DNA-sequence generation, models like ties to enable coordinated generation of biologically coher-
HyenaDNA [40] serve as backbones. This efficient long- ent macromolecular complexes.
sequence architecture is critical, as HyenaDNA is trained on
sequences of up to 1 million nucleotides. It allows the model Controllability in Generation
to capture long-range interactions at single-nucleotide reso- A key challenge in advancing FMs for biological design is
lution, which is crucial for tasks like detecting regulatory achieving fine-grained control over generated data. We note
elements, mutations, and other genomic features spanning that biological design is inherently an engineering endeavor.
large distances. RegLM[29] is a generative model that uses The designed entities are intended to be ultimately synthe-
a Hyena-based backbone, and Evo [26] relies on a variant sized in wet laboratories and then operationalized for partic-
called StripedHyena, combining both attention and Hyena ular outcomes. So, the issue of control is inherent to success-
Layers. ful, synthetically-accessible and operationalizable design.
For small molecules, continuous numerical properties
Diffusion Models may need to be controlled, including Drug-likeness, LogP,
Classic Diffusion Models Molecular Weight, Synthetic Accessibility, Toxicity, and
Diffusion models have become popular for generating con- Topological Surface Area. One may also require particular
tinuous data, such as images or molecular graphs. Recently, classes of molecular compounds, such as “kinase inhibitors”
these models have also been extended to biological se- or “Quaternary Ammonium Compounds” depending on the
quences by embedding discrete token inputs. For example, downstream task/application. For proteins, one typically
DNA-Diffusion [31] generates regulatory sequences con- controls for specific functions or similarity to other known
trolling chromatin accessibility and gene expression. It uses proteins. For DNA, it may be necessary to ensure specific
a U-net convolutional architecture, similar to image diffu- regulatory properties, such as promoters or enhancers, or de-
sion networks like DALL-E [49]. By applying a transfor- sign guide RNAs (gRNAs) to facilitate CRISPR-based gene
mation similar to one-hot encoding—where each nucleotide editing.
is represented within a continuous range of [-1,1]—DNA-
Fine-Tuning
Diffusion is able to introduce Gaussian noise to discrete bi-
ological sequences, facilitating the diffusion process. Build- Many of the models discussed above rely on some form of
ing on similar principles, DiscDiff [30] leverages a U-net fine-tuning to adapt a pre-trained FM for controlled gener-
with ResNet blocks for DNA generation, using a Variational ation. In its simplest form, this involves continued training
Autoencoder to encode nucleotide sequences into a contin- with the same pre-training objective but on a smaller sub-
uous latent space for diffusion, before decoding them back set of data that matches the desired properties/criteria. Ozc-
into discrete form after the reverse diffusion process. celik et al[27] pre-train- their S4-based CLM on 1.9 mil-
Specialized for Biological Design lion SMILES, then fine-tune it on 68 manually-annotated
EvoDiff [33] explores two distinct forward diffusion pro- molecules known to inhibit MAPK1, generating new candi-
cesses tailored for protein modeling: Order Agnostic Au- dates likely to have high binding affinity to MAPK1. Madani
toregressive Diffusion (OADM), which involves randomly et al. [21] fine-tune the Progen model on lysozyme fami-
masking tokens, and the Discrete Denoising Diffusion Prob- lies after pre-training on 280 million protein sequences, then
abilistic Model (D3PM), which applies mutation-based generating proteins with catalytic efficiencies comparable to
noise by replacing amino acids according to a transition natural lysozymes despite low sequence identity.
matrix derived from natural mutation probabilities. This Fine-tuning can be computationally expensive, especially
mutation-driven approach allows EvoDiff to navigate bio- for large models like ProGen, with 1.2 billion parameters, or
logically meaningful regions of evolutionary space, increas- insufficient when more granular control is required. Never-
ing the likelihood that the generated proteins will retain es- theless, fine-tuning is often a necessary step before applying
sential properties such as functionality, stability, and activ- more controlled generation techniques, such as conditional

---

<!-- Page 7 -->

generation. It is worth noting that fine tuning may not be ef- as bioactivity, drug-likeness, and synthetic accessibility. In-
fective if the dataset with properties of interest is particularly valid molecules receive a reward of zero, and the reward is
small relative to the pre-training dataset. incorporated into an augmented likelihood loss function that
balances property optimization with sequence validity.
Conditional Generation Similarly, Mazuz et al. [19] combine a Transformer with
RL, using a policy gradient approach and the REINFORCE
Conditional generation offers another method for control-
algorithm [50]. After pre-training on SMILES strings, the
ling model outputs by embedding “prompts” or “control
model is fine-tuned to optimize molecular properties like
tags” into the input, which guide the generation toward de-
QED and inhibitory concentrations (pIC50). A reward func-
sired characteristics. RegLM [29] employs conditional gen-
tion proportional to the property values is applied for fully
eration to design synthetic cis-regulatory elements ( CREs-
generated, valid molecules, while intermediate generation
e.g., promoters, enhancers), where autoregressive generation
steps receive zero reward. The model optimizes the expected
is conditioned on a starter fragment that guides the predic-
return, with a high discount factor (γ = 0.99) to priori-
tion of subsequent tokens. Similarly, Evo [26] fine-tune a
tize near-term rewards during sequence generation. Despite
model on 82, 430 loci containing CRISPR-Cas sequences,
these successes, we note that RL is often impractical due
using prompt tokens (e.g., “cas9,” “cas12,” “cas13”) to opti-
to the challenges of designing effective reward functions,
mize gRNA sequences for improved efficiency and reduced
which demand significant biological and computational in-
off-target effects.
sight, especially given the high-dimensional action spaces in
Progen2 conditions the generation of antibody (pro-
biological design.
tein) sequences on three-residue motif prompts, while Prot-
Mamba enables homologous protein generation by condi-
Custom Objective Functions
tioning on proteins from the desired family as context. RFD-
iffusionAA [24] ensures accurate protein-ligand complex Non-RL methods also employ custom loss functions to di-
generation by conditioning the denoising process on the rectly evaluate sequence properties, allowing for property-
presence of an unaltered ligand during diffusion. In con- specific optimization during generation. NOS[25] uses cus-
trast, MolGPT [17] embeds control tokens directly in the tom objective functions to optimize properties such as bind-
pre-training inputs. While effective, this approach retrains ing affinity and expression yield. This is achieved by incor-
the model from scratch for each new property or combi- porating a value function, v θ (w), trained via a separate dis-
nation of properties, diverging from the more general FM criminator (or value network), which shares hidden layers
paradigm. with the generative diffusion model up to a certain depth.
While conditional generation enables control over fine- The discriminator is trained to predict the target objective for
grained and numerical properties, it presents several limita- proteins in the training set. Once trained, the value function
tions. Chief among these is the reliance on examples in the is applied to the hidden states of the sequence representation
training or fine-tuning data, which can constrain the model’s in the denoising network, and the model uses gradient ascent
ability to discover novel ways of achieving desired proper- on these hidden states to maximize the objective value.
ties. Additionally, the model may develop a bias toward re- The Regression Transformer takes a similar approach
taining features correlated with the target properties from the by alternating between sequence generation and numerical-
training data, potentially hampering diversity in generated property regression tasks. It introduces a custom “prop-
data. erty prediction objective” that masks numerical tokens rep-
resenting property values, requiring the model to predict
Reinforcement Learning these values from the associated textual sequence: J P =
Reinforcement learning (RL) offers a promising alternative m ke a n x s, θ E xt z∼ a Z re T p [ t l h o e g a p s θ s ( o x c p i | a x te t) d ], t w ex h tu er a e l x to p k a e r n e s, th a e nd pro z pe ∼ rty Z to p -
by guiding the generation with a reward function. In RL, T
denotes the constrained permutation order ensuring that
an agent learns to make decisions through feedback from
only property tokens are masked. Additionally, a “self-
an environment, optimizing for specific objectives. In se-
consistency loss” is introduced to ensure the generated se-
quence generation, each token is treated as an action, and
quence adheres to the primed property by using the model’s
the model is fine-tuned based on how well the generated
own property prediction as a target during generation:
sequence meets the desired conditions. RL’s flexibility in
J = J (x) + α · J (xˆ), where J is the conditional
handling complex, non-linear reward landscapes makes it SC G p G
text generation objective, J is the property prediction ob-
ideal for multi-objective optimization, where properties like p
jective. By alternating between these custom loss functions,
bioactivity and molecular diversity must be balanced.
the model can effectively optimize conditional generation
The MCMG model [18] employs RL to control multiple
for fine-grained numerical properties.
properties in small-molecule generation. Initially, a condi-
tional Transformer generates molecules based on property
Post-Generation Filtering
embeddings. To improve the model’s efficiency and balance
diversity and novelty, the trained model is distilled into a A key measure of success for FMs in biological sequence
simpler recurrent model, which is then fine-tuned with RL. design is the ability to reliably generate sequences worth-
During RL training, the model generates molecules autore- while for practical validation. If in-silico validation is cost-
gressively, with a reward function evaluating properties such effective, high-throughput filtering can screen large numbers

---

<!-- Page 8 -->

of candidates, discarding those that fail to meet desired con- chemical limitations. A key challenge is managing tradeoffs,
ditions before advancing to in-vitro validation. where the model must balance generating valid and diverse
An example of this is the SSM-based CLM pro- molecules that meet all specified conditions.
posed by Ozccelik et al[27], where, after fine-tuning on In molecule generation, models are often evaluated based
MAPK1 inhibitors as mentioned above, they next gener- on criteria like validity, uniqueness, and novelty. A trade-
ated 256,000 molecules. The molecules are ranked based on off exists between validity and uniqueness: the more dis-
log-likelihood scores, computed by subtracting pre-training tinct or novel a generated molecule is, the harder it is to
scores from fine-tuning scores to focus on newly learned ensure its validity. This tradeoff is especially important in
bioactivity features. From the top 5,000 molecules, scaffold applications like antibacterial drug design, where novelty
similarity filtering divided them into high and low similar- is critical to address bacterial resistance. Users can adjust
ity groups. The highest-scoring molecules from each group priorities by tuning parameters such as the temperature in
were further evaluated using molecular dynamics simula- autoregressive Transformer models, emphasizing either va-
tions to assess binding affinity. lidity or uniqueness depending on the task. Several studies
Similarly, RegLM [29] apply post-generation filtering to explore this tradeoff. For instance, MCMG [18] uses rein-
synthetic CREs by using a sequence-to-function regression forcement learning to optimize multiple molecular proper-
model to predict activity levels. Sequences outside two stan- ties while maintaining both validity and diversity. DiffuMol
dard deviations from the mean activity were discarded. The [32] leverages a diffusion framework that provides stepwise
model also filtered sequences for cell type specificity, se- control over multiple objectives, making it easier to generate
lecting those with the highest specificity based on predicted novel molecules while optimizing specific properties. Diffu-
activity in target and off-target cell lines. Biological realism Mol’s use of the Transformer’s attention mechanism helps
was ensured through metrics like GC content and k-mer fre- balance diversity and specificity by focusing on key regions
quency, ensuring the synthetic sequences mimicked natural of the molecule that must meet certain property or scaffold
CREs. requirements, while allowing variation in other parts to pro-
mote molecular diversity.
Numerical Property Optimization Strategies
Sampling Algorithms
In biological design, many properties of interest are numeri-
cal, such as synthetic accessibility, drug-likeness, lipophilic- One part of autoregressive generation process that can af-
ity, and molecular weight. These molecular properties, eval- fect the natural plausibility of the output sequences is
uated using tools like RDKit, were considered in models like the sampling algorithm used to predict tokens based on
MolGPT[17] and DiffuMol[32]. Additional numerical prop- the model’s probability distribution. ProtGPT2[23] explored
erties include bioactivity[18], solubility[20], and inhibitory various sampling strategies to generate de-novo protein se-
potency[19]. For proteins, numerical properties like inter- quences, such as greedy search, beam search, and random
action potential (e.g., the Boman index), fluorescence, and sampling. They motivate this by noting that greedy and
stability (from datasets like TAPE [51]) are of interest [20]. beam search often lead to repetitive and deterministic se-
In DNA design, properties like gene expression levels are quences, which do not reflect the natural variability found in
key, as seen in DiscDiff [30], which optimizes regulatory el- proteins. On the other hand, random sampling from the top
ements to control expression. “k” tokens, especially when using a high value of ”k” (e.g.,
Several models incorporate these numerical targets di- k = 950), was found to produce more natural-like sequences
rectly into training. For instance, RL-based methods [19, 18] by introducing variability and capturing natural amino acid
optimize numerical properties as part of their reward func- propensities.
tions. One specialized approach is the Regression Trans-
former [20], which encodes numerical properties as tokens Multi-Modal FMs
within a decoder-only architecture. To handle numerical to- While FMs often excel at learning from a single data modal-
kenization, the authors introduced a tokenization scheme for ity, biological systems are inherently multi-modal, involving
floating-point numbers and developed numerical encodings, interactions across sequence, structure, and function at var-
similar to positional encodings, to help the model understand ious scales. Effectively integrating these diverse data types
numerical relationships. MolGPT [17], by contrast, reserves remains an open challenge in biological modeling. Often,
specific dimensions in the input embeddings for numerical biological data sources are treated independently, overlook-
values, avoiding explicit tokenization. This differs from the ing the interactions between systems. DNA sequences are
common NLP approach used in models like T5 [52] and often viewed in isolation, but DNA alone does not fully de-
GPTs [53], which apply word-piece tokenization to num- scribe an organism’s phenotype. As Denis Noble[54, 55] and
bers. others emphasize, biological processes result from interac-
tions across molecular, cellular, physiological and organis-
Multi-Condition Generation and Tradeoff mal scales[56].
Handling
Combining Multiple Forms of Biological Sequences
Generating molecules with multiple specified properties can
be challenging, especially when the desired combinations Multimodal approaches enhance GLMs’ understanding by
are rare in the training data or constrained by physical and incorporating epigenetic and transcriptomic data. The gLM2

---

<!-- Page 9 -->

model [57], trained on the Open MetaGenomic corpus, uses with biological sequence models, enabling tasks to be per-
both nucleotide sequences and corresponding amino acid se- formed through natural language prompts. Notable exam-
quences from coding regions, along with strand direction ples include ChatNT [38] for genomics and Nach0 [36] and
information, helping process gene regulation and reading InstructBioMol [37] for chemical sequences.
frames. ChatNT is a multimodal agent that combines biologi-
Hybrid approaches that combine multiple input modal- cal sequence processing with NLP, handling DNA, RNA,
ities or architectures are increasingly common in biologi- and proteins through conversational input. It integrates the
cal design. For example, MMDiff[34] integrates both struc- Nucleotide Transformer [60] with the Vicuna-7B language
tural (using rigid body frames for rotation and translation) model using a Perceiver-based projection layer, allowing for
and sequence data to jointly generate nucleic acid-protein seamless interaction in biological tasks through natural lan-
complexes. RFAA[24] tackles the complexity of model- guage. Nach0 extends this concept to SMILES molecular
ing biomolecular systems, including proteins, nucleic acids, sequences, using training data from PubMed abstracts and
small molecules, and metals. RFAA uses a three-track net- patents. It has been applied to tasks like molecular prop-
work architecture inspired by RoseTTAFold2 [58] with (1) erty prediction, generation, and reaction prediction. In a case
1D sequence data for amino acids, nucleic acids, and atom study, Nach0 was prompted to “Generate a random drug-
types, (2) pairwise relationships like residue distances or like small inhibitor molecule for Janus Kinase 3 (JAK3) that
bond types, and (3) 3D coordinate information, including contains a classic kinase hinge binding motif.” Despite lack-
atom positions and stereochemistry. RFAA also incorpo- ing 3D structural information, Nach0 successfully generated
rates a conditional diffusion fine-tuning approach to gener- eight valid molecules, with a discovery rate of 0.11%, com-
ate binding proteins, starting from substructures like ligands. pared to 1.53% from a structure-aware baseline. Instruct-
BioMol takes this further by training on natural language,
Combining Sequence and Structure
2D molecular graphs, protein sequences, and 3D structures.
Integrating structural information with sequence data can Its Motif-Guided Multimodal Feature Extraction Module al-
significantly improve model performance, especially for lows the model to handle tasks like molecule captioning,
tasks where geometry and physical constraints are crucial. A description-based molecule and protein generation, and pro-
common approach is to combine molecular graphs with se- tein property question answering.
quence data, providing geometric context that complements
raw sequences. Protein structures—secondary, tertiary, and Open Problems
quaternary—also offer essential spatial information that se-
quence data alone may not reveal. Additional inputs can Which Architectures for Which Biological Task:
include biological environment details, target receptors, or Many studies introduce specific approaches (e.g., Trans-
transcriptomic data linking RNA, DNA, and amino acid se- formers, diffusion, SSMs) for distinct applications, but there
quences. is little consensus on which architecture is best across bi-
For example, models like MMDiff [34], which gener- ological tasks. Direct comparisons are challenging due to
ate nucleic acid-protein complexes, use both sequence and inconsistent evaluations and benchmarks. We propose ex-
structural data for more accurate macromolecule modeling. ploring architectures that are underused in certain domains,
This is intended to help with handling Intrinsically Disor- such as diffusion models for textual molecular representa-
dered Regions is challenging since their structure cannot be tions. Additionally, we would compare the effects of dif-
fully inferred from sequence alone, underscoring the need ferent pre-training objectives, especially since many cur-
for both representations. ProtMamba [28] enhances protein rent objectives are borrowed from NLP, where sequence
inpainting and de novo protein generation by using homolo- behavior differs from biological data. Developing domain-
gous sequences, without relying on multiple sequence align- specific, self-supervised objectives—both multi-modal and
ments (MSAs). This approach captures evolutionary conser- sequence-only—would help create better representations for
vation and variability, providing valuable context for tasks biological tasks where additional modalities are unavailable.
like protein editing. The Gene Ontology (GO) [59] also Innovative Architectures to handle Data Limitations:
provides a structured framework for annotating biological While FMs have shown strong performance in specific bi-
processes, molecular functions, and cellular components. ological domains, scalability and generalization remain dif-
Although models like Progen2 [22] partially leverage GO ficult due to the relatively small and fragmented datasets in
terms for conditioning, the full graph structure of the on- biology. In NLP, large datasets have driven breakthroughs in
tology, which allows for rich parent-child relationships, re- models like GPT-3 [53], with scaling laws analyzed by Ka-
mains underutilized for generation. plan et al. [61] and Bahri et al. [62]. Similar trends have been
observed in biological models [21, 63, 64], but addressing
Incorporating Natural Language and Domain
data limitations may require lighter architectures or novel
Knowledge methods for obtaining generalizable representations without
One of the most appealing aspects of the FM paradigm, par- massive datasets. This demands new strategies for scalable
ticularly with models like GPT-4, is their ability to inter- biological models.
act via natural language, offering flexibility that is largely Enhancing Generalization and Transfer to Low-Data
absent in biology-specific models. To bridge this gap, re- Regimes: Finally, we would like to explore the important
cent works have focused on integrating natural language application transfer learning to help CLMs generalize to

---

<!-- Page 10 -->

classes of molecules that do not have a lot of available train- References
ing data. Specifically, Quaternary Ammonium Compounds [1] Protein structure initiative. National Institute of Gen-
are a group of chemicals with important antibiotic properties eral Medical Sciences, U.S. National Institutes of
but currently the number of available examples of molecules Health, 2000–2015. Available from https://www.
in this class is small. For example, we may experiment us- nigms.nih.gov/Research/specificareas/PSI.
ing techniques similar to Progen2’s[22] antibody generation
[2] Francis S. Collins and Leslie Fink. The human
approach combining fine-tuning with conditional generation
genome project. Alcohol Health and Research World,
to overcome the bias from pre-training. We would like to ex-
19(3):190–195, 1995.
plore which architectures best enable transfer learning in this
[3] Natalie L Dawson, Ian Sillitoe, Jonathan G Lees,
setting and additional techniques to guide generation toward
Su Datt Lam, and Christine A Orengo. Cath-gene3d:
the correct region of chemical space.
generation of the resource and its use in obtaining
Better Integration of Biological Modalities:
structural and functional annotations for protein se-
A promising direction is the integration of various bi- quences. Protein Bioinformatics: From Protein Mod-
ological modalities, such as combining chemical graphs ifications and Networks to Proteomics, pages 79–110,
with SMILES representations in CLMs. Techniques like 2017.
Adapters, used by Liu et al. [65] for molecular captioning,
[4] Molly Morgan Jones, Sophie Castle-Clarke, Daniel
may also improve molecule generation. We would begin by
Brooker, Edward Nason, Farah Huzair, and Joanna
evaluating the impact of these approaches by testing gen-
Chataway. The structural genomics consortium: a
erated sequence validity and property control. Furthermore,
knowledge platform for drug discovery: a summary.
we aim to explore pre-training models with Gene Ontology
Rand health quarterly, 4(3), 2014.
graph structures, extending Progen’s use of GO-derived key-
[5] Protein Data Bank. Protein data bank. Nature New
words, to enhance protein generation.
Biol, 233(223):10–1038, 1971.
Enabling Better Control in Generation:
[6] John Jumper, Richard Evans, et al. Highly accurate
We would like to push the boundaries of FMs’ capabilities
protein structure prediction with alphafold. nature,
to generalize to rare or physically unlikely property combi-
596(7873):583–589, 2021.
nations in the biological sequence space. This would involve
[7] Alexandre Blanco-Gonzalez, Alfonso Cabezon, Ale-
studying whether the difficulty in generating these combina-
jandro Seco-Gonzalez, Daniel Conde-Torres, Paula
tions is due to their absence from training data or intrinsic
Antelo-Riveiro, Angel Pineiro, and Rebeca Garcia-
physical constraints. This investigation connects to Ferruz
Fandino. The role of ai in drug discovery: chal-
et al.’s [23] concept of ”dark” regions in protein space, and
lenges, opportunities, and strategies. Pharmaceuticals,
could provide insight into improving generation for uncom-
16(6):891, 2023.
mon combinations.
[8] Christopher A Voigt. Synthetic biology 2020–2030:
six commercially-available products that are changing
Conclusion our world. Nature Communications, 11(1):1–6, 2020.
[9] Tzu-Chieh Tang, Bolin An, Yuanyuan Huang, Sangita
The field is moving ahead rapidly; a large number of the
Vasikaran, Yanyi Wang, Xiaoyu Jiang, Timothy K Lu,
cited papers here are from preprint servers such as arXiv
and Chao Zhong. Materials design by synthetic biol-
and BioRxiv, highlighting the need for standardization of
ogy. Nature Reviews Materials, 6(4):332–350, 2021.
datasets and metrics. Furthermore, looking ahead, it is cru-
[10] Rishi Bommasani, Drew A Hudson, Ehsan Adeli, Russ
cial for research to prioritize rigorous comparative evalua-
Altman, Simran Arora, Sydney von Arx, Michael S
tions of different model architectures for biological genera-
Bernstein, Jeannette Bohg, Antoine Bosselut, Emma
tion, more sophisticated integration of biological modalities,
Brunskill, et al. On the opportunities and risks of
and improved strategies for generalization across diverse bi-
foundation models. arXiv e-prints, pages arXiv–2108,
ological systems. This is especially timely, as the United
2021.
States National Academies of Sciences, Engineering, and
Medicine are founding a committee on Foundation Models [11] Ashish Vaswani. Attention is all you need. arXiv
for Scientific Discovery and Innovation, underscoring the preprint arXiv:1706.03762, 2017.
growing importance of this area.[66] By addressing these [12] Albert Gu, Karan Goel, and Christopher Re´. Efficiently
challenges, FMs could truly revolutionize fields such as drug modeling long sequences with structured state spaces.
discovery, synthetic biology, and genetic engineering, accel- arXiv preprint arXiv:2111.00396, 2021.
erating breakthroughs and moving us closer to practical, AI- [13] Albert Gu and Tri Dao. Mamba: Linear-time sequence
driven biological innovations that can meaningfully impact modeling with selective state spaces. arXiv preprint
our understanding and manipulation of life. arXiv:2312.00752, 2023.
[14] Xiang Li, John Thickstun, Ishaan Gulrajani, Percy S
Acknowledgements Liang, and Tatsunori B Hashimoto. Diffusion-lm im-
proves controllable text generation. Advances in Neu-
This work was supported in part by the National Science ral Information Processing Systems, 35:4328–4343,
Foundation Grant No. 2411529 and Grant No. 2310113. 2022.

---

<!-- Page 11 -->

[15] Emiel Hoogeboom, Didrik Nielsen, Priyank Jaini, Sequence modeling and design from molecular to
Patrick Forre´, and Max Welling. Argmax flows and genome scale with evo. Science, 2024.
multinomial diffusion: Learning categorical distribu- [27] Rıza O¨ zc¸elik, Sarah de Ruiter, Emanuele Criscuolo,
tions. Advances in Neural Information Processing Sys- and Francesca Grisoni. Chemical language modeling
tems, 34:12454–12465, 2021. with structured state space sequence models. Nature
[16] Emiel Hoogeboom, Alexey A Gritsenko, Jasmijn Bast- Communications, 15(1):6176, 2024.
ings, Ben Poole, Rianne van den Berg, and Tim Sali- [28] Damiano Sgarbossa, Cyril Malbranke, and Anne-
mans. Autoregressive diffusion models. In Interna- Florence Bitbol. Protmamba: a homology-aware but
tional Conference on Learning Representations, 2021. alignment-free protein state space model. bioRxiv,
[17] Viraj Bagal, Rishal Aggarwal, PK Vinod, and U Deva pages 2024–05, 2024.
Priyakumar. Molgpt: molecular generation using a [29] Avantika Lal, David Garfield, Tommaso Biancalani,
transformer-decoder model. Journal of Chemical In- and Gokcen Eraslan. reglm: Designing realistic regu-
formation and Modeling, 62(9):2064–2076, 2021. latory dna with autoregressive language models. In In-
ternational Conference on Research in Computational
[18] Jike Wang, Chang-Yu Hsieh, Mingyang Wang, Xi-
aorui Wang, Zhenxing Wu, Dejun Jiang, Benben Liao, Molecular Biology, pages 332–335. Springer, 2024.
Xujun Zhang, Bo Yang, Qiaojun He, et al. Multi- [30] Zehui Li, Yuhao Ni, William AV Beardall, Guoxuan
constraint molecular generation based on conditional Xia, Akashaditya Das, Guy-Bart Stan, and Yiren Zhao.
transformer, knowledge distillation and reinforcement Discdiff: Latent diffusion model for dna sequence gen-
learning. Nature Machine Intelligence, 3(10):914–922, eration. CoRR, 2024.
2021. [31] Simon Senan, Aniketh Janardhan Reddy, Zach Nuss-
[19] Eyal Mazuz, Guy Shtar, Bracha Shapira, and Lior baum, Aaron Wenteler, Matei Bejan, Michael I Love,
Rokach. Molecule generation using transformers and Wouter Meuleman, and Luca Pinello. Dna-diffusion:
policy gradient reinforcement learning. Scientific Re- Leveraging generative models for controlling chro-
ports, 13(1):8799, 2023. matin accessibility and gene expression via synthetic
regulatory elements. In ICLR 2024 Workshop on Ma-
[20] Jannis Born and Matteo Manica. Regression trans-
chine Learning for Genomics Explorations, 2024.
former enables concurrent sequence regression and
generation for molecular language modelling. Nature [32] Xinmiao Peng and Fei Zhu. Hitting stride by degrees:
Machine Intelligence, 5(4):432–444, 2023. Fine grained molecular generation via diffusion model.
Expert Systems with Applications, 244:122949, 2024.
[21] Ali Madani, Ben Krause, Eric R Greene, Subu Subra-
[33] Sarah Alamdari, Nitya Thakkar, Rianne van den Berg,
manian, Benjamin P Mohr, James M Holton, Jose Luis
Alex Lu, Nicolo Fusi, Ava Amini, and Kevin Yang.
Olmos, Caiming Xiong, Zachary Z Sun, Richard
Protein generation with evolutionary diffusion: se-
Socher, et al. Large language models generate func-
quence is all you need. In NeurIPS 2023 Generative
tional protein sequences across diverse families. Na-
AI and Biology (GenBio) Workshop, 2023.
ture Biotechnology, 41(8):1099–1106, 2023.
[34] Alex Morehead, Jeffrey Ruffolo, Aadyot Bhatnagar,
[22] Erik Nijkamp, Jeffrey A Ruffolo, Eli N Weinstein,
and Ali Madani. Towards joint sequence-structure gen-
Nikhil Naik, and Ali Madani. Progen2: exploring the
eration of nucleic acid and protein complexes with se
boundaries of protein language models. Cell systems,
(3)-discrete diffusion. In Proceedings of the NeurIPS
14(11):968–978, 2023.
2023 Workshop on Machine Learning in Structural Bi-
[23] Noelia Ferruz, Steffen Schmidt, and Birte Ho¨cker. ology, 2023.
Protgpt2 is a deep unsupervised language model for
[35] Christof Angermueller, David Dohan, David Belanger,
protein design. Nature communications, 13(1):4348,
Ramya Deshpande, Kevin Murphy, and Lucy Colwell.
2022.
Model-based reinforcement learning for biological se-
[24] Rohith Krishna, Jue Wang, Woody Ahern, Pas- quence design. In International conference on learning
cal Sturmfels, Preetham Venkatesh, Indrek Kalvet, representations, 2019.
Gyu Rie Lee, Felix S Morey-Burrows, Ivan An-
[36] Micha Livne, Zulfat Miftahutdinov, Elena Tutubalina,
ishchenko, Ian R Humphreys, et al. Generalized
Maksim Kuznetsov, Daniil Polykovskiy, Annika Brun-
biomolecular modeling and design with rosettafold all-
dyn, Aastha Jhunjhunwala, Anthony Costa, Alex
atom. Science, 384(6693):eadl2528, 2024.
Aliper, Ala´n Aspuru-Guzik, et al. nach0: Multimodal
[25] Nate Gruver, Samuel Stanton, Nathan Frey, Tim GJ natural and chemical languages foundation model.
Rudner, Isidro Hotzel, Julien Lafrance-Vanasse, Chemical Science, 15(22):8380–8389, 2024.
Arvind Rajpal, Kyunghyun Cho, and Andrew G
[37] Xiang Zhuang, Keyan Ding, Tianwen Lyu, Yinuo
Wilson. Protein design with guided discrete diffusion.
Jiang, Xiaotong Li, Zhuoyi Xiang, Zeyuan Wang,
Advances in neural information processing systems,
Ming Qin, Kehua Feng, Jike Wang, et al. Instruct-
36, 2024.
biomol: Advancing biomolecule understanding and de-
[26] E Nguyen, M Poli, MG Durrant, AW Thomas, B Kang, sign following human instructions. arXiv preprint
J Sullivan, MY Ng, A Lewis, A Patel, A Lou, et al. arXiv:2410.07919, 2024.

---

<!-- Page 12 -->

[38] Guillaume Richard, Bernardo P de Almeida, Hugo International conference on machine learning, pages
Dalla-Torre, Christopher Blum, Lorenz Hexemer, 8821–8831. Pmlr, 2021.
Priyanka Pandey, Stefan Laurent, Marie P Lopez,
[50] Ronald J Williams. Simple statistical gradient-
Alexander Laterre, Maren Lang, et al. Chatnt: A mul-
following algorithms for connectionist reinforcement
timodal conversational agent for dna, rna and protein
learning. Machine learning, 8:229–256, 1992.
tasks. bioRxiv, pages 2024–04, 2024.
[51] Roshan Rao, Nicholas Bhattacharya, Neil Thomas,
[39] Jianlin Su, Murtadha Ahmed, Yu Lu, Shengfeng Pan,
Yan Duan, Peter Chen, John Canny, Pieter Abbeel, and
Wen Bo, and Yunfeng Liu. Roformer: Enhanced trans-
Yun Song. Evaluating protein transfer learning with
former with rotary position embedding. Neurocomput-
tape. Advances in neural information processing sys-
ing, 568:127063, 2024.
tems, 32, 2019.
[40] Eric Nguyen, Michael Poli, Marjan Faizi, Armin
[52] Colin Raffel, Noam Shazeer, Adam Roberts, Kather-
Thomas, Michael Wornow, Callum Birch-Sykes, Ste-
ine Lee, Sharan Narang, Michael Matena, Yanqi Zhou,
fano Massaroli, Aman Patel, Clayton Rabideau,
Wei Li, and Peter J Liu. Exploring the limits of transfer
Yoshua Bengio, et al. Hyenadna: Long-range genomic
learning with a unified text-to-text transformer. Jour-
sequence modeling at single nucleotide resolution. Ad-
nal of machine learning research, 21(140):1–67, 2020.
vances in neural information processing systems, 36,
[53] Tom B Brown. Language models are few-shot learners.
2024.
arXiv preprint arXiv:2005.14165, 2020.
[41] Zhilin Yang. Xlnet: Generalized autoregressive pre-
training for language understanding. arXiv preprint [54] Denis Noble. A theory of biological relativity: no priv-
arXiv:1906.08237, 2019. ileged level of causation. Interface focus, 2(1):55–64,
2012.
[42] Michael Moret, Lukas Friedrich, Francesca Grisoni,
Daniel Merk, and Gisbert Schneider. Generative [55] Denis Noble. It’s time to admit that genes are not the
molecular design in low data regimes. Nature Machine blueprint for life. Nature, 626(7998):254–255, 2024.
Intelligence, 2(3):171–180, 2020. [56] Jeremy Ramsden. Bioinformatics: an introduction.
[43] Michael Poli, Stefano Massaroli, Eric Nguyen, Springer Nature, 2023.
Daniel Y Fu, Tri Dao, Stephen Baccus, Yoshua Ben- [57] Andre Cornman, Jacob West-Roberts, Antonio Pe-
gio, Stefano Ermon, and Christopher Re´. Hyena hierar- dro Camargo, Simon Roux, Martin Beracochea, Milot
chy: Towards larger convolutional language models. In Mirdita, Sergey Ovchinnikov, and Yunha Hwang. The
International Conference on Machine Learning, pages omg dataset: An open metagenomic corpus for mixed-
28043–28078. PMLR, 2023. modality genomic language modeling. bioRxiv, pages
[44] Bohao Xu, Yingzhou Lu, Yoshitaka Inoue, 2024–08, 2024.
Namkyeong Lee, Tianfan Fu, and Jintai Chen. [58] Minkyung Baek, Ivan Anishchenko, Ian R Humphreys,
Protein-mamba: Biological mamba models for protein Qian Cong, David Baker, and Frank DiMaio. Effi-
function prediction. arXiv preprint arXiv:2409.14617, cient and accurate prediction of protein structure using
2024. rosettafold2. BioRxiv, pages 2023–05, 2023.
[45] Zhangzhi Peng, Benjamin Schussheim, and Pranam [59] Michael Ashburner, Catherine A Ball, Judith A Blake,
Chatterjee. Ptm-mamba: A ptm-aware protein lan- David Botstein, Heather Butler, J Michael Cherry, Al-
guage model with bidirectional gated mamba blocks. lan P Davis, Kara Dolinski, Selina S Dwight, Janan T
bioRxiv, 2024. Eppig, et al. Gene ontology: tool for the unification of
[46] Mohammad Bavarian, Heewoo Jun, Nikolas Tezak, biology. Nature genetics, 25(1):25–29, 2000.
John Schulman, Christine McLeavey, Jerry Tworek, [60] Hugo Dalla-Torre, Liam Gonzalez, Javier Mendoza-
and Mark Chen. Efficient training of language models Revilla, Nicolas Lopez Carranza, Adam Henryk
to fill in the middle. arXiv preprint arXiv:2207.14255, Grzywaczewski, Francesco Oteri, Christian Dallago,
2022. Evan Trop, Bernardo P de Almeida, Hassan Sirelkha-
[47] Gonzalo Benegas, Chengzhong Ye, Carlos Albors, tim, et al. The nucleotide transformer: Building and
Jianan Canal Li, and Yun S Song. Genomic language evaluating robust foundation models for human ge-
models: Opportunities and challenges. arXiv preprint nomics. BioRxiv, pages 2023–01, 2023.
arXiv:2407.11435, 2024. [61] Jared Kaplan, Sam McCandlish, Tom Henighan,
[48] Daniel Y Fu, Tri Dao, Khaled Kamal Saab, Armin W Tom B Brown, Benjamin Chess, Rewon Child, Scott
Thomas, Atri Rudra, and Christopher Re. Hungry Gray, Alec Radford, Jeffrey Wu, and Dario Amodei.
hungry hippos: Towards language modeling with state Scaling laws for neural language models. arXiv
space models. In The Eleventh International Confer- preprint arXiv:2001.08361, 2020.
ence on Learning Representations, 2022.
[62] Yasaman Bahri, Ethan Dyer, Jared Kaplan, Jaehoon
[49] Aditya Ramesh, Mikhail Pavlov, Gabriel Goh, Scott Lee, and Utkarsh Sharma. Explaining neural scaling
Gray, Chelsea Voss, Alec Radford, Mark Chen, and laws. Proceedings of the National Academy of Sci-
Ilya Sutskever. Zero-shot text-to-image generation. In ences, 121(27):e2311878121, 2024.

---

<!-- Page 13 -->

[63] Alexander Rives, Joshua Meier, Tom Sercu, Siddharth
Goyal, Zeming Lin, Jason Liu, Demi Guo, Myle
Ott, C Lawrence Zitnick, Jerry Ma, et al. Biolog-
ical structure and function emerge from scaling un-
supervised learning to 250 million protein sequences.
Proceedings of the National Academy of Sciences,
118(15):e2016239118, 2021.
[64] Nathan C Frey, Ryan Soklaski, Simon Axelrod, Sid-
dharth Samsi, Rafael Gomez-Bombarelli, Connor W
Coley, and Vijay Gadepally. Neural scaling of
deep chemical models. Nature Machine Intelligence,
5(11):1297–1305, 2023.
[65] Zhiyuan Liu, Sihang Li, Yanchen Luo, Hao Fei, Yixin
Cao, Kenji Kawaguchi, Xiang Wang, and Tat-Seng
Chua. Molca: Molecular graph-language modeling
with cross-modal projector and uni-modal adapter.
In Proceedings of the 2023 Conference on Empiri-
cal Methods in Natural Language Processing, pages
15623–15638, 2023.
[66] National Academies of Sciences Engineering and
Medicine. Foundation models for scientific discovery
and innovation: Opportunities across the department of
energy, 2024. Accessed: 2024-10-22.
