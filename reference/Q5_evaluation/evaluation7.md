<!-- Page 1 -->

nature reviews bioengineering https://doi.org/10.1038/s44222-025-00349-8
Review article Check for updates
AI-driven protein design
Huan Yee Koh 1,2,5, Yizhen Zheng2,5, Madeleine Yang1, Rohit Arora1, Geoffrey I. Webb 2 , Shirui Pan 3 , Li Li 1,4
& George M. Church1,4
Abstract Sections
Protein design is undergoing a revolution driven by artificial intelligence Introduction
(AI), transforming how we engineer proteins for applications in drug
AI-driven protein design
discovery, biotechnology and synthetic biology. By navigating the
AI toolkits for protein design
immense complexity of protein sequence space and overcoming the
AI-driven protein design
limitations of structural and functional data, AI enables unprecedented
case studies
precision and speed in designing novel proteins with tailored functions.
Outlook
Central to this Review is a comprehensive and actionable roadmap
for designers, providing step-by-step guidance on how to integrate
state-of-the-art AI tools into protein design workflows, including tools
for structural and functional prediction as well as generative models
for de novo design. To illustrate this roadmap in practice, we present
case studies showcasing AI-driven protein design, from engineering
therapeutic proteins to designing novel proteins that unlock enzyme
functions and reprogramme biomolecular systems. Looking ahead,
we outline future directions highlighting the vast potential of AI to
revolutionize synthetic biology, expedite drug development and drive
sustainable biotechnology, positioning it as a transformative force at
the forefront of protein design.
1Department of Genetics, Blavatnik Institute, Harvard Medical School, Boston, MA, USA. 2Department of Data
Science and Artificial Intelligence, Monash University, Clayton, Victoria, Australia. 3School of Information and
Communication Technology, Griffith University, Southport, Queensland, Australia. 4Wyss Institute for Biologically
Inspired Engineering, Harvard University, Boston, MA, USA. 5These authors contributed equally: Huan Yee Koh,
Yizhen Zheng. e-mail: geoff.webb@monash.edu; s.pan@griffith.edu.au; li_li@hms.harvard.edu; gchurch@
genetics.med.harvard.edu
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1034

---

<!-- Page 2 -->

Review article
Key points AI tools, particularly those based on deep learning methodologies
(Box 1), have matured to the point where integrating them into protein
design workflows is not only feasible but essential. By enabling accurate
• Artificial intelligence (AI) is fundamentally reshaping protein design, generation, evaluation and optimization of protein structures and
transforming what was once a trial-and-error process into a predictive sequences, AI has transformed protein design from a trial-and-error
discipline. AI-driven tools now generate, evaluate and optimize process into a predictive, efficient discipline.
proteins with unprecedented speed and accuracy. To appreciate the role of AI in this rapidly evolving field, we present
a comprehensive roadmap that explores key aspects of this integration.
• This Review offers a practical roadmap for integrating AI tools into First, we examine the workflows involved in directed evolution and
protein design: it first outlines directed evolution and rational design rational design, highlighting how AI integration enhances these strate-
workflows and then categorizes an expanding suite of AI tools into gies by streamlining and optimizing various stages (see ‘AI-driven pro-
seven toolkits that support different tasks throughout the workflows. tein design’). Next, we delve into the specific AI tools available for each
step within these workflows, illustrating how these technol ogies con-
• The roadmap pairs each workflow step, from initial design to protein tribute to improved efficiency and precision at each phase (see ‘AI tool-
synthesis for experimental validation, with the most suitable toolkit kits for protein design’). Finally, we explore the current applications of
and guides designers in assembling end-to-end AI-driven workflows. AI-driven protein design in areas such as biotechnology, drug discovery
and synthetic biology (see ‘AI-driven protein design case studies’) and
• Case studies demonstrate the roadmap in action, showing how discuss future directions this field is poised to take (see ‘Outlook’).
toolkits synergistically combine to create AI-driven workflows
that shorten experimental cycles and unlock functions beyond AI-driven protein design
conventional reach. Protein design projects begin by defining objectives across three inter-
connected dimensions: function, structure and developability, and by
designing protein sequences that meet those objectives. Conceptually,
Introduction this process can be viewed as a search problem in the astronomical
Protein design has long been a cornerstone of scientific innovation, expanse of possible protein sequences (Fig. 2a-I). Framing the search
driving breakthroughs across drug development1, biotechnology2 and along these dimensions enables the development of strategies that
synthetic biology3. However, despite substantial progress, traditional efficiently navigate vast possibilities and transform an otherwise
methods are reaching their limits in addressing the vast complexity unmanageable challenge into a tractable, strategically guided process.
of protein sequences and functional diversity4. As demand grows for In the functional dimension, one assesses whether an existing pro-
precise, scalable design solutions, Artificial intelligence (AI) is emerg- tein performs the desired activity but requires optimization, or whether
ing as a transformative force to tackle challenges once considered a superior protein can be designed de novo. Constraining the search to
intractable5–14. variants of a known parent limits the explored sequence space, whereas
Protein design has relied on two main strategies: directed de novo approaches leverage mechanistic insights and predictive mod-
evolution2 and rational design15,16. Directed evolution mimics natu- els to explore a wider sequence space efficiently. The structural dimen-
ral selection by introducing random mutations, screening large sion considers whether specific features, such as scaffold symmetry,
variant libraries and selecting those with desired traits. By contrast, must be achieved or whether focusing solely on improving functional
rational design makes targeted, hypothesis-driven modifications activity is sufficient. Finally, the developability dimension ensures that
guided by structural and functional data17,18. Yet, directed evolution the designed protein can be expressed efficiently, maintains favourable
is labour-intensive and time-consuming19, whereas rational design biophysical properties and is manufacturable at scale.
is limited by the availability and accuracy of structural information6,
limiting either approach from efficiently traversing the enormous Protein design strategies
sequence space. Even with classical computational methods, finding Once an objective is defined, protein design proceeds through an
optimal designs remains challenging because these approaches often iterative cycle of three phases: defining strategy, library design and
fail to leverage modern hardware capabilities and cannot bridge gaps screening and optimization (Fig. 2). The cycle begins by selecting a
in the understanding of protein biophysics20. The search space itself directed evolution or rational design strategy (Fig. 2a (I)) to guide
is astronomical: a typical 350-residue protein has of the order of 10455 library generation, narrowing the sequence space to produce prom-
possible sequences4, making exhaustive exploration impractical using ising candidates (Fig. 2a (II)). These candidates are back-translated into
conventional methods. DNA for expression and experimental validation, and top candidates
AI-driven advances have spurred the development of new undergo further refinement in subsequent cycles (Fig. 2a (III)). The
tools that offer unprecedented speed, scale and precision for both key distinction between directed evolution and rational design lies in
strategies9,19 (Fig. 1). In directed evolution, AI tools accurately pro- how the sequence space is explored during the library design phase
pose beneficial mutations21 and predict function from sequence22, to meet objectives.
substantially reducing experimental cycles. In rational design, AI tools
predict structure from sequence at near-experimental accuracy6,7 Directed evolution. Directed evolution focuses on the ‘what’ —
without homologous templates23 and generate novel proteins from measurable outcomes that guide design towards defined objectives.
scratch9,24. Moreover, biomolecular co-folding models now predict It re-engineers natural proteins by selecting a parent and applying
multimolecular complexes among proteins, nucleotides and small iterative cycles of mutagenesis (Fig. 2a (II)), screening and selection
molecules directly from sequence data14,25, expanding the scope of (Fig. 2a (III)). Instead of dissecting underlying mechanisms, it relies on
AI-driven design13. experimental feedback to guide improvements. This strategy can be
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1035

---

<!-- Page 3 -->

Review article
Foundations of Computational-aided AI-driven
protein design protein design protein design
1997: First
computational 2024: AlphaFold 3
sequence redesign 2022: ESM Metagenomic predicted joint
1 s 9 eq 5 u 2 e : F n i c rs e t m pr a o p t p e e in d o p n ro a te z i i n nc-finger 2 co 0 l 1 l 4 ec : t U e n d i P 8 r 0 o t m illion A pr t e la d s i c w te it d h s > t 6 r 1 u 7 c m tu i r l e li s on b i b n i e t o t e m t r e a o r c l t t e h io c a u n n l s a s t r p r u e c c t ia u l r i e ze s d
1958: First protein 1 p 9 ro 9 t 8 e : i n F i d rs e t s n ig o n v e e d l a P n D n B o r t e a l t e e a d s e se d q 1 u 0 e 0 n ,0 c 0 es 0 , 2022: ESMFold tools
structure solved computationally structures i s m tr p u r c o tu ve re s p e r ff e ic d i i e c n ti c o y n of 2024: RFDiffusionAA
and BindCraft for
1988: Pioneering 1999: PDB released 2010–2016: Deep 2020: generating protein
rational design of 10,000 structures learning gained traction AlphaFold 2 2022: Foldseek for very binders
four-helix bundle with AlexNet (2012), achieved near- fast structure alignment
2003: Designed AlphaGo (2016) and experimental 2024: Variational
1993: Pioneering top 7 protein with Google's NMT (2016) accuracy in 2022: ProteinMPNN and Synthesis cut protein
directed evolution novel folds via structure ESM-IF for inverse folding synthesis costs
with subtilisin E computational tools 2017: Transformer model predictiona structure-to-sequence by up to a trillion-fold
1964: Sequence 2002: UniProt 2018: AlphaFold debut, 2021: AlphaFoldDB 2023: Generative structure
database (PIR) combines Protein winning the CASP13 launched with the aim models, RFDiffusion and
Information protein structure of releasing 100 million Chroma, for designing
1971: Structure Resources, Swiss-Prot prediction competition predicted structures protein backbone
database (Protein and TrEMBL
Data Bank, PDB) 2019: Protein language 2021: AlphaFold 2 was 2023: ProGen language
2005: UCSF Chimera models, seq2vec, released model for generating
1980–1990s: — visualization UniRep and TAPE, functional sequence
Swiss-Prot, TrEMBL, system for protein predict functions from 2021: Structure prediction
GenBank, Pfam and analysis sequences tools expanded with 2023: RoseTTAFold All-
InterPro databases 2005: Rosetta RosettaFold, RGN2, Atom for predicting joint
Commons and other 2019: Structured ColabFold and OpenFold structures of proteins and
1990: BLAST sequence softwares for protein Transformer for inverse other biomolecular
alignment tool design released folding protein design 2021: ESM and ProtTrans entities
protein language models
1993: MODELLER released
homology structure 2005–2010: Hidden 2020: DeepBLAST
prediction tool Markov models used sequence alignment
for homology detection tool
and function prediction
1999: Rosetta ab initio
structure prediction tool
1980–1990s: AMBER
Protein database
and GROMACS for
molecular dynamics Protein design tools
simulation Notable events
Fig. 1 | Historical development of artificial intelligence-driven protein design Transformer model194 in 2017, which laid the groundwork for advancements
tools. This timeline highlights landmark events in protein design, categorized in protein design. Finally, the ‘Artificial intelligence (AI)-driven protein design’
into three distinct generations. The ‘Foundations of protein design’ (1950s–1990s) (2018–present) era revolutionized the field with the advent of AI tools, such
established key sequence and structural data sets alongside foundational tools as AlphaFold 2 (ref. 6), achieving near-experimental accuracy in structural
for protein analysis and design. The ‘Computational-aided protein design’ predictions. Recent innovations include structure and function prediction
(1990s–2010s) introduced homology modelling and computational tools for methods, generative models and DNA synthesis tools, offering unprecedented
structure prediction and protein engineering, contributing substantially to the capabilities for protein design. Looking forward, future directions focus on
field. The transformative impact of deep learning during the 2010s was evident in enhancing protein design through advanced AI architectures, accelerating drug
other domains, such as image recognition with AlexNet192 and AlphaGo’s success discovery and development and expanding the frontiers of synthetic biology.
in mastering Go193. These breakthroughs culminated in the introduction of the
effective when outcomes are easier to measure than mechanisms are objectives by measuring against desired outcomes. Sequence–function
to model, such as in high-throughput functional assays26,27. AI models, which predict protein sequences corresponding to target
Once a parent is chosen, the process mimics natural selection functions, have a critical role19. Although insights from these models
through three iterative steps: generating variant libraries, screening for can be valuable, the accuracy of their predictions is paramount to
desired traits and selecting top candidates for refinement. Tradition- ensuring successful outcomes.
ally, this entails numerous expensive experimental cycles. AI-driven
methods accelerate this process21,26 by shifting early validation to a Rational design. Rational design focuses on the ‘how’ — the mecha-
virtual environment. AI tools predict fitness and function, enabling tar- nisms driving a protein to exhibit properties aligned with defined
geted and thus fewer experiments. This reduces timelines and experi- objectives. It leverages understanding of sequence–structure–func-
mental burden28,29. Similarly, AI-driven directed evolution achieves tion relationships to propose targeted designs (Fig. 2a (II)), followed
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1036

---

<!-- Page 4 -->

Review article
Box 1 | AI learning paradigms and model architectures
Artificial intelligence (AI) toolkits have transformed protein design. capturing key patterns in data. Variants such as VQ-VAE use a
In this Review, we focus on AI-driven tools powered by deep learning discrete codebook instead of a continuous prior, allowing data
models that automatically infer protein biophysics from data, to be compressed into meaningful tokens.
uncovering insights that traditional machine-learning approaches • Contrastive learning: learn to distinguish similar data points
relying on manual feature engineering often miss. We also (positives) from different ones (negatives). For example, by
acknowledge traditional rule-based or non-deep learning tools, but randomly cropping protein images, two crops from the same
they are not covered in detail as they fall outside our primary scope. protein are treated as similar, whereas crops from different
Deep learning models consist of two key components (see the proteins are seen as different197.
figure): learning paradigms that derive sequence–structure–function
relationships from data (part a) and architectures that incorporate L3. Reinforcement learning (RL): trains an AI agent to learn an
geometric and biological constraints to capture biophysical optimal long-term strategy by interacting with its environment: it
complexity of proteins (part b). observes states, takes actions and receives rewards that evaluate its
performance and guide its learning. Its internal structure may include
Learning paradigms: capturing key patterns from vast protein one or more of the following components:
databases is challenging. AI models achieved this through three • Policy: defines the agent’s behaviour by mapping states to actions,
learning paradigms: supervised, unsupervised and reinforcement determining which action to take in a given state based on a
learning. probability distribution.
L1. Supervised learning: trains models using labelled data, in which • Value function: estimates the expected return (cumulative reward)
input–output pairs guide the learning process (see the figure, part a, L1). from a given state, helping the agent evaluate the long-term
• Standard supervision: supervised learning is used in AI tools benefits of different actions.
by training on labelled data. For example, sequence–function • Model: represents the environment by predicting future states
predictors take a protein sequence as input and learn to predict and rewards based on the agent’s actions, enabling planning and
fitness using assay-labelled outputs52,140, whereas structure decision-making.
prediction models such as AlphaFold 2 (ref. 6) use sequences as
input and 3D structures from the Protein Data Bank (PDB) database In protein design, EvoPlay198 uses reinforcement learning by treating
as labelled outputs. protein sequences as states and single-site mutations as actions.
• Label-efficient supervision: enables learning with fewer labels, Although environmental assays (such as binding or bioluminescence)
as labelled data are scarce and costly. Transfer learning adapts ultimately provide reward signals, EvoPlay obtains them via a surrogate
a model trained on one data set to a new task with minimal model (for example, AlphaFold 2) that approximates these responses.
labelled data. Zero-shot learning generalizes without new Its RL agent includes a policy (a neural network assigning mutation
labelled examples, whereas few-shot learning does so with action probabilities), a value function (estimating long-term fitness)
only a few. Active learning improves efficiency by iteratively and a model (a sequence–function predictor forecasting mutation
selecting informative samples for annotation and then refining impacts). Through iterative simulations, the agent refines its policy
the model with it. to select mutations that maximize predicted rewards, efficiently
exploring the design space and enhancing variant properties. Similarly,
L2. Unsupervised learning: learns patterns from unlabelled data a top-down RL approach199 has been used to design folded multimer
for meaningful representations (see the figure, part a, L2). Key structures.
approaches are discussed subsequently in this Review, although the
list is not exhaustive. Model architecture: advancements in deep learning have enabled
• Language modelling: uses either next-token prediction195 or the learning of key pattern and feature extraction. However, not all
masked language modelling196. The former generates sequences aspects must be learned from data alone. Geometric priors, such as
step-by-step (that is, predicting the next residue5), whereas the fact that rotating or shifting a protein structure in 3D space does
the latter infers masked tokens from the surrounding context not alter its behaviour, are built-in rules reflecting the data’s structure.
(for example, ‘MP <MASK>MG’36). Similarly, biological priors, such as residue interactions and folding
• Diffusion models: learn by reversing a noise corruption process principles, guide models towards biophysically realistic solutions6,122.
to recover meaningful data. For instance, a model trained on Without these priors, models can overfit to superficial patterns and
unlabelled 3D structures from the PDB can learn by corrupting fail to generalize. To address this limitation, model architectures have
them into noise and then denoising them back to valid structures. been designed to tailor for specific data types and tasks. Modern
Using this method, AI models capture complex patterns that designs often integrate multiple layered architectures to develop
enable the generation of biophysically valid proteins, either from robust AI tools6,35. Subsequently, we outline the key architectures
pure noise (unconditionally) or by refining partially corrupted used in protein modelling.
inputs (conditionally)9,24. M1. Recurrent neural network: models sequential data one
• Variation autoencoders (VAEs): learn a probabilistic latent space token (discrete pieces of information such as a word or a residue)
by encoding data as a distribution. By enforcing a prior, typically at a time, and concurrently memory of previous tokens200 (see the
a normal distribution, VAEs enable structured representation, figure, part b, M1).
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1037

---

<!-- Page 5 -->

Review article
a Learning paradigms
L1. Supervised learning L2. Unsupervised learning L3. Reinforcement learning
Predict Patterns State
Action
AI model Data set with labels AI model Data set without labels AI agent Environment
Supervision Feedback Reward
Standard supervision Language modelling Policy
Sequence–function predictor Structure
prediction Ser Predicted AI fitness Predict Glu His
0.8
model
Error AI
Assay –0.1 Supervision
labels
Unconditional generation Conditional generation
Noise Generated Partial noise Generated Value function
coordinate data coordinate data
Predicted
Label efficient supervision reward 1 µm
Expected
Source Target
return
data set data set
Transfer learning
Knowledge Contrastive learning
Source transfer Target
Value of states For example
model model Attract Repel
Model
Zero shot learning
Environment representation
Surrogate Predicted
Few shot learning
Repel Attract model future state
Active learning
b Model architectures
Model design strategy
Inject
Biological and priors
AI model
geometric priors
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1038
gnidilS wodniw
Output T1 T2 T3 T4
T1 T2 T3 T4
Input Output
Input
3D space
Input Output Grid-like structure Input/output 3D structure
M3. Convolutional neural network
laitneuqeS gnissecorp
Sequential structure
Attention
weights
Graph structure
Input/output (nodes and edges)
noitamrofnI
gnituor
(continued from previous page)
A … Q Mutation as action
Trp Phe Autoregressive Masked State: S t Arg
E V Q L S … E V L S … Action: a 1 a 2 a 3 Ala Cys Tyr …
Likelihood: 0.7 0.2 0.1 0.1 0.2 0.3
Diffusion models Agent behaviour Probability
function of action
… …
…
$
S S S S
1 T 1 T
Variational autoencoder S … S …
0 0
Discrete code
or
normal
No new data required
Encoder Decoder
Limited data with good result
p (z)
e For example modelling protein
Data acquisition in a loop
Prior fitness post-mutation
Tyr Ser Gly Ser
Learning token-to-
Tyr Ser Gly UNK token relationship
M1. Recurrent neural network M2. Transformers
H H Cα
θ C O
H C H Cα
H H O
N C
R
M4. Graph neural network M5. Geometric 3D network
Box Fig. 1 | Artificial intelligence learning paradigms and model architectures for protein design. a, Three artificial intelligence (AI) learning
paradigms: (L1) supervised learning trains models using labelled data and includes two subcategories: standard supervision, which learns
directly from labelled examples (such as sequence–function predictors or structure prediction models), and label-efficient supervision,
which reduces reliance on large labelled data sets; (L2) unsupervised learning learns patterns from unlabelled data via language modelling

---

<!-- Page 6 -->

Review article
(continued from previous page)
(predicting next tokens or inferring masked ones), diffusion models (reversing noise corruption to recover meaningful data), variational
autoencoders (capturing a probabilistic latent space) and contrastive learning (distinguishing similar from dissimilar samples); (L3)
reinforcement learning optimizes an agent’s long-term decision-making by interacting with an environment, in which the agent observes states,
takes actions and receives rewards that guide learning. Key components include a policy (mapping states to actions), value function (estimating
expected rewards) and model (predicting future states and rewards). b, Summary of representative model architectures: (M1) recurrent neural
networks: treat input data as a sequence, processing it step-by-step to capture dependencies within sequences, such as amino-acid chains;
(M2) transformers: use attention mechanisms, which assign different importance (or ‘attention’) to each unit of the input sequence (or ‘token’),
enabling the model to learn long-range relationship of residues in protein sequences or structural segments in structures; (M3) convolutional
neural networks: capture local structural features by applying sliding windows, ideal for grid-like data such as voxel grid; (M4) graph neural
networks: represent proteins as graphs, with nodes as atoms or residues and edges as bonds or interactions; and (M5) geometric 3D networks:
capture the 3D spatial structure of proteins, enhancing accuracy in predicting folding and function when provided with 3D protein structures.
M2. Transformers: models all pairwise token interactions M4. Graph neural networks: modelling entities in the input as any
simultaneously using the self-attention mechanism rather than predefined graph structure202 (see the figure, part b, M4). For example,
sequentially194 (see the figure, part b, M2). This enables better capture proteins can be represented as 2D contact map graphs, in which amino
of long-range relationships. For instance, a residue token at the start acids are nodes and spatial relationships, such as proximity, are edges.
can interact with one at the end. M5. Geometric 3D networks: model 3D structures by integrating
M3. Convolutional neural networks: models grid-like data by rotational and translational invariances, ensuring that predictions
detecting local spatial patterns and can recognize these patterns remain consistent regardless of orientation203 (see the figure,
even when they shift (see the figure, part b, M3), as seen in computer part b, M5). This enables protein structure modelling with consistent,
vision applications201. orientation-independent predictions.
by experimental validation (Fig. 2a (III)). Rational design strategies Overview of AI toolkits
can be leveraged to achieve both the re-engineering of existing natural AI advances have introduced powerful tools, but their sheer number
proteins17, which involves knowledge-driven targeted modifications to and complexity make it difficult to discern interrelationships and opti-
native protein templates, and the creation of entirely novel (de novo) mal usage. To address this, we first define AI tools for protein design as
proteins30. In contrast to re-engineering, de novo design requires those supporting the search, understanding, generation, validation and
navigating vast sequence space from first principles, relying on the synthesis of candidate proteins. Following established protein design
understanding of protein biophysics to achieve a defined objective20. workflows (Fig. 2a), we then categorize these tools by (i) identifying key
Traditionally, site-directed mutagenesis, functional assays design tasks, (ii) reviewing supporting tools and (iii) grouping them
and structural methods such as X-ray crystallography guided these into seven functionally distinct toolkits (Fig. 2b) aligned with specific
efforts. For example, early structural studies of subtilisin identified tasks and workflow challenges, thereby including only tools highly
methionine-222 as oxidation-sensitive; replacing it with the more relevant to protein design.
resistant residue, cysteine, improved enzyme stability31. Over time, Before detailing how these toolkits fit into AI-driven workflows,
computational tools such as molecular docking and homology-based the following section provides an overview, with inputs and outputs
structure prediction1,32 have broadened the scope of rational design for each subcategory (Fig. 3). For detailed, toolkit-specific discussion,
(see post-2000s, Fig. 1). Despite being integral to this approach, see the section AI toolkits for protein design.
computational tools have broader applications and should not be
equated with rational design alone. Recent AI advances have fur- T1. Protein database search. This retrieves sequence and structural
ther expanded the depth and breadth of rational design, enabling templates via alignment to guide design. It includes two sub-toolkits:
metagenomic-scale exploration11,33–35 and more accurate modelling of sequence alignment (T1a)10,39,40 and structure alignment (T1b)11,41,42. T1a
sequence–structure–function relationships6,9,36. aligns queries to databases such as UniProt43 to find relevant homolo-
Choosing a strategy between directed evolution and rational gous sequences10,39,40,44. T1b searches structural databases such as the
design depends on expertise, available resources and which strat- Protein Data Bank (PDB)45 for structural templates.
egy best achieves the objective. Directed evolution is advantageous
when the functional goal is easily screened or predicted, but its T2. Protein structure prediction. This infers structures and dynamics
structural determinants remain uncertain26; for example, engineer- from protein sequences, a task traditionally requiring costly experi-
ing adeno-associated virus (AAV) capsids to cross the blood–brain ments. Breakthroughs such as AlphaFold 2 (ref. 6) now enable accurate,
barrier37, in which iterative experimental screening can optimize atomic-level predictions. Recent advances13,14,34,46 expanded this into
variants without full mechanistic insight. Conversely, when detailed four sub-toolkits: protein folding (T2a) predicts 3D structures of single
structural and mechanistic knowledge is available, rational design proteins6 or protein complexes7,47; biomolecular co-folding (T2b) models
is preferable. Classical examples include stabilizing subtilisin by protein complexes with other molecules such as nucleic acids and small
substituting methionine-222 with cysteine31 and the de novo protein molecules13,14; structure stability prediction (T2c) assesses whether a pro-
design of neoleukin-2/15, in which deep understanding enables precise, tein forms a stable structure; and conformational dynamics modelling
objective-driven design38. (T2d) models protein conformational states and dynamics12.
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1039

---

<!-- Page 7 -->

Review article
T3. Protein function prediction. This infers protein function from sequences optimized for those functions. T4c takes structural backbones
sequence or structure using three sub-toolkits: Gene Ontology (GO) as input and generates sequences predicted to fold into them.
annotation (T3a), binding site prediction (T3b) and post-translational
modification (PTM) prediction (T3c). T3a maps proteins to func- T5. Protein structure generation. These design structures aligned with
tions across biological processes, molecular functions and cellular functional objectives through three sub-toolkits: template-based struc-
components48. T3b identifies interaction residues as key regions for ture design (T5a), generative backbone design (T5b) and sequence–
binding and function to guide design49. T3c predicts PTM sites and structure co-design (T5c). T5a searches structural databases for motifs
evaluates their impact on protein function and stability. and scaffold templates as building blocks for assembling novel folds.
T5b directly generates backbone coordinates (excluding residue identi-
T4. Protein sequence generation. This enables targeted sequence ties and side chains) optimized for shape and function. T5c jointly gen-
design beyond random mutagenesis through three sub-toolkits: erates sequence and structure with all-atom optimization, including
evolution-guided generation (T4a), function-to-sequence generation side chains, to meet objectives.
(T4b) and structure-to-sequence generation (T4c). T4a takes protein
sequences as input and generates diversified, evolution-informed vari- T6. Virtual screening. Virtual screening evaluates alignment of design
ants. T4b takes functional annotations or ‘tags’ as input and generates candidates to objectives before experimental validation. It comprises
(I) Define strategy (II) Library design (III) Screening and optimization
a DNA
Directed evolution Activity Specificity
Screening > understanding
Outcome-driven approach
Design objective
Function, structure Parent Mutagenesis and DNA synthesis for Designed
and developability selection diversification protein expression protein
within the explorable
sequence space
Rational design Experimental validation
Understanding > screening • Wet lab screening Developability Stability
Knowledge-driven approach • Functional study
• Other aspects
Mechanistic Targeted
modelling design
b Advancing protein design with AI toolkits
AI-driven understanding AI-driven generation AI-driven optimization
T1 Protein database
search Protein
Virtual
T4 sequence T6
or generation screening
Function
Protein structure label Ub Ub
T2 prediction Ub
Protein DNA
T3 Protein function T5 s g t e r n u e c r tu at r i e o n T7 synthesis
prediction
Fig. 2 | Protein design strategies and workflows. a, Protein design projects for rational design, first elucidate the mechanisms driving protein function and
begin by defining objectives and evaluating them along three dimensions — subsequently make targeted modifications. (III) Screening and optimization:
function, structure and developability, which guide the formulation of a design designed library sequences undergo DNA synthesis and protein expression
strategy to navigate the vast, explorable sequence space in search of the optimal for experimental validation, completing one cycle of the design process, with
sequence. The design objective is then achieved through an iterative cycle of experimental results guiding subsequent rounds. Cycles are repeated until
three phases: (I) define strategy: choose between directed evolution or rational a designed protein meeting the objectives is achieved, often encompassing
design strategy to guide the search for optimal sequence. Directed evolution is multiple key properties such as activity, specificity, developability and stability.
an outcome-driven method that iteratively screens mutated protein variants to Projects may combine both strategies to address various aspects of protein
achieve the objective, whereas rational design is a knowledge-driven approach design. b, Advancing protein design with artificial intelligence (AI) toolkits:
that relies on an understanding of sequence–structure–function relationships AI tools support each design stage, from strategy definition through protein
to guide the design. (II) Library design: this phase designs a library of sequences database search (T1), structure prediction (T2) and function prediction (T3),
to maximize the chances of finding functional proteins. For directed evolution, to protein sequence (T4) and structure (T5) generation and, finally, virtual
first, select an existing protein with favourable characteristics (parent selection) screening (T6) and DNA synthesis (T7) for streamlined screening and validation.
and then use mutagenesis and diversification to search for improved variants;
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1040

---

<!-- Page 8 -->

Review article
T1. Protein database search Protein function
Mining protein database Function Functional Functional
Design template label generation sequences
Protein sequence ... T1a. Sequence Seq W F S T A V H
or structure alignment Seq X F S T A V H Input T4b. Function-to-sequence generation Output
Seq Y F A T A V Q
Align F S T A V H
or Protein structure Inverse folding M Protein
T1b. Structural Y sequences
alignment E
...
F
Input T1. Database search Output K
S
Input T4c. Structure-to-sequence generation Output
T2. Protein structure prediction
Protein Protein folding Protein
sequences from sequence structures T5. Protein structure generation
Template-
guided structure
Functional Search
Input T2a. Protein folding Output search tool miniprotein
database
Biomolecular sequences Biomolecular interaction Biomolecular
Protein Nucleotide Protein complex Input T5a. Template structure design Output
Ion Molecules Structure Generated backbone structure Backbone
objective structure
Input T2b. Biomolecular co-folding Output
Protein sequence Stability prediction Input T5b. Generative backbone design Output
or structure Flexibility
Flexible
score Sequence–structure co-design Designed
or All-atom protein
Residue position Stable Design structure
+
Input T2c. Structure stability prediction Output objective
Sequence
design
Protein sequence Multi-state
or structure protein structures Input T5c. Sequence–structure co-design Output
or
T6. Virtual screening
Input T2d. Conformational dynamic modelling Output Target Binders Binding and functional
protein activity estimation
Protein
DNA/RNA Binding
affinity or
T3. Protein function prediction Ion Molecules functional
activity
Protein sequence
or structure
Input T6a. Binding and functional activity Output
or Functional • Immunogenicity annotation
• Solubility
• Purity Metric
Input Output • Yield score
T3. Protein function prediction • Stability
Input T6b. Developability assessment Output
T4. Protein sequence generation
T7. DNA synthesis
Protein Mutated
Generation and mutation Protein Taxon Codon optimization DNA
sequences sequences
Seq W F S R A V H P L R sequences label sequences
Seq X F S T A V H P L H AGU CUA AGA
Seq Y F A T A V Q P L R + UCU UUG CGG
Seq Z F S T A I H P L R UCG CUG CGC
Input T4a. Evolution-guided generation Output Input T7. Protein–DNA translation Output
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1041
mynonyS
Protein function prediction
T3a. Gene Ontology (GO) annotation
T3b. Binding site identification Designed protein
T3c. Post-translational modification
Ser Leu Arg

---

<!-- Page 9 -->

Review article
Fig. 3 | Artificial intelligence toolkits for protein design. We categorize modification analysis (T3c); (T4) protein sequence generation creates sequences
artificial intelligence tools into seven toolkits with each specific sub-toolkits: based on evolutionary patterns (T4a), functional tags (T4b) or structural
(T1) protein database search uses sequence alignment (T1a) and structural templates (T4c); (T5) protein structure generation designs structures that
templates (T1b) to retrieve candidates; (T2) protein structure prediction predicts meet specific folding objectives; (T6) virtual screening includes binding and
folds from sequences (T2a and T2b), assesses structural stability (T2c) and functional activity prediction (T6a) as well as developability and immunogenicity
models conformational dynamics (T2d); (T3) protein function prediction covers assessments (T6b); and (T7) DNA synthesis performs back-translation and codon
Gene Ontology (T3a), binding site identification (T3b) and post-translational optimization for enhanced protein synthesis.
two sub-toolkits: binding and functional activity prediction (T6a) and Function-to-sequence generation (T4b)53 suggests mutations that
developability prediction (T6b). T6a predicts binding affinity or func- enhance or enable specific functions (Fig. 4b , functionally driven
(DE.3)
tional activity, whereas T6b assesses developability properties such as sequence mutation). Together, these approaches improve variant
stability and immunogenicity. library quality. Once complete, the library proceeds to screening and
optimization.
T7. DNA synthesis. DNA synthesis back-translates protein sequences
into optimized DNA, enabling efficient synthesis for experimental AI-driven rational library design. Rational design follows a three-step
validation50. workflow for AI-driven library design: first, designing a functional back-
bone structure that meets specific criteria (Fig. 4b , 1. Functional
(RD.1)
AI-driven protein design roadmap structure design); second, converting the structure into sequences
After organizing AI tools into toolkits, we present a roadmap that inte- predicted to fold into the intended conformation (Fig. 4b , 2. Protein
(RD.2)
grates them into a cohesive workflow for achieving protein design sequence design); and third, refining the designed proteins around key
objectives (Fig. 4). This roadmap provides a systematic guide for devel- regions to further enhance function (Fig. 4b , 3. Targeted design
(RD.3)
oping AI-driven design projects, whether based on directed evolution modification). The first two steps are required only when developing
or rational design strategies. a completely new scaffold or motif. For existing proteins, such as when
refining the active site of an enzyme, the process can begin at step 3.
AI-driven directed library evolution. Directed library evolution itera- The first step involves designing a backbone structure that
tively designs proteins in three steps: selecting a parent protein with meets specific functional criteria, using one of the three approaches:
baseline activity (Fig. 4b , 1. Parent selection), identifying regions crit- design-from-scaffold, design-from-motif or design-from-scratch. The
(DE.1)
ical to the target objectives (Fig. 4b , 2. Identify key region) and intro- design-from-scaffold approach (Fig. 4b , option 1) redesigns the
(DE.2) (RD.1)
ducing mutations to generate a diverse variant library (Fig. 4b , 3. functional motif site of a pre-existing scaffold, such as by adding a new
(DE.3)
Mutagenesis and diversification)2. complementarity determining region to an antibody without altering
In parent selection, a parent protein is chosen as a template to its framework scaffold. The design-from-motif strategy (Fig. 4b ,
(RD.1)
narrow the search space and facilitate evolution towards defined option 2) starts from a well-defined active motif, such as known
objectives. To establish a robust starting point (Fig. 4b , functional catalytic residues in enzymes, and builds a new scaffold around it to
(DE.1)
parent search), the protein database search toolkit (T1) identifies par- enhance specificity and stability. The design-from-scratch approach
ent candidates, whereas the GO annotation toolkit (T3a) highlights (Fig. 4b , option 3) designs the entire structure from scratch when
(RD.1)
under-annotated entries. As database searches might return many no suitable starting scaffold or motif is available to meet the objective54.
hits, virtual screening (T6) helps prioritize candidates. To evaluate a In all cases, the protein structure generation toolkit (T5) has a central
parent’s adaptability (Fig. 4b , evaluate parent adaptability), the role in building the structural backbone. Supporting toolkits enhances
(DE.1)
sequence alignment toolkit (T1a) and evolution-guided generation the process: T1 provides structural templates and T6 evaluates the
toolkit (T4a) assess its mutation tolerance and evolutionary patterns. generated structures. For protein binder designs, T1, T2 and T3 can
In the key region identification step51, specific regions are identi- help characterize the target protein.
fied for mutagenesis based on their potential to influence desired Once the functional backbone is defined, the next step is to design
properties. For example, focusing on just 10 positions in a 350-residue sequences that reliably fold into it, a process known as inverse folding.
protein shrinks the sequence space from 20350 to 2010. To identify func- The structure-to-sequence generation toolkit (T4c) assigns amino
tional sites (Fig. 4b , targeting functional sites), designers can use acids to the backbone, generating sequences predicted to adopt
(DE.2)
binding site identification (T3b) and structure folding (T2a and T2b) the intended structure (Fig. 4b , amino-acid assignment). These
(RD.2)
toolkits. To identify regions important to stability and developability sequences are then validated for structural consistency (Fig. 4b ,
(RD.2)
(Fig. 4b , targeting stability regions), structure stability predic- sequence folding validation). The structure prediction toolkit (T2) has
(DE.2)
tion (T2c) and conformational dynamics modelling (T2d) toolkits a central role in this step: its folding modules (T2a and T2b) confirm the
help pinpoint relevant sites. Protein database searches (T1) also aid intended conformation, and its stability prediction (T2c) along with
this step by identifying functional and stability-related regions from conformational dynamics modelling (T2d) assesses thermodynamic
homologous templates. stability and conformational flexibility. The database search toolkit
In the mutagenesis and diversification step, mutations are intro- (T1) can also be used to compare designs against known templates for
duced into the key regions to generate a variant library52. Tradition- additional verification.
ally performed via random mutagenesis, this process can now be In the third step, proteins are refined to meet specific design
guided by AI. Evolution-guided generation (T4a)21 proposes muta- objectives54–56. Structural analysis uses binding-site and PTM-site
tions broadly consistent with evolutionary pressures to reduce the predictors (T3b and T3c) to identify functional residues, with stabil-
risk of functional loss (Fig. 4b , fitness-driven sequence mutation). ity (T2c) and dynamics (T2d) modelling highlight residues essential
(DE.3)
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1042

---

<!-- Page 10 -->

Review article
a AI toolkits b Library design c Screening and
optimization
Directed evolution Go to
4
Maturity assessment Parent(s) Identify key Mutagenesis and
1 2 3 4 Designed library
Computational Experimental Production- selection region (optional) diversification
proof-of-concept validation ready deployment
Target
site
Nascent Advanced Mature
Functional parent Targeting Fitness-driven Virtual screening of
T1. Protein database T4. Protein sequence search functional sites sequence mutation designed protein library
search generation Identify good Sites that affect Evolutionarily Maximize library
starting point activity or specificity plausible sequences screening efficiency,
1a. Sequence 4a. Evolution-guided Toolkits: T1; T3a; T6 Toolkits: T1; T2a,b; T3b Toolkit: T4a improve success rate
alignment generation
Toolkit: T6
Evaluate parent Targeting stability Functionally driven
1b. Structure 4b. Function-to- adaptability regions sequence mutation
alignment sequence generation
Tolerance to Sites that affect Function-guided
mutation stability and mutagenesis Protein–DNA
4c. Structure-to- developability 5 translation
sequence generation
T2. Protein structure Toolkits: T1a; T4a Toolkits: T1; T2c,d Toolkit: T4b
prediction
T5. Protein structure
2a. Protein
generation
folding Rational design
5a. Template-based
2b. Biomolecular structure design Functional Protein sequence Targeted design DNA synthesis
co-folding 1 structure 2 design (inverse 3 modification
design folding) Optimizing taxon-specific
2c. Structure stability 5b. b G a e c n k e b r o a n ti e v e d esign M codon for DNA synthesis
prediction Y Toolkit: T7
E
2d. Conformational 5c. Sequence–structure . F ..
dynamics co-design S K
modelling
Option 1: design Amino acid Targeting key Experimental
6
T6. Virtual screening from scaffold assignment residues validation
T3. Protein function 6a. Binding and Toolkit: T5 (with Structure-to- Identifying residues DNA
T1–T3; T6) sequence mapping key to objective
prediction functional activity
prediction Option 2: design Toolkit: T4c Toolkits: T1; T2;
3a. Gene Ontology from motif T3b,c
(GO) annotation 6b. Developability
assessment Toolkit: T5 (with Sequence folding Refinement and
3b. Binding site T1; T6) validation diversification DNA insertion for
identification Option 3: design Check consistency Knowledge-guided protein expression
T7. DNA synthesis from scratch with designed modification • Lab screening
3c. Post-translational Toolkit: T5 (with structure Toolkits: T2d; T4c; • Functional study
modification • Other aspects
T1–T3; T6) Toolkits: T1; T2 T6
Library Design tasks Screening and
design steps with AI toolkits optimization steps
Fig. 4 | Artificial intelligence-driven protein design roadmap. a–c, Our three steps: first , selecting a ‘parent’ protein with baseline functionality and
(DE.1)
roadmap illustrates how artificial intelligence (AI) toolkits (a) integrate across adaptability; second , identifying key regions for mutagenesis; and third ,
(DE.2) (DE.3)
two phases: library design (b) and screening and optimization (c), serving as a introducing mutations to generate diversity for facilitating search of improved
guideline for developing an AI-driven protein design project from conception variants. By contrast, rational design designs library in three steps: first ,
(RD.1)
to validation. The roadmap should be applied only after objectives are firmly designing a functional structure to meet specific criteria; second , generating
(RD.2)
established and a design strategy is chosen. In each phase, numbered steps (1–6) sequences predicted to fold into that structure; and third , making targeted
(RD.3)
denote finer-scale task actions. b, Both directed evolution and rational design modifications to enhance properties towards design objectives. c, Screening
follow their own three-step library design sequences (steps 1–3, blue octagon and optimization: following library design, step 4 virtually filters the library
(SO.4)
icons). c, Steps 4–6 (red octagon icons) address screening and optimization. for efficiency; step 5 translates protein designs into DNA for expression in
(SO.5)
Within each step, specific design tasks (yellow star icons) specify the required host cells and step 6 experimentally validates the designs. If the designs pass
(SO.6)
action, and ‘Toolkit: T\#’ references indicate the supporting AI toolkits for each validation, the objective is achieved; otherwise, the process is repeated with
task. a, AI toolkits: tools are organized into seven primary toolkits (T1–T7) and AI prediction and/or experimental validation, providing feedback to guide the
subdivided into sub-toolkits serving various aspects of protein design, with next iteration of library design. Note that this roadmap is flexible; steps may be
maturity levels (nascent, advanced and mature) reflecting real-world validation bypassed or initiated midstream. For example, in rational design, if only minor
and deployment readiness. b, Directed evolution designs a candidate library in modifications are needed to optimize an existing protein, begin at step 3.
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1043

---

<!-- Page 11 -->

Review article
for stability and developability (Fig. 4b , targeting key residues). compelling strategy. Following our roadmap, the AI-driven workflow
(RD.3)
Database searches (T1) can further support this process by compar- begins with functional structure design, using the protein structure
ing designs with homologous structures. Identified key residues are generation toolkit (T5) to construct binder backbones (Fig. 4b ). The
(RD.1)
then optimized (Fig. 4b , refinement and diversification) using structure-to-sequence toolkit (T4c) then translates these backbones
(RD.3)
structure-based virtual screening (T6), with T2d-generated conform- into viable sequences, which are validated by the structure prediction
ers capturing protein dynamics to guide optimal side chain placement. toolkit (T2) for correct folding (Fig. 4b ). The design is subsequently
(RD.2)
The refined structures are passed to the structure-to-sequence toolkit refined using binding activity prediction (T6a) and conformational
(T4c), which generates a diverse, enriched library of sequence variants. dynamics modelling (T2d) toolkits (Fig. 4b ). Finally, the screening
(RD.3)
This library is then ready for screening and optimization. and validation process begins: the designed sequences are virtually
screened (T6) to prioritize candidates (Fig. 4c ), back-translated into
(SO.4)
AI-driven screening and optimization. After designing a sequence DNA (Fig. 4c ) using the DNA synthesis toolkit (T7) and synthesized
(SO.5)
library, the screening and optimization phase refines it through selec- for experimental validation (Fig. 4c ).
(SO.6)
tion, synthesis and experimental validation (Fig. 4c). The library first This roadmap also applies to de novo binder design for other
undergoes virtual screening (T6) to predict properties such as bind- ligand types, such as small molecules. It can also be used to design only
ing affinity, specificity, stability and solubility, selecting the most an active site motif to enhance function without compromising scaf-
promising variants (Fig. 4c , 4. Designed library). Selected proteins fold integrity, using the ‘design-from-scaffold’ approach (Fig. 4b ).
(SO.4) (RD.1)
are converted into optimized DNA sequences, with DNA synthesis Finally, when optimizing an existing functional protein, the process
tools (T7) enabling efficient expression in the target host organism can begin at the refinement step (Fig. 4b ).
(RD.3)
(Fig. 4c , 5. Protein–DNA translation). Finally, the synthesized DNA
(SO.5)
is inserted into host systems for experimental validation (Fig. 4c , 6. Designing proteins with specific structures. The objective here is to
(SO.6)
Experimental validation). rationally design a specific, defined structure. We present an example
With screening and optimization complete, one cycle of protein demonstrating how to use the roadmap to guide this process.
design concludes, but the process remains iterative, allowing for further Example — rational symmetry scaffold design from motif. Consider
refinement of selected variants through repeated cycles. The workflow a native protein with a functional metal-binding site whose original
is flexible and can begin at later stages if the protein is well characterized. scaffold positions the motif suboptimal, compromising structural pre-
Many projects also combine directed evolution and rational design to cision. To fix this, a symmetrical scaffold can be built around the motif
address distinct dimensions of the design objectives54,57. to achieve ideal geometry and enhance stability and robustness9,58. Fol-
lowing our roadmap, the protein structure generation toolkit (T5) first
Using roadmap for protein design objectives constructs a backbone scaffold matching the coordination geometry
The following section illustrates how our roadmap applies to diverse of the motif (Fig. 4b ). Next, the structure-to-sequence toolkit (T4c)
(RD.1)
design objectives across function, structure and developability translates the backbone into viable sequences, which the structure
dimensions, offering practical guidance for building AI-driven workflows. prediction toolkit (T2) validates for correct folding (Fig. 4b ). The
(RD.2)
virtual screening toolkit (T6a) then refines the design by optimizing
Designing proteins with specific functions. Our roadmap guides key residues to stabilize the scaffold and functional site (Fig. 4b ).
(RD.3)
functional design, from re-engineering native proteins to designing Finally, DNA synthesis toolkit (T7) enables efficient synthesis for
novel proteins. experimental validation.
Example — evolving enzyme to enhance antibiotic resistance. Con-
sider designing an enzyme to confer resistance by degrading β-lactam Designing proteins for improved developability. Translating pro-
antibiotics, which are widely used as bacterial selection markers. teins from the laboratory to real-world applications requires not only
Although the naturally occurring TEM-1 β-lactamase is a suitable candi- function and structural integrity but also developability traits such as
date for re-engineering, its complex interplay of mutations and epista- yield, solubility and thermal stability.
sis makes rational design challenging. This favours a directed evolution Example — evolving enzyme for enhanced thermostability. Con-
strategy52. Following our roadmap, the AI-driven workflow begins with sider an industrial lipase that loses activity above 60 °C owing to ther-
parent selection (Fig. 4b ); first, a naturally active variant is identi- mal instability. An AI-driven direct evolution workflow can enhance
(DE.1)
fied via database search (T1) and assessed with the evolution-guided its thermostability. First, we start with a lipase exhibiting the desired
generation toolkit (T4a) to ensure both function and evolvability. function but reduced high-temperature activity (Fig. 4b ). Second,
(DE.1)
Second, the binding site prediction toolkit (T3b) is used to pinpoint the stability prediction toolkit (T2c) pinpoints regions for stabilization
key catalytic residues (Fig. 4b ). Third, the function-to-sequence (Fig. 4b ). Third, an evolution-guided generation tool (T4a) intro-
(DE.2) (DE.2)
generation toolkit (T4b) introduces mutations to enhance catalytic duces mutations likely to preserve function (Fig. 4b ). Fourth, virtual
(DE.3)
efficiency, completing the library design (Fig. 4b ). Finally, the screening (T6; T6b for melting temperature and T6a for catalytic activ-
(DE.3)
library is virtually screened (T6) to prioritize high-potential candidates ity) evaluates the library in silico (Fig. 4b ). Finally, top candidates
(SO.4)
(Fig. 4c ), which are back-translated for expression (Fig. 4c ) using are synthesized and experimentally validated.
(SO.4) (SO.5)
DNA synthesis toolkit (T7) and experimentally validated (Fig. 4c ). Rational design can similarly improve developability by inte-
(SO.6)
Example — rational SARS-CoV-2 binder design from scratch. If the grating AI predictions with structural insights to guide targeted
objective is to design a protein that broadly inhibits SARS-CoV-2, modifications.
in this case, the inhibition mechanism is well defined: targeting the
receptor-binding domain of the spike protein, in which high-resolution AI toolkits for protein design
structures exist, to block ACE2 binding30. Because native proteins might We present seven AI toolkits and their sub-toolkits as separate sec-
fail to neutralize rapidly evolving variants, de novo binder design is a tions, covering their development, recent advances and limitations in
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1044

---

<!-- Page 12 -->

Review article
Table 1 | Overview of artificial intelligence toolkits and applications in protein design workflow
Toolkit Sub-toolkit category Applicable tasks Representative tools
T1. Protein database T1a. Sequence alignment Functional parent search Global-only alignment:
(DE.1)
search Evaluate parent adaptability DEDAL(seq)61, DeepBLAST(seq)10
(DE.1) (M2) (M2)
Targeting functional sites Global/local alignment:
(DE.2)
Targeting stability regions pLM − BLAST(seq)40, PLMSearch(seq)62, SMURF(seq)177
(DE.2) (M2) (M2) (M2)
Targeting key residues Search-and-Rank: SeekRank65
(RD.3)
T1b. Structure alignment Targeting functional sites DALI42, Foldseek11, Foldseek-Multimer63
(DE.2)
Targeting stability regions
(DE.2)
Design from scaffold, motif or
scratch
(RD.1)
Sequence folding validation
(RD.2)
Targeting key residues
(RD.3)
T p 2 re . d Pr ic o t t i e o i n n structure T2a. Protein folding S Ta e r q g u e e ti n n c g e f f u o n ld ct in io g n v a a l l s i i d te a s ti ( o DE n .2 ( ) RD.2) S C i o n m gl p e l - e c x h : a R in o : s A e l T p T h A a F F o o l l d d ( ( s M 2 e 2 ( ( q s M , ) e 5 2 q ) 7 , ) 5 , ) A 6, F E − SM M F u o lt l i d m ( ( M s e e 2 q r , ( ( ) 5 s M ) e 3 2 q 4 , ) 5) 47
Targeting key residues (RD.3) Database: AlphaFoldDB33, ESM Metagenomic Atlas34
T2b. Biomolecular co-folding Targeting functional sites (DE.2) Small molecule: NeuralPLexer ( ( M se 2 q , ) 5) 70, DynamicBind( ( s M e 4 q , ) 5) 178
Sequence folding validation (RD.2) Nucleic acid: RoseTTAFold − NA( ( s M e 2 q , ) 5) 46
Targeting key residues (RD.3) B B O io L m T o Z l − e 1 c (s u e l q a ) r 1 : 7 R 9, F C − h A ai l − lA 1 t (s o e m q) ( ( 2 s M 5 e 2 q , ) 5) 13, AlphaFold3 ( ( M se 2 q , ) 5) 14,
(M2,5) (M2,5)
T2c. Structure stability prediction Targeting stability regions Per-residue level:
(DE.2)
Sequence folding validation AF − pLDDT(seq)6, IUPred(seq)77, fIDPnn(seq)78
(RD.2)
Targeting key residues Whole-protein level:
(RD.3)
TemstaPro(seq)81, DDMut(str) 83, RaSP(str) 82
(M2) (M3) (M3)
Binding-interface level:
interface predicted TM (ipTM) and aligned error (iPAE)
of AF-Multimer47/AlphaFold 3 (ref. 14)
T2d. Conformational dynamics Targeting stability regions
(DE.2)
AFCluster(seq)12, AlphaFlow(seq)89, RifGen(str)55,
modelling Sequence folding validation ChemNet(str)58
(RD.2)
Refinement and diversification
(RD.3)
T p 3 re . d P i r c o t t i e o i n n function T3a. Gene Ontology (GO) annotation Functional parent search (DE.1) Gene Ontology (GO): NetGO3.0 ( ( M se 2 q ) )98, PhiGNet ( ( M se 4 q ) )95
Enzyme Commission (EC): CLEAN(seq)180
T3b. Binding site identification Targeting functional sites (DE.2) Protein sites: MaSIF ( ( M str 5 ) ) 49, ScanNet ( ( M str 5 ) ) 102
Targeting key residues (RD.3) Molecule sites: DeepSite ( ( M str 3 ) ) 103, DiffDock ( ( M str 5 ) ) 104
(Biomolecular co-folding tools can be applied here)
T3c. Post-translational modification Targeting functional sites (DE.2) DeepPhos ( ( M se 3 q ) )181, MusiteDeep ( ( M se 3 q ) )109
Targeting key residues
(RD.3)
T4. Protein sequence T4a. Evolution-guided generation Fitness-driven sequence UniRep(seq)5, ESM−1b(seq)36, ESM2(seq)34, ProGen2(seq)182
generation mutation (M1) (M2) (M2) (M2)
(DE.3)
Evaluate parent adaptability
(DE.1)
T4b. Function-to-sequence generation Functionally driven sequence ProGen 53, PoET 119, ESM3 35
(M2) (M2) (M2,5)
mutation
(DE.3)
T4c. Structure-to-sequence generation Amino-acid assignment (RD.2) ProteinMPNN( ( s M tr 4 ) ,5) 8, ESM − IF( ( s M tr 2 ) ,5) 123, LigandMPNN( ( s M tr 4 ) ,5) 124
Refinement and diversification
(RD.3)
T5. Protein structure T5a. Template-based structure design Design from scaffold, motif or DeepFragLib(seq)183, MaSIF − search(str) 30,184
generation scratch (M1) (M5)
(RD.1)
T5b. Generative structure design Design from scaffold, motif or RFDiffusion 9, Chroma 24, RFDiffusionAA 13
(M2,5) (M4,5) (M2,5)
scratch
(RD.1)
T5c. Sequence–structure co-design Design from scaffold, motif or Hallucination 54,72, RFDesign 73, BinderCraft 134,
(M3) (M2,5) (M2,5)
scratch ProteinGenerator 136, Protpardelle 137,
(RD.1) (M2,5) (M2,5)
RFDiffusion2 185
(M2,5)
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1045

---

<!-- Page 13 -->

Review article
Table 1 (continued) | Overview of artificial intelligence toolkits and applications in protein design workflow
Toolkit Sub-toolkit category Applicable tasks Representative tools
T6. Virtual screening T6a. Binding and functional activity Functional parent search (1) Off-the-shelf:
(DE.1)
prediction Design from scaffold, motif or - Protein binding: DOVE(str) 186, DeepRank(str) 187
(M3) (M4)
scratch (RD.1) - Antigen binding: IgLM ( ( M se 2 q ) )188, NetTCR ( ( M se 3 q ) )189
Refinement and diversification (RD.3) - Small-molecule binding: GNINA ( ( M str 3 ) ) 138, PSICHIC ( ( M se 4 q ) )22
Virtual screening of library (SO.4) - Nucleic acid binding: NucleicNet ( ( M str 3 ) ) 190
- Functional activity: ESM−1v(seq)115, ProMEP(str) 191
(M2) (M2,5)
(2) Few-shot customization: Low−N (seq)52, FSFP(seq)139
(M1) (M2)
(3) Lab-in-the-loop: EvolvePro(seq)28, ALDE(seq)29
T6b. Developability assessment Same as T6a Immunogenicity: NetMHCpan(seq)150, DeepImmuno(seq)153
(M3)
Developability: DeepSoluE(seq)146, AggreProt(seq)148
(M1) (M1)
T7. DNA synthesis Back translation Protein–DNA translation (SO.5) m Va B r A ia R ti T o ( ( n M se a 2 q ) l )1 6 S 1, y C nt o h d e o s n is T (s r e a q n )5 s 0 former ( ( M se 2 q ) )164,
The table organizes representative artificial intelligence tools (last column) into seven toolkits, followed by sub-toolkit categories and specific applicable tasks (Fig. 4). In the ‘Applicable tasks’
column, subscripts indicate the design phase: directed evolution (DE), rational design (RD) or screening and optimization (SO). In the ‘Representative tools’ column, superscripts denote whether
a method’s inputs are structure-based (str) or sequence-based (seq), and subscripts denote the model architectures (M1–M5) shown in the figure in Box 1; no entries indicate that the categorization
does not apply.
the context of AI learning paradigms and model architectures (Box 1). Foldseek uses a generative VQ-VAE64 model (Box 1) that encodes
Each toolkit concludes with a maturity assessment (Fig. 4a), classifying residue–residue interactions in 3D structures as simplified ‘coded
sub-toolkits as ‘nascent’ (computational proof-of-concept), ‘advanced’ alphabets’ of structural states. This encoding transforms structural
(experimental validation) or ‘mature’ (production-ready deployment) alignments into sequence alignments of these codes, accelerat-
(Table 1). ing alignments by four to five orders of magnitude over traditional
methods41. As a result, Foldseek enables structural template searches
Protein database search (T1) across the vast metagenomic landscape of in silico structures.
Sequence alignment (T1a). Identifying evolutionarily related homo- Maturity assessment. We classify T1a and T1b as mature owing to
logous sequences fundamentally relies on sequence alignment. When their long-standing use, extensive database support11,33 and wide valida-
related sequences are aligned in a multiple sequence alignment (MSA), tion in industrial54 and pharmaceutical26 design workflows. Advances
evolutionary couplings (statistical relationships between co-evolving in remote homology detection and metagenomic-scale structural
residues) can be inferred to predict conserved regions, mutational databases have further enhanced these capabilities10,40. However, as
effects and even structures44, thereby guiding protein design. alignment tools rely on similarity, large-scale searches can yield many
Traditional algorithms, such as Smith–Waterman59 and BLAST39,60, similar hits that require manual evaluation. SeekRank65 streamlines
use direct residue matching as a similarity score to align sequences. the discovery process by combining a database search (T1) for poten-
Consequently, they can miss conservative substitutions and distant tial candidates with a virtual screening model (T6) that predicts and
homologues. AI-driven tools leverage protein language models to ranks them by functional activity. This integrated ‘Search-and-Rank’
overcome these limitations and accelerate database searches. approach efficiently filters and prioritizes the most promising options.
Protein language models5,36 are trained to predict masked or next
residues in a sequence (Box 1). To perform this function accurately, Protein structure prediction (T2)
these models encode each residue as an ‘embedding’ that captures Protein folding (T2a). AlphaFold 2 (ref. 6) and RoseTTAFold7 have
structural, functional and evolutionary information5,36. Tools such as revolutionized protein structure prediction. These models combine
DEDAL61 and pLM-BLAST40 compare these embeddings across pro- transformer-based architectures with geometric 3D networks (Box 1)
teins, enabling detection of deeper evolutionary relationships than to achieve atomic-level accuracy from a sequence. To accomplish
residue-by-residue alignment. This leads to more accurate alignments this, these methods first retrieve an MSA for the input sequence by
and homology detection. DeepBLAST10 and PLMSearch62 extend this querying a database (T1a). The MSA is passed through a transformer
approach by training models to predict TM scores from embeddings, module to encode evolutionary signals6,66; these signals are then fed
allowing the identification of remote structural homologues from into a geometric 3D network to predict 3D structures67,68. However,
sequence alone with accuracy comparable to structure-based methods. dependence on MSAs limits speed34 because each run requires a data-
base search and can be less effective for orphan proteins23 that lack
Structure alignment (T1b). Comparing 3D protein structures through homologous sequences.
structural alignment allows designers to search databases such as the RGN2 (ref. 23) predicts structures from a single sequence, bypass-
PDB45 for design templates and uncover insights that go beyond what ing MSAs and outperforming AlphaFold 2’s accuracy on orphan
sequence alignment can reveal. Advances in protein folding models proteins. Its key innovation is a 260M-parameter protein language
(T2)6 have enabled accurate structure prediction at scale, resulting in model, AminoBERT, which encodes sequences into compressed
databases containing hundreds of millions of predicted structures33,34. embeddings capturing evolutionary signals. However, its 3D network
AI tools such as Foldseek11,63 efficiently search these databases based predicts only the backbone (Cα trace), with side chains added using
on structural similarity. Rosetta. Building on this, ESMFold34 introduced two improvements:
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1046

---

<!-- Page 14 -->

Review article
scaling its language model to 15 billion parameters and integrating the and others adopting multiple conformational states or even switching
3D geometric network adapted from AlphaFold 2 to predict all-atom folds to dynamically achieve functions85.
structures. ESMFold matches AlphaFold 2’s accuracy and enables rapid, Although AlphaFold 2 was designed for static structure prediction,
single-sequence predictions. its capacity to sample diverse conformations has also been explored.
For complexes, AlphaFold-Multimer47 predicts multiprotein struc- A key insight is that modifying MSAs, such as sequence depth or
tures from chain sequences, achieving accuracy on par with docking masking specific positions, can steer predictions towards alternative
methods69 that rely on experimental monomer structures. conformations12,86,87. AF-Cluster12 has experimentally shown that clus-
tering MSAs by sequence similarity can yield multiple high-confidence
Biomolecular co-folding (T2b). Beyond single-protein and protein conformational predictions.
complexes, modelling how structures adapt when interacting with However, AlphaFold’s predictions do not capture the Boltzmann
diverse biomolecules, including small molecules, RNA and DNA, distribution of energy landscapes (that is, how likely a system is to be
is essential for biomolecular complex prediction. Protein-only fold- found in a particular energy state at a given temperature)12,88. Instead,
ing models (T2a) such as AlphaFold 2 and RoseTTAFold2 attained high sampling-based approaches using AlphaFold 2 and AlphaFold 3 cor-
accuracy using residue-level inputs and a 20-amino-acid vocabulary. rectly predict only ~35% of fold-switching proteins and fail almost
However, extending architectures to biomolecular complexes demands entirely for proteins outside their training set88. Predictions often
representations that encompass nucleic acids and small-molecule reflect memorization rather than true energetic learning, indicating
chemistries. To address this, RoseTTAFold All-Atom13 and AlphaFold 3 a reliance on training-set bias over accurate energetic modelling88. To
(ref. 14) introduce token types for nucleotides and all atom types, cap- address this, AlphaFlow89 retrains AlphaFold 2 on molecular dynamics-
turing atomic-level and entity-level features. This method distinguishes derived structural ensembles, enhancing sampling beyond MSA-based
biomolecular building blocks and enforces biological constraints and approaches. However, it still focuses on sampling states rather than
stereochemistry for protein–nucleic-acid and protein–small-molecule modelling dynamics. AI2BMD90, which uses a 3D geometric network91
interactions. trained on quantum mechanical data, directly simulates all-atom pro-
These models predict holo-state conformations70 and elucidate tein molecular dynamics with lower computational cost and error than
atomic-level interactions, identifying binding sites and characterizing traditional force fields. Nonetheless, it remains limited to single-chain
interaction details. By modelling how biomolecular entities co-fold proteins.
into assemblies, these tools outperform protein-only methods and Maturity assessment. All T2 sub-toolkits, except for T2d, are
exemplify the emergence of foundational AI capable of transferring classified as mature, reflecting extensive research, the creation of
knowledge across interaction types. metagenomic structural databases and widespread industrial and phar-
maceutical use92,93. These toolkits and their predicted structures under-
Structure stability prediction (T2c). Structural stability or flexibility pin multiple steps in AI-driven workflows (Fig. 4). Yet, current models
in protein design is context-dependent: intrinsically disordered regions poorly capture energetic landscapes, tending to memorize rather
may require flexibility for signalling, whereas industrial or therapeutic than model conformational states and dynamics, and interpreting the
applications demand stability4. functional relevance of distinct conformations remains challenging94.
Structure prediction tools (T2a,b) provide confidence metrics Thus, we classify T2d as advanced rather than mature: although it pre-
that inform the reliability of predictions and have been found to cor- dicts valid conformations12, it has yet to robustly characterize protein
relate with structural stability7. AlphaFold 2 (ref. 6) assigns a predicted dynamics.
local distance difference test score (0–100) to each residue, offering
localized insights into structural confidence. Scores above 90 indi- Protein function prediction (T3)
cate high confidence and likely structural stability, whereas scores Gene Ontology (GO) annotation (T3a). GO provides a standardized
below 50 suggest low confidence, potentially indicating flexible or vocabulary for describing gene and protein functions across biological
disordered regions71. These insights have supported the design of processes, molecular functions and cellular components95. Despite its
stable proteins9,72,73. However, AlphaFold 2 can be slower and less broad coverage, millions of UniProt43 entries remain uncharacterized,
accurate than specialized predictors74,75. Faster alternatives, such as highlighting the need for accurate computational annotation.
MEDUSA76, IUPred77 and fIDPnn78, offer residue-level stability and Despite the traditional method BLAST-KNN48 being limited by
disorder prediction using just protein sequence. its reliance on sequence similarity, recent deep learning models have
Beyond local flexibility, global stability assessment is essential. considerably improved accuracy by capturing deeper functional
Averaging AlphaFold 2’s predicted local distance difference test relationships. For example, NetGO series96 integrates diverse data
scores across residues provides a reasonable stability estimate79, but sources and advanced AI architectures (Box 1). NetGO2.0 (ref. 97) used
does not capture mutation-induced shifts in stability80. To predict recurrent neural networks (RNNs) to model sequence context, and
mutation-induced changes, TemStaPro81 infers stability changes from its successor, NetGO3.0 (ref. 98), further enhanced performance by
the sequence using language models, whereas RaSP82 and DDMut83 esti- using transformer-based language-model embeddings. In a different
mate stability changes based on wild-type structures. For complexes, approach, PhiGNet95 uses graph neural networks representing residues
AlphaFold-Multimer47 and AlphaFold 3 (ref. 14) can report additional as nodes connected by co-evolutionary links to improve prediction
metrics: interface predicted TM(ipTM) and aligned error (iPAE) scores through graph-based modelling.
for assessing inter-subunit positioning, which has been proven useful
for estimating binding free energy changes in complex interactions84. Binding site identification (T3b). Identifying functional sites is essen-
tial for understanding protein function and guiding design, whether
Conformational dynamics modelling (T2d). Proteins are shaped not pinpointing binding sites of target proteins for binder development
only for stable folding but also for function, with some remaining rigid or locating regions within designed proteins for modification.
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1047

---

<!-- Page 15 -->

Review article
Early geometry-based tools such as Fpocket99, SPPIDER100 and PSIVER101 design avGFP and TEM-1 β-lactamase by generating evolutionarily
scanned predefined features but often missed the nuanced patterns plausible sequences that avoid non-functional regions of the fitness
that modern deep learning-based AI can capture49. Three-dimensional landscape. Similarly, unconditioned ESM models36,115 have been used
geometric networks such as MaSIF49 and ScanNet102 learn interaction to generate residue substitutions with higher predicted probabilities
fingerprints directly from structural data to identify protein–protein than the wild type, yielding improved fitness across diverse protein
interaction sites, whereas DeepSite103 uses voxelized 3D convolu- families21. By operating within evolutionarily plausible regions with-
tional neural networks (CNNs) to predict small-molecule pockets out enforcing explicit functional objectives, these tools minimize
from protein structures. functional loss and produce fitter variants52,116.
More recently, blind-docking methods such as AlphaFold-
Multimer47 predict protein–protein interfaces directly from sequence, Function-to-sequence generation (T4b). Bypassing structural inter-
and DiffDock104 identifies small-molecule binding sites using pre- mediates, function-to-sequence generation tools generate sequences
dicted structures. Biomolecular co-folding tools such as RoseTTA- directly from desired functions117,118. Functionally driven, language
Fold-AllAtom13 and AlphaFold 3 (ref. 14) extend binding-site discovery model-based tools, such as ProGen53, ESM3 (ref. 35) and PoET119, demon-
from sequence to diverse assemblies, including protein–protein, strate this capability. ProGen53 leverages functional tags (Pfam identifi-
protein–small-molecule and protein–nucleic-acid complexes. ers and more than 1,100 UniProtKB annotations) to generate sequences
tailored to specific protein families, whereas ESM3 (ref. 35) applies
Post-translational modification (T3c). PTMs act as molecular switches InterPro annotations and GO terms to produce candidates with desired
modulating protein activity, stability and interactions, enabling functions. In parallel, PoET119 infers sequence patterns within a protein
applications such as half-life extension105 and enhanced therapeutic family to propose functional variants.
efficacy106. With more than 400 documented PTMs107, AI can be essen- Alternatively, evolution-guided protein language models (see T4a)
tial for predicting modification sites and elucidating their structural can be converted into functional sequence generators by fine-tuning
and functional consequences. on functionally characterized sequences5 or feedback from virtual
Early efforts such as MuSiteDeep108 applied CNNs to scan protein screening tools (T6)120,121. This adapted approach has successfully
sequences for PTM sites109, but limited receptive fields of CNNs often engineered fluorescent proteins5 and enzymes52.
miss long-range interactions. Transformer-based PTMGPT2 (ref. 110)
overcomes this by using attention mechanisms and prompt-based Structure-to-sequence generation (T4c). Although AI tools can
training to capture distant dependencies. Building on this, MIND-S111 generate idealized protein structures (see T5), designing amino-acid
integrates sequence data with AlphaFold 2-predicted structures for sequences that reliably fold into a given backbone, known as inverse
structure-aware site prediction, whereas PTMdyna112 simulates PTM folding, remains a major challenge. T4c addresses this by generating
effects in silico by modelling modified and unmodified structural states sequences for a specified 3D backbone (N–Cα–C units excluding side
from molecular dynamics. chains), linking structural design to functional sequence realization.
Maturity assessment. T3a and T3b are classified as advanced based Structured transformer, one of the first AI tools, represented
on extensive research and experimental validation, such as CAFA GO backbones as graphs122, with atoms as nodes and interatomic dis-
prediction competition113 and MaSIF-site, identifying SARS-CoV-2 tances as edges; it outperformed Rosetta in sequence recovery and
receptor-binding domain sites30. Both are integral to AI-driven pro- ran 20 times faster. Building on this, ProteinMPNN8 improved both the
tein design workflows (Fig. 4): T3a enhances understanding of under- model architecture and learning strategy. Architecturally, it enriches
annotated or novel proteins, whereas T3b identifies key regions for atomic features and allows information to be updated not only at each
further modification and optimization. By contrast, T3c remains nas- atom (node) but also along the connections between atoms (edges),
cent, with limited experimental validation and minimal integration improving sequence recovery from 41.2% to more than 50.0%. On the
into existing AI-driven workflows. learning side, ProteinMPNN trains on diverse cases, including injecting
noise into backbone coordinates to capture conformational variability
Protein sequence generation (T4) and handle lower-quality inputs, and predicting residues in any order,
Evolution-guided generation (T4a). Natural evolution navigates enabling users to prespecify residues at desired structural positions.
vast sequence space through random mutation and recombination, To expand training data beyond experimentally resolved PDB pro-
selecting mutations that enhance fitness under specific pressures tein structures, ESM-IF123 leveraged 12 million AlphaFold 2-predicted
and preserving universally important properties such as stability and structures to expand its training set and improve performance. In paral-
evolvability4,114. Evolution-guided generation emulates this process lel, LigandMPNN124 extends ProteinMPNN to include non-protein atoms
by identifying mutations consistent with these universally conserved (small molecules, DNA, RNA and metal ions), enabling the design of
properties, a principle termed ‘evolutionary plausibility’21. This ligand-binding proteins.
approach uses protein language models trained to generate residues Despite being trained on native proteins, T4c can also generate
by assigning probability distributions over 20 amino acids at each sequences for de novo backbones. By capturing general structural
position. Without explicit design objectives, these models can pro- features, they generate amino-acid chains that fold reliably into any
pose mutations that are universally important and likely to preserve backbone, natural or novel, extending their utility in de novo pro-
or enhance function. tein design. Moreover, these models assign likelihood scores to
UniRep5, a next-token prediction language model (Box 1), can structure–sequence pairs, offering a quantitative metric for design
generate new sequences or evaluate existing ones by assessing the like- optimization56.
lihood of each residue being correctly placed at its position. Sequences Maturity assessment. We classify T4a as advanced based on
with higher probabilities better match evolutionary patterns, making experimental evidence showing improved fitness in enzymes5,52 and
them fitter candidates. In a follow-up study52, UniRep was used to antibodies21. T4b is nascent as its methods are primarily validated
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1048

---

<!-- Page 16 -->

Review article
in silico119 with limited experimental success53. Both T4a and T4b are Sequence–structure co-design (T5c). Protein side chains dictate
essential for mutagenesis and diversification in directed evolution. T4c functional properties by shaping interactions and intrinsic structural
has a central role in AI-driven rational design and supports industrial features. Generative backbone design (T5b) first produces backbone
tools125 such as ProteinMPNN8. It is used not only to generate sequences conformations and then applies structure-to-sequence generation
for idealized backbone structures with missing residues (Fig. 4b , 2. (T4c), overlooking side chain influence during generation. By con-
(RD.2)
Protein sequence design) but also to refine and diversify sequences trast, sequence–structure co-design jointly models backbone and side
of structures with known residues (Fig. 4b , 3. Targeted design chains, capturing their interdependencies.
(RD.3)
modification)54,126. Accurate structure prediction models (T2) such as trRosetta132,
RoseTTAFold7 and AlphaFold 2 (ref. 6) have enabled co-design through
Protein structure generation (T5) iterative sequence optimization. Beginning from random or partially
Template-guided structure design (T5a). Structural databases com- defined sequences, these models fold each candidate into a 3D struc-
pile decades of experimental structures, providing a rich source of ture, which is then evaluated to guide sequence mutations133. Evalu-
functional motifs and scaffold templates. Using the virtual screening ation occurs in structural space, where each predicted structure is
toolkit (T6), designers screen these databases to meet specific objec- assessed against defined objectives, including structural stability
tives. Selected motifs confer function or binding, whereas scaffold (measured by confidence scores from T2c), functional relevance
templates enhance stability or specificity; together, they are assem- (evaluated using virtual screening T6 tools) and structural similarity
bled into novel folds55. Physics-based docking has been used to iden- (determined via structural alignment T1b to known templates). This
tify templates for structural design32,127. However, these methods are fold–evaluate–mutate cycle repeats until the sequence converges on
computationally intensive and typically evaluate only thousands of a functional structure. RFDesign73 and BindCraft134 have applied this
candidates32, limiting exploration as databases expand. approach to generate scaffolds for existing active-site motifs73, cyclic
MaSIF49 accelerates template identification for protein binder assemblies135, binders134 and de novo structures54.
design with the 3D geometric network. It segments structural surfaces Diffusion-based frameworks extend co-design into a unified prob-
into overlapping patches and encodes each as a fingerprint vector abilistic process. ProteinGenerator136 denoises amino-acid identities
capturing structural and chemical features. MaSIF then builds a precom- and backbone geometry simultaneously in categorical sequence space
puted database of these vectors from PDB structures to enable rapid to support multistate designs. Protpardelle137 models full-atom struc-
screening via efficient vector comparisons. To design a binder, the target tures by maintaining a superposition of all possible side chain rotamers
site is similarly encoded and screened against this database to identify at each residue position. An ordinary differential equation scheme then
template patches likely to form complementary interactions. Because continuously evolves the backbone, with side chain superpositions
vector comparisons are computationally efficient, MaSIF searches collapse selectively based on rapid sequence predictions. This unified
20–200 times faster than conventional docking. This method has ena- approach removes the need for separate folding and mutation steps,
bled de novo binder design against targets such as the SARS-CoV-2 spike, yielding coherent sequence–structure trajectories.
PD-1, PD-L1 and CTLA-4 (ref. 30). MaSIF can scale to large repositories Maturity assessment. Sub-toolkits in T5 are classified as advanced
such as AlphaFoldDB33 or adapt to small-molecule binder design using based on experimental success. T5a has designed binders for targets
tools such as DrugCLIP128 to efficiently search for active site motifs. such as the SARS-CoV-2 spike and PD-1 (ref. 30). T5b generates binders
from scratch, validated by cryogenic electron microscopy9. T5c has
Generative backbone design (T5b). Advances in AI enable the genera- produced novel proteins such as luciferase54 and symmetric cyclic
tion of protein backbones aligned with design objectives. A key tech- assemblies135.
nique is diffusion models129 (Box 1), which starts from noisy, random When using the T5 toolkit, designers should define objectives
3D coordinates and iteratively refines them into coherent backbone and constraints as part of the input parameters of the tool to steer the
structures130. At each iterative step, small adjustments refine atom design towards functionally relevant proteins. Furthermore, although
positions; by learning how fold probabilities change with each adjust- T5a and T5c output sequences along with the designed structures, they
ment, these models can generate realistic backbones from noise131. can overlook secondary factors such as solubility. Adding an inverse
T5b focuses on first producing the 3D backbone and then sequence folding step (Fig. 4b ) with T4c can help refine sequences for sta-
(RD.2)
decoding via the structure-to-sequence toolkit (T4c). ble folding56 and diversify sequences for improved developability8.
RFDiffusion9 leverages diffusion learning to generate backbones For example, ProteinMPNN8 and its extension MPNNsol126 improve
unconditionally or conditionally by ‘denoising’ atoms initialized at ran- solubility more effectively than sequences generated from T5c134.
dom coordinates into functional structures. Trained on tasks ranging
from denoising entirely random coordinates to refining partial struc- Virtual screening (T6)
tures or generating binder backbones for a given target, RFDiffusion Binding and functional activity prediction (T6a). Assessing a candi-
can redesign motifs and scaffold backbones or generate entire proteins date’s binding interactions with target entities or its functional activ-
de novo. However, redirecting its output for constraints beyond protein ity can be accomplished via three approaches: (i) off-the-shelf tools,
sequence or structure requires retraining the model. (ii) few-shot customization and (iii) lab-in-the-loop methods.
Chroma24 addresses this limitation by embedding a programma- (i) ‘Off-the-shelf’ tools evaluate binding or activity on the fly,
ble ‘diffusion conditioner’ that can steer backbone generation using without customization. For binding interactions, AI tools can predict
user-defined constraints such as geometric features or functional cues protein–protein, protein–small-molecule and protein–nucleotide
from virtual screening models. By contrast, RFdiffusionAA13 integrates interactions (Table 1), accepting pairs of entities and outputting a
biomolecular interactions directly into the diffusion process, simulta- binding score and, in some tools, a predicted complex structure. Meth-
neously modelling protein–small-molecule or protein–nucleic-acid ods are either structure-based or sequence-based. Structure-based
interactions to design ligand binders. methods require structures to make predictions, such as GNINA138
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1049

---

<!-- Page 17 -->

Review article
for protein–small-molecule binding and MaSIF49 for protein–protein storage and industrial enzymes must remain active in harsh environ-
interactions. By contrast, sequence-based methods rely solely on ments. For instance, neural networks can predict melting (T ) and
m
sequence inputs (protein, nucleotide and SMILES sequences), making aggregation (T ) temperatures across pH and salt gradients144,145. Tools
agg
them suitable when high-quality, reliable structures are unavailable such as DeepSoluE146 and PLM_Sol147 predict solubility from sequence,
or when rapid, large-scale screening is required. Notably, PSICHIC22 enabling the selection of candidates less prone to expression failures,
uses only sequence data to match and even surpass structure-based whereas AggreProt148 identifies aggregation-prone regions to guide
methods in predicting protein–small-molecule binding affinity, and design149.
it does so faster. ‘Immunogenecity’ prediction tools evaluate a candidate’s poten-
AI tools also infer functional activity from the sequence. Language tial to elicit immune responses; NetMHCpan150, a neural network web
models described in T4a and T4b can not only generate novel can- server, predicts peptide-MHC binding to identify T cell epitopes, indi-
didates but also assess the functional activity. ESM-1v115 predicts cating peptide fragments at risk of eliciting unwanted responses151,152.
mutational effects in a zero-shot manner (Box 1) by estimating the DeepImmuno153 uses CNN to predict peptide immunogenicity to
probability of each amino acid being ‘correctly placed’ at every posi- prioritize low-risk variants, whereas Hu-mAb154 uses RNN to suggest
tion. Comparing mutant and wild-type probabilities reveals likely sequence changes to ‘humanize’ antibodies. By identifying immuno-
functional shifts: lower probabilities often signal impaired function, genic regions and suggesting targeted modifications, these tools guide
whereas higher probabilities suggest enhanced activity. design towards safer therapeutics.
Although convenient, off-the-shelf tools might not work well for Maturity assessment. T6a is classified as mature based on its dem-
novel proteins or functions, in these situations, a customized tool may onstrated use in pharmaceutical and industrial settings26,141,155,156. As a
be necessary. key component of AI-driven workflows (Fig. 4), T6a provides in silico
(ii) ‘Few-shot customization’ tools are predictive models that only screening for candidates before experimental validation, refines data-
require minimal experimental data to predict desired functions with base searches (T1) and guides sequence (T4) and structure (T5) gen-
high accuracy (see ‘Few-shot learning’ in Box 1). These tools hinge on eration. Distinguishing between structure-based and sequence-based
first obtaining transferable knowledge from large-scale models and tools is essential (Table 1), as each operates within a distinct design
databases; armed with this background, they can learn efficiently by space: structure-based approaches are well suited for structural mod-
fine-tuning on a handful of labelled sequence–function examples. elling and active-site optimization, whereas sequence-based methods
FSFP139 builds transferable knowledge by initializing from a pro- are more effective for identifying functional parents, guiding sequence
tein language model pretrained on millions of sequences and refin- generation and rapidly screening large libraries. By contrast, T6b
ing its priors using public deep-mutational-scanning data to capture remains nascent with mostly in silico testing146,147 and limited experi-
evolutionary constraints. Once the knowledge base is established, mental validation. Furthermore, available T6b tools remain scarce.
fine-tuning on a small in-house data set of sequences labelled with To address this, few-shot customization and lab-in-the-loop strategies,
target functions aligns FSFP to those functions and enables accurate adapted from T6a but focused on developability, offer promising
ranking of designed variants. solutions.
Simpler algorithms such as ridge regression140 or random forest
can also be customized effectively when equipped with transferable DNA synthesis (T7)
evolutionary features derived from MSAs, density models or language- Once a protein library is designed and virtually screened, it is experi-
model embeddings. For example, SeekRank65 combines language- mentally tested in host organisms such as Escherichia coli or yeast.
model embeddings with a random forest to predict functions from a Despite genetic code degeneracy (each residue type can be encoded
few labelled examples. by multiple codons), synonymous mutations can cause codon usage
(iii) ‘Lab-in-the-loop’ tools operate through an iterative cycle in bias, a phenomenon influencing gene expression and fitness. This bias
which AI predictions and laboratory experiments inform each other141. varies across species and gene length157–159. Unoptimized codons can
First, experimentally derived sequence–function pairs train an initial reduce expression, introduce translation errors and hinder experi-
model. That model then screens a combinatorial library to predict mental validation. The DNA synthesis toolkit (T7) addresses this by
high-performing variants. The top candidates are experimentally back-translating protein sequences into optimized DNA for efficient
tested, and the new data retrain the model. This feedback loop steadily synthesis.
improves predictive accuracy and reduces the number of experiments Because codon usage bias arises from selective pressure rather
required142. For example, EVOLVEpro28 combines language-model than randomness, AI models trained on naturally occurring protein–
embeddings with a random forest that trains on a small set of experi- DNA pairs can capture coding preference and avoid deleterious
mentally validated variants and then uses active learning (Box 1) to cis-elements. BiLSTM-CRF160 used an RNN trained on E. coli data to
select the most informative candidates for experimental screen- translate protein sequences into DNA. Transformer-based language
ing. Each new batch of experiment data refines model predictions, models (Box 1) such as mBART161, Co-BERTa162 and CodonBERT163
accelerating directed evolution and minimizing experimental rounds. extended this strategy to eukaryotic, bacterial and human hosts. How-
ever, these methods did not leverage large multispecies data sets to
Developability assessment (T6b). Evaluating a protein’s develop- capture codon usage patterns across organisms. CodonTransformers164
ability properties, including stability, solubility143 and, for therapeutic closes this gap by training on nearly one million gene–protein pairs
application, immunogenicity, is important for real-world applications. from 164 organisms, capturing universal and host-specific codon
‘Developability’ prediction tools evaluate a candidate’s stability preferences. Overall, these tools translate proteins into host-optimized
and solubility, which are essential for therapeutic and industrial appli- DNA, predict expression levels and rank high-yield variants.
cations because proteins must resist thermal, chemical and mechani- Variational synthesis165 takes a distinct approach to streamlining
cal stresses. For example, antibodies must resist aggregation during costs by directly optimizing laboratory parameters for DNA synthesis.
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1050

---

<!-- Page 18 -->

Review article
Define objective
Library design Screening and optimization
and strategy
~1010 AAV2 Capsid viability ensemble models
a AAV2 wild- Site-specific sequences
type parent random AAV2 library
Random Residue ~1010
mutation ... position variants 0.7
561–588 ...
Capsid viability
probability
Sequence Threefold axis
AI-driven directed (without structure) region mutation Prediction models
evolution of AAV
capsids Random virtual library Capsid viability prediction
b Functional Variable heavy/light DNA synthesis for expression Experimental
antibody chain mutants binding assay
parent
ESM protein Seq W F S R A V H P L R ~101
language model Seq X F S T A V H P L H variants
Seq Y F A T A V Q P L R
Seq Z F S T A I H P L R
AI-driven directed Sequence Evolutionarily
evolution of (without structure) plausible mutation
antibodies
Evolutionary-guided generation Experimental validation
c Experimental Structure-guided DNA synthesis for expression Experimental
complex structure sequence generation binding assay
ESM-IF
Antibody inverse ~101
folding Beneficial variants
mutation
given
structure
AI-driven rational
Antigen
antibody optimization
Structure-to-sequence generation Experimental validation
Generated RifDock
structures binding prediction
d Wild NTF2 Generated NTF2-like
sequences trRosetta novel structures structures A si c te tive
structure Structural 1,615
... prediction ... alignment scaffold
Luciferin
(DTZ)
AI-driven rational Topology-guided mutation
de novo luciferase (fix core, vary loops)
design
Sequence–structure co-design Protein–ligand docking
The model learns experimental settings, such as codon probabilities workflows (Fig. 4b , Refinement and diversification). Likewise,
(RD.3)
and assembly rules, to reproduce the target protein sequences and CaLM167 and Evo168 operate at the nucleotide level, leveraging the
then generates detailed lab protocols. It supports petascale synthesis 64-codon vocabulary to generate DNA sequences that encode proteins
(up to 1017 proteins), substantially reducing costs50. tailored to specific biological systems.
Maturity assessment. We consider T7 as advanced50 because,
despite successes, synthesis remains a bottleneck: many candidate AI-driven protein design case studies
designs persist only in theory without laboratory validation. AI can help AI reshapes protein design by rapidly exploring sequence space and
close this gap. CodonMPNN166 optimizes host-specific DNA directly elucidating complex molecular interactions. The following case studies
from backbone structures instead of adapting codons from designed illustrate how integrated AI tools form a cohesive workflow to accelerate
sequences, facilitating early sequence refinement in rational design design cycles.
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1051

---

<!-- Page 19 -->

Review article
Fig. 5 | Artificial intelligence-driven protein design case studies. a, AI-driven c, AI-driven rational antibody optimization: ESM-IF123 inverse folding is used to
directed evolution of adeno-associated virus (AAV) capsid26: random mutations identify beneficial mutations for sequence generation when given experimentally
at targeted positions of the AAV2 wild-type (WT) parent are used to generate determined antibody–antigen complexes, followed by experimental screening of
a virtual library with 1010 AAV2 sequences. These sequences are efficiently synthesized variants. d, AI-driven rational de novo luciferase design: the trRosetta
screened using ensemble AI models to predict capsid viability. The process tool is used to generate novel NTF2 scaffolds guided by NTF2-like structures
filters the library down to 201,426 sequences, of which 110,689 (58.1%) are that are searched from structural databases and predicted using Rosetta to
experimentally validated as viable, including designs with up to 29 mutations perform topology-guided mutation. The scaffolds were further refined using
from the WT. b, AI-driven directed evolution of antibodies21: ESM36,115 protein RifDock55, a protein–ligand docking model, and RosettaDesign to optimize pocket
language model is used to generate heavy and light chain mutants by predicting structures, whereas ProteinMPNN8 was used to optimize and virtually screen
the most probable mutations that could improve general fitness, without relying thousands of novel protein sequences. Experimental screening identified several
on structure or specific functional guidance. In each round, the top 20 or fewer active variants, with LuxSit showing exceptional promise owing to its remarkable
ESM-generated antibody variants are experimentally screened. After two rounds thermostability (melting temperature >95 °C) and high specificity in catalysing
of this process, the binding affinities of four highly mature antibodies improved the chemiluminescent reaction of DTZ with the synthetic substrate.
by up to sevenfold, and three immature antibodies improved by up to 160-fold.
AI-driven directed evolution bypassed the first two rational design steps and focused directly on
AAV capsids. AAV capsids are multiprotein assemblies essential targeted modifications (Fig. 4b , 3. Refinement and diversifica-
(RD.3)
for gene delivery. Traditional AAV capsid engineering struggles to tion). Informed by 3D backbone data from experimentally determined
evade pre-existing neutralizing antibodies because structure-based antibody–antigen complexes, ESM-IF1 generated mutant sequences
designs without sufficient mechanistic insights offer limited sequence that predicted to improve complex stability (Fig. 5c). Experimental
diversity26. AI-driven directed evolution has been applied to design validation of the top 30 mutants revealed up to a 37-fold increase in
AAV capsids, navigating a vast sequence space without compromising binding affinity against escape variants BQ.1.1 and XBB.1.5, demonstrat-
functional integrity26 (Fig. 5a). ing the advantage of integrating AI with structural insights to optimize
The case study follows the steps outlined in our roadmap (Fig. 4). antibodies for evolving viral epitopes.
First, wild-type AAV2 served as the parent for its proven efficacy in
the first FDA-approved gene therapy169 and other serotypes in clinical De novo luciferase design. Luciferase is a light-producing protein
trials170. Second, a 28-residue stretch at the AAV2’s three-fold symmetry used in bioassays and imaging when bound to luciferins. Traditional
axis (positions 561–588) was targeted owing to its role in genome pack- rational design struggles to generate luciferases for synthetic luciferins
aging and host–cell interactions. Third, a virtual library of 1010 AAV2 such as diphenylterazine (DTZ) because native proteins rarely bind
variants was generated by random, in silico mutagenesis at these DTZ and modifications are unpredictable. To overcome this limitation,
positions. Fourth, custom CNN and RNN models (T6a) screened the AI-driven de novo rational design was applied to create DTZ-optimized
library for capsid functionality and packaging efficiency, narrowing luciferases54 (Fig. 5d).
it to 201,426 candidates. Remarkably, 110,689 (58.1%) of these were Following our roadmap (Fig. 4), the team began with ‘family-wide
experimentally confirmed as viable, some with up to 29 mutations, hallucination’ using trRosetta132 (T5c) for sequence–structure
all without structural guidance. co-design (Fig. 4b , 1. Functional structure design). The method gen-
(RD.1)
Future improvements to this workflow could involve using an erated structures with alignment guidance from both PDB-resolved
evolution-guided generation toolkit (T4a), replacing random mutagen- (T1) and Rosetta-predicted (T2a) NTF2 structures, which were cho-
esis, to generate fitter variants with a higher likelihood of retaining sen for strong DTZ binding. The generation process preserved the
function, and using a DNA synthesis toolkit (T7) to reduce experimental core fold but let loop regions to vary freely, yielding 1,615 novel scaf-
validation costs. folds with geometry and chemistry superior to natural DTZ-binding
proteins54.
Antibodies. Evolution-guided generation toolkit (T4a) has been used Because sequences were co-designed with their structures
to accelerate directed evolution of clinically validated antibodies such (Fig. 4b , 2. Protein sequence design), the resulting designs were
(RD.2)
as MEDI8852 for influenza A and FDA-approved mAb114 for ebolavirus21 ready for optimization (Fig. 4b , 3. Targeted design modification).
(RD.3)
(Fig. 5b). Because the parent sequences and key binding regions were The team ran RifGen (T2d) to sample millions of side chain placements
already known, parent selection and region identification were unnec- around the binding site, then used RifDock (T6a)55 to dock each place-
essary; mutagenesis instead targeted the variable heavy and light ment and score its ligand interactions, keeping only the top candi-
chains (Fig. 4b , 3. Mutagenesis and diversification). They used ESM dates. ProteinMPNN8 (T4c) further refined and diversified candidates,
(DE.3)
language models (T4a), trained on general protein sequences rather generating a designed library of sequences. Experimental validation
than antibody-specific interactions, to evolve antibodies. By suggest- revealed several active variants; LuxSit stood out for its outstanding
ing novel, plausible mutations, this approach achieved up to 160-fold thermostability (melting temperature >95 °C) and its efficient, highly
binding improvements in just two rounds with minimal screening. specific catalysis of the DTZ chemiluminescent reaction.
The study also demonstrated that this workflow generalizes to other
protein families. Outlook
AI has advanced protein design from optimizing antibodies to creat-
AI-driven rational design ing novel luciferases. However, designing complex, multifunctional
Antibody optimization. In contrast to directed evolution approaches21, proteins such as large multidomain assemblies or those with intricate
the structure-to-sequence tools (T4c) such as ESM-IF1 (ref. 123) can be allosteric networks remains challenging, highlighting opportunities
harnessed to refine clinically mature antibodies56. Similarly, the study for future innovation.
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1052

---

<!-- Page 20 -->

Review article
To tackle these challenges, the next generation of AI tools must References
rest on robust, diverse data foundations. Training data drive model 1. Ebrahimi, S. B. & Samanta, D. Engineering protein-based therapeutics through structural
and chemical design. Nat. Commun. 14, 2411 (2023).
learning, whereas validation data evaluate performance. Biases or gaps
2. Chen, K. & Arnold, F. H. Tuning the activity of an enzyme for unusual environments:
in training sets can skew predictions171, and unrepresentative valida- sequential random mutagenesis of subtilisin E for catalysis in dimethylformamide.
tion data can mislead development, masking true utility172. Robust Proc. Natl Acad. Sci. USA 90, 5618–5622 (1993).
3. Lajoie, M. J. et al. Genomically recoded organisms expand biological functions. Science
data protocols are therefore essential. These include comprehensive
342, 357–360 (2013).
training libraries, rigorous validation and bias mitigation strategies 4. Listov, D., Goverde, C. A., Correia, B. E. & Fleishman, S. J. Opportunities and challenges
such as reweighing under-represented sequences. Equally important in design and optimization of protein function. Nat. Rev. Mol. Cell Biol. 25, 639–653
(2024).
is the ability of AI tools to dynamically integrate new biological and
5. Alley, E. C., Khimulya, G., Biswas, S., AlQuraishi, M. & Church, G. M. Unified rational
experimental data. For example, Chai-1 doubles prediction accuracy protein engineering with sequence-based deep representation learning. Nat. Methods
by incorporating epitope-conditioning constraints25, whereas vari- 16, 1315–1322 (2019).
UniRep is one of the first protein language models to learn rich evolutionary,
ational synthesis enables petascale-level synthesis with optimized structural and biophysical representations from raw, unlabelled protein
experimental parameters50. Leveraging large, high-quality data sets sequences, demonstrating how such models can power a diverse suite of artificial
could open new avenues in previously inaccessible topics such as intelligence-driven tools.
6. Jumper, J. et al. Highly accurate protein structure prediction with AlphaFold. Nature 596,
intrinsically disordered proteins. 583–589 (2021).
Beyond data, interpretability remains a key hurdle. Many AI tools AlphaFold 2 is the first model to regularly predict protein 3D structures from amino-acid
sequences with near-experimental accuracy, and its high-fidelity structural predictions
operate as black boxes, offering little insight into their decision-making
now underpin artificial intelligence-driven protein design workflows.
processes173. To foster adoption and trust, explainable AI methods are 7. Baek, M. et al. Accurate prediction of protein structures and interactions using a three-track
needed to elucidate the basis of in silico designs. Early efforts using neural network. Science 373, 871–876 (2021).
8. Dauparas, J. et al. Robust deep learning-based protein sequence design using ProteinMPNN.
sparse autoencoders show promise for discovering interpretable
Science 378, 49–56 (2022).
features, giving a glimpse into the ‘thinking’ behind these tools174. ProteinMPNN solves the inverse folding challenge by generating amino-acid
When these methodological foundations are in place, AI-driven sequences for fixed backbones with accuracy well above physics-based methods
and at high throughput, making it a widely adopted cornerstone in artificial
protein design is poised to usher in a new era of precision therapeutics,
intelligence-driven rational design workflows.
opening once ‘undruggable’ targets such as cancer-linked proteins 9. Watson, J. L. et al. De novo design of protein structure and function with RFDiffusion.
without obvious small-molecule pockets to protein-based drugs. Nature 620, 1089–1100 (2023).
RFDiffusion generates protein backbones that meet specified structural or functional
Advanced AI models can fine-tune binding specificity and enhance
objectives with high success rates across diverse, experimentally validated design
properties such as stability, solubility and manufacturability. This settings, including de novo design.
capability accelerates design–make–test–analyse cycles, enabling 10. Hamamsy, T. et al. Protein remote homology detection and structural alignment using
personalized, accessible treatments21,56. Yet, experimental valida- deep learning. Nat. Biotechnol. 42, 975–985 (2024).
11. van Kempen, M. et al. Fast and accurate protein structure search with Foldseek.
tion is still the bottleneck, and biological complexity can steer even Nat. Biotechnol. 42, 243–246 (2024).
accurate models towards irrelevant targets or missed critical disease 12. Wayment-Steele, H. K. et al. Predicting multiple conformations via sequence clustering
and AlphaFold2. Nature 625, 832–839 (2024).
mechanisms175. Progress is also limited by sparse data on key attributes,
13. Krishna, R. et al. Generalized biomolecular modeling and design with RoseTTAFold
especially stability and immunogenicity176. Expanding data coverage, All-Atom. Science 384, eadl2528 (2024).
such as incorporating new high-throughput stability measurements 14. Abramson, J. et al. Accurate structure prediction of biomolecular interactions with
AlphaFold 3. Nature 630, 493–500 (2024).
or curated immunogenicity data, would enhance model robustness
15. Hutchison, C. A. et al. Mutagenesis at a specific position in a DNA sequence. J. Biol. Chem.
and translatability. 253, 6551–6560 (1978).
AI-driven methods are also transcending traditional protein engi- 16. Alber, T., Sun, D. P., Nye, J. A., Muchmore, D. C. & Matthews, B. W. Temperature-sensitive
mutations of bacteriophage T4 lysozyme occur at sites with low mobility and low solvent
neering, which has focused on modifying natural proteins or recombin-
accessibility in the folded protein. Biochemistry 26, 3754–3758 (1987).
ing known functional domains. Emerging approaches now enable the 17. Marshall, S. A., Lazar, G. A., Chirino, A. J. & Desjarlais, J. R. Rational design and engineering
design of entirely novel proteins and biological systems with functions of therapeutic proteins. Drug Discov. Today 8, 212–221 (2003).
18. Davey, J. A., Damry, A. M., Goto, N. K. & Chica, R. A. Rational design of proteins that exchange
not found in nature. Strategies such as family-wide hallucination54, on functional timescales. Nat. Chem. Biol. 13, 1280–1285 (2017).
RFDiffusion9 and AlphaProteo156 achieve high accuracy in de novo binder 19. Yang, K. K., Wu, Z. & Arnold, F. H. Machine-learning-guided directed evolution for protein
generation. The impact of this capability extends beyond individual engineering. Nat. Methods 16, 687–694 (2019).
20. Huang, P.-S., Boyken, S. E. & Baker, D. The coming of age of de novo protein design.
proteins into the broader field of synthetic biology, in which future AI Nature 537, 320–327 (2016).
tools might predict and optimize complex genetic networks, enabling 21. Hie, B. L. et al. Efficient evolution of human antibodies from general protein language
molecular circuits with precisely controlled functions. However, design- models. Nat. Biotechnol. 42, 275–283 (2024).
22. Koh, H. Y., Nguyen, A. T. N., Pan, S., May, L. T. & Webb, G. I. Physicochemical graph
ing circuits remains challenging owing to the complexity of cellular neural network for learning protein–ligand interaction fingerprints from sequence data.
systems and limited understanding of emergent behaviours, especially Nat. Mach. Intell. 6, 673–687 (2024).
23. Chowdhury, R. et al. Single-sequence protein structure prediction using a language
interactions between proteins and other cellular components. Ethical
model and deep learning. Nat. Biotechnol. 40, 1617–1623 (2022).
considerations around synthetic biology must also be addressed. 24. Ingraham, J. B. et al. Illuminating protein space with a programmable generative model.
Looking ahead, AI could design systems incorporating non- Nature 623, 1070–1078 (2023).
25. Chai Discovery Team et al. Chai-1: decoding the molecular interactions of life. Preprint at
canonical amino acids or entirely new chemical backbones, lead-
bioRxiv https://doi.org/10.1101/2024.10.10.615955 (2024).
ing to unprecedented robustness and novel functionality. Even 26. Bryant, D. H. et al. Deep diversification of an AAV capsid protein by machine learning.
whole-proteome design is becoming conceivable: genomic language Nat. Biotechnol. 39, 691–696 (2021).
This study applies AI-driven directed evolution to generate and screen ~1010 AAV2
model, Evo, has begun conceptualizing whole proteomes, underscor-
capsid variants, yielding 110,689 viable mutants that exceed natural serotype diversity,
ing this possibility, although this capability is not yet fully realized, and and positions AI-driven capsid diversification as a new paradigm in gene-therapy vector
the resulting proteomes are not yet functional168. engineering.
27. Ogden, P. J., Kelsic, E. D., Sinai, S. & Church, G. M. Comprehensive AAV capsid fitness
landscape reveals a viral gene and enables machine-guided design. Science 366,
Published online: 8 September 2025 1139–1143 (2019).
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1053

---

<!-- Page 21 -->

Review article
28. Jiang, K. et al. Rapid in silico directed evolution by a protein language model with 56. Shanker, V. R., Bruun, T. U. J., Hie, B. L. & Kim, P. S. Unsupervised evolution of protein and
EVOLVEpro. Science 387, eadr6006 (2024). antibody complexes with a structure-informed language model. Science 385, 46–53
This study optimizes artificial intelligence-driven directed evolution by integrating (2024).
protein language-model embeddings with sequence-based activity predictors, 57. Röthlisberger, D. et al. Kemp elimination catalysts by computational enzyme design.
achieving up to 100-fold improvements in protein activity across diverse targets and Nature 453, 190–195 (2008).
streamlining modern directed evolution workflows. 58. Lauko, A. et al. Computational design of serine hydrolases. Science 388, eadu2454 (2025).
29. Yang, J. et al. Active learning-assisted directed evolution. Nat. Commun. 16, 714 (2025). 59. Smith, T. F. & Waterman, M. S. Identification of common molecular subsequences.
30. Gainza, P. et al. De novo design of protein interactions with learned surface fingerprints. J. Mol. Biol. 147, 195–197 (1981).
Nature 617, 176–184 (2023). 60. Altschul, S. F., Gish, W., Miller, W., Myers, E. W. & Lipman, D. J. Basic local alignment
This study developed a unified artificial intelligence-driven rational design workflow search tool. J. Mol. Biol. 215, 403–410 (1990).
that integrates 3D geometric network for binding-site prediction, structural database 61. Llinares-López, F., Berthet, Q., Blondel, M., Teboul, O. & Vert, J.-P. Deep embedding and
mining and motif-based binder design to generate de novo protein binders against alignment of protein sequences. Nat. Methods 20, 104–111 (2023).
targets such as the SARS-CoV-2 spike with nanomolar affinities. 62. Liu, W. et al. PLMSearch: protein language model powers accurate and fast sequence
31. Grøn, H., Bech, L. M., Branner, S. & Breddam, K. A highly active and oxidation-resistant search for remote homology. Nat. Commun. 15, 2775 (2024).
subtilisin-like enzyme produced by a combination of site-directed mutagenesis and 63. Kim, W. et al. Rapid and sensitive protein complex alignment with Foldseek-Multimer.
chemical modification. Eur. J. Biochem. 194, 897–901 (1990). Nat. Methods 22, 469–472 (2025).
32. Fleishman, S. J. et al. Computational design of proteins targeting the conserved stem 64. van den Oord, A., Vinyals, O. & kavukcuoglu, K. Neural discrete representation learning.
region of influenza hemagglutinin. Science 332, 816–821 (2011). In Advances in Neural Information Processing Systems (eds Guyon, I. et a.) Vol. 30
33. Varadi, M. et al. AlphaFold protein structure database: massively expanding the structural (Curran Associates, 2017).
coverage of protein-sequence space with high-accuracy models. Nucleic Acids Res. 50, 65. Eom, H. et al. Discovery of highly active kynureninases for cancer immunotherapy
D439–D444 (2022). through protein language model. Nucleic Acids Res. 53, gkae1245 (2025).
34. Lin, Z. et al. Evolutionary-scale prediction of atomic-level protein structure with a 66. Hu, M. et al. Advances in Neural Information Processing Systems Vol. 35
language model. Science 379, 1123–1130 (2023). (Curran Associates, Inc., 2022).
This study introduces ESM2, one of the most widely adopted protein language models, 67. Mirdita, M. et al. ColabFold: making protein folding accessible to all. Nat. Methods 19,
and ESMFold, which matches AlphaFold 2’s accuracy using only single‐sequence inputs 679–682 (2022).
without multiple‐sequence alignments, enabling substantially faster structure prediction. 68. Ahdritz, G. et al. OpenFold: retraining AlphaFold2 yields new insights into its learning
35. Hayes, T. et al. Simulating 500 million years of evolution with a language model. Science mechanisms and capacity for generalization. Nat. Methods 21, 1514–1524 (2024).
387, 850–858 (2025). 69. Ketata, M. A. et al. DiffDock-PP: rigid protein–protein docking with diffusion models.
36. Rives, A. et al. Biological structure and function emerge from scaling unsupervised Preprint at https://doi.org/10.48550/arXiv.2304.03889 (2023).
learning to 250 million protein sequences. Proc. Natl Acad. Sci. USA 118, e2016239118 70. Qiao, Z., Nie, W., Vahdat, A., Miller, T. F. & Anandkumar, A. State-specific protein–ligand
(2021). complex structure prediction with a multiscale deep generative model. Nat. Mach. Intell.
37. Ravindra et al. Multiplexed Cre-dependent selection yields systemic AAVs for targeting 6, 195–208 (2024).
distinct brain cell types. Nat. Methods 17, 541–550 (2020). 71. Guo, H.-B. et al. AlphaFold2 models indicate that protein sequence determines both
38. Silva, D.-A. et al. De novo design of potent and selective mimics of IL-2 and IL-15. Nature structure and dynamics. Sci. Rep. 12, 10696 (2022).
565, 186–191 (2019). 72. Anishchenko, I. et al. De novo protein design by deep network hallucination. Nature 600,
39. Altschul, S. F. et al. Gapped BLAST and PSI-BLAST: a new generation of protein database 547–552 (2021).
search programs. Nucleic Acids Res. 25, 3389–3402 (1997). 73. Wang, J. et al. Scaffolding protein functional sites using deep learning. Science 377,
40. Kaminski, K., Ludwiczak, J., Pawlicki, K., Alva, V. & Dunin-Horkawicz, S. pLM-BLAST: 387–394 (2022).
distant homology detection based on direct comparison of sequence representations 74. He, J., Turzo, S. B. A., Seffernick, J. T., Kim, S. S. & Lindert, S. Prediction of intrinsic disorder
from protein language models. Bioinformatics 39, btad579 (2023). using Rosetta ResidueDisorder and AlphaFold2. J. Phys. Chem. B 126, 8439–8446 (2022).
41. Zhang, Y. & Skolnick, J. TM-align: a protein structure alignment algorithm based on the 75. Kurgan, L. et al. Tutorial: a guide for the selection of fast and accurate computational
TM-score. Nucleic Acids Res. 33, 2302–2309 (2005). tools for the prediction of intrinsic disorder in proteins. Nat. Protoc. 18, 3157–3172 (2023).
42. Holm, L. Dali server: structural unification of protein families. Nucleic Acids Res. 50, 76. Vander Meersche, Y., Cretin, G., de Brevern, A. G., Gelly, J.-C. & Galochkina, T. MEDUSA:
W210–W215 (2022). prediction of protein flexibility from sequence. J. Mol. Biol. 433, 166882 (2021).
43. The UniProt Consortium. UniProt: a worldwide hub of protein knowledge. Nucleic Acids Res. 77. Mészáros, B., Erdős, G. & Dosztányi, Z. IUPred2A: context-dependent prediction of
47, D506–D515 (2019). protein disorder as a function of redox state and protein binding. Nucleic Acids Res. 46,
44. Hopf, T. A. et al. The EVcouplings Python framework for coevolutionary sequence analysis. W329–W337 (2018).
Bioinformatics 35, 1582–1584 (2019). 78. Hu, G. et al. flDPnn: accurate intrinsic disorder prediction with putative propensities of
45. Burley, S. K. et al. RCSB Protein Data Bank (RCSB.org): delivery of experimentally-determined disorder functions. Nat. Commun. 12, 4438 (2021).
PDB structures alongside one million computed structure models of proteins from artificial 79. Roney, J. P. & Ovchinnikov, S. State-of-the-art estimation of protein model accuracy using
intelligence/machine learning. Nucleic Acids Res. 51, D488–D508 (2023). AlphaFold. Phys. Rev. Lett. 129, 238101 (2022).
46. Baek, M. et al. Accurate prediction of protein–nucleic acid complexes using RoseTTAFoldNA. 80. Pak, M. A. et al. Using AlphaFold to predict the impact of single mutations on protein
Nat. Methods 21, 117–121 (2024). stability and function. PLoS ONE 18, e0282689 (2023).
47. Evans, R. et al. Protein complex prediction with AlphaFold-Multimer. Preprint at bioRxiv 81. Pudžiuvelytė, I. et al. TemStaPro: protein thermostability prediction using sequence
https://doi.org/10.1101/2021.10.04.463034 (2022). representations from protein language models. Bioinformatics 40, btae157 (2024).
48. Radivojac, P. et al. A large-scale evaluation of computational protein function prediction. 82. Blaabjerg, L. M. et al. Rapid protein stability prediction using deep learning
Nat. Methods 10, 221–227 (2013). representations. eLife 12, e82593 (2023).
49. Gainza, P. et al. Deciphering interaction fingerprints from protein molecular surfaces 83. Zhou, Y., Pan, Q., Pires, D. E. V., Rodrigues, C. H. M. & Ascher, D. B. DDMut: predicting
using geometric deep learning. Nat. Methods 17, 184–192 (2020). effects of mutations on protein stability using deep learning. Nucleic Acids Res. 51,
50. Weinstein, E. N. et al. Manufacturing-aware generative model architectures W122–W128 (2023).
enable biological sequence design and synthesis at petascale. Preprint at bioRxiv 84. Yin, R., Feng, B. Y., Varshney, A. & Pierce, B. G. Benchmarking AlphaFold for protein
https://doi.org/10.1101/2024.09.13.612900 (2024). complex modeling reveals accuracy determinants. Protein Sci. 31, e4379 (2022).
51. Packer, M. S. & Liu, D. R. Methods for the directed evolution of proteins. Nat. Rev. Genet. 85. Ferreiro, D. U., Komives, E. A. & Wolynes, P. G. Frustration in biomolecules. Q. Rev.
16, 379–394 (2015). Biophys. 47, 285–363 (2014).
52. Biswas, S., Khimulya, G., Alley, E. C., Esvelt, K. M. & Church, G. M. Low-N protein 86. del Alamo, D., Sala, D., Mchaourab, H. S. & Meiler, J. Sampling alternative conformational
engineering with data-efficient deep learning. Nat. Methods 18, 389–396 (2021). states of transporters and receptors with AlphaFold2. eLife 11, e75751 (2022).
53. Madani, A. et al. Large language models generate functional protein sequences across 87. Guan, X. et al. Predicting protein conformational motions using energetic frustration
diverse families. Nat. Biotechnol. 41, 1099–1106 (2023). analysis and AlphaFold2. Proc. Natl Acad. Sci. USA 121, e2410662121 (2024).
ProGen shows that large protein language models conditioned on ‘tags’ (short textual 88. Chakravarty, D. et al. AlphaFold predictions of fold-switched conformations are driven by
annotations such as enzyme function) can generate functional protein sequences structure memorization. Nat. Commun. 15, 7296 (2024).
across diverse families, enabling rapid tag-driven protein design without explicit 89. Jing, B., Berger, B. & Jaakkola, T. AlphaFold meets flow matching for generating protein
structural input. ensembles. In Proc. 41st International Conference on Machine Learning Vol. 235,
54. Yeh, A. H.-W. et al. De novo design of luciferases using deep learning. Nature 614, 22277–22303 (JMLR.org, 2024).
774–780 (2023). 90. Wang, T. et al. Ab initio characterization of protein molecular dynamics with AI2BMD.
This study integrates AI tools such as structure prediction, sequence design and Nature 635, 1019–1027 (2024).
virtual screening into a unified AI-driven rational design workflow to create de novo 91. Wang, Y. et al. Enhancing geometric representations for molecules with equivariant
luciferases that catalyse DTZ chemiluminescence with exceptional specificity. vector–scalar interactive message passing. Nat. Commun. 15, 313 (2024).
55. Cao, L. et al. Design of protein-binding proteins from the target structure alone. Nature 92. Arnold, C. AlphaFold touted as next big thing for drug discovery — but is it? Nature 622,
605, 551–560 (2022). 15–17 (2023).
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1054

---

<!-- Page 22 -->

Review article
93. Callaway, E. Major AlphaFold upgrade offers boost for drug discovery. Nature 629, 127. Dou, J. et al. De novo design of a fluorescence-activating β-barrel. Nature 561, 485–491
509–510 (2024). (2018).
94. Miller, E. B. et al. Enabling structure-based drug discovery utilizing predicted models. 128. Gao, B. et al. Advances in Neural Information Processing Systems Vol. 36
Cell 187, 521–525 (2024). (Curran Associates, Inc., 2023).
95. Jang, Y. J. et al. Accurate prediction of protein function using statistics-informed graph 129. Ho, J., Jain, A. & Abbeel, P. Advances in Neural Information Processing Systems Vol. 33
networks. Nat. Commun. 15, 6601 (2024). (Curran Associates, Inc., 2020).
96. You, R. et al. NetGO: improving large-scale protein function prediction with massive 130. Trippe, B. L. et al. Diffusion probabilistic modeling of protein backbones in 3D for the
network information. Nucleic Acids Res. 47, W379–W387 (2019). motif-scaffolding problem. Int. Conf. Learn. Represent. ICLR 2022 (2022).
97. Yao, S. et al. NetGO 2.0: improving large-scale protein function prediction with massive 131. Luo, S. et al. Antigen-specific antibody design and optimization with diffusion-based
sequence, text, domain, family and network information. Nucleic Acids Res. 49, generative models for protein structures. Adv. Neural Inf. Process. Syst. 35, 9754–9767
W469–W475 (2021). (2022).
98. Wang, S., You, R., Liu, Y., Xiong, Y. & Zhu, S. NetGO 3.0: protein language model improves 132. Yang, J. et al. Improved protein structure prediction using predicted interresidue
large-scale functional annotations. Genom. Proteom. Bioinform. 21, 349–358 (2023). orientations. Proc. Natl Acad. Sci. USA 117, 1496–1503 (2020).
99. Le Guilloux, V., Schmidtke, P. & Tuffery, P. Fpocket: an open source platform for ligand 133. Bennett, N. R. et al. Improving de novo protein binder design with deep learning.
pocket detection. BMC Bioinform. 10, 168 (2009). Nat. Commun. 14, 2625 (2023).
100. Porollo, A. & Meller, J. Prediction-based fingerprints of protein–protein interactions. 134. Pacesa, M. et al. BindCraft: one-shot design of functional protein binders. Preprint at
Proteins Struct. Funct. Bioinform. 66, 630–645 (2007). bioRxiv https://doi.org/10.1101/2024.09.30.615802 (2024).
101. Murakami, Y. & Mizuguchi, K. Applying the naive Bayes classifier with kernel density 135. Wicky, B. I. M. et al. Hallucinating symmetric protein assemblies. Science 378, 56–61
estimation to the prediction of protein–protein interaction sites. Bioinformatics 26, (2022).
1841–1848 (2010). 136. Lisanza, S. L. et al. Multistate and functional protein design using RoseTTAFold sequence
102. Tubiana, J., Schneidman-Duhovny, D. & Wolfson, H. J. ScanNet: an interpretable space diffusion. Nat. Biotechnol. 43, 1288–1298 (2024).
geometric deep learning model for structure-based protein binding site prediction. 137. Chu, A. E. et al. An all-atom protein generative model. Proc. Natl Acad. Sci. USA 121,
Nat. Methods 19, 730–739 (2022). e2311500121 (2024).
103. Jiménez, J., Doerr, S., Martínez-Rosell, G., Rose, A. S. & De Fabritiis, G. DeepSite: 138. McNutt, A. T. et al. GNINA 1.0: molecular docking with deep learning. J. Cheminform. 13,
protein-binding site predictor using 3D-convolutional neural networks. Bioinformatics 43 (2021).
33, 3036–3042 (2017). 139. Zhou, Z. et al. Enhancing efficiency of protein language models with minimal wet-lab
104. Corso, G., Stärk, H., Jing, B., Barzilay, R. & Jaakkola, T. DiffDock: diffusion steps, twists, data through few-shot learning. Nat. Commun. 15, 5566 (2024).
and turns for molecular docking. In International Conference on Learning Representations 140. Hsu, C., Nisonoff, H., Fannjiang, C. & Listgarten, J. Learning protein fitness models from
(2023). evolutionary and assay-labeled data. Nat. Biotechnol. 40, 1114–1122 (2022).
105. Elliott, S. et al. Enhancement of therapeutic protein in vivo activities through 141. Frey, N. C. et al. Lab-in-the-loop therapeutic antibody design with deep learning. Preprint
glycoengineering. Nat. Biotechnol. 21, 414–421 (2003). at bioRxiv https://doi.org/10.1101/2025.02.19.639050 (2025).
106. Hunter, T. The age of crosstalk: phosphorylation, ubiquitination, and beyond. Mol. Cell 142. Wu, Z., Kan, S. B. J., Lewis, R. D., Wittmann, B. J. & Arnold, F. H. Machine learning-assisted
28, 730–738 (2007). directed protein evolution with combinatorial libraries. Proc. Natl Acad. Sci. USA 116,
107. Ramazi, S. & Zahiri, J. Post-translational modifications in proteins: resources, tools and 8852–8858 (2019).
prediction methods. Database 2021, baab012 (2021). 143. Narayanan, H. et al. Machine learning for biologics: opportunities for protein
108. Wang, D. et al. MusiteDeep: a deep-learning framework for general and kinase-specific engineering, developability, and formulation. Trends Pharmacol. Sci. 42, 151–165 (2021).
phosphorylation site prediction. Bioinformatics 33, 3909–3916 (2017). 144. Gentiluomo, L. et al. Application of interpretable artificial neural networks to early
109. Wang, D. et al. MusiteDeep: a deep-learning based webserver for protein post-translational monoclonal antibodies development. Eur. J. Pharm. Biopharm. 141, 81–89 (2019).
modification site prediction and visualization. Nucleic Acids Res. 48, W140–W146 (2020). 145. Gentiluomo, L., Roessner, D. & Frieß, W. Application of machine learning to predict
110. Shrestha, P., Kandel, J., Tayara, H. & Chong, K. T. Post-translational modification monomer retention of therapeutic proteins after long term storage. Int. J. Pharm. 577,
prediction via prompt-based fine-tuning of a GPT-2 model. Nat. Commun. 15, 6699 119039 (2020).
(2024). 146. Wang, C. & Zou, Q. Prediction of protein solubility based on sequence physicochemical
111. Yan, Y. et al. MIND-S is a deep-learning prediction model for elucidating protein patterns and distributed representation information with DeepSoluE. BMC Biol. 21, 12
post-translational modifications in human diseases. Cell Rep. Methods 3, 100430 (2023).
(2023). 147. Zhang, X. et al. PLM_Sol: predicting protein solubility by benchmarking multiple
112. Shi, X.-X. et al. PTMdyna: exploring the influence of post-translation modifications on protein language models with the updated Escherichia coli protein solubility dataset.
protein conformational dynamics. Brief. Bioinform. 23, bbab424 (2022). Brief. Bioinform. 25, bbae404 (2024).
113. Zhou, N. et al. The CAFA challenge reports improved protein function prediction and new 148. Planas-Iglesias, J. et al. AggreProt: a web server for predicting and engineering
functional annotations for hundreds of genes through experimental screens. Genome Biol. aggregation prone regions in proteins. Nucleic Acids Res. 52, W159–W169 (2024).
20, 244 (2019). 149. Louros, N., Schymkowitz, J. & Rousseau, F. Mechanisms and pathology of protein
114. Bloom, J. D., Labthavikul, S. T., Otey, C. R. & Arnold, F. H. Protein stability promotes misfolding and aggregation. Nat. Rev. Mol. Cell Biol. 24, 912–933 (2023).
evolvability. Proc. Natl Acad. Sci. USA 103, 5869–5874 (2006). 150. Reynisson, B., Alvarez, B., Paul, S., Peters, B. & Nielsen, M. NetMHCpan-4.1 and
115. Meier, J. et al. Advances in Neural Information Processing Systems Vol. 34, 29287–29303 NetMHCIIpan-4.0: improved predictions of MHC antigen presentation by concurrent
(Curran Associates, Inc., 2021). motif deconvolution and integration of MS MHC eluted ligand data. Nucleic Acids Res.
116. Ferruz, N., Schmidt, S. & Höcker, B. ProtGPT2 is a deep unsupervised language model 48, W449–W454 (2020).
for protein design. Nat. Commun. 13, 4348 (2022). 151. Hashemi, N. et al. Improved prediction of MHC-peptide binding using protein language
117. Unsal, S. et al. Learning functional properties of proteins with language models. models. Front. Bioinform. 3, 1207380 (2023).
Nat. Mach. Intell. 4, 227–245 (2022). 152. Müller, M. et al. Machine learning methods and harmonized datasets improve
118. Ferruz, N. & Höcker, B. Controllable protein design with language models. Nat. Mach. immunogenic neoantigen prediction. Immunity 56, 2650–2663.e6 (2023).
Intell. 4, 521–532 (2022). 153. Li, G., Iyer, B., Prasath, V. B. S., Ni, Y. & Salomonis, N. DeepImmuno: deep
119. Truong, T. F. Jr & Bepler, T. PoET: A generative model of protein families as sequences- learning-empowered prediction and generation of immunogenic peptides for T-cell
of-sequences. In Advances in Neural Information Processing Systems (eds Oh, A. et al.) immunity. Brief. Bioinform. 22, bbab160 (2021).
Vol. 36 (Curran Associates, 2023). 154. Marks, C., Hummer, A. M., Chin, M. & Deane, C. M. Humanization of antibodies using a
120. Gligorijević, V. et al. Function-guided protein design by deep manifold sampling. machine learning approach on large-scale repertoire data. Bioinformatics 37, 4041–4047
Preprint at bioRxiv https://doi.org/10.1101/2021.12.22.473759 (2021). (2021).
121. Kucera, T., Togninalli, M. & Meng-Papaxanthos, L. Conditional generative modeling for 155. Qiu, Y. & Cheng, F. Artificial intelligence for drug discovery and development in
de novo protein design with hierarchical functions. Bioinformatics 38, 3454–3461 (2022). Alzheimer’s disease. Curr. Opin. Struct. Biol. 85, 102776 (2024).
122. Ingraham, J., Garg, V., Barzilay, R. & Jaakkola, T. Generative models for graph-based protein 156. Zambaldi, V. et al. De novo design of high-affinity protein binders with AlphaProteo.
design. In Advances in Neural Information Processing Systems (eds Wallach, H. et al.) Preprint at https://doi.org/10.48550/arXiv.2409.08022 (2024).
Vol. 32 (Curran Associates, 2019). 157. Ostrov, N. et al. Design, synthesis, and testing toward a 57-codon genome. Science 353,
123. Hsu, C. et al. Learning inverse folding from millions of predicted structures. In Proc. 39th 819–822 (2016).
International Conference on Machine Learning 8946–8970 (PMLR, 2022). 158. Liu, Y., Yang, Q. & Zhao, F. Synonymous but not silent: the codon usage code for gene
124. Dauparas, J. et al. Atomic context-conditioned protein sequence design using expression and protein folding. Annu. Rev. Biochem. 90, 375–401 (2021).
LigandMPNN. Nat. Methods 22, 717–723 (2025). 159. Hanson, G. & Coller, J. Codon optimality, bias and usage in translation and mRNA decay.
125. McFerrin, L. & Ratan, U. Highlights from the AWS Life Sciences Executive Symposium Nat. Rev. Mol. Cell Biol. 19, 20–30 (2018).
2023: accelerating pharma drug discovery with ML and generative AI. AWS Blogs 160. Fu, H. et al. Codon optimization with deep learning to enhance protein expression.
https://go.nature.com/4gbiXvp (31 May 2023). Sci. Rep. 10, 17617 (2020).
126. Goverde, C. A. et al. Computational design of soluble and functional membrane protein 161. Sidi, T., Bahiri-Elitzur, S., Tuller, T. & Kolodny, R. Predicting gene sequences with AI to
analogues. Nature 631, 449–458 (2024). study codon usage patterns. Proc. Natl Acad. Sci. USA 122, e2410003121 (2025).
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1055

---

<!-- Page 23 -->

Review article
162. Constant, D. A. et al. Deep learning-based codon optimization with large-scale 190. Lam, J. H. et al. A deep learning framework to predict binding preference of RNA
synonymous variant datasets enables generalized tunable protein expression. constituents on protein surface. Nat. Commun. 10, 4941 (2019).
Preprint at bioRxiv https://doi.org/10.1101/2023.02.11.528149 (2023). 191. Cheng, P. et al. Zero-shot prediction of mutation effects with multimodal deep
163. Ren, Z. et al. CodonBERT: a BERT-based architecture tailored for codon optimization representation learning guides protein engineering. Cell Res. 34, 630–647 (2024).
using the cross-attention mechanism. Bioinformatics 40, btae330 (2024). 192. Krizhevsky, A., Sutskever, I. & Hinton, G. E. ImageNet classification with deep
164. Fallahpour, A., Gureghian, V., Filion, G. J., Lindner, A. B. & Pandi, A. CodonTransformer: convolutional neural networks. In Advances in Neural Information Processing Systems
a multispecies codon optimizer using context-aware neural networks. Nat. Commun. 16, (ed Pereira, F. et al.) Vol. 25 (Curran Associates, 2012).
3205 (2025). 193. Silver, D. et al. Mastering the game of Go without human knowledge. Nature 550,
165. Weinstein, E. N. et al. Optimal design of stochastic DNA synthesis protocols based 354–359 (2017).
on generative sequence models. In Proc. 25th International Conference on Artificial 194. Vaswani, A. et al. Advances in Neural Information Processing Systems Vol. 30
Intelligence and Statistics 7450–7482 (PMLR, 2022). (Curran Associates, Inc., 2017).
166. Stark, H., Padia, U., Balla, J., Diao, C. & Church, G. CodonMPNN for organism specific 195. Radford, A. et al. Learning transferable visual models from natural language supervision.
and codon optimal inverse folding. Preprint at https://doi.org/10.48550/arXiv.2409.17265 In Proc. 38th International Conference on Machine Learning 8748–8763 (PMLR, 2021).
(2024). 196. Devlin, J., Chang, M.-W., Lee, K. & Toutanova, K. BERT: pre-training of deep bidirectional
167. Outeiral, C. & Deane, C. M. Codon language embeddings provide strong signals for use transformers for language understanding. In Proc. 2019 Conference of the North
in protein engineering. Nat. Mach. Intell. 6, 170–179 (2024). American Chapter of the Association for Computational Linguistics: Human Language
168. Nguyen, E. et al. Sequence modeling and design from molecular to genome scale with Technologies, Vol. 1 (Long and Short Papers) (eds Burstein, J. et al.) 4171–4186 (ACL, 2019).
Evo. Science 386, eado9336 (2024). 197. Zhang, Z. et al. Protein representation learning by geometric structure pretraining.
169. Russell, S. et al. Efficacy and safety of voretigene neparvovec (AAV2-hRPE65v2) in Int. Conf. Learn. Represent. ICLR 2022 (2022).
patients with RPE65-mediated inherited retinal dystrophy: a randomised, controlled, 198. Wang, Y. et al. Self-play reinforcement learning guides protein engineering. Nat. Mach. Intell.
open-label, phase 3 trial. Lancet 390, 849–860 (2017). 5, 845–860 (2023).
170. Mendell, J. R. et al. Single-dose gene-replacement therapy for spinal muscular atrophy. 199. Lutz, I. D. et al. Top-down design of protein architectures with reinforcement learning.
N. Engl. J. Med. 377, 1713–1722 (2017). Science 380, 266–273 (2023).
171. Ding, F. & Steinhardt, J. Protein language models are biased by unequal sequence sampling 200. Rumelhart, D. E. & McClelland, J. L. Parallel Distributed Processing: Explorations in the
across the tree of life. Preprint at bioRxiv https://doi.org/10.1101/2024.03.07.584001 Microstructure of Cognition: Foundations 318–362 (MIT Press, 1987).
(2024). 201. LeCun, Y., Bengio, Y. & Hinton, G. Deep learning. Nature 521, 436–444 (2015).
172. Volkov, M. et al. On the frustration to predict binding affinities from protein–ligand 202. Kipf, T. N. & Welling, M. Semi-supervised classification with graph convolutional
structures with deep neural networks. J. Med. Chem. 65, 7946–7958 (2022). networks. Int. Conf. Learn. Represent. ICLR 2017 (2017).
173. Medina-Ortiz, D., Khalifeh, A., Anvari-Kazemabad, H. & Davari, M. D. Interpretable and 203. Bronstein, M. M., Bruna, J., LeCun, Y., Szlam, A. & Vandergheynst, P. Geometric deep
explainable predictive machine learning models for data-driven protein engineering. learning: going beyond Euclidean data. IEEE Signal. Process. Mag. 34, 18–42 (2017).
Biotechnol. Adv. 79, 108495 (2025).
174. Simon, E. & Zou, J. InterPLM: discovering interpretable features in protein language models Acknowledgements
via sparse autoencoders. Preprint at bioRxiv https://doi.org/10.1101/2024.11.14.623630 The authors thank members of the Church lab for their critical reading of the manuscript and
(2025). helpful discussions, including X. Portillo, Z. Tang, J. Lee, C.-T. Wu and E. Mintzer. This work was
175. AI’s potential to accelerate drug discovery needs a reality check. Nature 622, 217–217 funded by the Leo Foundation (LF-OC-20-000420), the grant from the American Academy of
(2023). Dermatology (AAD), and the Wyss Funding for Validation Projects.
176. Cuturello, F., Celoria, M., Ansuini, A. & Cazzaniga, A. Enhancing predictions of protein
stability changes induced by single mutations using MSA-based language models. Author contributions
Bioinformatics 40, btae447 (2024). H.Y.K., Y.Z., L.L. and G.M.C. conceptualized the manuscript. H.Y.K., Y.Z., M.Y., R.A., L.L., G.I.W.,
177. Petti, S. et al. End-to-end learning of multiple sequence alignments with differentiable S.P. and G.M.C. contributed to the development of the concept and structure of the paper.
Smith–Waterman. Bioinformatics 39, btac724 (2023). H.Y.K., Y.Z., M.Y., R.A. and L.L. performed the literature review and drafted the manuscript.
178. Lu, W. et al. DynamicBind: predicting ligand-specific protein–ligand complex structure H.Y.K. and Y.Z. prepared the figures, and G.I.W., S.P., and L.L. supervised the overall
with a deep equivariant generative model. Nat. Commun. 15, 1071 (2024). preparation. All authors contributed to the final preparation of the manuscript and read,
179. Wohlwend, J. et al. Boltz-1 democratizing biomolecular interaction modeling. Preprint at edited and approved the final version.
bioRxiv https://doi.org/10.1101/2024.11.19.624167 (2025).
180. Yu, T. et al. Enzyme function prediction using contrastive learning. Science 379, Competing interests
1358–1363 (2023). Disclosures for G.M.C. can be found at http://arep.med.harvard.edu/gmc/tech.html.
181. Luo, F., Wang, M., Liu, Y., Zhao, X.-M. & Li, A. DeepPhos: prediction of protein
phosphorylation sites with deep learning. Bioinformatics 35, 2766–2773 (2019). Citation diversity statement
182. Nijkamp, E., Ruffolo, J. A., Weinstein, E. N., Naik, N. & Madani, A. ProGen2: exploring the We acknowledge that papers authored by scholars from historically excluded groups are
boundaries of protein language models. Cell Syst. 14, 968–978.e3 (2023). systematically under-cited. Here, we have made every attempt to reference relevant papers in
183. Wang, T. et al. Improved fragment sampling for ab initio protein structure prediction a manner that is equitable in terms of racial, ethnic, gender and geographical representation.
using deep neural networks. Nat. Mach. Intell. 1, 347–355 (2019).
184. Marchand, A. et al. Targeting protein–ligand neosurfaces with a generalizable deep Additional information
learning tool. Nature 639, 522–531 (2025). Peer review information Nature Reviews Bioengineering thanks the anonymous reviewer(s) for
185. Ahern, W. et al. Atom level enzyme active site scaffolding using RFdiffusion2. Preprint at their contribution to the peer review of this work.
bioRxiv https://doi.org/10.1101/2025.04.09.648075 (2025).
186. Wang, X., Terashi, G., Christoffer, C. W., Zhu, M. & Kihara, D. Protein docking model Publisher’s note Springer Nature remains neutral with regard to jurisdictional claims in
evaluation by 3D deep convolutional neural networks. Bioinformatics 36, 2113–2118 published maps and institutional affiliations.
(2020).
187. Réau, M., Renaud, N., Xue, L. C. & Bonvin, A. M. J. J. DeepRank-GNN: a graph neural Springer Nature or its licensor (e.g. a society or other partner) holds exclusive rights to
network framework to learn patterns in protein–protein interfaces. Bioinformatics 39, this article under a publishing agreement with the author(s) or other rightsholder(s);
btac759 (2023). author self-archiving of the accepted manuscript version of this article is solely governed
188. Shuai, R. W., Ruffolo, J. A. & Gray, J. J. IgLM: infilling language modeling for antibody by the terms of such publishing agreement and applicable law.
sequence design. Cell Syst. 14, 979–989.e4 (2023).
189. Montemurro, A. et al. NetTCR-2.0 enables accurate prediction of TCR–peptide binding by © Springer Nature Limited 2025
using paired TCRα and β sequence data. Commun. Biol. 4, 1–13 (2021).
Nature Reviews Bioengineering | Volume 3 | December 2025 | 1034–1056 1056
