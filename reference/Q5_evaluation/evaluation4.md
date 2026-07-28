<!-- Page 1 -->

nature biotechnology
Review article https://doi.org/10.1038/s41587-024-02127-0
Machine learning for functional
protein design
Received: 1 July 2023 Pascal Notin1,2,5 , Nathan Rollins3,5 , Yarin Gal2, Chris Sander1,4 &
Debora Marks 1,4
Accepted: 5 January 2024
Published online: 15 February 2024
Recent breakthroughs in AI coupled with the rapid accumulation of protein
Check for updates
sequence and structure data have radically transformed computational
protein design. New methods promise to escape the constraints of natural
and laboratory evolution, accelerating the generation of proteins for
applications in biotechnology and medicine. To make sense of the exploding
diversity of machine learning approaches, we introduce a unifying
framework that classifies models on the basis of their use of three core
data modalities: sequences, structures and functional labels. We discuss
the new capabilities and outstanding challenges for the practical design of
enzymes, antibodies, vaccines, nanomachines and more. We then highlight
trends shaping the future of this field, from large-scale assays to more robust
benchmarks, multimodal foundation models, enhanced sampling strategies
and laboratory automation.
Proteins fulfill a wide range of functions in nature, with that functional Machine learning methods have recently emerged as another
diversity encoded in their amino acid sequences. The goal of protein strategy to efficiently explore the functional protein space, given
design is to create new proteins by discovering sequences with func- their ability to learn complex distributions that model fitness land-
tions that enhance or extend beyond those of existing proteins—an aim scapes from data. This ability typically increases with the quantity
with the potential to address globally pressing problems in healthcare, and quality of data available for training, as well as the aptness of the
agriculture and sustainability. However, the potential design space is underlying algorithms to learn from these data via the right induc-
massive and sparsely functional: there are more unique sequences of tive biases—that is, the set of assumptions or constraints encoded in
100 amino acids than the number of atoms in the universe, and only a the model architecture. The massive progress in DNA sequencing over
small fraction of these has desired functions in the context of interest the past two decades, combined with improvements in the experimen-
(for example, organism, temperature, pH). The quantitative map of the tal determination of protein structure and properties, has provided the
representations of proteins to their functions is referred to as a ‘fitness required foundational data for machine learning for protein design to
landscape’. Given the impossibility to exhaustively list all possible amino be successful (Box 1). In parallel, algorithmic and computing advances
acid combinations, let alone quantify their properties experimentally have led to an increasing capacity to model distributions over these
or computationally in different contexts, one of the first challenges that various data inputs, leading to a broad collection of performant protein
protein design is faced with is narrowing the search within the fitness design models achieving diverse objectives (Box 2).
landscape to a tractable space. A multitude of strategies have been While in practice it may be effective to combine several design
developed to address this challenge: from rational design methods that strategies (for example, generate initial designs with a machine learn-
select the most promising mutants on the basis of a deep understanding ing model and then optimize with a biophysical method), we focus
of a given protein structure and function, to experimental methods test- here on machine learning-based design methods. After providing an
ing a broader range of variants (for example, directed evolution, com- overview of the breadth of tasks in protein design, we review the funda-
binatorial libraries), to biophysics-based models of protein structure, mental modeling approaches involved and discuss their practical appli-
folding and interactions—a staple of computational design. cations, successes and limitations. Given the rapid pace of progress
1Department of Systems Biology, Harvard Medical School, Boston, MA, USA. 2Department of Computer Science, University of Oxford, Oxford, UK.
3Seismic Therapeutic, Cambridge, MA, USA. 4Broad Institute of Harvard and MIT, Cambridge, MA, USA. 5These authors contributed equally: Pascal Notin,
Nathan Rollins. e-mail: pascal_notin@hms.harvard.edu; nrollins.home@gmail.com; debbie@hms.harvard.edu
Nature Biotechnology | Volume 42 | February 2024 | 216–228 216

---

<!-- Page 2 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
from a sequence-based model2,3 or a sequence–structure model1,4.
Box 1 Sequence-based models stand out for their ability to accurately predict
effects of mutations on diverse evolutionary phenotypes (binding,
stability, enzymatic function and more)12–18 and to produce designs
The three core modalities of
achieving the mixture of phenotypes key to function2,3,19–21, owing to the
machine learning for functional depth of sequence data available for many protein families. Sequence–
structure models such as inverse folding models can generate highly
protein design stable protein sequences1,4,22,23. However, they have so far relied on pro-
tein family sequence profiles and simulated residue-interaction fields
to account for constraints on functions such as enzymatic activity22,23.
Protein design models are trained on a combination of sequences, Circumstantially, when sufficient mutation–phenotype data exist for
structures, and functional labels. Each modality has unique virtues the property of interest, sequence–label models can also prove useful
and caveats, depending on the abundance of data, the need for to guide design, for example, for intended function24,25, stability26–28 or
human knowledge and intervention, and the proximity of data immune epitope5–11 prediction.
examples to the desired function.
Redesign for a new function
The objective here is to design a protein with a new function by working
Sequences
• Billions of publicly available sequences encode from an existing protein with a related function (for example, shifting
...PNYCD...
evolutionary constraints, encompassing the a binder or enzyme to act on a new target29,30). This requires either a
...PNACE... diversity of protein families and mitigating the
need to generate data in the lab. detailed understanding of the mechanism of function or ample data
• Models of evolved sequences can optimize for relating sequence to the new function. Consequently, most approaches
functions that are selected for during evolution.
have relied on sequence–label models. These data can be obtained
by selecting sequences according to the reaction of interest via
Structures measured phenotypes of natural proteins31, deep mutational scans25,
• Thousands of publicly available structures
provide 3D detail of the biochemical interactions next-generation sequencing of library selection32 or directed evolu-
that underpin protein folding and function. tion experiments29,30,33–35. Sequence-based models can also be used
• Models of sequences and structures can
optimize for custom folds, active sites, and to generate libraries of ‘new family members’ to pan for secondary
binding complexes, but often require expert properties3,19–21,36–38 (for example, enzyme functionality within Escheri-
knowledge of key residues and interactions.
chia coli36, viral gene delivery to a tissue37 or antibody binding affinity
to a target14,39,40). This panning may cost more than screening a small
Functional labels
label-driven library when sufficient labels exist for training, but can
• Lab-generated functional labels explore new
binding targets, reactions and biochemical reduce costs (for example, necessary iterations and scale of selection)
conditions. Applicable datasets are often sparse
compared to random libraries by enriching for sequences with good
and bespoke, but the ability to generate larger
and more generalizable libraries is increasing. intrinsic properties and high diversity14,37. Sequence–structure mod-
• Models of sequences and labels can optimize els can also be leveraged for this objective, for instance, to redesign a
for new functions or for existing functions in
new conditions. region of a protein to achieve a new binding interaction or to insert an
active site, as has been achieved repeatedly with non-machine learning
methods41–43. However, application of sequence–structure models has
so far leaned toward de novo objectives, and, even when templating
in this field, our emphasis is on teasing out the overarching principles from existing proteins, the templates have often been abstracted to
that characterize all methods, rather than focusing on the details of fragments and topology constraints44.
the current top-performing models that are sure to be outperformed
in the near future. We conclude by providing a vision for the field of De novo design
protein engineering as different threads of research are converging. Machine learning-based design of sequences with de novo folds
focuses on sequence–structure models. These methods can gener-
Objectives of machine learning for functional ate sequences with diverse 3D folds and multimer arrangements with a
protein design high success rate of stable expression22,23,45–47. The motivation to design
The design objectives supported by machine learning can be broadly sequences based on 3D structure results from the critical role of struc-
classified into three groups, depending on whether we start from a ture in our understanding of protein function. The 3D structure of a
known protein or from scratch and, for known proteins, whether we protein enables us to make assertions about physicochemical interac-
enhance its existing function or create a new function (Fig. 1). We review tions and is a convenient representation for inferring or specifying
these different strategies and connect them with the machine learning constraints on function. De novo design requires function constraints
approaches discussed in Box 2. on sequence and structure, often derived from other existing pro-
teins, such as metal-binding sites and fragments of protein–protein
Redesign to enhance an existing function complexes23,48. Excitingly, it is becoming possible to design a de novo
The goal of protein enhancement is to start from a protein (natural or protein on the basis of the target structure alone for both protein–
otherwise) that already possesses the desired function and introduce protein binding43,48,49 and small-molecule binding44,49,50. Recently,
mutations to improve its properties or achieve the original biologi- luciferase enzymatic activity has been achieved by a de novo protein,
cal function in different conditions. The aim could be to enhance the with model-generated 3D structure and sequence, albeit templated
main function of the protein (for example, catalytic activity, bind- on an existing family of small-molecule-binding proteins44. Although
ing affinity to a specific target), to enhance another of its attributes some applications require thousands of designs to be assayed, the
(for example, thermostability1–4) or to mitigate undesirable interactions capabilities of de novo design are growing rapidly. Lastly, it is possible
with other molecules, such as reducing the immunogenicity of thera- to use sequence-based models to generate new proteins not explicitly
peutic proteins by altering epitopes5–11. One way to enhance intrinsic templated on an existing protein and even with predicted folds unique
properties such as stability is to sample high-probability sequences from those in the PDB51,52. However, to achieve a new desired function
Nature Biotechnology | Volume 42 | February 2024 | 216–228 217

---

<!-- Page 3 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
Box 2
Types of machine learning models for protein design
The majority of machine learning models for protein design can be increasingly, embeddings extracted from sequence-based models,
broadly categorized into three groups, based on the way proteins giving rise to label-efficient semi-supervised architectures. The
are represented, the data used for training and the probability that trained regressor is usually lightweight to avoid overfitting, for
the underlying algorithm seeks to learn (Fig. 3). We use a unifying example, a ridge regression, Gaussian process, shallow CNN or
probabilistic framework to facilitate comparisons between the dense network159,185–187. Discriminative models provide an efficient
different methods in this section and in Fig. 3. While certain models way to predict phenotypical values for a large list of potential
do not explicitly learn a distribution, one can always cast the designs and prioritize the most promising candidates. However,
corresponding tasks as implicitly modeling a distribution, adopting a the quality of these candidates directly depends on the quality
Bayesian viewpoint. of the external procedure (for example, combinatorial libraries,
sampling with a separate unsupervised model) that was used to
Sequence-based models. This model class can be split into two craft the initial list of prioritized mutants to assess. Conversely,
distinct groups. The first group, sequence-only models, learns label-conditioned generative models, such as conditional variational
a generative model P(x) of the primary structure x of a given autoencoders (VAEs)29, guided diffusion188, Regression Transformer154
protein. By training on a large collection of protein sequences, or ProteinNPT155, learn an approximation of the joint probability P(x,y)
they aim to implicitly capture the biochemical constraints that or the conditional probability P(x|y) for a sequence x and functional
characterize the proteins present in the training set. Models in label y. They enable the generation of new sequences conditioned
that category were classically ‘family-specific’ alignment-based on a desired phenotypical value, leading to potentially more effective
models and trained on a set of homologous sequences contained end-to-end procedures. Lastly, while the majority of supervised
in a multiple-sequence alignment. While initial alignment-based models have relied on representations of the primary structure
models focused on position-specific predictions independent (one dimensional) of proteins of interest, some architectures are
from other sequence residues (for example, position-specific instead based on their tertiary 3D structure34,189 and would be more
scoring matrices), subsequent models considered pairs of adequately characterized as structure–label models.
residues12,174 and, more recently, were generative models of the full
sequence13,14,16,38. Building on the intuition that certain amino acid Structure-based models. There are four main categories of
constraints or patterns may generalize across protein families, structure-based models that may be used for protein design.
‘family-agnostic’ protein language models—trained on unaligned Structure prediction models143,146,190,191 seek to predict the tertiary
sequences across protein families—then emerged as a practical structure z of a protein on the basis of its primary structure x. Structure
alternative covering all proteins with a single model. This has led generation models, based on generative adversarial networks192,
to a wide diversity of models, inspired by learning paradigms VAEs96 or, more recently, diffusion models23,77,193, are trained to
initially introduced in the natural language-processing literature, directly learn the probability P(z). Inverse folding models22,62,107,194,195
such as autoregressive modeling20,52,61,141, masked-language learn the probability P(x|z) of a protein sequence x, conditioned on
modeling15,146,175,176 or seq2seq architectures177,178. However, without a 3D structure z, where the structure is typically encoded with a
relying more explicitly on homology (for example, via fine-tuning graph neural network196–199. Lastly, holistic design approaches, such
on alignments15), family-agnostic models have not been able to as protein hallucination45,48,200, inpainting48 or ProteinGenerator100,
match the fitness-prediction abilities of the best family-specific learn to model the joint probability P(x,z) of the sequence x and
model18,136,137,144,169. This observation subsequently gave rise to a structure z. In the text, we often refer to sequence–structure
multitude of hybrid models that sought to combine the relative models, which encompass both inverse folding as well as the
strengths of each approach144,145,179,180. Recently, diffusion models joint sequence and structure models. To eventually produce new
of single-sequence or MSA inputs have also been proposed as a sequence designs, structure generation models must be paired
promising avenue for learning the process to generate full protein with these sequence–structure models. In that case, the combined
sequences from scratch181. The second group, conditional sequence architecture can itself be seen as a joint model of sequence and
models, further condition the generative process P(x|t) on broad structure since, using the chain rules for probabilities, P(x,z) = P(x|z)P(z).
taxonomic groups or gene ontology annotations t to provide more
control over the nature and properties of generated sequences. Choosing a model architecture. The main drivers in the selection
Several architectures have been proposed based on autoregressive of a particular model are the desired design objective (as discussed
modeling20,153 or masked-language modeling182. in Objectives of machine learning for functional protein design)
and available data to support that goal (for example, a sufficiently
Sequence–label models. When a sufficiently large number large number of labels to train sequence–label models). Another
of labels for the property of interest are available, it becomes consideration is how the model will be effectively used in practice.
possible to train discriminative supervised models learning a Generative models, whether they are sequence or structure based,
distribution P(y|x) of a functional label y for a given input sequence provide a way to sample new proteins that resemble the data
x. Functional labels are typically measurements collected in the they have been trained on. A sound sampling process producing
laboratory via massively parallel sequencing of directed evolution natural-like proteins coupled with a robust experimental pipeline
campaigns29,30,35,40, mutation libraries25,27,37,89,183,184, nature sourced to measure the actual properties of generated objects is key.
(for example, antibody repertoires32, chimeric libraries34), or partial Additional controls (for example, taxonomic labels20, enzyme
measurements that supplement natural sequence data24,31. The classification153) with which we can condition the sampling
sequence representation can be either a simple one-hot encoding, process may help in increasing the usefulness of each sample.
physicochemical properties and other handcrafted features or, Alternatively, sequence–label architectures provide diverse ways
Nature Biotechnology | Volume 42 | February 2024 | 216–228 218

---

<!-- Page 4 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
(continued from previous page)
to prioritize a subset of variants for subsequent experimental of interest is differentiable (for example, when jointly training
validation. For instance, if the model outputs both predictions a regressor with a VAE201–203 or in guided diffusion188), one can
along with the corresponding uncertainty (for example, Gaussian instead use gradient ascent. Lastly, as long as enough labels
process, Bayesian neural network), one can frame the iterative are available to train them, supervised generative models154,155
design approach under a batch Bayesian optimization framework. provide finer-grained control over the sampling process than their
If the function mapping the protein representation to the property unsupervised counterparts.
Yes Existing protein? No
Existing target function?
Yes No
Redesign to enhance an Redesign for a
De novo design
existing function new function
Spectrum of existing
sequence–function
More Less
information
Sequence-based models
Sequence–label models
Structure-based models
Fig. 1 | Protein design objectives. The various protein design objectives can task. When selecting a design method, one can decide to ignore the existence
be placed into three groups based on how far the design target is from existing of relevant functional proteins in nature. For instance, even if a known protein
functional proteins. For each group, different model classes may be more already carries out the desired function, de novo design methods can be used to
appropriate depending on available sequence–function information. The size delve into regions of sequence space not previously explored by evolution but
of the circle indicates how suited a given approach is to a particular design yielding the same function.
in the absence of a template protein, it is foreseeably more practical to practical importance: enzymes and antibodies. We then cover other
incorporate structural constraints, for instance, via hybrid models46. applications, such as improving therapeutic properties and designing
protein machines (Fig. 2). With each example, we concisely describe the
Redesign versus de novo design machine learning model applied, focusing particularly on the nature
The common distinction in protein design between redesign of the training data (sequence, structure and functional labels) and
(creating new sequences based on existing proteins) and de novo design the training paradigm used (generative or discriminative, supervised
(creating new sequences based on new folds) is more nuanced than the or unsupervised) (Fig. 3).
dichotomy implies. It is more accurately represented as a spectrum of
strategies (Fig. 1), all of which leverage function from natural sequence Applications to enzyme design
and structural elements to varying degrees. Even de novo designs, Improving thermostability
despite their seemingly new sequence or overall structure, are prod- Increasing stability promotes other goals such as improving yield,
ucts of training data from natural sequences and structures and often preventing inactivity and toxicity due to aggregation and operating
incorporate functional motifs from existing proteins. Therefore, when enzymes at optimal but challenging temperature and solvent condi-
faced with a new protein design challenge, the initial question should tions (for example, denaturation due to low pH). Enhancing the stabil-
be: what existing protein with similar function can I use as a template? ity of constructs entering directed evolution may also improve the
The extent of the match between the function ask and the template chances of success by supporting otherwise unstable variants with the
protein then determines the sources of data and the model strategy desired target function53–55. Conventional non-machine learning-based
that are best suited to the task. approaches typically find stabilizing mutations by assaying libraries
of single substitutions56,57 or chimeric combinations of natural protein
Protein design applications fragments26,58, often iterating via directed evolution59,60. When mutant
Machine learning methods have been applied to create new functional combinations such as chimeras are assayed, sequence–label models
designs for a wide range of protein families. This section first focuses can be used to identify the key mutations leading to increased stability
on their applications for the design of two protein types with high across multiple designs26,61. Sequence-based and sequence–structure
Nature Biotechnology | Volume 42 | February 2024 | 216–228 219

---

<!-- Page 5 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
Enzymes Antibodies Others
Redesigned,
more stable
PETase
Fold-
changing
Efficient Redesigned switches
nanobody CDRs that
libraries for bind an existing
binder panning target
Multicomponent
assemblies,
e.g., nanopores
‘De novo’
luciferase De novo CDRs
templated that bind
on NTF2 a new target
Epitope-presenting De novo
scaffolds protein binders
Redesign to enhance • Enhancing enzyme activity • Improving binding affinity to target • Avoiding human immune reaction
existing function • Improving stability at high • Maintaining affinity while optimizing • Avoiding chemical modification or
temperature or pH viscosity, solubility and immunogenicity protease digestion
Redesign for a new • Altering substrate or product specificity • Decreasing antibody polyreactivity • Designing allosteric and switchable
function function
• Designing a new scaffold, given a • Designing new antibody CDRs • Designing a de novo binder, given a target
De novo design catalytic motif from scratch, given a target
• Scaffold/adjoin functional elements
Fig. 2 | Protein design applications. Examples of machine learning-driven protein design applications for different protein types across the three protein design
objective categories. NTF2, nuclear transport factor 2.
models have been surprisingly successful at designing proteins with To reduce the number of mutation–selection rounds required, recent
enhanced stability without the need for labels1–4,22 to circumvent costly directed evolution efforts have replaced random mutagenesis at each
preliminary assays. Although these models do not explicitly predict step with library design by sequence–label models updated at each
folding ΔG or melting temperature, the sequence or structure like- round with the new data29,30,33,35,71,72.
lihoods output by these generative models trained on natural pro- In a standout example, Schmitt et al. trained a sequence–label
teins correlate strongly with stability12–14,62, enabling success even in conditional variational autoencoder (VAE) model on extensive directed
small-scale experiments. For example, sequence–structure models evolution data: 89 Cre-recombinase libraries evolved against different
were used to design polyethylene terephthalate hydrolase (PETase) DNA targets, amounting to >2 million protein–DNA sequence pairs29.
variants (one to four mutations)1 and myoglobin variants (mutating The resulting model was then able to generate new protein sequences
~50% of the sequence, avoiding 17 amino acids at the heme-binding conditioned on custom-input DNA sequence, thereby circumventing
site)4 with enhanced stability, assaying only ~20 designs for each. The the need for additional directed evolution campaigns tailored to the
key challenge is to maintain the original function while making sta- new targets. It was used in particular to design a single protein sequence
bilizing mutations, often by avoiding mutations to existing amino for each of ten new DNA targets not cleaved by the original libraries.
acids that are essential for function. This was explored by Sumida Remarkably, four of ten designs showed successful excision at these
et al.4, who tested 144 redesigned tobacco etch virus (TEV) protease new targets.
sequences and found that most designs conserving over 50% of the
original sequence sustained or enhanced activity, whereas designs Design a new scaffold, given a functional motif
with less than 50% retention exhibited loss of activity. Looking for- The ability to embed small functional motifs in new scaffolds enables
ward, new high-throughput stability assays such as those by the Rocklin a more modular design of functional components (for example, to
group (about 800,00 high-quality measurements for over 450 protein fuse multiple properties). One approach is to combine a compatible
domains)63 may provide the basis to train supervised models27,64 for structure with a structural arrangement of residues that enable binding
thermostability design that generalizes across protein families, with or reaction. For example, existing protein domains that already bind or
the aim to exceed fully unsupervised methods while still circumventing react with some molecule have had active sites replaced to perform new
project-specific data generation. reactions42,43,73. Proteins with entirely unrelated function have also been
functionalized by this approach. For example, Holst et al. converted
Altering specificity or activity an armadillo repeat protein into a new polycarbonate hydrolase by
Inspired by the fact that natural proteins often evolve multiple unique just four mutations41. Likewise, force-field methods have been used
functions originating from the same family and fold65–67 or are pro- to design a number of new structures that contain protein-binding
miscuous to alternative substrates or reactions68, a common design motifs, epitopes and fluorophore sites49,74,75. To find plausible 3D
strategy is to alter existing proteins. Enzymes can even be modified folds among the huge space of possibilities, conventional de novo
to catalyze reactions not yet found in nature42,69,70. Design of enzymes methods narrow the space to well-defined topologies with favorable
with the new chemistries has long relied on directed evolution69,70 or folding interactions. The scope of these approaches may be poised to
approaches replacing enzyme active sites by structure comparison42,43. expand thanks to new methods that propose molecular interactions
Nature Biotechnology | Volume 42 | February 2024 | 216–228 220

---

<!-- Page 6 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
Sequence-based models Sequence–label models Structure-based models
Sequence-only models Discriminative models Structure Structure
P(x) P(y|x) prediction models generation models
P(z|x) P(z)
Ø
Alignment-based models: PSSM, HMM,
DCA, DeepSequence, EVE, WaveNet • Ridge regression
• Boosting and bagging trees • AlphaFold2
Protein language models • Shallow MLP/CNN • RoseTTAFold • Ig-VAE
• AR: UniRep, RITA, ProtGPT2 • Lightweight attention • ESMFold • Chroma
• MLM: ESM-1v, ESM-2, CARP • Gaussian process • OmegaFold • RFdiffusion
• Seq2seq: ProtT5, Ankh
• Diffusion: EvoDiff
Hybrid models: Tranception,
TranceptEVE, MSA Transformer, PoET Generative models Inverse folding models Joint sequence +
P(x, y) or P(x|y) P(x|y) structure models
Conditional sequence models P(x, z)
P(x|t) or P(x,t)
• Conditional VAEs • ProteinMPNN • Hallucination
Autoregressive: ProGen, ZymCTRL • • G Re u g id re e s d s i d o i n ff u T s r i a o n n sformer • • E P S iF M ol - d IF1 • • I P n r p o a te in in ti G n e g nerator
MLM: ProteinBERT • ProteinNPT
Sequence (x) Taxonomic group (t) Functional label (y) Structure (z)
Fig. 3 | Typology of protein design models. The majority of machine learning distributions that these approaches seek to model for predictive and generative
methods for protein design can be broadly categorized into three groups purposes. AR, autoregressive; MLM, masked language model; MLP, multilayer
depending on the data modalities used to train them and the underlying perceptron.
and identify compatible scaffolds (RifGen, RifDock)76. Additionally, by training on deep mutational scan labels. It simultaneously lead to
scaffold compatibility may be improved by using sequence–structure marginal improvement of trastuzumab’s affinity for HER2 while also
transformer models to generate modified structures. These meth- considering viscosity, solubility and immunogenicity89. In an appli-
ods have already been applied to create new scaffolds for a luciferase cation that supports cross-target binding, Liu et al. trained multiple
functional site by templating on an existing small-molecule-binding discriminative sequence–label CNN-based models on phage-display
family44 and to customize de novo folds to accommodate functional data for several binding targets, each target being a separate antibody.
motifs23,45,46,48,77–79. The resulting models were used in combination to predict sequences
cross-reactive to all targets by binding the Fc40. Lastly, Makowski et al.
Applications to antibody design improved binding to the kinase c-MET by training a discriminative
The role of machine learning in antibody design sequence–label model on a mutational scan of emibetuzumab90.
Antibodies are omnipresent in biomedicine owing to their remarkable Despite these successes, an important shortcoming of these various
specificity and affinity for biomolecules. Previously, obtaining an anti- methods is that they are usually antibody specific. Their application to
body specific to a therapeutic or scientific target of interest required other antibodies would require the collection of new, project-specific
animal inoculation to exploit the natural process of affinity maturation experimental data, limiting their broader utility.
by somatic hypermutation80,81. More recently, antibody-discovery cam- Three notable strategies have been able to generalize to new anti-
paigns have shifted toward large-affinity screens such as yeast82–84 and bodies and antigens without project-specific sequencing data. First,
phage display85,86. Yet, these campaigns remain costly and with a low Harvey et al. developed a sequence–label model to reduce polyspecific-
guarantee of success. Machine learning-driven antibody design prom- ity in antibody and nanobody complementarity-determining regions
ises to decrease these costs and increase success rate. While we would (CDRs)32. The model was trained on deep sequencing of selection
like to design a specific antibody directly, computational approaches experiments for high and low polyreactivity in a naive nanobody library.
are currently limited to accelerating certain well-defined steps along More than 85% of predicted mutations reduced polyreactivity in three
the end-to-end discovery process, such as improving the likelihood of nanobodies. For an anti-angiotensin II type 1 receptor (AT1R) antibody,
successful clones, reducing the need for rounds of affinity maturation, 3 of 13 predicted mutations decreased polyreactivity by up to 80% while
optimization of specificity, reducing polyreactivity or determining the retaining AT1R binding. This suggests that it is possible to reduce the
3D structure of the antibody–target complex. polyspecificity of nanobodies while retaining on-target binding, with-
out antigen-specific data. Second, Hie et al. leveraged a sequence-only
Enhance features of existing antibodies protein language model, ESM-1v, to introduce mutations that improve
The majority of machine learning models used to improve exist- the affinities of seven known antibodies39. Here, rather than being
ing antibodies rely on deep sequencing from rounds of selection or trained on antigen selection data specific to the problem at hand, it
deep mutational scans for training data. For instance, Parkinson et al. was instead trained on a large set of protein sequences from diverse
developed a sequence–label model to predict yeast display affinities families. It was then used to recommend up to 14 single mutations
on the basis of sequence embeddings pretrained on native antibody to be screened for binding affinity. Mutants that increased affinity
sequences. The model was then used to optimize atezolizumab for were combined in a second round, resulting in an affinity increase
binding to programmed cell death ligand 1 (PD-L1)87. Similarly, Saka up to 160-fold over that of unmatured antibodies. This implies that
et al. trained a sequence-only long short-term memory (LSTM) model generalizable machine learning models can help reduce library size
on sequences from phage-display selection to optimize an antibody and the number of rounds needed to optimize existing antibodies
specific to kynurenine88. In another instance, Mason et al. developed without modeling the antigen or training on antigen-specific sequenc-
a discriminative sequence–label convolutional neural network (CNN) ing data. Third, sequence–structure models were used to recommend
Nature Biotechnology | Volume 42 | February 2024 | 216–228 221

---

<!-- Page 7 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
mutations to an existing antibody sequence, given the 3D structure of or increasing successful design rates. For instance, Shanehsazzadeh
the bound antibody–target complex as input91,92. In one example, the et al.97 generated new heavy-chain CDRs with a model conditioned on
ESM-IF1 model62 was used to redesign Ly-1404 and SA58, antibodies for an existing antibody–antigen structure (trastuzumab–human HER2)
severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2)91. With and using framework and light-chain CDR sequences from a known
testing of only ~30 designs for each starting point, the top designs had antibody (trastuzumab). The approach led to binding rates higher than
seven and two mutations, and affinity enhanced 26-fold and 11-fold, those generated by randomly sampling heavy-chain CDRs from existing
respectively. The model also showed standout ability to predict the antibody repertoires. However, the greater practical challenge will be to
affinity of combinatorial variants of antibodies specific for influenza demonstrate successful designs in cases in which an effective antibody
hemagglutinin. While this inverse folding strategy is restricted to the is not already known and therefore the antibody-binding interface, the
redesign of antibodies with sufficiently high affinity to obtain 3D struc- framework and any CDR sequences are not known. Given the recent
tures in complex with target, it may enable de novo antibody design success in de novo design of protein folds that bind a target23,98, a break-
in the future if paired with powerful predictive models proposing new through in de novo antibody design could be near. This might neces-
antibody–antigen 3D complexes. sitate innovations such as antibody-specific training, simultaneous
sequence and structure optimization99,100 or more detailed structure
Accelerating affinity campaigns by using smart libraries modeling like atomistic modeling101,102.
One strategy to increase the odds of finding successful antibodies
is to design intelligent starting libraries that are enriched for func- Other applications
tional antibodies. Although billions of known antibody sequences Avoiding human immune reaction
are currently available (for example, the Observed Antibody Space When proteins are injected as therapeutics, they are often thwarted by
database93), they only represent a small fraction of the pan-human anti-drug antibodies (ADAs) that can neutralize therapeutic activity and
repertoire and we expect to see this number substantially increase as even lead to toxicity103. To be safe and effective, a protein therapeutic
new sequencing methods become available. Furthermore, because the must avoid binding by existing ADAs at antibody-binding sites (also
cost of synthesis lags far behind the cost of sequencing, the potential called B cell epitopes) and avoid eliciting new ADAs by T cell epitopes.
to design custom libraries is still constrained. Consequently, various Existing antibodies can be avoided by eliminating B cell epitopes
computational strategies have been developed to approximate the on the protein surface. Strategies include coating the surface with
functional antibody sequence space. A simple approach is to generate glycans or polymers or ‘resurfacing’ the protein by mutation so that
variations that mimic residue preferences in the CDRs of single-domain the existing antibodies are no longer compatible104,105. For exam-
antibodies from solved 3D structures. This method has successfully dis- ple, Bootwala et al.106 leveraged an inverse folding model107 to gen-
covered specific nanobodies for two distinct human G protein-coupled erate sequences based on l-asparaginase while mutating only the
receptors84 and the SARS-CoV-2 receptor-binding domain83. An alterna- protein surface. The standout design introduced 40 mutations and
tive strategy is to design smaller libraries that can be precisely synthe- reduced human ADA binding by 50%, although at the expense of a 50%
sized. For instance, SeqDesign82, a sequence-only CNN model trained decrease in both expression and enzymatic activity. With knowledge
on 12 million publicly available nanobody sequences, generated a of antibody-binding hotspots or with approximate antibody-binding
diverse library of approximately 185,000 sequences with unique CDR3 probabilities108, it may be possible to use hotspot-focused resurfacing
regions and both CDR1 and CDR2 identical to those of the germline. to achieve similar ADA-binding reduction with fewer mutations and
This library led to improved expression in yeast, and, despite being mitigate chances of reduced function.
1,000× smaller than typical yeast nanobody campaigns81, contained Newly elicited antibodies can be reduced by eliminating T cell
low- to moderate-affinity antibodies specific to human serum albu- epitopes throughout the linear sequence of a protein by removing the
min84 and green fluorescent protein83. Looking ahead, recently pro- major histocompatibility complex II (MHC-II) display of T cell epitopes
posed computational strategies such as variational synthesis94 may or by suppressing T cell receptor complementation. Thus far, protein
be used to optimize larger library design. design to reduce T cell immunogenicity has focused on eliminating
MHC-II display104–108. This has been partly due to strong capabilities
Design a monobody from scratch, given a target in measuring and predicting MHC-II display109–113, while the reliabil-
The closest example to date of machine learning-driven de novo anti- ity of models to predict T cell receptor complementation remains
body design is the engineering of a single fibronectin 3 (Fn3) domain uncertain114. MHC-II-binding sequence–label models have been paired
(in imitation of the immunoglobulin G fold) targeting a conserved with sequence-only models to identify mutations predicted to both
epitope on α-elapitoxin95. First, 1.6 million Fn3 domains were gener- remove epitopes and retain function8. Unlike prior epitope-removal
ated via molecular dynamics simulations on 442 known natural Fn3 approaches that caused function loss5–7, these approaches left function
domain structures and used to train a structure generation model intact74. Similar efforts geared toward MHC-I receptor display, to avoid
(similar to Ig-VAE96) to then efficiently sample new conformations. the killer T cell response, will be important for proteins introduced by
Second, the sampled synthetic structures were docked onto the tar- gene delivery.
get using a statistical potential based on residue interactions in the
PDB. Lastly, specific sequences were generated using a sequence– Design a binder, given a target
structure CNN model and further optimized with Rosetta. Roughly A major goal of protein design, with massive foreseeable impact in
6,000 sequences generated by the method were experimentally science and medicine, is to produce protein binders for any target,
screened for binding to five toxins, each of which conserved the without the need for intensive panning experiments or for an existing
target epitope, resulting in one design found to bind three of five known binder. While there have been breakthroughs in force-field
toxins. Although the affinity was not reported and a random or design given a target alone, these have typically required thousands
target-independent library was not screened for comparison, the of constructs to be assayed76. In contrast, recent progress in machine
corresponding hit rate is much higher than for naive antibody rep- learning approaches has enabled instances of protein binder design
ertoires or random yeast-display libraries, which typically screen requiring fewer than 100 constructs to be assayed23. For instance, in a
several millions of unique sequences to find hits. recent two-stage approach, a structure generation model, such as RFdif-
For de novo antibody design to be practical, it must substan- fusion22, produces 3D backbones complementary to the structures of
tially decrease the effort needed for screening by reducing necessary protein targets, which are input to an inverse folding model, such as
throughput, enabling parallelization, decreasing selection rounds ProteinMPNN22,74,110, to generate sequences. While this two-step process
Nature Biotechnology | Volume 42 | February 2024 | 216–228 222

---

<!-- Page 8 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
consisting of structure sampling and sequence design is similar to pro- proteins2,3,19–21,36–38. A direct comparison of the design abilities of dif-
tein design with Rosetta, it has been able to generate greater breadth ferent model architectures has nonetheless been difficult due to their
of structures with much fewer iterations. When applied to design bind- application to substantially different protein families. While primarily
ers for four protein targets, the approach showed an overall success focused on low mutational depth, benchmarks based on large collec-
rate of 18%, eclipsing the performance of prior target-only de novo tions of mutational scan assays such as ProteinGym18 or FLIP159 enable
binder design22,76,115, potentially due to better shape complementarity thorough baseline comparisons in various design settings and will
of backbones generated by RFdiffusion, in contrast to the formulaic help guide future model-development efforts. However, an increased
topologies used by non-machine learning methods76. Recently, these accuracy in mutation effect prediction may not necessarily translate
methods enabled a similar breakthrough in the design of DNA-specific into increased design accuracy—that is, a superior ability to generate
binding proteins116. Although there are limitations to current diffusion sequences with the desired functions. While various in silico metrics
methods, we expect the increased ability to design customized protein have emerged as means of comparison between structure-based mod-
folds, incorporating interfaces and functional motifs, will substantially els, such as recovery of native sequences from existing structures22,107
enhance the practicality of protein design. or recovery of target structure from designed sequences by AlphaFold
prediction22,23,45,48,115, these are not unbiased measures of protein design
Vaccines, machines and more success. Regarding sequence recall, a model with enough capacity
The aforementioned examples represent some of the most common could easily memorize training sequences and, if prompted appro-
protein design applications, but there are many more: vaccines protec- priately, may perform extremely well on that metric without neces-
tive against future virus evolution117, vaccine scaffolds that efficiently sarily being able to extrapolate to new sequences. Regarding structure
present immunogens to immune cells118–122, anti-viral drugs designed to recall, AlphaFold may serve as a coarse proxy115, but it is known to fail at
bind and inhibit viral proteins123–127, switches and sensors that activate discerning stability at the level of individual mutations160,161. Although
a biological pathway in response to target molecules128–133, axles that AlphaFold can successfully predict the fold of many de novo proteins
perform nanoscale rotation134 and nanopores for DNA and protein designed by methods built on natural protein information, it may fail to
sequencing or detection135–139. generalize to designs that lack sequence and structure features known
Presently, innovation in protein design relies on both the exist- to nature. More comprehensive evaluation frameworks are emerging162
ing functions of natural proteins and the customizability of de novo and may help to further optimize designs in silico and focus in vitro
design. Taking nanopore sequencing for example, one can rationally efforts on higher-quality candidates.
specify dimensions of the pore47,137,140 to achieve electrical resistance
unique to each nucleotide or amino acid that passes through, but strate- Experimental evaluation
gies to thread proteins through pores still take advantage of existing The field still lacks unbiased experimental benchmarks that capture
unfolding machinery from nature136. Advances in design methods that practical design tasks, such as ‘given a protein or small-molecule tar-
further blur the lines between ‘find and modify a component to do X’ get, design a binder’ or ‘given a reaction, design an enzyme’. To avoid
and ‘create a component to do X’ are the inflection points to watch out conflating ‘natural protein recall’ with design capability, the chosen
for as this field evolves. targets must be ‘new to nature’, searching for binding or reactions
not known in natural examples. The Institute for Protein Design has
Future directions created some initial benchmark tasks22,23,48,76 for target protein binding
Data and model scaling and functional motif scaffolding, although these have yet to address
Preliminary analyses of the scaling laws of protein language models141 natural protein recall. As most real-life design use cases involve the
have highlighted the benefits of scaling model size and, perhaps, simultaneous optimization of multiple properties163, experimental
hinted at some of its limits51. If trends observed in natural language benchmarks should also probe this capability, for instance, via tasks
processing142 hold for proteins, leveraging larger datasets of protein such as ‘given a protein, increase its stability while retaining activity’ or
sequences during training will yield improved generative models and, ‘given a protein, alter its function while maintaining stability’.
in turn, increase design quality. Similarly, the performance of protein
models, whether for structure prediction143 or fitness prediction144, Toward a unified approach to protein design
explicitly leveraging homology145 or with single-sequence input15,146, Boundaries between the diverse model categories outlined in Box 2 and
increases with a larger number of homologs. Further progress may Fig. 3 are becoming increasingly blurred. Recent developments include
thus be achieved for specific design efforts by enriching training sets models combining structure-aware models together with powerful
with tailored sequence libraries. sequence-based models164 as well as protein language models trained
with a structure-aware vocabulary165. Approaches adapted from the
Finer-grained control of design natural language processing and computer vision literature166 are pro-
The ability to design proteins for precise functions and conditions may viding effective ways to combine diverse modalities in the same model
be facilitated by the growing amount of data quantifying the functions to learn richer protein representations167. Extending machine learning
of both known and synthetic proteins. This corpus of data includes models with biophysics principles may provide the necessary inductive
resources that compile enzyme classification147, substrates and reac- biases to extrapolate beyond the training data168. Improved sampling
tions148,149, gene ontologies150, biophysical properties63,151, millions of approaches169–171 will help increase the quality of generated sequences
measured effects of mutations152 and sequences produced by directed for subsequent experimental validation. The emergence of self-driving
evolution29. Explicitly modeling this information provides finer control laboratories172,173 that leverage a robust integration of uncertainty-aware
over generated sequences, for instance, by conditioning on broad models and experimental processes holds the promise of accelerating
taxonomic labels20,153 and, increasingly, on more granular property comprehensive end-to-end design cycles. In the foreseeable future,
values154,155. Integration with natural language models, as recently intro- we anticipate the rise of unified design models, which fuse aspects
duced for chemical design156 and proteins157,158, may eventually offer a of sequence-based, sequence–label and structure-based models64.
more intuitive interface for design. This will lead to models capable of supporting both tightly controlled
sampling for efficient design iterations, optimizing multiple objectives
In silico evaluation within specific experimental or cellular contexts, and more challeng-
Sequence-only models for design have succeeded in design- ing de novo tasks aimed at designing proteins with functions beyond
ing functional proteins distant in sequence space from existing those naturally occurring.
Nature Biotechnology | Volume 42 | February 2024 | 216–228 223

---

<!-- Page 9 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
References 24. Biswas, S., Khimulya, G., Alley, E. C., Esvelt, K. M. & Church, G. M.
1. Lu, H. et al. Machine learning-aided engineering of hydrolases for Low-N protein engineering with data-efficient deep learning.
PET depolymerization. Nature 604, 662–667 (2022). Nat. Methods 18, 389–396 (2021).
2. Giessel, A. et al. Therapeutic enzyme engineering using a 25. Eid, F.-E. et al. Systematic multi-trait AAV capsid engineering for
generative neural network. Sci. Rep. 12, 1536 (2022). efficient gene delivery. Preprint at bioRxiv https://doi.org/10.1101/
3. Fram, B. et al. Simultaneous enhancement of multiple functional 2022.12.22.521680 (2022).
properties using evolution-informed protein design. Preprint at 26. Li, Y. et al. A diverse family of thermostable cytochrome
bioRxiv https://doi.org/10.1101/2023.05.09.539914 (2023). P450s created by recombination of stabilizing fragments.
4. Sumida, K. H. et al. Improving protein expression, stability, Nat. Biotechnol. 25, 1051–1056 (2007).
and function with ProteinMPNN. J. Am. Chem. Soc. 146, 27. Pak, M. A., Dovidchenko, N. V., Sharma, S. M. & Ivankov, D. N.
2054–2061 (2024). New mega dataset combined with deep neural network makes
5. Schubert, B. et al. Population-specific design of de-immunized a progress in predicting impact of mutation on protein stability.
protein biotherapeutics. PLoS Comput. Biol. 14, e1005983 Preprint at bioRxiv https://doi.org/10.1101/2022.12.31.522396
(2018). (2023).
6. Salvat, R. S. et al. Computationally optimized deimmunization 28. Umerenkov, D. et al. PROSTATA: protein stability assessment
libraries yield highly mutated enzymes with low immunogenicity using transformers. Preprint at bioRxiv https://doi.org/10.1101/
and enhanced activity. Proc. Natl Acad. Sci. USA 114, 2022.12.25.521875 (2022).
E5085–E5093 (2017). 29. Schmitt, L. T., Paszkowski-Rogacz, M., Jug, F. & Buchholz, F.
7. Jankowski, W. et al. Mitigation of T-cell dependent Prediction of designer-recombinases for DNA editing with
immunogenicity by reengineering factor VIIa analogue. Blood generative deep learning. Nat. Commun. 13, 7966 (2022).
Adv. 3, 2668–2678 (2019). 30. Wu, Z., Kan, S. B. J., Lewis, R. D., Wittmann, B. J. & Arnold, F. H.
8. Mufarrege, E. F. et al. De-immunized and functional therapeutic Machine learning-assisted directed protein evolution
(DeFT) versions of a long lasting recombinant α interferon for with combinatorial libraries. Proc. Natl Acad. Sci. USA 116,
antiviral therapy. Clin. Immunol. 176, 31–41 (2017). 8852–8858 (2019).
9. Winterling, K. et al. Development of a novel fully functional 31. Malbranke, C. et al. Computational design of novel Cas9
coagulation factor VIII with reduced immunogenicity utilizing PAM-interacting domains using evolution-based modelling
an in silico prediction and deimmunization approach. J. Thromb. and structural quality assessment. PLoS Comput. Biol. 19,
Haemost. 19, 2161–2170 (2021). e1011621 (2023).
10. Zhao, H. et al. Globally deimmunized lysostaphin evades human 32. Harvey, E. P. et al. An in silico method to assess antibody fragment
immune surveillance and enables highly efficacious repeat polyreactivity. Nat. Commun. 13, 7554 (2022).
dosing. Sci. Adv. 6, eabb9011 (2020). 33. Fox, R. J. et al. Improving catalytic function by ProSAR-driven
11. Zhao, H. et al. Depletion of T cell epitopes in lysostaphin mitigates enzyme evolution. Nat. Biotechnol. 25, 338–344 (2007).
anti-drug antibody response and enhances antibacterial efficacy 34. Romero, P. A., Krause, A. & Arnold, F. H. Navigating the protein
in vivo. Chem. Biol. 22, 629–639 (2015). fitness landscape with Gaussian processes. Proc. Natl Acad. Sci.
12. Hopf, T. A. et al. Mutation effects predicted from sequence USA 110, E193–E201 (2013).
co-variation. Nat. Biotechnol. 35, 128–135 (2017). 35. Saito, Y. et al. Machine-learning-guided library design cycle
13. Riesselman, A. J., Ingraham, J. B. & Marks, D. S. Deep generative for directed evolution of enzymes: the effects of training data
models of genetic variation capture the effects of mutations. composition on sequence space exploration. ACS Catal. 11,
Nat. Methods 15, 816–822 (2018). 14615–14624 (2021).
14. Shin, J.-E. et al. Protein design and variant prediction using 36. Repecka, D. et al. Expanding functional protein sequence spaces
autoregressive generative models. Nat. Commun. 12, 2403 using generative adversarial networks. Nat. Mach. Intell. 3,
(2021). 324–333 (2021).
15. Meier, J. et al. Language models enable zero-shot prediction 37. Sinai, S., Jain, N., Church, G. M. & Kelsic, E. D. Generative AAV
of the effects of mutations on protein function. Adv. Neural Inf. capsid diversification by latent interpolation. Preprint at bioRxiv
Process. Syst. 34, 29287–29303 (2021). https://doi.org/10.1101/2021.04.16.440236 (2021).
16. Frazer, J. et al. Disease variant prediction with deep generative 38. Hawkins-Hooker, A. et al. Generating functional protein
models of evolutionary data. Nature 599, 91–95 (2021). variants with variational autoencoders. PLoS Comput. Biol. 17,
17. Brandes, N., Goldman, G., Wang, C. H., Ye, C. J. & Ntranos, V. e1008736 (2021).
Genome-wide prediction of disease variant effects with a deep 39. Hie, B. L. et al. Efficient evolution of human antibodies
protein language model. Nat. Genet. 55, 1512–1522 (2023). from general protein language models. Nat. Biotechnol.
18. Notin, P. et al. ProteinGym: large-scale benchmarks for protein https://doi.org/10.1038/s41587-023-01763-2 (2023).
fitness prediction and design. In Advances in Neural Information 40. Liu, G. et al. Antibody complementarity determining region
Processing Systems (NeurIPS) Vol. 36 (2023). design using high-capacity machine learning. Bioinformatics 36,
19. Russ, W. P. et al. An evolution-based model for designing 2126–2133 (2020).
chorismate mutase enzymes. Science 369, 440–445 (2020). 41. Holst, L. H. et al. De novo design of a polycarbonate hydrolase.
20. Madani, A. et al. Large language models generate functional Protein Eng. Des. Sel. 36, gzad022 (2023).
protein sequences across diverse families. Nat. Biotechnol. 41, 42. Siegel, J. B. et al. Computational design of an enzyme catalyst for
1099–1106 (2023). a stereoselective bimolecular Diels–Alder reaction. Science 329,
21. Lian, X. et al. Deep learning-enabled design of synthetic 309–313 (2010).
orthologs of a signaling protein. Preprint at bioRxiv https://doi. 43. Jiang, L. et al. De novo computational design of retro-aldol
org/10.1101/2022.12.21.521443 (2022). enzymes. Science 319, 1387–1391 (2008).
22. Dauparas, J. et al. Robust deep learning-based protein sequence 44. Yeh, A. H.-W. et al. De novo design of luciferases using deep
design using ProteinMPNN. Science 378, 49–56 (2022). learning. Nature 614, 774–780 (2023).
23. Watson, J. L. et al. De novo design of protein structure and 45. Anishchenko, I. et al. De novo protein design by deep network
function with RFdiffusion. Nature 620, 1089–1100 (2023). hallucination. Nature 600, 547–552 (2021).
Nature Biotechnology | Volume 42 | February 2024 | 216–228 224

---

<!-- Page 10 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
46. Verkuil, R. et al. Language models generalize beyond natural 68. Khersonsky, O. & Tawfik, D. S. Enzyme promiscuity: a mechanistic
proteins. Preprint at bioRxiv https://doi.org/10.1101/2022.12. and evolutionary perspective. Annu. Rev. Biochem. 79, 471–505
21.521521 (2022). (2010).
47. Lutz, I. D. et al. Top–down design of protein architectures with 69. Arnold, F. H. Directed evolution: bringing new chemistry to life.
reinforcement learning. Science 380, 266–273 (2023). Angew. Chem. Int. Ed. Engl. 57, 4143–4148 (2018).
48. Wang, J. et al. Scaffolding protein functional sites using deep 70. Yang, Y. & Arnold, F. H. Navigating the unnatural reaction space:
learning. Science 377, 387–394 (2022). directed evolution of heme proteins for selective carbene and
49. Dou, J. et al. De novo design of a fluorescence-activating β-barrel. nitrene transfer. Acc. Chem. Res. 54, 1209–1225 (2021).
Nature 561, 485–491 (2018). 71. Bedbrook, C. N. et al. Machine learning-guided channelrhodopsin
50. Basanta, B. et al. An enumerative algorithm for de novo design of engineering enables minimally invasive optogenetics.
proteins with diverse pocket structures. Proc. Natl Acad. Sci. USA Nat. Methods 16, 1176–1184 (2019).
117, 22135–22145 (2020). 72. Wittmann, B. J., Johnston, K. E., Wu, Z. & Arnold, F. H. Advances in
51. Nijkamp, E., Ruffolo, J., Weinstein, E. N., Naik, N. & Madani, A. machine learning for directed evolution. Curr. Opin. Struct. Biol.
ProGen2: exploring the boundaries of protein language models. 69, 11–18 (2021).
Cell Syst. 14, 968–978 (2023). 73. Röthlisberger, D. et al. Kemp elimination catalysts by
52. Ferruz, N., Schmidt, S. & Höcker, B. ProtGPT2 is a deep computational enzyme design. Nature 453, 190–195 (2008).
unsupervised language model for protein design. Nat. Commun. 74. Sesterhenn, F. et al. De novo protein design enables the precise
13, 4348 (2022). induction of RSV-neutralizing antibodies. Science 368, eaay5051
53. Bloom, J. D., Wilke, C. O., Arnold, F. H. & Adami, C. Stability and (2020).
the evolvability of function in a model protein. Biophys. J. 86, 75. Yang, C. et al. Bottom–up de novo design of functional
2758–2764 (2004). proteins with complex structural features. Nat. Chem. Biol. 17,
54. Bloom, J. D., Labthavikul, S. T., Otey, C. R. & Arnold, F. H. Protein 492–500 (2021).
stability promotes evolvability. Proc. Natl Acad. Sci. USA 103, 76. Cao, L. et al. Design of protein-binding proteins from the target
5869–5874 (2006). structure alone. Nature 605, 551–560 (2022).
55. Tokuriki, N., Stricher, F., Serrano, L. & Tawfik, D. S. How protein 77. Ingraham, J. et al. Illuminating protein space with a programmable
stability and new functions trade off. PLoS Comput. Biol. 4, generative model. Nature 623, 1070–1078 (2023).
e1000002 (2008). 78. Trippe, B. L. et al. Diffusion probabilistic modeling of protein
56. Nakatani, K. et al. Increase in the thermostability of Bacillus sp. backbones in 3D for the motif-scaffolding problem. In International
strain TAR-1 xylanase using a site saturation mutagenesis library. Conference on Learning Representations Vol. 11 (ICLR, 2023).
Biosci. Biotechnol. Biochem. 82, 1715–1723 (2018). 79. Lee, J. S., Kim, J. & Kim, P. M. Score-based generative modeling for
57. Katano, Y. et al. Generation of thermostable Moloney murine de novo protein design. Nat. Comput. Sci. 3, 382–392 (2023).
leukemia virus reverse transcriptase variants using site saturation 80. Rajewsky, K. Clonal selection and learning in the antibody system.
mutagenesis library and cell-free protein expression system. Nature 381, 751–758 (1996).
Biosci. Biotechnol. Biochem. 81, 2339–2345 (2017). 81. Teng, G. & Papavasiliou, F. N. Immunoglobulin somatic
58. Richardson, T. H. et al. A novel, high performance enzyme for hypermutation. Annu. Rev. Genet. 41, 107–120 (2007).
starch liquefaction. J. Biol. Chem. 277, 26501–26507 (2002). 82. Boder, E. T., Raeeszadeh-Sarmazdeh, M. & Price, J. V. Engineering
59. Giver, L., Gershenson, A., Freskgard, P.-O. & Arnold, F. H. Directed antibodies by yeast display. Arch. Biochem. Biophys. 526,
evolution of a thermostable esterase. Proc. Natl Acad. Sci. USA 99–106 (2012).
95, 12809–12813 (1998). 83. Wellner, A. et al. Rapid generation of potent antibodies by
60. Bell, E. L. et al. Directed evolution of an efficient and thermostable autonomous hypermutation in yeast. Nat. Chem. Biol. 17,
PET depolymerase. Nat. Catal. 5, 673–681 (2022). 1057–1064 (2021).
61. Alley, E. C., Khimulya, G., Biswas, S., AlQuraishi, M. & 84. McMahon, C. et al. Yeast surface display platform for rapid
Church, G. M. Unified rational protein engineering with discovery of conformationally selective nanobodies. Nat. Struct.
sequence-based deep representation learning. Nat. Methods 16, Mol. Biol. 25, 289–296 (2018).
1315–1322 (2019). 85. Almagro, J. C., Pedraza-Escalona, M., Arrieta, H. I. & Pérez-Tapia, S.
62. Hsu, C. et al. Learning inverse folding from millions of predicted M. Phage display libraries for antibody therapeutic discovery and
structures. In Proceedings of the 39th International Conference development. Antibodies 8, 44 (2019).
on Machine Learning (eds Chaudhuri, K. et al.) 8946–8970 86. Ledsgaard, L. et al. Advances in antibody phage display
(PMLR, 2022). technology. Drug Discov. Today 27, 2151–2169 (2022).
63. Tsuboyama, K. et al. Mega-scale experimental analysis of protein 87. Parkinson, J., Hard, R. & Wang, W. The RESP AI model accelerates
folding stability in biology and protein design. Nature 620, the identification of tight-binding antibodies. Nat. Commun. 14,
434–444 (2023). 454 (2023).
64. Dieckhaus, H., Brocidiacono, M., Randolph, N. & Kuhlman, 88. Saka, K. et al. Antibody design using LSTM based deep generative
B. Transfer learning to leverage larger datasets for improved model from phage display library for affinity maturation. Sci. Rep.
prediction of protein stability changes. Proc. Natl Acad. Sci USA 11, 5852 (2021).
121, e2314853121 (2024). 89. Mason, D. M. et al. Optimization of therapeutic antibodies by
65. Nagano, N., Orengo, C. A. & Thornton, J. M. One fold with many predicting antigen specificity from antibody sequence via deep
functions: the evolutionary relationships between TIM barrel learning. Nat. Biomed. Eng. 5, 600–612 (2021).
families based on their sequences, structures and functions. 90. Makowski, E. K. et al. Co-optimization of therapeutic antibody affinity
J. Mol. Biol. 321, 741–765 (2002). and specificity using machine learning models that generalize
66. Isin, E. M. & Guengerich, F. P. Complex reactions catalyzed to novel mutational space. Nat. Commun. 13, 3788 (2022).
by cytochrome P450 enzymes. Biochim. Biophys. Acta 1770, 91. Shanker, V. R., Bruun, T. U. J., Hie, B. L. & Kim, P. S. Inverse folding
314–329 (2007). of protein complexes with a structure-informed language model
67. Guengerich, F. P. & Munro, A. W. Unusual cytochrome P450 enables unsupervised antibody evolution. Preprint at bioRxiv
enzymes and reactions. J. Biol. Chem. 288, 17065–17073 (2013). https://doi.org/10.1101/2023.12.19.572475 (2023).
Nature Biotechnology | Volume 42 | February 2024 | 216–228 225

---

<!-- Page 11 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
92. Shanehsazzadeh, A. et al. In vitro validated antibody design 113. Racle, J. et al. Machine learning predictions of MHC-II specificities
against multiple therapeutic antigens using generative inverse reveal alternative binding mode of class II epitopes. Immunity 56,
folding. In Generative AI and Biology (GenBio) Workshop, NeurIPS 1359–1375 (2023).
(2023). 114. Peters, B., Nielsen, M. & Sette, A. T cell epitope predictions.
93. Olsen, T. H., Boyles, F. & Deane, C. M. Observed Antibody Space: a Annu. Rev. Immunol. 38, 123–145 (2020).
diverse database of cleaned, annotated, and translated unpaired 115. Bennett, N. et al. Improving de novo protein binder design with
and paired antibody sequences. Protein Sci. 31, 141–146 (2022). deep learning. Nat. Commun. 14, 2625 (2023).
94. Weinstein, E. N. et al. Optimal design of stochastic DNA synthesis 116. Glasscock, C. J. et al. Computational design of sequence-specific
protocols based on generative sequence models. In Proceedings DNA-binding proteins. Preprint at bioRxiv https://doi.org/10.1101/
of the 25th International Conference on Artificial Intelligence and 2023.09.20.558720 (2023).
Statistics (eds Camps-Valls, G., Ruiz, F. J. R. & Valera, I.) 7450–7482 117. Youssef, N. et al. Deep generative models predict SARS-CoV-2
(PMLR, 2022). spike infectivity and foreshadow neutralizing antibody escape.
95. Eguchi, R. R. et al. Deep generative design of epitope-specific Preprint at bioRxiv https://doi.org/10.1101/2023.10.08.561389
binding proteins by latent conformation optimization. Preprint at (2023).
bioRxiv https://doi.org/10.1101/2022.12.22.521698 (2022). 118. Walls, A. C. et al. Elicitation of potent neutralizing antibody
96. Eguchi, R. R., Choe, C. A. & Huang, P.-S. Ig-VAE: generative responses by designed protein nanoparticle vaccines for
modeling of protein structure by direct 3D coordinate generation. SARS-CoV-2. Cell 183, 1367–1382 (2020).
PLoS Comput. Biol. 18, e1010271 (2022). 119. Brouwer, P. J. M. et al. Two-component spike nanoparticle
97. Shanehsazzadeh, A. et al. Unlocking de novo antibody design vaccine protects macaques from SARS-CoV-2 infection. Cell 184,
with generative artificial intelligence. Preprint at bioRxiv 1188–1200 (2021).
https://doi.org/10.1101/2023.01.08.523187 (2023). 120. Cohen, A. A. et al. Mosaic nanoparticles elicit cross-reactive
98. Gainza, P. et al. De novo design of protein interactions with immune responses to zoonotic coronaviruses in mice. Science
learned surface fingerprints. Nature 617, 176–184 (2023). 371, 735–741 (2021).
99. Mahajan, S. P., Ruffolo, J. A., Frick, R. & Gray, J. J. Hallucinating 121. Kang, Y.-F. et al. Rapid development of SARS-CoV-2 spike protein
structure-conditioned antibody libraries for target-specific receptor-binding domain self-assembled nanoparticle vaccine
binders. Front. Immunol. 13, 999034 (2022). candidates. ACS Nano 15, 2738–2752 (2021).
100. Lisanza, S. L. et al. Joint generation of protein sequence and 122. Nguyen, B. & Tolia, N. H. Protein-based antigen presentation
structure with RoseTTAFold sequence space diffusion. Preprint at platforms for nanoparticle vaccines. NPJ Vaccines 6, 70 (2021).
bioRxiv https://doi.org/10.1101/2023.05.08.539766 (2023). 123. Karoyan, P. et al. Human ACE2 peptide-mimics block SARS-CoV-2
101. Chu, A. E., Cheng, L., El Nesr, G., Xu, M. & Huang, P.-S. pulmonary cells infection. Commun. Biol. 4, 197 (2021).
An all-atom protein generative model. Preprint at bioRxiv 124. Glasgow, A. et al. Engineered ACE2 receptor traps potently
https://doi.org/10.1101/2023.05.24.542194 (2023). neutralize SARS-CoV-2. Proc. Natl Acad. Sci. USA 117,
102. Krishna, R. et al. Generalized biomolecular modeling and design 28046–28055 (2020).
with RoseTTAFold All-Atom. Preprint at bioRxiv https://doi.org/ 125. Torchia, J. A. et al. Optimized ACE2 decoys neutralize antibody-
10.1101/2023.10.09.561603 (2023). resistant SARS-CoV-2 variants through functional receptor
103. Krishna, M. & Nadler, S. G. Immunogenicity to biotherapeutics — mimicry and treat infection in vivo. Sci. Adv. 8, eabq6527 (2022).
the role of anti-drug immune complexes. Front. Immunol. 7, 126. Cao, L. et al. De novo design of picomolar SARS-CoV-2
21 (2016). miniprotein inhibitors. Science 370, 426–431 (2020).
104. Chapman, A. M. & McNaughton, B. R. Scratching the surface: 127. Hunt, A. C. et al. Multivalent designed proteins neutralize
resurfacing proteins to endow new properties and function. SARS-CoV-2 variants of concern and confer protection against
Cell Chem. Biol. 23, 543–553 (2016). infection in mice. Sci. Transl. Med. 14, eabn1252 (2022).
105. Remmel, J. L. et al. Combinatorial resurfacing of Dengue 128. Zhang, J. Z. et al. Thermodynamically coupled biosensors for
envelope protein domain III antigens selectively ablates epitopes detecting neutralizing antibodies against SARS-CoV-2 variants.
associated with serotype-specific or infection-enhancing Nat. Biotechnol. 40, 1336–1340 (2022).
antibody responses. ACS Comb. Sci. 22, 446–456 (2020). 129. Leonard, A. C. & Whitehead, T. A. Design and engineering of
106. Bootwala, A. et al. Protein re-surfacing of E. coli l-asparaginase genetically encoded protein biosensors for small molecules.
to evade pre-existing anti-drug antibodies and hypersensitivity Curr. Opin. Biotechnol. 78, 102787 (2022).
responses. Front. Immunol. 13, 1016179 (2022). 130. Quijano-Rubio, A. et al. De novo design of modular and tunable
107. Ingraham, J., Garg, V., Barzilay, R. & Jaakkola, T. Generative models protein biosensors. Nature 591, 482–487 (2021).
for graph-based protein design. In Advances in Neural Information 131. Langan, R. A. et al. De novo design of bioactive protein switches.
Processing Systems Vol. 32 (2019). Nature 572, 205–210 (2019).
108. Thadani, N. N. et al. Learning from prepandemic data to forecast 132. Ng, A. H. et al. Modular and tunable biological feedback control
viral escape. Nature 622, 818–825 (2023). using a de novo protein switch. Nature 572, 265–269 (2019).
109. Singh, H. & Raghava, G. P. ProPred: prediction of HLA-DR binding 133. Lee, G. R. et al. Small-molecule binding and sensing with a
sites. Bioinformatics 17, 1236–1237 (2001). designed protein family. Preprint at bioRxiv https://doi.org/
110. Zhang, L. et al. TEPITOPEpan: extending TEPITOPE for peptide 10.1101/2023.11.01.565201 (2023).
binding prediction covering over 700 HLA-DR molecules. PLoS 134. Courbet, A. et al. Computational design of mechanically coupled
ONE 7, e30483 (2012). axle-rotor protein assemblies. Science 376, 383–390 (2022).
111. Racle, J. et al. Robust prediction of HLA class II epitopes by deep 135. Huang, G., Willems, K., Soskine, M., Wloka, C. & Maglia, G.
motif deconvolution of immunopeptidomes. Nat. Biotechnol. 37, Electro-osmotic capture and ionic discrimination of peptide
1283–1286 (2019). and protein biomarkers with FraC nanopores. Nat. Commun. 8,
112. Reynisson, B. et al. Improved prediction of MHC II antigen 935 (2017).
presentation through integration and motif deconvolution of 136. Zhang, S. et al. Bottom–up fabrication of a proteasome–nanopore
mass spectrometry MHC eluted ligand data. J. Proteome Res. 19, that unravels and processes single proteins. Nat. Chem. 13,
2304–2315 (2020). 1192–1199 (2021).
Nature Biotechnology | Volume 42 | February 2024 | 216–228 226

---

<!-- Page 12 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
137. Shimizu, K. et al. De novo design of a nanopore for 160. Pak, M. A. et al. Using AlphaFold to predict the impact of single
single-molecule detection that incorporates a β-hairpin peptide. mutations on protein stability and function. PLoS ONE 18,
Nat. Nanotechnol. 17, 67–75 (2022). e0282689 (2023).
138. Alfaro, J. A. et al. The emerging landscape of single- 161. AlphaFold Protein Structure Database. Frequently asked
molecule protein sequencing technologies. Nat. Methods 18, questions. AlphaFold Protein Structure Database https://alphafold.
604–617 (2021). ebi.ac.uk/faq (2022).
139. Berhanu, S. et al. Sculpting conducting nanopore size and 162. Johnson, S. R. et al. Computational scoring and experimental
shape through de novo protein design. Preprint at bioRxiv evaluation of enzymes generated by neural networks. Preprint at
https://doi.org/10.1101/2023.12.20.572500 (2023). bioRxiv https://doi.org/10.1101/2023.03.04.531015 (2023).
140. Xu, C. et al. Computational design of transmembrane pores. 163. Tagasovska, N. et al. A Pareto-optimal compositional
Nature 585, 129–134 (2020). energy-based model for sampling and optimization of
141. Hesslow, D., Zanichelli, N., Notin, P., Poli, I. & Marks, D. RITA: protein sequences. Preprint at arXiv https://doi.org/10.48550/
a study on scaling up generative protein sequence models. arXiv.2210.10838 (2022).
Workshop on Computational Biology, ICML (2022). 164. Zheng, Z. et al. Structure-informed language models are protein
142. Hoffmann, J. et al. Training compute-optimal large language designers. In International Conference on Machine Learning Vol.
models. Adv. Neural Inf. Process. Syst. 35, 30016–30030 (2022). 40 (PMLR, 2023).
143. Jumper, J. et al. Highly accurate protein structure prediction with 165. Su, J. et al. SaProt: protein language modeling with structure-
AlphaFold. Nature 596, 583–589 (2021). aware vocabulary. Preprint at bioRxiv https://doi.org/10.1101/
144. Notin, P. et al. Tranception: protein fitness prediction with 2023.10.01.560349 (2023).
autoregressive transformers and inference-time retrieval. In 166. Radford, A. et al. Learning transferable visual models from natural
Proceedings of the 39th International Conference on Machine language supervision. In International Conference on Machine
Learning 16990–17017 (PMLR, 2022). Learning 8748–8763 (PMLR, 2021).
145. Notin, P. et al. TranceptEVE: Combining family-specific and 167. Xu, M., Yuan, X., Miret, S. & Tang, J. ProtST: multi-modality learning
family-agnostic models of protein sequences for improved fitness of protein sequences and biomedical texts. In International
prediction. Learning Meaningful Representations of Life Workshop, Conference on Machine Learning Vol. 40 (PMLR, 2023).
NeurIPS (2022). 168. Malbranke, C., Bikard, D., Cocco, S., Monasson, R. & Tubiana, J.
146. Lin, Z. et al. Evolutionary-scale prediction of atomic-level protein Machine learning for evolutionary-based and physics-inspired
structure with a language model. Science 379, 1123–1130 (2023). protein design: current and future synergies. Curr. Opin. Struct.
147. Kanehisa, M. Enzyme annotation and metabolic reconstruction Biol. 80, 102571 (2023).
using KEGG. Methods Mol. Biol. 1611, 135–145 (2017). 169. Frey, N. C. et al. Protein discovery with discrete walk–jump
148. Mendez, D. et al. ChEMBL: towards direct deposition of bioassay sampling. Preprint at arXiv https://doi.org/10.48550/arXiv.2306.
data. Nucleic Acids Res. 47, D930–D940 (2019). 12360 (2023).
149. Bairoch, A. The ENZYME database in 2000. Nucleic Acids Res. 28, 170. Darmawan, J. T., Gal, Y. & Notin, P. Sampling protein language
304–305 (2000). models for functional protein design. In Generative AI and Biology
150. Ashburner, M. et al. Gene ontology: tool for the unification of (GenBio) Workshop, NeurIPS (2023).
biology. Nat. Genet. 25, 25–29 (2000). 171. Kirjner, A. et al. Optimizing protein fitness using Gibbs sampling
151. Nikam, R., Kulandaisamy, A., Harini, K., Sharma, D. & Gromiha, M. M. with graph-based smoothing. Preprint at arXiv https://doi.org/
ProThermDB: thermodynamic database for proteins and mutants 10.48550/arXiv.2307.00494 (2023).
revisited after 15 years. Nucleic Acids Res. 49, D420–D424 (2021). 172. Rapp, J. T., Bremer, B. J. & Romero, P. A. Self-driving laboratories to
152. Rubin, A. F. et al. MaveDB v2: a curated community database with autonomously navigate the protein fitness landscape. Nat. Chem.
over three million variant effects from multiplexed functional Eng. 1, 97–107 (2024).
assays. Preprint at bioRxiv https://doi.org/10.1101/2021.11.29. 173. Yu, T., Boob, A. G., Singh, N., Su, Y. & Zhao, H. In vitro continuous
470445 (2021). protein evolution empowered by machine learning and
153. Munsamy, G., Lindner, S., Lorenz, P. & Ferruz, N. ZymCTRL: a automation. Cell Syst. 14, 633–644 (2023).
conditional language model for the controllable generation of 174. Morcos, F. et al. Direct-coupling analysis of residue coevolution
artificial enzymes. In Machine Learning for Structural Biology captures native contacts across many protein families. Proc. Natl
Workshop, NeurIPS (2022). Acad. Sci. USA 108, E1293–E1301 (2011).
154. Born, J. & Manica, M. Regression Transformer: concurrent 175. Rives, A. et al. Biological structure and function emerge from
sequence regression and generation for molecular language scaling unsupervised learning to 250 million protein sequences.
modeling. Nat. Mach. Intell. 5, 432–444 (2023). Proc. Natl Acad. Sci. USA 118, e2016239118 (2021).
155. Notin, P., Weitzman, R., Marks, D. S. & Gal, Y. ProteinNPT: 176. Yang, K. K., Fusi, N. & Lu, A. X. Convolutions are competitive with
improving protein property prediction and design with transformers for protein sequence pretraining. Preprint at bioRxiv
non-parametric transformers. In Advances in Neural Information https://doi.org/10.1101/2022.05.19.492714 (2023).
Processing Systems Vol. 36 (2023). 177. Elnaggar, A. et al. ProtTrans: toward understanding the language
156. Bran, A. M., Cox, S., White, A. D. & Schwaller, P. ChemCrow: of life through self-supervised learning. IEEE Trans. Pattern Anal.
augmenting large-language models with chemistry tools. Preprint Mach. Intell. 44, 7112–7127 (2022).
at arXiv https://doi.org/10.48550/arXiv.2304.05376 (2023). 178. Elnaggar, A. et al. Ankh: optimized protein language model
157. Liu, S. et al. A text-guided protein design framework. Preprint at unlocks general-purpose modelling. Preprint at arXiv
arXiv https://doi.org/10.48550/arXiv.2302.04611 (2023). https://doi.org/10.48550/arXiv.2301.06568 (2023).
158. Hie, B. et al. A high-level programming language for generative 179. Rao, R. M. et al. MSA Transformer. In Proceedings of the 38th
protein design. Preprint at bioRxiv https://doi.org/10.1101/ International Conference on Machine Learning 8844–8856
2022.12.21.521526 (2022). (PMLR, 2021).
159. Dallago, C. et al. FLIP: benchmark tasks in fitness landscape 180. Truong, T. F. Jr. & Bepler, T. PoET: a generative model of protein
inference for proteins. In Proceedings of the Neural Information families as sequences-of-sequences. Advances in Neural
Processing Systems Track on Datasets and Benchmarks (2021). Information Processing Systems Vol. 36 (2023).
Nature Biotechnology | Volume 42 | February 2024 | 216–228 227

---

<!-- Page 13 -->

Review article https://doi.org/10.1038/s41587-024-02127-0
181. Alamdari, S. et al. Protein generation with evolutionary diffusion: 199. Veličković, P. et al. Graph attention networks. In International
sequence is all you need. Preprint at bioRxiv https://doi.org/ Conference on Learning Representations Vol. 6 (2018).
10.1101/2023.09.11.556673 (2023). 200. Wicky, B. I. M. et al. Hallucinating symmetric protein assemblies.
182. Brandes, N., Ofer, D., Peleg, Y., Rappoport, N. & Linial, M. Science 378, 56–61 (2022).
ProteinBERT: a universal deep-learning model of protein 201. Gómez-Bombarelli, R. et al. Automatic chemical design using a
sequence and function. Bioinformatics 38, 2102–2110 (2022). data-driven continuous representation of molecules. ACS Cent.
183. Bryant, D. H. et al. Deep diversification of an AAV capsid protein Sci. 4, 268–276 (2018).
by machine learning. Nat. Biotechnol. 39, 691–696 (2021). 202. Castro, E. et al. Transformer-based protein generation with
184. Zhu, D. et al. Optimal trade-off control in machine learning-based regularized latent space optimization. Nat. Mach. Intell. 4,
library design, with application to adeno-associated virus (AAV) 840–851 (2022).
for gene therapy. Sci. Adv. 10, eadj3786 (2024). 203. Notin, P., Hernández-Lobato, J. M. & Gal, Y. Improving black-box
185. Heinzinger, M. et al. Modeling aspects of the language of life optimization in VAE latent space using decoder uncertainty.
through transfer-learning protein sequences. BMC Bioinformatics Adv. Neural Inf. Process. Syst. 34, 802–814 (2021).
20, 723 (2019).
186. Stärk, H., Dallago, C., Heinzinger, M. & Rost, B. Light attention Acknowledgements
predicts protein location from the language of life. Bioinform. Adv. We thank members of the Marks lab for valuable discussions. P.N.
1, vbab035 (2021). was supported by GSK, the UK Engineering and Physical Sciences
187. Yang, K. K., Wu, Z. & Arnold, F. H. Machine-learning-guided Research Council (EPSRC ICASE award no. 18000077) and a
directed evolution for protein engineering. Nat. Methods 16, Chan Zuckerberg Initiative Award (Neurodegeneration Challenge
687–694 (2019). Network, CZI2018-191853). Y.G. holds a Turing AI Fellowship (Phase
188. Gruver, N. et al. Protein design with guided discrete diffusion. In 1) at the Alan Turing Institute, which is supported by EPSRC grant
Advances in Neural Information Processing Systems Vol. 36 (2023). reference V030302/1. C.S. is supported by the National Resource
189. Blaabjerg, L. M. et al. Rapid protein stability prediction using deep for Network Biology (NRNB, P41GM103504). D.S.M. holds a Ben
learning representations. eLife 12, e82593 (2023). Barres Early Career Award from the Chan Zuckerberg Initiative as
190. Baek, M. Efficient and accurate prediction of protein structures part of the Neurodegeneration Challenge Network (CZI2018-191853)
and interactions using RoseTTAFold. Acta Crystallogr. A Found. and is supported by a NIH Transformational Research Award (TR01
Adv. 78, a235 (2022). 1R01CA260415).
191. Wu, R. et al. High-resolution de novo structure prediction from
primary sequence. Preprint at bioRxiv https://doi.org/10.1101/ Competing interests
2022.07.21.500999 (2022). D.M. is an advisor for Dyno Therapeutics, Octant, Jura Bio, Tectonic
192. Anand, N., Eguchi, R. & Huang, P.-S. Fully differentiable full-atom Therapeutic and Genentech and a cofounder of Seismic. N.R. is
protein backbone generation. In Deep Generative Models for employed by Seismic. C.S. is on the scientific advisory board of
Highly Structured Data Workshop, ICLR (2019). CytoReason. The other authors declare no competing interests.
193. Wu, K. E. et al. Protein structure generation via folding diffusion.
Nat. Commun. 15, 1059 (2024). Additional information
194. Jing, B., Eismann, S., Suriana, P., Townshend, R. J. L. & Dror, R. Correspondence and requests for materials should be addressed to
Learning from protein structure with geometric vector Pascal Notin, Nathan Rollins or Debora Marks.
perceptrons. In International Conference on Learning
Representations Vol. 9 (2021). Reprints and permissions information is available at
195. Gao, Z., Tan, C., Chacón, P. & Li, S. Z. PiFold: toward effective and www.nature.com/reprints.
efficient protein inverse folding. In International Conference on
Learning Representations Vo. 11 (2023). Publisher’s note Springer Nature remains neutral with regard to
196. Defferrard, M., Bresson, X. & Vandergheynst, P. Convolutional jurisdictional claims in published maps and institutional affiliations.
neural networks on graphs with fast localized spectral filtering. In
Advances in Neural Information Processing Systems Vol. 29 (2016). Springer Nature or its licensor (e.g. a society or other partner) holds
197. Kipf, T. N. & Welling, M. Semi-supervised classification with graph exclusive rights to this article under a publishing agreement with
convolutional networks. In International Conference on Learning the author(s) or other rightsholder(s); author self-archiving of the
Representations Vol. 5 (2017). accepted manuscript version of this article is solely governed by the
198. Bronstein, M. M., Bruna, J., LeCun, Y., Szlam, A. & Vandergheynst, terms of such publishing agreement and applicable law.
P. Geometric deep learning: going beyond Euclidean data.
IEEE Signal Process. Mag. 34, 18–42 (2017). © Springer Nature America, Inc. 2024
Nature Biotechnology | Volume 42 | February 2024 | 216–228 228
