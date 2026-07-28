<!-- Page 1 -->

Theory
A Whole-Cell Computational Model
Predicts Phenotype from Genotype
Jonathan R. Karr,1,4 Jayodita C. Sanghvi,2,4 Derek N. Macklin,2 Miriam V. Gutschow,2 Jared M. Jacobs,2
Benjamin Bolival, Jr.,2 Nacyra Assad-Garcia,3 John I. Glass,3 and Markus W. Covert2,*
1Graduate Program in Biophysics
2Department of Bioengineering
Stanford University, Stanford, CA 94305, USA
3J. Craig Venter Institute, Rockville, MD 20850, USA
4These authors contributed equally to this work
*Correspondence: mcovert@stanford.edu
http://dx.doi.org/10.1016/j.cell.2012.05.044
SUMMARY First, until recently, not enough has been known about the indi-
vidual molecules and their interactions to completely model
Understanding how complex phenotypes arise from any one organism. The advent of genomics and other high-
individual molecules and their interactions is a throughput measurement techniques has accelerated the char-
primary challenge in biology that computational acterization of some organisms to the extent that comprehensive
approaches are poised to tackle. We report a modeling is now possible. For example, the mycoplasmas,
whole-cell computational model of the life cycle of a genus of bacteria with relatively small genomes that includes
several pathogens, have recently been the subject of an exhaus-
the human pathogen Mycoplasma genitalium that
tive experimental effort by a European consortium to determine
includes all of its molecular components and their
the transcriptome (Gu¨ ell et al., 2009), proteome (Ku¨ hner et al.,
interactions. An integrative approach to modeling
2009), and metabolome (Yus et al., 2009) of these organisms.
that combines diverse mathematics enabled the
The second limiting factor has been that no single computa-
simultaneous inclusion of fundamentally different
tional method is sufficient to explain complex phenotypes in
cellular processes and experimental measurements. terms of molecular components and their interactions. The first
Our whole-cell model accounts for all annotated approaches to modeling cellular physiology, based on ordinary
gene functions and was validated against a broad differential equations (ODEs) (Atlas et al., 2008; Browning
range of data. The model provides insights into et al., 2004; Castellanos et al., 2004, 2007; Domach et al.,
many previously unobserved cellular behaviors, 1984; Tomita et al., 1999), were limited by the difficulty in obtain-
including in vivo rates of protein-DNA association ing the necessary model parameters. Subsequently, alternative
approaches were developed that require fewer parameters,
and an inverse relationship between the durations
including Boolean network modeling (Davidson et al., 2002)
of DNA replication initiation and replication. In
and constraint-based modeling (Orth et al., 2010; Thiele et al.,
addition, experimental analysis directed by model
2009). However, the underlying assumptions of these methods
predictions identified previously undetected kinetic
do not apply to all cellular processes and conditions, and
parameters and biological functions. We conclude
building a whole-cell model entirely based on either method is
that comprehensive whole-cell models can be used therefore impractical.
to facilitate biological discovery. Here, we present a ‘‘whole-cell’’ model of the bacterium
Mycoplasma genitalium, a human urogenital parasite whose
genome contains 525 genes (Fraser et al., 1995). Our model
INTRODUCTION
attempts to: (1) describe the life cycle of a single cell from the
level of individual molecules and their interactions; (2) account
Computer models that can account for the integrated function
for the specific function of every annotated gene product; and
of every gene in a cell have the potential to revolutionize bio-
(3) accurately predict a wide range of observable cellular
logy and medicine, as they increasingly contribute to how we
behaviors.
understand, discover, and design biological systems (Di Ventura
et al., 2006). Models of biological processes have been
increasing in complexity and scope (Covert et al., 2004; Orth RESULTS
et al., 2011; Thiele et al., 2009), but with efforts at increased
inclusiveness of genes, parameters, and molecular functions Whole-Cell Model Construction and Integration
come a number of challenges. Our approach to developing an integrative whole-cell model
Two critical factors in particular have hindered the construc- was to divide the total functionality of the cell into modules,
tion of comprehensive, ‘‘whole-cell’’ computational models. model each independently of the others, and integrate these
Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc. 389

---

<!-- Page 2 -->

A
B
Condensation (3)
Segregation (7)
Damage (0)
Repair (18)
Supercoiling (5)
Replication (10)
Replication initiation (1)
Transcriptional reg. (5)
Transcription (8)
Processing (6)
Modification (14)
Aminoacylation (25)
Decay (2) Translation (103)
Processing I (2)
Translocation (9)
Processing II (2)
Folding (6)
Modification (3)
Complexation (0)
Ribosome assembly (6)
Term. org. assembly (8)
Activation (0)
Decay (9)
FtsZ polymerization (1)
Metabolism (140)
Cytokinesis (1)
Host interaction (16)
Cell process submodels
submodels together. We defined 28 modules (Figure 1A) and
independently built, parameterized, and tested a submodel of
each. Some biological processes have previously been studied
quantitatively and in depth, whereas other processes are less
well characterized or are hardly understood. Consequently,
each module was modeled using the most appropriate mathe-
matical representation. For example, metabolism was modeled
using flux-balance analysis (Suthers et al., 2009), whereas
DNA
RNA
Protein
Other
Update time &
cell variables
Chromosome
Transcript
RNA
Polypeptide
Protein mon.
Complex
RNA pol
No:
Ribosome repeat Initialize Cell
FtsZ ring divided?
Metabolic rxn
Metabolite
Geometry
Host
Mass
Stimulus
Time
Cell variables
AND
ANR
nietorP
etilobateM
rehtO
Figure 1. M. genitalium Whole-Cell Model
External Integrates 28 Submodels of Diverse Cellular
environment RNA
modification Processes
Metabolism d R e N c A ay R as ib s o e s m o b m ly e Term a in s a se l o m r b g l a y nelle (A) Diagram schematically depicts the 28 sub-
tRNA Protein models as colored words—grouped by category
RNA processing aminoacylation Protein translocation Host as metabolic (orange), RNA (green), protein
processing interaction (blue), and DNA (red)—in the context of a single
Host epithelium M. genitalium cell with its characteristic flask-
Transcription like shape. Submodels are connected through
Transcriptional Macromolecular Translation common metabolites, RNA, protein, and the
regulation complexation
supe D r N co A iling mo P d r i o fi t c e a in tion chromosome, which are depicted as orange,
a P ct r i o va te ti i o n n P fo r l o d t i e n i g n green, blue, and red arrows, respectively.
(B) The model integrates cellular function sub-
DNA
repair DNA models through 16 cell variables. First, simulations
damage
Protein Metabolites are randomly initialized to the beginning of the cell
decay
RNA cycle (left gray arrow). Next, for each 1 s time step
Protein (dark black arrows), the submodels retrieve the
Chromosome DNA current values of the cellular variables, calculate
condensation
their contributions to the temporal evolution of the
Replication
DNA initiation cell variables, and update the values of the cellular
replication
FtsZ variables. This is repeated thousands of times
polymerization
during the course of each simulation. For clarity,
Cytokinesis
Chromosome cell functions and variables are grouped into five
segregation
physiologic categories: DNA (red), RNA (green),
protein (blue), metabolite (orange), and other
(black). Colored lines between the variables and
submodels indicate the cell variables predicted by
each submodel. The number of genes associated
with each submodel is indicated in parentheses.
Finally, simulations are terminated upon cell divi-
sion when the septum diameter equals zero (right
gray arrow).
RNA and protein degradation were
modeled as Poisson processes.
A key challenge of the project was to
Send cell integrate the 28 submodels into a unified variables Yes:
terminate model. Although we and others had
previously developed methods to inte-
grate ODEs with Boolean, probabilistic,
and constraint-based submodels (Covert
et al., 2001, 2004, 2008; Chandrasekaran
and Price, 2010), the current effort
involved so many different cellular func-
tions and mathematical representations
that a more general approach was
needed. We began with the assumption
that the submodels are approximately
independent on short timescales (less
than 1 s). Simulations are then performed
by running through a loop in which the
submodels are run independently at each time step but
depend on the values of variables determined by the other
submodels at the previous time step. Figure 1B summarizes
the simulation algorithm and the relationships between the
submodels and the cell variables. Data S1 (available
online) provides a detailed description of the complete
modeling process, including reconstruction and computational
implementation.
390 Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc.

---

<!-- Page 3 -->

Model Training and Parameter Reconciliation specific DNA-binding proteins (Bratton et al., 2011), the
Our model is based on a synthesis of over 900 publications and whole-cell model can predict both the instantaneous protein
includes more than 1,900 experimentally observed parameters. chromosomal occupancy as well as the temporal dynamics
Most of these parameters were implemented as originally and interactions of every DNA-binding protein at the genomic
reported. However, several other parameters were carefully scale at single-cell resolution. Figure 3A illustrates the average
reconciled; for example, the experimentally measured DNA predicted chromosomal protein occupancy as well as the pre-
content per cell (Morowitz et al., 1962; Morowitz, 1992) repre- dicted chromosomal occupancies for DNA and RNA polymerase
sents less than one-third of the calculated mass of the myco- and the replication initiator DnaA, which are three of the 30 DNA-
plasma chromosome. Data S1 details how we resolved this binding proteins represented by our model. Consistent with
and several similar discrepancies among the experimentally a recent experimental study by Vora et al. (2009), the predicted
observed parameters. high-occupancy RNA polymerase regions correspond to highly
Once the model was implemented and all parameters were transcribed ribosomal RNAs (rRNAs) and transfer RNAs (tRNAs).
reconciled, we verified that the model recapitulates key features In contrast, the predicted DNA polymerase chromosomal occu-
of our training data. We simulated 128 wild-type cells in a typical pancy is significantly lower and biased toward the terC (see
Mycoplasma culture environment, with each simulation predict- below for further discussion).
ing not only cellular properties such as the cell mass and growth The model further predicts that the chromosome is explored
rate but also molecular properties including the count, localiza- very rapidly, with 50% of the chromosome having been bound
tion, and activity of each molecule (Movie S1 illustrates the life by at least one protein within the first 6 min of the cell cycle
cycle of one in silico cell). We found that the model calculations and 90% within the first 20 min (Figure 3B). RNA polymerase
were consistent with the observed doubling time (Figures 2A and contributes the most to chromosomal exploration, binding
2B), cellular chemical composition (Figure 2C), replication of 90% of the chromosome within the first 49 min of the cell cycle.
major cell mass fractions (Figure 2D), and gene expression On average, this results in expression of 90% of genes within the
(R2 = 0.68; Figure S1A). first 143 min (Figure 3C), with transcription lagging RNA poly-
merase exploration due to the significant contribution of nonspe-
Model Validation against Independent cific RNA polymerase-DNA interactions to RNA polymerase
Experimental Data diffusion (Harada et al., 1999).
Next, we validated the model against a broad range of indepen- The model also predicts protein-protein collisions on the chro-
dent data sets that were not used to construct the model and mosome. Previous researchers have studied the collisions of
which encompass multiple biological functions—metabolomics, pairs of specific proteins (Pomerantz and O’Donnell, 2010), but
transcriptomics, and proteomics—and scales from single cells experimentally determining the collisions among all pairs of
to populations. In agreement with earlier reports (Yus et al., DNA-binding proteins at the genomic scale at single-cell resolu-
2009), the model predicts that the flux through glycolysis tion is currently infeasible. Our model predicts that over 30,000
is >100-fold more than that through the pentose phosphate collisions occur on average per cell cycle, leading to the
and lipid biosynthesis pathways (Figure 2E). Furthermore, the displacement of 0.93 proteins per second. Figure 3D illustrates
predicted metabolite concentrations are within an order of mag- the binding dynamics of the same proteins depicted in Figure 3A
nitude of concentrations measured in Escherichia coli for 100% over the course of the cell cycle for one representative simulation
of the metabolites in one compilation of data (Sundararaj et al., and highlights several protein-protein collisions. Further catego-
2004) and for 70% in a more recent high-throughput study rization of the predicted collisions by chromosomal location
(Bennett et al., 2009; Figure 2F). Our model also predicts indicates that the frequency of protein-protein collisions corre-
‘‘burst-like’’ protein synthesis due to the local effect of intermit- lates strongly with DNA-bound protein density across the
tent messenger RNA (mRNA) expression and the global effect genome (Figure 3F) and that the majority of collisions are caused
of stochastic protein degradation on the availability of free amino by RNA polymerase (84%) and DNA polymerase (8%), most
acids for translation, which is comparable to recent reports by commonly resulting in the displacement of structural mainte-
Yu et al. (2006) and So et al. (2011) (Figure 2G). The mRNA and nance of chromosome (SMC) proteins (70%) or single-stranded
protein level distributions predicted by our model are also binding proteins (6%) (Figure 3E and Table S2F).
consistent with recently reported single-cell measurements (Fig-
ure 2H; compare to Taniguchi et al., 2010). Taking all of these Identification of Metabolism as an Emergent
specific tests of the model’s predictions together, we concluded Cell-Cycle Regulator
that our model recapitulates experimental data across multiple The model can also highlight interesting aspects of cell behavior.
biological functions and scales. In reviewing our model simulations, we noticed variability in
the cell-cycle duration (Figure 2B) and wanted to determine the
Prediction of DNA-Binding Protein Interactions source of that variability. The model representation of the
Models are often used to predict molecular interactions that are M. genitalium cell cycle consists of three stages: replication initi-
difficult or prohibitive to investigate experimentally, and our ation, replication itself, and cytokinesis. We found that there was
model offers the opportunity to make such predictions in the relatively more cell-to-cell variation in the durations of the repli-
context of the entire cell. Whereas previous studies have either cation initiation (64.3%) and replication (38.5%) stages than in
focused on the genomic distribution of DNA-binding proteins cytokinesis (4.4%) or the overall cell cycle (9.4%; Figure 4A).
(Vora et al., 2009) or on the detailed diffusion dynamics of This data raised two questions: (1) what is the source of duration
Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc. 391

---

<!-- Page 4 -->

Time (d)
60
20
2
0
055DO
0 ln(2) ∆t
τ = ln(dilution factor)
0.2
∆t = 21.4 h ∆t = 19.3 h τ = 9.2 h τ = 8.3 h
1X dilution
0.4 5X dilution
25X dilution
Blank
0.6
0 5 10 15
atad
gniniarT
30
20
)gf(
ssaM
8
0
vid
lleC
%
0 5 10
Time (h)
75
50
25
0
ssam
yrd
tnecreP
DNA Lipid Protein RNA
Time (h)
)mron(
ssaM
2 Total
DNA
RNA
Protein
Membrane
1
0 4 8
Glycolysis
esotneP
etahpsohp
ATP Nucleotide metabolism
synthesis
Pyruvate
metabolism
Flux
(rxn
s
)
-1
104
TalA 102
(0.17%)
GpsA
(0.05%) 100
noitadilav
tnednepednI
Ala Arg Asn Asp Cys Gln Glu Gly His Ile Leu Lys Met Phe Pro Ser Thr Trp Tyr Val ATP CTP GTP UTP ADP CDP GDP UDP AMP CMP GMP UMP dATP dCTP dGTP dTTP Pi PPi H
+
102
101
100
10-1
10-2
noitartnecnoc
ledom/tpxE
Bennett et al., 2009
Literature (CCDB)
Model s.d.
Amino acid NTP NDP NMP dNTP Ion
)tnc(
nietorP
)tnc(
ANRm
0 8
Time (h)
50
0
qerF
50
0
0 1 2 0 6
mRNA count Freq
tnuoc
nietorP
A B
Mean Median cell
τ = 9.0 h τ = 8.9 h
C D
E G
F H
392 Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc.

---

<!-- Page 5 -->

variability in the initiation and replication phases; and (2) why is and replication phases is inversely related to each other in single
the overall cell-cycle duration less varied than either of these cells (Figure 4E), such that longer initiation times led to shorter
phases? replication times. This occurs because cells that require extra
With respect to the first question, replication initiation occurs time to initiate replication also build up a large dNTP surplus,
as DnaA protein monomers bind or unbind stochastically and leading to faster replication. This interplay buffers against the
cooperatively to form a multimeric complex at the replication high variability in the duration of replication initiation, giving rise
origin (Figure 4B, top) (Browning et al., 2004). When the complex to substantially less variability in the length of the cell cycle.
is complete, DNA polymerase gains access to the origin, and the The whole-cell model therefore presents a hypothesis of an
complex is displaced. We found a correlation (R2 = 0.49) emergent control of cell-cycle duration that is independent of
between the predicted duration of replication initiation and the genetic regulation.
initial number of free DnaA monomers (Figure 4C); however,
the low correlation indicated that the duration depends on Global Distribution of Energy
more than the initial conditions. In particular, we observed that The model also provided an opportunity to develop a quantitative
the stochastic aspect of the transcription and translation submo- assessment of cellular energetics, which represents one of the
dels creates variability in the number of new DnaA monomers most connected aspects of our model. To begin, we investigated
produced over time, as well as the DnaA-binding and -unbinding the synthesis dynamics of the high-energy intermediates ATP,
events themselves. This indicates that the variability in replica- GTP, FAD(H ), NAD(H), and NADP(H) and found that ATP and
2
tion initiation duration depends not only on variability in initial guanosine triphosphate (GTP) are synthesized at rates greater
conditions but also in the simulation itself. than 1,000-fold higher than the others (Figure 5A). Notably, the
As to the second question, because the replication sub- overall usage of ATP and GTP did not vary considerably in all
model is substantially more deterministic than the initiation but the very slowest of our simulations (Figure 5B), underscoring
submodel, we expected to find a straightforward relationship the role of metabolism in controlling the cell-cycle length. We
between the progress of replication and the cell cycle. Instead, then considered the processes that use ATP and GTP and found
the model predicts that DNA replication proceeds at two that usage is dominated by production of mRNA and protein
distinct rates during the cell cycle. This is reflected in the motion (Figure 5C). We also found a large (44%) discrepancy between
and DNA-binding density of DNA polymerase (Figures 3A total energy usage and production (Figure 5D). Others have
and 3D) and in the dynamics of DNA synthesis as compared to noted an uncoupling between catabolism and anabolism, attrib-
the synthesis of other macromolecules (Figure 4B, middle). uting the difference to factors such as varying maintenance
Initially, replication proceeds quickly due to the free deoxyribo- costs or energy spilling via futile cycles (Russell and Cook,
nucleotide triphosphate (dNTP) content in the cell (Figure 4B, 1995), and the model’s prediction estimates the total energy
bottom). When DNA polymerase initially binds to the replication cost of such uncoupling.
origin, dNTPs are abundant, and replication proceeds unim-
peded. When the dNTP pool is exhausted, however, the rate Determining the Molecular Pathologies of Single-Gene
of replication slows to the rate of dNTP synthesis. Accordingly, Disruption Phenotypes
the duration of the replication phase in individual cells is Having considered these above-described model predictions for
more closely related to the free dNTP content at the start of repli- the wild-type M. genitalium strain, we next performed in silico
cation than to the dNTP content at the start of the cell cycle genome perturbations to gain insight into the genetic require-
(Figure 4D). ments of cellular life. We performed multiple simulations of
This change in the availability of dNTPs imposes a control on each of the 525 possible single-gene disruption strains (over
the cell-cycle duration. Specifically, the duration of the initiation 3,000 total simulations) and found that 284 genes are essential
Figure 2. The Model Was Trained with Heterogeneous Data and Reproduces Independent Experimental Data across Multiple Cellular
Functions and Scales
(A) Growth of three cultures (dilutions indicated by shade of blue) and a blank control measured by OD550 of the pH indicator phenol red. The doubling time, t, was
calculated using the equation at the top left from the additional time required by more dilute cultures to reach the same OD550 (black lines).
(B) Predicted growth dynamics of one life cycle of a population of 64 in silico cells (randomly chosen from the total simulation set). Median cell is highlighted in red.
Distribution of cell-cycle lengths is shown at bottom.
(C) Comparison of the predicted and experimentally observed (Morowitz et al., 1962) cellular chemical compositions. Red bars indicate model SD; Morowitz et al.
(1962) did not report SD.
(D) Temporal dynamics of the total cell mass and four cell mass fractions of a representative in silico cell. Mass fractions are normalized to their initial values.
(E) Average predicted metabolic fluxes (see Figure S1B for metabolite and reaction labels). Arrow brightness indicates flux magnitude. The ratios of the GpsA and
TalA fluxes to the Glk flux are indicated in orange boxes and are comparable to experimental data (Yus et al., 2009).
(F) Ratios of observed (Sundararaj et al., 2004; Bennett et al., 2009) and average predicted concentrations of 39 metabolites. Blue bars indicate model SD.
(G) Temporal dynamics of cytadherence high-molecular-weight protein 2 (HMW2, MG218) mRNA and protein expression of one in silico cell. Red dashed lines
indicate the direct link between mRNA synthesis and subsequent bursts in protein synthesis.
(H) HMW2 mRNA and protein copy number distribution of an unsynchronized population of 128 in silico cells. Histograms indicate the marginal distributions of the
copy numbers of mRNA (top) and protein (right). Red lines indicate log-normal regressions of these marginal distributions. The absence of correlation between the
copy numbers of mRNA and protein and the shapes of the marginal distributions is consistent with recent single-cell measurements by Taniguchi et al. (2010).
See also Movie S1 and Tables S1 and S2.
Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc. 393

---

<!-- Page 6 -->

10-3
10-4
10-5
10-6
lop
AND
dnuob
.borp
100
10-2
10-4
AanD
dnuob
.borp
100
10-1
10-2
10-3
10-4
lop
ANR
dnuob
.borp
100
10-1
10-2
snietorp
llA
dnuob
.borp
D
*
naA
* * complex
100
Protein * All
oriC RNA pol
SMC
DNA pol
Gyrase
0
0 8
Time (h)
S 3
2 A
N R
,S
6 1 r ,S
5
emosomorhC
%
derolpxe
100 t = 18 min
50
0
0 8
Time (h)
ANR
%
desserpxe
Time (h)
noitisoP
terC
oriC
terC
0 8
Time (h)
)tn(
noitisoP
Lagging
DNA pol
562000
DNA pol-RNA
560000 pol collision
DnaA Complex 558000
DNA pol Leading
RNA pol DNA pol
1.35 1.4
loP
AND
AanD BanD NanD ruF RtnG BAryG AcrH RxuL loP
ANR
CMS BSS VI
opoT
DNA Pol
DnaA
DnaB
DnaN
Fur
GntR
GyrAB
HrcA
LuxR
RNA Pol
SMC
SSB
Topo IV
Binding
gnidnibnU
102
100
10-2
1- )
h(
qerF
)1-h1-tnk(
snoisilloC
A B
C
D
E F
14
12
10
8
6
4
1 2
Density (knt-1)
394 Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc.

---

<!-- Page 7 -->

A C
40 Cell cycle
Replication initiation
Replication 70
Cytokinesis
20
50
30
0 10 0 4 8 12 Duration (h) Replication initiation duration (h)
D
Beginning of cell cycle
Beginning of replication
80
40
0
0 4 8 Replication duration (h)
to sustain M. genitalium growth and division and that 117 are
nonessential. The model accounts for previously observed
gene essentiality with 79% accuracy (p < 10(cid:1)7; Glass et al.,
2006; Figure 6A).
In cases in which the model prediction agrees with the
experimental outcome with respect to gene essentiality, we
found that a deeper examination of the simulation can generate
insight into why the gene product is required by the system.
We examined the capacities of the 525 simulated gene disrup-
tion strains to produce major biomass components (RNA,
DNA, protein, and lipid) and to divide. As shown in Figure 6B,
the nonviable strains were unable to adequately perform one
or more of these major functions. The most debilitating
disruptions involved metabolic genes and resulted in the inability
Figure 3. The Model Highlights the Central Physiological Role of DNA-Protein Interactions
(A) Average density of all DNA-bound proteins and of the replication initiation protein DnaA and DNA and RNA polymerase of a population of 128 in silico cells. Top
magnification indicates the average density of DnaA at several sites near the oriC; DnaA forms a large multimeric complex at the sites indicated with asterisks,
recruiting DNA polymerase to the oriC to initiate replication. Bottom left indicates the location of the highly expressed rRNA genes.
(B and C) Percentage of the chromosome that is predicted to have been bound (B) and the number of genes that are predicted to have been expressed (C) as
functions of time. SMC is an abbreviation for the name of the chromosome partition protein (MG298).
(D) DNA-binding and dissociation dynamics of the oriC DnaA complex (red) and of RNA (blue) and DNA (green) polymerases for one in silico cell. The oriC DnaA
complex recruits DNA polymerase to the oriC to initiate replication, which in turn dissolves the oriC DnaA complex. RNA polymerase traces (blue line segments)
indicate individual transcription events. The height, length, and slope of each trace represent the transcript length, transcription duration, and transcript elon-
gation rate, respectively. The inset highlights several predicted collisions between DNA and RNA polymerases that lead to the displacement of RNA polymerases
and incomplete transcripts.
(E) Predicted collision and displacement frequencies for pairs of DNA-binding proteins.
(F) Correlation between DNA-binding protein density and frequency of collisions across the chromosome. Both (E) and (F) are based on 128 cell-cycle
simulations.
sllec
%
tnuoc
laitinI
selucelom
AanD
fo
)Mm(
.cnoc
PTNd
0 4 8 12
Replication initiation duration (h)
)h(
noitaruD
noitacilpeR
30
10
0
2
E
8
1
20 4
10
0
8
ni
selucelom
AanD
emosomorhC
.cnoc
PTNd
xelpmoc
Ciro
rebmun
ypoc
)Mm(
Figure 4. The Model Predictions Regarding
Regulation of the Cell-Cycle Duration
(A) Distributions of the duration of three cell-cycle
phases, as well as that of the total cell-cycle
length, across 128 simulations.
(B) Dynamics of macromolecule abundance in
a selected cell simulation. Top, the size of the
DnaA complex assembling at the oriC (in mono-
0 mers of DnaA); middle, the copy number of the
chromosome; and bottom, the cytosolic dNTP
B concentration. The quantities of these macromol-
Replication initiation Replication Cytokinesis
120 ecules correlate strongly with the timing of key
cell-cycle stages.
20 (C) Correlation between the initial cellular DnaA
content and the duration of the replication initiation
cell-cycle stage across the same 128 in silico cells
depicted in (A).
(D) Correlation between the dNTP concentrations
(both at the beginning of the cell cycle and at the
beginning of replication) and the duration of repli-
cation across the same 128 in silico cells depicted
in (A).
(E) Correlation between the duration of replication
30 initiation and replication across the same 128
in silico cells depicted in (A).
0
to produce any of the major cell mass
0 4
Time (h) components. The next most debilitating
gene disruptions impacted the synthesis
of a specific cell mass component, such
as RNA or protein. Interestingly, in these cases, the model pre-
dicted an initial phase of near-normal growth followed by
decreasing growth due to diminishing protein content. In some
cases (Figure 6B, fifth column), the time required for the levels
of specific proteins to fall to lethal levels was greater than
one generation (Figures 6C and 6D). A third class of lethal
gene disruptions impaired cell-cycle processes. For these,
the model predicted normal growth rates and metabolism, but
it also predicted incapacity to complete the cell cycle. The
remaining lethal gene disruption strains grew so slowly
compared to wild-type that they were considered nonviable
(Figures 6B and S2). We conclude that the model can be used
to classify cellular phenotypes by their underlying molecular
interactions.
Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc. 395

---

<!-- Page 8 -->

ATP
GTP
NAD(H) NADP(H)
FAD(H )
2
Time (h)
Model-Driven Biological Discovery
Using computational modeling as a complement to an experi-
mental program has previously been shown to facilitate biolog-
ical discovery (Di Ventura et al., 2006). This is often accom-
plished by reconciling model predictions that are initially
inconsistent with observations (Covert et al., 2004). To test the
utility of the whole-cell model in this context, we experimentally
measured the growth rates of 12 single-gene disruption strains—
ten of which were correctly predicted to be viable and two of
which were incorrectly predicted to be nonviable—for compar-
ison to our model’s predictions (Figure 7A). We found that two-
thirds of the predictions were consistent with the measured
growth rates.
The most interesting of these comparisons concerned
the lpdA disruption strain. The lpdA gene was originally deter-
mined to be nonessential (Glass et al., 2006). Consequently,
we initially classified the model’s prediction as false (Figure 6A).
However, we did not detect growth using our colorimetric
assay (Figure 7B), which was a discrepancy that warranted
further investigation. An alternative method to determine the
doubling time yielded a value that was 40% lower than the
wild-type (Table S1). Taken together, the data suggested that
disrupting the lpdA gene had a severe but noncritical impact
on cell growth.
)1-s
lom
12-01(
sisehtnyS
102 2000
0
100 1000
0
10-2 500
0
10-4
100
0
10-6
0 4 8 200
0
200
0
5
0
)1-s
lom
42-01(
esU
PTN
20
0
2
0
2
0
1
0
0.1
0
0.05
0
0.04
0
0.005 0 0 4 8
Time (h)
)lom
81-01(
esu
PTN
toT
A C Translation Figure 5. Model Provides a Global Analysis of the
Use and Allocation of Energy
(A) Intracellular concentrations of the energy carriers ATP,
tRNA aminoacylation
GTP, FAD(H ), NAD(H), and NADP(H) of one in silico cell. 2
(B) Comparison of the cell-cycle length and total ATP and
Transcription GTP usage of 128 in silico cells.
(C) ATP (blue) and GTP (green) usage of 15 cellular
DNA supercoiling processes throughout the life cycle of one in silico cell. The
pie charts at right denote the percentage of ATP and GTP
usage (red) as a fraction of total usage.
Protein decay
(D) Average distribution of ATP and GTP usage among
all modeled cellular processes in a population of 128
B Replication in silico cells. In total, the modeled processes account for
only 44.3% of the amount of energy that has been 125 ATP
Protein translocation experimentally observed to be produced during cellular
GTP growth.
100 FtsZ polymerization
RNA modification
75 In an effort to resolve the discrepancy
Chromosome condensation between our model and the experimental
50 measurements, we determined the molecular
8 10 12 14
Cell Cycle Length (h) Protein modification pathology of the lpdA disruption strain. The
lpdA gene product is part of the pyruvate dehy-
D
Ribosome assembly drogenase complex, which catalyzes the trans-
fer of electrons to nicotinamide adenine dinucle-
Unaccounted
(44.3%) RNA processing otide (NAD) as a subset of the overall pyruvate
dehydrogenase chemical reaction (de Kok
Other Replication Initiation et al., 1998). The viability of the lpdA disruption
(4.4%) strain suggests that this reaction could be cata-
Translation
(29.0%) tR ( N 15 A .1 % ac ) yl Tra ( n 7. s 1 c % r ) iption Chromosome segregation l e y f z fi B e c e d ie c b n a c y u y s a . e no p t r h e e v r io e u n s zy s m tu e d w ie i s th h a av lo e w s e h r o c w a n tal t y h t a ic t
ATP
GTP many M. genitalium genes are multifunctional
(Pollack et al., 2002; Cordwell et al., 1997), we
searched the genome for candidates encoding
an alternative NAD electron transfer pathway. We found that
the Nox sequence was far more similar to the LpdA sequence
than any other gene product in the genome, with 61% coverage,
25% identity, and an expectation value of less than 10(cid:1)6 (Fig-
ure 7C). Furthermore, the nox gene product, NADH oxidase,
has been shown to oxidize NAD (Schmidt et al., 1986). Moreover,
the nox locus falls in a suboperon that contains two other pyru-
vate dehydrogenase genes and has been shown to be
coexpressed with pdhA (Gu¨ ell et al., 2009) (Figure 7D), strongly
suggesting a functional relationship between the products of
these two genes. Our model suggests that, to reproduce the
observed growth rate in the absence of lpdA, the hypothetical
Nox-dependent reaction would require a k of (cid:3)50 s(cid:1)1 (Fig-
cat
ure 7E), which represents only (cid:3)5% of the maximum throughput
of this enzyme. We therefore concluded that substrate promis-
cuity of Nox is likely to enable the lpdA disruption strain to
survive.
Four gene disruption strains exhibited growth rates that were
quantitatively different than those predicted by the model (Fig-
ure 7A); of these, we used the complete simulations for the
thyA and deoD strains to determine the underlying pathology
of the respective gene disruptions. The thyA gene product
catalyzes thymidine monophosphate (dTMP) production and
can be complemented by the tdk gene product. We therefore
396 Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc.

---

<!-- Page 9 -->

Essential Non-ess
hypothesized that, by reducing the k value for Tdk in the modeling can be used to guide biological discovery (Kitano,
cat
model, we would see a reduction in the growth rate of the tdk 2002; Brenner, 2010).
disruption strain. Reducing the Tdk k in the model did indeed
cat
reduce the predicted growth rate of the thyA strain, but it also DISCUSSION
affected the wild-type growth rate (Figure 7F). Only a small range
of the k values both reduced the thyA strain growth rate to the We have developed a comprehensive whole-cell model that
cat
experimentally observed levels and was also consistent with the accounts for all of the annotated gene functions identified in
wild-type growth rate. M. genitalium and explains a variety of emergent behaviors in
In a similar case, purine nucleoside phosphorylase (DeoD) terms of molecular interactions. Our model accurately recapitu-
catalyzes the conversion of deoxyadenosine to adenine and lates a broad set of experimental data, provides insight into
D-ribose-1phosphate; these products can also be produced several biological processes for which experimental assessment
by the pdp gene product from deoxyuridine. We identified is not readily feasible, and enables the rapid identification of
a Pdp k range for which the wild-type and deoD gene disrup- gene functions as well as specific cellular parameters.
cat
tion strains produce the same growth rate (Figure 7G). In contemplating these results, we make two observations
Significantly, these newly predicted k values are consistent based on comparing this work in whole-cell modeling with earlier
cat
with previously reported values. In the original model reconstruc- work in whole-genome sequencing. First, similar to the first
tion, to least constrain the metabolic model, we conservatively reports of the human genome sequence, the model presented
set each of these k s to the least restrictive value found during here is a ‘‘first draft,’’ and extensive effort is required before
cat
the reconstruction process. For Tdk and Pdp, these values cor- the model can be considered complete. Of course, much of
responded to distantly related organisms; however, the newly this effort will be experimental (for example, further characteriza-
predicted k values are consistent with reports from more tion of gene products), but the technical and modeling aspects of
cat
closely related species (Figure 7H). this study will also have to be expanded, updated, and improved
In each of these three cases (lpdA, deoD, and thyA), identifying as new knowledge comes to light.
a discrepancy between model predictions and experimental Second, in whole-genome sequencing as well as in whole-cell
measurements led to further analysis, which resolved the modeling, M. genitialium was a focus of initial studies, primarily
discrepancy and also provided insight into M. genitalium biology because of its small genome size. The goal of our modeling
(Figure 7I). These results support the assertion that large-scale efforts, as well as that of early sequencing projects, was to
laitnessE
sse-noN
Model
tnemirepxE 270 71
14 46
Correct: 316 (79%)
Incorrect: 85 (21%)
Generation
0 10
Time (h)
devaelc
mret-N
)gf(
nietorp
0.3 WT
∆map 0
0 5
Generation
1- ) h
gf(
htworG
A B Essential
Macromolecule synthesis Cell cycle
WT Metabolic RNA Protein Other DNA Cytokinesis Quasi-Ess
(79, tmk) (12, rpoE) (125, asnS) (32, ffh) (8, dnaN) (11, parC) (17, tilS)
2.5
Growth (fg h-1)
0
7
C Protein (fg)
2
0.4
RNA (fg)
0 1.2
D DNA (fg)
1 WT 0.6
250
Septum (nm)
0 ∆map 0
0 5
Figure 6. Model Identifies Common Molecular Pathologies Underlying Single-Gene Disruption Phenotypes
(A) Comparison of predicted and observed (Glass et al., 2006) gene essentiality. Model predictions are based on at least five simulations of each single-gene
disruption strain; see Data S1 for details.
(B) Single-gene disruption strains were grouped into phenotypic classes (columns) according to their capacity to grow, synthesize protein, RNA, and DNA, and
divide (indicated by septum length). Each column depicts the temporal dynamics of one representative in silico cell of each essential disruption strain class.
Disruption strains of nonessential genes are not shown. Dynamics significantly different from wild-type are highlighted in red. The identity of the representative cell
and the number of disruption strains in each category are indicated in parenthesis.
(C and D) Degradation and dilution of N-terminal protein content (C) of methionine aminopeptidase (map, MG172) disrupted cells causes reduced growth (D). Blue
and black lines indicate the map disruption and wild-type strains, respectively. Bars indicate SD.
See also Figure S2 for the distribution of simulated growth rates.
Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc. 397

---

<!-- Page 10 -->

F
smc 0.08 fruA
deoD ecoD WT MG210
MG390
0.06 tkt cinA scpB
thyA
0.04
0.02
lpdA 0
0 0.02 0.04 0.06 0.08 10-2 10-1 100
Predicted growth rate constant (h-1) Tdk k (s-1)
2 cat
)1-h(
tnatsnoc
etar
htworg
latnemirepxE
A
0.08
recA
0.06
0.04
Model prediction
compared to Glass et al. 0.02
2006 True non-essential
False essential Wild-type
)1-h(
tnatsnoc
etar
htworg
detciderP
G
0.08
Wild-type
0.06
ΔdeoD
0.04
∆thyA 0.02
Original
k cat 0
10-4 10-2 100 102
Pdp k (s-1)
1 cat
)1-h(
tnatsnoc
etar
htworg
detciderP
Wild-type
Tdk k
2 cat
VBE VSH suerua
.S .D
retsagonalem
10-2 10-1 100 (s-1)
sulucsum
.M
sneipas
.H
iloc
.E
H
Pdp k
1 cat
10-4 102 (s-1)
0
0.2
0.4
0.6
0 10 20 30
Time (d)
055DO
B
Wild-type
ΔlpdA
blank
C
10-1
10-3
10-5
10-7
lpdA nox trxB glf rplJ
D Pyruvate dehydrogenase
lpdA pdhC pdhB pdhA nox
E 330000 332000 334000
eulav
tcepxE
0.08
WT
deoD
0.06
thyA
lpdA
0.04
0.02
0
0 0.02 0.04 0.06 0.08
Predicted growth rate constant (h-1)
)1-h(
tnatsnoc
etar
htworg
latnemirepxE
Original
k cat
I
Refined kinetic parameters (modeling, experiments)
0.08
Newly predicted 0.06 protein function
(modeling, experiments,
0.04 informatics)
0.02
0
etar
htworg
detciderP
)1-h(
tnatsnoc
*
Wild-type
LpdA-pyruvate
dehyhrogenase
ΔlpdA k
cat
10-1 101 103
Nox-pyruvate dehydrogenase k (s-1) cat
Figure 7. Quantitative Characterization of Selected Gene Disruption Strains Leads to Identification of Novel Gene Functions and Kinetic
Parameters
(A) Comparison of measured and predicted growth rates for wild-type and 12 single-gene disrupted strains. Model predictions that fall within the shaded region
were considered consistent with experimental observations; the region has a width of four times the SD of the wild-type strain growth measurement. Horizontal
and vertical bars indicate predicted and observed SD.
(B) Growth curves for the wild-type and lpdA gene disruption strains and blank, similar to Figure 2A.
(C) Expectation values determined by performing a pBLAST search of the M. genitalium genome with the LpdA sequence as a query. The asterisk and colored bar
indicate a significant match (E < 10(cid:1)6).
(D) Detail of the M. genitalium genome. The pyruvate dehydrogenase complex genes are indicated by the top bracket, and transcription units identified in
M. pneumoniae (Gu¨ ell et al., 2009) are indicated by arrows. The transcription unit including nox is highlighted in color.
(E) Allowing Nox to partially replace LpdA in pyruvate dehydrogenase reconciles model predictions and experimental observations. The blue and red lines
represent the predicted wild-type and DlpdA strain growth rates as a function of the Nox-pyruvate dehydrogenase kcat. The pink box indicates the kcat at which
the model predictions are consistent with both the wild-type and DlpdA strain experimentally measured growth rates.
(F and G) Diagnosing the discrepancy between predictions and experiment for the thyA (F) and deoD (G) gene disruption strains. Some of the functionalities of
ThyA and DeoD can be replaced by the enzymes Tdk and Pdp, respectively. The predicted growth rates of the wild-type and gene disruption strains depend on
the kcat of these enzymes. The green region highlights the range of kcat values that are consistent with the measured growth rates of both the wild-type and gene
disruption strain.
(H) Newly predicted kcat values are similar to values that were measured in closely related organisms. Measured values of kcat for Tdk (top) and Pdp (bottom) are
shown; green arrow indicates the initial and revised kcat values. The nearest M. genitalium relative is highlighted in green.
398 Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc.

---

<!-- Page 11 -->

develop the technology in a reduced system before proceeding on a 1 s timescale using different mathematics and different experimental
to more complex organisms. However, M. genitalium presents data. The submodels spanned six areas of cell biology: (1) transport and
many challenges with regard to experimental tractability. metabolism; (2) DNA replication and maintenance; (3) RNA synthesis and
maturation; (4) protein synthesis and maturation; (5) cytokinesis; and (6) host
Resistance to most antibiotics, the lack of a chemically defined
interaction. Submodels were implemented as separate classes. See Data S1
medium, and a cell size that requires advanced microscopy
for further discussion of each submodel.
techniques for visualization all greatly limit the range of experi-
mental techniques available to study this organism. As a result, Submodel Integration
much of the data used to build and validate the model were ob- We integrated the submodels in three steps. First, we structurally integrated
tained from other organisms. Therefore, although the results we the process submodels by linking their common inputs and outputs through
16 cell variables (shown in Figure 1), which together represent the complete
report suggest several experiments that could yield important
configuration of the modeled cell: (1) metabolite, RNA, and protein copy
insight with respect to M. genitalium function, comprehensive
numbers; (2) metabolic reaction fluxes; (3) nascent DNA, RNA, and protein
validation of our approach will require modeling more experi- polymers; (4) molecular machines; (5) cell mass, volume, and shape; (6) the
mentally tractable organisms such as E. coli. external environment, including the host urogenital epithelium; and (7) time.
We are optimistic that whole-cell models will accelerate bio- Second, the common inputs to the submodels were computationally allocated
logical discovery and bioengineering by facilitating experimental at the beginning of each time step. Third, we refined the values of the submo-
del parameters to make the submodels mutually consistent. See Data S1 for
design and interpretation. Moreover, these findings, in combina-
further discussion.
tion with the recent de novo synthesis of the M. genitalium chro-
mosome and successful genome transplantation of Mycoplasma
Simulation Algorithm
genomes to produce a synthetic cell (Gibson et al., 2008, 2010; The whole-cell model is simulated using an algorithm comparable to those
Lartigue et al., 2007, 2009), raise the exciting possibility of using used to numerically integrate ODEs. First, the cell variables are initialized.
whole-cell models to enable computer-aided rational design of Second, the temporal evolution of the cell state is calculated on a 1 s timescale
novel microorganisms. Finally, we anticipate that the construc- by repeatedly allocating the cell variables among the processes, executing
each of the cellular process submodels, and updating the values of the cell
tion of whole-cell models and the iterative testing of them against
variables. Finally, the simulation terminates when either the cell divides or
experimental information will enable the scientific community to
the time reaches a predefined maximum value. See Data S1 for further
assess how well we understand integrated cellular systems. discussion.
Single-Gene Disruptions
EXPERIMENTAL PROCEDURES
Single-gene disruptions were modeled by (1) initializing the cell variables, (2)
deleting the in silico gene, and (3) calculating the temporal evolution of the
Reconstruction
cell state for the first generation postdisruption. We also calculated the
The whole-cell model was based on a detailed reconstruction of M. genitalium
mean growth rate of each single-gene disruption strain at successive genera-
that was developed from over 900 primary sources, reviews, books, and data-
tions postdisruption. See Data S1 for further discussion of the implementation
bases. First, we reconstructed the organization of the chromosome, including
of disruption strains and their computational analysis.
the locations of each gene, transcription unit, promoter, and protein-binding
site. Second, we functionally annotated each gene, beginning with the
Computational Simulation and Analysis
Comprehensive Microbial Resource (CMR) annotation. Functional annotation
We used the whole-cell model to simulate 192 wild-type cells and 3,011 single-
was primarily based on homologs identified by bidirectional best BLAST. To fill
gene deletants. All simulations were performed with MATLAB R2010b on a 128
gaps in the reconstructed organism and to maximize the scope of the model,
core Linux cluster. The predicted dynamics of each cell were logged at each
we expanded and refined each gene’s annotation using primary research arti-
time point and subsequently analyzed using MATLAB. See Data S1 for further
cles and reviews (see Data S1 and Table S3). Third, we curated the structure of
discussion.
each gene product, including the posttranscriptional and posttranslational
processing and modification of each RNA and protein and the subunit compo-
Bacterial Culture
sition of each protein and ribonucleoprotein complex. After annotating each
M. genitalium wild-type and mutant strains with single-gene disruptions by
gene, we categorized the genes into 28 cellular processes. We curated the
transposon insertion (Glass et al., 2006) were grown in Spiroplasma SP-4
c in h a e n m M ic y a S l Q re L ac re ti l o a n ti s on o a f l e d a a c ta h b c a e s l e lu . l S a e r e p D ro a c t e a s S s 1 . T a h n e d T re a c b o le ns S t 3 ru f c o t r io fu n rt w he a r s d s is to c r u e s d - culture media at 37(cid:4)C and 5% CO 2 . Growth was detected using the phenol
red pH indicator. Cells were harvested for quantitative growth measurement
sion of the reconstruction.
at pH 6.3–6.7. See Data S1 for more information about media and culture
conditions.
Cellular Process Submodels
Because biological systems are modular, cells can be modeled by the Colorimetric Assay to Measure Cell Growth
following: (1) dividing cells into functional processes; (2) independently To measure the growth rates of the wild-type and mutant strains, cells were
modeling each process on a short timescale; and (3) integrating process sub- collected from 10 cm plate cultures at pH 6.3–6.7, resuspended in 3 ml of fetal
models at longer timescales. We divided M. genitalium into the 28 functional bovine serum (FBS), and serial filtered through 1.2, 0.8, 0.45, and 0.2 mm poly-
processes illustrated in Figure 1 and modeled each process independently ethersulfone filters to sterilize and separate individual cells. Cells were then
(I) Model-based biological discovery. Comparison of model predictions to experimental measurements identified gene disruption strains of particular interest,
including the lpdA, deoD, and thyA disruption strains. Further investigation—using a combination of experiments, modeling, and/or informatics—led to new and
more consistent measurements and predictions. Most importantly, the higher consistency reflected novel insights into M. genitalium biology. The arrows (red for
lpdA, green for deoD and thyA) indicate the shift from lower to higher consistency between model and experiment, and each arrow is annotated with the new
biological insight and the supporting evidence in parentheses. The overall graph format is the same as in Figure 7A. Horizontal and vertical bars indicate predicted
and observed SD.
Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc. 399

---

<!-- Page 12 -->

plated at 5-, 25-, and 125-fold serial dilutions in triplicate on a 96-well plate and Chandrasekaran, S., and Price, N.D. (2010). Probabilistic integrative modeling
incubated at 37(cid:4)C and 5% CO2. Six wells per plate were filled with blank SP-4 of genome-scale metabolic and regulatory networks in Escherichia coli and
phenol red media as a negative control. Optical density readings were taken Mycobacterium tuberculosis. Proc. Natl. Acad. Sci. USA 107, 17845–17850.
twice a day at 550 nm to measure the decrease in phenol red color as pH Cordwell, S.J., Basseal, D.J., Pollack, J.D., and Humphery-Smith, I. (1997).
decreased. Growth rate constants were calculated from the additional time Malate/lactate dehydrogenase in mollicutes: evidence for a multienzyme
required for consecutive dilutions to reach the same OD550 value and were protein. Gene 195, 113–120.
averaged over two to three independent sets of three replicates. See Data
Covert, M.W., Schilling, C.H., and Palsson, B.O. (2001). Regulation of gene
S1 for further description of these calculations. We used a heteroscedastic
expression in flux balance models of metabolism. J. Theor. Biol. 213, 73–88.
two-sample two-tailed t test to determine whether the doubling time of each
single-gene disruption strain differed significantly from that of the wild-type. Covert, M.W., Knight, E.M., Reed, J.L., Herrgard, M.J., and Palsson, B.O.
The growth rates of several slow-growing strains were also measured by (2004). Integrating high-throughput and computational data elucidates bacte-
DNA quantification using a modified version of the procedure described in rial networks. Nature 429, 92–96.
Glass et al. (2006). See Data S1 for further discussion. Covert, M.W., Xiao, N., Chen, T.J., and Karr, J.R. (2008). Integrating metabolic,
transcriptional regulatory and signal transduction models in Escherichia coli.
Source Code Bioinformatics 24, 2044–2050.
The model source code, training data, and results are freely available at SimTK Davidson, E.H., Rast, J.P., Oliveri, P., Ransick, A., Calestani, C., Yuh, C.H.,
(https://simtk.org/home/wholecell). Minokawa, T., Amore, G., Hinman, V., Arenas-Mena, C., et al. (2002). A
genomic regulatory network for development. Science 295, 1669–1678.
SUPPLEMENTAL INFORMATION de Kok, A., Hengeveld, A.F., Martin, A., and Westphal, A.H. (1998). The pyru-
vate dehydrogenase multi-enzyme complex from Gram-negative bacteria.
Supplemental Information includes Extended Experimental Procedures, one Biochim. Biophys. Acta 1385, 353–366.
data file, two figures, three tables, and one movie and can be found with this
Di Ventura, B., Lemerle, C., Michalodimitrakis, K., and Serrano, L. (2006). From
article online at http://dx.doi.org/10.1016/j.cell.2012.05.044.
in vivo to in silico biology and back. Nature 443, 527–533.
Domach, M.M., Leung, S.K., Cahn, R.E., Cocks, G.G., and Shuler, M.L. (1984).
ACKNOWLEDGMENTS
Computer model for glucose-limited growth of a single cell of Escherichia coli
B/r-A. Biotechnol. Bioeng. 26, 1140.
We thank R. Altman, S. Brenner, Z. Bryant, J. Ferrell, K. Huang, B. Palsson, S.
Quake, L. Serrano, J. Swartz, E. Yus, and the Covert Lab for numerous enlight- Fraser, C.M., Gocayne, J.D., White, O., Adams, M.D., Clayton, R.A., Fleisch-
ening discussions on bacterial physiology and computational modeling; mann, R.D., Bult, C.J., Kerlavage, A.R., Sutton, G., Kelley, J.M., et al. (1995).
T. Vora for critical reading of the manuscript; and M. O’Reilly and J. Maynard The minimal gene complement of Mycoplasma genitalium. Science 270,
for graphical design assistance. This work was supported by an NIH Director’s 397–403.
Pioneer Award (1DP1OD006413) and a Hellman Faculty Scholarship to Gibson, D.G., Benders, G.A., Andrews-Pfannkoch, C., Denisova, E.A., Baden-
M.W.C.; NSF and Bio-X Graduate Student Fellowships to J.C.S.; NDSEG, Tillson, H., Zaveri, J., Stockwell, T.B., Brownley, A., Thomas, D.W., Algire,
NSF, and Stanford Graduate Student Fellowships to J.R.K.; a Benchmark M.A., et al. (2008). Complete chemical synthesis, assembly, and cloning of
Stanford Graduate Fellowship to D.N.M.; and a U.S. Department of Energy a Mycoplasma genitalium genome. Science 319, 1215–1220.
Cooperative Agreement (DE-FC02-02ER63453) to the J. Craig Venter Institute. Gibson, D.G., Glass, J.I., Lartigue, C., Noskov, V.N., Chuang, R.Y., Algire,
M.A., Benders, G.A., Montague, M.G., Ma, L., Moodie, M.M., et al. (2010).
Received: March 8, 2012 Creation of a bacterial cell controlled by a chemically synthesized genome.
Revised: April 20, 2012 Science 329, 52–56.
Accepted: May 14, 2012
Glass, J.I., Assad-Garcia, N., Alperovich, N., Yooseph, S., Lewis, M.R., Maruf,
Published: July 19, 2012
M., Hutchison, C.A., III, Smith, H.O., and Venter, J.C. (2006). Essential genes of
a minimal bacterium. Proc. Natl. Acad. Sci. USA 103, 425–430.
REFERENCES
Gu¨ ell, M., van Noort, V., Yus, E., Chen, W.H., Leigh-Bell, J., Michalodimitrakis,
K., Yamada, T., Arumugam, M., Doerks, T., Ku¨ hner, S., et al. (2009). Transcrip-
Atlas, J.C., Nikolaev, E.V., Browning, S.T., and Shuler, M.L. (2008). Incorpo-
tome complexity in a genome-reduced bacterium. Science 326, 1268–1271.
rating genome-wide DNA sequence information into a dynamic whole-cell
model of Escherichia coli: application to DNA replication. IET Syst. Biol. 2, Harada, Y., Funatsu, T., Murakami, K., Nonoyama, Y., Ishihama, A., and
369–382. Yanagida, T. (1999). Single-molecule imaging of RNA polymerase-DNA inter-
actions in real time. Biophys. J. 76, 709–715.
Bennett, B.D., Kimball, E.H., Gao, M., Osterhout, R., Van Dien, S.J., and
Rabinowitz, J.D. (2009). Absolute metabolite concentrations and implied Kitano, H. (2002). Systems biology: a brief overview. Science 295, 1662–1664.
enzyme active site occupancy in Escherichia coli. Nat. Chem. Biol. 5, 593–599. Ku¨ hner, S., van Noort, V., Betts, M.J., Leo-Macias, A., Batisse, C., Rode, M.,
Bratton, B.P., Mooney, R.A., and Weisshaar, J.C. (2011). Spatial distribution Yamada, T., Maier, T., Bader, S., Beltran-Alvarez, P., et al. (2009). Proteome
and diffusive motion of RNA polymerase in live Escherichia coli. J. Bacteriol. organization in a genome-reduced bacterium. Science 326, 1235–1240.
193, 5138–5146. Lartigue, C., Glass, J.I., Alperovich, N., Pieper, R., Parmar, P.P., Hutchison,
Brenner, S. (2010). Sequences and consequences. Philos. Trans. R. Soc. C.A., III, Smith, H.O., and Venter, J.C. (2007). Genome transplantation in
Lond. B Biol. Sci. 365, 207–212. bacteria: changing one species to another. Science 317, 632–638.
Browning, S.T., Castellanos, M., and Shuler, M.L. (2004). Robust control of Lartigue, C., Vashee, S., Algire, M.A., Chuang, R.Y., Benders, G.A., Ma, L.,
initiation of prokaryotic chromosome replication: essential considerations for Noskov, V.N., Denisova, E.A., Gibson, D.G., Assad-Garcia, N., et al. (2009).
a minimal cell. Biotechnol. Bioeng. 88, 575–584. Creating bacterial strains from genomes that have been cloned and engi-
Castellanos, M., Wilson, D.B., and Shuler, M.L. (2004). A modular minimal cell neered in yeast. Science 325, 1693–1696.
model: purine and pyrimidine transport and metabolism. Proc. Natl. Acad. Sci. Morowitz, H.J. (1992). Beginnings of Cellular Life: Metabolism Recapitulates
USA 101, 6681–6686. Biogenesis (New Haven, CT: Yale University Press).
Castellanos, M., Kushiro, K., Lai, S.K., and Shuler, M.L. (2007). A genomically/ Morowitz, H.J., Tourtellotte, M.E., Guild, W.R., Castro, E., and Woese, C.
chemically complete module for synthesis of lipid membrane in a minimal cell. (1962). The chemical composition and submicroscopic morphology of
Biotechnol. Bioeng. 97, 397–409. Mycoplasma gallisepticum, avian PPLO 5969. J. Mol. Biol. 4, 93–103.
400 Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc.

---

<!-- Page 13 -->

Orth, J.D., Thiele, I., and Palsson, B.O. (2010). What is flux balance analysis? Suthers, P.F., Dasika, M.S., Kumar, V.S., Denisov, G., Glass, J.I., and Mara-
Nat. Biotechnol. 28, 245–248. nas, C.D. (2009). A genome-scale metabolic reconstruction of Mycoplasma
Orth, J.D., Conrad, T.M., Na, J., Lerman, J.A., Nam, H., Feist, A.M., and genitalium, iPS189. PLoS Comput. Biol. 5, e1000285.
Palsson, B.O. (2011). A comprehensive genome-scale reconstruction of
Taniguchi, Y., Choi, P.J., Li, G.W., Chen, H., Babu, M., Hearn, J., Emili, A., and
Escherichia coli metabolism—2011. Mol. Syst. Biol. 7, 535.
Xie, X.S. (2010). Quantifying E. coli proteome and transcriptome with single-
Pollack, J.D., Myers, M.A., Dandekar, T., and Herrmann, R. (2002). Suspected molecule sensitivity in single cells. Science 329, 533–538.
utility of enzymes with multiple activities in the small genome Mycoplasma
species: the replacement of the missing ‘‘household’’ nucleoside diphosphate Thiele, I., Jamshidi, N., Fleming, R.M., and Palsson, B.O. (2009). Genome-
kinase gene and activity by glycolytic kinases. OMICS 6, 247–258. scale reconstruction of Escherichia coli’s transcriptional and translational
machinery: a knowledge base, its mathematical formulation, and its functional
Pomerantz, R.T., and O’Donnell, M. (2010). Direct restart of a replication fork
characterization. PLoS Comput. Biol. 5, e1000312.
stalled by a head-on RNA polymerase. Science 327, 590–592.
Russell, J.B., and Cook, G.M. (1995). Energetics of bacterial growth: balance Tomita, M., Hashimoto, K., Takahashi, K., Shimizu, T.S., Matsuzaki, Y.,
of anabolic and catabolic reactions. Microbiol. Rev. 59, 48–62. Miyoshi, F., Saito, K., Tanida, S., Yugi, K., Venter, J.C., and Hutchison, C.A.,
Schmidt, H.L., Sto¨ cklein, W., Danzer, J., Kirch, P., and Limbach, B. (1986). III. (1999). E-CELL: software environment for whole-cell simulation. Bioinfor-
Isolation and properties of an H2O-forming NADH oxidase from Strepto- matics 15, 72–84.
coccus faecalis. Eur. J. Biochem. 156, 149–155. Vora, T., Hottes, A.K., and Tavazoie, S. (2009). Protein occupancy landscape
So, L.H., Ghosh, A., Zong, C., Sepu´ lveda, L.A., Segev, R., and Golding, I. of a bacterial genome. Mol. Cell 35, 247–253.
(2011). General properties of transcriptional time series in Escherichia coli.
Yu, J., Xiao, J., Ren, X., Lao, K., and Xie, X.S. (2006). Probing gene expression
Nat. Genet. 43, 554–560.
in live cells, one protein molecule at a time. Science 311, 1600–1603.
Sundararaj, S., Guo, A., Habibi-Nazhad, B., Rouani, M., Stothard, P., Ellison,
M., and Wishart, D.S. (2004). The CyberCell Database (CCDB): a comprehen- Yus, E., Maier, T., Michalodimitrakis, K., van Noort, V., Yamada, T., Chen,
sive, self-updating, relational database to coordinate and facilitate in silico W.H., Wodke, J.A., Gu¨ ell, M., Martı´nez, S., Bourgeois, R., et al. (2009). Impact
modeling of Escherichia coli. Nucleic Acids Res. 32 (Database issue), D293– of genome reduction on bacterial metabolism and its regulation. Science 326,
D295. 1263–1268.
Cell 150, 389–401, July 20, 2012 ª2012 Elsevier Inc. 401
