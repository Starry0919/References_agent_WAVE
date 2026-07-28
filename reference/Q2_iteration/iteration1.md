<!-- Page 1 -->

Methods to watch
The virtual cell the availability of biological data — although
orders of magnitude higher than decades
ago — is still dwarfed as compared with areas
such as language and image processing, in
which powerful large language models now
Virtual cells based on artificial dominate. More critically, high-quality data
intelligence models are on the that are particularly valuable for revealing
horizon biological mechanism and causality, such
as multimodal, time-series or perturbation
data, are still badly needed. Also, there is still
By Lin Tang no consensus on the best modeling strategy
to build a virtual cell model; how to leverage
The paramount appeal of a virtual cell existing models and biological knowledge is
model cannot be overstated (Cell 187, an open question.
7045–7063; 2024). From molecular cell There are even yet more directions to
biology to translational medicine, almost explore, such as generating virtual tissues Intrinsic disorder in proteins makes
every branch of life sciences stands to benefit using spatial omics technology data, which structural characterization a challenge.
from it. Despite largely being a conceptual feat take into account intercellular interactions
at present, some of our wish list items for a vir- and communication. Although it is still early
tual cell model include that: (1) it will provide days to affirmatively answer the question of have been linked to various diseases, which
a holistic picture of all the molecular and cel- when a virtual cell model will be within reach, necessitates the development of methods to
lular phenotypes of a cell; (2) it will be mecha- we are excited to witness the flourishing characterize them.
nistic and dynamic, and reveal the biological of methods development towards this Recent developments have advanced both
underpinnings of various cellular behaviors; ambitious goal. experimental and computational methods
and (3) it will be predictive, with the ability in this field. DisP-seq makes use of disorto generate predictions under a wide range dered protein precipitation followed by
of conditions. DNA sequencing to map the genome-wide
Intrinsic protein
With the age of big data and artificial binding of DNA-associated proteins that
intelligence (AI), massive volumes of bio- disorder at scale contain IDRs (Nat. Biotechnol. 42, 52–64;
logical data (especially those generated 2024). This is a departure from previously
by high-throughput omics technologies) available technologies that use antibodies
coupled with advanced machine-learning to pull down proteins and were restricted to
approaches represent two of the major drivers well-characterized proteins.
that fuel the aspiration of virtual cell models. Methods to study the structural and Another method for global analysis of
A large number of AI models already exist for functional properties of proteins endogenous protein disorder uses a bifuncvarious specific biological tasks, including that contain intrinsically disordered tional chemical probe called TME to caprecently emerging foundation models that ture unfolded proteins, marked by exposed
regions at the proteome scale are on
aim to be versatile performers (Nature 640, cysteine residues, in situ (Nat. Methods 22,
the rise.
623–633; 2025). However, there is still a long 124–134; 2025). The captured proteins are
way to go to meeting the challenges on our detected by a fluorescence readout or enriched
wish list. By Arunima Singh and analyzed by mass spectrometry-based
One persistent bottleneck is data scarcity. proteomics. The approach enables the cap-
As recently touched upon by a Nature Meth- Recent advances in computational pro- ture of both basal disordered proteins as well
ods Editorial (Nat. Methods 22, 1387; 2025), tein structure prediction methods, as proteins whose folding status changes
along with high-throughput and com- under stress at a cellular level.
prehensive proteomic analysis approaches, ALBATROSS is a deep-learning-based model
have deepened our understanding of the rela- that combines rational sequence design and
tionships between protein structure and func- large-scale molecular simulations to predict
tion. However, one class of proteins continues the ensemble properties of IDPs directly from
to elude more comprehensive investigation — sequence (Nat. Methods 21, 465–476; 2024).
intrinsically disordered proteins (IDPs) and Another computational method to generate
proteins that contain intrinsically disordered conformational ensemble for IDRs was used
regions (IDRs). Unlike structured proteins, to simulate nearly all (more than 28,000)
IDPs lack a fixed three-dimensional fold, IDRs from the human proteome (Nature 626,
which makes them difficult to characterize 897–904; 2024). Additionally, a strategy
using traditional biochemical and structural specifically developed to target flexible IDPs
methods. Nevertheless, nearly 40% of human and IDRs has proven effective in generating
Using virtual cell models to simulate proteins are estimated to contain IDRs and experimentally validated binders against a
biological experiments. are involved in key regulatory pathways and variety of disordered proteins (Nature 644,
nature methods
Volume 22 | December 2025 | 2493–2497 | 2493
