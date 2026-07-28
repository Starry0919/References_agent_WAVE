<!-- Page 1 -->

Article https://doi.org/10.1038/s41467-023-40380-0
A neural-mechanistic hybrid approach
improving the predictive power of genomescale metabolic models
Received: 1 December 2022 Léon Faure1, Bastien Mollet2,3, Wolfram Liebermeister 4 &
Jean-Loup Faulon 1,5
Accepted: 19 July 2023
Constraint-based metabolic models have been used for decades to predict the
Check for updates phenotype of microorganisms in different environments. However, quantitative predictions are limited unless labor-intensive measurements of media
uptake fluxes are performed. We show how hybrid neural-mechanistic models
can serve as an architecture for machine learning providing a way to improve
phenotype predictions. We illustrate our hybrid models with growth rate
predictions of Escherichia coli and Pseudomonas putida grown in different
media and with phenotype predictions of gene knocked-out Escherichia coli
mutants. Our neural-mechanistic models systematically outperform
constraint-based models and require training set sizes orders of magnitude
smaller than classical machine learning methods. Our hybrid approach opens a
doorway to enhancing constraint-based modeling: instead of constraining
mechanistic models with additional experimental measurements, our hybrid
models grasp the power of machine learning while fulfilling mechanistic
constrains, thus saving time and resources in typical systems biology or biological engineering projects.
In this study, we present an approach that combines machine learning this foot step, one may wonder if in the future we will be able to use
(ML) and mechanistic modeling (MM) to improve the performance of ML to accurately model whole-cell behaviors. The curse of
constraint-based modeling (CBM) on genome-scale metabolic models dimensionality2, i.e. the fact that fitting many parameters may require
(GEMs). Our hybrid MM-ML models are applied to common tasks in prohibitively large data sets, is perhaps the biggest hurdle that presystems biology and metabolic engineering, such as predicting quali- vents using ML to build cell models. Obviously, cells are far more
tative and quantitative phenotypes of organisms grown in various complex than single proteins and since the amount of data needed
media or subjected to gene knock-outs (KOs). Our approach leverages for ML training grows exponentially with the dimensionality2, as of
recent advances in ML, MM, and their integration, which we briefly today, ML methods have not been used alone to model cellular
review next. dynamics at a genome scale.
The increasing amounts of data available for biological research For the past decades, MM methods have been developed to
bring the challenge of data integration with ML to accelerate the simulate whole-cell dynamics (cf. Thornburg et al.3 for one of the latest
discovery process. The most compelling achievement within this models). These models encompass metabolism, signal transduction,
grand challenge is protein folding, recently cracked by AlphaFold1, as well as gene and RNA regulation and expression. Cellular dynamics
which in the last CASP14 competition predicted structures with a being tremendously complex, MM methods are generally based on
precision similar to structures determined experimentally. Following strong assumptions and oversimplifications. Ultimately, they suffer
1MICALIS Institute, INRAE, AgroParisTech, University of Paris-Saclay, 78350 Jouy-en-Josas, France. 2Ecole Normale Supérieure of Lyon, 69342 Lyon, France.
3UMR MIA, INRAE, AgroParisTech, University of Paris-Saclay, 91120 Palaiseau, France. 4MaIAGE, INRAE, University of Paris-Saclay, 78350 Jouy-en-
Josas, France. 5Manchester Institute of Biotechnology, University of Manchester, Manchester M1 7DN, UK. e-mail: Jean-loup.Faulon@inrae.fr
Nature Communications | ( 2023)1 4:4669 1
;,:)(0987654321 ;,:)(0987654321

---

<!-- Page 2 -->

Article https://doi.org/10.1038/s41467-023-40380-0
from a lack of capacities to make predictions beyond the assumptions training and therefore increasing MM predictability, and they enable
and the data used to build them. ML methods to overcome the dimensionality curse by being trained on
Flux balance analysis (FBA) is the main MM approach to study the smaller datasets because of the constraints brought by MM.
relationship between nutrient uptake and the metabolic phenotype In the current paper we propose a MM-ML hybrid approach in
(i.e., the metabolic fluxes distribution) of a given organism, e.g., E. coli, which FBA is embedded within artificial neural networks (ANNs). Our
with a model iteratively refined over the past 30 years or so4. FBA approach bridges the gap between ML and FBA by computing steadysearches for a metabolic phenotype at steady state, i.e., a phenotype state metabolic phenotypes with different methods that can be
that is constant in time and in which all compounds are mass-balanced. embedded with ML. All these methods rely on custom loss functions
Usually, such a steady state is assumed to be reached in the mid- surrogating the FBA constraints. By doing so, our AMNs are mechanexponential growth phase. The search for a steady state happens in the istic models, determined by the stoichiometry and other FBA conspace of possible solutions that satisfies the constraints of the meta- straints, and also ML models, as they are used as a learning
bolic model, i.e., the mass-balance constraints according to the stoi- architecture.
chiometric matrix as well as upper and lower bounds for each flux in We showcase our AMNs with a critical limitation of classical FBA
the distribution. The steady state search is performed with an optim- that impede quantitative phenotype predictions, the conversion of
ality principle, with one principal objective (usually the biomass pro- medium composition to medium uptake fluxes5. Indeed, realistic and
duction flux) and possibly secondary objectives (e.g., minimize the condition-dependent bounds on medium uptake fluxes are critical for
sum of fluxes in parsimonious FBA, or the flux of a metabolite of growth rate and other fluxes computations, but there is no simple
interest). As we shall see later and as discussed in O’Brien et al.5, FBA conversion from extracellular concentrations, i.e., the controlled
suffers from making accurate quantitative phenotype predictions. experimental setting, to such bounds on uptake fluxes. With AMNs, a
The MM and ML approaches are based on two seemingly opposed neural pre-processing layer aims to capture, effectively, all effects of
paradigms. While the former is aimed at understanding biological transporter kinetics and resource allocation in a particular experiphenomena with physical and biochemical details, it has difficulties mental setting, predicting the adequate input for a metabolic model to
handling complex systems; the latter can accurately predict the out- give the most accurate steady-state phenotype prediction possible.
comes of complex biological processes even without an under- Consequently, AMNs provide a new paradigm for phenotype predicstanding of the underlying mechanisms, but require large training sets. tion: instead of relying on a constrained optimization principle per-
The pros of one are the cons of the other, suggesting the approaches formed for each condition (as in classical FBA), we use a learning
should be coupled. In particular, MMs may be used to tackle the procedure on a set of example flux distributions that attempts to
dimensionality curse of ML methods. For instance, one can use MMs to generalize the best model for accurately predicting the metabolic
extend experimental datasets with in silico data, increasing the train- phenotype of an organism in different conditions. As shown in the
ing set sizes for ML. However, with that strategy, if the model is inac- results section, the AMN pre-processing layer can also capture metacurate, ML will be trained on erroneous data. One can also embed MMs bolic enzyme regulation and in particular predict the effect of gene
within the ML process, in this strategy, named hybrid-modeling, ML KOs on phenotype.
and MM are trained together and the model parameters can be estimated through training, increasing the model predictive capacities. To Results
improve FBA phenotype predictions, ML approaches have been used Overview of AMN hybrid models
to couple experimental data with FBA. Among published approaches, When making predictions using FBA, one typically sets bounds for
one can cite Plaimas et al.6 where ML is used after FBA as a post-process medium uptake fluxes, V , to simulate environmental conditions for
in
to classify enzyme essentiality. Similarly, Schinn et al.7 used ML as a the GEM of an organism (Fig. 1a). Each condition is then solved indepost-process to predict amino acid concentrations. Freischem et al.8 pendently from each other by a linear program (LP), usually making
computed a mass flow graph running FBA on the E. coli model iML15159 use of a Simplex solver. In most cases, one sets the LP’s objective to
and used it with a training set of measured growth rates on E. coli gene maximize the biomass production rate (i.e., the growth rate), under the
KO mutants. Several ML methods were then utilized in a post-process metabolic model constraints (i.e., flux boundary and stoichiometric
to classify genes as essential vs. non-essential. As reviewed by Sahu constraints). FBA computes the resulting steady-state fluxes, V , for
out
et al.10, ML has also been used to preprocess data and extract features all the reactions of the metabolic network, which we use later in our
prior to running FBA. For instance, data obtained from several omics reference “FBA-simulated data”, for the benchmarking of the hybrid
methods can be fed to FBA, after processing multi-omics data via models developed in this study. While FBA is computationally efficient
ML11–13. and easy to use through libraries like Cobrapy19, FBA cannot directly be
In all these previous studies, and as discussed in Sahu et al.10, the embedded within ML methods, like neural networks, because grainterplay between FBA and ML still shows a gap: some approaches use dients cannot be backpropagated through the Simplex solver.
ML results as input for FBA, others use FBA results as input for ML, but To enable the development of hybrid models and gradient backnone of them embed FBA into ML, as we do in this study with the propagation, we developed three alternative MM methods (Wt-solver,
artificial metabolic network (AMN) hybrid models. LP-solver and QP-solver) that replace the Simplex solver while produ-
The main issue with hybrid modeling is the difficulty of making cing the same results (Fig. 1b). The three solvers, further described in
MM amenable to training. Overcoming this difficulty, solutions have the next subsection, take as input any initial flux vector that respect
recently been proposed under different names in biology for signaling flux boundary constraints.
pathways and gene-regulatory networks (Knowledge Primed Neural We next used the MM models as a component of AMN hybrid
Network14, Biologically-Informed Neural Networks15) with recent solu- models that can directly learn from sets of flux distributions (Fig. 1c).
tions based on recurrent neural networks (RNNs)16. Hybrid models These flux distributions used as learning references (i.e., training sets)
have also been developed in physics to solve partial differential are either produced through FBA simulations or acquired experiequations, such as Physics Informed Neural Network17 (PINN), available mentally. The AMN model comprises a trainable neural layer followed
in open-source repositories like SciML.ai18. The goal of these emerging by a mechanistic layer (composed of Wt-solver, LP-solver or QP-solhybrid modeling solutions is to generate models that comply well with ver). The purpose of the neural layer is to compute an initial value, V0,
observations or experimental results via ML, but that also use for the flux distribution to limit the number of iterations of the
mechanistic insights from MM. The advantages of hybrid models are mechanistic layer. The initial flux distribution is computed from
two-fold: they can be used to parametrize MM methods through direct medium uptake flux bounds, V , when the training set has been
in
Nature Communications | ( 2023)1 4:4669 2

---

<!-- Page 3 -->

Article https://doi.org/10.1038/s41467-023-40380-0
a b c d
Classical FBA Mechanistic Layer AMN AMN-Reservoir
surrogating FBA
Reference Reference Reference Reference
V 0 : initial flux values FBA-simulated or Experimental Experimental and FBA-simulated
respecting Vin bounds data data data data
for different media
bounds on medium medium
uptake fluxes composition composition
Vin : bounds on uptake fluxes Vin Cmed Cmed
Maximize
growt u h n r d a e te r S s im ol p ve le r x V Wt-solver U w p h d il a e t e re a s l p l e fl c u t x in e g s Neural layer T ex ra p i e n r e im d e o n n t al
constraints LP-solver mechanistic Neural layer data
QP-solver constraints
V
in
V 0
Vout : steady-state solution
for all fluxes Neural layer
Mechanistic Layer
AMN-
V 0 Reservoir
V fo o r u t a : l l s f t l e u a xe d s y - a s n ta d t e a l s l o m lu e t d io ia n V out Mechanistic Layer F P B re A t - r s d a i a i m n ta e u d la o te n d
Reference Custom Loss V
FBA-simulated out
data Fit reference fluxes
and mechanistic
constraints Custom Loss
Fig. 1 | Computing and learning frameworks for FBA, alternative mechanistic experimental data. The input is then passed to a trainable neural layer, predicting
models, AMN, and AMN-Reservoir. a Computing framework for classical FBA. The an initial vector, V0, for the mechanistic layer (a MM method of b). In turn, the
process is repeated for each medium, computing the corresponding steady state mechanistic layer computes the final output of the model, V . The training is
out
fluxes. Blue circles represent different bounds on metabolites uptake fluxes and based on a custom loss function (cf. “Methods”) ensuring the reference fluxes are
each red circle represents a flux value at steady-state. b Computing framework for fitted (i.e., Vout matches simulated or measured fluxes) and that the mechanistic
MM methods surrogating FBA. The methods can handle multiple growth media at constraints (on flux bounds and stoichiometry) are respected. d Learning frameonce. Disregarding the solver (Wt, LP and QP), the MM layer takes as input an work for an AMN-Reservoir. The first step is to train an AMN on FBA-simulated data
arbitrary initial flux vector, V0, respecting uptake flux bounds for different media, (as in c), after which parameters of this AMN are frozen. This AMN model, which
and computes all steady-state fluxes values (Vout) through an iterative process. purpose is to surrogate FBA, is named non-trainable AMN-Reservoir. In the second
c Learning framework for AMN hybrid models. The input (for multiple growth step, a neural layer is added prior to V taking as input media compositions, C ,
in med
media) can be either a set of bounds on uptake fluxes (V ), when using simulation and learning the relationship between the compositions and bounds on
in
data (generated as in a), or a set of media compositions, Cmed, when using uptake fluxes.
generated through FBA simulations, or medium compositions, C , Alternative mechanistic models to surrogate FBA
med
for experimental training sets. For all AMNs, the training of the neural Let us first recall that the methods described in this subsection are
layer is based on the error computation between the predicted fluxes, mechanistic models (MMs) that replace the Simplex-solver used in FBA
V , and the reference fluxes, as well as on the respect of mechanistic and allow for gradient backpropagation, but without any learning
out
constraints. It is important to point out that AMNs attempt to learn a procedure performed. As far as medium uptake fluxes are concerned,
relationship between V (or C ) and the steady-state metabolic we consider in the following two cases: (1) when exact bound values
in med
phenotype, generalizing this relationship for a set of conditions and (EB) for medium uptake fluxes are provided, and (2) when only upper
not just only one as in FBA. In the upcoming subsections, Fig. 2 pre- bound values (UB) for medium uptake fluxes are given.
sents results for FBA-simulated training sets and Figs. 3 and 4 results Our first method (Wt-solver), inspired by previous work on sigfor experimental training sets. naling networks16, recursively computes M, the vector of metabolite
Finally, we developed a non-trainable AMN-Reservoir to showcase production fluxes, and V, the vector of all reaction fluxes (cf. “Wthow the predictive power of classical FBA can be improved (Fig. 1d). solver” in “Methods” and in Supplementary Information for further
This architecture is based on a two-step learning process with the details). The vectors M and V are iteratively updated using matrices
specific goal of finding the best bounds on uptake fluxes for FBA, by derived from the metabolic network stoichiometric matrix S and from
extracting V after training. Indeed, once the AMN has been trained on a weight matrix, W , representing consensual flux branching ratios
in r
adequate FBA-simulated data, we can fix its parameters, resulting in a found in example flux distributions (i.e., reference FBA-simulated data
gradient backpropagation compatible reservoir that mimics FBA. The or experimental measurements). Since the mass conservation law is
AMN reservoir can then be used to tackle the above-mentioned issue the central rule when satisfying metabolic networks constraints, these
of unknown uptake fluxes: adding a pre-processing neural layer and ratios play a key role in the determination of the metabolic phenotype,
training this layer with an experimental dataset, one can predict uptake i.e. the paths taken by metabolites in the organism. In this approach,
fluxes from the media composition. Results of the pre-processing we assume that the flux branching ratios remain similar between flux
neural layer can directly be plugged into a classical FBA solver and the distributions with different bounds on different uptake fluxes. A simneural layer can be reused by any FBA user to improve the predictive ple toy model network is shown to demonstrate the functioning of the
power of metabolic models with an adequate experimental set-up. Wt-solver in Supplementary Fig. S1.
We showcase AMN-Reservoir results in Fig. 5 using experimental While the Wt-solver is simple to implement it suffers from a
measurements acquired on E. coli and P. putida. drawback. As discussed in Supplementary Information “AMN-Wt
Nature Communications | ( 2023)1 4:4669 3

---

<!-- Page 4 -->

Article https://doi.org/10.1038/s41467-023-40380-0
a b c
Fig. 2 | Benchmarking AMNs with different training sets and mechanistic layers. bounds Vin and produce a vector Vout composed of all fluxes with which the loss is
All results were computed on 5-fold cross-validation sets. Plotted is the mean and computed. a–c show results for different training sets: a, b for 1000 simulations
standard error (95% confidence interval) over the five validation sets of the cross- training sets generated with the E. coli core model, respectively with UB and EB as
validation. Top panels show the custom mechanistic loss values, and bottom panels inputs, whereas c is for a 1000 simulations training set generated with the iML1515
plot the Q² values for the growth rate, over learning epochs (Q² is the regression model, with UB as input (for more details on the training set generations, refer to
coefficient on cross-validation datapoints not seen during training). All AMNs have “Methods”). As mentioned in subsection “Alternative mechanistic models to surthe architecture given in Fig. 1c, with V as input, and a neural layer composed of rogate FBA”, AMN-Wt cannot be used to make predictions when exact bounds (EB)
in
one hidden layer of size 500. For all models, dropout = 0.25, batch size = 5, the are used and is therefore not plotted in (b). Source data are provided as a Source
optimizer is Adam, the learning rate is 10−3. The architecture for ANN (a classical Data file (cf. “Data availability”).
dense network) is given in the “Methods” section it takes as input the uptake fluxes
architecture”, a consensus set of weights leads to a solution when to solve partial differential equations matching a small set of
upper bounds (UB) for uptake fluxes are provided, but not when exact observations24. With PINNs, solutions are first approximated with a
bounds (EB) for uptake fluxes are given (cf. Supplementary Fig. S2). neural network and then refined to fulfill the constraints imposed by
Consequently, we cannot assume that the Wt-solver can handle all the differential equations and the boundary conditions. Refining the
possible flux distributions in the EB case. To overcome this short- solutions necessitates the computation of three loss functions. The
coming, we next present two alternative methods that are much closer first is related to the observed data, the second to the boundary conto the optimizations behind FBA and that can accommodate both EB ditions and the third to the differential equations. As detailed in
and UB cases for uptake fluxes. The two methods address two distinct “Methods”, we similarly compute losses for simulated or measured
tasks in flux modeling: optimizing a flux distribution for maximal reference fluxes, V , the flux boundary constraints, and the metabolic
ref
growth rate (LP-solver), as in classical FBA, and fitting a stationary flux network stoichiometry. As in PINN we next compute the gradient on
distribution to partial flux data (QP-solver). these losses to refine the solution vector V. Unlike with the LP-solver,
The second method (LP-solver), derived from a method proposed we do not provide an objective to maximize in the present case, but
by Yang et al.20, handles linear problems using exact constraint bounds instead reference fluxes, consequently the method is named QP
(EBs) or upper bounds (UBs) for uptake fluxes (V ). That method because it is equivalent to solving an FBA problem with a quadratic
in
makes use of Hopfield-like networks, which is a long-standing field of program.
research21 inspired by the pioneering work of Hopfield and Tank22. As To assess the validity of the LP and QP solver, we used the E. coli
with the Wt-solver, the LP-solver iteratively computes fluxes to come core model25 taken from the BiGG database26. To generate with
closer to the steady-state solution (V ). However, calculations are Cobrapy package19 a training set of 100 growth rates varying 20 uptake
out
more sophisticated, and the method integrates the same objective fluxes, following the procedure given in “Methods”. Results can be
function (e.g. maximize growth rate) as the classical FBA Simplex sol- found in Supplementary Fig. S6, showing excellent performances after
ver. The solver iteratively updates the flux vector, V, and the vector, U, 10,000 iteration steps.
representing the dual problem variables also named metabolites shadow prices23 (cf. “LP-solver” in “Methods” and in Supplementary AMNs: metabolic and neural hybrid models for predictive power
Information for further details). with mechanistic insights
The third approach (QP-solver), is loosely inspired by the work on While the above solvers perform well, their main weakness is the
physics-informed neural networks (PINNs), which has been developed number of iterations needed to reach satisfactory performances. Since
Nature Communications | ( 2023)1 4:4669 4

---

<!-- Page 5 -->

Article https://doi.org/10.1038/s41467-023-40380-0
a b c
C C C
med med med
← ← ←
V
← + ∇ U, V ← + ∇ V ←
→
← + ∇ ← ( ⊙ ) +
→
Q²=0.78 ± 0.03 Q²=0.78 ± 0.01 Q²=0.77 ± 0.01
Fig. 3 | Benchmarking growth rate predictions by AMNs with experimental layer of size 550 corresponding to all fluxes (V) of the iML1515 reduced model. The
measurements. In all panels, the experimental measurements were carried out on mechanistic layer (green box) follows the neural layer and minimizes the loss
E. coli grown in M9 with different combinations of carbon sources (strain DH5- between measured and predicted growth rate, as well as the losses of the metabolic
alpha, model iML1515). Training and 10-fold stratified cross-validation were per- network constraints. The model was trained for 1000 epochs with dropout = 0.25,
formed three times with different initial random seeds. All points plotted were batch size = 5, and the Adam optimizer with a 10−3 learning rate. b Architecture and
compiled from predicted values obtained for each cross-validation set. In all cases, performance of AMN-LP. This model hyperparameters are identical to those of (a).
means are plotted for both axes (measured and predicted), and error bars are The neural layer computes the initial values for the 550 reaction fluxes (vector V),
standard deviations. For the measured data, means and standard deviations were the initial values for the 1083 metabolite shadow prices (vector U) are set to zero.
computed based on three replicates, whereas for predictions, means and standard c Architecture and performance of the AMN-Wt architecture. The model hyperdeviations were computed based on the 3 repeats of the 10-fold cross-validation. parameters are those of the previous panels and the size of the W matrix is
r
a Architecture and performance of AMN-QP. The neural layer (gray box) is com- 550 × 1083 (sizes of V and U vectors). Source data are provided as a Source Data file
posed of an input layer of size 38 (Cmed), a hidden layer of size 500, and an output (cf. “Data availability”).
our goal is to integrate such methods in a learning architecture, this Figure 2 shows the loss values on mechanistic constraints and the
drawback has to be tackled. As illustrated in Fig. 1c, our solution is to regression coefficient (Q²) for the growth rates of the aforementioned
improve our initial guesses for fluxes, by training a prior neural layer (a models. All results shown are computed on 5-fold cross-validation sets.
classical dense ANN) to compute initial values for all fluxes (V ) from Additional information on hyperparameters and results on indepen-
0
bounds on uptake fluxes (V ) or media compositions (C ). This dent test sets are found in the Supplementary Information. In partiin med
solution enables the training of all AMNs with few iterations in the cular, Supplementary Fig. S7 shows performances obtained with AMNmechanistic layer. In the remainder of the paper, we name AMN-Wt, QP and the E. coli core model with different neural layer architectures
AMN-LP and AMN-QP, the hybrid model shown in Fig. 1c composed of and hyperparameters, justifying our choices for the neural layers of
a neural layer followed by a mechanistic layer, i.e., a Wt, LP or QP AMNs (one hidden layer of dimension 500 and a training rate of 10−3).
solver. Similar results were found for AMN-LP and AMN-Wt. Additionally, in
The performances of all AMN architectures (Wt, LP, QP) and a Supplementary Table S1, more extensive benchmarking is provided
classical ANN architecture (cf. Methods “ANN architecture”, for further comparing MMs, ANNs and AMNs. This table shows performances for
details) are given in Fig. 2, using FBA-simulated data on two different E. training, validation, and independent test sets of more diverse datacoli metabolic models, E. coli core25 and iML15159. These models are sets, along with all training sets parameters and the models’
composed respectively of 154 reactions and 72 metabolites, and 3682 hyperparameters.
reactions and 1877 metabolites (after duplicating bi-directional reac- All AMN architectures exhibit excellent regression coefficients
tions). In all cases, the training sets were generated by running the and losses after a few learning epochs, and this for both models E. coli
default Simplex-based solver (GLPK) of Cobrapy19 to optimize 1000 core25 and iML15159. It is interesting to observe the good performances
growth rates for as many different media. Each medium was composed of AMN-Wt when UB training sets are provided. Indeed, while counof metabolites found in minimal media (M9) and different sets of terexamples can be found for which AMN-Wt will not work with EB
additional metabolites (sugars, acids) taken up by the cell (more training sets (cf. Supplementary Fig. S2), we argue in the Supplemendetails in Methods “Generation of training sets with FBA”). These tary Information “AMN-Wt architecture” that AMN-Wt is able to handle
training sets have as variables a vector of bounds on uptake fluxes (20 UB training sets because the initial inputs (UB values for uptake fluxes)
for E. coli core, 38 for iML1515) along with the Cobrapy19 computed are transformed into suitable exact bound values during training (via
growth rate. For the ANN training set, to enable loss computation on the neural layer).
constraints, we replaced the growth rate by the whole flux distribution We recall that in Fig. 2, ANNs were trained on all fluxes to enable
computed by Cobrapy19 (cf. Methods “ANN architecture”). loss computation (154 fluxes for E. coli core and 550 fluxes for iML1515),
Nature Communications | ( 2023)1 4:4669 5

---

<!-- Page 6 -->

Article https://doi.org/10.1038/s41467-023-40380-0
a b d
C R
med KO
Neural layer
AUC=0.90
V 0
Mechanistic layer
V c e
out
Custom
Loss
Fit reference fluxes
and constraints with AUC=0.71
reaction KOs
Fig. 4 | AMNs growth rate predictions for E. coli gene KOs mutants. An AMN dropout = 0.25, batch size = 5, and the Adam optimizer with a 10−3 learning rate.
model was trained on a set of 17,400 measured growth rates of E. coli grown in 120 b AMN regression performance on aggregated growth rate predictions from a 10unique media compositions and 145 different single metabolic gene KOs. a AMN fold cross-validation. The mechanistic layer used for this architecture was the QP
architecture integrating metabolic gene KOs. This architecture is similar to Fig. 1c, solver. c Regression performance of classical FBA with scaled upper bounds for
except for a secondary input (RKO) for the neural layer, alongside the medium compounds present in the medium and setting the upper bound and lower bound
composition C . The R input is a binary vector describing which reactions are to zero for reactions that are KO (having a value of 0 in R ). d ROC curve of AMN
med KO KO
KO. The custom loss function ensures that reference fluxes (i.e., the E. coli mutants results. We thresholded the measured growth rates (continuous values) in order to
measured growth rates) and mechanistic constraints are respected and that reac- transform them into binary growth vs. no growth measures. e ROC curve of clastions experimentally KO have in Vout a null flux value. The neural layer comprised sical FBA results. The same thresholding as for (d) was applied. Source data are
one hidden layer of size 500 and the model was trained for 200 epochs with provided as a Source Data file (cf. “Data availability”).
thus the number of training data points is substantially larger than for The resulting experimental dataset of media compositions, C ,
med
AMNs (154,000 or 550,000 for ANNs, instead of 1000 for AMNs). and growth rates, V , was used to train all AMN architectures (LP, QP,
ref
Despite requiring larger training sets, ANNs also need more learning Wt). These architectures are those shown in Fig. 1c with C as input.
med
epochs than AMNs to reach satisfying constraint losses and growth In all cases the mechanistic layer was derived from the stoichiometric
rate predictions for E. coli core (Fig. 2a, b) and do not handle well the matrix of the iML151520 E. coli reduced model (cf. Methods “Making
large iML1515 GEM (i.e., the growth rate cannot be accurately predicted metabolic networks suitable for neural computations”). Following
and the oscillatory behavior in Fig. 2c demonstrates 100 epochs are Fig. 1c, C was entered as a binary vector (presence/absence of
med
not enough to reach convergence). specific metabolites in the medium), the vector was then transformed
through the neural layer into an initial vector, V0, for all reaction fluxes
AMNs can be trained on experimental datasets with good (therefore including the medium uptake fluxes) prior to be used in the
predictive power mechanistic layer and the loss computations. Prediction performances
To train AMNs on an experimental dataset, we grew E. coli DH5-alpha in are provided in Fig. 3, alongside schematics for each of the
110 different media compositions, with M9 supplemented with four architectures.
amino acids as a basis and ten different carbon sources as possibly For displaying meaningful results and to avoid any overfitting
added nutrients. From 1 up to 4 carbon sources were simultaneously bias, we show in Fig. 3 predictions for points unseen during training.
added to the medium at a concentration of 0.4 g l−1 (more details in More precisely, we computed the mean and standard deviation of
Methods “Culture conditions”). We determined which compositions to predictions over 3 repeats of stratified 10-fold cross-validations, each
test by choosing all the 1-carbon source media compositions and repeat having all points predicted, by aggregating validation sets
randomly picking one hundred of the 2-, 3- and 4-carbon sources predictions of each fold. Overall, results presented in Fig. 3 have been
media compositions (more details in Methods “Generation of an compiled over 3 × 10 = 30 different AMN models, each having different
experimental training set”). The growth of E. coli was monitored in 96- random seeds for the neural layer initialization and the train/validation
well plates, by measuring the optical density at 600 nm (OD ) over splits.
600
24 h. The raw OD was then passed to a maximal growth rate As a matter of comparison, a decision tree algorithm predicting
600
determination method based on a linear regression performed on only the growth rate from C (the RandomForestRegressor function
med
log(OD ) data (more details in Methods “Growth rate from the sci-kit learn package27 having 1000 estimators and other
600
determination”). parameters left with default values) reach a regression performance of
Nature Communications | ( 2023)1 4:4669 6

---

<!-- Page 7 -->

c
Neural layer
Neural layer
Mechanistic layer
d f
b
AMN-Reservoir Scaled uptake fluxes
uptake fluxes bounds bounds
V
in
Simplex
solver
Growth Rate
0.71 ± 0.01 with the same dataset and cross-validation scheme, indi- therefore composed of medium composition and reaction KOs, both
cating AMNs can outperform regular machine learning algorithms. encoded as binary vectors, alongside the measured growth rates. More
As one can observe in Fig. 3, the experimental variability on the details can be found in Methods “External training sets acquisition”.
measured growth rates is relatively high, and the Q² values could be Results are presented in Fig. 4 and compared with classical FBA results,
interpreted differently if taking this variability into account. To study which were obtained running Cobrapy using the same dataset and
this further, we estimated the best possible Q² that can be reached at a setting scaled upper bounds (cf. Methods “Searching uptake fluxes
given experimental variability. Precisely, for each experimental data upper bounds in FBA”) corresponding to medium uptake fluxes and
point, we randomly drew a new point from a normal distribution with a constraining KO reactions to zero fluxes in the metabolic model. The
mean and variance equal to what was experimentally determined for AMN architecture (Fig. 4a) used with this dataset is similar to the
the original point. This point can be considered as an experimental architecture shown in Fig. 1c, with an added input for reaction KOs
randomized point. After doing this for all points and computing the Q², (R ). Importantly, we also added a term to the custom loss in order to
KO
repeating this process 1000 times, we obtain a mean Q² = 0.91 with a respect the reaction KOs (cf. Methods “Derivation of loss functions” for
standard deviation of 0.02. Consequently, the best possible Q² more details).
accounting for experimental variability is 0.91, and the performance of The AMN regression performance in Fig. 4 (aggregated predic-
Q² = 0.77 (or 0.78) must be interpreted considering that value. Fur- tions from a 10-fold cross-validation) reaches Q² = 0.81 (Fig. 4b). For
thermore, substituting each point by a box defined by standard comparison, a decision tree algorithm predicting only the growth rates
deviations of both measurement and prediction, we find that 79% for from C and R (the XGBRegressor function from the XGBoost
med KO
AMN-QP (76% for AMN-LP and 74% for AMN-Wt) of the boxes intersect package29 with all parameters set to default values) yields a regression
the identity line indicating that these points are correctly predicted performance of 0.75, with the same cross-validation scheme and
within the variances. dataset.
Our results show that AMNs can learn on FBA-simulated training The performance of classical FBA is poor, as no correlation can be
sets and make accurate predictions while respecting the mechanistic found between measured and calculated growth rate (Fig. 4c). Such
loss, as shown in Fig. 2. AMNs can also perform well on a small performance is expected as classical FBA relies on fixed uptake fluxes.
experimental growth rates dataset as shown in Fig. 3. To demonstrate In contrast, FBA should perform better to predict growth vs. no growth
capabilities of AMNs beyond these tasks, we extracted from the ASAP (a classification task), this is due to the fact that the network structure
database28 a dataset of 17,400 growth rates for 145 E. coli mutants. Each of GEMs already provides a lot of information on reaction essentiality,
mutant had a KO of a single metabolic gene and was grown in 120 growth yields on different substrates, and other qualitative insights
media with a different set of substrates. Our AMNs training set, were about metabolism. Indeed, in the most recent GEM of E. coli, iML15159,
elbaniart-noN riovreseR-NMA
Article https://doi.org/10.1038/s41467-023-40380-0
C
a med e
R²=0.97
V
in
V 0
V
out
Regression
Growth Rate R²=0.51
Classification
or
Regression
Classification
Fig. 5 | Reservoir computing for improving the predictive power of FBA mod- 500, the model was trained for 1000 epochs with dropout = 0.25, batch size = 5, and
eling (strain E. coli DH5-alpha, model iML1515 and strain P. putida KT2440, the Adam optimizer with a 10−4 learning rate. b Scheme showing the two possible
model iJN1463). For (c, d), plotted are the measured growth rates means and inputs for Cobrapy (running a simplex solver), either using V extracted from (a),
in
standard deviations, computed from replicates (cf. “Methods”). a Learning archi- or using scaled upper bounds on uptake fluxes. c Regression performance of
tecture. The two-step learning is similar to what is shown in Fig. 1d. Here an AMN Cobrapy for the E. coli dataset when using Vin. d Regression performance of
with QP-solver is trained either on iML1515 (c, d) or iJN1463 (e, f) with FBA simu- Cobrapy when using scaled upper bounds on corresponding uptake fluxes.
lations. The AMN (with frozen parameters) is then connected to a prior trainable e Accuracy performance of Cobrapy for the P. putida dataset when using V .
in
network that computes medium uptake fluxes (V ) from the medium composition f Accuracy performance of Cobrapy when using original values of the study from
in
(Cmed). From Vin the non-trainable reservoir returns all fluxes (Vout) including the Nogales et al. For the results in (e, f), accuracies are given for the whole dataset (All)
growth rate. Next, a regression or classification is carried out on the growth rate. composed of carbon source assays (Carbon) and nitrogen source assays (Nitrogen).
For results presented in (c, e), the neural layer comprised one hidden layer of size Source data are provided as a Source Data file (cf. “Data availability”).
Nature Communications | ( 2023)1 4:4669 7

---

<!-- Page 8 -->

Article https://doi.org/10.1038/s41467-023-40380-0
an accuracy >90% was found for a dataset of growth assays based on The output of FBA was used to produce the results shown in
media compositions (classification task predicting growth vs. no panels c and e. As a matter of comparison, we show the performance of
growth). Consequently, we also show in Fig. 4 the performances of FBA for the E. coli dataset (Fig. 5d) with scaled uptake fluxes bounds (cf.
AMN and FBA for classification. Precisely, we treat the growth rate Methods “Searching uptake fluxes upper bounds in FBA”), and for P.
value predicted by either the AMN or FBA as a classification score for putida (Fig. 5f) where we used the same flux bounds as given in the
growth vs. no growth, to that end and following Orth et al.30, we reference study33.
threshold the growth rate measures (continuous values) to binary Overall, results shown in Fig. 5 indicate that the usage of AMNvalues (1 when the growth rate is above 5% of the maximum growth Reservoirs substantially increases the predictive capabilities of FBA
rate of the dataset, 0 otherwise). With classifications, one can compute without additional experimental work. Indeed, after applying the AMN-
ROC curves, and these are shown in Fig. 4d for AMN and Fig. 4e for Reservoir procedure to find the best uptake fluxes, we raised the R² on
classical FBA. E. coli growth rates from 0.51 (panel d) to 0.97 (panel c) and we raised
Overall, the results presented in Fig. 4 show that for both the accuracy on P. putida growth assays from 0.81 (panel f) to 0.96
regression and classification tasks, AMNs, which integrates learning (panel e). We note that these uptake fluxes were found for the training
procedures, outperforms classical FBA, which is based on maximizing set of the AMN-Reservoir, but we also show the performance of FBA
a biological objective only. Indeed, as mentioned in the introduction, with uptake fluxes found for cross-validation sets (Supplementary
one main issue of classical FBA is the unknown uptake fluxes, which Fig. S9). As expected, Fig. S9 displays the same level of performance as
have a large impact on the predicted growth rate value, while AMNs the AMNs directly trained on experimental data (Fig. 3).
can handle this problem because of their learning abilities. To further
showcase AMN capabilities, in particular when multiple fluxes are Discussion
measured, we provide in Supplementary Fig. S8 the performance of an In this study we showed how a neural network approach, with meta-
AMN on a dataset from Rijsewijk et al.31. With this dataset, composed of bolic networks embedded in the learning architecture, can be used to
31 fluxes measured for 64 single regulator gene KO mutants of E. coli address metabolic modeling problems. Previous work on RNNs and
grown in 2 media compositions, our AMN reaches a variance averaged PINNs for solving constrained optimization problems was re-used and
Q² value of 0.91 in 10-fold cross-validation. adapted to develop three models (AMN-Wt, -LP and -QP) enabling
gradient backpropagation within metabolic networks. The models
AMNs can be used in a reservoir computing framework to exhibited excellent performance on FBA generated training sets (Fig. 2
enhance the predictive power of traditional FBA solvers and Supplementary Table S1). We also demonstrated that the models
As already mentioned in the introduction section, the uptake fluxes of can directly be trained on an experimental E. coli growth rate dataset
E. coli nutrients, as well as their relation to external nutrient con- with good predictive abilities (Fig. 3).
centrations, remain largely unknown: the uptake flux for each com- In classical FBA, all biological regulation mechanisms behind a flux
pound may vary between growth media. In classical FBA calculations, distribution are ignored and flux computation relies entirely on
this is usually ignored and the same upper bound (or zero, if a com- bounds set on uptake or internal fluxes. Therefore, when performing
pound is absent) is used in all cases. Our results for KO mutants sug- classical FBA, one needs to set uptake bounds individually for each
gest that this strongly reduced regression performance of classical condition to reliably predict metabolic phenotypes. AMNs attempt to
FBA, while in classification the effect is less severe. Nonetheless, for capture the overall effects of regulation via the neural layer while
regression or classification the problem remains: how can realistic keeping the mechanistic layer for the metabolic phenotype. Indeed, as
uptake fluxes be found? shown in Fig. 4 and Supplementary Fig. S8, gene KOs of metabolic
In the following, we show a way to find these uptake flux values enzymes or regulators can be taken into account via the neural layer.
and improve the performances of classical FBA solvers (for both Such AMNs can potentially be trained on a variety of experimental
regression and classification). Once an AMN has been trained on a inputs (wider than the carbon source composition shown in our stularge dataset of FBA-simulated data, we can fix its parameters and dies) to grasp the effects of complex regulation processes in the cell
exploit it in subsequent further learning in order to find uptake flux and to better explain the end-point metabolic steady-state phenotype
values that can be used in a classical FBA framework. Loosely inspired of an organism.
by reservoir computing32, we call this architecture “AMN-Reservoir” For improved adaptability, we also trained AMN-Reservoirs on
(Figs. 1d and 5a). Let us note that we are not using usual reservoirs32 large FBA-simulated training sets and used these to improve FBA
with random weights and a post-processing trainable layer. As a computations on two experimental datasets (E. coli growth rates and P.
matter of fact, we do not reach satisfactory performances when we putida growth assays). Figure 5 shows that our hybrid models subsubstitute the AMN-Reservoir weights (learned during training) by stantially enhance classical FBA predictions both quantitatively and
random weights. qualitatively, and this without any additional flux measurements.
We benchmarked our AMN-Reservoir approach with two datasets. One issue that impairs phenotype predictions with FBA is the lack
The first one is the one used in Fig. 3, composed of 110 E. coli growth of knowledge on media uptake fluxes and determining bounds on
rates, and the second is a growth assay of P. putida grown in 296 these fluxes is a core experimental work required for making classical
different conditions33 (more details in Methods “External training sets FBA computations realistic. These bounds depend on cell transporters
acquisition”). The procedure used for the two datasets is the same. abundances, which may vary between conditions and depend on the
First, the AMN-Reservoir is trained on FBA simulations. For E. coli we cell’s metabolic strategy. satFBA34 is a variant of FBA that assumes fixed
used as an AMN-Reservoir the AMN-QP of Supplementary Table S1 transporter levels and converts medium concentrations to possible
trained on an iML1515 UB dataset, for P. putida we used the AMN-QP of uptake fluxes by kinetic rate laws, relying on a Michaelis-Menten value
Supplementary Table S1 trained on an iJN146333 UB dataset. Second, as for each uptake reaction. In more sophisticated CBM approaches, such
shown in Fig. 5a, the whole experimental dataset is used to train the as molecular crowding FBA35 or Resource Balance Analysis36, conneural layer, setting up either a regression task for E. coli growth rates straints on the resource availability and allocation are added to obtain
and a classification task for P. putida growth assays (growth vs. no- more biologically plausible metabolic phenotypes, but parameterizing
growth). After training on media compositions and measured growth such models requires additional data. To provide the necessary data to
rates (for both E. coli and P. putida), we extract the corresponding the aforementioned CBM methods and to validate results, fluxomics37,
uptake fluxes (V ). These uptake fluxes are then taken as input for a metabolomics38, or transcriptomics39 have been used in the past.
in
classical FBA solver for growth rate calculation, as shown in Fig. 5b. Because additional experimental work is needed with sophisticated
Nature Communications | ( 2023)1 4:4669 8

---

<!-- Page 9 -->

Article https://doi.org/10.1038/s41467-023-40380-0
CBM approaches, many users rely on classical FBA, which as we have latter case, reactions would be turned off via a trainable layer, which
seen, has limitations as far as quantitative predictions are concerned. would be added prior to the mechanistic layers of our AMNs. Another
AMNs are used in this study for tackling the same issue as satFBA: potential application is the engineering of microorganism-based
predicting metabolites uptake fluxes from medium metabolite com- decision-making devices for the multiplexed detection of metabolic
position. To do so, where satFBA uses transporter kinetics with para- biomarkers or environmental pollutants. Here, AMNs could be used to
meters that need to be acquired through additional measurements, search for internal metabolite production fluxes enabling one to dif-
AMNs use a pre-processing neural layer that is accessible for learning. ferentiate positive samples containing biomarkers or pollutants from
Our AMN hybrid models get rid of additional experimental data for negative ones. Such a device has already been engineered in cell-free
reaching plausible fluxes distributions. We do so by backpropagating systems41, and AMNs could be used to build a similar device in vivo by
the error on the growth rate or any other measured flux, to find adding a trainable layer after the mechanistic layer whose purpose
complex relationships between the medium compositions and the would be to select metabolite production fluxes that best split positive
medium uptake fluxes. To this end, we demonstrated the high pre- from negative samples.
dictive power of AMNs, and their re-usability in classical FBA approaches. Indeed, FBA developers and users may now make use of our Methods
AMN-Reservoir method for relating medium uptake fluxes to growth Making metabolic networks suitable for neural computations
medium compositions. In this regard, a Source Data file (cf. Data The set-up of our AMNs requires all reactions to be unidirectional; that
availability) gives uptake fluxes for the metabolites used in our is, the solutions must show positive-only fluxes (which is not guaranbenchmarking work with E. coli and P. putida (Fig. 5), and these upper teed by usual GEMs). To split reactions of a given metabolic network
bounds for uptake fluxes can directly be used by Cobrapy to repro- into separate forward and reverse reactions, we wrote a standardizaduce Fig. 5c, e. tion script that loads an SBML model into Cobrapy19 and screens for all
Making FBA suitable for machine learning as we have done in this two-sided reactions, then duplicating them into two separate reacstudy opens the door to improve GEMs. For instance, in addition to tions; and writes a new version of the model with bi-directional reacestimating uptake fluxes, AMNs could be used to estimate the coeffi- tions split into separate forward and backward reactions. To avoid
cients of the biomass reaction based on measurements. So far, these confusion, we add a suffix to these reaction names, either “for” or “rev”
coefficients are derived based on literature, but also using experi- respectively designating the original forward reaction and the reversed
mental data: growth rate, fluxes, and macromolecular fractions mea- reaction. The uptake reactions were also duplicated, even if encoded
sures can help finding optimal coefficients9. However, these as one-sided, and their suffix was set to “i” for inflow reactions (adding
experiments are limited in number, and biomass coefficients are matter to the cell), and “o” for outflow reactions (removing matter
usually determined only once, for a single experimental setup, and are from the system).
hardly extrapolated to all possible conditions. Some studies already As detailed in the next subsection, our unidirectional models are
underline this issue and attempt to efficiently integrate experimental used to build flux data training sets. The duplicated iML15159 model is
data in the biomass reaction parametrization40. With AMNs, a trainable large, comprising 3682 reactions and 1877 metabolites. A substantial
layer containing the biomass coefficients could be added, adapting the number of reactions in this model have zero fluxes for many different
biomass reaction to any experimental setup. Another possible appli- media, and it is unnecessary to keep these reactions during the training
cation of AMN is to enhance GEMs reconstruction based on quantita- process. Prior to training, we therefore generated a reduced model by
tive prediction performance. Indeed, the method we developed for removing reactions having zero flux values along with the metabolites
KOs could be adapted to screen putative reactions in a metabolic no longer contributing to any reactions. Using that procedure, we were
model so that its predictions match experimental data. This task able to reduce iML15159 model to only 550 reactions and 1083
should be performed after a manual curation, of course, to rely on metabolites.
existing literature knowledge and databases.
Returning to the curse of dimensionality issue mentioned in the Generation of training sets with FBA
introduction, we systematically studied at which training set sizes Our reference flux data were obtained from FBA simulations, using the
‘black-box’ ML methods would yield performances similar to our AMN GNU Linear Programming Kit (GLPK, a simplex-based method) on
hybrid models. To that end, we trained a simple dense ANN model on Cobrapy19, with different models of different sizes. Throughout this
training sets of increasing sizes. Results obtained with E. coli core25 paper, when “reference FBA-simulated data” is mentioned, it refers to
show that at least 500,000 labeled data (reference fluxes) are needed data computed with this method.
in the training sets to reach losses below 0.01 (cf. in Supplementary Reference FBA-simulated data for metabolic flux distributions
Fig. S10), which according to Fig. 2 and Supplementary Table S1 are still were generated using models downloaded from the BiGG database26.
one order of magnitude higher than all AMNs losses trained on only The models were used to generate data using Cobrapy19 following a
1000 labeled data. This clearly demonstrates the capacity of hybrid precise set of rules. First, we identified essential uptake reactions for
models to reduce training set sizes by constraining the search space the models we used (E. coli core25 and iML15159) which we defined in
through the mechanistic layer. Other black-box models can also be the following way: if one of these reactions has its flux upper bound set
used, indeed the experimental measurements used in Figs. 3 and 4 can to 0 mmol gDW−1 h−1, the biomass reaction optimization is impossible,
be fitted with decision tree algorithms (Random Forests27 and even if all other uptake fluxes bounds are set to a high value, e.g.,
XGBoost29) with performances slightly under those of AMN. However, 1000 mmol gDW−1 h−1. In other words, we identified the minimal
with these algorithms, nothing is learned regarding the mechanistic uptake fluxes enabling growth according to the models. For E. coli
constraints and results produced by these methods cannot be fed back core25 we found seven of such obligate reactions (for the uptake of
to classical FBA, as we do in Fig. 5 with the AMN-Reservoir. CO2, H+, H20, NH4, O2, Phosphate, and Glycerol as the carbon source).
Beyond improving constraint-based mechanistic models and For iML151520 we had the same 7 obligate reactions and additional salt
black-box ML models, AMNs can also be exploited for industrial and ions uptake reactions (for the uptake of Fe2+, Fe3+, Mn2+, Zinc,
applications. Indeed, since arbitrary objective functions can be Mg, Calcium, Ni2+, Cu2+, Selenate, Co2+, Molybdate, Sulfate, K+,
designed and AMNs can be directly trained on experimental mea- Sodium, Chloride, Tungstate, Selenite). With iML15159, we also added
surements, AMNs can be used to optimize media for the bioproduc- as obligate reactions the uptake of four amino acids (Alanine, Proline,
tion of compounds of interest or to find optimal gene deletion and Threonine and Glycine) in order to be consistent with our experiinsertion strategies in typical metabolic engineering projects. In this mental training set where the four amino acids were systematically
Nature Communications | ( 2023)1 4:4669 9

---

<!-- Page 10 -->

Article https://doi.org/10.1038/s41467-023-40380-0
added to M9 (cf. subsection “Generation of an experimental training For each solution, V, of Eq. (1), four loss terms are defined. L is the
1
set”). During reference FBA-simulated data generation, the upper loss on the fit to the reference data. L ensures the respect of the
2
bounds on these obligate reactions were set to 10 mmol gDW−1 h−1. network stoichiometric constraint (S V = 0). L ensures the respect of
3
To generate different media compositions, we added to the the constraints on input fluxes that depend on medium composition
obligate reactions a set of variable uptake reactions. For the E. coli core (P in V ≤ V in). Finally, L 4 ensures the respect of the flux positivity (V ≥ 0).
model25 we added 13 variable uptake reactions (for Acetate, Acet- The losses are normalized, respectively by n for the fit to reference
ref
aldehyde, Oxoglutarate, Ethanol, Formate, Fructose, Fumarate, Gluta- data, m for the stoichiometric constraint, n for the boundary conin
mine, Glutamate, Lactate, Malate, Pyruvate, and Succinate). For each straints, and n for the flux positivity constraints.
generated medium, a set of variable uptake reactions was selected, Summing the four terms, the loss L is:
drawn with a binomial distribution B(n, p) with n = 13 and p = 0.5, p
being a tunable parameter related to the ratio of selected reaction. L = L 1 + L 2 + L 3 + L 4 ð2Þ
C w o as ns n eq × u p en = t 6 ly .5 , . th N e e m xt ea f n or nu e m ac b h er se o l f e s c e t l e e d ct r e e d a v c a ti r o ia n b , le th u e pt u a p k p e e r r ea b c o ti u o n n d s = nr 1 ef ∣P ref V (cid:2) V ref ∣2 + m 1 ∣SV∣2 + n 1 in ∣ReLUðP in V (cid:2) V in Þ∣2 + n 1 ∣ReLUð(cid:2)VÞ∣2
continuous value of the reaction flux was randomly drawn from a More details about each loss term can be found in the Suppleuniform distribution between 2 and 10 mmol gDW−1 h−1. For the mentary Information “QP-solver equations”.
iML15159 model, to limit the combinatorial search space, the selected When reaction KOs are added to the input of AMNs (as in Fig. 4),
variable uptake reactions were those of the experimental training set we add a term to the loss function, L , for ensuring a null value for
5
and consequently between 1 and 4 variable uptake reaction were fluxes that have their reaction KO:
added (cf. subsection “Generation of an experimental training set”).
T ch h o e se u n pp ra e n r d b o o m u l n y d be v t a w l e u e e n s 0 fo a r nd ea 2 c .2 h m se m le o c l t g e D d W v − a 1 r h ia −1 b ( l 0 e e r x e c a l c u t d io e n d). w T e h r e e L 5 = n K 1 O ∣ReLU (cid:1) P KO V (cid:2) R KO (cid:3) ∣2 ð3Þ
2.2 threshold was chosen to produce predicted growth rates that were
in the range of those observed experimentally. For the P. putida where R KO is a vector of length n KO describing which reactions are KO,
iJN146333 model, we used the same approach with variable uptake and P KO the projection matrix mapping the whole flux vector V to
reactions selected from the experimental training set, and conse- KO fluxes.
quently 1 variable uptake reaction was added to obligate reactions
(described as the minimal medium in the reference study33) for each Wt-solver
element of the training set. The upper bound values for each selected The Wt-solver describes a metabolic state by two vectors V and M,
variable reaction were chosen randomly between 0 and representing respectively the reaction fluxes and the metabolite pro-
10 mmol gDW−1 h−1 (0 excluded). duction fluxes. The initial value (V0) for vector V can be arbitrary as
After generating the set of growth media for E. coli core25, iML15159 long as the uptake medium bounds are respected. Vectors V and M are
and iJN146333 we ran FBA in Cobrapy19 for each medium and recorded iteratively computed until convergence using the following equations:
all steady-state fluxes including the growth rate (flux of the biomass
reaction). These fluxes were used as a training set for all models pre- M = P (cid:1) v!m V (cid:3) ð4Þ
s w e e n r t e ed tr i a n in F e ig d . o 2 n an t d he in b S io u m pp a l s e s m fl e u n x ta ( r i y .e T . a t b h l e e g S r 1 o . A w l t l h AM ra N te) a , rc w h h it i e le ct A u N re N s V = P m!v V / (cid:3) W r M + V0
architectures were trained on all fluxes. For all UB training sets, the where W r is a consensus weight mat (cid:4) r h ix re i p (cid:5) resenting flux branching
v th a e ria t b ra le in u in p g ta s k e e t. fl F u o x r v E a B lu t e r s ai w n e in re g t s h e o ts s , e t u h s e ed va b ri y ab C l o e b u r p ap ta y k 19 e t fl o u g x en va e l r u a e te s ratios, P v!m = ReLUðSÞ, P v!m = ReLU z (cid:2) i s 1 j,i , S is the stoichiometric
were those calculated by Cobrapy19 at steady state. matrix, s j,i the stoichiometric coefficient of row j and column i, z i the
number of strictly negative elements in column i of S, and ⊙ the
Hadamard product operation. Additional details on the procedure and
Derivation of loss functions
the associated matrices are provided in Supplementary Information
Loss functions are necessary to assess the performances of all MM
section “Wt-solver equations”.
solvers and all AMN architectures (AMN-Wt, -QP, and -LP) and also to
compute the gradients of the QP solvers. In the following and subsequent subsections, all vectors and matrices notations are defined LP-solver
when they are first used and can also be found in Supplementary The LP method aims at solving linear constrained problem similar to
Table S2. the ones solved by FBA. It relies on the results from Yang et al.20 where
To compute loss, we co(cid:1)nsider a m(cid:3) etabolic model with n reactions the authors used gradient descent on both primal and dual variables of
and m metabolites. Let V = v 1 , . . . ,v n T be the reaction flux vector and the problem.
S the m × n stoichiometric matrix of the model. We assume some When the uptake fluxes are known (EB method), the FBA problem
metabolites can be imported in the model through a corresponding can be written as:
uptake reaction. Let V be the vector of n upper bounds (or exact
in in
values) for these uptake reactions, and let P in the n in × n projection max : cT FBA V
matrix such that V in = P in V. We further assume that some reaction s:t: S int V = (cid:2) b FBA ð5Þ
fluxes have been experimentally measured, let V ref be the vector of V ≥ 0
reference flux data (FBA-simulated or measured). With P the n × n
ref ref
projection matrix for measured fluxes. V is calculated by solving the where S int is the stoichiometric matrix with uptake fluxes zeroed out
following quadratic program (QP): (i.e. fluxes that add matter in the system). In other words, S int is the
internal stoichiometric matrix. Let us consider b FBA, a vector of
minð∣
s
P
:t r : ef S
V
V
(cid:2)
=
V
0 ref
∣2Þ d
m
im
et
e
ab
ns
o
i
l
o
it
n
e m
m
i (
w
ei
i
t
t
h
h
er
b i
as
co
an
rre
e
s
x
p
a
o
ct
nd
va
in
lu
g
e
t
f
o
or
u
E
p
B
ta
o
k
r
e
an
flu
u
x
p
e
p
s
er
of
bo
m
u
e
n
d
d
iu
fo
m
r
P V ≤ V
ð1Þ UB) and c FBA, the objective vector of dimension n (in this work this
in in vector has non-zero elements only for reference fluxes like the biomass
V ≥ 0 reaction flux, i.e., the growth rate.
Nature Communications | ( 2023)1 4:4669 10

---

<!-- Page 11 -->

Article https://doi.org/10.1038/s41467-023-40380-0
This problem can be written in its dual form with U being the dual training, when only a fraction of fluxes are provided (like the growth
variable of V: rate with experimental datasets). In our implementation (cf. “Code
availability” section) AMN-Wt is embedded in a RNN Keras cell42 and
s
m
t :
in
ST
:
in
(cid:2)
t U
bT
≤
FB
c
A
F
U
BA
ð6Þ b
d
o
et
t
a
h
il
m
ed
at
i
r
n
ic
S
e
u
s
p
W
p
i
le
a
m
nd
en
W
ta
r
r
a
y
re
In
le
fo
ar
rm
ne
a
d
ti
d
o
u
n
ri
“
n
A
g
M
t
N
ra
-
i
W
ni
t
n
a
g
r
.
c
A
h
N
it
N
ec
-W
tu
t
r
i
e
s
”
f
.
urther
With all AMN architectures, the values of V corresponding to V
in
As mentioned before, the problem given by Eq. (5) can be solved are not updated in the neural nor mechanistic layers when training
conjointly with problem given by Eq. (6) by iteratively updating V and with exact values for medium uptake (EB training sets).
its dual U through gradient descent:
ANN and AMN training parameters
Vðt +1Þ = VðtÞ (cid:2) dt ∇V For ANN and AMN architectures, we use the mean squared error (L 1 in
Uðt +1Þ = UðtÞ (cid:2) dt ∇U ð7Þ Eq. (2)) for measured fluxes as the objective function to minimize
during training. In all AMN architectures we add to the L loss function
Vð0Þ = PT in V in andUð0Þ = 0 the terms corresponding to the 3 losses derived from th 1 e constraints
of the metabolic model (L , L and L in Eq. (2)).
2 3 4
where t is the iteration number and dt the learning rate. The parameters used when training ANNs and AMNs, there are
Note that initialization of LP with uptake fluxes is not mandatory two types:
with the method from Yang et al.20 as it has been proven to converge to (1) Reference data parameters: reference data can either be FBAglobal optimum independently from the initial values of V and U. simulated or experimental. For FBA-simulated data, we can tune
Detailed expressions and derivations of gradients for U and V are the size of the training set to be generated. We can also modify the
provided in Supplementary Information “LP-solver equations” along mean number of selected variable intake medium fluxes, and the
with Figs. S4 and S5. number of levels (i.e. the resolution) of the fluxes. We can also
modify the variable uptake reactions list, but this modifies the
QP-solver architecture of the model (initial layer size), so we kept the same
The QP solver solves the quadratic program given by Eq. (1). While the list for each model in the present work. The lists can be found in
QP system can be solved by a simplex algorithm, solutions can also be the subsection “Generation of training sets with FBA”.
approximated by calculating the vector V that minimizes the loss (L in (2) Model hyperparameters: during learning on FBA-simulated or
Eq. (2)). The gradient ∇V for vector V can thus be found by solving experimental data, ANN and AMN have a small set of parameters
∂L = 0 and, as in Eq. (7), V is computed iteratively with iteration number to tune: the number and size of hidden layers, the number of
∂V
t and learning rate dt. epochs, the batch size, the dropout ratio, the optimizer and
Detailed expressions and derivations for the gradient ∇V, when learning rate, and the number of folds in cross-validation. These
exact bounds (EBs) or upper-bounds (UBs) are provided for uptake numbers are provided in Supplementary Table S1 for models
flux medium, can be found in the Supplementary Information “QP- trained on FBA-simulated data and in the captions of Figs. 3–5 for
solver equations”. models trained on experimental data.
ANN architecture Searching uptake fluxes upper bounds in FBA
The ANN architecture is a “black box” dense neural network. As with The goal of this optimization was to find the best scaler for fluxes to
the other architectures the input layer corresponds to the medium best match experimentally determined growth rates, by using “out-ofuptake fluxes, V , and the output layer corresponds to the set of all the-box” FBA, simply informing the presence or absence of the flux
in
fluxes V . In order to assess losses with the ANN architecture, which according to the experimental medium composition. The optimal
out
does not have any mechanistic layer, each entry of the training set scaler used in Figs. 4 and 5 was found using the Cobrapy software
contained all flux values (in other words, V contains all fluxes). package19 by simply searching for the maximum R² between experiref
Consequently, the training process with ANN consists in fitting all mental and FBA-predicted growth rates for scalers ranging between
predicted fluxes to reference flux data (computing the MSE on all the 1 and 10.
fluxes). To compare results with the other architectures, R² and Q² are
computed for the growth rate, and constraint losses are computed Generation of an experimental training set
using predictions for all fluxes, using the formulation given in the Ten carbon sources were picked for being the variables of our training
subsection Methods “Derivation of loss functions”. sets: Ribose (Sigma-Aldrich, CAS:50-69-1), Maltose (Sigma-Aldrich,
CAS:6363-53-7), Melibiose (Sigma-Aldrich, CAS:585-99-9), Trehalose
AMN architectures (Sigma-Aldrich, CAS:6138-23-4), Fructose (Sigma-Aldrich, CAS:57-48-7),
As shown Figs. 1 and 3, we propose three AMN architectures: AMN-Wt, Galactose (Sigma-Aldrich, CAS:59-23-4), Acetate (Sigma-Aldrich,
AMN-LP and AMN-QP. The AMNs are run with training sets using exact CAS:127-09-3), Lactate (Sigma-Aldrich, CAS:867-56-1), Succinate
values (EB) or only upper bound values (UB) for medium uptake fluxes. (Sigma-Aldrich, CAS:150-90-3), Pyruvate (Sigma-Aldrich, CAS:113-24-6).
All AMNs take as their input a vector of bounds of size n in for medium These could ensure observable growth as a sole carbon source with a
uptake fluxes (V ) and then transform it via a dense neural network the concentration of 0.4 g l−1 in our M9 preparations. The selected carbon
in
input vector into an initial vector of size n for all fluxes (V0), which is sources enter different parts of the metabolic network: 6 sugars enter
refined through an iterative procedure computing Vðt +1Þ from VðtÞ. the upper glycolysis pathway, and 4 acids enter the lower glycolysis
With all AMNs a n in × n weight matrix transforming V in to V0 is learned pathway or the TCA cycle. With a binary (i.e., presence or absence of
during training, and we name this transforming layer the neural layer. each carbon source) approach when generating the combinations to
With AMN-LP/QP, VðtÞ is iteratively updated in a mechanistic layer by test for making the experimental training set, we generated all possible
the gradient (∇V) of LP/QP solvers (cf. previous subsections in combinations of 1, 2, 3 or 4 carbon sources simultaneously present in
“Method”). With AMN-Wt, the mechanistic layer computes Vðt +1Þ from the medium. Naturally, we picked all 1-carbon source media combina-
VðtÞ using the transformations shown in Fig. S1, which include a n × m tions for experimental determination (only 10 points). Then, we ranweight matrix (W r). That weight matrix can be directly computed from domly selected 100 more combinations to experimentally determine,
training data when all fluxes are provided or can be learned during by randomly picking 20 points from the 2-, 40 points from the 3- and
Nature Communications | ( 2023)1 4:4669 11

---

<!-- Page 12 -->

Article https://doi.org/10.1038/s41467-023-40380-0
40 points from the 4-carbon source combinations sets. The python mutant strains)28. That dataset was pre-processed by applying several
scripts to generate these combinations and pick the ones for making filtering steps: removing substrates that do not appear in iML1515 as
our experimental training set are available on our Github package43 (cf. possible substrates for uptake fluxes, removing genes not found in
“Codes availability” section). After picking the combinations to test, we iML1515, and removing all data duplicates to obtain a balanced and
experimentally determined the maximum specific growth rate of E. coli coherent dataset. The filtered dataset contains 17,400 growth rates:
for each combination of carbon sources in M9 (cf. next two subsec- 145 E. coli mutants (each having a KO of a single metabolic gene) grown
tions). The mean over replicates for each media composition was in 120 conditions (each with a different set of substrates) from Biolog
computed as the corresponding growth rate value to make the final phenotype microarrays44. The final training set can be found in the
experimental training set (cf. Methods “Growth rate determination”). source data, provided as a Source Data file (cf. “Data availability”).
For practical reasons, we converted the information about meta-
Culture conditions bolic gene KOs information into binary vectors describing which
The base medium for culturing E. coli DH5-α (DH5a) was a M9 medium reactions are directly affected by a gene KO, called R in Fig. 4. This
KO
prepared with those final concentrations: 100 µM CaCl (Sigma-Aldrich, mapping was automated with iML1515’s ability to link genes and
2
CAS:10035-04-8); 2 mM MgSO (Sigma-Aldrich, CAS:7487-88-9); 1X reactions. For reactions performed by enzymes encoded by more than
4
M9 salts: 3 g l−1 KH PO (Sigma-Aldrich, CAS: 7778-77-0), 8.5 g l−1 one gene, we make the assumption that when any of these genes is
2 4
Na HPO 2H O (Sigma-Aldrich, CAS:10028-24-7), 0.5 g l−1 NaCl (Sigma- knocked-out, the reaction is also knocked-out.
2 4 2
Aldrich, CAS:7647-14-5), 1 g l−1 NH Cl (Sigma-Aldrich, CAS:12125-02-9); For the FBA computation (Fig. 4c, e), we set an arbitrary upper
4
1X trace elements: 15 mg l−1 Na EDTA 2H 0 (Sigma-Aldrich, CAS:6381- bound on uptake fluxes (11 mmol gDW−1 h−1 was found to be the best
2 2
92-6), 4.5 mg l−1 ZnSO 7H O (Sigma-Aldrich, CAS:7446-20-0), 0.3 mg l−1 value in terms of regression performance) for each substrate in the
4 2
CoCl 6H O (Sigma-Aldrich, CAS:7791-13-1), 1 mg l−1 MnCl 4H O dataset when it is present (otherwise 0). To simulate a KO, we set the
2 2 2 2
(Sigma-Aldrich, CAS:13446-34-9), 1 mg l−1 H3BO3 (Sigma-Aldrich, lower and upper bound of a reaction to zero.
CAS:10043-35-3), 0.4 mg l−1 Na MoO 2H 0 (Sigma-Aldrich, CAS:10102- To transform the measured growth rates from continuous values
2 4 2
40-6), 3 mg l−1 FeSO 7H O (Sigma-Aldrich, CAS:7782-63-0), 0.3 mg l−1 into binary values (for the ROC curves in Fig. 4d, e), following Orth
4 2
CuSO 5H O (Sigma-Aldrich, CAS:7758-99-8), solution adjusted at et al.30, we applied a threshold of 0.165 h−1, which is equal to 5% of the
4 2
pH = 4 and stored at 4 °C; 1 mg l−1 Thiamine-HCl (Sigma-Aldrich, maximum growth rate (3.3 h−1) found in the dataset. Therefore, the
CAS:67-03-8); 0.04 g l−1 amino acid mix so that L-Alanine (Sigma- classification task can be seen as the ability for the model to classify
Aldrich, CAS:56-41-7), L-Proline (Sigma-Aldrich, CAS:147-85-3), growth rates below and above the threshold value.
L-Threonine (Sigma-Aldrich, CAS:72-19-5), Glycine (Sigma-Aldrich,
CAS:56-40-6) were each at a final concentration of 5 mg l−1 in the P. putida growth assays. The dataset used to generate Fig. 5 (panels e
medium. The additional carbon sources that could be added were and f) was taken from the study of Nogales et al.33 presenting iJN1462
individually set to a final concentration of 0.4 g l−1. The pH was adjusted (an updated version called iJN1463 is available on BiGG26) for P. putida’s
at 7.4 prior to a 0.22 µm filter sterilization of the medium. Pre-cultures GEM. This state-of-the-art GEM of P. putida KT2440 contains a few
were recovered from glycerol −80 °C stocks, grew in Luria-Bertani (LB) hundred more genes and reactions from the previous models, allowing
broth overday for 7 h, then used as 5 µl inoculate in 200 µl M9 (sup- better coverage. The dataset corresponds to growth assays with 188
plemented with variable compounds) in 96 U-bottom wells plates carbon and 108 nitrogen sources. For each condition, we verified that
overnight for 14 h. Then 5 µl of each well was passed to a replicate of the an uptake reaction flux was present in the iJN146333 model. Fifty-five
plate on the next day for growth monitoring. The temperature was set conditions contained a nutrient source without a corresponding
to 37 °C in a plate reader (Agilent Technologies, BioTek HTX Synergy), uptake reaction in the model. For all those conditions, the AMN input
with continuous orbital shaking at maximum speed, allowing aerobic would be the minimal medium. In order to avoid biasing the training
growth for 24 h. A monitoring every 10 min of the optical density at set with 55 identical conditions, we kept one condition describing the
600 nm (OD ) was performed. A figure for summarizing the experi- minimal medium for carbon sources and one condition describing the
600
mental workflow is available in Fig. S11. minimal medium for nitrogen sources. The 55 conditions were added
back to compute the final score. The training set can be found in the
Growth rates determination source data, provided as a Source Data file (cf. “Data availability”).
The maximal growth rate was determined by sliding a window of 1 h- The minimal medium assumed in our simulations was taken from
size, performing a linear regression on the log(OD ) data in each Nogales et al.33, reporting a set of uptake fluxes upper bounds. When
600
window. We then retrieve the maximum specific growth rate as the testing a carbon (nitrogen) source, glucose (NH ) was removed from
4
maximum regression coefficient over all windows. If several growth the minimal medium, and the respective nutrient source metabolite
phases are visible, one can omit a part of the growth curve for the was added. Using these simulated growth media, accuracies on growth
maximal growth rate determination (for this study we always retrieved predictions using Cobrapy (Fig. 5f) were calculated considering as
the maximal growth rate on the first growth phase, so as we are certain positive all non-zero growth predictions. Results presented in Fig. 5e
that the media contains all added carbon sources). Eight replicates for were obtained by training a reservoir on simulations as explained in
each medium composition were performed (on a single column of a Methods “AMN and ANN training parameters”. Thus, this reservoir was
96-well plate). Outliers were manually removed after visual inspection used to fit experimental data, and V was directly used as an input
in
of the growth curves or clear statistical deviation of the computed for Cobra.
growth rate from the remaining replicates. The numbers of replicates
kept range from 2 to 8, with an average of 4.6 (±1.6) replicates per Statistics and reproducibility
medium composition. Means and standard deviations over replicates As stated in the previous section “Generation of training sets with FBA”,
were computed to be used for training AMNs and making figures. All the exchange reactions upper bounds were randomized to produce
raw data and the code to process it are available in the Github FBA-simulated training sets. No statistical method was used to prerepository43 (cf. “Code availability”). determine the sample size, which was chosen based on time and
resources. Blinding was not relevant to generate these training sets.
External training sets acquisition As stated in the previous section “Generation of an experimental
Growth rates of E. coli metabolic gene KO mutants. The dataset was training set”, the media of the experimental training set were randodownloaded from the ASAP database (Mutant Biolog Data I for K-12 mized by randomly drawing carbon sources combinations. The growth
Nature Communications | ( 2023)1 4:4669 12

---

<!-- Page 13 -->

Article https://doi.org/10.1038/s41467-023-40380-0
rate measures were computed as means over 2 to 8 technical repli- 7. Schinn, S.-M., Morrison, C., Wei, W., Zhang, L. & Lewis, N. E. A
cates. In all figures displaying this dataset, we show the standard genome-scale metabolic network model and machine learning
deviation over replicates as the error bars. No statistical method was predict amino acid concentrations in Chinese Hamster Ovary cell
used to predetermine the sample size of 110. This size was chosen cultures. Biotechnol. Bioeng. 118, 2118–2123 (2021).
based on time and resources. Blinding was not relevant to generate 8. Freischem, L. J., Barahona, M. & Oyarzún, D. A. Prediction of gene
this training set. essentiality using machine learning and genome-scale metabolic
As stated in the previous section “External training sets acquisi- models. bioRxiv https://doi.org/10.1101/2022.03.31.486520 (2022).
tion”, we used two publicly available datasets, for which the authors 9. Monk, J. M. et al. iML1515, a knowledgebase that computes
did not specify any statistical method to predetermine the sample size. Escherichia coli traits. Nat. Biotechnol. 35, 904–908 (2017).
To our knowledge, there was no replication scheme for these external 10. Sahu, A., Blätke, M.-A., Szymański, J. J. & Töpfer, N. Advances in flux
training sets. Incompatible data were excluded in the pre-processing balance analysis by integrating machine learning and mechanismsteps of the training set stemming from the ASAP database (cf. based models. Comput. Struct. Biotechnol. J. 19, 4626–4640 (2021).
“External training sets acquisition” section). For more details on the 11. Kim, M., Rai, N., Zorraquino, V. & Tagkopoulos, I. Multi-omics intestatistics and reproducibility of these external training sets, please gration accurately predicts cellular state in unexplored conditions
refer to the original studies. for Escherichia coli. Nat. Commun. 7, 13090 (2016).
12. Lewis, J. E. & Kemp, M. L. Integration of machine learning and
Reporting summary genome-scale metabolic modeling identifies multi-omics bio-
Further information on research design is available in the Nature markers for radiation resistance. Nat. Commun. 12, 2700 (2021).
Portfolio Reporting Summary linked to this article. 13. Zampieri, G., Vijayakumar, S., Yaneske, E. & Angione, C. Machine
and deep learning meet genome-scale metabolic modeling. PLoS
Data availability Comput. Biol. 15, e1007084 (2019).
Metabolic models used in this study can be found with the following 14. Fortelny, N. & Bock, C. Knowledge-primed neural networks enable
accessions on the BiGG database26: E. coli core (http://bigg.ucsd.edu/ biologically interpretable deep learning on single-cell sequencing
models/e_coli_core), iML1515, iJN1463. Unidirectional versions of these data. Genome Biol. 21, 190 (2020).
models can be found on our repository at https://github.com/brsynth/ 15. Lagergren, J. H., Nardini, J. T., Baker, R. E., Simpson, M. J. & Flores, K.
amn_release/tree/main/Dataset_input/. The original dataset from the B. Biologically-informed neural networks guide mechanistic mod-
ASAP database28 can be found under the accession Mutant Biolog Data eling from sparse experimental data. PLoS Comput. Biol. 16,
I (https://asap.genetics.wisc.edu/asap/experiment_data.php). The ori- e1008462 (2020).
ginal dataset from Nogales et al.33 can be found in Supporting Infor- 16. Nilsson, A., Peters, J. M., Meimetis, N., Bryson, B. & Lauffenburger, D.
mation’s Table S2 of the study. The source data underlying all figures A. Artificial neural networks enable genome-scale simulations of
presented in the main manuscript and Supplementary Information intracellular signaling. Nat. Commun. 13, 3069 (2022).
(including training sets used in Figs. 3–5), are provided with this paper 17. Raissi, M., Perdikaris, P. & Karniadakis, G. E. Physics-informed neural
as a downloadable archive. Additional datasets and raw data are networks: a deep learning framework for solving forward and
available on our Github repository (cf. “Code availability”), or from the inverse problems involving nonlinear partial differential equations.
corresponding authors upon request. Source data are provided with J. Comput. Phys. 378, 686–707 (2019).
this paper. 18. Rackauckas, C. et al. Diffeqflux, V. jl-A julia library for neural differential equations, arXiv preprint arXiv:1902.02376 https://doi.org/
Code availability 10.48550/arXiv.1902.02376 (2019).
All scripts and data for generating results presented in this paper are 19. Ebrahim, A., Lerman, J. A., Palsson, B. O. & Hyduke, D. R. COBRApy:
available within a documented repository. For a citable and stable constraints-based reconstruction and analysis for Python. BMC
version of the repository supporting this article, refer to our Syst. Biol. 7, 74 (2013).
repository43 hosted on Zenodo with the https://doi.org/10.5281/ 20. Yang, Y., Cao, J., Xu, X., Hu, M. & Gao, Y. A new neural network for
zenodo.8056442 (https://zenodo.org/record/8056442). Alternatively, solving quadratic programming problems with equality and
to access future releases and interact with the repository authors, refer inequality constraints. Math. Comput. Simul. 101, 103–112 (2014).
to Github (https://github.com/brsynth/amn_release). The repository 21. Jin, L., Li, S., Hu, B. & Liu, M. A survey on projection neural networks
includes tutorials in Google Colab notebooks. The released codes and their applications. Appl. Soft Comput. 76, 533–544 (2019).
make use of Cobrapy19, numpy45, scipy46, pandas47, tensorflow48, sci-kit 22. Hopfield, J. J. & Tank, D. W. “Neural” computation of decisions in
learn27 and keras42 libraries. Figures were generated using the optimization problems. Biol. Cybern. 52, 141–152 (1985).
matplotlib49 and seaborn50 libraries. 23. Varma, A. & Palsson, B. O. Metabolic capabilities of Escherichia coli:
I. synthesis of biosynthetic precursors and cofactors. J. Theor. Biol.
References 165, 477–502 (1993).
1. Jumper, J. et al. Highly accurate protein structure prediction with 24. Cuomo, S. et al. Scientific machine learning through
AlphaFold. Nature 596, 583–589 (2021). physics–informed neural networks: where we are and what’s
2. Bellman, R. Dynamic Programming (Princeton University next. J. Sci. Comput. 92, 88 (2022).
Press, 1957). 25. Orth, J. D., Fleming, R. M. T. & Palsson, B. Ø. Reconstruction and use
3. Thornburg, Z. R. et al. Fundamental behaviors emerge from simu- of microbial metabolic networks: the core Escherichia coli metalations of a living minimal cell. Cell 185, 345–360.e28 (2022). bolic model as an educational guide. EcoSal Plus 4, 1–47 (2010).
4. Reed, J. L. & Palsson, B. Ø. Thirteen years of building constraint- 26. Norsigian, C. J. et al. BiGG Models 2020: multi-strain genome-scale
based in silico models of Escherichia coli. J. Bacteriol. 185, models and expansion across the phylogenetic tree. Nucleic Acids
2692–2699 (2003). Res. 48, D402–D406 (2020).
5. O’Brien, E. J., Monk, J. M. & Palsson, B. O. Using genome-scale 27. Pedregosa, F. et al. Scikit-learn: machine learning in Python. J.
models to predict biological capabilities. Cell 161, 971–987 (2015). Mach. Learn. Res. 12, 2825–2830 (2011).
6. Plaimas, K. et al. Machine learning based analyses on metabolic 28. Glasner, J. D. et al. ASAP, a systematic annotation package for comnetworks supports high-throughput knockout screens. BMC Syst. munity analysis of genomes. Nucleic Acids Res. 31, 147–151
Biol. 2, 67 (2008). (2003).
Nature Communications | ( 2023)1 4:4669 13

---

<!-- Page 14 -->

Article https://doi.org/10.1038/s41467-023-40380-0
29. Chen, T. & Guestrin, C. XGBoost: a scalable tree boosting system. ANR-21-CE45-0021-01 (AMN project) and the UE HORIZON BIOS proarXiv [cs.LG] https://doi.org/10.1145/2939672.2939785 (2016). gram (grant number 101070281). L.F. is supported by INRAE’s MICA
30. Orth, J. D. et al. A comprehensive genome-scale reconstruction of department and by INRAE’s metaprogram DIGIT-BIO. B.M. is supported
Escherichia coli metabolism–2011. Mol. Syst. Biol. 7, 535 (2011). by an Ecole Normale Supérieure (ENS) Scholarship. We thank Aymeric
31. Haverkorn van Rijsewijk, B. R. B., Nanchen, A., Nallet, S., Kleijn, R. J. Gaudin (CentraleSupélec Engineering School) for early development in
& Sauer, U. Large-scale 13C-flux analysis reveals distinct tran- reservoir computing with AMN, Ivan Radkevich (University of Paris
scriptional control of respiratory and fermentative metabolism in Saclay) for his work on custom RNN cells and Tom Lorthios and Hadi
Escherichia coli. Mol. Syst. Biol. 7, 477 (2011). Jbara (AgroParisTech and University of Paris Saclay) for their help on
32. Tanaka, G. et al. Recent advances in physical reservoir computing: a collecting data for experimental training sets. We thank Anne Giralt and
review. Neural Netw. 115, 100–123 (2019). Laetitia Laversa (INRAE) for reading and improving our manuscript.
33. Nogales, J. et al. High-quality genome-scale metabolic modelling of
Pseudomonas putida highlights its broad metabolic capabilities. Author contributions
Environ. Microbiol. 22, 255–269 (2020). L.F. and J.L.F. wrote the core of the text of the manuscript. J.L.F.
34. Müller, S., Regensburger, G. & Steuer, R. Resource allocation in designed the study and wrote the Wt and QP-solver and all the AMN and
metabolic networks: kinetic optimization and approximations by AMN-Reservoir codes used to produce results presented in Figs. 1–5.
FBA. Biochem. Soc. Trans. 43, 1195–1200 (2015). B.M. wrote the LP-solver and the corresponding part in the “Methods”
35. Beg, Q. K. et al. Intracellular crowding defines the mode and section and Supplementary Information. L.F. benchmarked all codes,
sequence of substrate uptake by Escherichia coli and constrains its wrote the codes transforming SBML models into unidirectional networks
metabolic activity. Proc. Natl Acad. Sci. USA 104, and processing experimental data, and handled the Colab and Git
12663–12668 (2007). implementations. L.F. also performed the experimental work reported in
36. Goelzer, A. et al. Quantitative prediction of genome-wide resource Fig. 3, acquired the data and run the AMN and AMN-Reservoir codes to
allocation in bacteria. Metab. Eng. 32, 232–243 (2015). produce Figs. 4 and 5 and wrote the corresponding “Methods” section.
37. Niedenführ, S., Wiechert, W. & Nöh, K. How to measure metabolic W.L. contributed to designing the project and was involved in the disfluxes: a taxonomic guide for 13C fluxomics. Curr. Opin. Biotechnol. cussions and writing the manuscript. All authors read, edited, and
34, 82–90 (2015). approved the manuscript.
38. Willemsen, A. M. et al. MetDFBA: incorporating time-resolved
metabolomics measurements into dynamic flux balance analysis. Competing interests
Mol. Biosyst. 11, 137–145 (2015). The authors declare no competing interests.
39. Alghamdi, N. et al. A graph neural network model to estimate cellwise metabolic flux using single-cell RNA-seq data. Genome Res. Additional information
31, 1867–1884 (2021). Supplementary information The online version contains
40. Lachance, J.-C. et al. BOFdat: generating biomass objective func- supplementary material available at
tions for genome-scale metabolic models from experimental data. https://doi.org/10.1038/s41467-023-40380-0.
PLoS Comput. Biol. 15, e1006971 (2019).
41. Pandi, A. et al. Metabolic perceptrons for neural computing in Correspondence and requests for materials should be addressed to
biological systems. Nat. Commun. 10, 3880 (2019). Jean-Loup Faulon.
42. Chollet, F. et al. Keras. https://keras.io (2015).
43. Faure, L., Mollet, B., Liebermeister, W. & Faulon, J. L. A neural- Peer review information Nature Communications thanks the anonmechanistic hybrid approach improving the predictive power of ymous, reviewer(s) for their contribution to the peer review of this work.
genome-scale metabolic models. amn_release: v1.0.1. https://doi. A peer review file is available.
org/10.5281/zenodo.8056442 (2023).
44. Mackie, A. M., Hassan, K. A., Paulsen, I. T. & Tetu, S. G. Biolog Reprints and permissions information is available at
phenotype microarrays for phenotypic characterization of micro- http://www.nature.com/reprints
bial cells. in Environmental Microbiology: Methods and Protocols
(eds. Paulsen, I. T. & Holmes, A. J.) 123–130 (Humana Press, 2014). Publisher’s note Springer Nature remains neutral with regard to jur-
45. Harris, C. R. et al. Array programming with NumPy. Nature 585, isdictional claims in published maps and institutional affiliations.
357–362 (2020).
46. Virtanen, P. et al. SciPy 1.0: fundamental algorithms for scientific Open Access This article is licensed under a Creative Commons
computing in Python. Nat. Methods 17, 261–272 (2020). Attribution 4.0 International License, which permits use, sharing,
47. McKinney, W. Data structures for statistical computing in Python. in adaptation, distribution and reproduction in any medium or format, as
Proceedings of the 9th Python in Science Conference (eds. van der long as you give appropriate credit to the original author(s) and the
Walt, S. & Millman, J.) (SciPy, 2010). source, provide a link to the Creative Commons license, and indicate if
48. Abadi, M. et al. TensorFlow: large-scale machine learning on het- changes were made. The images or other third party material in this
erogeneous distributed systems. arXiv [cs.DC] https://doi.org/10. article are included in the article’s Creative Commons license, unless
48550/arXiv.1603.04467 (2016). indicated otherwise in a credit line to the material. If material is not
49. Hunter, J. D. Matplotlib: a 2D graphics environment. Comput. Sci. included in the article’s Creative Commons license and your intended
Eng. 9, 90–95 (2007). use is not permitted by statutory regulation or exceeds the permitted
50. Waskom, M. seaborn: statistical data visualization. J. Open. Source use, you will need to obtain permission directly from the copyright
Softw. 6, 3021 (2021). holder. To view a copy of this license, visit http://creativecommons.org/
licenses/by/4.0/.
Acknowledgements
J.L.F. would like to acknowledge funding provided by the ANR funding © The Author(s) 2023
agency grant numbers ANR-18-CE44-0015 (SynBioDiag project) and
Nature Communications | ( 2023)1 4:4669 14
