<!-- Page 1 -->

ll
OPEN ACCESS
Leading Edge
Perspective
How to build the virtual cell with artificial
intelligence: Priorities and opportunities
Charlotte Bunne,1,2,3,4,50 Yusuf Roohani,1,3,5,50 Yanay Rosen,1,3,50 Ankit Gupta,3,6 Xikun Zhang,1,3,7 Marcel Roed,1,3
Theo Alexandrov,8,9 Mohammed AlQuraishi,9 Patricia Brennan,3 Daniel B. Burkhardt,11 Andrea Califano,10,12,13
(Author list continued on next page)
1Department of Computer Science, Stanford University, Stanford, CA, USA
2Genentech, South San Francisco, CA, USA
3Chan Zuckerberg Initiative, Redwood City, CA, USA
4School of Computer and Communication Sciences and School of Life Sciences, EPFL, Lausanne, Switzerland
5Arc Institute, Palo Alto, CA, USA
6Department of Protein Science, Science for Life Laboratory, KTH Royal Institute of Technology, Stockholm, Sweden
7Department of Bioengineering, Stanford University, Stanford, CA, USA
8Department of Pharmacology, University of California, San Diego, San Diego, CA, USA
9Department of Bioengineering, University of California, San Diego, San Diego, CA, USA
10Department of Systems Biology, Columbia University, New York, NY, USA
11Cellarity, Somerville, MA, USA
12Vagelos College of Physicians and Surgeons, Columbia University Irving Medical Center, New York, NY, USA
13Chan Zuckerberg Biohub, New York, NY, USA
14Department of Molecular and Cell Biology, University of California, Berkeley, Berkeley, CA, USA
15Department of Statistics, Stanford University, Stanford, CA, USA
16Chan Zuckerberg Biohub, San Francisco, CA, USA
17Chan Zuckerberg Institute for Advanced Biological Imaging, Redwood City, CA, USA
18Department of Bioengineering, University of California, Berkeley, Berkeley, CA, USA
19Microsoft Research, Redmond, WA, USA
20Center for Computational Biology, University of California, Berkeley, Berkeley, CA, USA
21Google Research, Mountain View, CA, USA
22NewLimit, San Francisco, CA, USA
23Schmidt Futures, New York, NY, USA
24Calico Life Sciences LLC, San Francisco, CA, USA
25Chan Zuckerberg Biohub, Chicago, IL, USA
26Northwestern University, Evanston, IL, USA
27Cell Biology and Biophysics Unit, European Molecular Biology Laboratory, Heidelberg, Germany
28Department of Systems Biology, Harvard Medical School, Boston, MA, USA
29Department of Genome Sciences, University of Washington, Seattle, WA, USA
30Brotman Baty Institute for Precision Medicine, Seattle, WA, USA
(Affiliations continued on next page)
SUMMARY
Cells are essential to understanding health and disease, yet traditional models fall short of modeling and
simulating their function and behavior. Advances in AI and omics offer groundbreaking opportunities to
create an AI virtual cell (AIVC), a multi-scale, multi-modal large-neural-network-based model that can repre-
sent and simulate the behavior of molecules, cells, and tissues across diverse states. This Perspective pro-
vides a vision on their design and how collaborative efforts to build AIVCs will transform biological research
by allowing high-fidelity simulations, accelerating discoveries, and guiding experimental studies, offering
new opportunities for understanding cellular functions and fostering interdisciplinary collaborations in
open science.
INTRODUCTION and adaptive system in which complex behavior emerges from
a myriad of molecular interactions. Some aspects are remark-
The cell, the fundamental unit of life, is a wondrously intricate en- ably robust to perturbations, such as the elimination of genes
tity with properties and behaviors that challenge the limits of or their replacement with homologs from different species. Other
physical and computational modeling. Every cell is a dynamic aspects are sensitive to even seemingly minor disruptions, such
Cell 187, December 12, 2024 ª 2024 The Authors. Published by Elsevier Inc. 7045
This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).

---

<!-- Page 2 -->

ll
OPEN ACCESS Perspective
Jonah Cool,3 Abby F. Dernburg,14 Kirsty Ewing,3 Emily B. Fox,1,15,16 Matthias Haury,17 Amy E. Herr,16,18 Eric Horvitz,19
Patrick D. Hsu,5,18,20 Viren Jain,21 Gregory R. Johnson,22 Thomas Kalil,23 David R. Kelley,24 Shana O. Kelley,25,26
Anna Kreshuk,27 Tim Mitchison,28 Stephani Otte,17 Jay Shendure,29,30,31,32 Nicholas J. Sofroniew,33 Fabian Theis,34,35,36
Christina V. Theodoris,37,38 Srigokul Upadhyayula,14,16,39 Marc Valer,3 Bo Wang,40,41 Eric Xing,42,43
Serena Yeung-Levy,1,44 Marinka Zitnik,45,46,47 Theofanis Karaletsos,3,* Aviv Regev,2,* Emma Lundberg,3,6,7,48,*
Jure Leskovec,1,3,* and Stephen R. Quake3,7,49,*
31Seattle Hub for Synthetic Biology, Seattle, WA, USA
32Howard Hughes Medical Institute, Seattle, WA, USA
33EvolutionaryScale, PBC, New York, NY, USA
34Institute of Computational Biology, Helmholtz Center Munich, Munich, Germany
35School of Computing, Information and Technology, Technical University of Munich, Munich, Germany
36TUM School of Life Sciences Weihenstephan, Technical University of Munich, Munich, Germany
37Gladstone Institute of Cardiovascular Disease, Gladstone Institute of Data Science and Biotechnology, San Francisco, CA, USA
38Department of Pediatrics, University of California, San Francisco, San Francisco, CA, USA
39Molecular Biophysics and Integrated Bioimaging Division, Lawrence Berkeley National Laboratory, Berkeley, CA, USA
40Department of Computer Science, University of Toronto, Toronto, ON, Canada
41Vector Institute, Toronto, ON, Canada
42Carnegie Mellon University, School of Computer Science, Pittsburgh, PA, USA
43Mohamed Bin Zayed University of Artificial Intelligence, Abu Dhabi, United Arab Emirates
44Department of Biomedical Data Science, Stanford University, Stanford, CA, USA
45Department of Biomedical Informatics, Harvard Medical School, Boston, MA, USA
46Kempner Institute for the Study of Natural and Artificial Intelligence, Harvard University, Cambridge, MA, USA
47Broad Institute of MIT and Harvard, Cambridge, MA, USA
48Department of Pathology, Stanford University, Stanford, CA, USA
49Department of Applied Physics, Stanford University, Stanford, CA, USA
50These authors contributed equally
*Correspondence: tkaraletsos@chanzuckerberg.com (T.K.), regev.aviv@gene.com (A.R.), emmalu@stanford.edu (E.L.), jure@cs.stanford.edu
(J.L.), steve@czbiohub.org (S.R.Q.)
https://doi.org/10.1016/j.cell.2024.11.015
as a point mutation or an external factor that tips cells into tion, metabolic pathways, and signal transduction. Each process
dysfunction and disease. involves a multitude of biomolecular species, in diverse and dy-
To understand a cell’s function, scientists have attempted to namic configurations and states. (3) Nonlinear dynamics: most
construct virtual cell models to simulate, predict, and steer cell cellular processes are highly nonlinear, such that small changes
behavior.1–6 Building on this vision, we use the term virtual cell in inputs can lead to complex changes in outputs. Thus, despite
to define a computational model that simulates the biological progress in modeling specific cellular processes, these factors
functions and interactions of a cell. Existing cell models are often collectively pose a substantial roadblock to the construction of
rule-based and combine assumptions about the underlying bio- a virtual cell.
logical mechanisms with parameters fit from observational data. Two exciting revolutions in science and technology—in AI and
They generally rely on explicitly defined mathematical or compu- in omics—now enable the construction of cell models learned
tational approaches, such as differential equations,7–9 stochas- directly from data. These parallel revolutions provide an unprec-
tic simulations,10,11 or agent-based models.12,13 They vary in edented opportunity for an ambitious vision of an AI virtual cell
complexity and cover different defined aspects of cell biology, (AIVC), a multi-scale, multi-modal, large-neural-network-based
such as transcription and translation,14 cytoskeletal driven cell model that can represent and simulate the behavior of mole-
behavior,15,16 biochemical networks,17 or metabolic flux.18,19 cules, cells and tissues across diverse states (Figure 1).
The first whole-cell model was developed in 2012, representing Experimentally, the exponential increase in the throughput of
all 482 genes and molecular functions known for an organism: measurement technologies has led to the collection of large
the bacteria Mycobacterium genitalium.8 Since this pioneering and growing reference datasets within and across different cell
work, genome-wide models have been developed to represent and tissue systems,23–25 with data doubling every 6 months for
other bacterial organisms, including Escherichia coli.8,20–22 the past several years,26 along with the ability to couple these
Despite their widespread use in modeling biological systems, measurements with systematic perturbations.27–29
approaches to date fall short of capturing many aspects of the Computationally, concurrent advances in AI have enhanced
operations of both bacterial and more complex systems, such our ability to learn patterns and processes directly from data
as human cells. Challenges include: (1) Multi-scale modeling: without needing explicit rules or human annotation.30,31 Such
cells operate on multiple scales across both time and space, modeling paradigms have been used successfully in the biomol-
from atomic to molecular to cellular and histological, with func- ecular realm, for example, to predict three-dimensional (3D) mo-
tional properties emerging through nonlinear transformation lecular structures from sequences32–34 and interactions between
from one scale to another. (2) Diverse processes with massive different molecular components.35–38 Recent modeling method-
numbers of interacting components: cellular function encom- ologies in AI provide representation and inference tools that
passes numerous interacting processes, such as gene regula- satisfy the trifecta of being predictive, generative, and queryable,
7046 Cell 187, December 12, 2024

---

<!-- Page 3 -->

ll
Perspective OPEN ACCESS
Figure 1. Capabilities of the AIVC
(A) The AIVC provides a universal representation (UR) of a cell state that can be obtained across species and conditions and generated from different data
modalities across scales (molecular, cellular, and multicellular).
(B) The AIVC possesses capabilities to represent and predict cell biology. This universality allows the representation to act as a reference that can generalize to
previously unobserved cell states, providing guidance for future data generation. Because the representation is shared across modalities, it also remains invariant
to the specific data type used to generate it, serving as a virtual representation for unified analysis across modalities. The AIVC also allows modeling the dynamics
of cells as they transition between different states, whether naturally due to processes such as differentiation or due to genetic variation or artificially through
engineered perturbations. Thus, the AIVC enables in silico experimentation that would otherwise be cost-prohibitive or impossible in a lab.
(C) The utility of the AIVC depends on its interactions with humans at different levels. At the individual scientist level, it must be accessible through open licenses
and the democratization of computing resources. Interpretability can be established through intermediary layers, such as language models that allow the virtual
cell to communicate its results effectively. At the scientific community level, evaluating the AIVC should focus on core capabilities that move beyond narrow
benchmarks. Community development will be crucial for ongoing improvements to the virtual cell that remain accessible. At the societal level, the AIVC must
ensure the privacy of its contents to protect sensitive data.
which are key utilities for advancing biological research and un- in response to perturbations in specific progenitor cells; and mi-
derstanding. By building on these properties, we argue that we crobiologists predict the effects of viral infection on not just the
now have the methods to develop a fully data-driven neural infected cell but also its host organism. AIVCs will empower ex-
network-based representation of an AIVC that can accelerate perimentalists and theorists alike, by transforming the means by
research in biomedicine by enabling fast-paced in silico studies, which hypotheses are generated and prioritized and allowing bi-
as well as powerful bridges between computational methods ologists to span a dramatically expanded scope, better fitting the
and confirmatory wet-lab experimentation (Figure 1). enormous scales of biology. Although the cellular models may
The creation of an AIVC will enable a new era of high-fidelity not always directly identify mechanistic relationships, they can
simulation in biology, in which cancer biologists model how spe- be viewed as tools for effectively narrowing the search space
cific mutations transition cells from healthy to malignant; devel- for mechanistic hypotheses, thereby accelerating the discovery
opmental biologists forecast how developmental lineages evolve of underlying factors behind cellular function.
Cell 187, December 12, 2024 7047

---

<!-- Page 4 -->

ll
OPEN ACCESS Perspective
Box 1. Grand challenges for building the AIVC
OUTLINING CAPABILITIES AND DESIGNING EVALUATION FRAMEWORKS
The burgeoning number of foundation models in biology perform a subset of the capabilities of virtual cells outlined in this perspective. Given the
diversity of these approaches, it is important to define what the core capabilities of AIVCs should be and how those capabilities can be evaluated. For
every capability, proper metrics must be designed, and comprehensive evaluation data be collected. Models’ capabilities should be assessed on
general performance as well as on their ability to answer specific biological questions. It is imperative to continuously improve benchmarking stra-
tegies along with AIVC models and ensure that they align with biologically meaningful objectives. As the field develops better alignment on these
questions, collaborative opportunities will arise, and the speed at which virtual cells can be generated will accelerate.
ESTABLISHING SELF-CONSISTENCY ACROSS VARYING CONTEXTS WITH DIFFERENT ARCHITECTURES
Biology is tremendously complex: it operates across different scales, in different contexts, and is measured with different modalities. AIVC models
must be self-consistent across all of these axes. Models should propagate function across physical scales—interactions between molecules should
have consistent effects when measuring binding affinity, gene expression, cell-cell communication, or tissue organization. As physical and dynamic
scales increase in scope and size, additional context, for example, species, cell type, tissue, disease status, etc., should fine-tune predictions made
at smaller resolutions, while also accounting for stochasticity. Model predictions should also be agnostic to their input and output modalities. The
same entity, profiled with different technologies, should have the same internal representation in an AIVC. To properly model such complex behav-
iors, many machine learning approaches should be explored and their merits carefully judged.
BALANCING INTERPRETABILITY AND BIOLOGICAL UTILITY
A consistent trend in the application of deep learning methods to biology, accelerated by the rise of large foundation models, has been the implicit
trade-off between models’ performance gains and their increasingly uninterpretable ‘‘black box’’ natures. AIVC models will ultimately be judged on
their ability to expand our understanding of biology, either by providing novel insights to biological processes or by accelerating the scientific pro-
cess. To achieve this goal, AIVC models must make highly accurate and well-calibrated predictions that simulate biology, and the trade-off between
actionability and interpretability will have to be balanced. Actionable model outputs are those of high utility to design affordable and efficient vali-
dation experiments and are key for initial real-world use. Various approaches exist for explaining model predictions, including causal modeling,
sparse featurization, and counterfactual reasoning, and this is a highly active research area. Building intuitive interfaces that facilitate the study
and interpretation of AIVCs via other models, such as AI research agents, will further increase downstream utility.
CONSTRUCTING A FRAMEWORK FOR COLLABORATIVE CELL MODELING
The successful development of AIVCs will require collaboration across disciplines. We foresee a future where AIVC platforms function as open, in-
terconnected hubs for collaborative development and broad deployment of cell models to researchers and as education hubs delivering training to
researchers, as well as providing engagement activities for educators, patients, and the public. Thus, investments in infrastructure fostering open
and collaborative development of AIVCs should be of high priority.
ENSURING AIVCs BENEFIT ALL AND PROMOTE ETHICAL AND RESPONSIBLE USE
Generating large open datasets that reflect human diversity—datasets integral for training AIVC models—poses a substantial challenge. Developers
will have to use the utmost care to ensure these datasets are used ethically and transparently while building AIVCs and develop strategies to mitigate
risks of model contamination with falsified data. Early adopters of AIVCs will have a key role in promoting and demonstrating responsible use of these
models. Furthermore, the development of chat-based interfaces could be crucial in democratizing access to AIVCs. Close collaboration with ethics
and regulatory experts from the outset is paramount for establishing new regulatory norms that will facilitate the responsible use of AIVCs.
UNDERSTANDING THE VALUE OF DIFFERENT DATA TYPES TO PRIORITIZE LARGE-SCALE DATA GENERATION
A fundamental question for the collaborative development of AIVCs is which data and modalities should be collected to enable generalization across
biological contexts and scales. These data will need to encompass the breadth of biology in different species, domains, and modalities, representing
the heterogeneity of life, while maintaining depth sufficient to distinguish true signals from noise. A key aspect of data generation will be the simul-
taneous measurement of temporal and physical scales, while also allowing perturbations of the system.
This perspective article is based on extensive community AIVCs. We describe a vision catalyzed by emerging advances
discussions, including a workshop hosted by the Chan Zuck- in AI in cell biology and their application to constructing virtual
erberg Initiative, and aims to ignite the formation of a collab- representations of cells. We lay out priorities and opportu-
orative research agenda for a large-scale, long-term initiative nities across data generation, AI models, benchmarking, inter-
with a roadmap for developing, implementing, and deploying pretation, and ensuring biological veracity and safety (Box 1).
7048 Cell 187, December 12, 2024

---

<!-- Page 5 -->

ll
Perspective OPEN ACCESS
Box 2. Vignettes
CELL ENGINEERING TO ENABLE PHENOTYPIC DRUG DISCOVERY AND CELL-BASED THERAPEUTICS
One challenge in developing successful therapies is the difficulty in incorporating the full underlying genetic, molecular and cellular basis of dis-
ease during drug discovery and development.129 These context-specific underpinnings are not fully specified and often vary between human pa-
tients and model systems used in pre-clinical studies. By integrating biological data from various sources relevant to specific disease contexts, the
AIVC could generate an environment for testing different therapeutic interventions in silico and identify approaches for engineering cells to reverse
disease phenotypes, while accounting for the effects of varying both treatments and patient profiles. By representing the overall disease phenotype
specific to patient populations (rather than one specific biochemical target at a time), the AIVC can enable virtual phenotypic screens. Although in
silico experiments may not always be fully accurate, by prioritizing virtual hits with higher chances of success, the AIVC can lower experimentation
costs and accelerate the process.
The AIVC has potential to push the cell therapy frontier. With growing evidence affirming the efficacy and safety of cell-based therapies for rare
diseases and cancer,130,131 the AIVC can improve systematization and precision to cell engineering. For example, virtual cell-based engineering
could enable targeted modifications to pancreatic beta cells to create individualized beta cell replacement therapies for type 1 diabetes. By simu-
lating the biological phenotype of individual patients, in silico experiments within the AIVC could identify interventions that help drive the differen-
tiation of beta cells from progenitors, cloak them from the immune system, and maintain their function, with the ultimate goal of either transplanting
these engineered cells into patients or engineering them in situ.
UNLOCKING THE POWER OF SPATIAL BIOLOGY TO FIGHT CANCER
Spatial structures in cancer, specifically within the tumor microenvironment (TME), are critical drivers of cancer progression and can drive
resistance to the immune system and limit drug efficacy.132 Malignant cells within a tumor can engage in active immune evasion by either block-
ing immune infiltration,133 evading immune recognition, or dampening immune cell function.134 Thus, immune resistance must be understood in
the spatial context of the cellular neighborhood to identify the specific cell states and gene signatures involved. Although next-generation spatial
profiling methods enable researchers to experimentally investigate the heterogeneity of the TME,135 an AIVC could extend these analyses to a
universal, pan-cancer framework, which can be personalized to individual patients. Using an AIVC model, cancer researchers should be able to
identify TME niches shared across multiple cancer types from many patients. Identifying pan-cancer markers can drive cancer treatment both by
highlighting new targets and also by identifying existing treatments that can be applied to new cancer types.136 In this setting, the AIVC would
help identify the interactions associated with TME cell states and would search for similar states from any disease where existing treat-
ments exist.
Finally, the AIVC could greatly advance precision oncology.137 Given that the AIVC will capture intrinsic variation, the genetic diversity of individual
patient’s cancers will be represented in any analyses. Although the AIVC would already accurately qualify the change in the expression of genes,
tumor sequencing data would allow it to model the change of function of those genes, for example, through loss of function, change in post-trans-
lational modifications, or rewiring of protein-protein interactions and signaling networks.138
(Continued on next page)
Cell 187, December 12, 2024 7049

---

<!-- Page 6 -->

ll
OPEN ACCESS Perspective
Box 2. Continued
DIAGNOSTIC VIRTUAL CELL MODELS FOR INDIVIDUAL PATIENTS
The AIVC could introduce a new approach to diagnostics that incorporates a personalized AIVC (or a digital twin139 ) to track a patient’s health and
suggest suitable interventions. The AIVC would create a detailed representation of each patient’s cells by incorporating specific patient data, such
as genetic sequences, single-cell profiles from blood, and tissue pathology images, along with additional clinical information from their health re-
cords. Periodic updates to each patient’s AIVC instance enable monitoring of evolving health conditions, prediction of upcoming adverse events,
and potential therapeutic outcomes.
Through additional updates from less costly assays, this virtual patient model could be progressively refined and made more robust.140 For
example, transcriptomic or genetic liquid biopsies can reveal significant and diverse characteristics of a patient from a single test and could greatly
aid in the diagnosis of a broad spectrum of conditions.141 Through the virtual cell’s implicit and structured representation of universal cell types and
states, one can envision the creation of patient models of inaccessible cell types, such as beta cells in the pancreas or neurons in the brain, gener-
ated after sampling accessible cell types such as blood or skin.
A HYPOTHESIS-GENERATING FRAMEWORK FOR SCIENTIFIC RESEARCH
Traditionally, the biological research community has relied on computational models for analyzing data from past experiments based on an ex-
isting hypothesis. The virtual cell could switch the paradigm by computationally exploring a vast array of possible hypotheses through in silico exper-
imentation. It could identify the most informative experiments for addressing specific biological questions, shifting the role of computational models
from merely validating hypotheses or processing observations without a particular goal to generating specific sets of hypotheses to pursue.
This shift could greatly enhance the scientific discovery process: instead of conducting a single experiment followed by an in-depth analysis, sci-
entists can engage in a dynamic iterative interaction with the virtual cell. With each new piece of data, they can refine their understanding of the
biological system and consult the virtual cell to identify what additional experimental data could be valuable. Ultimately, we may be able to perform
active learning with biologists in the loop and construct self-driving labs for efficient and unbiased generation of virtual cells.
By encouraging interdisciplinary collaborations in open sci- AIVCs
ence—spanning academia, philanthropy, and the biopharma
and AI industries—we posit that a comprehensive under- Our view of an AIVC is a learned simulator of cells and cellular
standing of cellular mechanisms is within reach. AIVCs have systems under varying conditions and changing contexts, such
the potential to revolutionize the scientific process, lead to as differentiation states, perturbations, disease states, stochas-
the understanding of novel biological principles, and augment tic fluctuations, and environmental conditions (Figure 1). In this
human intelligence to underpin future breakthroughs in pro- context, a virtual cell should integrate broad knowledge across
grammable biology, drug discovery, and personalized medi- cell biology. VCs must work across biological scales, over
cine (Box 2). time, and across data modalities and should help reveal the
7050 Cell 187, December 12, 2024

---

<!-- Page 7 -->

ll
Perspective OPEN ACCESS
programming language of cellular systems and provide an inter- arrangements. By modeling the transient nature of the overall
face to use it for engineering purposes. cell state and the continuous flux in cellular conditions, the AIVC
In particular, an AIVC needs to have capabilities that allows re- could uncover previously unstudied trajectories in diverse dynamic
searchers to (1) create a universal representation (UR) of biolog- processes, such as development, maintenance of homeostasis,
ical states across species, modalities, datasets, and contexts, pathogenesis, and disease progression. Another critical challenge
including cell types, developmental stages, and external condi- is understanding the molecular mechanisms underpinning
tions; (2) predict cellular function, behavior, and dynamics, as observed phenotypes and trajectories. The AIVC could propose
well as uncover the underlying mechanisms; and (3) perform in potential causal factors behind phenotypes by simulating the ef-
silico experiments to generate and test new scientific hypothe- fects of different interventions. Through its multi-scale design,
ses and guide data collection to efficiently expand the virtual the AIVC should be able to extrapolate the basis of cellular function
cell’s abilities. across scales and link intracellular processes to phenotypes at the
Next, we elaborate on these key capabilities and discuss ap- cell and tissue level. Thus, the AIVC opens new avenues for inves-
proaches for how to achieve them. tigating mechanisms linked to diverse phenotypes and behaviors.
Although uncovering a phenotype’s causal factors may not al-
URs ways be feasible through computation alone, the AIVC has the
An AIVC would map biological data to UR spaces (Figure 1A), potential to reduce the space of possible hypotheses. Through
facilitating insights into shared states and serving as a compre- simulating the effects of different interventions, the AIVC could
hensive reference. These URs should integrate across three propose potential causal factors behind phenotypes with corre-
physical scales—molecular, cellular, and multicellular—and sponding degrees of uncertainty, allowing scientists to validate
accommodate contributions from any relevant modality and claims experimentally.
context (Figure 1A). This integration will allow researchers to
complement new data with existing information within the In silico experimentation and guiding data generation
AIVC, leveraging its extensive biological knowledge to bridge For real-world utility, a defining function of an AIVC will be its ability
gaps between different data. Such a comparison with prior to guide data generation and experiment design. An AIVC should
data would provide a comprehensive context for every be queryable with computational twins of today’s laboratory ex-
analysis. periments, here called virtual instruments (VIs). Virtual experiments
Importantly, the multilevel representation should generalize could, for example, simulate experiments in a cell type that is chal-
to new states that are not present within the data used to train lenging to cultivate in vitro or simulate expensive readouts from
the AIVC. Such an emergent capability would unlock discov- low-cost measurements, such as single-cell transcriptomes from
eries about biological states that have not been directly label-free imaging.39 Virtual experiments could also be used to
observed or might not even occur in nature. For instance, screen a vast number of possible perturbagens at a scale that
the AIVC’s exposure to similar instances during training, would be impossible in the lab. Such capabilities are invaluable
such as inflammatory states in macrophages, might enable it when considering the exponentially larger search space of combi-
to predict previously unknown inflammatory states in micro- natorial perturbations involving more than one perturbagen.40–44
glia. Additionally, the AIVC should be able to predict novel AIVCs will usher in a new pradigm of how computational sys-
states resulting from interventions (or, equivalently, interven- tems are probed during the design of new biological experiments.
tions needed to achieve a novel specified state) offering a In this framework, an AIVC would not only design experiments to
range of downstream applications in cell engineering and syn- validate specific scientific hypotheses but also to enhance its
thetic biology. own capabilities. Equipped with the ability to assign confidence
values to its predictions, an AIVC could enable interactive
Predicting cell behavior and understanding querying to guide experimentalists to the most efficient path for
mechanisms generating additional data for fine-tuned improvement in low-
A defining function of an AIVC will be its ability to model cellular confidence areas. Extended to an active and iterative lab-in-
responses and dynamics. By training on a wide range of snap- the-loop process, we envision efficient and focused expansion
shots, time-resolved, non-interventional, and interventional da- of the AIVC’s performance. Ultimately, the AIVC might even be
tasets collected across contexts and scales, the AIVC can able to identify key gaps in its own understanding of biology
develop an understanding of the molecular, cellular, and tissue and propose the most efficient paths to bridge them.45–47
dynamics that occur under natural or engineered signals. These
signals include external and internal stresses or other factors BUILDING THE AIVC
such as chemical (e.g., small molecules) or genetic (engineered
or natural) perturbations and their combinations. An AIVC should We envision an AIVC as a comprehensive AI framework
be able to predict responses to perturbations that have not been composed of several interconnected foundation models that
previously tested in the lab, while also accounting for the specific represent dynamic biological systems at increasingly complex
features of the cellular context within which the perturbation is levels of organization—from molecules to cells, tissues, and
being tested. beyond. Our approach has two main components: (1) a universal
The AIVC should also have the capability to simulate the tempo- multi-modal multi-scale biological state representation and (2) a
ral evolution of alterations in cell states in response to both intrinsic set of VIs, which are neural networks that manipulate or decode
and extrinsic factors, along with the resulting multicellular spatial these representations. Although there may be other approaches
Cell 187, December 12, 2024 7051

---

<!-- Page 8 -->

ll
OPEN ACCESS Perspective
Figure 2. Overview of the AIVC
(A and B) (A) Similar to biological cells, (B) the AIVC
models cell biology across different physical
scales, including molecular, cellular, and multi-
cellular. Along the physical dimension, the first
scale models the state and interactions of indi-
vidual molecules, such as those of the central
dogma, as well as additional molecules, such as
metabolites. Molecules can be represented as
sequences or atomic structures. The next scale
represents cells as collections of these molecules.
For example, such cells contain a genetic
sequence, RNA transcripts, and some quantities
of proteins. Molecules within cells have specific
locations that may be related to their function. The
final scale models the interactions between cells
and how they communicate and form complex
tissues. Each scale relies on universal represen-
tations that are learned from multi-modal data and
are integrating URs from the previous scale.
(C and D) (C) To capture the behavior and dy-
namics of physical cells, its components, or col-
lections, (D) the AIVC comprises virtual in-
struments. On the cellular scale, for example,
manipulator VIs simulate how cell states change
as cells divide, migrate, develop from progenitor
states, or respond to perturbations through
learned transitions in the URs. Decoder VIs allow
for the decoding of the cell UR, e.g., to understand
phenotypic properties.
vidual cells interact with one another
and the non-cellular environment in a tis-
sue. Each of these scales is represented
by a distinct UR, building on abstractions
generated by the previous layer, thus link-
ing the different scales.
In the context of UR, VIs are neural net-
works that take URs as input and pro-
duce a desired output. We describe two
types of VIs: decoder VIs (or decoders)
that take a UR as an input and produce
human-understandable output, for
example, a cell type label or a synthetic
microscope image, and manipulator VIs
(or manipulators), which take a UR as an
input and produce another UR as an
output, for example, that of an altered
cell state after perturbation. Because
these instruments will operate over the
same representations, they can be
to building an AIVC, we believe this approach would provide a shared and reused across different use cases, experiments,
scaffold that can be scaled in a collaborative and open way. and datasets. Thus, we envision that any scientist will be able
We use the term UR to refer to an embedding produced by a to build a VI on top of a UR and share it with the community.
multi-modal AIVC foundation model. An embedding is a learned The building of VIs that closely resemble real instruments, such
numerical representation of data in a continuous vector space. as a microscope, has the potential to seed the development of
The AIVC transforms high-dimensional multi-scale multi-modal instrument-specific lab-in-the-loop systems.
biological data into embeddings that retain meaningful relation-
ships and patterns. Building UR across physical scales
The AIVC can capture cell biology at three distinct physical The AIVC would be a multi-scale foundation model that learns
scales by representing (1) molecules and their structures found distinct representations of biological entities at each physical
within individual cells, (2) individual cells, as spatial collections scale (Figure 2C). These representations can be aggregated
of those interacting molecules and structures, and (3) how indi- together and transformed to produce representations at the
7052 Cell 187, December 12, 2024

---

<!-- Page 9 -->

ll
Perspective OPEN ACCESS
next higher physical scale. This recurring architectural motif can molecular interactions and signaling networks formed in a cell,
be applied from the level of individual molecules to the scale of a cellular UR can be built using representations of molecular
entire tissues and organs granting the model consistency across and other (e.g., imaging) features, describing the organization
biological scales (Figure 2A). Each representation applies univer- and abundance of molecular components. The key step here
sally to a specific class of biological entities. This abstraction al- would be to integrate learned representations of molecules
lows the virtual cell to seamlessly evolve and incorporate new with their quantities and appropriately abstracted locations and
data—whether from new modalities or from out-of-distribution timestamps to create a unified representation of the cell.58–60
sources— within this general framework. Data for the cellular UR consist of measurements mapped to a
In the following sections, we discuss design principles and single-cell level, such as measurements of the transcriptome
data that could be used to construct each physical scale of the (single-cell RNA sequencing [scRNA-seq]), chromatin accessi-
AIVC bottom-up. Although many existing machine learning ar- bility (scATAC-seq), chromatin modification, transcription factor
chitectures could be applied directly to the task of learning func- binding, and proteome.61 Imaging technologies measure cell
tional representations of cellular components (Box 3), we addi- morphology at subcellular resolution, often together with molec-
tionally suggest the incorporation of biological inductive biases ular information.29,62,63 For example, fluorescence confocal mi-
into the design of these representations, and further modeling in- croscopy can help resolve the subcellular location of the human
novations should drive the refinement and success of these proteome.64 Live-cell imaging65 enables the study of proteins in
models. living cells using time-lapse microscopy. Cryoelectron micro-
Molecular scale scopy determines biomolecular structures at near-atomic reso-
The first layer of the virtual cell represents individual molecular lution.66,67 Super-resolution microscopy offers deeper insights
species (Figures 2A and 2C). Although there are many different into molecular processes through single-molecule imaging in
classes of molecules present in a cell, a starting point for the living systems.68,69 Complementing imaging approaches, mass
AIVC will be to model the three types of molecules of the central spectrometry, and proximity-dependent labeling can unveil pro-
dogma: DNA, RNA, and proteins. These can all be represented as tein-protein associations and provide deeper insights into cell
sequences of characters—nucleotides or amino acids.48–53 Such structure and signaling network rewiring.70,71
sequence data are particularly well suited for AI methods origi- From a model architecture perspective, vision transformers72
nally developed for natural language processing, such as large or models leveraging convolutional neural networks
language models (LLMs) (Box 3). Given the high-throughput mea- (CNNs)73,74 are widely applicable to biological images to model
surement capabilities for genomic sequences, there are substan- across multiple imaging channels capturing different biological
tial and growing amounts of training data available. This abun- features,75,76 while being robust to distribution shift and batch
dance of data, combined with simple objective functions (such variability.77 Autoencoders and transformers have been suc-
as predicting masked letters in a sequence), provides the key in- cessfully applied for learning representations for sequence-
gredients for effectively training models to generate an initial mo- based data.59,78,79 Using AI algorithms to integrate different
lecular UR. Furthermore, a biological language model could be data modalities collected with sequencing and imaging technol-
trained on all three modalities simultaneously, thus maximizing ogies creates a multi-view model of the cell that can be both dy-
interoperability and training corpus size. Despite its inherent namic and predictive.80,81
compatibility with transformers, specific considerations around As the AIVC model grows in complexity, it is crucial to also
masking and attention mechanisms must be addressed when model cellular organelles and membraneless compartments82
applying these models to biological sequence data as opposed as units that play specific roles within the cell. Robustly capturing
to natural language. Although language modeling approaches the functions of these units is vital to ensure accurate predic-
have been extensively studied for these core molecules and tions, mechanistic interpretability, and model generalizability.
have proven successful for some of their chemical modifica- Given their prevalence, the cellular UR will initially rely on tran-
tions54 and various other molecules, such as glycans, lipids, scriptomics measurements, whereas imaging modalities will be
and metabolites,55,56 they may struggle with other molecular key for continued modeling of cellular spatial organization and
constituents of the cell. Such modeling difficulties might be exac- dynamics.
erbated for data that are difficult to fit into a sequence or very Multicellular scale
small molecules. Given that the primary building blocks of these At the third layer of abstraction, the AIVC models the organiza-
entities are atoms, a neural network trained to model molecules at tion of cells into a multicellular UR (Figures 2A and 2C). This layer
the atomic level32,57 could be a more general choice for this layer. allows for the exploration of how cell-cell interactions, largely
However, models with atomic resolution introduce a substantial governed by spatial proximity, combine into tissues, organs,
computational burden and might be constrained by the limited and, ultimately, whole organisms. Multicellular interactions can
availability of training data. Although atomic-based modeling is be analyzed after tissue dissociation (such as in scRNA-seq)83
highly accurate for many static structures, it cannot yet represent or in situ in a 2D section or 3D volume, where the tissue structure
the full dynamic range of chemistry that occurs at this scale. is preserved. Building the AIVC will require integration across
Therefore, a broader, evolutionarily informed representation available modalities that provide spatial insights, i.e., both spatial
such as that of sequences may be preferred. molecular profiling, as well as non-molecular tissue imag-
Cellular scale ing data.
The next level of abstraction models individual cell states There are multiple methods to profile the spatial location of
(Figures 2A and 2C). As cellular function is underpinned by the RNA84 and proteins85 in cells, along with various imaging
Cell 187, December 12, 2024 7053

---

<!-- Page 10 -->

ll
OPEN ACCESS Perspective
Box 3. AI techniques for building the AIVC
The AIVC will connect a number of diverse neural network architectures. Although these architectures may not have been purpose-built for biological
applications, they have each demonstrated success when matched with specific biological modalities and inductive biases. In many cases, these
architectures may be exchangeable, and one must weigh their individual trade-offs in accuracy, speed, and generalizability. Beyond this, the com-
munity is actively developing AI architectures tailored to the characteristics of (large) biological datasets.
TRANSFORMERS
A transformer neural network30 comprises multiple transformer layers, each taking a series of tokens (discrete pieces of information such as
words, RNA molecules, or gene representations) as input—initial tokens for the first layer and outputs from the preceding layer for subsequent
ones. Within each layer, tokens use self-attention to integrate context from other tokens, enhancing their own representations, which are then pro-
cessed through a feed forward network. This architecture, which fundamentally requires only a collection of tokens,
adapts well across various applications and use cases.
The collection of tokens passed to a transformer does not have any ordering by default. Additionally, the self-attention mechanism, the core of the
success of the transformer, can be taken as a strong biological inductive bias. For instance, in representing cells through their RNA molecules de-
tected via scRNA-seq, each RNA molecule, represented as a token, interacts with others, modeling gene interactions through self-attention.30
Customizing input tokens with numerical representations of genes further allows the integration of diverse biological data scales, from individual
genes to whole cells.59,60
Additionally, introducing positional encodings to tokens enables transformers to process sequences, such as natural language,30 or biological
sequences, such as DNA,48,142 by incorporating sequence-specific dependencies. This approach is crucial in applications such as masked lan-
guage modeling, where the model predicts missing tokens in sequences, enhancing its understanding of contextual relationships within data. In-
novations continue to refine transformers, increasing their capacity to handle longer sequences and improving efficiency, with advancements
such as state-space models enabling the generation of extensive DNA sequences.51
CNN
A CNN is a deep learning model primarily used for analyzing images.73,74 It consists of multiple layers that automatically and adaptively learn
spatial hierarchies of features through backpropagation. This learning is facilitated by convolutional layers that apply filters to local patches of input
data, pooling layers that reduce dimensionality, and fully connected layers that interpret the features extracted to make decisions.
In the field of biology, CNNs have proven invaluable for tasks involving image data due to their ability to detect complex patterns and structures,
such as microscope images of cells and tissues. Here, CNNs play a critical role in multiplex imaging,143 where multiple targets within a single sample
are labeled and visualized simultaneously. This technique is particularly useful in studying the complex interactions of different molecules or cell
types within a heterogeneous tissue environment.144 Another notable application is in the analysis of H&E-stained tissue sections, commonly
used in clinical pathology.145 Lastly, in live-cell imaging, CNNs are employed to track dynamic changes within cells or even single molecules
over time, providing insights into cell migration, responses to treatment, or the movement and interaction of individual molecules within cells,
revealing crucial biological processes at a molecular level.146
Beyond their traditional use in image processing, CNNs can also be applied to model sequence data, such as DNA sequences, where they identify
patterns and features that are predictive of biological functions.147 Despite their extensive utility, CNNs are increasingly being supplemented or
(Continued on next page)
7054 Cell 187, December 12, 2024

---

<!-- Page 11 -->

ll
Perspective OPEN ACCESS
Box 3. Continued
replaced by vision transformer models,72 which leverage self-attention mechanisms to process entire images in parallel. These models can often
achieve higher accuracy on tasks where understanding the global context within the image is crucial.
DIFFUSION MODELS
Diffusion models are a class of generative deep learning models that have recently gained attention for their ability to generate high-quality,
diverse samples across various domains.148 They operate by gradually transforming a distribution of random noise into a structured output (images,
text, cellular states, etc.) through a process that mimics a physical diffusion process. Building up on diffusion model architectures, approaches such
as flow matching methods can also model the distributional evolution over time,149 making them especially powerful in biological applications where
dynamic changes and temporal progression are critical. Flow matching methods thus capture and generate sequences of data that reflect contin-
uous transformations, such as the developmental stages of cells over time and space or the response of biological systems to treatments.87 The
ability of diffusion and flow matching models to learn and replicate complex distributions, combined with the temporal and spatial modeling capa-
bilities of flow matching methods, makes them particularly suited for tasks that involve high-dimensional, intricate data structures typical of biolog-
ical systems.
GNNs
GNNs are a set of architectures that can model graphical data.150 Graphs, sets of nodes connected by edges, are useful representations for many
kinds of biological data. When modeling a biological system, a GNN could be a good choice if a graph structure represents some core inductive bias.
For example, a protein structure151 can be thought of as a graph where residues are nodes, and their bonds are edges. Cells in a tissue form a graph:
each cell is a node, and the cells it is physically proximal to are connected by edges.152,153 In both cases, the graph represents how nodes are phys-
ically proximal to each other. For spatially organized cells, the graph represents how they may pass chemical signals between one another.
GNNs can be used to make predictions about individual nodes, edges, or the graph as a whole.154 For simplicity, in the following section, we
describe a node-based GNN. At each layer, a node updates its representation using a neural network, which can take in that node’s current rep-
resentation, in addition to the representations of the node’s neighbors, which are connected by an edge. By stacking GNN layers, a node can receive
‘‘messages’’ from neighboring nodes at increasing distances, ‘‘hops,’’ from it. Nodes and edges can both be initialized with different features, which
control their final representation and what messages they pass to their neighbors. For example, a GNN trained on spatial transcriptomic data could
take node features to be the virtual cell representation of each cell’s gene expression. The GNN would then update those representations to include
context about each cell’s neighbors, helping to identify spatial interactions and niches.153
methods for select molecular species (e.g., immunohistochem- A more generalized data generation effort together with open
istry) or with stains for tissue structure alone (e.g., hematoxylin frameworks for spatial data86 could greatly accelerate modeling
and eosin [H&E]). Spatial molecular biology is currently a very at the multicellular scale.
active area of research and method development. Although pub- The relative organization of cells within a 2D tissue section and
licly available data are still limited, we foresee a rapid develop- 3D tissue volume can be represented using a graph or point
ment in this domain providing multi-omic 2D and 3D datasets. cloud. The multicellular UR can be derived from such data using
Cell 187, December 12, 2024 7055

---

<!-- Page 12 -->

ll
OPEN ACCESS Perspective
graph-learning techniques, such as graph neural networks In silico experimentation and guiding data generation
(GNNs) and equivariant neural networks (ENNs). For image- Manipulator VIs operating in the UR space could further enable
based data, convolutional neural networks or vision transformers the exploration of a broad range of hypotheses through in silico
can be applied (Box 3). experiments that virtually perturb a cell model. This might be
achieved by predicting changes in the URs following a perturba-
Predicting cell behavior and understanding tion prompt (Figure 2D).40,42–44
mechanisms The design of manipulators that predict transitions in the UR
VIs are the ‘‘tools’’ that operate on UR embeddings and perform upon an in silico input can build on conditional generative models:
various functions and tasks. By altering URs of molecules, cells, deep learning architectures such as conditional deep generative
and tissues, manipulators can abstract complex dynamic pro- models31 allow generating the desired UR based on the property
cesses (Figure 2B) more simply as transitions between (distribu- or context of interest (Box 3). Here, high-throughput perturbation
tions of) their representations (Figure 2D). Similarly, decoders screens—based on RNA-seq,28,83,90 optical pooled screens
can take an embedding of biological entities and predict one (OPS),29,39,91 or other technologies—offer a rich resource
or more concrete properties, for example, physical structure, through which the AIVC can be trained to predict these effects.
cell type/state, fitness, expression, or drug response. By conditioning on specific perturbations—such as environ-
The design of a wide array of manipulators provides us with an mental changes, genetic mutations, or chemical treatments—
unprecedented set of tools for modeling cell behavior and dy- the generative model might produce a new UR reflecting the pre-
namics: generative AI approaches, such as diffusion models87 dicted cellular response. This conditioning could be achieved
or autoregressive transformers,88 i.e., model architectures that through learned or pre-computed embeddings of the affected
capture heterogeneity and parameterize continuous time dy- molecular targets. Chemical compounds, small molecules, and
namics, can predict a future state or evolution of a cell or molec- metabolites could be embedded based on their chemical proper-
ular state (Box 3).57,89 Using integrated data from time-lapse im- ties. Additionally, LLMs trained on comprehensive scientific liter-
aging,65 gene expression profiles,83 and other modalities, ature and biological databases, such as Gene Ontology or drug
manipulators can allow inferring the phenotypic progression banks, could further provide a rich contextual background used
from stem cell to differentiated cell, while capturing the influence for conditioning the generative model, e.g., through considering
of both genetic factors and environmental conditions—through wide range of interactions and side effects.
learned interpolations and extrapolations between multi-scale VIs can be designed so that predictions are accompanied by
URs of different cell states. Similarly, they allow predicting the ef- estimates of model uncertainty.92 Under a Bayesian formulation
fect of treatments on patients, given a virtual representation of a of its predictive function, the predictions made for cell perturba-
patient’s molecular profile. tion outcomes could include an uncertainty score, either implic-
Furthermore, variations in cellular URs can be linked to corre- itly via inference, deep kernels,93,94 or through explicit estimation
sponding changes in molecular states or their spatial localiza- of the full posterior over model parameters.95,96 Some practical
tion, influenced by downstream factors, such as genetic variants approaches utilize model ensembles97 or conformal predic-
or functional changes in proteins, which are represented in a tions.98,99 By assigning specific confidence levels to its predic-
lower scale of the AIVC. Leveraging the ability of manipulators tions, the AIVC can call methods for computing the expected
to model temporally resolved molecular and cellular events, de- value of additional data or approximations referred to in machine
coders of the AIVC could potentially identify cellular compo- learning as active learning to guide experimental data collec-
nents, molecular pathways, and their interactions that contribute tion45 for expanding its UR. Alternatively, methods for computing
to each prediction and process. As such, the multi-scale design the expected value of information could be used to guide data
of the AIVC may unveil mechanistic hypotheses of such pro- generation with the goal of optimizing a desired biological prop-
cesses. erty.92 Lastly, through its ability to conduct in silico experiments
Despite the remarkable advancements in protein modeling, and suggest additional informative experiments, the AIVC could
the field continues to struggle in modeling dynamic molecular become an integrative part of lab-in-the-loop schemes. This al-
processes using foundation models. There will likely be areas lows not only for a seamless experimental validation of its predic-
of cell modeling, including dynamics, which pose similar chal- tions but also a sequence of experiments, predictions, and gen-
lenges. For instance, the modeling of intricate networks of tran- erations of hypotheses that gradually improve our systematic
sient and weak molecular interactions, which play a crucial role understanding of molecular circuits that drive biological
in rapid fine-tuning of cellular signaling and formation of cell bio- functions.
logical features such as condensates, may pose similar chal-
lenges. Consequently, we foresee a need for advanced data DATA NEEDS AND REQUIREMENTS
collection and modeling methodologies capable of capturing
the dynamics of cellular processes, akin to those encountered A key consideration for the AIVC is which datasets and modal-
in protein modeling. At the same time, although some functional- ities must be collected to enable its effective construction. Unlike
ities of the AIVC heavily depend on such solutions, others (e.g., traditional experimental design, where data are generated to test
certain predictive functionalities) may be successful even specific scientific hypotheses, data collection for training the
without them. That is one of the appealing properties of multi- AIVC should be focused on ensuring the broad applicability
modal AI models with emergent properties and why developing and generalizability expected of the AIVC. To meet these ambi-
the AIVC now is so compelling. tions, data would ideally span different domains and modalities,
7056 Cell 187, December 12, 2024

---

<!-- Page 13 -->

ll
Perspective OPEN ACCESS
capture the heterogeneity and diversity of biological variability, exceedingly challenging. Because combinatorial possibilities
and enable models to distinguish between technical (measure- quickly expand well beyond what is practical experimentally,
ment) noise, stochastic biological variation, and physiological or even computationally, new methods for their exploration
differences. must be developed.
Data generation will require simultaneous exploration of tem-
poral and physical scales, while allowing for system perturba- How much data are needed to build the AIVC?
tions. Here, classical imaging technologies,65,100,101 including The scale of raw biological data is undeniable, but so is the sheer
live-cell, and newer structural imaging technologies, such as cry- nominal size of even one human cell system, making first princi-
oelectron tomography and soft X-ray tomography,66,102,103 as ple estimates challenging. For instance, the Short Read Archive
well as novel spatial omics technologies,104,105 offer opportu- of biological sequence data holds over 14 petabytes of informa-
nities to model biomolecules and functions across scales. tion,112 which is more than 1,000 times larger than the dataset
Furthermore, biological processes span a vast range of time- used to train ChatGPT.113 Large parts of these data may be
scales, from the fastest reactions happening in picoseconds to redundant or have diminishing returns if used for training, and
a cell division progressing over hours to a day, tumor develop- the scaling laws for models’ performances must be investigated
ment occurring over years, and neurodegeneration over de- thoroughly.
cades. The recent construction of universal cell atlases101,106 In addition to data size, data diversity and quality are critical to
may serve as a powerful resource for modeling cellular behavior ensure model performance.114 Data from humans and model or-
over longer timescales, such as tissue formation. New ap- ganisms, such as mice and Escherichia coli, are unequally repre-
proaches will be needed to build comparable datasets that cap- sented in sequence and literature databases, which when used
ture the behavior of cells on shorter timescales, e.g., through for training, encode strong species biases.114 Other biases, for
methods such as live-cell imaging. Besides molecular measure- example, in terms of sex, specific diseases, or human ancestral
ments, an important aspect of data collection will lie in the mea- populations could also reduce the impact of AIVC models.115
surement of biophysical and biochemical cellular properties to Although efforts on the data side are required, the AI models
provide boundaries of physical and chemical realism to the AIVC. driving the AIVC must be designed to withstand and adapt to
Another important driver for the development of AIVCs will be these challenges, i.e., exhibit robustness in their ability to inte-
multi-modal datasets. For example, datasets that bridge molec- grate datasets of various origins and quality. This is crucial given
ular and spatial scales, such as single-cell transcriptomics data both the rapid pace of advances in lab technologies (which pre-
combined with histology to understand how cells interact and clude standardization on a single platform) and the broad diver-
what molecular signatures underpin the formation of specialized sity of modalities and cell systems that must be encompassed by
spatial niches.107 Further technological development is needed the AIVC. As virtual cell efforts mature, the dialog between the
to collect multi-modal data that better capture the relationship scientists who develop models, those who generate experi-
between molecular signatures, cell behavior, cellular regulation, mental data, and funding organizations must be further inten-
and organization. sified.
Although a core interest of virtual cell modeling will focus on
human datasets for the purpose of understanding disease and MODEL EVALUATION
aiding the development of novel therapeutics, human datasets
are limited in our ability to perform controlled experimentation A more important question for the development of AIVCs may
and perturbations in vivo. not be ‘‘how do we build them?’’ but rather ‘‘how do we build
Here, the field of 3D tissue biology, including culture systems, trust in their competence and fidelity?’’ To this end, a compre-
such as organoids, is emerging as a tool to study the complex- hensive and adaptable benchmarking framework will be needed.
ities of tissue architecture and function108 in a 3D environment, Although various frameworks already exist for tackling specific
while allowing perturbations of the system. Another critical biological questions (for example, protein structure prediction
avenue to surpass this limitation will be to perform diverse, or- models89 were developed in the context of the CASP evaluation
ganism-wide profiles of species spanning evolutionary history, framework), the AIVC will need to demonstrate generalizability
across perturbations and under various conditions.109–111 across numerous biological contexts and downstream tasks. It
Ideally, large datasets could be collected across all three phys- must account for dynamic distributions that evolve due to envi-
ical scales, allowing the AIVC to extend beyond disease research ronmental changes, infections, genetic variants, and other
into other areas such as industrial biotechnology, agricultural such factors causing distribution shifts.116
biotechnology, infectious diseases, and climate change. Howev- Even beyond generalizability, emergent capabilities, such as
er, based on data collection trends for the cellular and multicel- those associated with LLMs, could enable AIVC models to
lular scales, modeling animal cells remains the most realistic. extrapolate to truly out-of-distribution data. In a biological
Finally, a key aspect of biological data generation will be the context it may be difficult to decide how this boundary is defined
exploration of combinatorial spaces: biological spaces are during evaluation. New molecules, new cell states, and even new
commonly high dimensional, and enumerating their variants is species could be considered within the training distribution. A
intractable in general, e.g., when considering all possible vari- new molecule could have homologs, including remote homo-
ants of a genome. Even for combinations of a small number logs, within the dataset. A new cell type or state could execute
of entities, exemplified in the case of enumerating pairs or gene programs and regulatory networks found in existing cell
sets of perturbations,47,90 experimental design becomes types. A new strain could be closely related to existing species
Cell 187, December 12, 2024 7057

---

<!-- Page 14 -->

ll
OPEN ACCESS Perspective
in the training data or live in similar environmental niches. Extrap- original model. Although many capabilities of the AIVC rely on
olation to new data could then be limited to consider only the predictive tasks, generating mechanistic hypotheses could pro-
design of biological entities that do not naturally occur. This vide experimental routes to understand and explore the AIVC’s
type of evaluation is already considered within the molecular predictions further and will be vital for the adoption and use
design space because language-model-created proteins, such of AIVCs.
as esmGFP52 or OpenCrispr1,53 highlight how different they Ultimately, it will be of key interest to build an interactive layer
are from any of their naturally occurring counterparts. If extrapo- for the AIVC that enables researchers of varying expertise to
lation is a goal when designing these models, it is possible that grasp and utilize its predictions effectively. AI agents, built us-
additional inductive biases, fine tuning, or preference optimiza- ing LLMs, could serve as virtual research assistants, providing
tion using biomechanical, physics-based, or mechanistic an intuitive interface for non-experts.46,120 Leveraging their
modeling117 would prove necessary. extensive knowledge of scientific literature, these language
The evaluation of AIVCs should prioritize both generalizability, models can offer deeper insights into the predictions made
as well as discovering new biology. Generalizability measures by the AIVC.
how well the model performs in unseen contexts, such as novel
cell types and genetic backgrounds. It can be evaluated through AN OPEN COLLABORATIVE APPROACH
a cross-modal reconstruction task, such as predicting gene
expression given the morphology of a previously unseen cell or Creating an AIVC requires tremendous investment, diverse
the next image in a sequence of microscopy images of cell state. backgrounds, and many iterations and can only be advanced
Assessing generalizability builds confidence in the AIVC’s ability by a concerted open science effort. As a scientific community,
to capture core biological processes and understand how they we must strive to ensure that both the development and usage
vary across different contexts. Establishing such cross-modal of virtual cells are accessible and responsive to the entire scien-
benchmarks to link scales and modalities in cell biology is of tific community. These efforts would greatly benefit from open
imminent priority to the research community because these data resources and data standards, a collaborative platform
tasks are both biologically useful and well defined. for cell modeling, and, especially, open benchmark datasets
Ultimately, AIVC models should be judged on their ability to and common validation strategies to ensure their biological fidel-
unlock new ways of understanding biology. Such an evaluation ity and real-world utility. Such a collaborative program could
will ensure that model development is aligned with biological greatly accelerate progress across individual efforts and unify
relevance. The most useful initial accomplishments will likely scientific research at a global scale, connecting myriad
be to generate valuable testable hypotheses. For this purpose, smaller-scale efforts.
validation datasets that are related to phenotypes that are exper- To achieve this, multiple key parameters need to be consid-
imentally verifiable may be suitable, such as growth rate of cells, ered. First, we must ensure that AIVCs represent and benefit all
molecular profiles, disrupted protein-protein interactions, or of humanity, with open data that captures human ancestral,
transcription factor binding. sex, and geographic diversity.121 Ensuring that such datasets
As the capabilities of AIVCs improve, we must consider reflect human diversity, while safeguarding individuals’ privacy
whether statistical measures of performance are adequate, or is a principal challenge. Second, as the size of AIVC models in-
if interpretability and biological causality would be core re- creases, the cost of training, fine tuning, or using them as is will
quirements. also grow. Investments in diverse data collection, infrastruc-
ture, and a platform for hosting virtual cell models will be critical
INTERPRETABILITY AND INTERACTION to ensure representation, accessibility, and benefit to the
broader scientific community. The platform should foster
One of the hallmarks of scientific discovery in biology has been open and collaborative development of AIVCs, enabling active
the creation of mechanistic models of a phenomenon under collaboration between biologists, clinicians, statisticians, and
observation. When creating virtual cells, we may have to forgo computer scientists. This platform should facilitate swift itera-
our ability to build fully mechanistic models in favor of learning in- tions between the lab and the modeling environment and offer
teractions that will generalize from data and predict beyond the opportunities to quickly test and benchmark new models.
observations. However, it is still desirable to strive toward Third, synergistic collaboration among stakeholders is needed
increased interpretability. across the biomedical ecosystem, including philanthropy,
Every AIVC prediction could be substantiated with the corre- academia, biopharma, and the AI industry. Pre-competitive
sponding multi-scale interactions that determine resulting collaborations can greatly accelerate our collective progress
states, e.g., understanding how a cellular subsystem or protein toward creating AIVCs. Besides the synchronization with data
complex is disrupted in a diseased tissue can aid development generators and other modeling efforts, collaboration with regu-
of therapeutic interventions.118,119 The modular structure of the latory authorities and bioethics experts are crucial for bench-
AIVC will enable researchers to pinpoint specific genes, pro- marking and establishing new norms that will expedite the
teins, or molecular processes involved in each predicted deployment of AIVCs, while complying with legal requirements
behavior. Patterns in the wiring of large models can also be and setting standards for ethical issues for responsible use of
leveraged to uncover combinatorial biological interactions, virtual cells.
such as those between proteins, which can be projected to This article is intended to serve as a primer for the formation of
interpretable spaces without restricting the generality of the a collaborative research agenda and roadmap for a large-scale,
7058 Cell 187, December 12, 2024

---

<!-- Page 15 -->

ll
Perspective OPEN ACCESS
long-term initiative for developing and implementing AI-powered ACKNOWLEDGMENTS
VCs. If successful, such interactive AIVC models, capable of
simulating cellular biology, have the potential to fundamentally We thank Rok Sosic(cid:1), Charilaos Kanatsoulis, Lata Nair, Kexin Huang, Hanchen
Wang, Minkai Xu, Michael Bereket, Romain Lopez, Takamasa Kudo, Ayush
change how cell biology research is done. We foresee a future
Agrawal, Arnuv Tandon, Mika Jain, Michihiro Yasunaga, Tim Jing, Michael
where AIVC platforms function as open, interconnected hubs Moor, George Crowley, Maria Brbic(cid:3), Andrew Tolopko, Ivana Jelic, Ana-
for collaborative development and broad deployment of cell Maria Istrate, Sara Simmonds, Maximilian Lombardo, Pablo Garcia-Nieto,
models to researchers but also as education hubs delivering Mike Lin, Noorsher Ahmed, William Leineweber, Jan N. Hansen, Orit
training to researchers, as well as providing engagement activ- Rozenblatt-Rosen, Gita Mahmoudabadi, Zoe Piran, Adam Gayoso, Wei
ities for educators, patients, and the public. Ouyang, and Anshul Kundaje for discussions. J.L. was supported by NSF un-
der nos. OAC-1835598 (CINES), CCF-1918940 (Expeditions), and DMS-
2327709 (IHBEM); Stanford Data Applications Initiative; Wu Tsai Neurosci-
OUTLOOK AND REASONS FOR OPTIMISM
ences Institute; Stanford Institute for Human-Centered AI; Chan Zuckerberg
Initiative; Amazon; Genentech; GSK; Hi- Tachi; SAP; and UCB. E.L. was sup-
The genetics and genomics communities have created large ported by Schmidt Futures, the Bridge2AI Program (NIH Common Fund; OT2
reference datasets, such as the human genome project,23 OD032742), the Cancer Cell Map Initiative (NCI Center for Cancer Systems
HapMap,122 the Cancer Genome Atlas (TCGA),123 ENCODE,124 Biology; U54 CA274502), the Wallenberg Foundation (2021.0346), Stanford
the Genotype-Tissue Expression (GTEx) project, 125 the Human Institute for Human-Centered AI, Chan Zuckerberg Initiative, Phil & Penny
Knight Initiative for Brain Resilience at the Wu Tsai Neurosciences Institute,
Protein Atlas (HPA),64,126 the Human Cell Atlas (HCA),24 and a
Danaher, and Param Hansa Philanthropies.
growing number of deeply phenotyped, population-scale bio-
bank efforts.127 Thanks to these projects, massive reference DECLARATION OF INTERESTS
data are now available to train machine learning models.
Although these efforts will continue to grow, they also catalyze C.B. and A.V.R. are employees of Genentech, a member of the Roche Group.
a new, parallel effort: creating a virtual simulation of cell biology, A.V.R. has equity in Roche. A.V.R. was a co-founder and equity holder of
Celsius Therapeutics and is an equity holder in Immunitas. Until July 31,
a new process for scientific inquiry.
2020, A.V.R. was an S.A.B. member of ThermoFisher Scientific, Syros Pharma-
The result, the AIVC has the potential to revolutionize the sci-
ceuticals, Neogene Therapeutics, and Asimov. A.V.R. is a named inventor on
entific process, leading to future breakthroughs in biomedical multiple filed patents related to single-cell and spatial genomics, including for
research, personalized medicine, drug discovery, cell engineer- scRNA-seq, spatial transcriptomics, Perturb-Seq, compressed experiments,
ing, and programmable biology. Acting as a virtual laboratory, and PerturbView. E.L. is an advisor for the Chan-Zuckerberg Initiative Founda-
the AIVC could facilitate a seamless interface between data tion, Element Biosciences, Cartography Biosciences, Pfizer, Santa Ana Bio,
and Pixelgen Technologies. N.J.S. is an employee of EvolutionaryScale, PBC.
derived from in silico experimentation and results from physical
laboratories. As such, we expect the AIVC to contribute to a
REFERENCES
more unified view of biological processes, fostering alignment
among scientists on how emergent properties in biology arise. 1. Slepchenko, B.M., Schaff, J.C., Macara, I., and Loew, L.M. (2003). Quan-
By bridging the worlds of computer systems, modern genera- titative cell biology with the Virtual Cell. Trends Cell Biol. 13, 570–576.
tive AI and AI agents, and biology, the AIVC could ultimately 2. Johnson, G.T., Agmon, E., Akamatsu, M., Lundberg, E., Lyons, B.,
enable scientists to understand cells as information processing Ouyang, W., Quintero-Carmona, O.A., Riel-Mehan, M., Rafelski, S.,
systems and build virtual depictions of life. As the AIVC expands and Horwitz, R. (2023). Building the next generation of virtual cells to un-
the understanding of cellular and molecular systems, it will also derstand cellular biology. Biophys. J. 122, 3560–3569.
increasingly allow us to program them and design novel syn- 3. Marx, V. (2023). How to build a virtual embryo. Nat. Methods 20,
1838–1843.
thetic ones. AI models have already been used to design new
CRISPR enzymes,53 functional proteins,128 and even entire pro- 4. Goldberg, A.P., Szigeti, B., Chew, Y.H., Sekar, J.A., Roth, Y.D., and Karr,
karyotic genomes.51 The rapid progress in the precision of cell J.R. (2018). Emerging whole-cell modeling principles and methods. Curr.
Opin. Biotechnol. 51, 97–102.
and genome engineering tools will accelerate this shift and
5. Georgouli, K., Yeom, J.-S., Blake, R.C., and Navid, A. (2023). Multi-scale
different instantiations of the AIVC will compete in their ability
models of whole cells: progress and challenges. Front. Cell Dev. Biol. 11,
to engineer new, functional biology capabilities as much as in 1260507.
their ability to represent and simulate biology.
6. Marucci, L., Barberis, M., Karr, J., Ray, O., Race, P.R., de Souza Andrade,
Finally, we staunchly advocate the role for open science ap- M., Grierson, C., Hoffmann, S.A., Landon, S., Rech, E., et al. (2020). Com-
proaches, where the scientific community readily shares data, puter-aided whole-cell design: Taking a holistic approach by integrating
models, and benchmarks, where findings and insights are synthetic with systems biology. Front. Bioeng. Biotechnol. 8, 942.
contextualized, and where a climate of perpetual improvement 7. Lauffenburger, D.A., and Linderman, J.J. (1996). Receptors: models for
is fostered. We welcome and encourage all stakeholders binding, trafficking, and signaling (Oxford University Press).
across sectors and domains to engage in this endeavor. With 8. Karr, J.R., Sanghvi, J.C., Macklin, D.N., Gutschow, M.V., Jacobs, J.M.,
Bolival, B., Assad-Garcia, N., Glass, J.I., and Covert, M.W. (2012). A
a massive scientific undertaking and shared goals, open
whole-cell computational model predicts phenotype from genotype.
sharing of insights, and the power of safe, ethical, and reliable
Cell 150, 389–401.
AI, we believe that we are stepping into a new era of scientific
9. Mangan, S., and Alon, U. (2003). Structure and function of the feed-for-
exploration and understanding. The confluence of AI and
ward loop network motif. Proc. Natl. Acad. Sci. USA 100, 11980–11985.
biology, as encapsulated by AIVCs, signals a paradigm shift
10. Zopf, C.J., Quinn, K., Zeidman, J., and Maheshri, N. (2013). Cell-cycle
in biology and shines as a beacon of optimism for unraveling dependence of transcription dominates noise in gene expression.
multiple mysteries of the cell. PLoS Comput. Biol. 9, e1003161.
Cell 187, December 12, 2024 7059

---

<!-- Page 16 -->

ll
OPEN ACCESS Perspective
11. Eling, N., Morgan, M.D., and Marioni, J.C. (2019). Challenges in 30. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez,
measuring and understanding biological noise. Nat. Rev. Genet. 20, A.N., Kaiser, L., and Polosukhin, I. (2017). Attention is all you need.
536–548. Adv. Neural Inf. Process. Syst. 30.
12. Hellweger, F.L., Clegg, R.J., Clark, J.R., Plugge, C.M., and Kreft, J.-U. 31. Rombach, R., Blattmann, A., Lorenz, D., Esser, P., and Ommer, B. High-
(2016). Advancing microbial sciences by individual-based modelling. resolution image synthesis with latent diffusion models. In IEEE Confer-
Nat. Rev. Microbiol. 14, 461–471. ence on Computer Vision and Pattern Recognition (CVPR),
13. Gorochowski, T.E. (2016). Agent-based modelling in synthetic biology. 10684–10695.
Essays Biochem. 60, 325–336. 32. Jumper, J., Evans, R., Pritzel, A., Green, T., Figurnov, M., Ronneberger,
(cid:1)
14. Thiele, I., Jamshidi, N., Fleming, R.M., and Palsson, B. (2009). Genome- O., Tunyasuvunakool, K., Bates, R., Zı´dek, A., Potapenko, A., et al.
scale reconstruction of Escherichia coli’s transcriptional and translational (2021). Highly accurate protein structure prediction with AlphaFold. Na-
machinery: a knowledge base, its mathematical formulation, and its func- ture 596, 583–589.
tional characterization. PLoS Comput. Biol. 5, e1000312.
33. Baek, M., DiMaio, F., Anishchenko, I., Dauparas, J., Ovchinnikov, S., Lee,
15. Odell, G.M., and Foe, V.E. (2008). An agent-based model contrasts G.R., Wang, J., Cong, Q., Kinch, L.N., Schaeffer, R.D., et al. (2021). Ac-
opposite effects of dynamic and stable microtubules on cleavage furrow curate prediction of protein structures and interactions using a three-
positioning. J. Cell Biol. 183, 471–483. track neural network. Science 373, 871–876.
16. Popov, K., Komianos, J., and Papoian, G.A. (2016). MEDYAN: mechano- 34. Lin, Z., Akin, H., Rao, R., Hie, B., Zhu, Z., Lu, W., Smetanin, N., Verkuil, R.,
chemical simulations of contraction and polarity alignment in actomyosin Kabeli, O., Shmueli, Y., et al. (2023). Evolutionary-scale prediction of
networks. PLoS Comput. Biol. 12, e1004877. atomic-level protein structure with a language model. Science 379,
17. Burke, P.E.P., Campos, C.B.L., Costa, L.D.F., and Quiles, M.G. (2020). 1123–1130.
M. G. A biochemical network modeling of a whole-cell. Sci. Rep.
35. Gomes, J., Ramsundar, B., Feinberg, E.N., and Pande, V.S. (2017).
10, 13303.
Atomic convolutional networks for predicting protein-ligand binding af-
18. Li, G., Liu, L., Du, W., and Cao, H. (2023). Local flux coordination and finity. Preprint at arXiv.
global gene expression regulation in metabolic modeling. Nat. Commun.
36. Cunningham, J.M., Koytiger, G., Sorger, P.K., and AlQuraishi, M. (2020).
14, 5700.
Biophysical prediction of protein–peptide interactions and signaling net-
19. Fang, X., Lloyd, C.J., and Palsson, B.O. (2020). Reconstructing organ-
works using machine learning. Nat. Methods 17, 175–183.
isms in silico: genome-scale models and their emerging applications.
Nat. Rev. Microbiol. 18, 731–743. 37. Torng, W., and Altman, R.B. (2019). High precision protein functional site
detection using 3D convolutional neural networks. Bioinformatics 35,
20. Stevens, J.A., Gru¨ newald, F., van Tilburg, P.A.M., Ko¨ nig, M., Gilbert,
1503–1512.
B.R., Brier, T.A., Thornburg, Z.R., Luthey-Schulten, Z., and Marrink,
S.J. (2023). Molecular dynamics simulation of an entire cell. Front. 38. Corso G., Sta¨ rk H., Jing B., Barzilay R., and Jaakkola T. (2023). DiffDock:
Chem. 11, 1106495. Diffusion Steps, Twists, and Turns for Molecular Docking The Eleventh
International Conference on Learning Representations.
21. Maritan, M., Autin, L., Karr, J., Covert, M.W., Olson, A.J., and Goodsell,
D.S. (2022). Building structural models of a whole mycoplasma cell. 39. Kudo, T., Meireles, A.M., Moncada, R., Chen, Y., Wu, P., Gould, J., Hu,
J. Mol. Biol. 434, 167351. X., Kornfeld, O., Jesudason, R., Foo, C., et al. (2024). Multiplexed, im-
22. Ahn-Horst, T.A., Mille, L.S., Sun, G., Morrison, J.H., and Covert, M.W. age-based pooled screens in primary cells and tissues with perturbview.
(2022). An expanded whole-cell model of E. coli links cellular physiology Nat. Biotechnol., 1–10.
with mechanisms of growth rate control. npj Syst. Biol. Appl. 8, 30. 40. Roohani, Y., Huang, K., and Leskovec, J. (2023). Predicting transcrip-
23. Venter, J.C., Adams, M.D., Myers, E.W., Li, P.W., Mural, R.J., Sutton, tional outcomes of novel multigene perturbations with GEARS. Nat. Bio-
G.G., Smith, H.O., Yandell, M., Evans, C.A., Holt, R.A., et al. (2001). technol. 42, 927–935.
The sequence of the human genome. Science 291, 1304–1351. 41. Bunne, C., Stark, S.G., Gut, G., Del Castillo, J.S., Levesque, M., Leh-
24. Regev, A., Teichmann, S.A., Lander, E.S., Amit, I., Benoist, C., Birney, E., mann, K.-V., Pelkmans, L., Krause, A., and Ratsch, G. (2023). Learning
Bodenmiller, B., Campbell, P., Carninci, P., Clatworthy, M., et al. (2017). single-cell perturbation responses using neural optimal transport. Nat.
The human cell atlas. eLife 6, e27041. Methods 20, 1759–1768.
25. CZI Single-Cell Biology Program, Abdulla, S., Aevermann, B., Assis, P., 42. Lotfollahi, M., Klimovskaia Susmelj, A., De Donno, C., Hetzel, L., Ji, Y.,
Badajoz, S., Bell, S.M., Bezzi, E., Batuhan, C., Jim, C., Chambers, S., Ibarra, I.L., Srivatsan, S.R., Naghipourfar, M., Daza, R.M., Martin, B.,
et al. (2023). CZ CELL3GENE discover: A single- cell data platform for et al. (2023). Predicting cellular responses to complex perturbations in
scalable exploration, analysis and modeling of aggregated data. Preprint high-throughput screens. Mol. Syst. Biol. 19, e11517.
at bioRxiv.
43. Bunne, C., Krause, A., and Cuturi, M. (2022). Supervised Training of Con-
26. Heimberg, G., Kuo, T., DePianto, D., Heigl, T., Nathaniel, D., Salem, O., ditional Monge Maps. Adv. Neural Inf. Process. Syst. 35, 6859–6872.
Scalia, G., Biancalani, T., Turley, S., Rock, J., et al. (2023). Scalable
44. Bereket, M., and Karaletsos, T. (2024). Modelling Cellular Perturbations
querying of human cell atlases via a foundational model reveals com-
with the Sparse Additive Mechanism Shift Variational Autoencoder.
monalities across fibrosis-associated macrophages. Preprint at bioRxiv.
Adv. Neural Inf. Process. Syst. 36.
27. Dixit, A., Parnas, O., Li, B., Chen, J., Fulco, C.P., Jerby-Arnon, L., Marja-
novic, N.D., Dionne, D., Burks, T., Raychowdhury, R., et al. (2016). Per- 45. Huang, K., Huang, K., Lopez, R., Hutter, J.-C., Kudo, T., Rios, A., and Re-
turb-Seq: dissecting molecular circuits with scalable single-cell RNA gev, A. (2023). Sequential Optimal Experimental De- sign of Perturbation
profiling of pooled genetic screens. Cell 167, 1853–1866.e17. Screens Guided by Multi-modal Priors. In International Conference on
Research in Computational Molecular Biology (Springer Nature),
28. Srivatsan, S.R., McFaline-Figueroa, J.L., Ramani, V., Saunders, L., Cao,
pp. 17–37.
J., Packer, J., Pliner, H.A., Jackson, D.L., Daza, R.M., Christiansen, L.,
et al. (2020). Massively multiplex chemical transcriptomics at single- 46. Roohani, Y.H., Vora, J., Huang, Q., Liang, P., and Leskovec, J. (2024).
cell resolution. Science 367, 45–51. BioDiscoveryAgent: An AI Agent for Designing Genetic Perturbation Ex-
periments Preprint at arXiv.
29. Feldman, D., Funk, L., Le, A., Carlson, R.J., Leiken, M.D., Tsai, F., Soong,
B., Singh, A., and Blainey, P.C. (2022). Pooled genetic perturbation 47. Cleary, B., and Regev, A. (2024). The necessity and power of random,
screens with image-based phenotypes. Nat. Protoc. 17, 476–512. undersampled experiments in biology. Preprint at arXiv.
7060 Cell 187, December 12, 2024

---

<!-- Page 17 -->

ll
Perspective OPEN ACCESS
48. Ji, Y., Zhou, Z., Liu, H., and Davuluri, R.V. (2021). DNABERT: pre-trained 66. Nogales, E., and Mahamid, J. (2024). Bridging structural and cell biology
Bidirectional Encoder Representations from Transformers model for with cryo-electron microscopy. Nature 628, 47–56.
DNA-language in genome. Bioinformatics 37, 2112–2120. 67. Bauda, E., Gallet, B., Moravcova, J., Effantin, G., Chan, H., Novacek, J.,
49. Brandes, N., Ofer, D., Peleg, Y., Rappoport, N., and Linial, M. (2022). Pro- Jouneau, P.H., Rodrigues, C.D.A., Schoehn, G., Moriscot, C., et al.
teinBERT: a universal deep-learning model of pro- tein sequence and (2024). Ultrastructure of macromolecular assemblies contributing to bac-
function. Bioinformatics 38, 2102–2110. terial spore resistance revealed by in situ cryo-electron tomography. Nat.
Commun. 15, 1376.
50. Celaj, A., Gao, A.J., Lau, T.T.Y., Holgersen, E.M., Lo, A., Lodaya, V., Cole,
C.B., Denroche, R.E., Spickett, C., Wagih, O., et al. (2023). An RNA foun- 68. Lelek, M., Gyparaki, M.T., Beliu, G., Schueder, F., Griffie´ , J., Manley, S.,
dation model enables discovery of disease mechanisms and candidate Jungmann, R., Sauer, M., Lakadamyali, M., and Zimmer, C. (2021). Sin-
therapeutics. Preprint at bioRxiv. gle-molecule localization microscopy. Nat. Rev. Methods Primers 1, 39.
51. Nguyen, E., Poli, M., Durrant, M.G., Kang, B., Katrekar, D., Li, D.B., Bar- 69. Mo¨ ckl, L., and Moerner, W.E. (2020). Super-resolution microscopy with
tie, L.J., Thomas, A.W., King, S.H., Brixi, G., et al. (2024). Sequence single molecules in biology and beyond–essentials, current trends, and
modeling and design from molecular to genome scale with Evo. Science future challenges. J. Am. Chem. Soc. 142, 17828–17844.
386, eado9336. 70. Cesnik, A., Schaffer, L.V., Gaur, I., Jain, M., Ideker, T., and Lundberg, E.
52. Hayes, T., Rao, R., Akin, H., Sofroniew, N.J., Oktay, D., Lin, Z., Verkuil, R., (2024). Mapping the multiscale proteomic Or- ganization of cellular and
Tran, V.Q., Deaton, J., Wiggert, M., et al. (2024). Simulating 500 million Disease Phenotypes. Annu. Rev. Biomed. Data Sci. 7, 369–389.
years of evolution with a language model. Preprint at bioRxiv. 71. Qin, Y., Huttlin, E.L., Winsnes, C.F., Gosztyla, M.L., Wacheul, L., Kelly,
M.R., Blue, S.M., Zheng, F., Chen, M., Schaffer, L.V., et al. (2021). A
53. Ruffolo, J.A., Nayfach, S., Gallagher, J., Bhatnagar, A., Beazer, J., Hus-
multi-scale map of cell structure fusing protein images and interactions.
sain, R., Russ, J., Yip, J., Hill, E., Pacesa, M., et al. (2024). Design of highly
Nature 600, 536–542.
functional genome editors by modeling the universe of CRISPR-cas se-
quences. Preprint at bioRxiv. 72. Dosovitskiy, A. (2020). An image is worth 16x16 words: transformers for
image recognition at scale. Preprint at arXiv.
54. Peng, Z., Schussheim, B., and Chatterjee, P. (2024). PTM-mamba: a
PTM-aware protein language model with bidirectional gated mamba 73. Fukushima, K. (1980). Neocognitron: a self organizing neural network
blocks. Preprint at bioRxiv. model for a mechanism of pattern recognition unaffected by shift in po-
sition. Biol. Cybern. 36, 193–202.
55. Dai, B., Mattox, D.E., and Bailey-Kellogg, C. (2021). Atten- tion please:
modeling global and local context in glycan structure-function relation- 74. LeCun, Y., and Yoshua, B. (1995). Convolutional networks for images,
ships. Preprint at bioRxiv. speech, and time series. The Handbook of Brain Theory and Neural Net-
works 3361, 255–258.
56. Yu, T., Yao, T., Sun, Z., Shi, F., Zhang, L., Lyu, K., Xuan, B., Liu, A., Zhang,
75. Bao, Y., Sivanandan, S., and Karaletsos, T. (2023). Channel Vision Trans-
X., Zou, J., et al. (2024). LipidBERT: A Lipid Language Model Pre- trained
formers: An Image Is Worth c x 16 x 16 WordsThe Twelfth. International
on METiS de novo Lipid Library. Preprint at arXiv.
Conference on Learning Representations 4.
57. Krishna, R., Wang, J., Ahern, W., Sturmfels, P., Venkatesh, P., Kalvet, I.,
76. Kraus, O., Kenyon-Dean, K., Saberian, S., Fallah, M., McLean, P., Leung,
Lee, G.R., Morey-Burrows, F.S., Anishchenko, I., Humphreys, I.R., et al.
J., Sharma, V., Khan, A., Balakrishnan, J., Celik, S., et al. (2024). Masked
(2024). Generalized biomolecular modeling and design with
autoencoders for microscopy are scalable learners of cellular biology. In
RoseTTAFold All-Atom. Science 384, eadl2528.
IEEE Conference on Computer Vision and Pattern Recognition (CVPR),
58. Rosen, Y., Brbic(cid:3), M., Roohani, Y., Swanson, K., Li, Z., and Leskovec, J. pp. 11757–11768.
(2024). Toward universal cell embeddings: integrating single-cell RNA-
77. Bao, Y., and Karaletsos, T. (2023). Contextual vision transformers for
seq datasets across species with Saturn. Nat. Methods 21, 1492–1500.
robust representation learning. Preprint at arXiv.
59. Rosen, Y., Roohani, Y., Agrawal, A., Samotorc(cid:1)an, L., Tabula Sapiens
78. Lopez, R., Regier, J., Cole, M.B., Jordan, M.I., and Yosef, N. (2018). Deep
Consortium, Quake, S.R., and Leskovec, J. (2023). Universal cell embed-
generative modeling for single-cell transcriptomics. Nature Methods 15,
dings: A foundation model for cell biology. Preprint at bioRxiv.
1053–1058.
60. Chen, Y., and Zou, J. (2024). GenePT: A Simple but Effective Foun- da-
79. Theodoris, C.V., Xiao, L., Chopra, A., Chaffin, M.D., Al Sayed, Z.R., Hill,
tion Model for Genes and Cells Built from ChatGPT. Preprint at bioRxiv.
M.C., Mantineo, H., Brydon, E.M., Zeng, Z., Liu, X.S., et al. (2023). Trans-
61. Mahdessian, D., Cesnik, A.J., Gnann, C., Danielsson, F., Stenstro¨ m, L., fer learning enables predictions in network biology. Nature 618, 616–624.
Arif, M., Zhang, C., Le, T., Johansson, F., Schutten, R., et al. (2021). 80. Kobayashi-Kirschvink, K.J., Comiter, C.S., Gaddam, S., Joren, T., Grody,
Spatiotemporal dissection of the cell cycle with single-cell proteogenom- E.I., Ounadjela, J.R., Zhang, K., Ge, B., Kang, J.W., Xavier, R.J., et al.
ics. Nature 590, 649–654. (2024). Prediction of single-cell RNA expression profiles in live cells by
62. Chandrasekaran, S.N., Cimini, B.A., Goodale, A., Miller, L., Kost-Ali- Raman microscopy with Raman2RNA. Nat. Biotechnol. 42, 1726–1734.
mova, M., Jamali, N., Doench, J.G., Fritchman, B., Skepner, A., Melan- 81. Ryu, J., Lopez, R., Bunne, C., and Regev, A. (2024). Cross-modality
son, M., et al. (2024). Three million images and mor- phological profiles matching and prediction of perturbation responses with labeled
of cells treated with matched chemical and genetic perturbations. Nat. Gromov-Wasserstein optimal transport. Preprint at arXiv.
Methods 21, 1114–1121.
82. Saar, K.L., Scrutton, R.M., Bloznelyte, K., Morgunov, A.S., Good, L.L.,
63. Carlson, R.J., Leiken, M.D., Guna, A., Hacohen, N., and Blainey, P.C. Lee, A.A., Teichmann, S.A., and Knowles, T.P.J. (2024). Protein Conden-
(2023). A genome-wide optical pooled screen reveals regulators of sate Atlas from predic- tive models of heteromolecular condensate
cellular antiviral responses. Proc. Natl. Acad. Sci. USA 120, composition. Nat. Commun. 15, 5418.
e2210623120.
83. Macosko, E.Z., Basu, A., Satija, R., Nemesh, J., Shekhar, K., Goldman,
64. Thul, P.J., A˚ kesson, L., Wiking, M., Mahdessian, D., Geladaki, A., Ait Blal, M., Tirosh, I., Bialas, A., Kamitaki, N., Martersteck, E., et al. (2015). Highly
H., Alm, T., Asplund, A., Bjo¨ rk, L., Breckels, L.M., et al. (2017). A subcel- parallel genome-wide expression profiling of individual cells using nano-
lular map of the human proteome. Science 356, eaal3321. liter droplets. Cell 161, 1202–1214.
65. McDole, K., Guignard, L., Amat, F., Berger, A., Malandain, G., Royer, 84. Sta˚ hl, P.L., Salme´ n, F., Vickovic, S., Lundmark, A., Navarro, J.F., Mag-
L.A., Turaga, S.C., Branson, K., and Keller, P.J. (2018). In toto imaging nusson, J., Giacomello, S., Asp, M., Westholm, J.O., Huss, M., et al.
and reconstruction of post-implantation mouse development at the sin- (2016). Visualization and analysis of gene expression in tissue sections
gle-cell level. Cell 175, 859–876.e33. by spatial transcriptomics. Science 353, 78–82.
Cell 187, December 12, 2024 7061

---

<!-- Page 18 -->

ll
OPEN ACCESS Perspective
85. Lundberg, E., and Borner, G.H.H. (2019). Spatial proteomics: a powerful 105. Vandereyken, K., Sifrim, A., Thienpont, B., and Voet, T. (2023). Methods
discovery tool for cell biology. Nat. Rev. Mol. Cell Biol. 20, 285–302. and applications for single-cell and spatial multi-omics. Nat. Rev. Genet.
86. Marconato, L., Palla, G., Yamauchi, K.A., Virshup, I., Heidari, E., Treis, T., 24, 494–515.
Vierdag, W.M., Toth, M., Stockhaus, S., Shrestha, R.B., et al. (2024). Spa- 106. Tabula Sapiens Consortium*, Jones, R.C., Karkanias, J., Krasnow, M.A.,
tialData: an open and universal data framework for spatial omics. Nat. Pisco, A.O., Quake, S.R., Salzman, J., Yosef, N., Bulthaup, B., Brown, P.,
Methods. https://doi.org/10.1038/s41592-024-02212-x. et al. (2022). The tabula sapiens: A multiple-organ, single-cell transcrip-
87. Somnath, V.R., Pariset, M., Hsieh, Y.-P., Martinez, M.R., Krause, A., and tomic atlas of humans. Science 376, eabl4896.
Bunne, C. (2023). Aligned Diffusion Schro¨ dinger Bridges. In Uncertainty 107. He, B., Bergenstra˚ hle, L., Stenbeck, L., Abid, A., Andersson, A., Borg, A˚ .,
in Artificial Intelligence, pp. 1985–1995. Maaskola, J., Lundeberg, J., and Zou, J. (2020). Integrating spatial gene
88. Katharopoulos, A., Vyas, A., Pappas, N., and Fleuret, F. (2020). Fast au- expression and breast tumour morphology via deep learning. Nat. Bio-
toregressive transformers with linear attention. In International Confer- med. Eng. 4, 827–834.
ence on Machine Learning. 108. Bock, C., Boutros, M., Camp, J.G., Clarke, L., Clevers, H., Knoblich, J.A.,
89. Abramson, J., Adler, J., Dunger, J., Evans, R., Green, T., Pritzel, A., Ron- Liberali, P., Regev, A., Rios, A.C., Stegle, O., et al. (2021). The organoid
neberger, O., Willmore, L., Ballard, A.J., Bambrick, J., et al. (2024). Accu- cell atlas. Nat. Biotechnol. 39, 13–17.
rate structure prediction of biomolecular interactions with AlphaFold 3. 109. Tabula; Muris Consortium; Overall coordination; Logistical coordination;
Nature 630, 493–500. Organ collection and processing; Library preparation and sequencing;
90. Norman, T.M., Horlbeck, M.A., Replogle, J.M., Ge, A.Y., Xu, A., Jost, M., Computational data analysis; Cell type annotation; Writing group; Sup-
Gilbert, L.A., and Weissman, J.S. (2019). Exploring genetic interaction plemental text writing group; Principal investigators (2018). Single-cell
manifolds constructed from rich single-cell phenotypes. Science 365, transcriptomics of 20 mouse organs creates a tabula muris. Nature
786–793. 562, 367–372.
91. Lawson, M.J., Camsund, D., Larsson, J., Baltekin, O¨ ., Fange, D., and Elf, 110. Li, H., Janssens, J., De Waegeneer, M., Kolluru, S.S., Davie, K., Gardeux,
J. (2017). In situ genotyping of a pooled strain library after characterizing V., Saelens, W., David, F.P.A., Brbic(cid:3), M., Spanier, K., et al. (2022). Fly Cell
complex phenotypes. Mol. Syst. Biol. 13, 947. Atlas: A single-nucleus transcriptomic atlas of the adult fruit fly. Science
92. Papamarkou, T., Skoularidou, M., Palla, K., Aitchison, L., Arbel, J., Dun- 375, eabk2432.
son, D., Filliponne, M., Fortuin, V., Hennig, P., Hernandez-Lobato, J.M., 111. Lange, M., Granados, A., Vijaykumar, S., Bragantini, J., Ancheta, S., San-
et al. (2024). Position: bayesian deep learning is needed in the age of thosh, S., Borja, M., Kobayashi, H., McGeever, E., Solak, A.C., et al.
large-scale AI. In Forty-First International Conference on Machine (2023). Zebrahub – Multimodal zebrafish Developmental Atlas Reveals
Learning. the State Transition Dynamics of Late Vertebrate Pluripotent Axial Pro-
93. D’Angelo, F., and Fortuin, V. (2021). Wenzel F.On Stein Variational Neural genitors. Preprint at bioRxiv.
Network. Ensembles Preprint at arXiv. 112. Katz, K., Shutov, O., Lapoint, R., Kimelman, M., Brister, J.R., and O’Sul-
94. Ober, S.W., Rasmussen, C.E., and van der Wilk, M. (2021). The promises livan, C. (2022). The Sequence Read Archive: a decade more of explosive
and pitfalls of deep kernel learning. In Conference on Uncertainty in Arti- growth. Nucleic Acids Res. 50, D387–D390.
ficial Intelligence, pp. 1206–1216.
113. Achiam, J., et al. (2023). GPT-4 technical report. Preprint at arXiv.
95. Karaletsos, T. (2020). Bui T.D.Hierarchical Gaussian Process Priors for
114. Ding, F., and Steinhardt, J.N. (2024). Protein language models are biased
Bayesian Neural Network Weights. Adv. Neural Inf. Process. Syst. 33,
by unequal sequence sampling across the tree of life. Preprint at bioRxiv.
17141–17152.
115. Liao, W.-W., Asri, M., Ebler, J., Doerr, D., Haukness, M., Hickey, G., Lu,
96. Kapoor, S., Maddox, W.J., Izmailov, P., and Wilson, A.G. (2022). On un-
S., Lucas, J.K., Monlong, J., Abel, H.J., et al. (2023). A draft human pan-
certainty, tempering, and data augmentation in bayesian classification.
genome reference. Nature 617, 312–324.
Adv. Neural Inf. Process. Syst. 35, 18211–18225.
116. Liu, J., Shen, Z., He, Y., Zhang, X., Xu, R., Yu, H., and Cui, P. (2021). To-
97. Lakshminarayanan, B., Pritzel, A., and Blundell, C. (2017). Simple and
wards out-of-distribution generalization: A survey. Preprint at arXiv.
Scalable Predictive Uncertainty Estimation using Deep Ensembles.
Adv. Neural Inf. Process. Syst. 30. 117. Nisonoff, H., Wang, Y., and Listgarten, J. (2023). Coherent blend- ing of
biophysics-based knowledge with bayesian neural networks for robust
98. Angelopoulos, A.N., and Bates, S. (2021). A gentle introduction to
protein property prediction. ACS Synth. Biol. 12, 3242–3251. https://
conformal prediction and distribution-free uncertainty quantification.
doi.org/10.1021/acssynbio.3c00217.
Preprint at arXiv.
118. Zheng, F., Kelly, M.R., Ramms, D.J., Heintschel, M.L., Tao, K., Tutuncuo-
99. Cherian, J.J., Gibbs, I., and Cande` s, E.J. (2024). Large language model
glu, B., Lee, J.J., Ono, K., Foussard, H., Chen, M., et al. (2021). Interpre-
validity via enhanced conformal prediction methods. Preprint at arXiv.
tation of cancer mutations using a multiscale map of protein systems.
100. Cho, N.H., Cheveralls, K.C., Brunner, A.D., Kim, K., Michaelis, A.C., Ra-
Science 374, eabf3067.
ghavan, P., Kobayashi, H., Savy, L., Li, J.Y., Canaj, H., et al. (2022). Open-
Cell: endogenous tagging for the cartography of human cellular organiza- 119. Ma, J., Yu, M.K., Fong, S., Ono, K., Sage, E., Demchak, B., Sharan, R.,
tion. Science 375, eabi6983. and Ideker, T. (2018). Using deep learning to model the hierarchical struc-
ture and function of a cell. Nat. Methods 15, 290–298.
101. Uhle´ n, M., Fagerberg, L., Hallstro¨ m, B.M., Lindskog, C., Oksvold, P.,
Mardinoglu, A., Sivertsson, A˚ ., Kampf, C., Sjo¨ stedt, E., Asplund, A., 120. Gao, S., Fang, A., Huang, Y., Giunchiglia, V., Noori, A., Schwarz, J.R., Ek-
et al.. (2015). Proteomics. Tissue-based map of the human proteome. tefaie, Y., Kondic, J., and Zitnik, M. (2024). Empowering biomedical dis-
Science 347, 1260419. covery with AI agents. Cell 187, 6125–6151.
102. Berger, C., Premaraj, N., Ravelli, R.B.G., Knoops, K., Lo´ pez-Iglesias, C., 121. Hurrell, T., Naidoo, J., Ntlhafu, T., and Scholefield, J. (2024). An African
and Peters, P.J. (2023). Cryo-electron tomography on focused ion beam perspective on genetically diverse human induced pluripotent stem cell
lamellae transforms structural cell biology. Nat. Methods 20, 499–511. lines. Nat. Commun. 15, 8581.
103. Loconte, V., Chen, J.H., Vanslembrouck, B., Ekman, A.A., McDermott, 122. Gibbs, R.A., Belmont, J.W., Hardenbol, P., Willis, T.D., Yu, F.L., Yang,
G., Le Gros, M.A., and Larabell, C.A. (2023). Soft X-ray tomograms pro- H.M., Ch’ang, L.Y., Huang, W., Shen, B., Tam, Y., et al. (2003). The inter-
vide a structural basis for whole-cell modeling. FASEB J. 37, e22681. national HapMap project. Nature 5, 467–475.
104. Moffitt, J.R., Lundberg, E., and Heyn, H. (2022). The emerging landscape 123. Cancer; Genome; Atlas; Research Network, Weinstein, J.N., Collisson,
of spatial profiling technologies. Nat. Rev. Genet. 23, 741–759. E.A., Mills, G.B., Shaw, K.R.M., Ozenberger, B.A., Ellrott, K., Shmulevich,
7062 Cell 187, December 12, 2024

---

<!-- Page 19 -->

ll
Perspective OPEN ACCESS
I., Sander, C., and Stuart, J.M. (2013). The cancer genome atlas pan-can- 140. Rajewsky, N., Almouzni, G., Gorski, S.A., Aerts, S., Amit, I., Bertero,
cer analysis project. Nat. Genet. 45, 1113–1120. M.G., Bock, C., Bredenoord, A.L., Cavalli, G., Chiocca, S., et al. (2020).
124. ENCODE Project Consortium (2012). An integrated encyclopedia of DNA Lifetime and improving European healthcare through cell-based inter-
elements in the human genome. Nature 489, 57–74. ceptive medicine. Nature 587, 377–386.
125. Lonsdale, J., Thomas, J., Salvatore, M., Phillips, R., Lo, E., Shad, S., 141. Alix-Panabie` res, C., and Pantel, K. (2021). Liquid biopsy: from discovery
Hasz, R., Walters, G., Garcia, F., Young, N., and Foster, B. (2013). The to clinical application. Cancer Discov. 11, 858–873.
Genotype-Tissue Expression (GTEx) project. Nat. Genet. 45, 580–585. 142. Vaishnav, E.D., de Boer, C.G., Molinet, J., Yassour, M., Fan, L., Adiconis,
126. Ponte´ n, F., Jirstro¨ m, K., and Uhlen, M. (2008). The Human Protein Atlas–a X., Thompson, D.A., Levin, J.Z., Cubillos, F.A., and Regev, A. (2022). The
tool for pathology. J. Pathol. 216, 387–393. evolution, evolvability and engineering of gene regulatory DNA. Nature
127. Downey, P., and Peakman, T.C. (2008). Design and implementation of a 603, 455–463.
high-throughput biological sample processing facil- ity using modern 143. Go´ mez-de-Mariscal, E., Garcı´a-Lo´ pez-de-Haro, C., Ouyang, W., Donati,
manufacturing principles. Int. J. Epidemiol. 37 (Suppl 1), i46–i50. L., Lundberg, E., Unser, M., Mun˜ oz-Barrutia, A., and Sage, D. (2021).
128. Madani, A., Krause, B., Greene, E.R., Subramanian, S., Mohr, B.P., Hol- DeepImageJ: A user-friendly environment to run deep learning models
ton, J.M., Olmos, J.L., Xiong, C., Sun, Z.Z., Socher, R., et al. (2023). Large in ImageJ. Nat. Methods 18, 1192–1195.
language models generate func- tional protein sequences across diverse 144. Le, T., Winsnes, C.F., Axelsson, U., Xu, H., Mohanakrishnan Kaimal, J.,
families. Nat. Biotechnol. 41, 1099–1106. Mahdessian, D., Dai, S., Makarov, I.S., Ostankovich, V., Xu, Y., et al.
129. Nelson, M.R., Tipney, H., Painter, J.L., Shen, J., Nicoletti, P., Shen, Y., (2022). Analysis of the human protein atlas weakly supervised single-
Floratos, A., Sham, P.C., Li, M.J., Wang, J., et al. (2015). The support cell classification competition. Nat. Methods 19, 1221–1229.
of human genetic evidence for approved drug indications. Nat. Genet. 145. Chen, R.J., Ding, T., Lu, M.Y., Williamson, D.F.K., Jaume, G., Song, A.H.,
47, 856–860. Chen, B., Zhang, A., Shao, D., Shaban, M., et al. (2024). Towards a gen-
130. Mason, C., Brindley, D.A., Culme-Seymour, E.J., and Davie, N.L. (2011). eral-purpose foundation model for computational pathology. Nat. Med.
Cell therapy industry: billion dollar global business with unlimited poten- 30, 850–862.
tial. Regen. Med. 6, 265–272.
146. Moen, E., Bannon, D., Kudo, T., Graf, W., Covert, M., and Van Valen, D.
131. Bashor, C.J., Hilton, I.B., Bandukwala, H., Smith, D.M., and Veiseh, O. (2019). Deep learning for cellular image analysis. Nat. Methods 16,
(2022). Engineering the next generation of cell-based therapeutics. Nat. 1233–1246.
Rev. Drug Discov. 21, 655–675. (cid:1)
147. Avsec, Z., Weilert, M., Shrikumar, A., Krueger, S., Alexandari, A., Dalal,
132. Jia, Q., Wang, A., Yuan, Y., Zhu, B., and Long, H. (2022). Heterogeneity of K., Fropf, R., McAnany, C., Gagneur, J., Kundaje, A., et al. (2021).
the tumor immune microenvironment and its clinical relevance. Exp. Base-resolution models of transcription-factor binding reveal soft motif
Hematol. Oncol. 11, 24. syntax. Nat. Genet. 53, 354–366.
133. Melssen, M.M., Sheybani, N.D., Leick, K.M., and Slingluff, C.L. (2023).
148. Ho, J., Jain, A., and Abbeel, P. (2020). Denoising diffusion proba- bilistic
Barriers to immune cell infiltration in tumors. J. Immunother. Cancer 11.
models. Adv. Neural Inf. Process. Syst. 33, 6840–6851.
134. Chow, A., Perica, K., Klebanoff, C.A., and Wolchok, J.D. (2022). Clinical
149. Lipman, Y., Chen, R.T., Ben-Hamu, H., Nickel, M., and Le, M. (2023).
implications of T cell exhaustion for cancer immunotherapy. Nature Re-
Flow Matching for Generative Modeling. International Conference on
views Clinical Oncology 19, 775–790.
Learning Representations.
135. de Visser, K.E., and Joyce, J.A. (2023). The evolving tumor microenviron-
150. Scarselli, F., Gori, M., Tsoi, A.C., Hagenbuchner, M., and Monfardini, G.
ment: from cancer initiation to metastatic outgrowth. Cancer Cell 41,
(2009). The graph neural network model. IEEE Trans. Neural Netw. 20,
374–403.
61–80.
136. Barkley, D., Moncada, R., Pour, M., Liberman, D.A., Dryg, I., Werba, G.,
Wang, W., Baron, M., Rao, A., Xia, B., et al. (2022). Cancer cell states 151. Cao, Y., and Shen, Y. (2020). Energy-based graph convolutional net-
recur across tumor types and form specific interactions with the tumor works for scoring protein docking models. Proteins 88, 1091–1099.
microenvironment. Nat. Genet. 54, 1192–1201. 152. Brbic(cid:3), M., Cao, K., Hickey, J.W., Tan, Y., Snyder, M.P., Nolan, G.P., and
137. Schwartzberg, L., Kim, E.S., Liu, D., and Schrag, D. (2017). Precision Leskovec, J. (2022). Annotation of spatially resolved single-cell data with
oncology: who, how, what, when, and when not? American Society of STELLAR. Nat. Methods 19, 1411–1418.
Clinical Oncology Educational Book 37, 160–169. 153. Wu, Z., Trevino, A.E., Wu, E., Swanson, K., Kim, H.J., D’Angio, H.B., Pre-
138. Aebersold, R., Agar, J.N., Amster, I.J., Baker, M.S., Bertozzi, C.R., Boja, ska, R., Charville, G.W., Dalerba, P.D., Egloff, A.M., et al. (2022). Graph
E.S., Costello, C.E., Cravatt, B.F., Fenselau, C., Garcia, B.A., et al. (2018). deep learning for the characterization of tumour microenvironments
How many human proteoforms are there? Nat. Chem. Biol. 14, 206–214. from spatial protein profiles in tissue specimens. Nat. Biomed. Eng. 6,
139. Katsoulakis, E., Wang, Q., Wu, H., Shahriyari, L., Fletcher, R., Liu, J., 1435–1448.
Achenie, L., Liu, H., Jackson, P., Xiao, Y., et al. (2024). Digital twins for 154. Hamilton, W., Ying, Z., and Leskovec, J. (2017). Inductive Representation
health: a scoping review. npj Digit. Med. 7, 77. Learning on Large Graphs. Adv. Neural Inf. Process. Syst. 30.
Cell 187, December 12, 2024 7063
