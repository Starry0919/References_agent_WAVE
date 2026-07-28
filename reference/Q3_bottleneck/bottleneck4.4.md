<!-- Page 1 -->

Received: 29 January 2024 Revised: 22 March 2024 Accepted: 19 May 2024
DOI: 10.1002/aic.18501
R E S E A R C H A R T I C L E
P r o c e s s S y s t e m s E n g i n e e r i n g
Simultaneous design of fermentation and microbe
Anita L. Ziegler 1 | Ashutosh Manchanda 1 | Marc-Daniel Stumm 1 |
Lars M. Blank 2 | Alexander Mitsos 1,3,4
1Process Systems Engineering (AVT.SVT),
RWTH Aachen University, Aachen, Germany Abstract
2Institute of Applied Microbiology (iAMB), Constraint-based optimization of microbial strains and model-based bioprocess
Aachen Biology and Biotechnology (ABBt),
design have been used extensively to enhance yields in biotechnological processes.
RWTH Aachen University, Aachen, Germany
3JARA-ENERGY, Aachen, Germany However, strain and process optimization are usually carried out in sequential steps,
4Institute of Energy and Climate Research, causing underperformance of the biotechnological process when scaling up to indus-
Energy Systems Engineering (IEK-10),
trial fermentation conditions. Herein, we propose the optimization formulation Simul-
Forschungszentrum Jülich GmbH, Jülich,
Germany Knock that combines the optimization of a fermentation process with metabolic
network design in a bilevel optimization program. The upper level maximizes space-
Correspondence
Alexander Mitsos, Process Systems time yield and includes mass balances of a continuous fermentation, while the lower
Engineering (AVT.SVT), RWTH Aachen
level is based on flux balance analysis. SimulKnock predicts optimal gene deletions
University, 52074 Aachen, Germany.
Email: amitsos@alum.mit.edu and finds the optimal trade-off between growth rate and product yield. Results of a
case study with a genome-scale metabolic model of Escherichia coli indicate higher
Funding information
RWTH Aachen University, Grant/Award space-time yields than a sequential approach using OptKnock for almost all target
Number: thes1376; Deutsche
products considered. By leveraging SimulKnock, we reduce the gap between strain
Forschungsgemeinschaft, Grant/Award
Number: 390919832 and process optimization.
K E Y W O R D S
computational strain design, constraint-based metabolic modeling, metabolic engineering,
process optimization
1 | I N T RO DU CT I O N refine the cellular objective of the organism7 or better suit a geneti-
cally modified microorganism.8–10 Constraint-based strain optimiza-
Industrial microbiology promises product synthesis from renewable tion formulations go one step further and predict targets for genetic
feedstocks representing a sustainable alternative to petro-chemical modification.3,11 The first formulation, OptKnock, was presented by
synthesis.1 Often, these biotechnological products are produced by Burgard et al.12 OptKnock proposes optimal gene deletions by solving
high-performing microbial strains that have been designed using met- a bilevel optimization problem. The upper level represents the bio-
abolic engineering. Strain design is supported by computational engineering perspective to maximize the product yield on the
methods to reduce the experimental effort.2 In the first place, substrate. The lower level, based on FBA, represents the micro-
constraint-based metabolic modeling formulations predict the influ- organism with the cellular objective of maximizing biomass produc-
ence of a given genetic modification on the microorganism.3 The tion. OptKnock has been extended, for example, to account for
best-known formulation is flux balance analysis (FBA).4–6 Using linear worst-case predictions,13 insertion of genes,14 and up and down
programming, FBA predicts the internal fluxes of a microorganism regulation of genes.15,16 It was also modified to suit a genetically
based on its genome-scale metabolic model (GEM). Variations of FBA modified organism better.17 For strain design, the predicted
This is an open access article under the terms of the Creative Commons Attribution License, which permits use, distribution and reproduction in any medium,
provided the original work is properly cited.
© 2024 The Author(s). AIChE Journal published by Wiley Periodicals LLC on behalf of American Institute of Chemical Engineers.
AIChE J. 2024;70:e18501. wileyonlinelibrary.com/journal/aic 1 of 14
https://doi.org/10.1002/aic.18501

---

<!-- Page 2 -->

2 of 14 ZIEGLER ET AL.
modifications are experimentally tested and evaluated at a labora- consider continuous fermentation, an envisaged fermentation mode
tory scale, and the best-performing strain is chosen. in industry. SimulKnock, however, can readily be extended to account
For industrial production, industrial-scale process conditions come for other fermentation modes, too. Certainly, extensions may result in
into play. Process design involves the analysis of mass and energy bal- different optimization classes, for example, simultaneous optimization
ances and production costs, including up- and downstream processing.18 of batch operation and strain design would be a dynamic bilevel opti-
In bioprocess design, a suitable kinetic represents the microorganism, for mization problem, which is challenging.30,34 Michaelis-Menten or
example, its growth.19,20 Computational process optimization supports Monod kinetics are employed to connect the two levels. Compared to
process design by adjusting the process parameters to achieve maximal existing strain optimization formulations, SimulKnock can be inter-
space-time yield or minimal production cost.20–22 preted as an extension of OptKnock by process equations or as a vari-
Typically, strain and process design are separate steps, performed ation of dFBA with a switch to continuous fermentation and
in sequence. Process conditions, however, influence the behavior and implementation of a process objective and knockout predictions. Simi-
performance of the microorganism. Hence, a high-performing strain in larly, SimulKnock can be seen as an extension of process optimization
the laboratory may underperform in an industrial process. For exam- by the strain optimization level (lower level). For our case studies, we
ple, a strain is first designed under small-scale batch fermentation con- use strong dualization to reformulate the bilevel optimization program
ditions in the laboratory. Next, the industrial process is designed for into a single-level program and solve it globally. We apply our formu-
the designated strain, whereby industrial processes are envisaged to lation to a GEM of Escherichia coli for the production of ethanol, succi-
run on a large scale in continuous mode, and example processes nate, acetate, formate, fumarate, and lactate and compare the results
already exist in the pharmaceutical and food sectors. This switch in with sequential optimization results and experimental results for suc-
conditions entails a significant adjustment for the organism. Reasons cinate production from the literature. The proposed formulation
for the under-performance can be steep gradients in the spatial distri- SimulKnock will help close the gap in profitability between petro-
bution of substrates (e.g., oxygen) in the fermenter, high downstream chemical and biochemical processes.
processing costs, or lacking genetic and phenotypic stability by the
microbe.23,24 Strain and process design coupling is needed to over-
come these scale-up difficulties.24,25 There exist different approaches 2 | M E T H O D : SI M U L K N O C K
to do so. In their attempt to capture spatial changes in a stirred biore-
actor, Lapin et al.26 coupled computational fluid dynamics and meta- 2.1 | Mass balances for a continuous process
bolic modeling. To model diauxic growth, Mahadevan et al.27 optimization
connected the mass balance equations of batch fermentation with
metabolic modeling in their dynamic flux balance analysis (dFBA). For optimal process design, the fermentation process was modeled
Structurally, dFBA are differential-algebraic equations with embedded with mathematical equations. These equations may include mass and
optimization criteria. For fed-batch fermentation, Oliveira et al.28 energy balances of different reactor types and process units. In Simul-
replaced the metabolic network in dFBA with a surrogate model. In an Knock, we chose the mass balance equations of a continuous stirred-
iterative process, Zhuang et al.29 connected dFBA with computational tank reactor. In principle, however, SimulKnock can easily be extended
strain optimization techniques to suit the organism to the future pro- to account for other reactor types or even full processes. We assumed
cess conditions of batch fermentation. Ploch et al.30 developed a that the reactor is ideally mixed and contains only one homogeneous
differential-algebraic equation system with embedded dFBA optimiza- phase, that only one substrate limits growth and production, and that
tion to model a biorefinery process under changing conditions. Jabari- only one population of organisms is in the tank. Furthermore, we
velisdeh et al.31 introduced a bilevel dynamic optimization framework, assumed that the volumetric inflow equals the volumetric outflow.
where a previously found genetic modification can be switched on The biomass, the substrate, and the product were chosen as the rep-
during batch fermentation. In a step-wise approach, Tafur Rangel resentative compounds of the fermentation. Similar to standard litera-
et al.32 selected a microbial strain regarding the required downstream ture, mass conservation leads to
process units. Dimitriou et al.33 considered downstream process opti-
mization simultaneous to strain optimization, namely in a superstruc- dc d b t io ¼ ðμ (cid:2) DÞ (cid:3) c bio ture optimization program. However, the implications of the switch
dc 1 1 from laboratory (batch or fed-batch) fermentation conditions to indus- dt S ¼ (cid:2) Y bio=S (cid:3) μ (cid:3) c bio (cid:2) Y P=S (cid:3) q p (cid:3) c bio (cid:2) m S (cid:3) c bio þ D (cid:3) ðc S,Feed (cid:2) c SÞ ð1Þ
trial (continuous) fermentation conditions have yet to be considered. dc
We propose a new formulation combining strain optimization dt P ¼ q P (cid:3) c bio (cid:2) c P (cid:3) D,
with process optimization. Our simultaneous approach SimulKnock,
suggests optimal gene deletions that suit a strain to its future where D is the dilution rate in h(cid:2)1; c is the biomass concentration in
bio
industrial-scale conditions, and at the same time, the process condi- gram Cell Dry Weight (CDW) per liter (g L(cid:2)1); c , c and c are
CDW S,Feed S P
tions are customized to the strain. SimulKnock is a bilevel optimization the substrate feed concentration, substrate concentration, and prod-
program where the upper level maximizes the space-time yield subject uct concentration, respectively (all in g L(cid:2)1). Y bio=S and Y P=S , both with
to the mass balances of fermentation, and the lower level maximizes the unit g g(cid:2)1, are the yields of biomass and product per substrate,
biomass production based on the FBA formulation. In this article we respectively. The maintenance factor is denoted as m in g g(cid:2)1 h(cid:2)1
S
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use; OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 3 -->

ZIEGLER ET AL. 3 of 14
and describes the required substrate uptake rate for cellular mainte- 2.3 | Proposed combined optimization:
nance. Two kinetics were used in the equations: the product kinetics SimulKnock
q in g g(cid:2)1 h(cid:2)1, describing the rate of formation of the product, and
P
the growth rate kinetics μ in h(cid:2)1, describing the rate of formation of We designed SimulKnock by embedding the FBA into the optimization
the biomass. The dilution rate D is the quotient of the volumetric of a continuous fermentation accounting for cellular degrees of freedom,
inflow/outflow and the culture volume within the bioreactor. The resulting in a bilevel optimization formulation (Figure 1), following the par-
dilution rate is also the inverse of the residence time. As is typical, we adigm of OptKnock.12 Using the steady-state mass balances of metabo-
assumed that a flow equilibrium is achieved after a sufficiently long lites stemming from FBA, we assume that the cellular metabolism adapts
period of operation at a constant dilution rate. It follows that the con- infinitesimally quickly to shifting environmental conditions.35
tinuous fermentation is at a steady state, such that dcbio ¼ 0, dcS ¼ 0, SimulKnock maximizes the space-time yield in the upper-level
dt dt
and dcP ¼ 0 apply. Thereby, it directly follows that D ¼ μ, which means program like other bioprocess optimization examples.36,37 The con-
dt
that biomass is neither washed out nor accumulated in the process. nection between upper- and lower-level program is achieved via the
expression of process parameters with metabolic variables, based on
Ploch et al.30 and Mahadevan et al.27 The growth rate directly trans-
2.2 | Flux balance analysis forms to μ ¼ v bio , and due to steady-state continuous fermentation
conditions, it holds D ¼ v bio . Moreover, instead of considering that
FBA analyzes the internal fluxes within a cell using linear everything taken up goes into product formation, biomass formation,
programming.4–6 The analysis is based on the metabolic network of or maintenance, the substrate uptake is now directly expressed by
an organism that includes the metabolites and the stoichiometry (cid:2) YX 1 =S (cid:3) μ (cid:2) Y 1 P=S (cid:3) q p (cid:2) m S ¼ (cid:2)v S (cid:3) M S , where v S is the substrate uptake flux of the internal reactions. In FBA, based on the steady state assump- in mmol g(cid:2)1 h(cid:2)1 and M denotes the molar mass of the substrate in
CDW S
tion, the metabolites' net accumulation rates are constrained to g mmol(cid:2)1. Thus, the maintenance is only directly considered at the
zero, and the reaction fluxes are constrained to upper and lower lower level in SimulKnock by setting a threshold on the ATP mainte-
bounds. One cellular objective is defined, for example, the maximi- nance reaction; there is no doubling at the upper level. The rate of
zation of the biomass flux. The mathematical formulation of product formation can also be directly considered now by setting
FBA reads q P ¼ v P (cid:3) M P , where v P is the product flux in mmol g(cid:2) CD 1 W h(cid:2)1 and is an
element of the flux vector v and M is the molar mass of the product
P
max v bio in g mmol(cid:2)1. Hence, (1) transforms to v  ℝn
s:t: Sv ¼ 0
vlower ≤ v ≤ vupper, D ¼ v bio
0 ¼ (cid:2)v S (cid:3) M S (cid:3) c bio þ D (cid:3) ðc S,Feed (cid:2) c SÞ
where v denotes the vector of reaction fluxes in mmol g(cid:2)1 h(cid:2)1 and 0 ¼ v P (cid:3) M P (cid:3) c bio (cid:2) c P (cid:3) D:
CDW
where n is the number of reactions in a metabolic network, where
all reversible reactions were split into one forward and one back- Note that instead of fixing the dilution rate in the upper level and,
ward reaction, further called irreversible network. The biomass thereby, fixing the growth rate, the dilution rate D will be set accord-
flux is denoted by v in h(cid:2)1 and is an element of v; S is the stoichio- ing to the optimal value of v after the lower-level optimization.
bio bio
metric matrix of the irreversible network, and lower and upper are Hence, in the following, D will be replaced with v .
bio
lower and upper bounds of the flux values, respectively. These bounds Up to this point, we replaced process parameters with metabolic
may include thresholds on the biomass flux or the ATP maintenance variables, using the mechanistic, FBA-based model in the cellular level.
reaction. However, the process variable c does not yet have a connection to
S
F I G U R E 1 The bilevel optimization
formulation of SimulKnock. Note that
either Monod or Michaelis-Menten
kinetics are applied at the upper level or
the lower level.
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on [21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 4 -->

4 of 14 ZIEGLER ET AL.
the cellular level. Without this connection, c will always be set to reactions, further referred to as a reversible network. The parame-
S
zero during optimization (for analysis and exemplary studies, see the ter K is the number of maximal allowed knockouts, and the parameter
Appendix S1). Whether this setting is a valid assumption, however, f denotes a value between zero and one. The matrix B maps the reac-
can not be known in advance, or requires expert knowledge of the tions in the irreversible metabolic network with those in the reversible
specific strain in application. In order to overcome this issue, we network. The apostrophe 0 denotes the cellular variables in the upper
embedded an empirical model of kinetics. The combination of mecha- level. Note that, in the algorithm, they are fixed by the lower-level
nistic and empirical models in our optimization formulation is neces- program. As comes clear from (3), we define “knockout” as “reaction
sary, because the metabolic model can only replace process variables elimination” in this manuscript. The corresponding genes to the sug-
originating from the cellular level, as we have executed above. We gested reactions can be identified via the gene-protein-reaction rule.
considered two alternative kinetics to connect the upper and lower Note that several genes can correspond to one reaction.
levels: Monod and Michaelis-Menten. In the Appendix S1, we discuss As described above, we chose to eliminate D and c from the for-
S
why including both kinetics simultaneously is not advisable. mulation. In theory, the process variables c and c could also be
bio P
Monod is an empirical, widely known, and easy-to-measure model eliminated, as the equality constraints at the upper level are fixing
of microbial growth. It links the substrate concentration with the them. Nevertheless, we decided on this formulation because prelimi-
growth rate and reads nary tests and our intuition suggest that it results in simpler con-
vergence. Note that our recent research indicates that an
c v
v bio ¼ v b m io ax c S þ S K S ) c S ¼ K S v b m io ax b (cid:2) io v bio , ðMonodÞ ð2Þ i r n e t d e u r c m e e d d -s ia p t a e ce b f e o tw rm e u e l n atio fu n ll- ( s e p li a m c i e nat ( i k n e g ep a i l n l g va a ri l a l bl v e a s ria e b x l c e e s p ) t a t n h d e
degrees of freedom) is most beneficial in some cases.38,39 With c bio
where vmax denotes the maximum growth rate in h(cid:2)1, and K denotes and c being fixed by equality constraints, the substrate concentration
bio S P
the Monod affinity constant in g L(cid:2)1 for the specified substrate. We in the feed c is the only degree of freedom in the process condi-
S,Feed
assumed that gene deletions would not affect the kinetic parame- tions. At the cellular level, v will reach its upper bound based on an S
ters, i.e., we assumed that the kinetic parameters were constants experimental value, as it is standard in other strain optimization exam-
for a given organism and substrate. Thus, both vmax and K are ples (e.g., Reference 12). Even if the Monod kinetics constrain v and
bio S bio
parameters taken from literature or, in the case of vmax , can be c is fixed during optimization; spare carbon atoms will go into
bio S,Feed
approximated with FBA. The growth rate results from the lower- product formation.
level program, and thus, the Monod kinetics need to be imposed on In this article, the Monod constant was set to 0:044 g L(cid:2)1, and
the upper-level program (reactor level). As depicted on the right- vmax was set to 0:73 h(cid:2)1, according to Wick et al.40 The wild-type bio-
bio
hand side in (2), we, therefore, reformulated the kinetics such that mass flux v was determined by a previously performed FBA, and
bio,WT
the substrate concentration is a function of the growth rate: the parameter f was set to 0.1. Furthermore, the ATP maintenance
c S ¼ fðv bioÞ. Then, we implemented the kinetics in the upper level by reaction flux threshold was set to 6:86 mmol g(cid:2) CD 1 W h(cid:2)1, according to
replacing c with the kinetic term. If we would keep c , the growth the default value in iML1515.41 The upper bound of the glucose
S S
rate would be fixed by the kinetic term (equality constraint) instead of exchange reaction was set to 10 mmol g(cid:2)1 h(cid:2)1.
CDW
being optimized at the lower level. SimulKnock with included Monod Alternatively, we used Michaelis-Menten, the simplest form
kinetics reads of enzyme kinetics. Enzymes catalyze reactions within a cell, with
metabolites as reactants. An enzyme-catalyzed reaction can be
y,cS,Feed,cP m ,c a bio x ,v0 S ,v0 bio ,v0 P Pr c P (cid:3) v0 bio d M e a s h c a ri d b e e v d an us e in t g al M .27 ich a a n e d lis- P M lo e c n h ten et ki a n l e .,3 ti 0 cs. we In c a h l o ig s n e me to nt a w pp it l h y
s:t: ð1 (cid:2) y Þ ≤ K
i Michaelis-Menten kinetics to the substrate uptake reaction. Thus,
i¼1
0 ¼ (cid:2)v0 S (cid:3) (cid:2) M S (cid:3) c bio (cid:3) the kinetics link the substrate concentration in the bioreactor
þv0 bio (cid:3) c S,Feed (cid:2) K S vmax v0 b (cid:2) io v0 with the substrate uptake rate. More precisely, the substrate
bio bio uptake rate is a function of the substrate concentration:
v 0 0 ¼  v0 P ar (cid:3) g M m P (cid:3) a c x bio v (cid:2) c P (cid:3) v0 bio v S ¼ gðc SÞ. The kinetics read
bio v  ℝn
s:t: v S bi v o ¼ ≥ f 0 (cid:3) v bio,WT v S ¼ v S max c S þ c K S S,MM : ðMichaelis-MentenÞ
v ≥ vlower ∘ ðByÞ
v ≤ vupper ∘ ðByÞ, The maximal substrate uptake is denoted with v S max in mmol g(cid:2) CD 1 W h(cid:2)1,
ð3Þ and the Michaelis constant is K
S,MM
in g L(cid:2)1. Again, we assumed that
the kinetic parameters were constants and, thus, can be retrieved
where ∘ denotes the element-wise product, y  f0,1gr denotes the from the literature. As v S is a cellular variable, the kinetics were imple-
binary knockout vector, and r denotes the number of reactions in a mented in the lower level. SimulKnock with embedded Michaelis-
metabolic network, which contains irreversible and reversible Menten kinetics reads
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on Wiley
Online
Library
for rules
of use;
OA
articles are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 5 -->

ZIEGLER ET AL. 5 of 14
y,cS,Feed,cS, m cP, a cb x io,v0 S ,v0 bio ,v0 P c P (cid:3) v0 bio multiple substrates would potentially be easier with Michaelis-Menten
Pr (cf. Reference 30).
s:t: ð1 (cid:2) y Þ ≤ K
i
i¼1
0 ¼ (cid:2)v0 S (cid:3) M S (cid:3) c bio þ v0 bio (cid:3) ðc S,Feed (cid:2) c SÞ
0 ¼ v0 P (cid:3) M P (cid:3) c bio (cid:2) c P (cid:3) v0 bio 2.4 | Reformulation of the bilevel program
v0  arg max v to a single-level quadratically constrained quadratic
bio
v  ℝn
s:t: Sv ¼ 0 program
v bio ≥ f (cid:3) v bio,WT
c We used the software packages libALE43 and libDIPS44 to implement
v S ¼ v S max c S þ K S S,MM SimulKnock in both versions—Monod (3) and Michaelis-Menten (4)—and
v ≥ vlower ∘ ðByÞ successfully solved the bilevel programs for the E. coli core network45
v ≤ vupper ∘ ðByÞ: using the algorithm46 without KKT-based tightening and with Gurobi
ð4Þ v10.047 as the subsolver. However, this algorithm was too expensive for
the genome-scale metabolic model iML1515.41 Consequently, we refor-
Again, c and c are being fixed by the equality constraints in the mulated the bilevel programs to single-level mixed-integer quadratically
bio P
upper level. However, unlike the formulation including Monod, c is a constrained quadratic programs (MIQCQP). We conducted two reformu-
S
degree of freedom at the process level now. It is included in the lation steps for numerical reasons: first, we reformulated SimulKnock as a
upper-level equality constraint in the summand v bio (cid:3) ðc S,Feed (cid:2) c SÞ. single-level program. Second, we eradicated nonlinear terms to achieve
With v being part of the upper-level objective, this term also has an an MIQCQP formulation of SimulKnock. bio
optimum, and c is determined during the optimization. Another dif- To the first reformulation: In both versions of SimulKnock
S
ference is that v is now constrained by the kinetics instead of reach- (Monod or Michaelis-Menten embedded), the cellular level is linear
S
ing the upper bound set by the user. (in the lower-level variables, as the process level fixes the process
In our article, the Michaelis constant was calculated with variables). Thus, we can apply strong duality and reformulate to a
0:53 mmol L(cid:2)1 multiplied by the molar weight of glucose, and vmax single-level program. The reformulations for SimulKnock with Monod
S
was set to 10 mmol g(cid:2)1 h(cid:2)1, both values according to Meadows kinetics embedded are identical to those presented in OptKnock,12 as
CDW
et al.42 the Monod kinetics are in the upper-level program. In the following,
To simplify the comparison of Monod and Michaelis-Menten, Table 1 we will show the reformulation of SimulKnock with Michaelis-Menten
summarizes the different aspects of both kinetics applied in SimulKnock. kinetics embedded. For ease of notation, we introduced
Apart from the aspects already discussed above, we found that, in
2 3 2 3
general, the parameter availability for Monod is higher than for Ijnj vlower ∘ ðByÞ (cid:4)
Michaelis-Menten. Furthermore, the inclusion of inhibitions is suppos- C~ ¼ 6 4 Ijnj 7 5,b~ ¼ 6 4(cid:2)vupper ∘ ðByÞ 7 5,c i ¼ 1 0 , , i i f f i i ¼ ≠ b b io io , 8i  1,:::,n,
edly a straightforward extension with Monod, whereas including cT kin d
T A B L E 1 Comparison of Monod and Michaelis-Menten in where c describes the position of the biomass reaction and I is the
SimulKnock. unity matrix. The vector c
kin
 f0,1gjnj has exactly one nonzero entry
Monod Michaelis-Menten at the index of the glucose uptake reaction. The scalar d describes the
Functionality cS ¼ fðv bioÞ vS ¼ gðcSÞ right-hand side of the kinetics, that is, d ¼ v S max cSþK cS S,MM . By applying
the definitions above, the lower-level program of (4) can be rewrit-
Level Whole-cell kinetics ! Enzyme kinetics !
process level cellular level ten as
v Unrestricted, reaches Restricted by
S
its upper bound kinetics and c max cTv S v
c S Calculated by kinetics Determined by s:t: S (cid:3) v ¼ 0 ð5Þ equality constraint C~ (cid:3) v ≤ b~
and objective in v ≥ 0:
process level
Assumption Gene deletion does Gene deletion does
Converting program (5) to its dual and applying the strong duality
not change growth not change
behavior substrate uptake theorem yields the system of equations
behavior
Parameter availability Higher Lower cTv ¼ b~T (cid:3) μ~
Possible extensions Inclusion of Consideration of S (cid:3) v ¼ 0
inhibitions multiple substrates C~ (cid:3) v ≤ b~ ð6Þ
c ¼ ST (cid:3) λ þ C~T (cid:3) μ~
Abbreviations: c : substrate concentration; f, g: notation for functions;
S
v : growth rate; v : substrate uptake rate. μ~ ≥ 0,
bio S
15475905,
2024,
9, Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on Wiley
Online
Library
for
rules
of use;
OA
articles
are
governed
by
the applicable
Creative
Commons
License

---

<!-- Page 6 -->

6 of 14 ZIEGLER ET AL.
with λ  ℝjmj being the dual variables corresponding to the mass bal- on flux coupling analysis,52 lastly, the metabolic network was divided
ances for the metabolites and μ~ ℝj2nþ1j being the dual variables cor- into sections. This last step of network reduction was applied in our
þ
responding to the bounds set on the reaction fluxes through the case studies with GEMs but is optional for users of the open-source
inequality constraints and the kinetics. The set of Equations (6) can code. All programs were solved with Gurobi v10.0.47
readily replace the cellular level in (4). The resulting program is a
single-level mixed-integer nonlinear program. The nonlinearity is
introduced by the fact that process and cellular variables are at the 3 | C A S E S T U D I E S
same level now. The nonlinear term is the kinetic term in d. These
considerations about nonlinearity are also applicable to the reformu- We performed three case studies with SimulKnock. The first case
lated SimulKnock with Monod embedded. study illustrates SimulKnock's mode of action compared to OptKnock
In the second reformulation step, we reformulated the nonlinear and a sequential optimization approach. The second case study
kinetic term. We introduced an additional variable for the fraction on employs the genome-scale metabolic model iML151541 of E. coli for
the right-hand side of the kinetics, thereby introducing an additional one to three knockout predictions and elaborates on the differences
equality constraint in the problem. For example, in the Michaelis- between Monod and Michaelis-Menten kinetics. Note again that the
Menten kinetics, the fraction is replaced with the optimization vari- term knockout refers to reaction elimination in this article and that
able σ , and the constraints one knockout can result in multiple gene deletions, if several genes
MM
correspond to the targeted reaction. The third case study compares
v S ¼ vm S axσ MM ð7Þ the results of SimulKnock with the published results of an experimen-
σ MMðc S þ K S,MMÞ ¼ c S tal study on E. coli continuous fermentation.53 The first case study
was performed on up to 8 Intel Xeon E5-2640 CPU threads and was
are introduced, which results in the single-level optimization problem solved within less than a second. Case studies two and three were
becoming an MIQCQP. This reformulation is beneficial because solved within 5 h on the RWTH high-performance computing cluster
MIQCQPs are solved directly by commercial solvers, such as Gurobi.47 using 48 threads and up to 4 GB of memory per thread.
Replacing the lower level in (4) with the set of constraints of (6)
and applying the reformulation of the kinetic term suggested in (7)
yields the single-level mixed-integer quadratic form of SimulKnock 3.1 | SimulKnock predicts different knockouts
with Michaelis-Menten embedded: than OptKnock with embedded illustrative network
y,cS m ,cS a ,F x eed,σ P c P (cid:3) v bio To show SimulKnock's mode of action compared to sequential optimiza-
s:t: : ð1 (cid:2) y Þ ≤ 1 tion using OptKnock, we constructed an illustrative network (Figure 2).
i
0 ¼ (cid:2)v S (cid:3) M S (cid:3) c bio þ v bio (cid:3) ðc S,Feed (cid:2) c SÞ We performed four optimizations with the illustrative network
0 ¼ v P (cid:3) M P (cid:3) c bio (cid:2) c P (cid:3) v bio embedded: (i) an FBA with maximization of biomass as the objective
v S ¼ v S max σ MM (referred to as wild-type), (ii) an OptKnock prediction, (iii) a sequential
c S ¼ σ M(cid:5)Mðc S þ K S,MMÞ (cid:6) approach using OptKnock (see below), and (iv) SimulKnock. Table 2
v bio ¼ (cid:2)vlower ∘ ðByÞ vupper ∘ ðByÞ v S max σ (cid:3) μ ð8Þ shows the results of the case study.
S (cid:3) v ¼ 0
The sequential approach denotes a two-step procedure. First, Opt-
v ≥ vlower ∘ ðByÞ
Knock is performed. Second, the predicted knockouts are applied to the
v ≤ vupper ∘ ðByÞ
h i
network, and a continuous process optimization is performed. The continu-
ST (cid:3) λ þ Ijnj Ijnj c S (cid:3) μ ¼ c ous process optimization looks like the formulation of SimulKnock but with
v bio ≥ f (cid:3) v b m io ax fixed knockouts, which were determined from OptKnock. Thus, OptKnock
v,μ ≥ 0:
is included in the sequential approach. Still, we added the results of Opt-
Knock for completeness to allow for a direct comparison of functionalities
Similar reformulations also reduce SimulKnock with Monod kinet- with SimulKnock. Michaelis-Menten kinetics were applied in the sequential
ics to an MIQCQP. approach and SimulKnock. The FBA and OptKnock predictions do not
The reformulated programs were implemented using Pyomo.48,49 imply process variables, for example, the substrate or product concentra-
In a preprocessing step, the search space of reaction eliminations in tion, which is also why the kinetics were not applied in OptKnock or FBA.
the metabolic network was reduced. All exchange reactions, diffusive The results indicate that SimulKnock and OptKnock predict dif-
transport reactions and reactions without gene-protein-reaction rule ferent optimal knockouts for one maximum allowable knockout. The
were excluded from potential elimination. Note that users of our reason for this difference is that OptKnock optimizes for the target
open-source code may also decide to exclude transporters and the chemical production, whereas SimulKnock optimizes for space-time
corresponding reactions from elimination, which represents a small yield. Indeed, the product flux v is higher for OptKnock than for P
extension of our preprocessing. The software package COBRApy SimulKnock. The applied kinetics in SimulKnock and the sequential
ver.0.26.050 was used to also exclude blocked reactions and lethal approach force the substrate uptake lower than the maximum allowed
reactions from the search space. Similar to Larhlimi et al.51 and based value. Namely, in the sequential approach, the substrate uptake is set
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 7 -->

ZIEGLER ET AL. 7 of 14
F I G U R E 2 Illustrative network. The grey circles A to G denote metabolites, v and v denote the flux of oxygen and the substrate uptake
O S
reaction, respectively; v and v are the target chemical and biomass flux, respectively. All stoichiometric coefficients are one, except where
P bio
indicated with numbers. For one maximum allowable knockout, the wrenches indicate the knockout prediction of SimulKnock and OptKnock.
T A B L E 2 Results of the case study
Knockout v S v O v bio v P c bio c P STY
with the illustrative network (Figure 2) ((cid:2)) (mmol g(cid:2)1 h(cid:2)1) (g L(cid:2)1) (g L(cid:2)1 h(cid:2)1)
embedded. CDW
Wild-type — 10 3 13 0 — — —
OptKnock B-C 10 3 9.5 3.5 — — —
Sequential B-C 7.8 3 8.4 2.4 8.7 2.5 21.0
SimulKnock F-C 3 3 3 3 9.8 9.8 29.3
Notes: The substrate is glucose, and the maximum substrate flux allowed is set to
vupper ¼ 10 mmol g(cid:2)1 h(cid:2)1; the upper bounds on A-B and A-F are set to 7 and 3 mmol g(cid:2)1 h(cid:2)1,
S CDW CDW
respectively; the maximum oxygen flux allowed is vupper ¼ 3 mmol g(cid:2)1 h(cid:2)1. Michaelis-Menten kinetics
O CDW
were applied in SimulKnock and the sequential approach, with the Michaelis constant
K S,MM ¼ 0:53 mmol L(cid:2)1.42 In the sequential approach, 1. OptKnock, and 2. a process optimization is
performed with embedded knockouts from OptKnock.
Abbreviations: c
bio
, biomass concentration; cP, product concentration; STY, space-time yield; v
S
, substrate
uptake flux; v , oxygen flux; v , growth rate.
O bio
to 8 mmol g(cid:2)1 h(cid:2)1 by the process optimization, whereas OptKnock network includes 1516 genes, resulting in 1877 metabolites and 2712
CDW
predicted it to be 10 mmol g(cid:2)1 h(cid:2)1. In SimulKnock, only the reac- metabolic reactions. The objective was set to maximize the space-
CDW
tions in the upper part of the network, that is, the reactions going via time yield of six target chemicals for a glucose-limited medium.
the metabolites A, F, G, E, and C, are active and used for biomass and Furthermore, to highlight the superiority of the simultaneous
target chemical production. In contrast, in OptKnock and the sequen- strain and process optimization, SimulKnock was compared against
tial approach, the reactions going via B, D, and E are used for target the sequential approach on the space-time yield of the target
chemical production, while the route via F and C produces additional chemical.
biomass. The space-time yield, which is the product of the growth rate
v and the product concentration c , is higher for SimulKnock than
bio P
for the sequential approach. Note that both formulations predict the 3.2.1 | One knockout
same two knockouts, B-C and F-C, and the same space-time yield for
two maximum allowable knockouts. However, this does not generally For one knockout prediction, SimulKnock and the sequential approach
indicate that with more allowed knockouts, the results of OptKnock furnished identical results. The knockout predictions and space-time
and SimulKnock would be similar. Instead, the illustrative network is yields are in the Appendix S1 (cf. Figure S1 and Table S2).
constructed so small that no other options exist.
3.2.2 | Two knockouts
3.2 | SimulKnock can achieve higher space-time
yields than sequential optimization with embedded In this case study, we allowed for two gene knockouts. The compari-
iML1515
son results of Michaelis-Menten and Monod kinetics are plotted in
Figure 3.
To further investigate the computational tractability of the Simul- Note that for E. coli, the growth rate is higher with oxygen than
Knock approach, we chose a genome-scale metabolic model, without. The lower-level optimization problem always activates the
iML1515,41 which describes the metabolism of E. coli. The metabolic oxygen uptake to maximize growth. Hence, in SimulKnock, the oxygen
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 8 -->

(A) (B)
supply must be set by the modeler. We performed runs with and recognizes the trade-off between a higher growth rate and a higher tar-
without an oxygen supply. Figure 3 shows the results where Simul- get chemical flux. It is, therefore, not surprising that the sequential
Knock achieved the higher absolute value. approach predicts a higher target chemical concentration and lower
SimulKnock predicts significantly higher space-time yields for four of biomass concentrations than the SimulKnock approach.
the six considered target chemicals with embedded Michaelis-Menten The different modes of action become even more visible when
kinetics. The difference in the space-time yield from the two approaches comparing the molar product yield on the substrate. We computed the
is due to different reaction knockouts predicted (see Table S3 for refer- yield by dividing the target chemical flux v by the substrate flux v (cf.
P S
ence). For example, SimulKnock targets the 6-phosphogluconolactonase Table S3 for the data). In all cases, the molar product yield was lower
and the acetate reversible transport for higher ethanol space-time yield with SimulKnock than with the sequential approach. At maximum, in the
instead of the ATP synthase and the triose-phosphate isomerase. The case of acetate production, the yield was 45% lower, whereas the space-
most significant difference becomes visible for formate. Instead of the time yield was 2.6 times higher. With the same underlying uptake rate,
phosphoglycerate mutase, SimulKnock predicts the phosphofructokinase the production envelopes of succinate and acetate (Figure 4A,B, respec-
will be knocked out. Even if SimulKnock and the sequential approach do tively) give a detailed picture on product yield.
not predict the same knockouts for fumarate, they reach the same result In both cases of succinate and acetate, the envelope of Simul-
with Michaelis-Menten. Interestingly, the predicted reaction eliminations Knock lies right-hand of the envelope of OptKnock, which was to be
for ethanol and lactate production are equal. The reason for this result is expected. This established form of production envelope, however, is not
the optimistic formulation of SimulKnock: pathways which are competing able to show the mode of action and strength of SimulKnock. Therefore,
are not recognized. we created a new form of production envelope, where space-time yield is
The kinetics also influence the knockout predictions. SimulKnock plotted over biomass growth (Figure 4C,D). We compare SimulKnock
with embedded Michaelis-Menten kinetics suggests blocking acetal- with the sequential approach. It now comes visible that the space-time
dehyde dehydrogenase and D-alanine-D-alanine dipeptidase for suc- yield which is reachable with the mutant created with SimulKnock is
cinate production. With Monod embedded, dytosine deaminase is larger than the one with the sequential approach. Also the optimistic
knocked out instead of the dipeptidase. Interestingly, SimulKnock nature of both formulations comes visible, with both formulations exhibit-
achieves a lower space-time yield for fumarate than the sequential ing a vertical descent in their optimal point.
approach with embedded Monod kinetics.
The sequential formulation maximizes the target chemical concen-
tration at the process level, with the biomass growth rate being used 3.2.3 | Three knockouts
only in the metabolism level problem. Therefore, the targeted reaction
knockouts decrease the growth rate to achieve the maximum target Upon increasing the possible reaction eliminations to three, the Simul-
chemical concentration. In contrast, the SimulKnock formulation Knock formulation with Michaelis-Menten kinetics could not be
)
(
)
(
8 of 14 ZIEGLER ET AL.
F I G U R E 3 Comparison of space-time yield using Michaelis-Menten and Monod kinetics for two reaction eliminations on the genome-scale
metabolic model iML1515.41 Ethanol, succinate, and lactate were produced via anaerobic pathways; acetate, formate, and fumarate were
produced via aerobic pathways. (A) Michaelis-Menten, (B) Monod.
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 9 -->

(A) (B)
(C) (D)
solved within a feasible time limit. Thus, only the Monod kinetics reason for this difference is the different reaction knockouts predicted
results are presented in Figure 5. by the two approaches (cf. Table S4 for data). The knockouts for lac-
Note that, again, we performed runs with and without an oxygen tate and fumarate are similar, often targeting neighboring reactions,
supply. Figure 5 shows the results where SimulKnock achieved the thereby predicting similar yields. When ethanol is considered, two of
higher absolute value, all achieved using aerobic pathways. the three reaction eliminations target the same reactions with Simul-
Acetate and formate space-time yield is increased by about 100% Knock when compared to the sequential approach. When the target
when using SimulKnock, whereas ethanol, succinate, and fumarate chemical is acetate, all three knockouts are different; with formate,
increase marginally, and lactate remains the same. Once again, the two of the three knockouts are different. This observation hints
)
(
)
(
)
(
)
(
ZIEGLER ET AL. 9 of 14
( ) ( )
( ) ( )
F I G U R E 4 Production envelopes for succinate and acetate production with Monod kinetics for the wild type and the mutants (two
knockouts) predicted by SimulKnock and OptKnock/Sequential approach. Succinate (A,C) is produced anaerobically; acetate (B,D) is produced
aerobically. (C,D) represent a new form of production envelope, where space-time yield is plotted against biomass growth rate. The plots are
generated by repeatedly maximizing and minimizing product flux or space-time yield, with a growth rate fixed to a fraction of its maximum. The
points and triangles denote the optimal value of the respective formulation. Note that no optimal value can be given for SimulKnock in (A) and (B),
due to SimulKnock not optimizing for product flux. (A) Succinate, (B) Acetate, (C) Succinate, (D) Acetate.
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 10 -->

significantly at three knockouts, in alignment with the increase in
growth. With the sequential approach, the space-time yield is lowest
for two knockouts and then increases again, decreasing the growth
rate. This interesting behavior stems from the two-step procedure.
Only in the second step are the process conditions optimized, but
they can only influence one of the two factors, namely the product
concentration c . Thus, there is no monotonous behavior with the P
sequential approach. This finding displays the problems often occur-
ring during scale-up when sequentially optimizing the microbial strain
and the process conditions. On the other hand, the acetate case
underpins the potential of SimulKnock.
3.3 | SimulKnock can furnish meaningful knockout
predictions but also exhibits model-experiment
mismatch
In the last case study, we took the experimental study of van Heerden
et al.53 as a test case to elaborate on how far SimulKnock reproduces
their results regarding space-time yield, dilution rate, and knockouts.
We aimed to see whether SimulKnock furnishes experimentally mean-
ingful results. In their experimental study, van Heerden et al.53 pro-
toward the possibility of missing possible knockout strategies with the duced succinic acid from E. coli KJ134 in a continuous fermentation
sequential approach. with two different glucose feed concentrations. We applied Simul-
It is worth noting that the assumption made in this article about Knock with embedded Monod kinetics to the E. coli GEMs iML151541
the biomass reaction being the rate-limiting step has yet to be experi- as well as iEC1349_Crooks54 with three maximum allowable knock-
mentally validated. Therefore, reaction eliminations could, theoreti- outs. While van Heerden et al.53 tested different dilution rates and
cally, target the rate-limiting step on which the Monod kinetic measured the space-time yield for each, SimulKnock predicted the
parameters were fitted. In that case, a new parameter fitting using the optimal space-time yield and the corresponding dilution rate. Figure 7
modified organism would be required. In contrast, the Michaelis- shows the case study results, depicted as the space-time yield over
Menten kinetics do not require parameter refitting due to reaction the dilution rate. Note that, in continuous fermentation, the dilution
eliminations, as the substrate uptake reaction is always active. rate equals the growth rate μ and the biomass flux v .
bio
When we line up space-time yield and growth rate with an In the experimental study, 13 genetic modifications were applied
increasing number of knockouts, we observe different behaviors: For to the organism to reach a maximum space-time yield of around
ethanol, succinate, lactate, and formate, space-time yield and growth 1 g L(cid:2)1 h(cid:2)1 on 20 g L(cid:2)1 glucose feed. SimulKnock predicted a maxi-
rate with SimulKnock stay more or less constant over one to three mum space-time yield of about 4 and 6 g L(cid:2)1 h(cid:2)1 with iML1515 and
knockouts. Exemplary, Figure 6A shows the course for succinate. iEC1349_Crooks, respectively, on 50 g L(cid:2)1. The space-time yields
In the sequential approach, space-time yield decreases with an were reached with three knockouts. The reactions to be eliminated,
increasing number of knockouts, as depicted at two gene knockouts predicted with iML1515 embedded, were acetate kinase, ATP
in Figure 6A. This decrease in space-time yield comes due to the synthase, and fumarase. With iEC1349_Crooks embedded, the pre-
mathematical structure of OptKnock. In OptKnock, high product dicted reaction eliminations were phosphotransacetylase, ATP
yields are achieved at the expense of reduced growth (cf. Table S4 for synthase, and succinyl-CoA synthetase. Among them, acetate kinase
data). In turn, space-time yield (equals product concentration times and phosphotransacetylase were also eliminated in the experimental
growth rate) is linearly dependent on the growth rate. The figure strain. Hence, SimulKnock proves to predict experimentally meaning-
depicts the aerobic pathway for three gene knockouts, following our ful results. However, the figure reveals a substantial model-
decision to show the results for the highest SimulKnock space-time experiment mismatch. Especially the results of iEC1349_Crooks are
yield. Hence, the fermentation conditions change compared to the higher than any experimental value. In iEC1349_Crooks, the high
anaerobic conditions that apply for one and two gene knockouts. growth rate might result from the biomass function difference. For
While the space-time yield of the sequential approach would decline illustration, for an FBA with a glucose limitation of 10 mmol g(cid:2)1 h(cid:2)1,
CDW
for anaerobic conditions (not shown in the figure), it reaches similar iML1515 has a growth rate of 0:87 h(cid:2)1, whereas iEC1349_Crooks has
results as SimulKnock for aerobic conditions. a growth rate of 1:02 h(cid:2)1. The mismatch in space-time yield that
Acetate and fumarate exhibit a different behavior, as depicted in comes visible with both metabolic networks might result from Simul-
an example in Figure 6B. With SimulKnock, the space-time yield rises Knock not considering inhibition and repression effects and being
)
(
10 of 14 ZIEGLER ET AL.
F I G U R E 5 Space-time yield using Monod kinetics for three
reaction eliminations on the genome-scale metabolic model
iML1515.41 All six target chemicals were produced via aerobic
pathways.
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 11 -->

(A) (B)
thereby overcoming current scale-up difficulties. SimulKnock is a bile-
vel optimization formulation, which we transformed into a single-level
mixed-integer nonlinear optimization program and solved globally for
an illustrative example network as well as for the E. coli GEM
iML1515.41 We applied Monod or Michaelis-Menten kinetics to con-
nect the process level to the cellular level in SimulKnock. SimulKnock
with applied Monod kinetics showed similar results as Michaelis-
Menten kinetics, with Monod being less computationally intensive.
SimulKnock predicted different knockouts than OptKnock.12 Also, the
space-time yield was significantly higher with SimulKnock compared
to a sequential approach of OptKnock plus process optimization for
aerobic and anaerobic conditions. Compared to experimental data,53
SimulKnock indicated that higher space-time yields could be achieved
with fewer knockouts. SimulKnock is readily applicable to different
strains by exchanging the metabolic network and to different target
products measurable in a fermenter, represented as exchange reac-
tions in the respective metabolic network.
The computations for SimulKnock with embedded GEM were
performed on a high-performance computing cluster. A decrease in
overly optimistic by not considering byproduct formation unless the the computation demand and reduction of computation time could be
byproduct formation hinders biomass formation. The mismatch could achieved by applying further network reduction methods57 or by con-
be reduced by including experimental flux data of the organism in sidering essential genes.58 Adaptation of the OptForce16 framework
question, for example, from Fischer et al.55 for E. coli, or by using addi- for SimulKnock could also lead to speed-up and a higher number of
tional information from a protein allocation model.56 In both cases, possible knockouts, as Chowdhury et al.59 have already shown signifi-
the bounds of specific fluxes would be fixed in a preprocessing step, cantly lower computation time of OptForce compared to OptKnock
which can readily be done in the SimulKnock code. These refinements with increasing number of interventions in the metabolic network.
of the metabolic network and adaptations at the cellular level are Future work should consider that kinetics would have to be adjusted
interesting in case of application but were not in the scope of this when knockouts are applied to the organism because Michaelis-
article. Menten, describing the substrate uptake, and Monod, describing the
growth behavior, are affected by genetic modifications. Especially for
altered growth behavior, the update of the kinetics should be
4 | C O N CL U S I O N considered.
Our results of the case study with experimental data indicated
We presented SimulKnock, an optimization formulation combining that SimulKnock furnishes overly optimistic results. Furthermore,
continuous fermentation optimization with strain optimization via SimulKnock does not account for competing pathways, as came clear
gene knockouts. Such an optimization formulation allows us to con- when SimulKnock predicted the same reaction eliminations for etha-
sider industrial fermentation conditions already in the strain design, nol and lactate production. The conversion to a robust optimization
)
(
)
(
)
(
)
(
F I G U R E 6 Change of space-
time yield and growth rate over
the number of knockouts for
iML151541 with embedded
Monod kinetics. Succinate (A) was
produced anaerobically for one
and two knockouts and
aerobically for three knockouts.
Acetate (B) was produced via an
aerobic pathway. STY: space-time
yield, Seq. Appr.: Sequential
approach. (A) Succinate;
(B) Acetate.
)
(
ZIEGLER ET AL. 11 of 14
d
d
( )
F I G U R E 7 Comparison of experimental laboratory data for
succinic acid production using E. coli KJ13453 with results from
SimulKnock, based on the metabolic networks iML151541 and
iEC1349_Crooks.54 Two glucose feed concentrations were studied:
20 g L(cid:2)1 and 50 g L(cid:2)1.
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 12 -->

12 of 14 ZIEGLER ET AL.
formulation, as suggested in RobustKnock13 and OptForce,16 could writing – review and editing; conceptualization. Alexander Mitsos:
tackle these two observations. Moreover, experimental flux data (for conceptualization; funding acquisition; supervision; methodology,
E. coli, see Pharkya et al.15 and Fischer et al.55) could reduce the writing – review and editing.
model-experiment mismatch by fixing the bounds of specific fluxes in
a preprocessing step. With available experimental data, SimulKnock ACKNOWLEDGMENTS
could also be integrated in the Design section of a Design-Build-Test- This project was funded by the Deutsche Forschungsgemeinschaft
Learn pipeline, as it has already been suggested for OptKnock.60,61 An (DFG, German Research Foundation) under Germany's Excellence
interesting future study could also include determining the complete Strategy – Cluster of Excellence 2186 “The Fuel Science Center” – ID:
knockout set of SimulKnock by iteratively solving SimulKnock and 390919832. This project benefited from the work of Clemens Kortmann,
excluding the previously found solution from the search space of the who improved the modularity and the user-friendliness of our git reposi-
next iteration. In this scope, a comparison with OptKnock appears of tory. Computations were performed with computing resources granted
interest, for example, to identify the number of iterations needed, by RWTH Aachen University under project thes1376. Open Access fund-
when such procedure is applied to OptKnock, to gain the same solu- ing enabled and organized by Projekt DEAL.
tion as suggested by SimulKnock in the first place.
To make a more accurate prediction, SimulKnock could be CONFLICTS OF INTEREST STATEMENT
extended both at the process level and at the cellular level, for exam- No conflicts to declare.
ple, by more elaborate microbial formulations,2,8,9 as depicted by Opt-
Knock12 and its extensions.62,63 These formulations include a DATA AVAILABILITY STATEMENT
reference flux distribution, which could be furnished using a protein The implementation of the SimulKnock approach, the data preproces-
allocation model56 or experimental in vivo flux data.64 More elaborate sing, and the interface with the solver Gurobi are openly available in
microbial formulations or an adapted OptForce framework16 could our GitLab repository “SimulKnock: Simultaneous design of fermenta-
also tackle the current limitation of SimulKnock to growth-coupled tion and microbe” at https://git.rwth-aachen.de/avt-svt/public/
production, which is due to the maximization of growth in the cellular simulknock. Data from the article's figures are tabulated in the
level. The extension could also comprise other genetic modifications, Appendix S2.
that is, gene insertion14 and regulation,15,16 other compounds, for
example, oxygen, as well as other process operation modes, for exam-
ORCID
ple, continuous mode with cell retention, batch, and fed-batch. The
Marc-Daniel Stumm https://orcid.org/0009-0000-7464-4122
three key metrics for an efficient, economic fermentation are yield,
Alexander Mitsos https://orcid.org/0000-0003-0335-6566
titer, and productivity, that is, space-time yield. Optimizing these
three factors results in optimal substrate consumption, low down-
REFERENCES
stream separation effort, and optimal fermentation reactor size,
1. Clomburg JM, Crumbley AM, Gonzalez R. Industrial biomanufacturing:
respectively. Yield is maximized by OptKnock,12 and SimulKnock max- the future of chemical production. Science. 2017;355:aag0804.
imizes space-time yield. With yield and space-time yield being con- 2. Landon S, Rees-Garbutt J, Marucci L, Grierson C. Genome-driven cell
engineering review: in vivo and in silico metabolic and genome engi-
flicting objectives, our results depicted that OptKnock outperforms
neering. Essays Biochem. 2019;63:267-284.
SimulKnock with respect to yield, and SimulKnock outperforms Opt-
3. Maia P, Rocha M, Rocha I. In silico constraint-based strain optimiza-
Knock with respect to space-time yield. An idea to gain the full picture tion methods: the quest for optimal cell factories. Microbiol Mol Biol
would be to extend SimulKnock to a multi-objective optimization, tar- Rev. 2016;80:45-67.
geting all three key metrics at the same time. 4. Savinell JM, Palsson BØ. Network analysis of intermediary metabo-
lism using linear optimization. I. Development of mathematical formal-
ism. J Theor Biol. 1992;154:421-454.
AUTHOR CONTRIBUTIONS 5. Watson MR. A discrete model of bacterial metabolism. Comput Appl
ALZ designed the SimulKnock formulation, the reformulation, the Biosci. 1986;2:23-27.
implementation, and the case studies. MS performed the formulation 6. Orth JD, Thiele I, Palsson BØ. What is flux balance analysis? Nat Bio-
technol. 2010;28:245-248.
setup, the reformulation, the implementation, and the case studies
7. Schuetz R, Zamboni N, Zampieri M, Heinemann M, Sauer U. Multidi-
under the supervision of ALZ and AsMa. ALZ and MS visualized the
mensional optimality of microbial metabolism. Science. 2012;336:
data. ALZ, MS, and AsMa analyzed and discussed the data. ALZ and 601-604.
AsMa wrote the manuscript draft. AlMi and LMB had the initial idea 8. Segrè D, Vitkup D, Church GM. Analysis of optimality in natural and
perturbed metabolic networks. Proc Natl Acad Sci U S A. 2002;99:
of SimulKnock, discussed the data, and reviewed the draft. AlMi
15112-15117.
secured funding. All authors read and approved the final manuscript. 9. Brochado AR, Andrejev S, Maranas CD, Patil KR. Impact of stoichiom-
Anita L. Ziegler: conceptualization; methodology; software; valida- etry representation on simulation of genotype-phenotype relation-
tion; investigation; writing – original draft; writing – review and edit- ships in metabolic networks. PLoS Comput Biol. 2012;8:e1002758.
10. Shlomi T, Berkman O, Ruppin E. Regulatory on/off minimization of
ing; visualization; project administration. Ashutosh Manchanda:
metabolic flux changes after genetic perturbations. Proc Natl Acad Sci
methodology; software; investigation; writing – review and editing.
U S A. 2005;102:7695-7700.
Marc-Daniel Stumm: writing – review and editing; methodology; soft- 11. Valderrama-Gomez MA, Kreitmayer D, Wolf S, Marin-Sanguino A,
ware; validation; investigation; visualization. Lars M. Blank: Kremling A. Application of theoretical methods to increase succinate
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 13 -->

ZIEGLER ET AL. 13 of 14
production in engineered strains. Bioprocess Biosyst Eng. 2017;40: 33. Konstantinos D, Antonis K. Simultaneous synthesis of metabolic and
479-497. process engineering for the production of Muconic acid. Comput Aid
12. Burgard AP, Pharkya P, Maranas CD. Optknock: a bilevel program- Chem Eng. 2022;51:889-894.
ming framework for identifying gene knockout strategies for micro- 34. Mitsos A, Chachuat B, Barton PI. Towards global bilevel dynamic opti-
bial strain optimization. Biotechnol Bioeng. 2003;84:647-657. mization. J Global Optim. 2009;45:63-93.
13. Tepper N, Shlomi T. Predicting metabolic engineering knockout strat- 35. Stephanopoulos G, Aristidou AA, Nielsen J. Metabolic Engineering:
egies for chemical production: accounting for competing pathways. Principles and Methodologies. Academic Press[nachdr.] ed; 1998.
Bioinformatics. 2010;26:536-543. 36. Gordeeva EL, Ravichev LV, Borodkin AG, Gordeeva YL. Mathematical
14. Pharkya P, Burgard AP, Maranas CD. OptStrain: a computational Modeling of a biotechnological continuous fermentation process for
framework for redesign of microbial production systems. Genome Res. lactic acid production: a review. Theor Found Chem Eng. 2021;55:
2004;14:2367-2376. 1192-1203.
15. Pharkya P, Maranas CD. An optimization framework for identifying 37. Sinner P, Kager J, Daume S, Herwig C. Model-based analysis and opti-
reaction activation/inhibition or elimination candidates for overpro- misation of a continuous corynebacterium glutamicum bioprocess uti-
duction in microbial systems. Metab Eng. 2006;8:1-13. lizing lignocellulosic waste. IFAC-PapersOnLine. 2019;52:181-186.
16. Ranganathan S, Suthers PF, Maranas CD. OptForce: an optimization 38. Bongartz D, Mitsos A. Deterministic global flowsheet optimization:
procedure for identifying all genetic manipulations leading to targeted between equation–oriented and sequential–modular methods. AIChE
overproductions. PLoS Comput Biol. 2010;6:e1000744. J. 2019;65:1022-1034.
17. Kim J, Reed JL, Maravelias CT. Large-scale bi-level strain design 39. Najman J, Bongartz D, Mitsos A. Linearization of McCormick relaxa-
approaches and mixed-integer programming solution techniques. tions and hybridization with the auxiliary variable method. J Global
PLoS One. 2011;6:e24162. Optim. 2021;80:731-756.
18. Biegler LT. Systematic Methods of Chemical Process Design. Prentice 40. Wick LM, Quadroni M, Egli T. Short- and long-term changes in prote-
Hall International Series in the Physical and Chemical Engineering sci- ome composition and kinetic properties in a culture of Escherichia
ences. Prentice Hall PTR; 1997. coli during transition from glucose-excess to glucose-limited growth
19. Chmiel H, Takors R, Weuster-Botz D, eds. Bioprozesstechnik. Springer conditions in continuous culture and vice versa. Environ Microbiol.
Spektrum4. auflage ed; 2018. 2001;3:588-599.
20. Villadsen J, Nielsen J, Lidén G. Bioreaction Engineering Principles. 3rd 41. Monk JM, Lloyd CJ, Brunk E, et al. iML1515, a knowledgebase that
ed. Springer Science+Business Media; 2011. computes Escherichia coli traits. Nat Biotechnol. 2017;35:904-908.
21. Edgar TF, Himmelblau DM, Lasdon LS. Optimization of Chemical Pro- 42. Meadows AL, Karnik R, Lam H, Forestell S, Snedecor B. Application of
cesses. McGraw-Hill Chemical Engineering Series. 2nd ed. McGraw- dynamic flux balance analysis to an industrial Escherichia coli fermen-
Hill; 2001. tation. Metab Eng. 2010;12:150-160.
22. Gordeeva YL, Gordeev LS. Optimization of continuous microbiologi- 43. Djelassi H, Mitsos A. libALE – a library for algebraic-logical expression
cal synthesis processes with nonlinear microbial growth kinetics. trees. 2019.
Theor Found Chem Eng. 2015;49:829-835. 44. Jungen D, Zingler A, Djelassi H, Mitsos A. libDIPS - a library for
23. Wehrs M, Tanjore D, Eng T, Lievense J, Pray TR, Mukhopadhyay A. discretization-based semi-infinite programming solvers. 2023.
Engineering robust production microbes for large-scale cultivation. 45. Orth JD, Fleming RMT, Palsson BØ. Reconstruction and use of micro-
Trends Microbiol. 2019;27:524-537. bial metabolic networks: the core Escherichia coli metabolic model as
24. Olsson L, Rugbjerg P, Torello Pianale L, Trivellin C. Robustness: linking an educational guide. EcoSal Plus. 2010;4:1-48.
strain design to viable bioprocesses. Trends Biotechnol. 2022;40: 46. Mitsos A, Lemonidis P, Barton PI. Global solution of bilevel programs
918-931. with a nonconvex inner program. J Global Optim. 2008;42:475-513.
25. Richelle A, David B, Demaegd D, et al. Towards a widespread adop- 47. Gurobi Optimization, LLC. Gurobi Optimizer Reference Manual. Gurobi
tion of metabolic modeling tools in biopharmaceutical industry: a pro- Optimization, LLC; 2023.
cess systems biology engineering perspective. NPJ Syst Biol Appl. 48. Bynum ML, Hackebeil GA, Hart WE, et al. Pyomo–Optimization Model-
2020;6:6. ing in Python. Vol 67. 3rd ed. Springer Science & Business; 2021.
26. Lapin A, Müller D, Reuss M. Dynamic behavior of microbial popula- 49. Hart WE, Watson J-P, Woodruff DL. Pyomo: modeling and solving
tions in stirred bioreactors simulated with Euler(cid:2)Lagrange methods: mathematical programs in python. Math Program Comput. 2011;3:
traveling along the lifelines of single cells. Ind Eng Chem Res. 2004;43: 219-260.
4647-4656. 50. Ebrahim A, Lerman JA, Palsson BØ, Hyduke DR. COBRApy:
27. Mahadevan R, Edwards JS, Doyle FJ. Dynamic flux balance analysis COnstraints-based reconstruction and analysis for python. BMC Syst
of diauxic growth in Escherichia coli. Biophys J. 2002;83:1331-1340. Biol. 2013;7:74.
28. Oliveira RD, Guedes MN, Matias J, Le Roux GAC. Nonlinear predic- 51. Larhlimi A, David L, Selbig J, Bockmayr A. F2C2: a fast tool for the
tive control of a bioreactor by surrogate model approximation of flux computation of flux coupling in genome-scale metabolic networks.
balance analysis. Ind Eng Chem Res. 2021;60:14464-14475. BMC Bioinformatics. 2012;13:57.
29. Zhuang K, Yang L, Cluett WR, Mahadevan R. Dynamic strain scanning 52. Burgard AP, Nikolaev EV, Schilling CH, Maranas CD. Flux coupling
optimization: an efficient strain design strategy for balanced yield, analysis of genome-scale metabolic network reconstructions. Genome
titer, and productivity. DySScO strategy for strain design. BMC Bio- Res. 2004;14:301-312.
technol. 2013;13:8. 53. van Heerden CD, Nicol W. Continuous and batch cultures of
30. Ploch T, Zhao X, Hüser J, et al. Multiscale dynamic modeling and sim- Escherichia coli KJ134 for succinic acid fermentation: metabolic flux
ulation of a biorefinery. Biotechnol Bioeng. 2019;116:2561-2574. distributions and production characteristics. Microb Cell Fact. 2013;
31. Jabarivelisdeh B, Waldherr S. Optimization of bioprocess productivity 12:80.
based on metabolic-genetic network models with bilevel dynamic 54. Monk JM, Koza A, Campodonico MA, et al. Multi-omics quantification
programming. Biotechnol Bioeng. 2018;115:1829-1841. of species variation of Escherichia coli links molecular features with
32. Tafur Rangel AE, Oviedo AG, Mojica FC, Gómez JM, Gónzalez strain phenotypes. Cell Syst. 2016;3:238-251.e12.
Barrios AF. Development of an integrating systems metabolic engi- 55. Fischer E, Zamboni N, Sauer U. High-throughput metabolic flux analy-
neering and bioprocess modeling approach for rational strain sis based on gas chromatography-mass spectrometry derived 13C
improvement. Biochem Eng J. 2022;178:108268. constraints. Anal Biochem. 2004;325:308-316.
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License

---

<!-- Page 14 -->

14 of 14 ZIEGLER ET AL.
56. Alter TB, Blank LM, Ebert BE. Proteome regulation patterns deter- 63. Kim J, Reed JL. OptORF: optimal metabolic and regulatory perturba-
mine Escherichia coli wild-type and mutant phenotypes. mSystems. tions for metabolic engineering of microbial strains. BMC Syst Biol.
2021;6:e00625-20. 2010;4:53.
57. Erdrich P, Steuer R, Klamt S. An algorithm for the reduction of 64. Kuepfer L, Sauer U, Blank LM. Metabolic functions of duplicate genes
genome-scale metabolic network models to meaningful core models. in Saccharomyces cerevisiae. Genome Res. 2005;15:1421-1430.
BMC Syst Biol. 2015;9:48.
58. Goodall ECA, Robinson A, Johnston IG, et al. The essential genome of
Escherichia coli K-12. MBio. 2018;9:e02096-17. SUPPORTING INFORMATION
59. Chowdhury A, Zomorrodi AR, Maranas CD. Bilevel optimization tech-
Additional supporting information can be found online in the Support-
niques in computational strain design. Comput Chem Eng. 2015;72:
ing Information section at the end of this article.
363-372.
60. Liu R, Bassalo MC, Zeitoun RI, Gill RT. Genome scale engineering
techniques for metabolic engineering. Metab Eng. 2015;32:
How to cite this article: Ziegler AL, Manchanda A,
143-154.
61. Carbonell P, Currin A, Jervis AJ, et al. Bioinformatics for the synthetic Stumm M-D, Blank LM, Mitsos A. Simultaneous design of
biology of natural products: integrating across the design-build-test fermentation and microbe. AIChE J. 2024;70(9):e18501.
cycle. Nat Prod Rep. 2016;33:925-932.
doi:10.1002/aic.18501
62. Apaydin M, Xu L, Zeng B, Qian X. Robust mutant strain design by pes-
simistic optimization. BMC Genomics. 2017;18:677.
15475905,
2024,
9,
Downloaded
from
https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.18501,
Wiley
Online
Library
on
[21/07/2026].
See
the
Terms
and
Conditions
(https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
Online
Library
for
rules
of
use;
OA
articles
are
governed
by
the
applicable
Creative
Commons
License
