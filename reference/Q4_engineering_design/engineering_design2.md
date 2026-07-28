<!-- Page 1 -->

nature chemical engineering
Article https://doi.org/10.1038/s44286-023-00002-4
Self-driving laboratories to autonomously
navigate the protein fitness landscape
Received: 20 July 2023 Jacob T. Rapp 1, Bennett J. Bremer1 & Philip A. Romero 1,2
Accepted: 20 November 2023
Protein engineering has nearly limitless applications across chemistry,
Published online: 11 January 2024
energy and medicine, but creating new proteins with improved or novel
Check for updates
functions remains slow, labor-intensive and inefficient. Here we present
the Self-driving Autonomous Machines for Protein Landscape Exploration
(SAMPLE) platform for fully autonomous protein engineering. SAMPLE
is driven by an intelligent agent that learns protein sequence–function
relationships, designs new proteins and sends designs to a fully automated
robotic system that experimentally tests the designed proteins and provides
feedback to improve the agent’s understanding of the system. We deploy
four SAMPLE agents with the goal of engineering glycoside hydrolase
enzymes with enhanced thermal tolerance. Despite showing individual
differences in their search behavior, all four agents quickly converge on
thermostable enzymes. Self-driving laboratories automate and accelerate
the scientific discovery process and hold great potential for the fields of
protein engineering and synthetic biology.
Human researchers engineer biological systems through the discovery- hold great promise for the fields of protein engineering and synthetic
driven process of hypothesis generation, designing experiments to test biology11–13, but these applications are challenging because biological
hypotheses, performing these experiments in a wet laboratory, and phenotypes are complex and nonlinear, genomic search spaces are
interpreting the resulting data to refine understanding of the system. high-dimensional, and biological experiments require multiple hands-
This process is iterated to converge on knowledge of biological mecha- on processing steps that are error-prone and difficult to automate.
nisms and design new systems with improved properties and behaviors. There are examples of automated workflows for synthetic biology
However, despite notable achievements in biological engineering and that require some human input and manual sample processing14,15,
synthetic biology, this process remains highly inefficient, repetitive but these are not fully autonomous in their ability to operate without
and laborious, requiring multiple cycles of hypothesis generation and human intervention.
testing that can take years to complete. In this Article we introduce the Self-driving Autonomous Machines
Robot scientists and self-driving laboratories combine automated for Protein Landscape Exploration (SAMPLE) platform to rapidly engi-
learning, reasoning and experimentation to accelerate scientific dis- neer proteins without human intervention, feedback or subjectivity.
covery and design new molecules, materials and systems. Intelligent SAMPLE is driven by an intelligent agent that learns protein sequence–
robotic systems are superior to humans in their ability to learn across function relationships from data and designs new proteins to test
disparate data sources and data modalities, make decisions under hypotheses. The agent interacts with the physical world though a fully
uncertainty, operate continuously without breaks, and generate highly automated robotic system that experimentally tests the designed
reproducible data with full metadata tracking and real-time data shar- proteins by synthesizing genes, expressing proteins and performing
ing. Autonomous and semi-autonomous systems have been applied biochemical measurements of enzyme activity. Seamless integration
to gene identification in yeast1–3, new chemical synthesis method- between the intelligent agent and experimental automation enables
ologies4–6 and the discovery of new photocatalysts7, photovoltaics8, fully autonomous design–test–learn cycles to understand and optimize
adhesive materials9 and thin-film materials10. Self-driving laboratories the sequence–function landscape.
1Department of Biochemistry, University of Wisconsin–Madison, Madison, WI, USA. 2Department of Chemical & Biological Engineering, University of
Wisconsin–Madison, Madison, WI, USA. e-mail: promero2@wisc.edu
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 97

---

<!-- Page 2 -->

Article https://doi.org/10.1038/s44286-023-00002-4
We deployed four independent SAMPLE agents to navigate the engineering goal. BO techniques address this problem of sequential
glycoside hydrolase landscape and discover enzymes with enhanced decision-making under uncertainty. The upper confidence bound (UCB)
thermal tolerance. The agents’ optimization trajectories started with algorithm iteratively samples points with the largest upper confidence
exploratory behavior to understand the broad landscape structure bound (predictive mean plus prediction interval) and is proven to rapidly
and then quickly converged on highly stable enzymes that were at converge to the optimal point with high sample efficiency23,24. How-
least 12 °C more stable than the initial starting sequences. We observed ever, naïve implementation of UCB for protein engineering is limited,
notable differences in the individual agents’ search behavior arising because the inactive ‘holes’ in the landscape provide no information to
from experimental measurement noise, yet all agents robustly iden- improve the model. We devised two heuristic BO methods that consider
tified thermostable designs while searching less than 2% of the full the output of the active/inactive GP classifier (P ) to focus sampling
active
landscape. SAMPLE agents continually refine their understanding of toward functional sequences. The ‘UCB positive’ method only considers
the landscape through active information acquisition to efficiently the subset of sequences that are predicted to be active by the GP classi-
discover optimized proteins. SAMPLE is a general-purpose protein fier (P > 0.5) and selects the sequence with the top UCB value. The
active
engineering platform that can be broadly applied across biological ‘Expected UCB’ method takes the expected value of the UCB score by
engineering and synthetic biology. multiplying by the GP classifier P and selects the sequence with the
active
top expected UCB value. We tested these methods by running 10,000
Results simulated protein engineering experiments with the cytochrome P450
A fully autonomous system for protein engineering data (Fig. 1c,d). On average, the UCB positive and Expected UCB methods
We sought to build a fully autonomous system to mimic the human bio- found thermostable P450s with only 26 measurements and required
logical discovery and design process. Human researchers can be viewed three- to fourfold fewer samples than the standard UCB and random
as intelligent agents that perform actions in a laboratory environment methods. We also tested the BO methods in a batch setting where multi-
and receive data as feedback. Through repeated interactions with the ple sequences are tested in parallel and found a slight benefit to running
laboratory environment, human agents develop an understanding of experiments in smaller batches (Supplementary Fig. 1).
the system and learn behaviors to achieve an engineering goal. SAMPLE The agent designs proteins and sends them to the SAMPLE labora-
consists of an intelligent agent that autonomously learns, makes deci- tory environment to provide experimental feedback (Supplementary
sions and takes actions in a laboratory environment to explore protein Video 1). We developed a highly streamlined, robust and general pipe-
sequence–function relationships and engineer proteins (Fig. 1a). line for automated gene assembly, cell-free protein expression and bio-
The protein fitness landscape describes the mapping from sequence chemical characterization. Our procedure assembles pre-synthesized
to function and can be imagined as a terrestrial landscape of peaks, val- DNA fragments using Golden Gate cloning25 to produce a full intact
leys and ridges16. The SAMPLE agent aims to identify high-activity fitness gene and the necessary 5′/3′ untranslated regions for T7-based protein
peaks (that is, top performing sequences) from an initially unknown expression. The assembled expression cassette is then amplified via
sequence–function landscape. The agent actively queries the environ- polymerase chain reaction (PCR) and the product is verified using
ment to gather information and construct an internal perception of the the fluorescent dye EvaGreen to detect double-stranded DNA (Sup-
landscape. The agent must allocate resources between exploration, to plementary Fig. 2). The amplified expression cassette is then added
understand the landscape structure, and exploitation, to utilize current directly to T7-based cell-free protein expression reagents to produce
landscape knowledge to identify optimal sequence configurations. We the target protein. Finally, the expressed protein is characterized using
pose the agent’s protein engineering task as a Bayesian optimization colorimetric/fluorescent assays to evaluate its biochemical activity and
(BO) problem that seeks to optimize an unknown objective function properties (Supplementary Fig. 3).
and must efficiently trade off between exploration and exploitation17,18. For this work we focused on glycoside hydrolase enzymes and
The SAMPLE agent uses a Gaussian process (GP) model to build their tolerance to elevated temperatures. We tested the reproducibil-
an understanding of the fitness landscape from limited experimen- ity of our automated experimental pipeline on four diverse glycoside
tal observations. The model must consider the protein function of hydrolase family 1 (GH1) enzymes from Streptomyces species (Fig. 1e).
interest, in addition to inactive ‘holes’ in the landscape arising from The system reliably measured the thermostability (T , defined in the
50
destabilization of the protein structure19,20. We use a multi-output GP section Thermostability assay) of the enzymes with an error less than
that simultaneously models whether a protein sequence is active/ 1.6 °C. The procedure takes ∼1 h for gene assembly, 1 h for PCR, 3 h for
inactive and a continuous protein property of interest (Methods). protein expression, 3 h to measure thermostability, and 9 h overall to
We benchmarked our modeling approach on previously published go from a requested protein design to a physical protein sample to a
cytochrome P450 data consisting of 331 inactive sequences and 187 corresponding data point.
active sequences with thermostability labels21,22. The multi-output GP We added multiple layers of exception handling and data qual-
showed excellent predictive ability with an 83% active/inactive clas- ity control to further increase the reliability of the SAMPLE platform
sification accuracy and, for the subset of sequences that are active, (Fig. 1f). The system checks whether (1) the gene assembly and PCR
predicts the thermostability with r = 0.84 (Fig. 1b). has worked by assaying double-stranded DNA with EvaGreen, (2) the
The GP model trained on sequence–function data represents enzyme reaction progress curves look as expected, and the activity as a
the SAMPLE agent’s current knowledge, and, from here, the agent function of temperature can be fit using a sigmoid function, and (3) the
must decide which sequences to evaluate next to achieve the protein observed enzyme activity is above the background hydrolase activity
Fig. 1 | SAMPLE is a fully autonomous system for protein engineering. maximum observed thermostability for a given number of sequence evaluations,
a, SAMPLE consists of an intelligent agent that learns sequence–function averaged over 10,000 simulated protein engineering trials. d, The number of
relationships and designs proteins to test hypotheses. The agent sends designed evaluations needed for the design strategies to discover sequences within 90%
proteins to a laboratory environment that performs fully automated gene of the maximum thermostability (>61.9 °C) using 10,000 simulated protein
assembly, protein expression and biochemical characterization, and sends engineering trials. e, The reproducibility of the fully automated gene assembly,
the resulting data back to the agent, which refines its understanding of the protein expression and thermostability characterization pipeline on four diverse
system and repeats the process.b, The multi-output GP model classifies active/ GH1 enzymes from Streptomyces species. The curves’ small shoulder centered
inactive P450s with 83% accuracy and predicts P450 thermostability with around 60 °C is the result of background enzyme activity present in the E. coli
r = 0.84 using tenfold cross-validation. c, The performance of four sequential cell extracts. f, The pipeline has multiple layers of exception handling and data
design strategies using P450 sequence–function data. The lines show the quality control for failed experimental steps.
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 98

---

<!-- Page 3 -->

Article https://doi.org/10.1038/s44286-023-00002-4
from the cell-free extracts. Failure at any one of these checkpoints will Combinatorial sequence spaces to sample protein landscapes
flag the experiment as inconclusive and add the sequence back to the The SAMPLE platform searches a large and diverse protein sequence
potential experiment queue. space by assembling unique combinations of pre-synthesized DNA
Actions: designed
proteins to test
Percepts: fitness of
designed proteins
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 99
ytivitca
emyzne
laudiseR
Bgl3 (UniProt: Q59976) GH1 (UniProt: A0A0N0AST4) GH1 (UniProt: A0A1V9KJG2) GH1 (UniProt: A0A1K2FS28)
Rep1 T = 49.8 °C Rep1 T = 36.3 °C Rep1 T = 38.5 °C Rep1 T = 42.8 °C
1.0 50 50 50 50
Rep2 T = 51.1 °C Rep2 T = 36.9 °C Rep2 T = 39.3 °C Rep2 T = 43.3 °C
50 50 50 50
Rep3 T = 50.5 °C Rep3 T = 37.0 °C Rep3 T = 39.2 °C Rep3 T = 43.7 °C
50 50 50 50
0.8
0.6
0.4
0.2
0
20 30 40 50 60 70 80 20 30 40 50 60 70 80 20 30 40 50 60 70 80 20 30 40 50 60 70 80
Temperature (°C) Temperature (°C) Temperature (°C) Temperature (°C)
)C°(
ytilibatsomreht
.xam
egarevA
64
62
60
58
56
54
52
50
0 10 20 30 40 50 60
No. of sequences evaluated
ytisneD
2.0
1.5
1.0
0.5
0
1 10 100 1,000
Measured thermostability (°C) No. of sequence evaluations
needed to reach 90% of maximum
)C°(
ytilibatsomreht
detciderP
a
Agent Environment
Design proteins to
Presynthesized Assembly of DNA explore/exploit landscape DNA fragments fragments
DNA amplification
Bayesian optimization to efficiently discover proteins Self-driving
P(landscape|data) autonomous
machines for
protein
landscape
exploration
Data quality control
and filtering Biochemical Cell-free
expression
characterization
Temperature (°C)
b c d
65 Maximum thermostability Median = 26 Median = 83
Random Median = 26
UCB
60 T P h ea e r r s m o o n stability 90% of maximum U Ex C p B e c p t o e s d it i U v C e B
r = 0.84
55
50
45 Median = 108
Active/inactive
classification 40 accuracy = 0.83
FP = 0.08 TP = 0.27 Random
TN = 0.56 FN = 0.09 UCB
Inactive UCB positive
Expected UCB
Inactive 40 45 50 55 60 65
ytivitca
emyznE
Infer sequence-function
landscape from data
UCB optimal
sequence
Golden Gate
gene assembly
Designed gene fragments
addressable in 96-well plates
Update sequence-
function database
10
8
6
4
2
E e an x n p d zy r a e m l s l e s a i o s s e s n o q , c u a i c e a t n t i e v c d i e t y , m , s e t t a a b d i a li t t a y 0 00 0 1.. .. . 0 0 64 8 2 2030405 01 0 .0.8 60 70 8 4 0 05 0 0 1..08 6070 8 4 0 05060 70 80 S e b n u a z c c y k c m g e r s e o s u f a u n c l d t g iv , e i a t n n y e d a a b c s o u s v r e v e m e b fi l t y t , i ng 0 te E m nz p 3 y 0 e m ra 4 e 0 tu a 5 r c e 0 t i i v 6 n i 0 c ty u 7 b 0 a a ft 8 t e i 0 o r n E. coli extracts
e
f
Success Enzyme activity Yes Thermostability
above background Yes value
Success E a n s z s y a m y e No Success ab E o n v z e y m ba e c a k c g t r i o vi u ty nd
Fail
S r e e q q u u e e n s c t e as G se e m ne bly Fail Add to s U eq C u B e q n u c e e u b e ack Success E a n s z s y a m y e No I e n n a z c y t m iv e e
Gene
Retry assembly Fail
Fail

---

<!-- Page 4 -->

Article https://doi.org/10.1038/s44286-023-00002-4
a
P1F0 P1F1 P1F2 P1F3
P2F0 P2F1 P2F2 P2F3
P3F0 P3F1 P3F2 P3F3
P4F0 P4F1 P4F2 P4F3
P5F0 P5F1 P5F2 P5F3
P6F0 P6F1 P6F2 P6F3
Start Stop
PRF5
PRF4 PRF8 PRF6
PRF7
PCF5
PCF4 PCF8 PCF6
PCF7
b c
Pairwise Hamming distance
fragments. Combinatorial sequence spaces leverage exponential scal- three sequences per round, and ran for a total of 20 rounds (Fig. 3a).
ing to broadly sample the protein fitness landscape from a limited set The four agents’ optimization trajectories showed a gradual climb of
of gene fragments. We define a combinatorial sequence space using the landscape, with early phases characterized by exploratory behavior
a DNA assembly graph that specifies which sequence elements can and later rounds consistently sampling thermostable designs. There
be joined to generate a valid gene sequence (Fig. 2a). We designed a were two instances where the quality filters missed faulty data and
glycoside hydrolase (GH1) combinatorial sequence space composed incorrectly assigned a thermostability value to an inactive sequence
of sequence elements from natural GH1 family members, elements (Agent 1 in round 10 and Agent 3 in round 5). We intentionally did not
designed using Rosetta26, and elements designed using evolutionary correct these erroneous data points to observe how the agents recover
information27. The fragments were designed to sample broad sequence from the error as they acquire more landscape information. There
diversity and were not intended to target or enhance a particular func- were a large number of inconclusive experiments as noted by question
tion (for example, thermostability). All designed sequence fragments marks along the bottom of Fig. 3a. A majority of these were the result
are provided in Supplementary Data 5. The full combinatorial sequence of inactive enzymes that the agent must test twice to assign as inactive
space contains 1,352 unique GH1 sequences that differ by 116 muta- (Fig. 1f). Approximately 9% of the experiments failed, presumably due
tions on average and by at least 16 mutations (Fig. 2b). The sequences to liquid-handing errors.
introduce diversity throughout the GH1 TIM barrel fold and sample up Each agent discovered GH1 sequences that were at least 12 °C
to six unique amino acids at each site (Fig. 2c). more stable than the six initial natural sequences. The agents identify
these sequences while searching less than 2% of the full combinatorial
Autonomous cloud-based design of glycoside hydrolases landscape. We visualized the agents’ search trajectory and found that
We applied SAMPLE with the goal of navigating and optimizing the GH1 each agent broadly explored the sequence space before converging
thermostability landscape. We implemented our experimental pipeline on the same global fitness peak (Fig. 3b). All four agents arrived at
on the Strateos Cloud Lab for enhanced scalability and accessibility by similar regions of the landscape, but the top sequence discovered
other researchers28. We deployed four independent SAMPLE agents that by each agent was unique. The thermostable sequences tended to be
were each seeded with the same six natural GH1 sequences. The agents composed of the P6F0, P1F2 or P5F2, and P1F3 gene fragments, suggest-
designed sequences according to the Expected UCB criterion, chose ing the corresponding amino-acid segments may contain stabilizing
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 100
)000,1×(
ytisneD
Natural
sequence
fragments
Rosetta-
designed
fragments
Evolution-
designed
fragments
Mode = 137
20 No. of unique
amino acids sampled
6
Mean = 116
15
5
10 4
3
5
Max. =
Min. = 16 169 2
0 1
20 60 100 140 180
Fig. 2 | GH1 combinatorial sequence space. a, A DNA assembly graph defines designed GH1 sequence space differ by 116 amino-acid substitutions on average
which sequence elements have compatible overhangs and can be joined to and by at least 16 amino acids. c, Sequences within this space sample amino-acid
produce a valid gene sequence. Any path from the Start codon to the Stop codon diversity across the protein structure. Sampling diversity is scattered across
(for example, the red line) is a full gene sequence that can be assembled using the protein structure and not focused on a particular domain. The structural
Golden Gate cloning. Our GH1 sequence space has a total of 1,352 paths from illustration is adapted from Protein Data Bank ID 1GNX (β-glucosidase from
Start to Stop representing unique protein sequences. b, Sequences within the Streptomyces sp).

---

<!-- Page 5 -->

Article https://doi.org/10.1038/s44286-023-00002-4
60
50
40
30
Inactive
residues and/or interactions. We believe the agents have identified the as the ‘unified landscape model’ (Supplementary Fig. 4). We analyzed
global fitness peak of the 1,352-member combinatorial sequence space, how each agent’s landscape perception correlates with the unified land-
because all four agents converged to the same peak, and a GP model scape model and found agents’ understanding became progressively
trained on all data collected by all agents (the unified landscape model refined and improved as they acquired sequence–function information
discussed in the following section) predicts top sequences similar to (Fig. 4b). Notably, most agents discovered thermostable sequences
those discovered by the agents. by rounds 11 or 12, when their understanding of the landscape was
The agents’ search trajectory and landscape ascent varied sub- still incomplete, as indicated by a moderate Pearson correlation of
stantially, despite being seeded with the same six sequences and fol- ∼0.5. We also analyzed the different agents’ degree of agreement on
lowing identical optimization procedures. Agent 3 found thermostable the underlying landscape structure (Fig. 4c). All four agents started
sequences by round 7, whereas Agent 1 took 17 rounds to identify with correlated landscape perceptions because they were initialized
similarly stable sequences. Agent 2 did not discover any functional from the same six sequences, but the landscape consistency quickly
sequences until round 8. The divergence in behaviors can be traced dropped, with some agents even displaying negative correlations. The
to the first decision-making step, where the four agents designed early disagreement arose because each agent pursued a unique search
different sequences to test in round 1. These initial differences arose trajectory and thus specialized on different regions of the landscape.
due to experimental noise in characterizing the six seed sequences, The correlation between agents’ perceived landscapes eventually
which gave rise to slightly different landscape models that altered increased as more information was acquired. Again, it is notable how
each agent’s subsequent decisions. The stochastic deviation between the agents tended to discover thermostable sequences by rounds 11–12,
agents propagated further over the rounds to produce highly varied while largely disagreeing on the full landscape structure. BO algorithms
landscape searches, but these were ultimately steered back to the same are efficient because they focus on understanding the fitness peaks,
global fitness peak. while devoting less effort to regions known to be suboptimal. After
round 20, we found the four agents were more confident on the top
SAMPLE agents actively acquire landscape information thermostable sequences and had greater uncertainty associated with
SAMPLE agents efficiently and robustly discovered thermostable GH1 lower fitness regions of the landscape (Fig. 4d).
enzymes. We analyzed the four agents’ internal landscape perception The SAMPLE agents designed sequences according to the expected
and decision-making behavior to reveal how they navigate the protein UCB criterion, which considers the thermostability prediction, the
fitness landscape. We plotted each agent’s model predictions for all 1,352 model uncertainty and the probability an enzyme is active (P ). We
active
combinatorial sequences over the course of the optimization (Fig. 4a). wanted to understand the interplay of these three factors and how they
The agents’ perception of the landscape changed over time, and impor- influenced each agent’s decision-making. We looked at the sequences
tant events, such as observing new stable sequences or erroneous data chosen in each round and their percentile rank for thermostability pre-
points, resulted in large landscape reorganization, as indicated by the diction, model uncertainty and P (Fig. 4e). The agents prioritized
active
crossing lines in Fig. 4a. Many eventual top sequences were ranked near the thermostability prediction throughout the optimization, and
the bottom in early rounds. tended to sample uncertain sequences in early phases, while emphasiz-
To obtain an estimated ‘ground truth’ landscape, we trained a GP ing P in the later phases. Agent 3 prioritized P earlier than the
active active
model on all sequence–function data from all agents, which we refer to other agents, which seems to be the result of discovering thermostable
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 101
)C°(
ytilibatsomrehT
Agent 1 Agent 2 Agent 3 Agent 4
Bayesian optimization round
noitazilausiv
hcraes
epacsdnaL
a
S 2 4 6 8 10 12 14 16 18 20 S 2 4 6 8 10 12 14 16 18 20 S 2 4 6 8 10 12 14 16 18 20 S 2 4 6 8 10 12 14 16 18 20
Inconclusive experiment, retry Inactive enzyme Thermostability value Thermostable enzyme (>10 °C)
b
Predicted
thermostability
Fig. 3 | Autonomous exploration of the GH1 landscape. a, Protein optimization the landscape search. The 1,352 possible sequences were arranged using
trajectories of four independent SAMPLE agents. Inconclusive experiments, multidimensional scaling and colored according to their predicted
defined as in Fig. 1f, are marked with a ‘?’. There were two instances of inactive thermostability from the unified landscape model. The center left yellow cluster
sequences that were incorrectly classified as active enzymes with thermostability corresponds to the landscape’s fitness peak. The search trajectory is plotted as
values (Agent 1 in round 10 and Agent 3 in round 5). b, Visualization of the most stable sequence from each round.

---

<!-- Page 6 -->

Article https://doi.org/10.1038/s44286-023-00002-4
a
Agent 1 Agent 2 Agent 3 Agent 4
0 2 4 6 8 10 12 14 16 18 0 2 4 6 8 10 12 14 16 18 0 2 4 6 8 10 12 14 16 18 0 2 4 6 8 10 12 14 16 18
Bayesian optimization round
sequences early and putting less emphasis on exploration. We also is dictated by its large P range, and Agent 2’s is determined by its
active
analyzed the agents’ final perception of thermostability, P and predicted thermostability. Meanwhile, Agent 3 still has considerable
active
expected UCB, and found the agents specialized on different factors landscape uncertainty, as indicated by the high expected UCB points
resulting from their past experiences (Fig. 4f). Agent 4’s expected UCB with moderate thermostability and P predictions.
active
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 102
)C°(
weiv
epacsdnal
s’tnegA
60
50
40
30
20
Bayesian optimization round Bayesian optimization round Bayesian optimization round
evitca
ytilibaborp
detciderP
1.0 A1–A2 A1–A3 A1–A4
A2–A3 A2–A4 0.8 A3–A4
0.6
0.4
0.2
0
–0.2
–0.4
0 2 4 6 8 10 12 14 16 18 20
Bayesian optimization round
f
0.8 0.8 0.8 0.8
0.6 0.6 0.6 0.6
Expected
UCB
0.4 0.4 0.4 0.4 30
0.2 0.2 0.2 0.2
0
20 40 60 20 40 60 20 40 60 20 40 60
Predicted thermostability (°C) Predicted thermostability (°C) Predicted thermostability (°C) Predicted thermostability (°C)
neewteb
noitalerroc
nosraeP
sepacsdnal
detciderp
’stnega
c
0.8
0.6
0.4
0.2
0
0 2 4 6 8 10 12 14 16 18 20
Bayesian optimization round
htiw
noitalerroc
nosraeP
ledom
epacsdnal
deifinu
b d
Agent 1
Agent 2 Agent 3 10
Agent 4
8
6
4
2
25 30 35 40 45 50 55 60
ytniatrecnu
epacsdnal
egarevA
)C°
,σ
PG(
02
dnuor
ta
Thermostable enzyme Thermostable enzyme Thermostable enzyme
Other sequences Other sequences Other sequences Other sequences
A1 A2 A3 A4
Unified landscape model T (°C)
50
e
Agent 1 Agent 2 Agent 3 Agent 4
0 2 4 6 8 10 12 14 16 18 0 2 4 6 8 10 12 14 16 18 0 2 4 6 8 10 12 14 16 18 0 2 4 6 8 10 12 14 16 18
Bayesian optimization round
Agent 1 Agent 2 Agent 3 Agent 4
fo
knar
elitnecreP
secneuqes
nesohc
Thermostable enzyme
1.0
0.8
Expected UCB
GP stability
0.6 GP uncertainty
GP P
active
0.4
0.2
0
Bayesian optimization round Bayesian optimization round Bayesian optimization round
Fig. 4 | SAMPLE agents’ landscape search behavior. a, Agents’ landscape T range predicted by the unified landscape model. e, The chosen sequences’
50
perception over the course of the optimization. The light gray lines show the percentile ranks for four key factors: the expected upper confidence bound
agents’ thermostability predictions for all 1,352 sequences, and the bold colored (expected UCB), the thermostability model’s mean prediction (GP stability),
lines show sequences that were ultimately discovered to be thermostable by each the thermostability model’s predictive uncertainty (GP uncertainty) and the
agent. b, Pearson correlation between the agents’ predicted thermostability active/inactive classifier’s predicted probability a sequence is active (P ).
active
landscape and the unified landscape model that incorporates all data The percentile ranks were averaged over the three sequences in the batch.
retrospectively. c, Pearson correlation between different agents’ thermostability A percentile rank approaching one indicates the chosen sequences were
landscapes over the course of the optimization. d, Average model uncertainty exceptional for a given factor. f, The agents’ view of the landscape after the 20
as a function of the landscape thermostability. The GP uncertainty (sigma) was rounds of optimization, with expected UCB overlaid to highlight which factors
averaged over all sequences falling within a 10 °C sliding window across the full are contributing to the expected UCB.

---

<!-- Page 7 -->

Article https://doi.org/10.1038/s44286-023-00002-4
Human characterization of machine-designed proteins pause caused by shipping delays. Even this six-month duration com-
The SAMPLE system was given a protein engineering objective, rea- pares favorably to human researchers, which we estimate may take
gents and DNA components, and autonomously proceeded to search 6–12 months to perform similar experiments using standard molecular
the fitness landscape and discover thermostable GH1 enzymes. We biology and protein engineering workflows. Learning from previous
experimentally characterized the top sequence discovered by each delays, and with better planning, we estimate that SAMPLE could per-
agent to validate the SAMPLE system’s findings using standard human form 20 design–test–learn cycles in two months using the Strateos
protocols. We expressed the enzymes in Escherichia coli and performed Cloud Lab. We estimate the cost to perform a SAMPLE run of 20 rounds
lysate-based thermostability assays (Methods). We found that all four with a batch size of 3 is US$5,200 (US$2,400 for the DNA fragments,
machine-designed enzymes were substantially more thermostable US$1,300 for all the reagents and US$1,500 for the Strateos Cloud Lab).
than the top natural sequence (Bgl3), and the designs from Agents 1 We deployed four identical SAMPLE agents and observed nota-
and 4 were nearly 10 °C more stable (Fig. 5a). The human-measured ble differences in their search behavior and landscape optimization
thermostability values and thermostability differences were not as efficiency. The agents explored distinct regions of sequence space,
large as observed using our automated experimental set-up, which is a specialized on different tasks such as classifying active/inactive
result of the different protein expression and assay conditions. We also enzymes versus predicting thermostability, and Agent 3 discovered
tested the enzymes’ Michaelis–Menten kinetic properties and found thermostable enzymes with ten fewer rounds than Agent 1. The initial
that all designs displayed similar reaction kinetics with wild-type Bgl3 divergence in behavior arises from experimental measurement noise,
(Fig. 4b) and the other wild-type input sequences (Supplementary Fig. which influences the agents’ decisions, which then further propagates
5). Our protein engineering search did not explicitly consider reaction differences between agents. There is also an element of luck that is
kinetics, but it seems that the enzyme catalytic activity was maintained compounded with positive feedback: an agent may happen to search
by utilizing an activity-based thermostability assay. in a particular region and come across improved sequences, which then
drives the search upward in favorable directions. These observations
Discussion have interesting parallels with human researchers, where success or
Self-driving laboratories automate and accelerate the scientific dis- failure could be influenced by seemingly inconsequential experimental
covery process and hold great potential to revolutionize the fields of outcomes and the resulting decisions. The SAMPLE agents explored
protein engineering and synthetic biology. Automating the biological distinct regions of the landscape and specialized on unique tasks, which
design process remains challenging due to the scale and complexity of indicates a potential to coordinate multiple agents towards a single
biological fitness landscapes and the specialized operations required protein engineering goal. The decentralized and on-demand nature
for wet laboratory experiments. In this work we have developed the of cloud laboratory environments would further assist multi-agent
SAMPLE platform for fully autonomous protein engineering. SAM- coordination systems.
PLE tightly integrates automated learning, decision-making, protein Other research groups have developed automated pipelines
design and experimentation to explore fitness landscapes and dis- and semi-autonomous systems for biological systems engineering.
cover optimized proteins. We deployed SAMPLE agents with the goal Carbonell and colleagues developed an automated design–build–
of engineering glycoside hydrolase (GH1) enzymes with enhanced test–learn pipeline that searches over gene regulatory elements such
thermal tolerance. The agents efficiently and robustly searched the as promoters and operon configurations to optimize biosynthetic
landscape to identify thermostable enzymes that were at least 12 °C pathway titers14. They demonstrated their pipeline by performing two
more stable than the initial starting sequences. These gains are larger design–build–test–learn cycles to optimize flavonoid and alkaloid
than achieved in other GH1 thermostability engineering work using production in E. coli. Each step of this pipeline utilized automation,
Rosetta29 and high-throughput screening30. but the entire procedure was not fully integrated to enable autono-
SAMPLE is a general protein engineering platform that can be mous operation. HamediRad and colleagues developed an automated
broadly applied to diverse protein engineering targets and functions. design–build–test–learn system to optimize biosynthetic pathways by
Although we only demonstrated thermostability engineering, the same searching over promoters and ribosome binding sites15. They applied
general approach could engineer enzyme activity, specificity and even their system to enhance lycopene production in E. coli and performed
new-to-nature chemical reactions. Like directed evolution, the system three design–build–test–learn cycles. The most notable difference
does not require prior knowledge of protein structure or mechanism, between SAMPLE and these earlier demonstrations is SAMPLE’s high
but instead takes an unbiased approach that examines how sequence level of autonomy, which allowed us to perform four independent tri-
changes impact function. The greatest barrier to establishing SAM- als of 20 design–test–learn cycles each. High autonomy enables more
PLE for a new protein function is the required biochemical assay. The experimental cycles without the need for slow human intervention.
robotic systems used in this work had access to a microplate reader and The protein engineering set-up for this initial SAMPLE demon-
thus required a colorimetric or fluorescence-based assay. In principle, stration was relatively simple compared to most directed evolution
more advanced analytical instruments, such as liquid chromatography- campaigns. First, the search space of 1,352 is small and, for some assays,
mass spectrometry or NMR spectroscopy, could be integrated into could be fully evaluated using high/medium-throughput screening.
automation systems to expand the types of protein functions that could The size the combinatorial sequence space is determined by the num-
be engineered. Finally, we implemented our full experimental pipeline ber of gene fragments (in our case we used 34) and could be scaled
on the Strateos Cloud Lab to produce a cost-effective and accessible massively using oligonucleotide pools. Even a small pool of 1,000 oli-
system that can be adopted by other synthetic biology researchers. gos could be split into 250 fragment options for four segments across
SAMPLE has the potential to streamline and accelerate the process a gene and could be assembled into nearly four billion (2504) unique
of protein engineering. The experimental side of the system is the major sequences. Another simple aspect of our SAMPLE demonstration was
throughput bottleneck that limits the overall process. A single round the thermostability engineering goal. Protein thermostability is fairly
of experimental testing takes 9 h on our Tecan automation system well understood and there are already computational tools to predict
or 10 h split over two days (5 h × 2 days) on the Strateos Cloud Lab. At stabilizing mutations with moderate success. SAMPLE is certainty not
these rates, with continuous operation, the system could get through restricted to thermostability, and similar classes of machine learning
20 design–test–learn cycles in just 1–2 weeks. In practice, the process models have been used to model complex protein properties such as
was much slower due to system downtime, robotic malfunctions and enzyme activity20, substrate specificity, light sensitivity of channelrho-
time needed for restocking reagents. Our 20 rounds of GH1 optimiza- dopsins31, in vivo titer in metabolic pathways32 and adeno-associated
tion took just under six months, which included a single 2.5-month virus capsid viability33, among others. Our initial work demonstrates
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 103

---

<!-- Page 8 -->

Article https://doi.org/10.1038/s44286-023-00002-4
which the agent can then systematically explore to refine mechanistic
1.2 understanding and discover new molecular behaviors. This human–
T (°C) ∆T (°C)
50 50 robot collaboration would combine human intuition and creativity
1.0
WT Bgl3 (1111) 44.7 0.0 with intelligent autonomous systems’ ability to execute experiments,
0.8 Agent 1 (6151) 54.6 9.9 interpret data and efficiently search large hypothesis spaces, leading
to rapid progress in molecular design and discovery.
0.6 Agent 2 (6251) 53.0 8.3
The powerful combination of artificial intelligence and automa-
0.4 Agent 3 (6311) 50.9 6.2 tion is disrupting nearly every industry, from manufacturing and
Agent 4 (6511) 54.6 9.9 food preparation to pharmaceutical discovery, agriculture and waste
0.2
management. Self-driving laboratories will revolutionize the fields
0 of biomolecular engineering and synthetic biology by automating
40 45 50 55 60 65 70 75 highly inefficient, time-consuming and laborious protein engineering
Temperature (°C) campaigns, enabling rapid turnaround and allowing researchers to
focus on important downstream applications. Intelligent autonomous
systems for scientific discovery will become increasingly powerful
with continued advances in deep learning, robotic automation and
k K k /K (s c – a 1 t ) (µM M ) (M ca – t 1s– M 1) high-throughput instrumentation.
WT Bgl3 (1111) 10.7 76 1.4 × 105
Methods
Agent 1 (6151) 7.6 214 3.6 × 104
Benchmarking BO methods on P450 data
Agent 2 (6251) 5.1 204 2.5 × 104 We compiled a cytochrome P450 dataset to benchmark the modeling
Agent 3 (6311) 9.6 107 9.0 × 104 and BO methods. The dataset consists of 518 data points with binary
Agent 4 (6511) 11.0 133 8.2 × 104 active/inactive data from ref. 22 and thermostability measurements
from ref. 21. We tested the multi-output GP model by performing ten-
fold cross-validation, where a GP classifier was trained on binary active/
inactive data and a GP regression model was trained on thermostability
data. The models used a linear Hamming kernel (sklearn36 DotProduct
with sigma_0 = 1) with an additive noise term (sklearn WhiteKernel
noise_level = 1). For the test-set predictions, we categorized sequences
as either true negative (TN), false negative (FN), false positive (FP) or
true positive (TP), and for true positives we calculated the Pearson
correlation between predicted thermostability and true thermosta-
bility values.
We used the cytochrome P450 data to benchmark the BO methods.
The random method randomly selects a sequence from the pool of
untested sequences. The UCB method chooses the sequence with the
largest upper confidence bound (GP thermostability model mean + 95%
prediction interval) from the pool of untested sequences. The UCB
method does not have an active/inactive classifier and, if it observes
an inactive sequence, it does not update the GP regression model.
The UCB positive method incorporates the active/inactive classifier
a generalizable protein engineering platform whose scope and power and only considers the subset of sequences that are predicted to be
will continuously expand with future development. active by the GP classifier (P > 0.5). From this subset of sequences
active
It was notable that our combinatorial sequence space consisted of it selects the sequence with the top UCB (GP thermostability model
natural-sequence, Rosetta-designed and evolution-design fragments, mean + 95% prediction interval) value. The expected UCB method takes
but the top designs were composed purely of natural sequence ele- the expected value of the UCB score by (1) subtracting the minimum
ments. The agents collectively tested seven designs with Rosetta- or value from all thermostability predictions to set the baseline to zero,
evolution-designed fragments, and only two showed any enzyme (2) adding the 95% prediction interval and (3) multiplying by the active/
activity, with very low thermostability. Our unified landscape model inactive classifier P . The sequence with the top expected UCB value
active
(Supplementary Fig. 4) predicts most of these designed fragments is chosen from the pool of untested sequences.
to negatively impact the probability an enzyme is active (P ), ther- We tested the performance of these four methods by running
active
mostability, or both. These fragments probably failed because the 10,000 simulated protein engineering trials using the cytochrome
designs were too aggressive by introducing many sequence changes. P450 data. For each simulated protein engineering trial, the first
Future work could focus on more conservative designs with two to five sequence was chosen randomly, and subsequent experiments were
mutations per fragment and the latest protein design methods (such chosen according to the different BO criteria. A trial’s performance
as ProteinMPNN34). at a given round is the maximum observed thermostability from that
Our combinatorial sequence space was designed to generate round and all prior rounds. We averaged each performance profile over
sequence diversity in a function-agnostic manner, but we see great the 10,000 simulated trials.
future potential of using more advanced design algorithms to tailor We also developed and tested batch methods that select multiple
the sequence space toward desired molecular functions. CADENZ is sequences each round. For the batch methods we use the same UCB
a recent atomistic and machine learning design approach to gener- variants described above to choose the first sequence in the batch,
ate diverse, low-energy enzymes for combinatorial assembly of gene then we update the GP model assuming the chosen sequence is equal
fragments35 and would readily integrate with SAMPLE’s gene assembly to its predicted mean, and then we select the second sequence accord-
procedure. SAMPLE’s sequence space design provides an opportu- ing to the specified UCB criteria. We continue to select sequences and
nity for humans to propose multiple different molecular hypotheses, update the GP model until the target batch size is met. We assessed
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 104
ytivitca
emyzne
dezilamroN
) 1– s(
]emyznE[/yticolev
noitcaer
laitinI
a
b
10
8
6
4
2
0
0 100 200 300 400 500
[Substrate] (µM)
Fig. 5 | Thermostability and kinetic properties of the designed GH1s.
a, Enzyme inactivation as a function of temperature. Each measurement was
performed in quadruplicate, and shifted sigmoid functions were fit to the average
over replicates. The T parameter is the midpoint of the sigmoid function and is
50
defined as the temperature where 50% of the enzyme is irreversibly inactivated
in 10 min. The enzyme variant is specified by the sequence of its four constituent
fragments, for example 6151 corresponds to P6F0-P1F1-P5F2-P1F3. b, Enzyme
reaction velocity as a function of substrate concentration. Each measurement
was performed in triplicate, and the Michaelis–Menten equation was fit to the
average over replicates to determine the kinetic constants. Bgl3 is the most active
wild-type input sequence, and the kinetics for the other wild-type sequences are
provided in Supplementary Fig. 5

---

<!-- Page 9 -->

Article https://doi.org/10.1038/s44286-023-00002-4
how the batch size affects performance by running 10,000 simulated PCR amplification of assembled genes. A 10-μl volume of the Golden
protein engineering trials at different batch sizes and evaluating how Gate assembly product was combined with 90 μl of the PCR primers
many learning cycles were needed to reach 90% of the maximum stock, and 10 μl of this mixture was then added to 10 μl Phusion 2X
thermostability. Master Mix. PCR was carried out with a 5-min melt at 98 °C, followed
by 35 cycles of 56 °C anneal for 30 s, 72 °C extension for 60 s, and 95 °C
Glycoside hydrolase combinatorial sequence space design melt for 30 s. This was followed by one final extension for 5 min at 72 °C.
We designed a combinatorial glycoside hydrolase family 1 (GH1)
sequence space composed of sequence elements from natural GH1 Verification of PCR amplification. A 10-μl volume of the PCR product
family members, elements designed using Rosetta26, and elements was combined with 90 μl of water, and 50 μl of this mixture was then
designed using evolutionary information27. The combinatorial combined with 50 μl 2× EvaGreen. The fluorescence of the sample was
sequence space mixes and matches these sequence elements to cre- read on a microplate reader (excitation, 485 nm; emission, 535 nm) and
ate new sequences. The sequences are assembled using Golden Gate the signal was compared to previous positive/negative control PCRs to
cloning and thus require common four-base-pair overhangs to facilitate determine whether PCR amplification was successful.
assembly between adjacent elements.
We chose six natural sequences by running a BLAST search on Cell-free protein expression. A 30-μl volume of the 10× PCR dilution
Bgl337 and selecting five additional sequences that fell within the from the previous step was added to 40 μl of AccuRapid E. coli extract
70–80% sequence identity range (Supplementary Fig. 3). We aligned and mixed with 80 μl of AccuRapid Master Mix. The protein expression
these six natural sequences and chose breakpoints using SCHEMA reaction was incubated at 30 °C for 3 h.
recombination38,39 with the wild-type Bgl3 crystal structure (PDB 1GNX).
The breakpoints for the Rosetta and evolution-designed sequence Thermostability assay. We used T measurements to assess GH1 ther-
50
fragments were chosen to interface with the natural fragments and mostability. T is defined as the temperature where 50% of the enzyme
50
also introduce new breakpoints to promote further sequence diversity. is irreversibly inactivated in 10 min and is measured by heating enzyme
For the Rosetta fragments, we started with the crystal structure of samples across a range of temperatures, evaluating residual enzyme
wild-type Bgl3 (PDB 1GNX), relaxed the structure using FastRelax, and activity, and fitting a sigmoid function to the temperature profile to
used RosettaDesign to design a sequence segment for a given fragment obtain the curve midpoint. T represents the fractional activity lost
50
while leaving the remainder of the sequence and structure as wild-type as a function of temperature and is therefore independent of absolute
Bgl3. At each position, we only allowed residues that were observed enzyme concentration and expression level.
within the six aligned natural sequences. For the evolution-designed A 70-μl volume of the expressed protein was diluted with 600 μl of
fragments, we used Jackhmmer40 to build a large family of multiple water, and 70-μl aliquots of this diluted protein were added to a column
sequence alignment and designed sequence segments containing the of a 96-well PCR plate for temperature gradient heating. The plate was
most frequent amino acid from residues that were observed within the heated for 10 min on a gradient thermocycler such that each protein
six natural sequences. The GH1 family’s active site involves a glutamic sample experienced a different incubation temperature. After incuba-
acid catalytic nucleophile around position 360 and a glutamic acid tion, 10 μl of the heated sample was added to 90 μl of the fluorogenic
general acid/base catalyst around position 180. As all fragments were substrate master mix and mixed by pipetting. The fluorescein internal
designed based on aligned sequences, these conserved active-site resi- standard was analyzed on a microplate reader (excitation, 494 nm;
dues will all fall within the same fragment position. The Glu nucleophile emission, 512 nm) for sample normalization, and the enzyme reaction
is present in blocks P1F3, P2F3, P3F3, P4F3, P5F3, P6F3, PrF6 and PcF6. progress was monitored by analyzing the sample fluorescence (excita-
The Glu general acid/base is present in blocks P1F1, P2F1, P3F1, P4F1, tion, 372 nm; emission, 445 nm) every 2 min for an hour. Any wells with
P5F1, P6F1, PrF4, PcF4, PrF5 and PcF5. fluorescein fluorescence less than 20% of the average for a given run
We designed DNA constructs to assemble sequences from the com- were assumed to reflect pipetting failure and were not considered when
binatorial sequence space using Golden Gate cloning. The designed fitting a thermostability curve.
amino-acid sequence elements were reverse-translated using the Twist
codon optimization tool, and the endpoints were fixed to preserve the Human characterization of top designed enzymes
correct Golden Gate overhangs. We added BsaI sites to both ends to Bacterial protein expression and purification. The designs were
allow restriction digestion and ordered the 34 gene fragments cloned built using Golden Gate cloning to assemble the constituent gene
into the pTwist Amp High Copy vector. Each sequence element’s amino fragments, and the full gene was cloned into the pET-22b expression
acid and gene sequence are given in Supplementary Data 5. plasmid. The assemblies were transformed into E. coli DH5α cells and
the gene sequences were verified using Sanger sequencing. The plas-
Automated gene assembly, expression and characterization mids were then transformed into E. coli BL21(DE3) and preserved as
We implemented our fully automated protein testing pipeline on an glycerol stocks at −80 °C. The glycerol stocks were used to inoculate an
in-house Tecan liquid-handling system and the Strateos Cloud Lab. The overnight Luria broth (LB) starter culture and the next day this culture
system was initialized with a plate of the 34 gene fragments (5 ng μl−1), was diluted 100× into a 50-ml LB expression culture with 50 μg ml−1
an NEB Golden Gate Assembly Kit (E1601L) diluted to a 2× stock solu- carbenicillin. The culture was incubated while shaking at 37 °C until
tion, a 2 μM solution of forward and reverse PCR primers, Phusion the optical density at 600 nm reached 0.5–0.6 and then induced with
2X Master Mix (ThermoFisher F531L), 2× EvaGreen stock solution, 1 mM isopropyl β-d-1-thiogalactopyranoside. The expression cultures
Bioneer AccuRapid Cell Free Protein Expression Kit (Bioneer K-7260) were incubated while shaking overnight at 16 °C, and the next day
Master Mix diluted in water to 0.66×, AccuRapid E. coli extract with the cultures were collected by centrifugation at 3,600g for 10 min,
added 40 μM fluorescein, a fluorogenic substrate master mix (139 μM discarding the supernatant. The cell pellets were resuspended in 5 ml
4-methylumbelliferyl-α-d-glucopyranoside, 0.278% vol/vol dimethyl- of phosphate-buffered saline and lysed by sonication at 22 W for 20
sulfoxide (DMSO), 11 mM phosphate and 56 mM NaCl, pH 7.0) and water. cycles of 5 s on and 15 s off. The lysates were clarified by centrifugation
at 10,000g for 15 min.
Golden Gate assembly of DNA fragments. For a given assembly, 5 μl The enzymes were purified by loading the clarified lysates
of each DNA fragment were mixed and 10 μl of the resultant mixture was onto a Ni-NTA agarose column (Cytiva 17531801), washing with
then combined with 10 μl of 2× Golden Gate Assembly Kit. This reaction 20 ml of wash buffer (25 mM Tris, 400 mM NaCl, 20 mM imidazole,
mix was heated at 37 °C for 1 h, followed by a 5-min inactivation at 55 °C. 10% vol/vol glycerol, pH 7.5) and eluting with 5 ml of elution buffer
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 105

---

<!-- Page 10 -->

Article https://doi.org/10.1038/s44286-023-00002-4
(25 mM Tris, 400 mM NaCl, 250 mM imidazole, 10% vol/vol glycerol, 3. King, R. D. et al. Functional genomic hypothesis generation and
pH 7.5). The eluted samples were concentrated using an Amicon filter experimentation by a robot scientist. Nature 427, 247–252 (2004).
concentrator and concurrently transitioned to storage buffer (25 mM 4. Caramelli, D. et al. Discovering new chemistry with an
Tris, 100 mM NaCl, 10% vol/vol glycerol, pH 7.5). The final protein con- autonomous robotic platform driven by a reactivity-seeking
centration was determined using the Bio-Rad protein assay, the sam- neural network. ACS Cent. Sci. 7, 1821–1830 (2021).
ples were diluted to 2 mg ml−1 in storage buffer, and frozen at −80 °C. 5. Abolhasani, M. & Kumacheva, E. The rise of self-driving labs in
chemical and materials sciences. Nat. Synth 2, 483–492 (2023).
Thermostability assay. The clarified cell lysate from the protein 6. Volk, A. A. et al. AlphaFlow: autonomous discovery and
expression was diluted 100× in phosphate-buffered saline, then 100 μl optimization of multi-step chemistry using a self-driven fluidic lab
of the diluted lysate was arrayed into a 96-well PCR plate and heated guided by reinforcement learning. Nat. Commun. 14, 1403 (2023).
for 10 min on a gradient thermocycler from 40 °C to 75 °C. The heated 7. Burger, B. et al. A mobile robotic chemist. Nature 583, 237–241
samples were assayed for enzyme activity in quadruplicate with final (2020).
reaction conditions of 10% heated lysate, 125 μM 4-methylumbelliferyl- 8. Langner, S. et al. Beyond ternary OPV: high-throughput
β-d-glucopyranoside, 0.125% vol/vol DMSO, 10 mM phosphate buffer experimentation and self-driving laboratories optimize
pH 7 and 50 mM NaCl. The reaction progress was monitored using a multicomponent systems. Adv. Mater. 32, 1907801 (2020).
microplate reader analyzing sample fluorescence (excitation, 372 nm; 9. Li, R. et al. A self-driving laboratory designed to accelerate the
emission, 445 nm) every 2 min for 30 min. The reaction progress curves discovery of adhesive materials. Digit. Discov. 1, 382–389 (2022).
were fit using linear regression to obtain the reaction rate, and a shifted 10. MacLeod, B. P. et al. Self-driving laboratory for accelerated
sigmoid function was fit to the rate as a function of temperature incuba- discovery of thin-film materials. Sci. Adv. 6, eaaz8867 (2020).
tion to obtain the T value. 11. Beal, J. & Rogers, M. Levels of autonomy in synthetic biology
50
engineering. Mol. Syst. Biol. 16, e10019 (2020).
Michaelis–Menten kinetic assay. The purified enzymes were assayed 12. Martin, H. G. et al. Perspectives for self-driving labs in synthetic
in quadruplicate along an eight-point twofold dilution series of biology. Curr. Opin. Biotechnol. 79, 102881 (2023).
4-methylumbelliferyl-β-d-glucopyranoside starting from 500 μM. 13. Carbonell, P., Radivojevic, T. & García Martín, H. Opportunities
The assays were performed with 10 nM enzyme, 0.5% vol/vol DMSO, at the intersection of synthetic biology, machine learning and
10 mM phosphate buffer pH 7 and 50 mM NaCl. The reaction progress automation. ACS Synth. Biol. 8, 1474–1477 (2019).
was monitored using a microplate reader analyzing the sample fluores- 14. Carbonell, P. et al. An automated design-build-test-learn pipeline
cence (excitation, 372 nm; emission, 445 nm) every 2 min for 30 min. for enhanced microbial production of fine chemicals. Commun.
A standard curve of 4-methylumbelliferone (4MU) ranging from 3.91 to Biol. 1, 66 (2018).
62.5 μM was used to determine the assay’s linear range. The initial rate 15. HamediRad, M. et al. Towards a fully automated algorithm driven
for each reaction was determined by fitting a linear function to 4MU platform for biosystems design. Nat. Commun. 10, 5150 (2019).
fluoresence (excitation, 372 nm; emission, 445 nm) at 0-, 2- and 4-min 16. Romero, P. A. & Arnold, F. H. Exploring protein fitness landscapes
reaction times. The initial rate data were fit to the Michaelis–Menten by directed evolution. Nat. Rev. Mol. Cell Biol. 10, 866–876 (2009).
equation using the scikit-learn36 curve_fit function to determine the 17. Shahriari, B., Swersky, K., Wang, Z., Adams, R. P. & De Freitas,
enzyme k and K . N. Taking the human out of the loop: a review of Bayesian
cat M
optimization. Proc. IEEE 104, 148–175 (2016).
SAMPLE code execution 18. Hie, B. L. & Yang, K. K. Adaptive machine learning for protein
A detailed description of the software loop driving SAMPLE is provided engineering. Curr. Opin. Struct. Biol. 72, 145–152 (2022).
in the Supplementary Information under the heading Detailed descrip- 19. Thomas, N. & Colwell, L. J. Minding the gaps: the importance
tion of SAMPLE code functionality. of navigating holes in protein fitness landscapes. Cell Syst. 12,
1019–1020 (2021).
Materials availability 20. Romero, P. A., Krause, A. & Arnold, F. H. Navigating the protein
All plasmids used in this project are available upon request to fitness landscape with Gaussian processes. Proc. Natl Acad. Sci.
promero2@wisc.edu. USA 110, E193–E201 (2013).
21. Li, Y. et al. A diverse family of thermostable cytochrome P450s
Reporting summary created by recombination of stabilizing fragments.
Further information on research design is available in the Nature Nat. Biotechnol. 25, 1051–1056 (2007).
Portfolio Reporting Summary linked to this Article. 22. Otey, C. R. et al. Structure-guided recombination creates an
artificial family of cytochromes P450. PLoS Biol. 4, e112 (2006).
Data availability 23. Srinivas, N., Krause, A., Kakade, S. M. & Seeger, M. Gaussian
A more complete set of data including the code to interpret the data is process optimization in the bandit setting: no regret and
accessible at https://doi.org/10.5281/zenodo.10048592. Source data experimental design. In Proc. 27th International Conference on
are provided with this paper. Machine Learning 1015–1022 (ACM, 2010).
24. Auer, P. Using confidence bounds for exploitation-exploration
Code availability trade-offs. J. Mach. Learn. Res. 3, 397–422 (2002).
All code and the necessary data to run that code are accessible at 25. Engler, C., Kandzia, R. & Marillonnet, S. A one pot, one step,
https://doi.org/10.5281/zenodo.10048592. precision cloning method with high throughput capability. PLoS
ONE 3, e3647 (2008).
References 26. Alford, R. F. et al. The Rosetta all-atom energy function for
1. King, R. D. et al. The automation of science. Science 324, 85–89 macromolecular modeling and design. J. Chem. Theory Comput.
(2009). 13, 3031–3048 (2017).
2. Coutant, A. et al. Closed-loop cycles of experiment design, 27. Porebski, B. T., Buckle, A. M., By, E. & Daggett, V. Consensus
execution and learning accelerate systems biology model protein design. Protein Eng. Des. Sel. 29, 245–251 (2016).
development in yeast. Proc. Natl Acad. Sci. USA 116, 18142–18147 28. Arnold, C. Cloud labs: where robots do the research. Nature 606,
(2019). 612–613 (2022).
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 106

---

<!-- Page 11 -->

Article https://doi.org/10.1038/s44286-023-00002-4
29. Carlin, D. A. et al. Thermal stability and kinetic constants for 129 implemented the full experimental and computational system. J.T.R.
variants of a family 1 glycoside hydrolase reveal that enzyme performed all protein engineering runs and biochemistry. J.T.R. and
activity and stability can be separately designed. PLoS ONE 12, P.A.R. analyzed the data and wrote the manuscript, with feedback from
e0176255 (2017). B.J.B.
30. Romero, P. A., Tran, T. M. & Abate, A. R. Dissecting enzyme
function with microfluidic-based deep mutational scanning. Proc. Competing interests
Natl Acad. Sci. USA 112, 7159–7164 (2015). J.T.R., B.J.B. and P.A.R. have submitted a patent application on related
31. Bedbrook, C. N. et al. Machine learning-guided channelrhodopsin work with the Wisconsin Alumni Research Foundation (US patent
engineering enables minimally invasive optogenetics. Nat. application no. US20210074377A1).
Methods 16, 1176–1184 (2019).
32. Greenhalgh, J. C., Fahlberg, S. A., Pfleger, B. F. & Romero, P. A. Additional information
Machine learning-guided acyl-ACP reductase engineering for Supplementary information The online version contains
improved in vivo fatty alcohol production. Nat. Commun. 12, 5825 supplementary material available at https://doi.org/10.1038/s44286-
(2021). 023-00002-4.
33. Bryant, D. H. et al. Deep diversification of an AAV capsid protein
by machine learning. Nat. Biotechnol. 39, 691–696 (2021). Correspondence and requests for materials should be addressed to
34. Dauparas, J. et al. Robust deep learning-based protein sequence Philip A. Romero.
design using ProteinMPNN. Science 378, 49–56 (2022).
35. Lipsh-Sokolik, R. et al. Combinatorial assembly and design of Peer review information Nature Chemical Engineering thanks
enzymes. Science 379, 195–201 (2023). Melodie Christensen and the other, anonymous, reviewer(s) for their
36. Pedregosa, F. et al. Scikit-learn: machine learning in Python. contribution to the peer review of this work.
J. Mach. Learn. Res. 12, 2825–2830 (2011).
37. Perez-Pons, J. A. et al. A β-glucosidase gene (bgl3) from Reprints and permissions information is available at
Streptomyces sp. strain QM-B814. Molecular cloning, nucleotide www.nature.com/reprints.
sequence, purification and characterization of the encoded
enzyme, a new member of family 1 glycosyl hydrolases. Eur. J. Publisher’s note Springer Nature remains neutral with regard
Biochem. 223, 557–565 (1994). to jurisdictional claims in published maps and institutional
38. Endelman, J. B., Silberg, J. J., Wang, Z.-G. & Arnold, F. H. Site- affiliations.
directed protein recombination as a shortest-path problem.
Protein Eng. Des. Sel. 17, 589–594 (2004). Open Access This article is licensed under a Creative Commons
39. Voigt, C. A., Martinez, C., Wang, Z.-G., Mayo, S. L. & Arnold, F. H. Attribution 4.0 International License, which permits use, sharing,
Protein building blocks preserved by recombination. Nat. Struct. adaptation, distribution and reproduction in any medium or format,
Biol. 9, 553–558 (2002). as long as you give appropriate credit to the original author(s)
40. Wheeler, T. J. & Eddy, S. R. nhmmer: DNA homology search with and the source, provide a link to the Creative Commons license,
profile HMMs. Bioinformatics 29, 2487–2489 (2013). and indicate if changes were made. The images or other third
party material in this article are included in the article’s Creative
Acknowledgements Commons license, unless indicated otherwise in a credit line to
The research reported in this publication was supported by the National the material. If material is not included in the article’s Creative
Institute of General Medical Sciences of the National Institutes of Health Commons license and your intended use is not permitted by
under awards T32GM008349 and T32GM135066 to J.T.R., 5R35GM119854 statutory regulation or exceeds the permitted use, you will need
to P.A.R. and the Great Lakes Bioenergy Research Center. to obtain permission directly from the copyright holder. To view
a copy of this license, visit http://creativecommons.org/licenses/
Author contributions by/4.0/.
J.T.R., B.J.B. and P.A.R. conceived the project and the approach.
B.J.B. implemented the computational simulations. J.T.R. and B.J.B. © The Author(s) 2024
Nature Chemical Engineering | Volume 1 | January 2024 | 97–107 107

---

<!-- Page 12 -->

Philip Romero
27 October 2023
X
X
X
X
X
X
We used Python 3.7 to run the experiments. All code is available at DOI: 10.5281/zenodo.10048592
We used Python 3.7 to run the experiments. All code is available at DOI: 10.5281/zenodo.10048592
All data for main text figures are present in the SI. All data with code to interpret it are available at DOI: 10.5281/zenodo.10048592
1

---

<!-- Page 13 -->

n/a
n/a
n/a
n/a
n/a
We performed four independent protein engineering trials and this sample size was determined based on our maximum experimental capacity
No data were excluded
We performed four independent protein engineering trials. All four successfuly found highly improved proteins.
Randomization was not relevant as all biological experiments were performed in vitro.
When working with machines that operate fully independently of human interaction, blinding is not a meaningful concept.
X X
X X
X X
X
X
X
X
2
