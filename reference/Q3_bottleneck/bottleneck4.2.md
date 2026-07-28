<!-- Page 1 -->

Single-cell RNA-seq interpretations using evolutionary
multiobjective ensemble pruning
Xiangtao Li, Shixiong Zhang, Ka-Chun Wong
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by
guest
on
22
July
2026

---

<!-- Page 2 -->

Bioinformatics, 35(16), 2019, 2809–2817
doi: 10.1093/bioinformatics/bty1056
Advance Access Publication Date: 28 December 2018
Original Paper
Gene expression
Single-cell RNA-seq interpretations using
evolutionary multiobjective ensemble pruning
Xiangtao Li 1,2, Shixiong Zhang 2 and Ka-Chun Wong 2,*
1School of Computer Science and Information Technology, Northeast Normal University, Changchun, Jilin, China
and 2Department of Computer Science, City University of Hong Kong, Hong Kong SAR
*To whom correspondence should be addressed.
Associate Editor: Inanc Birol
Received on July 26, 2018; revised on October 31, 2018; editorial decision on December 18, 2018; accepted on December 21, 2018
Abstract
Motivation: In recent years, single-cell RNA sequencing enables us to discover cell types or even sub-
types. Its increasing availability provides opportunities to identify cell populations from single-cell
RNA-seq data. Computational methods have been employed to reveal the gene expression variations
among multiple cell populations. Unfortunately, the existing ones can suffer from realistic restrictions
such as experimental noises, numerical instability, high dimensionality and computational scalability.
Results: We propose an evolutionary multiobjective ensemble pruning algorithm (EMEP) that
addresses those realistic restrictions. Our EMEP algorithm first applies the unsupervised dimension-
ality reduction to project data from the original high dimensions to low-dimensional subspaces;
basic clustering algorithms are applied in those new subspaces to generate different clustering
results to form cluster ensembles. However, most of those cluster ensembles are unnecessarily
bulky with the expense of extra time costs and memory consumption. To overcome that problem,
EMEP is designed to dynamically select the suitable clustering results from the ensembles.
Moreover, to guide the multiobjective ensemble evolution, three cluster validity indices including
the overall cluster deviation, the within-cluster compactness and the number of basic partition clus-
ters are formulated as the objective functions to unleash its cell type discovery performance using
evolutionary multiobjective optimization. We applied EMEP to 55 simulated datasets and seven real
single-cell RNA-seq datasets, including six single-cell RNA-seq dataset and one large-scale dataset
with 3005 cells and 4412 genes. Two case studies are also conducted to reveal mechanistic insights
into the biological relevance of EMEP. We found that EMEP can achieve superior performance over
the other clustering algorithms, demonstrating that EMEP can identify cell populations clearly.
Availability and implementation: EMEP is written in Matlab and available at https://github.com/
lixt314/EMEP
Contact: kc.w@cityu.edu.hk
Supplementary information: Supplementary data are available at Bioinformatics online.
1 Introduction
identifying cell types. The rapid development in RNA-seq enables us
Single-cell RNA-seq techniques have been proved to be effective for to sequence massive amounts of single-cell RNA-sequencing data,
discovering new cell types by detecting subpopulations in a hetero- which pose computational challenges; for instance, transcript ampli-
geneous cell population based on transcriptomic profiles. In fact, the fication noise, dropout events, high-dimensionality and data sparsity
identification of cell types from single-cell RNA-seq data is consid- (Kiselev et al., 2017; Wang et al., 2017). Those computational chal-
ered as a clustering problem in unsupervised learning. Therefore, lenges brought difficulties in developing effective unsupervised
computational methods including k-means, principal component clustering on single-cell RNA-seq data for cell population
analysis and spectral clustering (SC) are frequently adopted for interpretations.
VC The Author(s) 2018. Published by Oxford University Press. All rights reserved. For permissions, please e-mail: journals.permissions@oup.com 2809
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by
guest
on
22
July
2026

---

<!-- Page 3 -->

2810 X.Li et al.
In the past, application-specific unsupervised clustering methods EMEP shows its competitive edges over several state-of-the-art clus-
have been developed to address those computational challenges; for tering methods.
instance, Kiselev et al. (2017) proposed an unsupervised clustering
called single-cell consensus clustering (SC3), which integrates mul- 2 Materials and methods
tiple cluster labels by a consensus approach and can improve cell
type identification from the transcriptomes of neoplastic cells. Wang 2.1 Methodology overview of EMEP
et al. (2017) proposed single-cell interpretation via multikernel In this section, we propose the EMEP algorithm for single-cell RNA-
learning (SIMLR) by learning similarity measures from single-cell seq data. The framework of EMEP is summarized in Figure 1.
RNA-seq data. Zhu et al. (2017) applied the classic non-negative Considering an n(cid:2) m matrix X of single-cell RNA-seq data with n cells
matrix factorization (NMF), which is compared with other unsuper- and m genes, our proposed algorithm EMEP includes three important
vised clustering methods; the results demonstrate that the non-NMF components (Fig. 1). In the first component, NMF can be adopted for
can identify interaction modules. Zhang et al. (2018a) utilized mul- dimensionality reduction of the gene space (i.e. the single-cell RNA-seq
tiple single-cell populations from biological replicates (scVDMC) data matrix X). Algebraically, NMF can decompose X into the product
for single-cell RNA-seq interpretation. The scVDMC algorithm is a of the non-negative n(cid:2) r basis matrix W and the non-negative r(cid:2) m co-
multitask learning method with embedded feature selection to cap- efficient matrix H. With different numbers of rank models r in
ture the differentially expressed genes simultaneously. Zhang et al. Figure 1, we generate various basis vectors W ¼ fW 1 ; W 2 ; . . . ; W d g
(2018b) proposed an interpretable framework named DendroSplit for clustering, where d is the number of various basis vectors. In this
based on feature selection to uncover multiple levels of single-cell work, we set the number of rank models from 2 to 20. It is noted that
RNA-seq clustering problems. Park et al. (2018) proposed a novel any basic clustering algorithm can be chosen for clustering various basis
SC framework using multiple doubly stochastic similarity matrices vectors in the set W and obtain multiple cluster results. For example,
to form a similar matrix for clustering cell types. Yang et al. (2017) we can select the K-means (KM) clustering algorithm in this step be-
presented Single-cell Analysis via Iterative Clustering to find the op- cause of its simplicity and efficient performance.
timal set of signature genes for separating cells into distinct groups Then, EMEP removes some of the multiple cluster results p ¼
based on iterative clustering with the best parameters. However, it is fp 1 ; p 2 ; . . . ; p d g and further improves the generalization performance
hardly believed that each of those unsupervised clustering methods for clustering. Given a clustering algorithm C and the set of basis vec-
can be the all-time winner across all datasets for single-cell RNA-seq tors W ¼ fW 1 ; W 2 ; . . . ; W d g; C : W ! Y maps each basis vector W
interpretations. In fact, each clustering algorithm has its own to the label space Y and C s denotes the pruned ensemble with the
strengths and weaknesses; different clustering algorithms provide selected vectors s i 2 f0; 1gd where s i ¼ 1 means that the clustering re-
different performance on different single-cell RNA-seq datasets. sult on W i is chosen. To guide the multiobjective ensemble pruning,
Therefore, it is difficult for users to decide which clustering algo- three cluster validity indices (i.e. the overall cluster deviation, the
rithm is the most appropriate choice for single-cell RNA-seq data. within-cluster compactness and the number of basic ensemble parti-
Cluster ensembles have emerged as an effective method that can tions), are chosen as the objective functions, capturing multiple char-
integrate solutions from multiple individual unsupervised clustering acteristics of the evolving clusters during ensemble pruning. In the
algorithms into consensus results. Cluster ensembles have been evolution process, for different single-cell RNA-seq datasets, they re-
proved effective in solving real-world problems: ensemble clustering quire different consensus functions with different clustering algo-
for medical diagnostics (Greene et al., 2004), fuzzy ensemble cluster- rithms. Therefore, to cluster specific single-cell RNA-seq data,
ing (Avogadri and Valentini, 2009), link-based cluster ensemble different consensus functions with different clustering algorithms are
(LCE) method (Iam-On et al., 2010a,b), graph-based consensus clus- beneficial during different evolutionary stages. Therefore, a pool of
tering (Yu et al., 2007) for DNA microarray data, ensemble frame- distinct consensus functions with different clustering parameter set-
work for clustering protein–protein interaction networks (Asur tings is maintained throughout the evolution process, resulting in the
et al., 2007), ensemble non-NMF methods (Greene et al., 2008) and evolutionary selection competition among different clustering algo-
knowledge-based cluster ensemble for cancer discovery on biomo- rithms. Among the consensus functions available, we choose three of
lecular data (Yu et al., 2011). A detailed list of cluster ensembles them for concise diversity including the connected-triple-based simi-
could be referred to the past survey (Yang et al., 2010). larity (CTS) matrix, the SimRank-based similarity (SRS) matrix and
Unfortunately, most of those existing cluster ensembles methods can the approximate SimRank-based similarity (ASRS) matrix. For clus-
produce unnecessarily large ensembles at the expense of extra time tering, KM clustering algorithm, SC and clustering by fast search and
costs and memory consumption. To address those limitations, find of density peaks (CDP) are selected and compared.
ensemble pruning is proposed to select suitable clusters from the en-
2.2 Unsupervised dimensionality reduction
semble. In fact, the goal of ensemble pruning is to reduce the number
of clusters without any sacrifice on accuracy. Intuitively, the objec- To interpret high-dimensional single-cell RNA-seq datasets, NMF is
tives of ensemble pruning involve both maximizing the generaliza- employed to project data from the original high-dimensional spaces
tion performance and minimizing the number of clusters for to lower dimensional subspaces as the unsupervised dimensionality
regularization. Unfortunately, those two objectives are usually con- reduction (Gupta and Xiao, 2011). NMF (Lee and Seung, 2001) is a
flicting; the optimal decision needs to be enabled as the tradeoff be- well-studied unsupervised learning algorithm to decompose the ma-
tween those two objectives. In this case, it would be ideal to regard trix X into two non-negative matrices W 2 Rn(cid:2)r and H 2 Rr(cid:2)m by
ensemble pruning as a multiobjective problem rather than a single- minimizing the following objective (Frobenius norm) with non-
objective problem. Therefore, an evolutionary multiobjective ensem- negativity constraints on W and H:
b te l r e in p g ru a n l i g n o g ri ( t E h M ms EP a ) s i a s n pr e o n p s o em se b d le to ; i d t y c n a a n m b ic e a c ll o y n s s e i l d e e c r t e t d he as ba a si s c p c e l c u ia s- l LNMF ¼ jjX (cid:3) WHjj2 F ¼ P ij jX ij (cid:3) ðWHÞ ij j2; (1)
s:t: W; H (cid:4) 0;
case of weight ensemble clusters with binary weights. Extensive
comparisons with other methods on 55 simulated datasets, 7 real where jj (cid:5) jj denotes the Frobenius norm. To optimize the objective,
F
single-cell RNA-seq datasets and 2 case studies demonstrate that the following multiplicative update rules are iterated until convergence,
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by
guest
on
22
July
2026

---

<!-- Page 4 -->

Evolutionary ensemble pruning 2811
The first objective function concerns with the clustering devi-
ation; it computes the overall deviation of partitioning
(Mukhopadhyay et al., 2015). It is calculated as the total sum of dis-
tances between data points and their corresponding cluster centers.
X X
f 1 ¼ dðc k ; x iÞ (3)
ck2c xi2ck
where dðc
k
; x iÞ is the distance (e.g. Euclidean distance) between data
point x and its corresponding cluster center c . Based on this defin-
i k
ition, we can observe that it shares a similar strategy with KM.
The second objective function is to minimize the compactness of
clustering (Iam-on et al., 2010a,b); it is another commonly used
measurement. The compactness measures the average distance be-
tween every pairs of data points in the same cluster; it can be
expressed as follows:
f 2 ¼ 1 S XK a k P a xi; ð x a j2ck (cid:3) dð 1 x Þ i = ; 2 x jÞ ! (4)
k¼1 k k
where S is the number of cells in RNA-seq dataset. K denotes the
number of clusters. c is the kth cluster set. a is the number of cells
k k
belonging to the kth cluster. Conceptually, the elements in the same
group should be as close to each other as possible; thus, the f value
2
should be minimized.
The last objective function is to minimize the number of chosen
basic partition clusters for regularization. Given a clustering algo-
Fig. 1. The overall framework of the EMEP pipeline. (a) The first part is dimension-
rithm C and the set of basis vectors W, a map C : W ! Y between
ality reduction; NMF can be adopted for dimensionality reduction of gene space
each basis vector and the label space is constructed. Let C denotes
from the single-cell RNA-seq data matrix X. It is noted that, for various rank mod- s
els, the algorithm generates various basis vectors W; (b) The second part is the the sth pruned ensemble with the binary mask vector s i 2 f0; 1gd.
basic partitioning; for instance, the KM clustering algorithm can be chosen as the The number of basic partition clusters can be described as:
basic partitioning algorithm. For different basis vectors in the set W, the KM clus-
t t e h r ir in d g p a a l r g t o is rit E h M m E c P a . n It o r b e t m ai o n v m es ul t t h ip e le un cl s u u s i t t e a r bl s e ol c u lu tio st n e s r p re ¼ su f lt p s 1 f ; r p o 2 m ; .. t . h ; e pd e g n ; s ( e c m ) T b h le e . f 3 ¼ jjsjj ¼
Xd
s i (5)
i¼1
Adaptive selection between different consensus functions and clustering algo-
rithms is executed to produce the cluster solution ensemble iteratively
XHT
W ¼ W(cid:6) ;
WHHT 2.4 Pareto optimal approach
(2)
WTX In EMEP, we design the overall cluster deviation, the within-cluster
H ¼ H(cid:6)
WTWH compactness and the number of basic partition clusters as the object-
ive functions and treat the ensemble subsets from the whole multiple
After optimizing those objectives, the high-dimensional single-
clustering results as the candidate solutions to optimize those three cell RNA-seq datasets can be projected to lower dimensional sub-
objective functions. For the first and second objectives, the lower the spaces by NMF; it has been proved that the above updating process
score, the better-separated is the clustering between each basis vec-
can reach local minima of LNMF . With different rank models r,
tor W and the label space Y. For the third objective, the minimiza- NMF can obtain various basis matrices W. We arrange those basis
tion of chosen basic partition clusters is the goal of ensemble matrices W to a set W ¼ fW 1 ; W 2 ; . . . ; W d g. A clustering algorithm
pruning. Therefore, the problem of ensemble cluster pruning for can then be selected as the basic partitioning algorithm to cluster
high-dimensional single-cell RNA-seq datasets can be regarded as a
each of those different basis matrices in the set W and obtain mul-
multiobjective optimization problem on those objectives.
tiple clustering results p ¼ fp 1 ; p 2 ; . . . ; p d g.
Interpreting single-cell RNA-seq datasets under those three conflict-
ing objectives, the difficulty lies in the existence of explainable math-
ematical solution; each objective is usually conflicting to each other. In
2.3 Objective functions
other words, a solution good for one objective may be bad for another.
After dimensionality reduction, EMEP algorithm is proposed to
Therefore, it is hard to search for a solution that satisfies all objective
evolve multiple clustering results for RNA-seq cell type discovery.
functions; single optimality is not guaranteed for more than one object-
To guide the evolution, objective functions have to be carefully
ive. The relationship among those objectives can be described herein: a
designed. We note that the goal of ensemble pruning is to maximize
!
the generalization performance and minimize the number of chosen decision vector (also known as solution) p1 2 P is said to Pareto-dom-
basic partition clusters. Therefore, for the first goal, we consider ! ! !
two objective functions: (i) sum of distances between the cluster cen-
inate the decision vector p2 2 P if 8e 2 f1; . . . ; Eg; f eðp1Þ (cid:7) f eðp2Þ
! !
ters and its data points; (ii) data consistency within the same clus- and 9e 2 f1; . . . ; Eg; f e ðp1Þ < f eðp2Þ, where f eð(cid:5)Þ is the eth objective
ters. For the second goal, the third objective function is designed to function as previously defined and E is the number of objective func-
minimize the number of chosen basic partition clusters. tions for minimization.
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by
guest
on
22
July
2026

---

<!-- Page 5 -->

2812 X.Li et al.
If those conditions are satisfied, the decision vector (also known as 2.5.2 Mutation
! ! After the initialization phase, the evolution phase is mainly for mutation
solution) p1 2 P dominates the decision vector p2. Taking two objectives
and crossover operations. The mutation and crossover operations are
as an example, the relationship between the design space (i.e. solution
inspired from differential evolution (Das and Suganthan, 2011). The mu-
space) and the objective space can be exemplified in Figure 2. Ensemble
tation operation is employed to generate a mutant vector v correspond-
cluster pruning can be extended to find the non-dominated set of solu- i
ing to the solution vector p , which can be described as follows:
tions; its multiobjective optimization can be summarized as follows: i
min
8 >>>>>>>>>< f
f
1
2
¼
¼
X
1 c S k2 X c K x
X
i2c a k k
d
P
ðc
a
k
x
;
i; ð
x
x a j
i
2
Þ
c
;
k (cid:3) dð 1 x Þ i = ; 2 x jÞ ! ; (6) p w o h p e u re lat r i 1 o , n r . 2 F an is d a r 3 di a f
v
f r
j i
e e
¼
re t n h
p
t r
j r
i
1
e a e
þ
l w i
F
n e d
(cid:2)
i e g x h
ð
e
p
t s
j r
p
2
s a
(cid:3)
e r l a e
p
m c
j r
t
3
e e
Þ
t d
;
er ra c n a d ll o ed ml s y ca f l r e om fac t t
(
h o
8
e r
)
>>>>>>>>>:
f 3 ¼
Xd
k¼
S
1
i ;
k k that can scale the difference vector.
i¼1 2.5.3 Crossover
After the mutation phase, the crossover operation is applied to the target
Here, we design the EMEP algorithm based on the decomposition
vector p and the mutant vector v to produce the trial vector u as follows:
i i
method (tchebycheff approach) to elucidate all non-dominated solutions.
(cid:2) vj if randð0; 1Þ (cid:7) CR uj ¼ i
i pj Otherwise
i (9) 2 Fo .5 llo E w v in o g lu th ti e o p n r a ev ry iou m s u se l c t t i i o o b ns j , e E c M tiv E e P e is n p s r e o m po b se l d e f p o r r u c n lu i s n te g ring and sj i ¼ (cid:2) 1 0 i O f th u er j i w (cid:7) is 0 e :5
interpreting high-dimensional single-cell RNA-seq data in this section.
The EMEP process includes target vector definition, mutation, cross- where CR 2 ½0; 1(cid:8) is the crossover rate, which controls the fraction
over and the tchebycheff-based decomposition approach. The mutation of values copied from the mutant vector. This crossover operation
and crossover operations are mainly for updating the current individu- copies the jth parameter of the mutant vector v to the corresponding
i
als in the population. The tchebycheff decomposition approach focuses element in the trial vector u . Otherwise, It copies the jth parameter
i
on decomposing the multiobjective single-cell RNA-seq clustering from target vector p . After obtaining the u , it can be transformed
i i
problem into many single-objective single-cell RNA-seq clustering into the binary cluster selection space s , which is employed to select
i
subproblems. the base clusters to form an ensemble to produce the final clustering
result (p ) for the ith individual.
(cid:9)
2.5.1 Target vector definition 2.5.4 Tchebycheff decomposition approach
For initialization, a population with N parameter vectors encodes Given a basic clustering method C and a set of basis vectors W ¼
each candidate solution p i ¼ fp1 i ; p2 i ; . . . ; pd i g where i ¼ f1; 2; . . . ; fW igd i¼1 ; C : W ! Y maps the feature space W to the label space Y.
Ng; each vector (or candidate solution) is also associated to each After that, we can obtain multiple cluster results p ¼ fp 1 ; p 2 ; . . . ; p d g.
subprobem. The initial population should cover the entire search In our article, the number of basic cluster results is d. As we know,
space as much as possible by randomizing the individuals within the the goal of our proposed algorithm EMEP is to prune clusters from
upper and lower boundaries p max ¼ fp1 max ; p2 max ; . . . ; pj max g and the ensemble and further improve the generalization performance. To
p min ¼ fp1 min ; p2 min ; . . . ; pj min g: obtain the well-separated clusters with modal regularization, our algo-
rithm decomposes the problem into a number of single-objective sin-
pj ¼ pj þ randð0; 1Þ (cid:5) ðpj (cid:3) pj Þ; 8j ¼ f1; 2; . . . ; dg
i min max min gle-cell RNA-seq data clustering subproblems by the Tchebycheff
( sj ¼ 1 if pj i (cid:7) 0:5 (7) approach (Zhang and Li, 2007) and then optimize them simultan-
i 0 Otherwise eously. The Tchebycheff approach can be defined as follows:
where sj
i
¼ 1 means that the basic cluster C
j
is selected and sj
i
¼ 0 gteðpjkjÞ ¼
1
m
(cid:7)i
a
(cid:7)
x
E
fkj
i
jf iðpÞ (cid:3) z(cid:9)
i
jg;
(10)
means that the base cluster C is removed for the ith solution p .
j i i 2 f1; . . . ; Eg; j 2 f1; 2; . . . ; Ng
rand(0, 1) is a random variable within the range [0, 1].
where E is the number of objective functions; N is the number
of evenly spread weight vectors, which is also the population size;
kj ¼ fkj ; kj ; . . . ; kj g is the weight vector of jth individual and the
1 2 E
weight vector satisfies PE kj ¼ 1 and kj (cid:4) 0. z(cid:9) ¼ fz(cid:9); z(cid:9); . . . ; z(cid:9) g
i¼1 i i 1 2 E
is the ideal reference point for each z(cid:9)
i
< minff iðpÞjx 2 Xg. In this
article, we generate N weight vectors fk1 ¼ fk1; k1; . . . ; k1 g; k2 ¼
1 2 E
fk2; k2; . . . ; k2 g; . . . ; kN ¼ fkN; kN; . . . ; kNgg and decompose the
1 2 E 1 2 E
multiobjective single-cell RNA-seq data clustering problem into
N single objective single-cell RNA-seq data clustering problems.
Then, each individual represents a subproblem associated with the
weight vector k. The framework of EMEP for clustering single-cell
RNA-seq data is outlined in Supplementary Algorithm S1.
For the initialization phase, N weight vectors are generated
Fig. 2. Relationship between the design space and the objective space and so- according to the corresponding individual. Then the neighborhood
lution definition for two-objective problems index B is calculated by finding the T closest weight vectors. Each
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by guest
on
22
July
2026

---

<!-- Page 6 -->

Evolutionary ensemble pruning 2813
population member is randomly assigned with one of the consensus
functions from the pool and the associated basic clustering algo-
rithms are chosen randomly from the corresponding pool. Based on
the consensus functions and the basic clustering algorithm, the
selected cluster in s are combined to establish the final clustering re-
i
sult (p(cid:9)) for the ith individual. Next, three objective functions
f ; f ; f can be calculated to measure the performance of the cluster-
1 2 3
ing result (p(cid:9)). After that, the evolution phase is proposed for
population evolution using mutation and crossover operations.
By executing those two operations, we can obtain a new population
with the vector u . The new u can be transformed into the binary
i i
cluster selection space s which is employed to select the base clus-
i,
ters to form an ensemble to produce the final clustering result (p )
(cid:9)
for the ith individual by the corresponding consensus function and
basic clustering algorithm. After calculating those objective func-
tions, the neighbors of each subproblem are considered to compare Fig. 3. The proposed method of adaptive selection between consensus func-
with the current subproblem to find better solutions; its details are tions and basic clustering algorithms in a iterative manner. First, multiple
described in Supplementary Algorithm S2. If gteðu jkkÞ is higher cluster results p are obtained after applying NMF and the basic partitioning al-
k
than gteðp jjkkÞ, the individual p
j
is replaced by the new trial vector gorithm. pi and ui are two pruning solutions, which denote the selected clus-
ter results from p to form different ensembles receptively. Then, adaptive
u . After repeating this procedure for each subproblem, each off-
k selection can select a consensus function from the pool and then find the cor-
spring individual is compared with the current subproblem and its
responding clustering algorithm to produce the final cluster result. Three con-
neighbors in the original population. If the trial vector u is fitter
k sensus functions including the CTS matrix, the SRS matrix and the ASRS
than the target vector p j , it demonstrates that the combination of matrix are considered. For basic clustering algorithms in the pool, KM cluster-
selected consensus function and basic clustering algorithm are suit- ing algorithm, SC and CDP are selected. Finally, the new cluster result p(cid:9) and
1
able to analyze the current single-cell RNA-seq dataset of interest. p(cid:9) 2 can be obtained
Therefore, that combination will be stored for positive selection. If
the target vector p j has better performance than the new trial vector the CTS matrix (Klink et al., 2006), the SRS matrix (Calado et al.,
u k , it represents that this combination of consensus function and 2006) and the ASRS matrix (Iam-On et al., 2012) are considered. For
basic clustering algorithm is not very suitable for the current single- basic clustering algorithms in the pool, KM clustering algorithm, SC
cell RNA-seq dataset. Adaptive selection is employed to select the (Von Luxburg, 2007) and CDP published on Science (Rodriguez and
consensus functions and basic clustering algorithm from the pool, Laio, 2014) are selected to evolutionarily interpret those single-cell
exerting directional selection pressure on the fittest combination of RNA-seq datasets for cell population identification.
consensus functions and basic clustering algorithms.
2.7 Parameter settings
2.6 Pool selection of consensus functions and clustering
In order to evaluate the performance of EMEP, five parameters
algorithms
including the population size (N), the number of objective function
The effectiveness of ensemble algorithms for single-cell RNA-seq
evaluations, the scaling factor (F), the CR and the neighborhood size
datasets depends on the selected consensus functions and its associ-
(T) are set for scalability and flexibility. The detailed parameter set-
ated basic clustering algorithms. However, different single-cell
tings of our proposed EMEP are summarized as follows:
RNA-seq datasets require different consensus functions with various
clustering algorithms. In addition, to cluster single-cell RNA-seq 1. Settings for reproduction operators: The scaling factor (F) is 0.4
datasets, different consensus functions with different clustering algo- and CR is 0.1 as discussed in Supplementary Figure S1 and
rithms can compete and outperform each other at different stages of Supplementary Tables S1 and S2. The parameter analysis on
the evolution than a single consensus function with single clustering those values is summarized in Figure 4.
algorithm as in the ensemble algorithm. 2. Population size: The population size N is determined by the
Motivated by such observation, we propose an ensemble of con- simplex-lattice design factor H together with the objective number
sensus functions and clustering algorithms as adaptive selection for E (Deb and Jain, 2014); N ¼ CM(cid:3)1 where E is the number of
HþE(cid:3)1
evolutionary multiobjective optimization in which a pool of consensus objective functions in our proposed problem and H is set to three.
functions, along with a pool of algorithms corresponding to each asso- 3. Neighborhood size: T ¼ 4 (discussion in Supplementary Tables
ciated basic clustering algorithm competes to produce successful off- S3 and S4 and Fig. 4)
spring populations. The candidate pool of consensus functions and 4. Number of runs and stopping condition: Each algorithm is run
clustering algorithms is designed to exhibit diverse characteristics so 30 independent times on each dataset. Then, we compute the
that they can achieve robust performance characteristics in the evolu- averages of 30 independent runs and analyze the results on each
tion, as depicted in Figure 3. From this figure, p i and u i are two prun- single-cell RNA-seq dataset for fair comparisons. The 1000 ob-
ing solutions, which denote the selected cluster results from p to form jective function evaluations are adopted as the termination crite-
different ensembles. Each member is assigned with a consensus func- ria. (Li et al., 2017; Li and Wong, 2018).
tion and associated clustering algorithm taken from the respective
pools to produce the final cluster result. Then, if the generated trial
3 Results
vector produced u is better than the target vector p , the consensus
i i
function and associated clustering algorithm are retained with trial 3.1 Datasets
vector u which becomes the target vector in the next generation. For In this work, 55 simulated datasets based on a real human transcrip-
i
the pool of consensus functions, three consensus functions including tional regulation network of 2723 genes are adopted to validate the
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by
guest
on
22
July
2026

---

<!-- Page 7 -->

2814 X.Li et al.
obtained cluster labels and the true labels on each of those 55 simu-
lated datasets. To simulate the data for different subtypes (clusters),
Liu et al. (2017) assume that each subtype is characterized by a spe-
cific set of knocked-out genes. The set of the number of knocked-out
genes is [100, 200, 300, 400, 500]. The noise level is varied from [0,
0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]. Each knock-out
genes includes 11 instances for different noise levels. Therefore, for
various synthetic datasets, they have different knocked-out genes
with various noise levels. The detail description of those 55 synthetic
datasets for NMI was provided in Supplementary Table S5 and
Supplementary Fig. S2 (similarity results are obtained for ARI in
Supplementary Table S6 and Supplementary Fig. S2). From those
Tables, we found that for most datasets, EMEP is superior to other
computational methods. For 100 knock-out genes, EMEP can pro-
vide better solutions on 10 datasets. At the 0.5 noise level, SC, SSC
and MPSSC are superior to EMEP. For the rest dataset, EMEP
achieves promising results on some datasets by a large margin.
Fig. 4. Figures (a) and (b) denote the average NMI and ARI values versus the Meanwhile, we can observe that all algorithms can cluster the small
parameter analysis on F and CR under the same objective function evalua- noise levels clearly with high NMI since only light perturbations are
tions (i.e. 1000). Figures (c) and (d) denote the NMI and ARI values versus the applied for the human transcriptional regulation network. To com-
values of T for six small-scale single-cell RNA-seq datasets and the line chart pare the overall performance of those dataset, we also summarized
denotes the average values for those six small-scale single-cell RNA-seq data
the average value, as listed in the last column of Supplementary
Table S5. From the results, SC, SSC, MPSSC, SLMIR and EMEP are
performance of our proposed algorithm EMEP; the simulated data-
clearly superior to LCE, KM, CDP, t-SNE and ECC in regard to the
sets are generated based on the dynamical gene regulation model
average results. Meanwhile, EMEP is also competitive to, if not bet-
(Liu et al., 2017) as follows:
ter than, the SC, SSC, MPSSC and SLMIR. For the ARI, from the
dx experimental results in Supplementary Table S6, we can find that it
F i mRNAðx; yÞ¼ dt i ¼ m i (cid:5) f iðyÞ (cid:3) km i RNA (cid:5) x i ; has similar performance with the NMI. Therefore, we can conclude
F i Protðx; yÞ¼ d d y t i ¼ r i (cid:5) x i (cid:3) kP i rot (cid:5) y i ; (11) t t h er a i t ng ou a r lg p o r r o it p h o m se s d in a a lg c o o ri m th p m eti E ti M ve E m P a p n e n r e fo r. rms better than nine clus-
8i ¼ f1; . . . ; ng
where m is the maximum transcription rate and r is the translation 3.4 Application to single-cell RNA-seq datasets
i i
rate, kmRNA and kProt are the mRNA and protein degradation rates. In this section, we evaluate our proposed EMEP and other clustering
i i
f ið(cid:5)Þ is the relative activation of the ith gene. For the 55 synthetic algorithms including LCE, ECC, SC, KM, CDP, t-SNE, SIMLR, SSC
datasets, they are provided based on a real human transcription and MPSSC on those seven single-cell RNA-seq datasets containing
regulation network. Each dataset contains 200 samples, which are six small-scale datasets and one large-scale dataset. The detailed de-
classified into 4 clusters. The number of knock-out genes is varied scription of those seven single-cell RNA-seq datasets including the
from 100 to 500. The noise level is varied from 0 to 0.5. Each number of cells, the number of genes and the cell types are summar-
knock-out genes includes 11 instances for different noise levels. ized in Table 1. NMI and ARI are employed as the evaluation met-
On top of those 55 simulated datasets, six real-world single-cell rics. Figure 5 and Supplementary Table S7 summarize the clustering
RNA-seq datasets and one large-scale single-cell RNA-seq datasets performance of different algorithms measured by NMI on the six
(>3000 cells) are employed to test the cluster validity of EMEP. The small-scale single-cell RNA-seq data (Similar results are obtained
summary of the characteristics of the seven real single-cell RNA-seq using ARI; see Supplementary Table S8 and Fig. S3). For statistically
datasets is tabulated in Table 1. significant comparisons, the Paired Wilcoxonil signed rank test is
computed to perform statistically significant testing between pairs of
algorithms in Supplementary Tables S7 and S8. Three symbols
3.2 Competitive methods
including ‘þ’, ‘(cid:3)’ and ‘(cid:10)’, are designed based on P-value < 0.05.
The performance of EMEP is evaluated through comparative studies
The ‘(cid:10)’ denotes that there is not any significant difference between
including nine well-known clustering algorithms: LCE (Iam-On
two compared algorithms. The ‘þ’ denotes that our algorithm
et al., 2012), entropy-based consensus clustering (ECC) (Liu et al.,
EMEP is better than other algorithms while the ‘(cid:3)’ indicates the op-
2017), SC (Von Luxburg, 2007), KM clustering, CDP (Rodriguez
posite meaning. From the results, we found that EMEP, MPSSC and
and Laio, 2014), t-distributed stochastic neighbor embedding
SIMLR are superior to other seven clustering algorithms. From the
(t-SNE) (Maaten and Hinton, 2008), SIMLR (Wang et al., 2017),
Figure 5 and Supplementary Table S7, the EMEP is the best algo-
Sparse SC (SSC) (Von Luxburg, 2007) and SC based on learning
rithm while CDP algorithm performs the worst because it suffers
similarity matrix (MPSSC) (Park et al., 2018).
from the curse of dimensionality where the distances between all
pairs of points in the high dimensional and sparse data can become
3.3 Evaluation on simulated datasets meaningless. Moreover, our proposed algorithm EMEP can provide
Since all those simulated datasets have the truth labels, the external promising results on several datasets including Buettner, Deng and
measurements are applied to evaluate the performance of different Treutlin. On the Ting dataset, our algorithm EMEP can provide the
clustering algorithms. Two important external measurements nearly optimal accuracy. Meanwhile, we also compare EMEP with
including normalized mutual information (NMI) and adjusted rand t-SNE for those six single-cell RNA-seq data. t-SNE is a dimension-
index (ARI) are chosen for evaluating the consistency between the ality reduction technique that is particularly well suited for the
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by
guest
on
22
July
2026

---

<!-- Page 8 -->

Evolutionary ensemble pruning 2815
Table 1. Summary of the seven single-cell RNA-seq datasets
Dataset Cells (n) Genes (m) Cell types Depth (per cell)
Buettner (Buettner et al., 2015) 182 8989 3 (cid:11)3000 reads
Deng (Deng et al., 2014) 135 12548 7 (cid:11)40 000 reads
Ginhoux (Schlitzer et al., 2015) 251 11834 3 (cid:11)60 000 reads
Pollen (Pollen et al., 2014) 249 14805 11 (cid:11)50 000 reads
Ting (Ting et al., 2014) 114 14405 5 (cid:11)75 000 reads
Treutlein (Treutlein et al., 2014) 80 9352 5 (cid:11)62 500 reads
Zeisel (Zeisel et al., 2015) 3005 4412 9 (cid:11)50 000 reads
visualization of high-dimensional datasets. From the experimental
results, we can find that EMEP outperforms t-SNE on the six data-
sets; the differences between SIMLR and the t-SNE are often large,
especially for Buettner and Deng datasets. In addition to producing
2D embedding consistent with the true labels on each dataset, we
compare EMEP and t-SNE for 2D visualization as summarized in
Supplementary Figures S9 and S10. For the EMEP, the similarity
matrices for consensus functions from the data are obtained and then
the t-SNE is employed to visualize the similarity matrices. The axes
are in arbitrary units. Each point represents a cell and smaller distan-
ces between two cells represent greater similarity and vice versa.
None of the two methods used the true labels as inputs and the true
label information was added in the form of distinct colors to validate
the results. From those figures, EMEP can identify subpopulation
structures for most single-cell RNA-seq data such as Buettner dataset.
We observed that each of those three validated groups could be fur-
ther divided into subgroups and most of them are consistent with the
original cellular subpopulations (Buettner et al., 2015). As evidenced
by the experimental results, we can summarize that our algorithm
can produce better solutions than other state-of-the-art clustering
algorithms on most of the single-cell RNA-seq datasets. The reason is
Fig. 5. The performance of EMEP and other nine clustering algorithms including
that EMEP can optimize the basic partitions with ensemble pruning; LCE, ECC, SC, KM, CDP, t-SNE, SIMLR, SSC and MPSSC on the six small-scale
it can enable the expressive interpretations with sturdy stability. To single-cell RNA-seq datasets. The performance is measured using the NMI
compare the overall performance of those clustering algorithms, we
calculate the average values on those small-scale single-cell RNA-seq Zeisel et al. (2015) analyzed the transcriptomes of mouse brain cells
datasets as shown in Supplementary Tables S7 and S8; it demon- and the interneurons of similar type in dissimilar regions of the
strates that EMEP has significant advantages in a robust manner over brain. The Zeisel dataset includes nine subpopulations and 3005
multiple runs and trials. cells from the mouse brain. Ten clustering algorithms including
Among those small-scale single-cell RNA-seq datasets, we mainly LCE, ECC, SC, KM, CDP, t-SNE, SIMLR, SSC, MPSSC and EMEP
analyze two single-cell RNA-seq datasets, Buettner dataset (Buettner are employed to test the performance. The experimental results are
et al., 2015) and Ting dataset (Ting et al., 2014) for detailed insights. summarized in Supplementary Figure S4. As depicted in this figure,
The first dataset is the Buettner dataset which has 182 embryonic we can argue that our algorithm EMEP can provide better solutions
stem cells and 8989 genes with three clusters at different cell cycles than other compared methods even for such a big dataset.
(G1, M and G2M) based on the sorting of the Hoechst 33 342-
stained cell area of flow cytometry (FACS) distribution (Buettner 3.5 Case studies
et al., 2015). Figure 6a visualizes the heatmap of Buettner dataset Two case studies are conducted to reveal insights into EMEP on the
with three clusters and Figure 6c shows the 2D visualization of NCBI Gene Expression Omnibus (GEO) repository. The first case is
EMEP for Buettner dataset. We observe that our algorithm EMEP derived from pancreas islet single-cell-based identification of six
can yield significant clusters. The second single-cell RNA-seq dataset known human pancreas islet cell types (alpha cells, beta cells, delta
is Ting dataset including 114 pancreatic circulating tumor cells and cells, pp cells, acinar cells and duct cells) based on the known marker
14 405 genes with five clusters including single-cell transcriptomes genes (Jiang et al., 2018) in contact with the surrounding acinar and
from MEFs, the NB508 pancreatic cancer cell line, normal WBCs, ductal cells of the exocrine pancreas. The sequencing datasets of pan-
bulk primary tumors diluted to 10 or 100 pg of RNA and classical creas islet single cells can be found in the GEO repository under the
CTC (Ting et al., 2014). Figure 6b visualizes the heatmap of the Ting accession number GSE73727. In this dataset, 60 single cells including
dataset where we observe that five clusters can be found in the figure 18 alpha cells, 12 beta cells, 11 acinar cells, 8 duct cells, 2 delta cells
and Figure 6d shows the 2D visualization of EMEP for Ting dataset. and 9 pp cells are assayed for 4494 genes. The results of LCE, ECC,
Moreover, we also evaluate the robustness and effectiveness of SC, KM, CDP, t-SNE, SIMLR, SSC, MPSSC and EMEP are summar-
EMEP on the large-scale single-cell RNA-seq dataset. The Zeisel ized in Supplementary Figure S5. From the figure, EMEP provides
dataset is derived from the mouse cortex and hippocampus, which better solutions than other clustering algorithms. SIMLR and MPSSC
relies on unique molecule identifier assays and 3ndays counting. are the first and second runners-up in terms of NMI. For the external
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by
guest
on
22
July
2026

---

<!-- Page 9 -->

2816 X.Li et al.
Fig. 7. The clustering results from different clustering algorithms including LCE,
ECC, SC, KM, CDP, t-SNE, SIMLR, SSC, MPSSC and EMEP on the pancreas islet
Fig. 6. (a) Heatmap visualizes the Buettner dataset including 182 embryonic single cells dataset and Human Cancer Cells dataset. Cells that are grouped in the
stem cells and 8989 features with three clusters in the similarity matrix. same cluster are annotated in the same color in each column (i.e. each algorithm)
(b) Heatmap visualizes the Ting dataset including 114 pancreatic circulating
tumor cells and 14 405 features with five clusters using the similarity matrix.
(c) 2D visualization for Buettner dataset. (d) 2D visualization for Ting dataset
measurement ARI, EMEP obtains the best solution compared with
other algorithms while CDP is ranked the second for this pancreatic
islet single cells dataset. It indicates that EMEP is of good robustness
for single-cell RNA-seq datasets. The clustering results from different
clustering algorithms for the pancreatic islet single-cells datasets are
shown in Figure 7. Cells that are grouped in the same cluster are
annotated in the same color in each algorithm column.
The second case is human cancer cell dataset (Ramsko¨ld et al.,
2012), derived from Smart-Seq which accession number in GEO is
GSE38495. In this dataset, there are 33 cells and 3575 features with
seven clusters including hESC cells, LNCap cells, CTC cells, PC3 cells, Fig. 8. The performance of EMEP and other nine clustering algorithms includ-
SKMEL cells, T24 cells and UACC cells. The results of different clus- ing LCE, ECC, SC, KM, CDP, t-SNE, SIMLR, SSC and MPSSC on the low-depth
tering algorithms including LCE, ECC, SC, KM, CDP, t-SNE, SIMLR, single-cell RNA-seq dataset published in Nature Communications. (a) is the
SSC, MPSSC and EMEP are summarized in Supplementary Figure S6. performance of NMI and ARI; (b) is the 2D visualization for that dataset
From this figure, we can find that EMEP generally performs better
than the competitors for NMI. For ARI, we observe that EMEP pro- the best values while KM and CDP perform the worst. In addition, we
vides the best solutions while SSC performs the worst. Meanwhile, produce 2D embedding consistent with the true labels on Kimmerling
Figure 7 also depicts the actual clustering results on the human cancer dataset as shown in Figure 8b. From the figure, we can find that dif-
cells dataset, revealing the detailed insights provided by EMEP. ferent cells are clearly clustered in their own groups.
4 Discussion
3.6 Low-depth single-cell RNA-seq data
In this section, we conduct an experiment for comparing EMEP with In this study, a novel multiobjective ensemble algorithm based on evo-
other computational methods on a low-depth single-cell RNA-seq lutionary pruning (EMEP) is proposed based on the observation that
Data published in Nature Communications (Kimmerling et al., 2016). not all clustering results are suitable for all single-cell RNA-seq data
This single-cell libraries were sequenced on a NextSeq500 using 30- distribution. In the algorithm, a dimensionality reduction method is
bp paired end reads to an average depth of 1 229 637 6 60 907 reads employed to project data from the original high-dimensional space to
((cid:11)6000 reads per cell) (Streets and Huang, 2014). After that, low-dimensional subspaces. Three different cluster validity indices
Kimmerling dataset was created to test the C1 platform including 194 including the overall cluster deviation, the cluster compactness and
mouse cell lines with 23420 features. It consists of two groups includ- the number of chosen basic partition clusters are proposed as object-
ing C1: 89 L1210, mouse lymphocytic leukemia cells, and 105 mouse ive functions to capture multiple characteristics of the evolving clus-
CD8þ T-cells (Kimmerling et al., 2016). Five cells with less than 500 ters. After that, EMEP is proposed to remove unsuitable clusters from
non-zero genes were omitted. The data can be downloaded in the the ensemble, improving the generalization performance. Based on
GEO repository under the accession number GSE74923. The experi- the experimental results, EMEP can demonstrate significate advan-
ment results of LCE, ECC, SC, KM, CDP, t-SNE, SIMLR, SSC, tages in terms of NMI and ARI, compared with 9 clustering methods
MPSSC and EMEP are summarized in Figure 8a. From the figure, we on more than 60 single-cell RNA-seq datasets. Two case studies
can find that EMEP has the highest NMI values; it represents that including pancreatic islet single cells and human cancer cells are con-
EMEP performs better than their competitors. This demonstrates that ducted to demonstrate that EMEP can clearly distinguish different cell
the proposed methods can optimize the basic partitions with ensemble types from single-cell RNA-seq data.
pruning. Except EMEP, t-SNE can provide better NMI values than Although EMEP has a good performance for single-cell RNA-seq
other computational methods. Meanwhile, LCE, ECC and SIMLR data, there are some limitations in this algorithm. Since EMEP is an
can generate the same NMI values. For ARI, EMEP also can provide ensemble-based method, it can be usually time-consuming with high
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by
guest
on
22
July
2026

---

<!-- Page 10 -->

Evolutionary ensemble pruning 2817
complexity (discussion in Supplementary Material). Moreover, the Iam-On,N. et al. (2010b) Linkclue: a matlab package for link-based cluster
final solution depends on the choice of the ensemble algorithm. ensembles. J. Stat. Softw., 36, 1–36.
Meanwhile, since evolutionary algorithms are stochastic, there is no Iam-On,N. et al. (2012) A link-based cluster ensemble approach for categoric-
al data clustering. IEEE Trans. Knowl. Data Eng., 24, 413–425.
guarantee that two runs under the same conditions will find the same
Jiang,H. et al. (2018) Single cell clustering based on cell-pair differentiability
solutions. Itol very hard to theoretically prove and design mutation
correlation and variance analysis. Bioinformatics, 1, 11.
and crossover operations to detect the appearance of the ‘best’ point.
Kimmerling,R.J. et al. (2016) A microfluidic platform enabling single-cell
Therefore, in this study, we run the EMEP algorithm for 30 inde-
RNA-seq of multigenerational lineages. Nat. Commun., 7, 10220.
pendent times on each single-cell RNA-seq dataset and compute the Kiselev,V.Y. et al. (2017) Sc3: consensus clustering of single-cell RNA-seq
averages for statistically significant comparisons. data. Nat. Methods, 14, 483.
For further studies, from the perspective of multiobjective evolu- Klink,S. et al. (2006) Analysing social networks within bibliographical data.
tionary optimization for single-cell RNA-seq data, multiobjective evo- In: International Conference on Database and Expert Systems Applications,
lutionary optimization including encoding schemes and selection of Stephane,B. et al. (eds) pp. 234–243. Springer, Berlin, Heidelberg.
final solution from the non-dominated front is still lacking. Therefore, Lee,D.D. and Seung,H.S. (2001) Algorithms for non-negative matrix factor-
ization. In: Advances in Neural Information Processing Systems, MIT Press,
studies are needed to consider those areas. Meanwhile, we believe that
Cambridge, MA, USA, pp. 556–562.
our study provides a refreshing view on the use of multiobjective opti-
Li,X. and Wong,K.-C. (2018) Evolutionary multiobjective clustering and its appli-
mization for single-cell RNA-seq, enabling numerous downstream
cations to patient stratification. IEEE Trans. Cybernetics, 99, 1–14.
studies on the multiobjective formulation in other problems.
Li,X. et al. (2017) Evolving spatial clusters of genomic regions from
high-throughput chromatin conformation capture data. IEEE Trans.
Nanobiosci., 16, 400–407.
Acknowledgements
Liu,H. et al. (2017) Entropy-based consensus clustering for patient stratifica-
tion. Bioinformatics, 33, 2691–2698.
The authors would like to thank reviewers for their reading time and con-
Maaten,L. v d. and Hinton,G. (2008) Visualizing data using t-sne. J. Mach.
structive comments.
Learn. Res., 9, 2579–2605.
Mukhopadhyay,A. et al. (2015) A survey of multiobjective evolutionary clus-
Funding tering. ACM Comput. Surveys, 47, 1.
Park,S. et al. (2018) Spectral clustering based on learning similarity matrix.
This work was supported by three grants from the Research Grants Council Bioinformatics, 1, 8.
of the Hong Kong Special Administrative Region [CityU 21200816], [CityU Pollen,A.A. et al. (2014) Low-coverage single-cell mRNA sequencing reveals
11203217] and [CityU 11200218]. This research is also supported by the cellular heterogeneity and activated signaling pathways in developing cere-
National Natural Science Foundation of China under [Grant No. 61603087] bral cortex. Nat. Biotechnol., 32, 1053.
and funded by the Natural Science Foundation of Jilin Province under [Grant Ramsko¨ld,D. et al. (2012) Full-length mRNA-seq from single-cell levels of
No. 20190103006JH]. Meanwhile, this research is also supported by the RNA and individual circulating tumor cells. Nat. Biotechnol., 30, 777.
Fundamental Research Funds for the Central Universities [No. Rodriguez,A. and Laio,A. (2014) Clustering by fast search and find of density
2412017FZ026]. peaks. Science, 344, 1492–1496.
Schlitzer,A. et al. (2015) Identification of cdc1-and cdc2-committed dc pro-
Conflict of Interest: none declared.
genitors reveals early lineage priming at the common dc progenitor stage in
the bone marrow. Nat. Immunol., 16, 718.
Streets,A.M. and Huang,Y. (2014) How deep is enough in single-cell
References
RNA-seq? Nat. Biotechnol., 32, 1005.
Asur,S. et al. (2007) An ensemble framework for clustering protein–protein Ting,D.T. et al. (2014) Single-cell RNA sequencing identifies extracellular matrix
interaction networks. Bioinformatics, 23, i29–i40. gene expression by pancreatic circulating tumor cells. Cell Rep., 8, 1905–1918.
Avogadri,R. and Valentini,G. (2009) Fuzzy ensemble clustering based on random Treutlein,B. et al. (2014) Reconstructing lineage hierarchies of the distal lung
projections for DNA microarray data analysis. Artif. Intell. Med., 45, 173–183. epithelium using single-cell RNA-seq. Nature, 509, 371.
Buettner,F. et al. (2015) Computational analysis of cell-to-cell heterogeneity Von Luxburg,U. (2007) A tutorial on spectral clustering. Stat. Comput., 17,
in single-cell RNA-sequencing data reveals hidden subpopulations of cells. 395–416.
Nat. Biotechnol., 33, 155. Wang,B. et al. (2017) Visualization and analysis of single-cell RNA-seq data
Calado,P. et al. (2006) Link-based similarity measures for the classification of by kernel-based similarity learning. Nat. Methods, 14, 414.
web documents. J. Am. Soc. Inform. Sci. Technol., 57, 208–221. Yang,L. et al. (2017) Saic: an iterative clustering approach for analysis of sin-
Das,S. and Suganthan,P.N. (2011) Differential evolution: a survey of the gle cell RNA-seq data. BMC Genomics, 18, 689.
state-of-the-art. IEEE Trans. Evol. Comput., 15, 4–31. Yang,P. et al. (2010) A review of ensemble methods in bioinformatics. Curr.
Deb,K. and Jain,H. (2014) An evolutionary many-objective optimization algo- Bioinformatics, 5, 296–308.
rithm using reference-point-based nondominated sorting approach, part i: solv- Yu,Z. et al. (2007) Graph-based consensus clustering for class discovery from
ing problems with box constraints. IEEE Trans. Evol. Comput., 18, 577–601. gene expression data. Bioinformatics, 23, 2888–2896.
Deng,Q. et al. (2014) Single-cell RNA-seq reveals dynamic, random monoal- Yu,Z. et al. (2011) Knowledge based cluster ensemble for cancer discovery
lelic gene expression in mammalian cells. Science, 343, 193–196. from biomolecular data. IEEE Trans. Nanobiosci., 10, 76–85.
Greene,D. et al. (2004) Ensemble clustering in medical diagnostics. In: Zeisel,A. et al. (2015) Cell types in the mouse cortex and hippocampus
Computer-Based Medical Systems, 2004. CBMS 2004. Proceedings. revealed by single-cell RNA-seq. Science, 347, 1138–1142.
17th IEEE Symposium on, Olivier,C. (ed), pp. 576–581. IEEE, Bethesda. Zhang,H. et al. (2018a) A multitask clustering approach for single-cell
Greene,D. et al. (2008) Ensemble non-negative matrix factorization methods for RNA-seq analysis in recessive dystrophic epidermolysis bullosa. PLoS
clustering proteinymposium onDeng</snam. Bioinformatics, 24, 1722–1728. Comput. Biol., 14, e1006053.
Gupta,M.D. and Xiao,J. (2011) Non-negative matrix factorization as a fea- Zhang,J.M. et al. (2018b) An interpretable framework for clustering
ture selection tool for maximum margin classifiers. In: Computer Vision and single-cell RNA-seq datasets. BMC Bioinformatics, 19, 93.
Pattern Recognition (CVPR), 2011 IEEE Conference on, Colorado Springs, Zhang,Q. and Li,H. (2007) Moea/d: a multiobjective evolutionary algorithm
CO, USA, pp 2841–2848. based on decomposition. IEEE Trans. Evolution. Comput., 11, 712–731.
Iam-On,N. et al. (2010a) Lce: a link-based cluster ensemble method for Zhu,X. et al. (2017) Detecting heterogeneity in single-cell RNA-seq data by
improved gene expression data analysis. Bioinformatics, 26, 1513–1519. non-negative matrix factorization. PeerJ., 5, e2888.
Downloaded
from
https://academic.oup.com/bioinformatics/article/35/16/2809/5265329
by
guest
on
22
July
2026
