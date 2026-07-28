<!-- Page 1 -->

nature reviews genetics https://doi.org/10.1038/s41576-024-00786-y
Review article Check for updates
The design and engineering
of synthetic genomes
Joshua S. James 1,2, Junbiao Dai 3,4, Wei Leong Chew 2 & Yizhi Cai 1
Abstract Sections
Synthetic genomics seeks to design and construct entire genomes to Introduction
mechanistically dissect fundamental questions of genome function
Synthetic genome design
and to engineer organisms for diverse applications, including
Computer-aided synthetic
bioproduction of high-value chemicals and biologics, advanced cell genomics
therapies, and stress-tolerant crops. Recent progress has been fuelled
Top-down synthetic genome
by advancements in DNA synthesis, assembly, delivery and editing. construction
Computational innovations, such as the use of artificial intelligence Bottom-up synthetic genome
to provide prediction of function, also provide increasing capabilities to construction
guide synthetic genome design and construction. However, translating Synthetic genome delivery
synthetic genome-scale projects from idea to implementation remains
Synthetic genome debugging
highly complex. Here, we aim to streamline this implementation and tailoring
process by comprehensively reviewing the strategies for design, Conclusion and future
perspectives
construction, delivery, debugging and tailoring of synthetic genomes
as well as their potential applications.
1Manchester Institute of Biotechnology, University of Manchester, Manchester, UK. 2Genome Institute of Singapore
(GIS), Agency for Science, Technology and Research (A*STAR), Singapore, Republic of Singapore. 3Shenzhen
Branch, Guangdong Laboratory for Lingnan Modern Agriculture, Shenzhen Key Laboratory of Agricultural Synthetic
Biology, Genome Analysis Laboratory of the Ministry of Agriculture and Rural Affairs, Agricultural Genomics Institute
at Shenzhen, Chinese Academy of Agricultural Sciences, Shenzhen, China. 4Shenzhen Key Laboratory of Synthetic
Genomics, Guangdong Provincial Key Laboratory of Synthetic Genomics, Shenzhen Institute of Synthetic Biology,
Shenzhen Institute of Advanced Technology, Chinese Academy of Sciences, Shenzhen, China. e-mail: yizhi.cai@
manchester.ac.uk
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 298

---

<!-- Page 2 -->

Review article
Introduction tools and the necessary social-scientific frameworks2,34. Further appli-
Falling DNA synthesis costs, paired with expanding DNA assembly and cations will continue to emerge as technology develops, with improved
delivery technologies and a powerful genome engineering toolbox, genomic data storage, biocomputing and biosensing all proposed as
have driven the emergence of synthetic genomics, a field characterized potential goals43,44.
by the synthesis, editing and testing of genome sequences1,2. Operating Here, we review the recent advances in designing, constructing,
at the interface of synthetic and systems biology, the construction of refining and applying synthetic genomes. First, we cover genome
synthetic genomes facilitates the probing of biological hypotheses by design strategies and tools, including template-guided and syn-
design through exploration and analysis of genomic sequence variants thetic circuit-based genome design, followed by the role of compu-
in otherwise isogenic cells. This approach bypasses the noise from tational tools to guide design and manufacturing. Next, we overview
varying genomic backgrounds that has frustrated sequencing-based approaches for synthetic genome construction — both top-down modi-
interrogation, enabling direct mechanistic dissection and inference fication of natural genomes and bottom-up genome synthesis, assem-
of the function of genetic changes3,4. Decoding the complex rules of bly and delivery — and the importance of improved DNA synthesis and
genome function, regulation and organization also informs the appli- assembly methods. We also discuss validation and post-construction
cation of synthetic genomics across diverse sectors, including health- debugging and tailoring. Finally, we look forward and predict the tools
care, industry and food security, through the construction of designer required for the routine deployment of synthetic genomes to enhance
organisms augmented with powerful novel functions. understanding and address global challenges.
The roots of synthetic genomics trace back to the early 1970s,
with the first demonstration of chemical gene synthesis, and seminal Synthetic genome design
work on recombinant DNA leading to the assembly of a hybrid viral The construction of synthetic genomes begins with design. This phase
genome5–7. Since then, our ability to synthesize and engineer genomes governs the translation of desired features and functions into genomic
has scaled exponentially (Fig. 1). Small viral genomes were early tar- sequence blueprints for assembly, testing and deployment. Top-down
gets for de novo construction using chemically synthesized DNA, as design strategies can range from minimal alteration of natural genomes
demonstrated by hepatitis C virus replicon (8 kb), poliovirus (7.5 kb), to large-scale template modifications, whereas bottom-up design, free
φX174 (5.38 kb) and T7 bacteriophage (12.5 kb) genome construction of template constraints, seeks to leverage generative or circuit-based
in the early 2000s8–11. Viral synthetic genomes have since been used approaches to build genomes with novel functions.
for reverse genetics12–14, design and testing of vaccine candidates15,16
and pandemic surveillance17,18; furthermore, designer phage thera- Template-guided synthetic genome design
pies are likely to be a key strategy to combat antimicrobial-resistant A lacking understanding of fundamental genome design rules has
bacterial pathogens19. Initial viral efforts were soon followed by syn- largely limited synthetic genomics to template-guided design. With this
thetic bacterial genome construction — first of Mycoplasma species approach, natural genome sequences are used as functional starting
(0.5–1.0 Mb)20–22, before Escherichia coli strains C321 (4.6 Mb), Syn61 points on which design layers can be added and tested iteratively. As
(3.97 Mb) and Ec_Syn57 (in development)23–26. Alongside diverse bio- such, this strategy relies on the accuracy of genome sequence assem-
medical applications, synthetic bacterial genomes hold promise for blies, with advances in DNA sequencing, including recent long-read
efficient bioproduction, with potential outputs including high-value approaches, providing complete, high-quality references for even
pharmaceuticals, biofuels and biomaterials1. Furthermore, such sys- large, repetitive vertebrate and plant genomes45–47. Furthermore,
tems can be engineered for bioremediation, notably of industrial waste, comprehensive annotation of genomes, aided by techniques such as
carbon dioxide and plastics1. Although larger eukaryotic genomes ribosome profiling and transcription start site identification, prevents
represent a more complex engineering challenge, the Synthetic the accidental disruption of important functional elements during
Yeast Genome Project (Sc2.0) recently reported the total de novo synthetic genome design26,48,49.
synthesis of all 16 yeast chromosomes as well as a new-to-nature tRNA Early synthetic genomics projects established invaluable founda-
neochromosome27–33, totalling more than 11 Mb of DNA with edits tions, mitigating the risks of non-functional designs by reconstruct-
occurring on average every 400 bp (ref. 27). ing native genomic sequences without alteration or with minimal
To date, synthetic genomics has been characterized by expensive, changes to distinguish synthetic from natural genomes2,8,9,20. Since
long-term projects reliant on technologies largely restricted to a small these proof-of-principle milestones, synthetic genome projects have
number of well-funded, specialized groups. However, expanding capa- expanded in scope, employing several design principles, includ-
bilities in DNA design, synthesis, assembly and delivery stand to lower ing minimization, genetic code alteration, refactoring and generating
barriers to research and accelerate advancements, driving the transi- dynamic synthetic genomes.
tion from proof-of-concept projects to custom genomes with varied Minimization seeks to reduce genome size by removing redun-
real-world applications. Although the complete de novo synthesis of dancies and functionalities beyond those required for survival or
large eukaryotic genomes remains in its early stages, recent advances desired applications50. Reduced genomic complexity enables analy-
have expanded targets beyond model microorganisms, including into sis of the basal components required for life, simplifies modelling
mammalian, algal, plant and organellar genomes34–39. Such targets have and downstream engineering, and provides a streamlined biological
substantial potential for application in areas such as maintenance of chassis for loading with heterologous genetic modules for efficient
food security (for example, programmable crop plant genomes with bioproduction22,51–55. In contrast to maximal minimization, the reten-
enhanced nutritional content or stress tolerance40) and biomedical tion of some quasi-essential genes (those that incur growth penalties
health care (for example, engineered porcine genomes that produce when removed) can yield a stronger chassis for downstream manipula-
tissues suitable for personalized transplantation to humans41,42). Pro- tion and applications22,56,57. As such, experimental mapping of sequence
gress towards these goals is supported by consortia such as Genome essentiality is central to efficient minimal-genome design58–61. For
Project-Write and the Dark Matter Project, which seek to develop both example, high-throughput mapping of native functional regions by
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 299

---

<!-- Page 3 -->

Review article
10 Gb Viral Medical
Prokaryotic Synthetic • Vaccine development
• Therapeutic proteins
Eukaryotic Human
1 Gb Planned projects Genome • Xenotransplantation
SynMoss
Food security
100 Mb
• Enhanced nutrition
Sc2.0 SynDiatom • Pathogen resistance
• Environmental tolerance
10 Mb
E. coli Syn61
Sc2.0 SynII, V, VI, X, XII Sc2.0 Syn 7.5 Industrial
1 Mb M. mycoides Sc2.0 SynI, IV, VII, VIII, XI, XIV, XV • • B En io g f i u n e e l e p re ro d d b u i c o t m io a n terials
JCV-syn3.0 • Fine chemical synthesis
Sc2.0 tRNA neochromosome
M. genitalium
100 kb Sc2.0 SynIII
Environmental
T7 Bacteriophage Sc2.0 SynIXR • Bioremediation
• Contaminant biosensing
10 kb
• Engineered biodiversity
Poliovirus cDNA
1 kb
2000 2005 2010 2015 2020 2025
Fig. 1 | Synthetic genome projects and applications. Early milestones in heteropolymers, are already in use. Recent work has seen the expansion of
synthetic genomics saw the bottom-up synthesis of small viral genomes. With synthetic genomics into mammalian systems, offering a powerful empirical
advances in large-scale DNA assembly in yeast and genome transfer between approach to understanding genome functions at a previously inaccessible
microbial hosts, these feats were soon followed by the first synthetic bacterial resolution. Building on the foundations of the past 25 years of advances, falling
genomes. In 2014, the first synthetic eukaryotic chromosome was completed DNA synthesis costs and an expanding repertoire of technologies will see
as part of the Synthetic Yeast Genome Project (Sc2.0). Recent years have seen the acceleration of synthetic genomics. Future work will likely see synthetic
the completion of all 17 synthetic yeast chromosomes, alongside the planning genomes built using function-led design, producing organisms ranging from
of further expansive projects targeting diverse organisms. Although the field designer crops exhibiting stress tolerance and pathogen resistance, to enhanced
remains in a foundational stage, synthetic genomes encoding valuable functions, microorganisms for the bioproduction of biofuels, high-value chemicals and
such as Escherichia coli Syn61 enabling the translation of non-canonical therapeutics.
transposon insertion mutagenesis underpinned the design of the mini- by numerous recoded sequences yielding cryptic promoters driving
mal Mycoplasma mycoides JCVI-syn3.0 genome but also highlighted deleterious transcription26. Alternative approaches for code expansion
the enduring challenge of identifying synthetic lethal interactions22,62. include the encoding and decoding of genetic information through
Genetic code alteration, or recoding, involves manipulation of quadruplet codons and the use of unnatural base pairs74–79. A more radi-
the structures and patterns by which genetic information is encoded cal proposal is to expand information storage and propagation beyond
and decoded63,64. For example, code compression (used in several DNA and RNA using nucleic acid analogues or xeno nucleic acids79,80.
large synthetic genomics projects) reduces the number of codons The Sc2.0 synthetic yeast genome design introduces the concept
used in a genome by reassigning selected codons to synonymous of a dynamic synthetic genome, in which integrated recombination
alternatives23–25,27,65,66. This approach enables the removal of cognate mechanisms enable rapid and diverse reconfiguration of genome
tRNAs, providing resistance to viruses and other mobile genetic ele- structure81. Through accelerated directed evolution of a single syn-
ments due to the absence of machinery required to translate invading thetic genome, this approach reveals novel configurations enabling
genes67,68. Furthermore, liberated codons may be redeployed for alter- diverse functionalities. Over 4,000 loxPsym sites introduced through-
native uses, including biocontainment mechanisms and non-canonical out the Sc2.0 genome enable the induction of the SCRaMbLE (Synthetic
amino acid incorporation for the biosynthesis of unnatural therapeutic chromosome rearrangement and modification by loxP-mediated evolu-
and industrial proteins34,68–71. Of note, stop codons are common targets tion) system, with combinatorial deletion, inversion, duplication and
for code compression due to their relative scarcity (which minimizes translocation of loxP-flanked units generating diversity27,82,83. Work to
the scale of engineering required) and reduced impact on transla- retrofit loxPsym sites has enabled SCRaMbLE within human, mouse and
tion through absence of amino acid encoding, where codon choice native yeast genomes, thus permitting massively parallel investigation
can influence translation kinetics and protein folding25,72. Given the of genome structure and plasticity84–88.
importance of codon selection on gene regulation, two E. coli synthetic In software development, refactoring involves reorganizing and
genome projects, Syn61 and Ec_Syn57 (which removed three and seven refining internal system design while maintaining or enhancing overall
codons, respectively), have both required multiple design iterations function. This process may be applied to genomes, as first demon-
and substantial debugging23,26. In particular, construction of Ec_Syn57 strated in an investigation of the T7 bacteriophage genome leveraging
(exhibiting the greater proportion modified73) has been complicated genome decompression — a common refactoring strategy in which
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 300

---

<!-- Page 4 -->

Review article
overlapping genes are separated to simplify regulatory investigation and error-prone process. Therefore, computational frameworks have
and engineering2,10,89. Refactoring can also include defragmentation proved essential to streamline and error-proof genome design as well
to group genes or genomic elements by function; such groupings may as to plan construction and track project progress.
be augmented with genetic or epigenetic mechanisms that provide
synthetic control over the encoded functions28,90. Beyond the restruc- Genome design software
turing of native sequences, more intensive refactoring schemes have Early synthetic genomics projects were reliant upon simple sequence
been applied to gene clusters90–93. Such schemes seek to reformat visualization and manipulation tools, such as vector NTI, genomBench
complex, interlinked genetic systems to minimal synthetic gene cir- and SGI Archetype, to guide genome design and formulate assem-
cuits that share little sequence identity with native templates while bly strategies10,20,22,102. However, the design of larger genomes host-
retaining function. This reformatting may be achieved by removing ing complex suites of designer changes requires more sophisticated
redundancies, non-coding regions and non-essential genes, alongside computer-aided design (CAD) tools, augmented with packages ena-
replacing complex native regulation with benchmarked synthetic bling automated, rule-based sequence design103–106. To that end, BioStu-
parts controlling individual elements. Recoding of retained sequences dio was developed to automate the design of the Sc2.0 genome, scaling
may also be used to disrupt any remaining internal regulation91,92. The design capacity to whole yeast chromosomes27. Alongside sequence
resultant simplified structure and decoupling from wider regulatory modification at both local and global levels, BioStudio incorporates
networks aid both the forward engineering of function and portability design rule conflict management, rollback version control and coordi-
of functional units between hosts91. Notably, the successful replace- nation of collaborative genome design by multiple stakeholders27. Since
ment of a yeast chromosome arm with recoded essential genes under the progress of BioStudio, progress towards a flexible, genome-agnostic
synthetic control suggests that such intensive refactoring is feasible tool capable of implementing diverse user-defined modifications has
at the genome scale94. been slow. However, the recent development of GenoDesigner, an
online design tool capable of handling gigabase-scale projects, should
Towards synthetic circuit-based genome design provide a strong platform for the flexible design of large genomes38,107.
The refactoring of genomes or genetic networks seeks to rebuild the
function of parent systems in circuit format. Therefore, outputs of Predicting function
this approach remain largely restricted by the boundaries of original Given the investments required to construct synthetic genomes and
system function. Instead, bottom-up design may enable a function-led shortfalls in the ability to predict genome design functionality, con-
approach, with synthetic genetic circuits encoding desired character- servative design has typically been necessary to mitigate the risk of
istics layered into genome designs as required. This strategy will be growth penalties or non-function. Therefore, improved predictive
supported by the development of increasingly complex and diverse power remains a key priority to provide valuable risk management
synthetic circuits95–97 and requires a far more complete understanding and accelerate more ambitious synthesis projects50,99. Although com-
of the requirements for genome function. However, it unlocks access putational tools are currently lacking for predicting genome-scale
to a wider, template-free design space, potentially enabling a greater function, tools are becoming increasingly available for predicting RNA
range of functions and applications. folding108–111, protein structure112,113, regulatory element function114–118
Viral genomes provide accessible targets for reconstruction and the impacts of non-synonymous mutations119. Unification of
using synthetic gene circuits. For example, prior work has designed these available tools within broader CAD software may provide a
modular oncolytic viruses and phage therapies tailored to target bac- route towards simultaneous design and functional prediction at the
terial pathogens19,98. It is also feasible to augment a minimal genomic genome scale.
chassis with characterized synthetic circuit-based modules encoding Tools to predict biological function have been massively enhanced
metabolic pathways, bioprocessing capacity or other functions in a by recent advances in machine learning and artificial intelligence.
combinatorial, ‘plug-and-play’ format, generating complex systems for In step with improvements in prediction, generative artificial intel-
specific applications50,90,99. This approach offers a potential stepping ligence models have received increasing traction across several areas
stone towards future modular genome design of entire large genomes. of biological design, notably in the de novo generation of regulatory
Design automation will be required to handle the complexity of sequences120–124 and novel proteins with designer functions125–128.
expanding bottom-up strategies to the genome scale. Current tools, Recent work has attempted to scale up these approaches for artificial
such as the Cello software suite, facilitate the automated design of intelligence-guided whole-genome design129–132. Although these mod-
synthetic genetic circuits95. Cello converts high-level circuit func- els remain untested and lack fine control over prospective genome
tions into testable DNA sequences using a benchmarked library of functions, we anticipate that increasingly accessible large-scale DNA
repressor-based Boolean logic gates to accurately produce desired synthesis, assembly and testing will both provide a scalable source of
circuit characteristics95. An updated software, Cello 2.0, begins to training data and offer validation and fine-tuning of predictive and
address interactions between circuits and their genomic contexts — a generative models — both exciting prospects for synthetic genomics.
key step to layering genetic programmes and moving more genomic Holistic computational modelling of cellular and genomic func-
processes under synthetic control100,101. Nonetheless, additional work tion may enable genotype-to-phenotype prediction and thus provide
is needed to inform how genetic part and circuit function will vary by estimates of genome design functionality133–135. Whole-cell models
context to enable scaling up from the design of synthetic circuits to (WCMs) seek to reconstruct cellular function in silico by combining
networks and entire genomes. multiple layers, representing various biological processes, into a single
unified model136. Current WCMs are limited to a handful of model organ-
Computer-aided synthetic genomics isms, including Mycoplasma genitalium, E. coli and Saccharomyces
For even the smallest genomes, manually translating simple design cerevisiae, and vary in completeness137–140. Although the accuracy of
principles to functional blueprints for manufacturing is a complex current models has not been fully assessed, and constructing WCMs
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 301

---

<!-- Page 5 -->

Review article
remains challenging, building on current progress may see the acceler- In general, dedicated assembly planning tools that are capable of
ated production of high-quality models across diverse organisms141. handling entire genomes should facilitate fast-tracked design imple-
Accelerated synthetic genome construction offers an exciting oppor- mentation and the lowering of access barriers for non-specialists, espe-
tunity to provide additional data points informing WCM development cially as synthetic genomics transitions towards application-driven
and validation and, in turn, improve genome functionality prediction. projects using high-level, abstracted genome design157. However,
executing complex, multimodal genome assembly plans by hand
Design for manufacturing remains a challenging prospect. Flexible compilers capable of trans-
Design-for-manufacturing tools assess the ‘constructability’ of a lating assembly plans to machine-readable code facilitate auto-
product, with the aim of saving time and resources by highlighting mated assembly of genetic circuits158–160. Similar tools may enable the
designs that violate manufacturing constraints142,143. Despite advances translation of genome-scale assembly plans to automated assembly
in de novo DNA synthesis and assembly capabilities, sequences such instructions, interfacing with robotic wet-lab platforms that feature
as tandem repeats, hairpin loops and GC/AT-rich regions can com- high-throughput liquid handling hardware and facilities to conduct
plicate commercial phosphoramidite synthesis. As such, predicting complex molecular biology protocols. Expanded platforms, such
DNA synthesis success at the design stage streamlines construction as biofoundries or cloud labs, may incorporate modules for bench-
by flagging problematic sequences for redesign144–146. Software tools, top DNA synthesis, cell culture, colony picking, flow cytometry and
such as RepeatSmasher, Genome Calligrapher and BOOST, are available DNA sequencing, potentially enabling advanced, end-to-end genome
to ‘polish’ such sequences into synthesis-friendly alternatives27,142,147. assembly with minimal human intervention161,162. Powerful laboratory
However, care must be taken to ensure polished sequences function information management systems will be necessary for organizing and
as intended in their end context148. tracking these complex automated constructions163–165.
Computer-aided manufacturing Future developments
Segmentation tools, such as Genome Partitioner, facilitate the optimal Extensibility of CAD and computer-aided manufacturing tools will
division of genome designs into fabricable chunks for downstream be important as new technologies for genome synthesis, assembly
assembly142,149. BioStudio and Segman software played similar roles and delivery are developed. Software inter-operability will be simi-
during Sc2.0 construction, providing computational partitioning and larly valuable to enable combinations of tools, operating in tandem
restriction enzyme placement27,150,151. Optimal partitioning strategies behind simple user interfaces, to provide real-time optimized design.
typically generate the minimum number of synthesizable fragments to Similarly, the expansion of standardized biofoundries will streamline
reduce assembly steps. However, the chosen strategy may be influenced communication between design software and laboratory automation
by metrics, including commercial synthesis speed, cost and risk of platforms162,166.
failure145. DNA Scanner connects to commercial synthesis application In the architecture, engineering and construction sectors, next-
programming interfaces, providing rapid reporting of these metrics generation design and modelling tools, such as building information
across different providers145. Improved access and industry standardi- modelling (BIM) systems and digital twins, are becoming increas-
zation will support the uptake of similar tools145. Tools to scan existing ingly widespread. Unlike CAD, BIM systems offer real-time project
repositories of DNA may facilitate the bypass of synthesis constraints management and functional modelling of processes, such as water
through the reuse of available DNA (and derived variants). Such tools and electricity supply, alongside traditional structural design and
may influence partitioning schemes, reducing synthesis costs and rendering167. BIM-like systems may therefore offer a suitable frame-
providing access to a broader manufacturable design space152–154. work for future synthetic genome design by augmenting sequence
Synthetic genomics projects have traditionally used simple con- control with modelling of function, including 3D genome archi-
struction regimes, with the chosen DNA source, assembly and delivery tecture, RNA polymerase flux and metabolic modelling, alongside
strategies conserved across entire designs. Such strategies streamline design-for-manufacturing feedback, integrated assembly planning
project planning and management but rarely provide the optimal and project management (Fig. 2). Digital twins provide virtual descrip-
route from design to final product. Instead, projects may benefit from tions of physical products, with smart sensors providing continuous
custom implementation pathways in which designs are divided into feedback throughout product life cycles. Such representations may
regions amenable to specific construction strategies. For example, provide value for tracking and performance monitoring of synthetic
sequences that diverge heavily from available natural templates are genomes168. In combination with artificial intelligence and biofound-
typically best synthesized de novo. Conversely, this approach is waste- ries operating automated, closed-loop, design–build–test–learn
ful when sequences closely mirror natural templates and are readily cycles, these tools provide a potential route to smart manufacturing
constructible through PCR or top-down editing. With the diversifica- of synthetic genomes169.
tion of DNA synthesis, assembly and delivery technologies, the fastest
or cheapest genome synthesis pathways are increasingly represented Top-down synthetic genome construction
by complex combinations of techniques. Without capable software, Bottom-up (de novo) synthesis is seen as the pinnacle of synthetic
identifying optimal pathways is complex and impractical. Raven CAD genomics but is limited by cost-prohibitive DNA synthesis and assem-
facilitates software-guided assembly planning for genetic circuits, bly. Technological limitations preventing the construction of repeti-
using dynamic programming to select optimal construction pathways tive sequences such as centromeres — and organism-specific delivery
from a broad solution space155. Looking forward, Raven CAD may pro- challenges — further complicate this approach170,171. By contrast,
vide a stepping stone towards fully automated navigation of complex top-down synthetic genome construction relies upon modification
genome construction decisions. Suitable description and recording of natural genomes. This strategy is often practical given the increas-
of construction decisions and their performance will aid this process ing capabilities of genome-editing tools and that synthetic genome
through model-guided learning and algorithm optimization155,156. designs typically closely resemble natural counterparts.
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 302

---

<!-- Page 6 -->

Review article
Computer-aided design and manufacturing
Genome design Prediction of functionality Design for manufacturing Assembly planning
Time
• Sequence level design • Model-guided prediction of • Polish synthesis constraint • Select assembly and delivery
• Global design rule function violations method
implementation • Prevent construction of • Parse design for optimal synthesis • Compile plan to machine readable
• Design conflict management dysfunctional genomes and reassembly code
Learn Test
The top-down genome engineering toolbox editors have advanced substantially in efficiency and functionality188–195.
Programmable nucleases, such as CRISPR–Cas9, transcription Recently developed click editors use a DNA-dependent DNA polymerase
activator-like effector nucleases and zinc finger nucleases, can induce to deliver sequence modifications196. Both prime and click editors show
targeted DNA double-strand breaks to introduce desired edits, typi- promise for implementing complex genome designs owing to their
cally through non-homologous end-joining or homology-directed ability to simultaneously deliver a diverse range of multimodal edits.
repair pathways172–174. However, strategies programming multiple Beyond sequence editing, the removal of undesired sequences is
double-strand breaks within the cell risk high toxicity and catastrophic also important for top-down synthetic genomics. To this end, paired
structural rearrangements, mandating intensive screening to ensure Cas9 DNA cleavage followed by end-joining of the two distal DNA breaks
the maintenance of genome integrity175–178. Base editors enable more creates a new junction, removing the intervening sequence197,198. Cas9
precise changes by driving single point mutations through enzymatic has been further used to delete sequences at the chromosome scale199.
base modification179. More specifically, early cytosine and adenine base Dual prime editor methods avoid double-strand breaks, which
editors enable transition mutations, while more recent architectures reduces the risk of compromising genome stability189,200,201. However,
have begun to facilitate base transversions180–183. Alongside heavy usage efficiency may be reduced for larger deletions such that the desired
in gene-editing therapy, base editors have been useful for genome edits exist within a smaller subset of cells amidst potential off-target
recoding184,185. Prime editors are another complementary technol- changes189,200,201. To improve deletion efficiency, prime editing can
ogy; these tools are RNA-guided DNA editors that use a reverse tran- be paired with site-specific recombinases: inserting recombination
scriptase to directly write DNA into a target site from an encoded RNA sites at either side of a target sequence can facilitate higher efficiency
template186,187. Capable of introducing all 12 possible point mutations, recombinase-mediated removal of large sequences, albeit at the cost of
small deletions and insertions within a flexible editing window, prime a short recombination scar189,202. Recent work characterizing the Cas3
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 303
DO
gDNA
WT
Syn GCA TCG ATC ATT
GCA TCA ATC ATT
Build
Performance-
guided
feedback
Liquid Colony
handler Acoustic picker
dispenser
Fig. 2 | Towards integrated computer-aided design and manufacturing of also provide value by reporting the constructability of designs. Design for
synthetic genomes. Computational assistance is required to design and manage manufacturing prevents wastage from attempting projects that lie beyond
genome-scale engineering. Small viral or bacterial genomes may be addressed assembly and delivery capacities. Furthermore, reports enable design polishing,
using existing plasmid editors but larger genomes provide greater challenges, where problematic sequences or regions are redesigned to avoid construction
especially when version control, collaborative working, complex design rule violations. After segmentation of designs into constructible sections, modules
implementation and design conflict management are desired. Flexible and governing automated assembly planning may select optimal DNA sources
powerful computer-aided design and manufacturing software will streamline and assembly strategies before compiling instructions into machine-readable
the design and construction of synthetic (Syn) genomes. Beyond handling code for biofoundry-assisted construction. Artificial intelligence and machine
complex design strategies for large genomes, prediction of design functionality learning provide a novel opportunity for performance-guided feedback and will
will enable complex projects, relaxing the requirements for conservative eventually enable closed-loop design-and-build cycles for smart manufacturing
design. One strategy for this may be the integration of whole-cell or genome- of synthetic genomes. gDNA, genomic DNA; OD, optical density; WT, wild type.
scale models to test designs in silico. Design-for-manufacturing packages will

---

<!-- Page 7 -->

Review article
effector offers an additional approach for efficient implementation underlying phosphoramidite chemistry reaches technical limits due
of large deletions54,203,204. to intrinsic error rates such that increased length sacrifices overall
Outside of CRISPR–Cas systems, recombineering offers a pow- synthesis fidelity170. Pre-assembled and validated >10 kb chunks of
erful top-down editing strategy. This approach supplements micro- synthetic DNA are now routinely offered by commercial DNA synthesis
organisms with bacteriophage-derived recombination machinery, vendors; however, costs remain prohibitive for large genomes.
notably the λ-Red system in E. coli, to enable highly efficient Enzymatic DNA synthesis is a promising alternative for the de novo
homologous recombination205. Libraries of short, single-stranded, generation of long, repetitive and highly structured sequences at
mismatch-encoding oligonucleotides (with overall complemen- high fidelity, thus minimizing costly lower-order assembly and
tarity to the endogenous genome) are then introduced to encour- validation170,218. Although enzymatic DNA technology remains expen-
age recombineering-driven genetic replacement during genome sive and limited in scale, substantial recent private investment and
replication206,207. This approach has been extended to develop multi- breakthroughs towards electronically controlled DNA synthesis
plex automated genome engineering (MAGE) that involves the continu- on a scalable semiconductor chip indicate substantial near-term
ous introduction of oligonucleotide libraries to drive the accumulation advancements18,219.
of edits over time208. MAGE was first demonstrated as a directed evolu- Repurposing existing DNA can provide an inexpensive alter-
tion system to optimize the DXP biosynthesis pathway for lycopene native to de novo synthesis, especially when large amounts of DNA
production and subsequently enabled the first recoded E. coli genome are required154. Strategies to extract natural sources of DNA include
in which 321 TAG stop codons were replaced with synonymous TAA homology capture and direct PCR from genomes or bacterial artificial
sequences25,208,209. MAGE was initially limited to the few microorgan- chromosome (BAC)/yeast artificial chromosome (YAC) libraries220,221.
isms with known associated single-stranded DNA-annealing proteins High-efficiency sequence editing can further be performed in vitro or
but recent screening efforts have begun to implement MAGE in diverse in intermediate microbial hosts222–224. Synthetic part libraries may also
bacterial species210. Furthermore, computational tools have been be used to source DNA153,225,226. Reuse of existing DNA may be especially
developed to streamline complex oligo library design211,212. Enticingly, favourable when designs, or design sections, adhere closely to native
oligonucleotide-mediated recombineering has been expanded to sequences, minimizing the need for extensive editing227.
eukaryotic hosts with tools, such as YOGE and eMAGE, that are capable
of genome editing in yeast213,214. Whether an oligonucleotide-mediated DNA assembly strategies
recombineering system can be efficiently used in additional organisms, Bottom-up genome construction approaches typically require small
including human cells, remains an important line of inquiry215. input chunks of source DNA to be assembled into larger units. Assembly
can be performed either in vitro or in vivo, with the optimal method
Challenges for top-down synthetic genomics depending on the size and structure of DNA.
With the recent proliferation of genome-editing agents, a diverse tool- In vitro DNA assembly is invaluable for completing lower-order
box for top-down synthetic genomics is now available to adapt natu- assemblies using short-length input DNA. For example, polymerase
rally occurring genomes to synthetic designs. However, implementing cycling assembly enables the DNA polymerase-mediated stitching
designs using top-down approaches hinges on the density and com- of overlapping oligonucleotides into single contiguous sequences
plexity of required edits. Further development addressing challenges (Fig. 3a). Polymerase cycling assembly has some capacity to assemble
in editing efficiency, on-target sequence purity, genotoxicity and inef- repetitive DNA if overlaps do not share repetitive sequences; in addi-
ficient delivery of multiple components will strengthen the potential of tion, error-correcting enzymes may identify mismatches for increased
top-down approaches184. These advancements will be especially valuable assembly fidelity228,229. Alternatively, Gibson assembly uses a DNA
in the context of large eukaryotic genomes by minimizing the rounds of exonuclease, polymerase and ligase enzyme cocktail capable of driving
lengthy engineering and verification required to implement designs, thus assembly of DNA fragments with short overlapping homology regions
facilitating the construction of more ambitious synthetic genomes216. into sequences spanning hundreds of kilobases230. Golden Gate assem-
bly, although limited by incompatibility with internal Type IIS restric-
Bottom-up synthetic genome construction tion enzyme sites, provides a powerful, largely sequence-agnostic
Approaching synthetic genome construction from the bottom up ena- assembly approach, as demonstrated by the recent one-pot assembly
bles flexible design beyond the constraints of natural template editing. of a 40-kb viral genome from 52 parts231–233. Golden Gate assembly is
Falling DNA synthesis costs as well as expanding technologies for DNA especially valuable if repetitive sequences prohibit homology-guided
assembly and delivery will continue to facilitate bottom-up synthesis assembly approaches234,235.
of genomes of increasing size and complexity. In vitro DNA assembly methods approach a technical bottleneck
when large constructs are required owing to the risk of high-molecular-
Sourcing DNA for genome construction weight DNA shearing. As such, in vivo assembly within microbial hosts
The primary building blocks of synthetic genomics have been short has been favoured for the construction of larger synthetic sequences.
(<200 bp), single-stranded oligonucleotides produced by phospho- Typically, high-capacity episomal constructs, including yeast artificial
ramidite chemical synthesis. Column-based phosphoramidite synthe- chromosomes or BACs, provide a route to rapid DNA assembly and
sis requires large equipment space and high chemical quantities for propagation.
each reaction, providing challenges for both scalability and cost when Yeast has served as a premier assembly host for synthetic genomics
large quantities of non-uniform DNA are required. Oligonucleotides owing to an exceptional native capacity for high-fidelity homologous
constructed on silicon-based microarray chips facilitate large-scale recombination, tolerance of large supernumerary chromosomes and
oligonucleotide-pool synthesis, increasing access to abundant and a well-developed toolbox for sequence manipulation236–239. Homolo-
cheap DNA217. However, although scaling down physical volumes has gous recombination-driven assembly of oligonucleotides, or larger
correspondingly scaled up the number of reactions possible, the double-stranded DNA chunks with small overlapping regions, can
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 304

---

<!-- Page 8 -->

Review article
be achieved in vivo by transformation-associated recombination sequences into an episomal ‘assemblon’; however, complex handling
cloning14,240–243 (Fig. 3a). eSwap-In uses homologous recombination and and transformation of large linear sequences limits the size of each
selectable marker swapping to drive iterative integrations of linear DNA integration28,227,242.
a DNA synthesis and lower-order assembly Fig. 3 | De novo DNA assembly from
oligonucleotides to megabases. a, Constructing
large, custom, synthetic DNA sequences underpins
bottom-up synthetic genomics. Typically, the
basal units of DNA assembly are short (~200 bp)
oligonucleotides that are assembled into
contiguous sequences. These building blocks can be
consolidated into increasingly larger units through
a variety of assembly methods — both in vitro
using Gibson or Golden Gate assembly techniques
and in vivo using homology-guided assembly.
Yeast oligonucleotide assembly Polymerase cycling assembly Advancements in high-fidelity enzymatic synthesis
of longer DNA oligonucleotides may soon reduce
requirements for extensive lower-order assembly.
Gibson assembly b, Although in vitro DNA assembly techniques can
yield fragments spanning hundreds of kilobases,
larger assemblies are typically conducted in vivo
within microbial hosts, avoiding complex
in vitro handling and ensuring enough product
for downstream applications. Yeast remains
b Kilobase to megabase constructs the most used host due to its capacity for
eSwap-In
homologous recombination and tolerance of large
supernumerary chromosomes. Episomal constructs
can be produced with stepwise techniques such
as eSwap-In. Here, multiple large, overlapping
fragments can be integrated into the construct at
each step. Several methods facilitate the hierarchical
assembly of constructed episomes through yeast
mating, where nuclear fusion colocates synthetic
constructs, enabling their consolidation into a single,
BASIS Hierarchical assembly by yeast mating large unit. The bacterial artificial chromosome (BAC)
stepwise insertion synthesis (BASIS) method in
Haploid Escherichia coli facilitates stepwise DNA integration
a α into an assembly episome. As highly repetitive DNA
Assembly Donor can be unstable in yeast, E. coli may provide a suitable
BAC BAC alternative construction host.
Diploid
Assembly a/α
BAC
Assembly Donor Haploid
BAC BAC
a α
Diploid
Assembly BAC a/α
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 305

---

<!-- Page 9 -->

Review article
a Cell fusion
Yeast mating Spheroplast or protoplast fusion Microcell-mediated chromosome transfer
a α
Bacteria Yeast
a α
Yeast Mammalian
a/α
Plant Plant
b Conjugation c Further techniques
Microinjection Biolistic bombardment
Au
Au
Au
Au Au
Au
Au Au
Viral transduction Lipid vesicles
Herpes
simplex
virus
Baculovirus
Yeast Bacteria
Chemical Electroporation
Cell-penetrating
peptides
Carbon
nanostructures
+ +
Polycations + +
+
Algae Plants Mammalian
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 306

---

<!-- Page 10 -->

Review article
Fig. 4 | Delivering engineered DNA to target cells. Delivering large DNA for plants using microprotoplasts303. Efficient transfer of synthetic chromosomes
payloads from microbial construction hosts, or between cells for hierarchical will be key to hierarchical assembly of large eukaryotic genomes. b, Conjugative
construction, is a central enabling technology for constructing synthetic transfer has been used extensively within synthetic genomics to deliver large DNA
genomes. a, Cell fusion strategies bypass the in vitro handling of DNA, where it structures between bacteria and drive hierarchical assembly of entire bacterial
remains vulnerable to shearing and degradation2,349,354–356. Yeast mating underpins genomes. However, high-capacity conjugative delivery from bacteria to algae,
several technologies for the hierarchical assembly of episomal DNA and synthetic yeast and even mammalian cells has been reported248,253,269,359–361. c, Several further
yeast chromosomes. It may be possible to utilize sexual reproduction for diverse technologies have been employed to mediate DNA delivery to target cells.
consolidating synthetic DNA in further systems beyond yeast. Yeast spheroplasts Megabase-scale chromosomes and genomes have been stabilized for delivery
may be fused with mammalian cells, bacteria or other yeasts, typically in the with polycations or in agarose plugs, while mechanical methods, including
presence of polyethylene glycol. Virus-mediated fusion and electrofusion present electroporation, biolistic bombardment or microinjection, can be used across a
alternative approaches to directing cell–cell fusion357,358. Microcell-mediated variety of target cells255,362. High-capacity viral vectors, cell-penetrating peptides
chromosome transfer facilitates chromosome transfer between cells, with most and lipid vesicles similarly offer an exciting platform for DNA delivery across an
work addressing mammalian genomes. Similar approaches have been reported expanding range of cell types271,363,364.
The CasHRA approach circumvents these drawbacks through synthetic genomes to direct virus formation or cellular replication)2,18,21.
yeast protoplast fusion delivery of large, circular donor sequences For example, delivering viral synthetic genomes can simply involve
before Cas9 linearization for homologous recombination244. Yeast Life transferring the assembled genome to an appropriate host and assess-
Cycle assembly replaces complex protoplast-mediated DNA transfer ing propagation8,10,13,15. Prokaryotic genome delivery is simplified by
with sexual mating of haploid yeast strains to consolidate episomal the absence of a membrane-bound nuclear structure. However, even
constructs245. Meiotic sporulation and selectable marker retention the smallest bacterial genomes span hundreds of kilobases, complicat-
provides haploid cells housing consolidated episomes for further hier- ing isolation and delivery due to the structural fragility of large DNA
archical assembly rounds as demonstrated with assembly of 1.26 Mb structures in aqueous solution. In the first successful bacterial genome
of the human IGH locus. The sporulation step can be bypassed with transplantation, the native genome from M. mycoides was isolated and
Cas9 destabilization of chromosomes from one parental strain after purified within low-melting-point agarose plugs. The isolated genome
mating246. This engineered haploidization facilitates accelerated was then transferred to a Mycoplasma capricolum cell that had been
progression to further mating-driven DNA delivery and subsequent treated with polyethylene glycol to increase membrane fluidity and cal-
episomal expansion246 (Fig. 3b). cium chloride to counteract the negative charge of incoming DNA18,255.
Large, repeat-dense sequences have proved difficult to assemble Finally, tetracycline resistance enabled selection of cells carrying the
and propagate in yeast due to undesired recombination and synthetic successfully transplanted genome. This approach was extended to
sequence instability247. Bacterial assembly hosts offer a powerful facilitate the transplantation of a M. mycoides genome cloned in yeast to
alternative solution, with methods such as BAC stepwise insertion M. capricolum236. Cloning in yeast enabled the use of its powerful homolo-
synthesis facilitating the iterative assembly of large episomal DNA gous recombination capabilities during DNA assembly and simplified
sequences in E. coli using λ-Red-mediated recombination248. BAC the propagation of sufficient quantities of genomic DNA for booting-up.
stepwise insertion synthesis was used to generate a 1.1-Mb section However, a restriction system responsible for the degradation of foreign
of human chromosome 21 that contains many repetitive regions, DNA in both M. mycoides and M. capricolum prevented direct transplanta-
G-quadruplexes and other complex elements, providing an effi- tion after isolation from yeast. Both disruption of this system and in vitro
cient route to the large-scale assembly of challenging sequences248 genome methylation subsequently enabled transplantation. Despite
(Fig. 3b). In addition, E. coli strains genetically engineered to be free these initial achievements, successful genome transfer has been limited
of mobile genetic elements, which can disrupt the assembly of syn- to a subset of mycoplasma species, with efficiency inversely proportional
thetic sequences, offer an attractive platform for DNA assembly26,249. to the phylogenetic distance between donor genome and recipient cell256.
Alternative bacterial construction hosts include Bacillus subtilis, Proposed explanations for these limitations include the mutagenicity of
which is capable of assembling over 50 DNA parts in a single step the transfer process and activation of bacterial surface-associated nucle-
and thus facilitating the rapid assembly of sequences >100 kb using ases by calcium chloride (ref. 18). Work is ongoing to expand genome
small, synthesis-friendly building blocks250. Homologous recombi- transfer to a broader range of species18,257. The removal of native chromo-
nation of larger overlapping sequences may be used to generate and somes, leaving genome-free cells, may bypass conflict between native
propagate multi-megabase-scale assemblies within the B. subtilis and synthetic genomes during delivery and booting-up258. In addition,
genome itself251,252. Conjugative delivery of DNA parts bypasses BAC continued development of synthetic cells (that is, artificial compartmen-
transfection limits and increases construction scale253. talized systems that mimic natural cells and their functions) may provide
powerful platforms to host, test and propagate synthetic genomes259,260.
Synthetic genome delivery Organellar genomes are key targets for synthetic genomics with
In recent years, a suite of methodologies has enabled the synthesis proposed applications including therapeutic protein production and
and assembly of diverse, custom DNA at megabase scale. However, the synthetic nitrogen fixation4,261–264. Several organellar genomes have
delivery and installation of these sequences into destination organisms been entirely synthesized but delivery remains a key challenge, often
provides a major challenge for testing synthetic genome designs2,254. complicated by genome ploidy and heteroplasmy251,265–267. Biolistic
bombardment and polyethylene glycol-mediated transformation
Whole-genome delivery remain widely used delivery methods; however, bacterial conjuga-
For small genomes, construction may be completed ex situ before one- tion and nanoparticle-guided or peptide-guided delivery have been
step delivery to a host organism for ‘booting-up’ (that is, the installation of proposed as less disruptive alternatives268–271 (Fig. 4c).
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 307

---

<!-- Page 11 -->

Review article
a Stepwise genome rewriting Fig. 5 | Synthetic genome assembly with stepwise
rewriting and hierarchical assembly. a, Most
M1 flagship synthetic genomics projects have relied
upon homologous recombination-mediated
stepwise rewriting of DNA payloads. Swapping
of selectable marker cassettes with each payload
delivery facilitates the rapid isolation of clones
M2 carrying desired integrations. Swap-In and REXER
methodologies underpin the replacement of native
M1 sequences with synthetic counterparts in yeast and
Escherichia coli, respectively. Similar techniques
have recently been applied to generate engineered
M2 mouse models and rewrite genomic regions of the
land moss Physcomitrium patens. Recombinase-
mediated strategies may provide an alternative
solution where homologous recombination is
unavailable. M1 and M2, selectable marker cassettes
Bacteria Yeast Mammalian Plants 1 and 2. b, Although stepwise insertions facilitate the
rapid rewriting of genomic regions, they approach a
technical bottleneck where many steps are required
to rewrite a large region or genome. Instead,
b Hierarchical synthetic genome assembly
hierarchical approaches facilitate the distributed
manufacturing of several regions in parallel before
consolidation into a single contiguous unit after
colocation. This approach massively increases
the speed at which large synthetic regions can be
assembled and may offer accelerated synthesis
of large eukaryotic chromosomes. Homologous
recombination underpins most methods used
for consolidating synthetic regions. However,
recombinases and prime editing-based approaches
have also been demonstrated to programme
required sequence translocations.
Homology-guided recombination Recombinases Prime editing
Stepwise synthetic genome installation CONEXER leverages high-efficiency conjugative delivery to condense
Technical barriers currently limit the size and type of genome that can be the integration workflow to a single day248. Furthermore, deletion of
delivered in a single step. Subdividing delivery into manageable sections 20 endogenous host factors minimizes unwanted recombination
is possible but requires methodologies to integrate intermediate syn- between the native genome and synthetic DNA. Iterative CONEXER
thetic sections into natural genomic scaffolds while maintaining overall delivery, termed continuous genome synthesis, was used to recode
genome function. To that end, several mechanistically related stepwise 500 kb of the E. coli genome in just 10 days248. The recently reported
genome rewriting methods leverage efficient homologous recombi- SynOMICS method follows a similar structure, with further stepwise
nation and robust counter-selectable markers to enrich for desired bacterial genome replacement capabilities demonstrated in Salmonella
integrations (Fig. 5a). In E. coli, REXER enables the replacement of up typhimurium and Corynebacterium glutamicum26,65,272. In eukaryotes,
to 100 kb of genomic sequence through BAC donors delivered by elec- Swap-In delivery underpinned Sc2.0 yeast chromosome construc-
troporation before Cas9 linearization and λ-Red-driven homologous tion by replacing native sequences with synthetic ‘megachunks’27. The
recombination23,66. GENESIS extends this platform to facilitate iterative recent mSwap-In approach largely mirrors yeast Swap-In by mediat-
REXER-driven replacement of contiguous DNA sequences. The related ing efficient, iterative genomic delivery of >180 kb payloads in mouse
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 308

---

<!-- Page 12 -->

Review article
embryonic stem cells, which perform efficient homologous recombi- recombination (for example, human chromosomes have been trans-
nation (unlike most mammalian cell types)35,273. The synMoss project, ferred to homologous recombination-capable chicken DT40 cells277,278)
which seeks to extend the successes of synthetic genomics into plants, but this process remains highly technically challenging and time con-
has recently applied sequential genome substitution in the homologous suming. Landing pad installation avoids homologous recombination by
recombination-capable bryophyte Physcomitrium patens38 (Fig. 5a). enabling targeted, site-specific recombinase-mediated delivery of large
Homology-dependent genome replacement requires the incom- DNA payloads, at the cost of short recombinase scar sequences36,279.
ing synthetic DNA to maintain the essential functions of replaced Landing pads are frequently single-use and non-functional after
sequences. This functional maintenance is facilitated by design strate- sequence integration. However, some multi-entry and regenerative
gies, such as genome recoding or minimization, but faces challenges strategies offer iterative retargeting, typically at the cost of com-
when structural changes are required. In these cases, more complex plexity with requirements for multiple recombinases or heterotypic
engineering strategies are needed such as the insertion of synthetic recognition sites280–286. Alternatively, targeted writing of recombi-
DNA followed by removal of corresponding native sequences. Alter- nase recognition sites with prime editing has enabled single-step
natively, relocating essential elements to essential arrays or chromo- landing pad installation and DNA delivery in mammalian and plant
somes can free up flexibility for synthetic structural alterations274. genomes189,195,202,287. Notably, programmable recombinases promise
In Sc2.0, tRNA genes are relocated to a synthetic neochromosome27,28. the avoidance of both recombination scarring and recombination
However, consolidation of tRNA gene-free synthetic chromosomes has site installation requirements288–290. Finally, CRISPR-associated trans-
required supplementation with tRNA gene arrays to maintain viability posases also provide useful tools for directed integration of synthetic
prior to tRNA neochromosome delivery29. DNA payloads291–295. Delivery and formation of artificial chromosomes
Delivery of large synthetic DNA is further complicated in recipi- bypasses the integration of synthetic DNA into existing structures, with
ent organisms where efficient homologous recombination is unavail- recent advancements streamlining deployment in eukaryotic synthetic
able. In these cases, the capacity for homologous recombination can genomes (Box 1).
be enhanced or encoded by manipulating native DNA repair path-
ways or introducing exogenous machinery such as λ-Red in some Hierarchical synthetic genome delivery
bacteria205,275,276. However, this solution may induce structural insta- Engineering at the genome scale rapidly approaches a bottleneck when
bility within heavily repetitive genomes. Alternatively, native chromo- linear stepwise manufacturing schemes are employed. The speed and
somes may be transferred to intermediate hosts capable of homologous scale of engineering is constrained by the delivery capacity of each step
Box 1 | Synthesizing artificial chromosomes
Yeast artificial chromosomes are dependent on simple, canonical with the unintended capture of native genomics sequences.
sequences that promote the formation of point centromeres A strategy was developed to bypass the requirement for complex
that govern accurate segregation365,366. Simple production and centromeric DNA — instead using an epigenetic seeding strategy
manipulation of these vectors have led to their employment as to deposit CENP-A and drive centromere formation — but HACs
powerful and flexible tools for diverse biotechnological applications, were still multimerization-dependent and could not be isolated in
for example, replacing native chromosomes with synthetic copies30, single copy371. Work from the same team recently overcame this
introducing supernumerary chromosomes with novel metabolic issue by applying their seeding strategy to a 760-kb yeast artificial
functions246, and large-scale DNA assembly, including entire viral and chromosome, delivered through polyethylene glycol-mediated fusion
bacterial genomes21,245. of spheroplasted donor yeast cells and recipient human cells349,355.
Outside of budding yeast, constructing eukaryotic artificial The increased size of the initial construct is proposed to enable
chromosomes provides a more complex challenge. Natural the formation of distinct chromatin types required for centromere
eukaryotic centromeres can span several megabases, hosting formation without multimerization, hence generating stable and
highly repetitive satellite DNA171. Furthermore, centromere formation predictable single-copy HACs349. With further characterization,
is not defined solely by sequence but rather by association with including locations of centromeric chromatin boundaries, it should
nucleosomes harbouring the CENP-A histone H3 variant367. Human be possible to augment HAC constructs with user-defined payloads
artificial chromosomes (HACs) have therefore largely relied upon for accelerated precision engineering of bottom-up synthetic
top-down approaches such as removing sequences from native chromosomes. Although the maximum size limitations of this
chromosomes through telomere-directed truncations after transfer to approach remain to be determined, an 11.8 Mb chromosome has been
chicken DT40 cells by microcell-mediated chromosome transfer278. generated in yeast, hinting at potential capacity372. Large tetraploid or
These linear, reduced chromosomes typically range from 0.5 to engineered yeast strains may push this capacity further.
10 Mb, becoming unstable below approximately 300 kb (ref. 368). Improved capabilities to transfer artificial chromosomes
Until recently, the de novo generation of HACs relied upon between cells will accelerate their widespread adoption across
transformation of vectors hosting large stretches of highly repetitive synthetic genomics. Highly conserved centromere and kinetochore
captured centromeric alpha satellite DNA, which enable faithful machinery may result in the applicability of recent bottom-up
artificial chromosome segregation but are highly challenging approaches across kingdoms. Synthetic centromere generation
to handle369,370. Furthermore, HAC formation was typified by through histone seeding has already been demonstrated in plants,
extreme, uncontrolled multimerization, during which input DNA indicating the feasibility of plant artificial chromosomes with broad
undergoes substantial duplication and rearrangement, often applications for bioeconomy and food security373.
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 309

---

<!-- Page 13 -->

Review article
(for example, length of synthetic DNA or number of multiplexed edits) blueprint and the constructed genome. Such discrepancies are pri-
and the time needed to recover and validate correct intermediates for marily identified with high-throughput DNA sequencing. However,
further engineering. This bottleneck can be overcome with hierarchical PCR-based approaches remain valuable for rapid quality control during
genome assembly (also referred to as convergent genome assembly), assembly and testing314. Deleterious phenotypes connected to obvi-
in which synthetic regions are installed and validated in parallel prior ous errors, such as nonsense mutations and large deletions, are easily
to rounds of consolidation within single synthetic genomes (Fig. 5b). identified for correction; by contrast, those caused by more cryptic
This approach subsequently provides a route to the construction of ‘bugs’, such as missense mutations, can be challenging to pinpoint,
large, heavily engineered synthetic genomes. especially when several such mutations co-occur. Computational pre-
In bacteria, conjugation and λ-Red recombination facilitate the dictions of protein structure can help to rank missense mutations to
consolidation of large genomic sections manufactured in parallel prioritize repair223.
and thus have played an important role in several bacterial genome Recurrent failed delivery of the correct synthetic genome or
construction projects23,24,26,65,209,296 (Fig. 4b). Hierarchical approaches genomic section indicates potential flaws in sequence design. If
have also underpinned synthetic yeast construction at both the assembly errors or mutations enable propagation of these otherwise
chromosome and genome level. For example, after colocation (that dysfunctional sequences, the problematic regions can be implicated
is, bringing together into a single organism) of semi-synthetic chro- by identifying repeated errors across multiple clones66,315,316 (Fig. 6a).
mosomes by haploid sexual mating, homologous recombination However, if propagation fails outright, more comprehensive redesign
(often in concert with Cas9 or homing endonucleases) has been and testing of synthetic sequences is required. Bug mapping is more
leveraged to guide assembly of fully synthetic chromosomes297–299 complex if synthetic designs are successfully delivered but cause a
(Fig. 4a). Mating-based strategies have similarly been used to con- phenotypic defect. In these cases, similarly comparing mutational
solidate fully synthetic chromosomes within yeast cells29. However, signatures amongst clones with defects may provide clues to bug
chromoduction — where brief cell fusion during incomplete mat- location and mechanism, although higher resolution mapping can be
ing allows target chromosomes to pass from a donor to a receiver achieved by reverting synthetic sequences to functional native variants
yeast cell — may provide a more efficient approach29,300. Similarly, and measuring phenotypic recovery29,299,317,318 (Fig. 6b). This approach
selective ablation of chromosomes after mating may enable efficient is typically complemented with deep omics analysis for multimodal
chromosome transfer246. bug detection26,29,299,315 (Fig. 6c).
Colocation and consolidation of synthetic regions remain chal- Hierarchical assembly and delivery strategies can expedite the
lenging outside of conjugative bacteria and yeast. In mammalian cells, debugging process through the testing of multiple synthetic regions in
microcell-mediated chromosome transfer enables the colocation of parallel at each step, thus avoiding lengthy sequential cycles of stepwise
target chromosomes (although this approach remains highly techni- assembly and debugging318. Similarly, if assembly is conducted in a
cally challenging and time consuming)301,302. Similar approaches have heterologous host, strategies to test part functionality in the destination
been reported in plants using microprotoplasts303 (Fig. 4a). The wider organism prior to final assembly are invaluable. Delivery and testing of
use of nuclear fusion during sexual reproduction may provide further 11 genomes housing different synthetic regions were required to debug
solutions to improving colocation of synthetic regions, notably in assembly of the first complete synthetic bacterial genome JCVI-syn1.0
algal and plant genomes304. Upon colocation of synthetic regions (ref. 21). Alternatively, genetic complementation was used to validate
in target organisms lacking efficient homologous recombination, the functionality of synthetic Caulobacter ethensis-2.0 genome sec-
several CRISPR–Cas, insertion sequence and recombinase-driven tions, specifically by assessing tolerance of transposon-mediated dis-
techniques offer the capacity to programme guided translocations ruption to native sequences in the presence of corresponding synthetic
between semi-synthetic chromosomes288–290,305–309 (Fig. 5b). Improving episomes319. This approach was able to detect several novel genetic
the availability and efficiency of these tools will streamline hierar chical control elements that informed further rounds of design320. Of note,
synthetic chromosome construction, specifically by consolidating strategies that test synthetic regions in parallel may be ineffective in
synthetic chromosomes within the final host organisms to complete detecting synthetic lethal or synergistic bugs that manifest as regions
large eukaryotic synthetic genomes. are combined within a single host22,29.
Despite technological developments, genome delivery remains a Synthetic designs that diverge heavily from natural templates will
slow and challenging step, especially for large genomes. Intermediate require novel solutions for debugging. For example, linking transcrip-
assays that avoid complex delivery steps offer a platform for acceler- tomics with biophysical models of function has improved debugging of
ated prototyping, refinement and iteration of synthetic designs. To synthetic gene circuits321. In combination with expanded omics inputs,
this end, cell-free systems offer an exciting platform to test and refine such as epigenomics, proteomics and metabolomics, this approach
genetic circuits and even entire small viral and organellar genomes310–313. may eventually be scalable to entire synthetic genomes.
Synthetic genome debugging and tailoring Tailoring of synthetic genomes
An incomplete understanding of genome function often compli- Unlike the products of traditional engineering disciplines, biologi-
cates predictions of whether modifications to a natural sequence or cal systems evolve. As such, across generations, synthetic genomes
de novo-designed modules will produce and maintain their intended may diverge in sequence and function from their original designs.
function. As such, synthetic genomes typically require debugging or This evolvability may be harnessed through adaptive laboratory
refinement to identify and correct dysfunctional regions. evolution to tailor or improve synthetic genome function, buffering
against imperfect design and avoiding requirements for costly design
Debugging synthetic genomes iteration26,322–327 (Fig. 6d).
The first step to debugging synthetic genomes is to determine whether Beyond natural mutational processes, the evolvability of a syn-
assembly errors have resulted in discrepancies between the design thetic genome may be modulated during genome design to enhance
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 310

---

<!-- Page 14 -->

Review article
1
0
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 311
lanoitatuM ycneuqerf
a Compiled mutational landscape Fig. 6 | Approaches for debugging synthetic
genomes. a, With imperfect synthetic genome
Disallowed sequences design, mutations may be required for propagation
or rescue of a growth defect. Compiling the
frequency of mutations across a genome or genomic
region can highlight disallowed sequences for
redesign and testing. b, An alternative bug mapping
strategy is to revert synthetic sequences to their
native counterparts and assess phenotypic rescue.
Approaching this process in a highly parallel format
0 kb 20 kb 40 kb 60 kb 80 kb
can provide high-resolution maps of sequence
function. Sequence reversion can be particularly
useful to pinpoint additive bugs that manifest
during hierarchical genome assembly but are not
b Sequence reversion c Multi-omics investigation
detected during earlier rounds of construction and
Genome-incurring growth penalty testing. c, Multi-omics can complement sequence-
based bug mapping, highlighting dysregulation of
normal function. De novo design challenges bug
mapping as references of normal, natural function
Revert to native
sequence may be unavailable. Linking omics data with models
of expected function can reveal the failure of genetic
• Transcriptomics circuit logic and may eventually be applicable
• Ribosomal profiling
• Proteomics at the genome scale. d, Engineered biological
• Chromatin profiling systems can evolve. Therefore, adaptive laboratory
evolution can be used to optimize genome function.
While natural mutational processes can be used,
synthetic diversity-generating mechanisms, such as
SCRaMbLE, can accelerate this process.
Fix bug
d Adaptive laboratory evolution
Genome-incurring growth penalty
Induced hypermutation
Directed evolution
and selection
Growth penalty resolved

---

<!-- Page 15 -->

Review article
or accelerate tailoring. Genetic recoding to hyper-evolvable codes deleterious mutations through codon choice, may be used to pre-
increases the accessibility of protein mutational landscapes by bias- serve function340–345. In addition, hypo-evolvable codes (that is, cod-
ing single nucleotide changes towards non-synonymous mutations ing schemes likely to constrain evolution) may be generated through
(compared to the standard code)69,328,329. Furthermore, several systems, codon compression that directs point mutations to generate deleteri-
including low-fidelity polymerases and oligonucleotide-mediated ous null codons with the corresponding tRNAs or translation factors
recombineering, enable increased mutation rates for accelerated removed69,346.
adaptation towards a desired phenotype208,330–335. Such systems (both Despite the increasing diversity of approaches to manipulate
random and rationally guided towards a desired phenotype) are of evolvability, evolutionary potential has traditionally been overlooked
increased value for organisms with long generation times or low muta- during the design of biological systems. The emerging ‘evotype’ con-
tion rates. Inducible systems are preferred for their ability to restrict cept offers a valuable framework for mapping the evolutionary poten-
potentially maladaptive divergence once a desired performance tial of a system and subsequently sculpting this potential — through
threshold has been reached. Lastly, dynamic synthetic genomes are design — towards desired properties347,348. Such formalization is a cru-
designed to directly encode diversity-generating mechanisms, such cial step in promoting evolution as a key consideration during synthetic
as Sc2.0 with its SCRaMbLE system, offering fast-tracked tailoring genome design. Further improved prediction of likely evolutionary
towards diverse evolved functions336–339. trajectories will inform the integrated design of measures to either
In contrast to optimization through evolution, engineered stabilize function or guide evolvability.
sequences may be at risk of evolved dysfunction if, for example, the
encoded functions are deleterious. Here, control interventions, Conclusion and future perspectives
such as stabilization by sequence entanglement, selection mecha- The construction of a synthetic 7.9-kb poliovirus genome took close
nisms, removal of low-fidelity polymerases and biasing towards to 2 years to complete prior to publication in 2002 (refs. 8,18). Today,
multi-megabase bacterial genomes can be synthesized in just weeks
and the first fully synthetic eukaryotic genome is nearly complete248.
Glossary Synthetic genomics has already provided enhanced understanding
of genome function, including determination of minimal gene com-
plements required to sustain bacterial life and the complex roles of
Biological chassis biocontainment and unnatural protein non-coding sequences in mammalian development22,227. In addition,
A reusable biological platform, capable biosynthesis. synthetic genomes encoded with designed functions already fulfil
of self-maintenance, to which exogenous several applications: synthetic viral genomes have contributed to
genetic modules granting additional Refactoring vaccine development16, recoded bacterial genomes simplify unnatural
functions may be flexibly added. Design scheme aimed at simplifying protein production71 and engineered porcine genomes provide organs
the genetic organization of a system tailored for xenotransplantation41,42. Future applications include tai-
Hierarchical genome while maintaining overall function. lored phage therapies, microbial bioproduction using waste streams
assembly Simple refactoring strategies may (such as plastic, methane and carbon dioxide), disease models for
Consolidation of genomic sections incorporate decompression and personalized medicine, and stress-tolerant crops with enhanced
delivered and installed within discrete defragmentation. Deep refactoring can nutritional profiles. Recent investment has been channelled into
genomes. This process is typically used include the replacement of regulatory further emerging applications, including DNA-based data storage
for higher-order genome construction, elements with synthetic counterparts and biocomputing43,44.
such as generation of fully synthetic and recoding of coding sequences, With progress largely concentrated in bacterial and yeast syn-
chromosomes from semi-synthetic leaving minimal conserved sequence thetic genomics, expansion to larger eukaryotic genomes remains a
parental assemblies, or the colocation or regulatory identity from template key goal for the field. To this end, advancement of large DNA delivery
of multiple synthetic chromosomes sequences. tools to accelerate the hierarchical assembly of such genomes will
within a single cell. be necessary35,37,40,349. Additionally, the multicellular nature of larger
Stepwise genome rewriting eukaryotes entails their single genomes being capable of encoding
Minimization Iterative replacement of native genomic and organizing the structure and development of tissues housing
Reduction of genome content to DNA with synthetic sequences. diverse cell types. In contrast to the substantial tolerance of structural
remove redundancies and non-essential manipulations displayed by bacterial and yeast genomes, greater
elements, resulting in simplified Tailoring consideration of chromatin and 3D architecture will likely therefore be
genomes with improved predictability The post-construction modification of necessary in the design of mammalian, plant and other large eukaryotic
and simplified engineering. a genome to correct design errors or genomes2. These challenges can be addressed moving forward with
optimize function. technologies that rapidly prototype design iterations such as cell-free
Proportion modified systems, organoids and in silico modelling.
A useful heuristic for comparing the Xeno nucleic acids Our understanding of genome function, and the subsequent
scale of synthetic genome projects, Synthetic genetic polymers capable capacity to design genomes encoding desired properties, lags behind
combining the size and complexity of of the storage and recovery of strong construction capabilities. Although minimized genomic chas-
template redesign. information. Xeno nucleic acids are sis augmented with synthetic modules offer a stepping stone towards
orthogonal to natural polymerases and bottom-up design, new approaches are needed to bridge this gap.
Recoding therefore require engineered enzymes The large-scale building and testing of diverse synthetic genomes
Modification of native coding to govern their transcription and provides a highly powerful platform, enabling interrogation of both
schemes with notable applications in replication. genome and cellular function and bypassing many of the limitations
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 312

---

<!-- Page 16 -->

Review article
of sequencing-based approaches. Importantly, expanded genome 14. Thi Nhu Thao, T. et al. Rapid reconstruction of SARS-CoV-2 using a synthetic genomics
platform. Nature 582, 561–565 (2020).
construction will facilitate the training of powerful generative artificial
15. Noyce, R. S., Lederman, S. & Evans, D. H. Construction of an infectious horsepox
intelligence models and predictive computational representations of virus vaccine from chemically synthesized DNA fragments. PLoS One 13, e0188453
genome function. This cycle will be accelerated by the development (2018).
16. Dormitzer, P. R. et al. Synthetic generation of influenza vaccine viruses for rapid response
of automated platforms that facilitate closed-loop design–build–
to pandemics. Sci. Transl. Med. 5, 185ra68 (2013).
test–learn cycles as well as flexible, dedicated design software, even- 17. Menachery, V. D. et al. A SARS-like cluster of circulating bat coronaviruses shows
tually pushing the field towards function-led, abstracted design of potential for human emergence. Nat. Med. 21, 1508–1513 (2015).
18. Venter, J. C., Glass, J. I., Hutchison, C. A. & Vashee, S. Synthetic chromosomes, genomes,
genomes for wide-ranging applications. The accurate digitization
viruses, and cells. Cell 185, 2708–2724 (2022).
of testing of genome designs using computational models will likely 19. Ando, H., Lemire, S., Pires, D. P. & Lu, T. K. Engineering modular viral scaffolds for targeted
further drive advancements, especially in mammalian and plant bacterial population editing. Cell Syst. 1, 187–196 (2015).
20. Gibson, D. G. et al. Complete chemical synthesis, assembly, and cloning of
genomes, where protracted synthesis and long feedback loops restrict
a Mycoplasma genitalium genome. Science 319, 1215–1220 (2008).
advancements. This study demonstrated the bottom-up chemical synthesis and assembly in yeast of
In summary, falling DNA synthesis costs paired with expand- a 532 kb M. genitalium genome.
21. Gibson, D. G. et al. Creation of a bacterial cell controlled by a chemically synthesized
ing capabilities in DNA assembly and delivery will aid transition
genome. Science 329, 52–56 (2010).
from proof-of-concept projects to diverse, bespoke genomes with This seminal work presents the bottom-up chemical synthesis, assembly and delivery
designer functions. This transition will be supported by the continued of a 1.08-Mb M. mycoides genome.
22. Hutchison, C. A. et al. Design and synthesis of a minimal bacterial genome. Science 351,
development of robust computational design software, laboratory
aad6253 (2016).
automation and artificial intelligence for functional prediction and This study presents the bottom-up construction of the heavily minimized 531 kb
generative design. In combination, these advances will continue to JCVI-syn3.0 genome.
23. Fredens, J. et al. Total synthesis of Escherichia coli with a recoded genome. Nature 569,
drive synthetic genomics to a core position within both biological
514–518 (2019).
research and the bioeconomy. However, caution must also be taken This study presents the bottom-up construction of Syn61, a recoded E. coli strain
looking ahead — as synthetic genomes progress from the laboratory to where codon substitutions yield a 61-codon genome. This codon compression has
already been leveraged for non-canonical amino acid incorporation and stringent
real-world applications, biocontainment strategies will be necessary biocontainment.
to prevent escape of engineered organisms69,350,351. Furthermore, the 24. Ostrov, N. et al. Design, synthesis, and testing toward a 57-codon genome. Science 353,
dual-use capacity of synthetic genome technology must be recog- 819–822 (2016).
25. Lajoie, M. J. et al. Genomically recoded organisms expand biological functions. Science
nized. Self-regulation has been a central pillar of modern science since 342, 357–360 (2013).
the 1975 Asilomar conference on recombinant DNA161,352; however, the This article details the construction of a genomically recoded E. coli strain in which all
democratization of DNA and genome synthesis technologies will TAG codons have been converted to TAA.
26. Nyerges, A. et al. Synthetic genomes unveil the effects of synonymous recoding. Preprint
require stronger governance to maintain egalitarian access but at bioRxiv https://doi.org/10.1101/2024.06.16.599206 (2024).
prevent misuse353. 27. Richardson, S. M. et al. Design of a synthetic yeast genome. Science 355, 1040–1044
(2017).
This article describes the design of the Sc2.0 synthetic yeast genome and presents
Published online: 6 November 2024 Biostudio, a CAD tool for eukaryotic genome design.
28. Schindler, D. et al. Design, construction, and functional characterization of a tRNA
References neochromosome in yeast. Cell 186, 5237–5253 (2023).
1. Chari, R. & Church, G. M. Beyond editing to writing large genomes. Nat. Rev. Genet. 18, This article describes the design, assembly and characterization of the Sc2.0 tRNA
749 (2017). neochromosome, containing all 275 native S. cerevisiae tRNA genes.
2. Zhang, W., Mitchell, L. A., Bader, J. S. & Boeke, J. D. Synthetic genomes. Annu. Rev. Biochem. 29. Zhao, Y. et al. Debugging and consolidating multiple synthetic chromosomes reveals
89, 77–101 (2020). combinatorial genetic interactions. Cell 186, 5220–5236.e16 (2023).
3. Shalem, O., Sanjana, N. E. & Zhang, F. High-throughput functional genomics using This article details the generation of the syn6.5 yeast strain, where 6.5 synthetic
CRISPR-Cas9. Nat. Rev. Genet. 16, 299–311 (2015). chromosomes were compiled and debugged within a single cell. This study also
4. Coradini, A. L. V., Hull, C. B. & Ehrenreich, I. M. Building genomes to understand biology. reports the generation of syn7.5; however, characterization is incomplete.
Nat. Commun. 11, 6177 (2020). 30. Annaluru, N. et al. Total synthesis of a functional designer eukaryotic chromosome.
5. Agarwal, K. L. et al. Total synthesis of the gene for an alanine transfer ribonucleic acid Science 344, 55–58 (2014).
from yeast. Nature 227, 27–34 (1970). This work presents synIII, the first synthetic eukaryotic chromosome, constructed as
6. Khorana, H. G. et al. Total synthesis of the structural gene for an alanine transfer part of the Sc2.0 project.
ribonucleic acid from yeast. J. Mol. Biol. 72, 209–217 (1972). 31. Blount, B. A. et al. Synthetic yeast chromosome XI design provides a testbed for the
7. Jackson, D. A., Symons, R. H. & Berg, P. Biochemical method for inserting new genetic study of extrachromosomal circular DNA dynamics. Cell Genomics 3, 100418 (2023).
information into DNA of simian virus 40: circular SV40 DNA molecules containing lambda 32. McCulloch, L. H. et al. Consequences of a telomerase-related fitness defect and
phage genes and the galactose operon of Escherichia coli. Proc. Natl Acad. Sci. USA 69, chromosome substitution technology in yeast synIX strains. Cell Genomics 3, 100419
2904–2909 (1972). (2023).
8. Cello, J., Paul, A. V. & Wimmer, E. Chemical synthesis of poliovirus cDNA: generation 33. Lauer, S. et al. Context-dependent neocentromere activity in synthetic yeast
of infectious virus in the absence of natural template. Science 297, 1016–1018 chromosome VIII. Cell Genomics 3, 100437 (2023).
(2002). 34. Boeke, J. D. et al. The genome project-write. Science 353, 126–127 (2016).
9. Smith, H. O., Hutchison, C. A., Pfannkoch, C. & Venter, J. C. Generating a synthetic 35. Zhang, W. et al. Mouse genome rewriting and tailoring of three important disease loci.
genome by whole genome assembly: φX174 bacteriophage from synthetic Nature 623, 423–431 (2023).
oligonucleotides. Proc. Natl Acad. Sci. USA 100, 15440–15445 (2003). This study applies stepwise genome rewriting to mammalian systems using
10. Chan, L. Y., Kosuri, S. & Endy, D. Refactoring bacteriophage T7. Mol. Syst. Biol. 1, 2005.0018 homologous recombination in mouse embryonic stem cells. This paper proposes
(2005). Genome Project-Write, an initiative to accelerate the large-scale writing and editing of
This study introduces the principle of refactoring to synthetic genomics. The authors synthetic genomes.
applied bespoke design rules to reorganize the T7 bacteriophage genome in one of the 36. Brosh, R. et al. A versatile platform for locus-scale genome rewriting and verification.
first instances of whole-genome redesign. Proc. Natl Acad. Sci. USA 118, e2023952118 (2021).
11. Blight, K. J., Kolykhalov, A. A. & Rice, C. M. Efficient initiation of HCV RNA replication 37. Pampuch, M., Walker, E. J. L. & Karas, B. J. Towards synthetic diatoms: the Phaeodactylum
in cell culture. Science 290, 1972–1974 (2000). tricornutum Pt-syn 1.0 project. Curr. Opin. Green Sustain. Chem. 35, 100611 (2022).
12. Oldfield, L. M. et al. Genome-wide engineering of an infectious clone of herpes simplex 38. Chen, L.-G. et al. A designer synthetic chromosome fragment functions in moss.
virus type 1 using synthetic genomics assembly methods. Proc. Natl Acad. Sci. USA 114, Nat. Plants 10, 228–239 (2024).
E8885–E8894 (2017). This study demonstrates the stepwise delivery of synthetic DNA to the homologous
13. Yount, B. et al. Reverse genetics with a full-length infectious cDNA of severe acute recombination-competent land moss P. patens. This work lays the foundations for the
respiratory syndrome coronavirus. Proc. Natl Acad. Sci. USA 100, 12995–13000 (2003). synMoss project and synthetic plant genomes.
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 313

---

<!-- Page 17 -->

Review article
39. Patron, N. J. Beyond natural: synthetic expansions of botanical form and function. 76. Dunkelmann, D. L., Oehm, S. B., Beattie, A. T. & Chin, J. W. A 68-codon genetic code to
New Phytologist 227, 295–310 (2020). incorporate four distinct non-canonical amino acids enabled by automated orthogonal
40. Dawe, R. K. Charting the path to fully synthetic plant chromosomes. Exp. Cell Res. 390, mRNA design. Nat. Chem. 13, 1110–1117 (2021).
111951 (2020). 77. Neumann, H., Wang, K., Davis, L., Garcia-Alai, M. & Chin, J. W. Encoding multiple
41. Niu, D. et al. Inactivation of porcine endogenous retrovirus in pigs using CRISPR-Cas9. unnatural amino acids via evolution of a quadruplet-decoding ribosome. Nature 464,
Science 357, 1303–1307 (2017). 441–444 (2010).
42. Anand, R. P. et al. Design and testing of a humanized porcine donor for 78. Anderson, J. C. et al. An expanded genetic code with a functional quadruplet codon.
xenotransplantation. Nature 622, 393–401 (2023). Proc. Natl Acad. Sci. USA 101, 7566–7571 (2004).
43. Lu, X. & Ellis, T. Self-replicating digital data storage with synthetic chromosomes. 79. Gerecht, K. et al. The expanded central dogma: genome resynthesis, orthogonal
Natl Sci. Rev. 8, nwab086 (2021). biosystems, synthetic genetics. Annu. Rev. Biophys. 52, 413–432 (2023).
44. Grozinger, L. et al. Pathways to cellular supremacy in biocomputing. Nat. Commun. 10, 80. Pinheiro, V. B. et al. Synthetic genetic polymers capable of heredity and evolution.
5250 (2019). Science 336, 341–344 (2012).
45. Nurk, S. et al. The complete sequence of a human genome. Science 376, 44–53 81. Gallup, O., Ming, H. & Ellis, T. Ten future challenges for synthetic biology. Eng. Biol. 5,
(2022). 51–59 (2021).
46. Li, H. & Durbin, R. Genome assembly in the telomere-to-telomere era. Nat. Rev. Genet. 25, 82. Dymond, J. S. et al. Synthetic chromosome arms function in yeast and generate
658–670 (2024). phenotypic diversity by design. Nature 477, 471–476 (2011).
47. Logsdon, G. A., Vollger, M. R. & Eichler, E. E. Long-read human genome sequencing and This article demonstrates the replacement of a yeast chromosome arm with a
its applications. Nat. Rev. Genet. 21, 597–614 (2020). rewritten synthetic sequence. The authors also introduce the SCRaMbLE system for
48. Yan, B., Tzertzinis, G., Schildkraut, I. & Ettwiller, L. Comprehensive determination of generating combinatorial diversity within synthetic regions.
transcription start sites derived from all RNA polymerases using ReCappable-seq. 83. Shen, Y. et al. SCRaMbLE generates designed combinatorial stochastic diversity in
Genome Res. 32, 162–174 (2022). synthetic chromosomes. Genome Res. 26, 36–49 (2016).
49. Ingolia, N. T., Ghaemmaghami, S., Newman, J. R. S. & Weissman, J. S. Genome-wide 84. Khabarova, A. et al. A Cre-LoxP-based approach for combinatorial chromosome
analysis in vivo of translation with nucleotide resolution using ribosome profiling. rearrangements in human HAP1 cells. Chromosome Res. 31, 11 (2023).
Science 324, 218–223 (2009). 85. Koeppel, J. et al. Randomizing the human genome by engineering recombination
50. Xu, X. et al. Trimming the genomic fat: minimising and re-functionalising genomes using between repeat elements. Preprint at bioRxiv https://doi.org/10.1101/2024.01.22.576745
synthetic biology. Nat. Commun. 14, 1984 (2023). (2024).
51. Pósfai, G. et al. Emergent properties of reduced-genome Escherichia coli. Science 312, 86. Pinglay, S. et al. Multiplex generation and single cell analysis of structural variants in
1044–1046 (2006). a mammalian genome. Preprint at bioRxiv https://doi.org/10.1101/2024.01.22.576756
52. Juhas, M., Eberl, L. & Glass, J. I. Essence of life: essential genes of minimal genomes. (2024).
Trends Cell Biol. 21, 562–568 (2011). 87. Cheng, L. et al. Large-scale genomic rearrangements boost SCRaMbLE in
53. Dervyn, E. et al. Greedy reduction of Bacillus subtilis genome yields emergent Saccharomyces cerevisiae. Nat. Commun. 15, 770 (2024).
phenotypes of high resistance to a DNA damaging agent and low evolvability. 88. Ruf, S. et al. Large-scale analysis of the regulatory architecture of the mouse genome
Nucleic Acids Res. 51, 2974–2992 (2023). with a transposon-associated sensor. Nat. Genet. 43, 379–386 (2011).
54. Sengupta, A. et al. Genome streamlining to improve performance of a fast-growing 89. Jaschke, P. R., Lieberman, E. K., Rodriguez, J., Sierra, A. & Endy, D. A fully decompressed
cyanobacterium Synechococcus elongatus UTEX 2973. mBio 15, e03530–23 synthetic bacteriophage øX174 genome assembled and archived in yeast. Virology 434,
(2024). 278–284 (2012).
55. de Lorenzo, V., Krasnogor, N. & Schmidt, M. For the sake of the bioeconomy: define what 90. Lu, X., Shaw, W. M., Sutradhar, A., Stracquadanio, G. & Ellis, T. Synthetic genome modules
a synthetic biology chassis is! New Biotechnol. 60, 44–51 (2021). designed for programmable silencing of functions and chromosomes. Preprint at bioRxiv
56. Breuer, M. et al. Essential metabolism for a minimal cell. eLife 8, e36842 (2019). https://doi.org/10.1101/2024.03.22.586311 (2024).
57. Rancati, G., Moffat, J., Typas, A. & Pavelka, N. Emerging and evolving concepts in gene 91. Song, M. et al. Control of type III protein secretion using a minimal genetic system.
essentiality. Nat. Rev. Genet. 19, 34–49 (2017). Nat. Commun. 8, 14737 (2017).
58. Winzeler, E. A. et al. Functional characterization of the S. cerevisiae genome by gene 92. Temme, K., Zhao, D. & Voigt, C. A. Refactoring the nitrogen fixation gene cluster from
deletion and parallel analysis. Science 285, 901–906 (1999). Klebsiella oxytoca. Proc. Natl Acad. Sci. USA 109, 7085–7090 (2012).
59. Kamath, R. S. et al. Systematic functional analysis of the Caenorhabditis elegans genome 93. Watanabe, K. et al. Total biosynthesis of antitumor nonribosomal peptides in
using RNAi. Nature 421, 231–237 (2003). Escherichia coli. Nat. Chem. Biol. 2, 423–428 (2006).
60. Giaever, G. et al. Functional profiling of the Saccharomyces cerevisiae genome. Nature 94. Jiang, S. et al. Building a eukaryotic chromosome arm by de novo design and synthesis.
418, 387–391 (2002). Nat. Commun. 14, 7886 (2023).
61. Baba, T. et al. Construction of Escherichia coli K‐12 in‐frame, single‐gene knockout 95. Nielsen, A. A. K. et al. Genetic circuit design automation. Science 352, aac7341 (2016).
mutants: the Keio collection. Mol. Syst. Biol. 2, 2006.0008 (2006). This work presents Cello, a tool for the automated design of sequences encoding
62. Hutchison, C. A. et al. Global transposon mutagenesis and a minimal mycoplasma complex genetic circuits from high-level functional specifications.
genome. Science 286, 2165–2169 (1999). 96. Chen, Z. & Elowitz, M. B. Programmable protein circuit design. Cell 184, 2284–2301
63. Ostrov, N. et al. Synthetic genomes with altered genetic codes. Curr. Opin. Syst. Biol. 24, (2021).
32–40 (2020). 97. Brophy, J. A. N. et al. Synthetic genetic circuits as a means of reprogramming plant roots.
64. de la Torre, D. & Chin, J. W. Reprogramming the genetic code. Nat. Rev. Genet. 22, Science 377, 747–751 (2022).
169–184 (2021). 98. Maroun, J. et al. Designing and building oncolytic viruses. Future Virol. 12, 193–213
65. Lau, Y. H. et al. Large-scale recoding of a bacterial genome by iterative recombineering (2017).
of synthetic DNA. Nucleic Acids Res. 45, 6971–6980 (2017). 99. Gibson, D. G. Programming biological operating systems: genome design, assembly and
66. Wang, K. et al. Defining synonymous codon compression schemes by genome recoding. activation. Nat. Methods 11, 521–526 (2014).
Nature 539, 59–64 (2016). 100. Chen, Y. et al. Genetic circuit design automation for yeast. Nat. Microbiol. 5, 1349–1360
This study details the development of REXER, a strategy to replace large sections of (2020).
the E. coli genome with synthetic copies via programmed recombination. Iterated 101. Jones, T. S., Oliveira, S. M. D., Myers, C. J., Voigt, C. A. & Densmore, D. Genetic circuit
REXER, termed GENESIS, is also reported. design automation with Cello 2.0. Nat. Protoc. 17, 1097–1113 (2022).
67. Ma, N. J. & Isaacs, F. J. Genomic recoding broadly obstructs the propagation of 102. Lu, G. & Moriyama, E. N. Vector NTI, a balanced all-in-one sequence analysis suite.
horizontally transferred genetic elements. Cell Syst. 3, 199–207 (2016). Brief. Bioinformatics 5, 378–388 (2004).
68. Robertson, W. E. et al. Sense codon reassignment enables viral resistance and encoded 103. Zulkower, V. & Rosser, S. DNA Chisel, a versatile sequence optimizer. Bioinformatics 36,
polymer synthesis. Science 372, 1057–1062 (2021). 4508–4509 (2020).
69. Zürcher, J. F. et al. Refactored genetic codes enable bidirectional genetic isolation. 104. Villalobos, A., Ness, J. E., Gustafsson, C., Minshull, J. & Govindarajan, S. Gene designer:
Science 378, 516–523 (2022). a synthetic biology tool for constructing artificial DNA segments. BMC Bioinformatics 7,
70. Sanders, J., Hoffmann, S. A., Green, A. P. & Cai, Y. New opportunities for genetic code 285 (2006).
expansion in synthetic yeast. Curr. Opin. Biotechnol. 75, 102691 (2022). 105. Richardson, S. M., Wheelan, S. J., Yarrington, R. M. & Boeke, J. D. GeneDesign: rapid,
71. Dunkelmann, D. L. et al. Adding α,α-disubstituted and β-linked monomers to the genetic automated design of multikilobase synthetic genes. Genome Res. 16, 550–556
code of an organism. Nature 625, 603–610 (2024). (2006).
72. Quax, T. E. F., Claassens, N. J., Söll, D. & van der Oost, J. Codon bias as a means to 106. Guo, H.-X., Zhu, S.-B., Deng, Z. & Guo, F.-B. EcoliGD: an online tool for designing
fine-tune gene expression. Mol. Cell 59, 149–161 (2015). Escherichia coli genome. ACS Synth. Biol. 11, 2267–2274 (2022).
73. Carr, P. A. & Church, G. M. Genome engineering. Nat. Biotechnol. 27, 1151–1162 (2009). 107. Yu, W. et al. Designing a synthetic moss genome using GenoDesigner. Nat. Plants 10,
74. Zhang, Y. et al. A semi-synthetic organism that stores and retrieves increased genetic 848–856 (2024).
information. Nature 551, 644–647 (2017). 108. Zuker, M. Mfold web server for nucleic acid folding and hybridization prediction.
75. Fischer, E. C. et al. New codons for efficient production of unnatural proteins in a Nucleic Acids Res. 31, 3406–3415 (2003).
semisynthetic organism. Nat. Chem. Biol. 16, 570–576 (2020). 109. Lorenz, R. et al. ViennaRNA package 2.0. Algorithms Mol. Biol. 6, 26 (2011).
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 314

---

<!-- Page 18 -->

Review article
110. Wang, W. et al. trRosettaRNA: automated prediction of RNA 3D structure with 146. Zheng, Y. et al. Machine learning-aided scoring of synthesis difficulties for designer
transformer network. Nat. Commun. 14, 7266 (2023). chromosomes. Sci. China Life Sci. 66, 1615–1625 (2023).
111. Fu, L. et al. UFold: fast and accurate RNA secondary structure prediction with deep 147. Christen, M., Deutsch, S. & Christen, B. Genome calligrapher: a web tool for refactoring
learning. Nucleic Acids Res. 50, e14 (2022). bacterial genome sequences for de novo DNA synthesis. ACS Synth. Biol. 4, 927–934
112. Jumper, J. et al. Highly accurate protein structure prediction with AlphaFold. Nature 596, (2015).
583–589 (2021). 148. Zhang, W. et al. Manipulating the 3D organization of the largest synthetic yeast
113. Abramson, J. et al. Accurate structure prediction of biomolecular interactions with chromosome. Mol. Cell 83, 4424–4437.e5 (2023).
AlphaFold 3. Nature 630, 493–500 (2024). 149. Christen, M., Del Medico, L., Christen, H. & Christen, B. Genome partitioner: a web
114. de Boer, C. G. et al. Deciphering eukaryotic gene-regulatory logic with 100 million tool for multi-level partitioning of large-scale DNA constructs for synthetic biology
random promoters. Nat. Biotechnol. 38, 56–65 (2020). applications. PLoS One 12, e0177234 (2017).
115. LaFleur, T. L., Hossain, A. & Salis, H. M. Automated model-predictive design of synthetic 150. Richardson, S. M. et al. In: Parallel Processing and Applied Mathematics
promoters to control transcriptional profiles in bacteria. Nat. Commun. 13, 5159 (2022). (eds Wyrzykowski, R., Dongarra, J., Karczewski, K. & Wasniewski, J.) 280–289 (Springer,
116. Salis, H. M., Mirsky, E. A. & Voigt, C. A. Automated design of synthetic ribosome binding 2010).
sites to control protein expression. Nat. Biotechnol. 27, 946–950 (2009). 151. Shen, Y. et al. Dissecting aneuploidy phenotypes by constructing Sc2.0 chromosome VII
117. Vaishnav, E. D. et al. The evolution, evolvability and engineering of gene regulatory DNA. and SCRaMbLEing synthetic disomic yeast. Cell Genomics 3, 100364 (2023).
Nature 603, 455–463 (2022). 152. German, S., Pinglay, S., Camellato, B., Fenyö, D. & Boeke, J. D. MenDEL: automated
118. Avsec, Ž. et al. Effective gene expression prediction from sequence by integrating search of BAC sets covering long DNA regions of interest. Preprint at bioRxiv
long-range interactions. Nat. Methods 18, 1196–1203 (2021). https://doi.org/10.1101/2022.06.26.496179 (2022).
119. Zeng, Z., Aptekmann, A. A. & Bromberg, Y. Decoding the effects of synonymous variants. 153. Öling, D. et al. FRAGLER: a fragment recycler application enabling rapid and scalable
Nucleic Acids Res. 49, 12673–12691 (2021). modular DNA assembly. ACS Synth. Biol. 11, 2229–2237 (2022).
120. DaSilva, L. F. et al. DNA-diffusion: leveraging generative models for controlling chromatin 154. Coradini, A. L. V. et al. Building synthetic chromosomes from natural DNA. Nat. Commun.
accessibility and gene expression via synthetic regulatory elements. Preprint at bioRxiv 14, 8337 (2023).
https://doi.org/10.1101/2024.02.01.578352 (2024). 155. Appleton, E., Tao, J., Haddock, T. & Densmore, D. Interactive assembly algorithms for
121. Lal, A., Garfield, D., Biancalani, T. & Eraslan, G. regLM: designing realistic regulatory DNA molecular cloning. Nat. Methods 11, 657–662 (2014).
with autoregressive language models. Preprint at bioRxiv https://doi.org/10.1101/ 156. Mori, H. & Yachie, N. A framework to efficiently describe and share reproducible DNA
2024.02.14.580373 (2024). materials and construction protocols. Nat. Commun. 13, 2894 (2022).
122. Wang, Y. et al. Synthetic promoter design in Escherichia coli based on a deep generative 157. Appleton, E., Madsen, C., Roehner, N. & Densmore, D. Design automation in synthetic
network. Nucleic Acids Res. 48, 6403–6412 (2020). biology. Cold Spring Harb. Perspect. Biol. 9, a023978 (2017).
123. Kotopka, B. J. & Smolke, C. D. Model-driven generation of artificial yeast promoters. 158. Storch, M., Haines, M. C. & Baldwin, G. S. DNA-BOT: a low-cost, automated DNA assembly
Nat. Commun. 11, 2113 (2020). platform for synthetic biology. Synth. Biol. 5, ysaa010 (2020).
124. Zrimec, J. et al. Controlling gene expression with deep generative design of regulatory 159. Ko, S. C., Cho, M., Lee, H. J. & Woo, H. M. Biofoundry palette: planning-assistant software
DNA. Nat. Commun. 13, 5099 (2022). for liquid handler-based experimentation and operation in the biofoundry workflow.
125. Watson, J. L. et al. De novo design of protein structure and function with RFdiffusion. ACS Synth. Biol. 11, 3538–3543 (2022).
Nature 620, 1089–1100 (2023). 160. Luo, Y., James, J. S., Jones, S., Martella, A. & Cai, Y. EMMA-CAD: design automation for
126. Ingraham, J. B. et al. Illuminating protein space with a programmable generative model. synthetic mammalian constructs. ACS Synth. Biol. 11, 579–586 (2022).
Nature 623, 1070–1078 (2023). 161. Dixon, T. A., Curach, N. C. & Pretorius, I. S. Bio‐informational futures. EMBO Rep. 21,
127. Ruffolo, J. A. et al. Design of highly functional genome editors by modeling the universe e50036 (2020).
of CRISPR-Cas sequences. Preprint at bioRxiv https://doi.org/10.1101/2024.04.22.590591 162. Holowko, M. B., Frow, E. K., Reid, J. C., Rourke, M. & Vickers, C. E. Building a biofoundry.
(2024). Synth. Biol. 6, ysaa026 (2021).
128. Cao, L. et al. Design of protein-binding proteins from the target structure alone. Nature 163. Craig, T. et al. Leaf LIMS: a flexible laboratory information management system with
605, 551–560 (2022). a synthetic biology focus. ACS Synth. Biol. 6, 2273–2280 (2017).
129. Yelmen, B. et al. Creating artificial human genomes using generative neural networks. 164. Bartley, B. A., Beal, J., Karr, J. R. & Strychalski, E. A. Organizing genome engineering for
PLoS Genet. 17, e1009303 (2021). the gigabase scale. Nat. Commun. 11, 689 (2020).
130. Dudek, N. K. & Precup, D. Towards AI-designed genomes using a variational autoencoder. 165. Vrana, J. et al. Aquarium: open-source laboratory software for design, execution and data
Preprint at bioRxiv https://doi.org/10.1101/2023.10.22.563484 (2023). management. Synth. Biol. 6, ysab006 (2021).
131. Shao, B. & Yan, J. A long-context language model for deciphering and generating 166. Hillson, N. et al. Building a global alliance of biofoundries. Nat. Commun. 10, 2040
bacteriophage genomes. Nat. Commun. 15, 9392 (2024). (2019).
132. Nguyen, E. et al. Sequence modeling and design from molecular to genome scale with 167. Bryde, D., Broquetas, M. & Volm, J. M. The project benefits of Building Information
Evo. Preprint at bioRxiv https://doi.org/10.1101/2024.02.27.582234 (2024). Modelling (BIM). Int. J. Proj. Manag. 31, 971–980 (2013).
133. Wang, L. & Maranas, C. D. MinGenome: an in silico top-down approach for the synthesis 168. Tellechea-Luzardo, J. et al. Linking engineered cells to their digital twins: a version
of minimized genomes. ACS Synth. Biol. 7, 462–473 (2018). control system for strain engineering. ACS Synth. Biol. 9, 536–545 (2020).
134. Fang, X., Lloyd, C. J. & Palsson, B. O. Reconstructing organisms in silico: genome-scale 169. Carbonell, P., Le Feuvre, R., Takano, E. & Scrutton, N. S. In silico design and automated
models and their emerging applications. Nat. Rev. Microbiol. 18, 731–743 (2020). learning to boost next-generation smart biomanufacturing. Synth. Biol. 5, ysaa020
135. Rees-Garbutt, J. et al. Designing minimal genomes using whole-cell models. Nat. Commun. (2020).
11, 836 (2020). 170. Hoose, A., Vellacott, R., Storch, M., Freemont, P. S. & Ryadnov, M. G. DNA synthesis
This article presents algorithms enabling the design and simulation of minimal genomes technologies to close the gene writing gap. Nat. Rev. Chem. 7, 144–161 (2023).
using whole-cell models. 171. Logsdon, G. A. et al. The variation and evolution of complete human centromeres. Nature
136. Marucci, L. et al. Computer-aided whole-cell design: taking a holistic approach by 629, 136–145 (2024).
integrating synthetic with systems biology. Front. Bioeng. Biotechnol. 8, 567515 (2020). 172. Mali, P. et al. RNA-guided human genome engineering via Cas9. Science 339, 823–826
137. Karr, J. R. et al. A whole-cell computational model predicts phenotype from genotype. (2013).
Cell 150, 389–401 (2012). 173. Jinek, M. et al. A programmable dual-RNA-guided DNA endonuclease in adaptive
This article describes the first whole-cell model, describing the bacterium bacterial immunity. Science 337, 816–821 (2012).
M. genitalium. 174. Gaj, T., Gersbach, C. A. & Barbas, C. F. ZFN, TALEN, and CRISPR/Cas-based methods for
138. Macklin, D. N. et al. Simultaneous cross-evaluation of heterogeneous E. coli datasets via genome engineering. Trends Biotechnol. 31, 397–405 (2013).
mechanistic simulation. Science 369, eaav3751 (2020). 175. Leibowitz, M. L. et al. Chromothripsis as an on-target consequence of CRISPR–Cas9
139. Ye, C. et al. Comprehensive understanding of Saccharomyces cerevisiae phenotypes genome editing. Nat. Genet. 53, 895–905 (2021).
with whole-cell model WM_S288C. Biotechnol. Bioeng. 117, 1562–1574 (2020). 176. Shin, H. Y. et al. CRISPR/Cas9 targeting events cause complex deletions and insertions at
140. Thornburg, Z. R. et al. Fundamental behaviors emerge from simulations of a living 17 sites in the mouse genome. Nat. Commun. 8, 15464 (2017).
minimal cell. Cell 185, 345–360.e28 (2022). 177. Adikusuma, F. et al. Large deletions induced by Cas9 cleavage. Nature 560, E8–E9
141. Szigeti, B. et al. A blueprint for human whole-cell modeling. Curr. Opin. Syst. Biol. 7, 8–15 (2018). (2018).
142. Oberortner, E., Cheng, J. F., Hillson, N. J. & Deutsch, S. Streamlining the design-to-build 178. Weisheit, I. et al. Detection of deleterious on-target effects after HDR-mediated CRISPR
transition with build-optimization software tools. ACS Synth. Biol. 6, 485–496 (2017). editing. Cell Rep. 31, 107689 (2020).
143. Gaeta, A., Zulkower, V. & Stracquadanio, G. Design and assembly of DNA molecules 179. Rees, H. A. & Liu, D. R. Base editing: precision chemistry on the genome and
using multi-objective optimization. Synth. Biol. 6, ysab026 (2021). transcriptome of living cells. Nat. Rev. Genet. 19, 770–788 (2018).
144. Halper, S. M., Hossain, A. & Salis, H. M. Synthesis success calculator: predicting the 180. Komor, A. C., Kim, Y. B., Packer, M. S., Zuris, J. A. & Liu, D. R. Programmable editing of
rapid synthesis of DNA fragments with machine learning. ACS Synth. Biol. 9, 1563–1571 a target base in genomic DNA without double-stranded DNA cleavage. Nature 533,
(2020). 420–424 (2016).
145. Doçi, G. et al. DNA Scanner: a web application for comparing DNA synthesis feasibility, 181. Gaudelli, N. M. et al. Programmable base editing of T to G C in genomic DNA without
price and turnaround time across vendors. Synth. Biol. 5, ysaa011 (2020). DNA cleavage. Nature 551, 464–471 (2017).
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 315

---

<!-- Page 19 -->

Review article
182. Chen, L. et al. Programmable C:G to G:C genome editing with CRISPR-Cas9-directed 215. Wang, C. et al. dCas9-based gene editing for cleavage-free genomic knock-in of long
base excision repair proteins. Nat. Commun. 12, 1384 (2021). sequences. Nat. Cell Biol. 24, 268–278 (2022).
183. Kurt, I. C. et al. CRISPR C-to-G base editors for inducing targeted DNA transversions in 216. Ostrov, N. et al. Technological challenges and milestones for writing genomes. Science
human cells. Nat. Biotechnol. 39, 41–46 (2020). 366, 310–312 (2019).
184. Smith, C. J. et al. Enabling large-scale genome editing at repetitive elements by reducing 217. Hughes, T. R. et al. Expression profiling using microarrays fabricated by an ink-jet
DNA nicking. Nucleic Acids Res. 48, 5183–5195 (2020). oligonucleotide synthesizer. Nat. Biotechnol. 19, 342–347 (2001).
185. Chen, Y. et al. Multiplex base editing to convert TAG into TAA codons in the human 218. Palluk, S. et al. De novo DNA synthesis using polymerase-nucleotide conjugates.
genome. Nat. Commun. 13, 4482 (2022). Nat. Biotechnol. 36, 645–650 (2018).
186. Anzalone, A. V. et al. Search-and-replace genome editing without double-strand breaks 219. Fuller, C. W. et al. Molecular electronics sensors on a scalable semiconductor chip:
or donor DNA. Nature 576, 149–157 (2019). a platform for single-molecule measurement of binding kinetics and enzyme activity.
This work presents the development of prime editing, which enables users to Proc. Natl Acad. Sci. USA 119, e2112812119 (2022).
programme all 12 base substitutions and small insertions or deletions. 220. Kouprina, N. & Larionov, V. Transformation-associated recombination (TAR) cloning for
187. Chen, P. J. & Liu, D. R. Prime editing for precise and highly versatile genome genomics studies and synthetic biology. Chromosoma 125, 621–632 (2016).
manipulation. Nat. Rev. Genet. 24, 161–177 (2023). 221. Kouprina, N. & Larionov, V. Selective isolation of genomic loci from complex genomes
188. Chen, P. J. et al. Enhanced prime editing systems by manipulating cellular determinants by transformation-associated recombination cloning in the yeast Saccharomyces
of editing outcomes. Cell 184, 5635–5652.e29 (2021). cerevisiae. Nat. Protoc. 3, 371–377 (2008).
189. Anzalone, A. V. et al. Programmable deletion, replacement, integration and inversion of 222. Zhao, Y. et al. CREEPY: CRISPR-mediated editing of synthetic episomes in yeast.
large DNA sequences with twin prime editing. Nat. Biotechnol. 40, 731–740 (2022). Nucleic Acids Res. 51, e72 (2023).
190. Grünewald, J. et al. Engineered CRISPR prime editors with compact, untethered reverse 223. Rudolph, A. et al. Strategies to identify and edit improvements in synthetic genome
transcriptases. Nat. Biotechnol. 41, 337–343 (2022). segments episomally. Nucleic Acids Res. 51, 10094–10106 (2023).
191. Nelson, J. W. et al. Engineered pegRNAs improve prime editing efficiency. Nat. Biotechnol. 224. Liu, L., Huang, Y. & Wang, H. H. Fast and efficient template-mediated synthesis of genetic
40, 402–410 (2022). variants. Nat. Methods 20, 841–848 (2023).
192. Wang, J. et al. Efficient targeted insertion of large DNA fragments without DNA donors. 225. Martella, A., Matjusaitis, M., Auxillos, J., Pollard, S. M. & Cai, Y. EMMA: an extensible
Nat. Methods 19, 331–340 (2022). mammalian modular assembly toolkit for the rapid design and production of diverse
193. Doman, J. L. et al. Phage-assisted evolution and protein engineering yield compact, expression vectors. ACS Synth. Biol. 6, 1380–1392 (2017).
efficient prime editors. Cell 186, 3983–4002.e26 (2023). 226. Di Blasi, R., Zouein, A., Ellis, T. & Ceroni, F. Genetic toolkits to design and build
194. Koeppel, J. et al. Prediction of prime editing insertion efficiencies using sequence mammalian synthetic systems. Trends Biotechnol. 39, 1004–1018 (2021).
features and DNA repair determinants. Nat. Biotechnol. 41, 1446–1456 (2023). 227. Pinglay, S. et al. Synthetic regulatory reconstitution reveals principles of mammalian Hox
195. Yarnall, M. T. N. et al. Drag-and-drop genome insertion of large sequences without cluster regulation. Science 377, eabk2820 (2022).
double-strand DNA cleavage using CRISPR-directed integrases. Nat. Biotechnol. 41, 228. Ma, S., Saaem, I. & Tian, J. Error correction in gene synthesis technology.
500–512 (2023). Trends Biotechnol. 30, 147–154 (2012).
196. Ferreira da Silva, J. et al. Click editing enables programmable genome writing using 229. Sidore, A. M., Plesa, C., Samson, J. A., Lubock, N. B. & Kosuri, S. DropSynth 2.0:
DNA polymerases and HUH endonucleases. Nat. Biotechnol. https://doi.org/10.1038/ high-fidelity multiplexed gene synthesis in emulsions. Nucleic Acids Res. 48, e95 (2020).
s41587-024-02324-x (2024). 230. Gibson, D. G. et al. Enzymatic assembly of DNA molecules up to several hundred
197. Cong, L. et al. Multiplex genome engineering using CRISPR/Cas systems. Science 339, kilobases. Nat. Methods 6, 343–345 (2009).
819–823 (2013). 231. Engler, C., Kandzia, R. & Marillonnet, S. A one pot, one step, precision cloning method
198. Ran, F. A. et al. Double nicking by RNA-guided CRISPR cas9 for enhanced genome with high throughput capability. PLoS One 3, e3647 (2008).
editing specificity. Cell 154, 1380–1389 (2013). 232. Pryor, J. M. et al. Enabling one-pot golden gate assemblies of unprecedented
199. Essletzbichler, P. et al. Megabase-scale deletion using CRISPR/Cas9 to generate a fully complexity using data-optimized assembly design. PLoS One 15, e0238592 (2020).
haploid human cell line. Genome Res. 24, 2059–2065 (2014). 233. Pryor, J. M., Potapov, V., Bilotti, K., Pokhrel, N. & Lohman, G. J. S. Rapid 40 kb genome
200. Lin, Q. et al. High-efficiency prime editing with optimized, paired pegRNAs in plants. construction from 52 parts through data-optimized assembly design. ACS Synth. Biol. 11,
Nat. Biotechnol. 39, 923–927 (2021). 2036–2042 (2022).
201. Choi, J. et al. Precise genomic deletions using paired prime editing. Nat. Biotechnol. 40, 234. Lund, S., Potapov, V., Johnson, S. R., Buss, J. & Tanner, N. A. Highly parallelized
218–226 (2022). construction of DNA from low-cost oligonucleotide mixtures using data-optimized
202. Pandey, S. et al. Efficient site-specific integration of large genes in mammalian cells assembly design and golden gate. ACS Synth. Biol. 13, 745–751 (2024).
via continuously evolved recombinases and prime editing. Nat. Biomed. Eng. 235. James, J. S. et al. Automation and expansion of EMMA assembly for fast-tracking
https://doi.org/10.1038/s41551-024-01227-1 (2024). mammalian system engineering. ACS Synth. Biol. 11, 587–595 (2022).
203. Kita, Y. et al. Dual CRISPR-Cas3 system for inducing multi-exon skipping in DMD 236. Lartigue, C. et al. Creating bacterial strains from genomes that have been cloned and
patient-derived iPSCs. Stem Cell Rep. 18, 1753–1765 (2023). engineered in yeast. Science 325, 1693–1696 (2009).
204. Morisaka, H. et al. CRISPR-Cas3 induces broad and unidirectional genome editing in This work builds on Lartigue et al. (2007), enabling the delivery of genomes cloned in
human cells. Nat. Commun. 10, 5302 (2019). yeast to bacterial cells by deactivating endogenous bacterial restriction enzymes.
205. Yu, D. et al. An efficient recombination system for chromosome engineering in 237. DiCarlo, J. E. et al. Genome engineering in Saccharomyces cerevisiae using CRISPR-Cas
Escherichia coli. Proc. Natl Acad. Sci. USA 97, 5978–5983 (2000). systems. Nucleic Acids Res. 41, 4336–4343 (2013).
206. Ellis, H. M., Yu, D., DiTizio, T. & Court, D. L. High efficiency mutagenesis, repair, and 238. Postma, E. D. et al. A supernumerary designer chromosome for modular in vivo
engineering of chromosomal DNA using single-stranded oligonucleotides. Proc. Natl pathway assembly in Saccharomyces cerevisiae. Nucleic Acids Res. 49, 1769–1783
Acad. Sci. USA 98, 6742–6746 (2001). (2021).
207. Gallagher, R. R., Li, Z., Lewis, A. O. & Isaacs, F. J. Rapid editing and evolution of bacterial 239. Karas, B. J. et al. Direct transfer of whole genomes from bacteria to yeast. Nat. Methods
genomes using libraries of synthetic DNA. Nat. Protoc. 9, 2301–2316 (2014). 10, 410–412 (2013).
208. Wang, H. H. et al. Programming cells by multiplex genome engineering and accelerated 240. Gibson, D. G. et al. One-step assembly in yeast of 25 overlapping DNA fragments to form
evolution. Nature 460, 894–898 (2009). a complete synthetic Mycoplasma genitalium genome. Proc. Natl Acad. Sci. USA 105,
This study introduces MAGE, a strategy to direct targeted mutations throughout 20404–20409 (2008).
the E. coli genome using libraries of oligonucleotides and λ-Red mediated 241. Gibson, D. G. Synthesis of DNA fragments in yeast by one-step assembly of overlapping
recombineering. oligonucleotides. Nucleic Acids Res. 37, 6984–6990 (2009).
209. Isaacs, F. J. et al. Precise manipulation of chromosomes in vivo enables genome-wide 242. Mitchell, L. A. et al. De novo assembly and delivery to mouse cells of a 101 kb functional
codon replacement. Science 333, 348–353 (2011). human gene. Genetics 218, iyab038 (2021).
This study presents conjugation assembly genome engineering, which combines This article presents eSwap-In, a stepwise strategy to build large episomal constructs
conjugation and recombination to facilitate hierarchical consolidation of large in yeast.
genomic regions of the E. coli genome constructed in parallel. 243. Benders, G. A. et al. Cloning whole bacterial genomes in yeast. Nucleic Acids Res. 38,
210. Wannier, T. M. et al. Improved bacterial recombineering by parallelized protein discovery. 2558–2569 (2010).
Proc. Natl Acad. Sci. USA 117, 13689–13698 (2020). 244. Zhou, J., Wu, R., Xue, X. & Qin, Z. CasHRA (Cas9-facilitated homologous recombination
211. Bonde, M. T. et al. MODEST: a web-based design tool for oligonucleotide-mediated assembly) method of constructing megabase-sized DNA. Nucleic Acids Res. 44, e124
genome engineering and recombineering. Nucleic Acids Res. 42, W408–W415 (2014). (2016).
212. Quintin, M. et al. Merlin: computer-aided oligonucleotide design for large scale genome 245. He, B. et al. YLC-assembly: large DNA assembly via yeast life cycle. Nucleic Acids Res. 51,
engineering with MAGE. ACS Synth. Biol. 5, 452–458 (2016). 8283–8292 (2023).
213. Dicarlo, J. E. et al. Yeast oligo-mediated genome engineering (YOGE). ACS Synth. Biol. 2, 246. Ma, Y. et al. Convenient synthesis and delivery of a megabase-scale designer accessory
741–749 (2013). chromosome empower biosynthetic capacity. Cell Res. 34, 309–322 (2024).
214. Barbieri, E. M., Muir, P., Akhuetie-Oni, B. O., Yellman, C. M. & Isaacs, F. J. Precise editing This article details a strategy to conduct rapid hierarchical episomal DNA assembly in
at DNA replication forks enables multiplex genome engineering in eukaryotes. Cell 171, yeast, using programmed haploidization to bypass sporulation. This approach is used to
1453–1467.e13 (2017). generate a 1.024-Mb accessory chromosome encoding expanded metabolic functions.
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 316

---

<!-- Page 20 -->

Review article
247. Neil, D. L. et al. Structural instability of human tandemly repeated DNA sequences 279. Iacovino, M. et al. Inducible cassette exchange: a rapid and efficient system enabling
cloned in yeast artificial chromosome vectors. Nucleic Acids Res. 18, 1421–1428 conditional gene expression in embryonic stem and primary cells. Stem Cell 29,
(1990). 1580–1588 (2011).
248. Zürcher, J. F. et al. Continuous synthesis of E. coli genome sections and Mb-scale human 280. Dafhnis-Calas, F. et al. Iterative in vivo assembly of large and complex transgenes by
DNA assembly. Nature 619, 555–562 (2023). combining the activities of φC31 integrase and Cre recombinase. Nucleic Acids Res. 33,
This article describes CONEXER, an updated version of the REXER protocol for e189 (2005).
replacing large sections of the E. coli genome, using conjugation to deliver synthetic 281. Wallace, H. A. C. et al. Manipulating the mouse genome to engineer precise functional
payloads. Iterated CONEXER, or continuous genome synthesis, is projected to syntenic replacements with human sequence. Cell 128, 197–209 (2007).
reduce the construction of fully synthetic E. coli genomes to 2 months. BAC stepwise 282. Kameyama, Y., Kawabe, Y., Ito, A. & Kamihira, M. An accumulative site-specific gene
insertion synthesis is also described, a related technique capable of construction integration system using Cre recombinase-mediated cassette exchange. Biotechnol. Bioeng.
megabase-scale episomes of repetitive human DNA. 105, 1106–1114 (2010).
249. Umenhoffer, K. et al. Genome-wide abolishment of mobile genetic elements using 283. Hou, L. et al. An open-source system for in planta gene stacking by Bxb1 and cre
genome shuffling and CRISPR/Cas-assisted MAGE allows the efficient stabilization of recombinases. Mol. Plant. 7, 1756–1765 (2014).
a bacterial chassis. ACS Synth. Biol. 6, 1471–1483 (2017). 284. Suzuki, T., Kazuki, Y., Oshimura, M. & Hara, T. A novel system for simultaneous or
250. Tsuge, K. et al. Method of preparing an equimolar DNA mixture for one-step DNA sequential integration of multiple gene-loading vectors into a defined site of a human
assembly of over 50 fragments. Sci. Rep. 5, 10655 (2015). artificial chromosome. PLoS One 9, 110404 (2014).
251. Itaya, M., Fujita, K., Kuroki, A. & Tsuge, K. Bottom-up genome assembly using the 285. Lee, N. C. O. et al. Method to assemble genomic DNA fragments or genes on human
Bacillus subtilis genome vector. Nat. Methods 5, 41–43 (2008). artificial chromosome with regulated kinetochore using a multi-integrase system.
252. Itaya, M., Tsuge, K., Koizumi, M. & Fujita, K. Combining two genomes in one cell: stable ACS Synth. Biol. 7, 63–74 (2018).
cloning of the Synechocystis PCC6803 genome in the Bacillus subtilis 168 genome. 286. Elmore, J. R. et al. High-throughput genetic engineering of nonmodel and
Proc. Natl Acad. Sci. USA 102, 15971–15976 (2005). undomesticated bacteria via iterative site-specific genome integration. Sci. Adv. 9,
253. Itaya, M. et al. Far rapid synthesis of giant DNA in the Bacillus subtilis genome by a eade1285 (2023).
conjugation transfer system. Sci. Rep. 8, 8792 (2018). 287. Sun, C. et al. Precise integration of large DNA sequences in plant genomes using
254. Liberante, F. G. & Ellis, T. From kilobases to megabases: design and delivery of large DNA PrimeRoot editors. Nat. Biotechnol. 42, 316–327 (2024).
constructs into mammalian genomes. Curr. Opin. Syst. Biol. 25, 1–10 (2021). 288. Durrant, M. G. et al. Bridge RNAs direct programmable recombination of target and
255. Lartigue, C. et al. Genome transplantation in bacteria: changing one species to another. donor DNA. Nature 630, 984–993 (2024).
Science 317, 632–638 (2007). 289. Mukhametzyanova, L. et al. Activation of recombinases at specific DNA loci
This work presents a key advancement in whole-genome delivery, enabling the by zinc-finger domain insertions. Nat. Biotechnol. https://doi.org/10.1038/
shuttling of intact genomes between cells and ‘booting up’ of delivered genomes. s41587-023-02121-y (2024).
256. Labroussaa, F. et al. Impact of donor–recipient phylogenetic distance on bacterial 290. Siddiquee, R., Pong, C. H., Hall, R. M. & Ataide, S. F. A programmable seekRNA guides
genome transplantation. Nucleic Acids Res. 44, 8501–8511 (2016). target selection by IS1111 and IS110 type insertion sequences. Nat. Commun. 15, 5235
257. Baby, V. et al. Cloning and transplantation of the Mesoplasma florum genome. (2024).
ACS Synth. Biol. 7, 209–217 (2018). 291. Vo, P. L. H. et al. CRISPR RNA-guided integrases for high-efficiency, multiplexed bacterial
258. Fan, C. et al. Chromosome-free bacterial cells are safe and programmable platforms for genome engineering. Nat. Biotechnol. 39, 480–489 (2021).
synthetic biology. Proc. Natl Acad. Sci. USA 117, 6752–6761 (2020). 292. Tou, C. J., Orr, B. & Kleinstiver, B. P. Precise cut-and-paste DNA insertion using
259. Adamala, K. P., Martin-Alarcon, D. A., Guthrie-Honea, K. R. & Boyden, E. S. Engineering engineered type V-K CRISPR-associated transposases. Nat. Biotechnol. 41, 968–979
genetic circuit interactions within and between synthetic minimal cells. Nat. Chem. 9, (2023).
431–439 (2017). 293. Wang, X. et al. Long sequence insertion via CRISPR/Cas gene-editing with transposase,
260. Buddingh’, B. C. & van Hest, J. C. M. Artificial cells: synthetic compartments with life-like recombinase, and integrase. Curr. Opin. Biomed. Eng. 28, 100491 (2023).
functionality and adaptivity. Acc. Chem. Res. 50, 769–777 (2017). 294. Lampe, G. D. et al. Targeted DNA integration in human cells without double-strand breaks
261. Bock, R. Engineering plastid genomes: methods, tools, and applications in basic using CRISPR-associated transposases. Nat. Biotechnol. 42, 87–98 (2024).
research and biotechnology. Annu. Rev. Plant Biol. 66, 211–241 (2015). 295. Liu, P. et al. Transposase-assisted target-site integration for efficient plant genome
262. Dyo, Y. M. & Purton, S. The algal chloroplast as a synthetic biology platform for engineering. Nature 631, 593–600 (2024).
production of therapeutic proteins. Microbiology 164, 113–121 (2018). 296. Wang, K., de la Torre, D., Robertson, W. E. & Chin, J. W. Programmed chromosome fission
263. Silva-Pinheiro, P. & Minczuk, M. The potential of mitochondrial genome engineering. and fusion enable precise large-scale genome rearrangement and assembly. Science
Nat. Rev. Genet. 23, 199–214 (2022). 365, 922–926 (2019).
264. Coale, T. H. et al. Nitrogen-fixing organelle in a marine alga. Science 384, 217–222 297. Zhang, W. et al. Engineering the ribosomal DNA in a megabase synthetic chromosome.
(2024). Science 355, eaaf3981 (2017).
265. Gibson, D. G., Smith, H. O., Hutchison, C. A., Venter, J. C. & Merryman, C. Chemical 298. Shen, Y. et al. Deep functional analysis of synII, a 770-kilobase synthetic yeast
synthesis of the mouse mitochondrial genome. Nat. Methods 7, 901–903 (2010). chromosome. Science 355, eaaf4791 (2017).
266. Greiner, S. et al. Chloroplast nucleoids are highly dynamic in ploidy, number, and 299. Foo, J. L. et al. Establishing chromosomal design-build-test-learn through a synthetic
structure during angiosperm leaf development. Plant J. 102, 730–746 (2020). chromosome and its combinatorial reconfiguration. Cell Genomics 3, 100435
267. Walker, E. J. L., Pampuch, M., Chang, N., Cochrane, R. R. & Karas, B. J. Design and (2023).
assembly of the 117-kb Phaeodactylum tricornutum chloroplast genome. Plant. Physiol. 300. Dutcher, S. K. Internuclear transfer of genetic information in kar1-1/KAR1 heterokaryons
194, 2217–2228 (2024). in saccharomyces cerevisiae. Mol. Cell. Biol. 1, 245–253 (1981).
268. Klein, T. M., Wolf, E. D., Wu, R. & Sanford, J. C. High-velocity microprojectiles for delivering 301. Liskovykh, M., Lee, N. C., Larionov, V. & Kouprina, N. Moving toward a higher efficiency
nucleic acids into living cells. Nature 327, 70–73 (1987). of microcell-mediated chromosome transfer. Mol. Ther. Methods Clin. Dev. 3, 16043
269. Karas, B. J. et al. Designer diatom episomes delivered by bacterial conjugation. (2016).
Nat. Commun. 6, 6925 (2015). 302. Liskovykh, M., Larionov, V. & Kouprina, N. Highly efficient microcell-mediated transfer of
270. Yoshizumi, T., Oikawa, K., Chuah, J.-A., Kodama, Y. & Numata, K. Selective gene HACs containing a genomic region of interest into mammalian cells. Curr. Protoc. 1, e236
delivery for integrating exogenous DNA into plastid and mitochondrial genomes using (2021).
peptide–DNA complexes. Biomacromolecules 19, 1582–1591 (2018). 303. Verhoeven, H. A. et al. Partial genome transfer through micronuclei in plants.
271. Kwak, S.-Y. et al. Chloroplast-selective gene delivery and expression in planta using Acta Botanica Neerlandica 40, 97–113 (1991).
chitosan-complexed single-walled carbon nanotube carriers. Nat. Nanotechnol. 14, 304. Goold, H. D., Moseley, J. L. & Lauersen, K. J. The synthetic future of algal genomes.
447–455 (2019). Cell Genomics 4, 100505 (2024).
272. Ye, Y. et al. Genomic iterative replacements of large synthetic DNA fragments in 305. Smith, A. J. H. et al. A site-directed chromosomal translocation induced in embryonic
Corynebacterium glutamicum. ACS Synth. Biol. 11, 1588–1599 (2022). stem cells by Cre-loxP recombination. Nat. Genet. 9, 376–385 (1995).
273. Macdonald, L. E. et al. Precise and in situ genetic humanization of 6 Mb of mouse 306. Proudfoot, C., McPherson, A. L., Kolb, A. F. & Stark, W. M. Zinc finger recombinases with
immunoglobulin genes. Proc. Natl Acad. Sci. USA 111, 5147–5152 (2014). adaptable DNA sequence specificity. PLoS One 6, e19537 (2011).
274. Dai, J., Boeke, J. D., Luo, Z., Jiang, S. & Cai, Y. Sc3.0: revamping and minimizing the yeast 307. Torres, R. et al. Engineering human tumour-associated chromosomal translocations with
genome. Genome Biol. 21, 205 (2020). the RNA-guided CRISPR–Cas9 system. Nat. Commun. 5, 3964 (2014).
275. Liu, M. et al. Methodologies for improving HDR efficiency. Front. Genet. 9, 691 (2019). 308. Kweon, J. et al. Targeted genomic translocations and inversions generated using a paired
276. Yeh, C. D., Richardson, C. D. & Corn, J. E. Advances in genome editing through control of prime editing strategy. Mol. Ther. 31, 249–259 (2023).
DNA repair pathways. Nat. Cell Biol. 21, 1468–1478 (2019). 309. Hiraizumi, M. et al. Structural mechanism of bridge RNA-guided recombination. Nature
277. Dieken, E. S., Epner, E. M., Fiering, S., Fournier, R. E. K. & Groudine, M. Efficient 630, 994–1002 (2024).
modification of human chromosomal alleles using recombination-proficient 310. Böhm, C. V. et al. Chloroplast cell-free systems from different plant species as a rapid
chicken/human microcell hybrids. Nat. Genet. 12, 174–182 (1996). prototyping platform. ACS Synth. Biol. 13, 2412–2424 (2024).
278. Kazuki, Y. et al. Refined human artificial chromosome vectors for gene therapy and 311. Silverman, A. D., Karim, A. S. & Jewett, M. C. Cell-free gene expression: an expanded
animal transgenesis. Gene Ther. 18, 384–393 (2011). repertoire of applications. Nat. Rev. Genet. 21, 151–170 (2020).
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 317

---

<!-- Page 21 -->

Review article
312. Rustad, M., Eastlund, A., Jardine, P. & Noireaux, V. Cell-free TXTL synthesis of 348. Castle, S. D., Stock, M. & Gorochowski, T. E. Engineering is evolution:
infectious bacteriophage T4 in a single test tube reaction. Synth. Biol. 3, ysy002 a perspective on design processes to engineer biology. Nat. Commun. 15, 3640
(2018). (2024).
313. Shin, J., Jardine, P. & Noireaux, V. Genome replication, synthesis, and assembly of the 349. Gambogi, C. W. et al. Efficient formation of single-copy human artificial chromosomes.
bacteriophage T7 in a single cell-free reaction. ACS Synth. Biol. 1, 408–413 (2012). Science 383, 1344–1349 (2024).
314. Mitchell, L. A. et al. qPCRTag analysis — a high throughput, real time PCR assay for Sc2.0 This study uses yeast spheroplast fusion and epigenetic centromere seeding
genotyping. J. Vis. Exp. 2015, e52941 (2015). to generate stable HACs. This new generation of HACs can be maintained as
315. Mitchell, L. A. et al. Synthesis, debugging, and effects of synthetic chromosome single copies and do not undergo multimerization, facilitating predictable
consolidation: synVI and beyond. Science 355, eaaf4831 (2017). engineering.
316. Wu, Y. et al. Bug mapping and fitness testing of chemically synthesized chromosome X. 350. Lee, J. W., Chan, C. T. Y., Slomovic, S. & Collins, J. J. Next-generation biocontainment
Science 355, eaaf4706 (2017). systems for engineered organisms. Nat. Chem. Biol. 14, 530–537 (2018).
317. Sadhu, M. J., Bloom, J. S., Day, L. & Kruglyak, L. CRISPR-directed mitotic recombination 351. Hoffmann, S. A. et al. Safety by design: biosafety and biosecurity in the age of synthetic
enables genetic mapping without crosses. Science 352, 1113–1116 (2016). genomics. iScience 26, 106165 (2023).
318. Lin, Y., Zou, X., Zheng, Y., Cai, Y. & Dai, J. Improving chromosome synthesis with a 352. Berg, P., Baltimore, D., Brenner, S., Roblin, R. O. & Singer, M. F. Summary statement of
semiquantitative phenotypic assay and refined assembly strategy. ACS Synth. Biol. 8, the Asilomar conference on recombinant DNA molecules. Proc. Natl Acad. Sci. USA 72,
2203–2211 (2019). 1981–1984 (1975).
319. Venetz, J. E. et al. Chemical synthesis rewriting of a bacterial genome to achieve 353. Carter, S. R., Yassif, J. M. & Isaac, C. R. Benchtop DNA Synthesis Devices:
design flexibility and biological functionality. Proc. Natl Acad. Sci. USA 116, 8070–8079 Capabilities, Biosecurity Implications, and Governance https://www.nti.org/analysis/
(2019). articles/benchtop-dna-synthesis-devices-capabilities-biosecurity-implications-and-
320. van Kooten, M. J. F. M., Scheidegger, C. A., Christen, M. & Christen, B. The transcriptional governance/ (2023).
landscape of a rewritten bacterial genome reveals control elements and genome design 354. Li, L.-P. et al. Transgenic mice with a diverse human T cell antigen receptor repertoire.
principles. Nat. Commun. 12, 3053 (2021). Nat. Med. 16, 1029–1034 (2010).
321. Gorochowski, T. E. et al. Genetic circuit characterization and debugging using RNA‐seq. 355. Brown, D. M. et al. Efficient size-independent chromosome delivery from yeast to
Mol. Syst. Biol. 13, 952 (2017). cultured cell lines. Nucleic Acids Res. 45, e50 (2017).
322. Wannier, T. M. et al. Adaptive evolution of genomically recoded Escherichia coli. 356. Shitut, S. et al. Generating heterokaryotic cells via bacterial cell-cell fusion.
Proc. Natl Acad. Sci. USA 115, 3090–3095 (2018). Microbiol. Spectr. 10, e0169322 (2022).
323. Choe, D. et al. Adaptive laboratory evolution of a genome-reduced Escherichia coli. 357. Rems, L. et al. Cell electrofusion using nanosecond electric pulses. Sci. Rep. 3, 3382
Nat. Commun. 10, 935 (2019). (2013).
324. Lässig, M., Mustonen, V. & Nourmohammad, A. Steering and controlling 358. Leroy, H. et al. Virus-mediated cell-cell fusion. Int. J. Mol. Sci. 21, 9644 (2020).
evolution — from bioengineering to fighting pathogens. Nat. Rev. Genet. 24, 359. Waters, V. L. Conjugation between bacterial and mammalian cells. Nat. Genet. 231,
851–867 (2023). 375–376 (2001).
325. Moger-Reischer, R. Z. et al. Evolution of a minimal cell. Nature 620, 122–127 (2023). 360. Ma, N. J., Moonan, D. W. & Isaacs, F. J. Precise manipulation of bacterial
326. Sandberg, T. E. et al. Adaptive evolution of a minimal organism with a synthetic genome. chromo somes by conjugative assembly genome engineering. Nat. Protoc. 9,
iScience 26, 107500 (2023). 2285–2300 (2014).
327. Williams, T. C. et al. Parallel laboratory evolution and rational debugging reveal genomic 361. Lacroix, B. & Citovsky, V. Transfer of DNA from bacteria to Eukaryotes. mBio 7, e00863-16
plasticity to S. cerevisiae synthetic chromosome XIV defects. Cell Genomics 3, 100379 (2016).
(2023). 362. Marschall, P., Malik, N. & Larin, Z. Transfer of YACs up to 2.3 Mb intact into human cells
328. Rozhoňová, H., Martí-Gómez, C., McCandlish, D. M. & Payne, J. L. Robust genetic codes with polyethylenimine. Gene Ther. 6, 1634–1637 (1999).
enhance protein evolvability. PLoS Biol. 22, e3002594 (2024). This study presents a method for the transfer of extremely large constructs from yeast
329. Pines, G., Winkler, J. D., Pines, A. & Gill, R. T. Refactoring the genetic code for increased to human cells using polycation DNA stabilization.
evolvability. mBio 8, e01654-17 (2017). 363. Mansouri, M. et al. Highly efficient baculovirus-mediated multigene delivery in
330. Carr, P. A. et al. Enhanced multiplex genome engineering through co-operative primary cells. Nat. Commun. 7, 11529 (2016).
oligonucleotide co-selection. Nucleic Acids Res. 40, e132 (2012). 364. Chan, D. Y., Moralli, D., Wheatley, L., Jankowska, J. D. & Monaco, Z. L. Multigene human
331. Simon, A. J., d’Oelsnitz, S. & Ellington, A. D. Synthetic evolution. Nat. Biotechnol. 37, artificial chromosome vector delivery with herpes simplex virus 1 amplicons. Exp. Cell Res.
730–743 (2019). 388, 111840 (2020).
332. Molina, R. S. et al. In vivo hypermutation and continuous evolution. Nat. Rev. Methods 365. Murray, A. W. & Szostak, J. W. Construction of artificial chromosomes in yeast. Nature
Prim. 2, 37 (2022). 305, 189–193 (1983).
333. Tian, R. et al. Establishing a synthetic orthogonal replication system enables accelerated 366. Burke, D. T., Carle, G. F. & Olson, M. V. Cloning of large segments of exogenous
evolution in E. coli. Science 383, 421–426 (2024). DNA into yeast by means of artificial chromosome vectors. Science 236, 806–812
334. Chen, X. D. et al. Helicase-assisted continuous editing for programmable mutagenesis of (1987).
endogenous genomes. Science 386, eadn5876 (2024). 367. Kixmoeller, K., Allu, P. K. & Black, B. E. The centromere comes into focus: from CENP-A
335. Ji, J. & Day, A. Construction of a highly error-prone DNA polymerase for developing nucleosomes to kinetochore connections with the spindle. Open Biol. 10, 200051
organelle mutation systems. Nucleic Acids Res. 48, 11868–11879 (2020). (2020).
336. Luo, Z. et al. Identifying and characterizing SCRaMbLEd synthetic yeast using ReSCuES. 368. Kouprina, N. et al. Human artificial chromosome with regulated centromere: a tool for
Nat. Commun. 9, 1930 (2018). genome and cancer studies. ACS Synth. Biol. 7, 1974–1989 (2018).
337. Liu, W. et al. Rapid pathway prototyping and engineering using in vitro and in vivo 369. Harrington, J. J., Bokkelen, G. V., Mays, R. W., Gustashaw, K. & Willard, H. F. Formation
synthetic genome SCRaMbLE-in methods. Nat. Commun. 9, 1936 (2018). of de novo centromeres and construction of first-generation human artificial
338. Jia, B. et al. Precise control of SCRaMbLE in synthetic haploid and diploid yeast. microchromosomes. Nat. Genet. 15, 345–355 (1997).
Nat. Commun. 9, 1933 (2018). 370. Ikeno, M. et al. Construction of YAC-based mammalian artificial chromosomes.
339. Blount, B. A. et al. Rapid host strain improvement by in vivo rearrangement of a synthetic Nat. Biotechnol. 16, 431–439 (1998).
yeast chromosome. Nat. Commun. 9, 1932 (2018). 371. Logsdon, G. A. et al. Human artificial chromosomes that bypass centromeric DNA.
340. Csörgo, B., Fehér, T., Tímár, E., Blattner, F. R. & Pósfai, G. Low-mutation-rate, Cell 178, 624–639.e19 (2019).
reduced-genome Escherichia coli: an improved host for faithful maintenance of 372. Shao, Y. et al. Creating a functional single-chromosome yeast. Nature 560, 331–335
engineered genetic constructs. Microb. Cell Fact. 11, 11 (2012). (2018).
341. Blazejewski, T., Ho, H. I. & Wang, H. H. Synthetic sequence entanglement augments 373. Dawe, R. K. et al. Synthetic maize centromeres transmit chromosomes across
stability and containment of genetic information in cells. Science 365, 595–598 (2019). generations. Nat. Plants 9, 433–441 (2023).
342. Chlebek, J. L. et al. Prolonging genetic circuit stability through adaptive evolution of This work demonstrates the formation of synthetic centromeres in maize, a key step
overlapping genes. Nucleic Acids Res. 51, 7094–7108 (2023). towards the generation of plant artificial chromosomes.
343. Decrulle, A. L. et al. Engineering gene overlaps to sustain genetic constructs in vivo.
PLoS Comput. Biol. 17, e1009475 (2021). Acknowledgements
344. Moratorio, G. et al. Attenuation of RNA viruses by redirecting their evolution in sequence This work was supported by UK Biotechnology and Biological Sciences Research Council
space. Nat. Microbiol. 2, 17088 (2017). grants BB/M005690/1, BB/P02114X/1 and BB/W014483/1; a Volkswagen Foundation “Life?
345. Williams, R. L. & Murray, R. M. Integrase-mediated differentiation circuits improve Initiative” grant (94 771); an Engineering and Physical Sciences Research Council Fellowship
evolutionary stability of burdensome and toxic functions in E. coli. Nat. Commun. 13, EP/V05967X/1; and a European Research Council Consolidator Award EP/Y024753/1
6822 (2022). to Y.C. J.S.J. was supported by a Manchester-Singapore A*STAR Research Attachment
346. Calles, J., Justice, I., Brinkley, D., Garcia, A. & Endy, D. Fail-safe genetic codes designed to Programme Award. J.D. was supported by the Bureau of International Cooperation, Chinese
intrinsically contain engineered organisms. Nucleic Acids Res. 47, 10439–10451 (2019). Academy of Sciences (172644KYSB20180022), Shenzhen Science and Technology Program
347. Castle, S. D., Grierson, C. S. & Gorochowski, T. E. Towards an engineering theory of (KQTD20180413181837372), Innovation Program of Chinese Academy of Agricultural Science
evolution. Nat. Commun. 12, 3326 (2021). and Shenzhen Outstanding Talents Training Fund.
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 318

---

<!-- Page 22 -->

Review article
Author contributions Publisher’s note Springer Nature remains neutral with regard to jurisdictional claims in
J.S.J. researched the literature. Y.C., J.D. and W.L.C. contributed substantially to discussion of published maps and institutional affiliations.
the content. J.S.J. and Y.C. wrote the article. All authors reviewed and/or edited the manuscript
before submission. Springer Nature or its licensor (e.g. a society or other partner) holds exclusive rights to this
article under a publishing agreement with the author(s) or other rightsholder(s); author
Competing interests self-archiving of the accepted manuscript version of this article is solely governed by the
The authors declare no competing interests. terms of such publishing agreement and applicable law.
Additional information
© Springer Nature Limited 2024
Peer review information Nature Reviews Genetics thanks Pamela Silver, John Glass and the
other, anonymous, reviewer(s) for their contribution to the peer review of this work.
Nature Reviews Genetics | Volume 26 | May 2025 | 298–319 319
