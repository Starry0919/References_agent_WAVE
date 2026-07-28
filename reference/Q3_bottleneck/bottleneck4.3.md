<!-- Page 1 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Microbial Cell Factories
https://doi.org/10.1186/s12934-023-02277-x
METHODOLOGY Open Access
FastKnock: an efficient next-generation
approach to identify all knockout strategies
for strain optimization
Leila Hassani1†, Mohammad R. Moosavi1*†, Payam Setoodeh2,3† and Habil Zare4,5*†
Abstract
Overproduction of desired native or nonnative biochemical(s) in (micro)organisms can be achieved
through metabolic engineering. Appropriate rewiring of cell metabolism is performed by making rational changes
such as insertion, up-/down-regulation and knockout of genes and consequently metabolic reactions. Finding
appropriate targets (including proper sets of reactions to be knocked out) for metabolic engineering to design
optimal production strains has been the goal of a number of computational algorithms. We developed FastKnock,
an efficient next-generation algorithm for identifying all possible knockout strategies (with a predefined maximum
number of reaction deletions) for the growth-coupled overproduction of biochemical(s) of interest. We achieve
this by developing a special depth-first traversal algorithm that allows us to prune the search space significantly.
This leads to a drastic reduction in execution time. We evaluate the performance of the FastKnock algorithm
using various Escherichia coli genome-scale metabolic models in different conditions (minimal and rich mediums)
for the overproduction of a number of desired metabolites. FastKnock efficiently prunes the search space to less than
0.2% for quadruple- and 0.02% for quintuple-reaction knockouts. Compared to the classic approaches such
as OptKnock and the state-of-the-art techniques such as MCSEnumerator methods, FastKnock found many more
beneficial and important practical solutions. The availability of all the solutions provides the opportunity to further
characterize, rank and select the most appropriate intervention strategy based on any desired evaluation index. Our
implementation of the FastKnock method in Python is publicly available at https:// github. com/ leila hsn/ FastK nock.
Keywords Genome-scale metabolic model, Reaction knockout strategy, Growth-coupled biosynthesis, Biochemical
overproduction, Mathematical optimization, Reaction clustering, Search space reduction
†Leila Hassani and Mohammad R. Moosavi contributed equally. 5 Glenn Biggs Institute for Alzheimer’s & Neurodegenerative Diseases,
University of Texas Health Science Center, San Antonio, USA
†Payam Setoodeh and Habil Zare contributed equally.
*Correspondence:
Mohammad R. Moosavi
smmosavi@shirazu.ac.ir
Habil Zare
zare@uthscsa.edu
1 Department of Computer Science and Engineering and IT, School
of Electrical and Computer Engineering, Shiraz University, Shiraz, Iran
2 Department of Chemical Engineering, School of Chemical, Petroleum
and Gas Engineering, Shiraz University, Shiraz, Iran
3 Booth School of Engineering Practice and Technology, McMaster
University, Hamilton, ON, Canada
4 Department of Cell Systems and Anatomy, University of Texas Health
Science Center, San Antonio, TX, USA
© The Author(s) 2024. Open Access This article is licensed under a Creative Commons Attribution 4.0 International License, which
permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the
original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or
other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line
to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory
regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this
licence, visit http:// creat iveco mmons. org/ licen ses/ by/4. 0/. The Creative Commons Public Domain Dedication waiver (http:// creat ivec o
mmons. org/ publi cdoma in/ zero/1. 0/) applies to the data made available in this article, unless otherwise stated in a credit line to the data.

---

<!-- Page 2 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 2 of 22
Introduction combination of eliminations were identified [15,
Metabolic engineering aims at the proper rewiring of 33–36].
cell metabolism to construct genetically engineered There are two basic conventional approaches for
strains that can serve as robust cell factories for a designing metabolic intervention strategies: top-down
variety of purposes, including the biosynthesis of target (e.g., OptKnock [33], OptGene [37], MoMAKnock [34],
substances [1]. Extensive studies have been conducted CiED [38]) and bottom-up (e.g., FSEOF [39], CosMos
in this field to develop methods for efficiently [40]) procedures [41, 42]. The top-down strategies are
producing suitable natural compounds by using either used to determine whether the potential interventions
native cells or heterologous hosts [2, 3]. Systems are advantageous and they iteratively search for
metabolic engineering employs the concepts and the metabolic reaction network of interest until the
capabilities of systems biology, synthetic biology, and optimal solutions are identified. The search space in the
evolutionary engineering at the systems level. It uses corresponding problems includes all combinations of
approaches from these disciplines and combines them a predefined number of reactions in a GEM. Due to the
with standard metabolic engineering techniques to size of the developed and highly curated GEMs, this
facilitate the development of high-performance strains search space is extremely large and would explode with
[4–7]. Metabolic systems biology plays a significant the cardinality of the combination. Thus, it would not be
role in systems metabolic engineering because it feasible to conduct an exhaustive exploration within a
incorporates a systems-level perspective on cellular reasonable time frame.
metabolic functionalities [8–11]. Using metabolic Optimization techniques are commonly proposed
systems biology, scholars can integrate omics data with to address this computational challenge. For example,
results from genome-scale computational simulations OptKnock [33] is one of the most popular top-down
to improve metabolic engineering techniques. These frameworks. It uses bi-level optimization for in silico
techniques can lead to the development of potentially metabolic engineering. It aims to identify the appropriate
productive and operationally optimized microbial sets of genes or reactions that, when knocked out,
strains [10–13]. maximize the production rate of the desired biochemical
The growth-coupled overproduction of (bio) coupled with biomass formation. To find an optimal
chemicals is one of the most vital and practical solution for the growth-coupled production of the
objectives in systems metabolic engineering. Using biochemical(s) of interest, OptReg [31] expands the
this approach, synthesis of a desired compound can capabilities of OptKnock by predicting appropriate
be guaranteed along with the reproduction of the up- or down-regulation of revealed crucial genes or
engineered cell(s) [14, 15]. Genome-scale metabolic reactions. RobustKnock [43] has been developed based
network reconstructions (GENREs) [16] and their on optimization techniques that guarantee the minimum
relevant mathematical representatives (genome-scale production rate of the desired biochemical. Despite its
metabolic models (GEMs)) have been developed for novel approach, RobustKnock has not been widely used
numerous microorganisms (e.g., Escherichia coli [17– due to the difficulty of implementation.
20], Pseudomonas putida [21, 22], and Saccharomyces The challenge in employing these optimization
cerevisiae [23–26]). These tools are commonly used in approaches is that the time required for finding an
computational systems biology for in silico production optimal solution grows exponentially with the cardinality
strain design. In particular, biased COnstraint-Based of the combination. Worse, the solvers may fall into a
Reconstruction and Analysis (COBRA) computational deadlock situation and become trapped in an infinite
techniques such as flux balance analysis (FBA) [27] loop. Several metaheuristic algorithms have been
and flux variability analysis (FVA) [28] are useful in proposed to overcome this obstacle. These algorithms
analyzing GEMs [11, 12, 29, 30] (Additional file 1: can pinpoint the suboptimal solutions within a
Supplement A). Using COBRA, one can take advantage reasonable time. For example, BAFBA [44] is a top-down
of the synergistic effects of a variety of basic elements metaheuristic method that deploys the bees algorithm
including genes, gene products and metabolites to [45] to find candidate gene knockouts and evaluate the
evaluate cells’ potential and make model-driven results through FBA (Additional file 1: Supplement A).
discoveries. Accordingly, in silico studies based on Bottom-up approaches discover appropriate
systems-level analyses inspire researchers to examine intervention strategies by comparing two flux
intervention strategies, including gene or reaction distributions. One of these distributions relates to the
insertions, knockouts, and up- or down-regulations wild-type, which aims to maximize the cell’s growth
[31, 32]. For example, in several studies on gene rate. The other distribution relates to the functional
and reaction knockouts, the candidates for the best state, which takes into account the goal of the desired

---

<!-- Page 3 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 3 of 22
biochemical overproduction. Examples include In this paper, we present FastKnock as a next-
the flux distribution comparison analysis (FDCA) generation knockout strategy algorithm that provides
algorithm [46] and OptForce [32]. Using OptForce, all the user with all possible solutions for multiple gene
coordinated reaction modifications contributing to and reaction knockouts to overproduce a (bio)chemical
target overproduction are identified based on significant of interest. Unlike the MCSEnumerator approach,
differences between the two flux patterns (initial and FastKnock does not rely on any special parameter settings
desired) in the introduced network, calculated using and additional assumptions (except for predefining the
FVA. FVA finds the boundaries of the reaction fluxes that maximum number of simultaneous reaction knockouts).
can satisfy the optimality of the solution under steady- We developed a delicate search and prune algorithm to
state flux analysis (Additional file 1: Supplement A). accomplish this goal at a greatly reduced computational
In a nutshell, primitive top-down approaches use time and cost. Our method combines (and benefits
optimization methods to find an optimal solution at from) both basic approaches to tackle the problems
the cost of significant execution time. While top-down described above. It incorporates reaction knockouts to
metaheuristic approaches require less computational couple the biosynthesis of both primary (e.g., succinate,
resources, they are not guaranteed to find a globally lactate, ethanol, etc.) and secondary metabolites (e.g.,
optimal solution because the search space contains many dodecanoic acid, polyketides such as erythromycin and
local optima. On the other hand, bottom-up approaches terpenoids such as lycopene) with cell reproduction. It
can be used to find a set of potential solution candidates examines the GEM at the level of metabolic reactions
[14]. Despite various integrated computational and while checking the corresponding genes to consider the
experimental studies, it is challenging to identify the gene dependency of the reactions.
most proper and operative alterations by only comparing The availability of all solutions allows us to
the flux distributions of the wild-type to the ideally systematically characterize and rank these strategies in
engineered states. Considering high order cardinalities accordance with some criteria including (a) substrate-
and interventions [47] adds to the complexity of the specific productivity (SSP) [14, 15, 55, 56], (b) strength
problem. of growth coupling (SoGC), defined as the square of
State-of-the-art approaches have been developed to the product yield per unit substrate divided by the
dramatically alleviate the computational challenges and slope of the lower edge of the production curve [14,
significantly reduce the computational costs including 15, 55, 56], (c) strain dynamic performance, which
(iteratively) pruning the search space [48, 49] and depends on yield, productivity, and titer [57, 58], and (d)
sequentially enumerating the smallest minimal cut sets other important indices reflecting environmental and
(MCSs) in order to provide several solutions [50]. For operational considerations such as minimal production
example, Fast-SL properly explores a metabolic network of undesired or toxic byproducts and the feasibility of
of interest to find the most appropriate synthetic lethal C O biofixation. Some alternative criteria are discussed
2
reaction sets. Fast-SL improves the performance of a in [59]. Furthermore, it would be possible to evaluate
brute-force search algorithm by iteratively reducing the the solutions and categorize them in the different major
size of the search space, which substantially shortens the classes: potentially, weakly, directionally growth-coupled
execution time [49]. MCSEnumerator is another novel production (pGCP, wGCP, dGCP) and substrate-uptake
method that attempts to find many solutions using MCSs coupled production (SUCP) raised in [60].
aimed at the identification of either synthetic lethal sets The article is structured as follows: Initially, the
or optimal strain design targets [50]. FastKnock algorithm is introduced. Subsequently, we
Calculating the MCSs in GEMs is a complex and present the outcomes of in silico experiments utilizing
challenging computational problem [51]. The scalability meticulously curated GEMs of E. coli. Finally, discussions
of MCSEnumerator algorithms paves the way for both and conclusions are articulated.
theoretical and practical studies considering high-order
simultaneous reaction interventions for strong growth- The proposed method
coupled product formation [52, 53]. However, for in silico We developed the FastKnock algorithm, a versatile
strain design, the MCSEnumerator approach require framework intended to enhance the production rate of a
predefining of the acceptable thresholds for growth and targeted metabolite within a cell while promoting growth.
target product yields and this contributes to different This desired metabolite may belong to either a primary or
drawbacks such as neglection of some appropriate secondary category and can be of native or heterologous
suboptimal solutions [54]. origin. Specifically, the algorithm can be applied to

---

<!-- Page 4 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 4 of 22
heterologous metabolites through the inclusion of the Testing whether a set of reactions is a proper solution
associated pathways into the GEM set. is equivalent to solving an optimization problem in
In other words, FastKnock identifies reactions to be which the objective function is the growth of the
deleted from the network while ensuring that the flux of cell and the elimination of reactions corresponds to
the biomass formation reaction remains above a specific modifying the associated constraints of the optimization
cut-off (i.e., 1% of gr , (Additional file 1: Supplement D) problem (Additional file 1: Supplement F). By solving
WT
and maximizes the production of the desired substance(s) this optimization problem, we obtain the flux of all the
[61]. For practical applications, FastKnock can be utilized reactions including the production rate of a desired
to identify subsets of network reactions that can be biochemical. An appropriate solution (i.e., a knockout
removed to significantly enhance the production of the strategy) should satisfy the objective function along
desired biochemical. Specifically, FastKnock identifies with providing a suitable production rate for the desired
the strains in which the production rate of the desired biochemical product.
biochemical surpasses a predefined threshold in the base To find all reaction subsets of size ≤ k, we employ a
model (i.e., the model without any interventions). We tree-based representation that encompasses all combina-
refer to this threshold as Th , defined as 5% of the tions of reactions with a maximum size of k, as outlined
chemical
maximum theoretical yield (i.e., the optimal production below. Figure 1 illustrates the overall procedure using
rate of the desired biochemical when it is considered a depth-first traversal tree. The root node at level zero
the objective of the cell metabolism) in the base model. corresponds to the base model in which no reaction is
FastKnock, like other common approaches, employs deleted (i.e., the reduced model). All sets of k reactions
preprocessing to reduce the size of metabolic model are placed in nodes of the tree in depth k (i.e., at the level
reactions and the search space. In the preprocessing k). The FastKnock procedure starts with investigating the
phase (Additional file 1: Supplement C), a subset of elimination of a single arbitrary reaction r at level one.
1
reactions is identified and structurally excluded from the Whether knocking out r is a solution or not, we proceed
1
metabolic network to generate a reduced model denoted to explore the simultaneous elimination of r and another
1
as Reduced_model. Additionally, the set of candidate reaction at level two. At each level, we consider only the
reactions for deletion from the model is determined and reactions with nonzero flux, determined by the optimiza-
denoted as Removable. tion problem solved in the parent node at the upper level
The search space of the exhaustive search includes all (Additional file 1: Supplement F, part 2). The procedure
members of the power set of the Removable set with a of adding reactions with nonzero flux to the set of knock-
particular maximum cardinality. out reactions continues at lower levels of the tree until
The search space grows exponentially as the size of one of the two stopping conditions is met: a) we reach a
the set increases. Therefore, conducting an exhaustive leaf at level k (the predefined number of knockouts), or
search and examining all subsets of reactions is highly b) we reach a node guaranteed to have no solution in its
time-consuming and infeasible. To address this challenge, subtree.
our proposed algorithm utilizes information available To check condition b in each node at level l < k, we
only during the search procedure to dynamically narrow determine whether the subtree may lack a solution
the search space—iteratively pruning the space and by investigating the optimization problem. If the
temporarily excluding certain reactions. This reduced optimization problem already indicates an infeasible
search space is employed to identify knockout strategies, region at a node, adding more constraints in the subtree
and we refer to it as the target space. of the node would not lead to a proper solution (see
Additional file 1: Supplement F).
The FastKnock algorithm The merit of the procedure is the technique of
Our proposed method aims to identify all solutions bounding the search by a) excluding the reactions with
to a strain optimization problem (with a predefined zero flux at each node from the target space of the node
maximum number of reaction deletions), enabling (Additional file 1: Supplement F, part 2) and b) checking
the growth-coupled overproduction of a metabolite the feasibility of reaching a solution before expanding the
(biochemical) of interest. Each solution represents a set subtree of each node. If a reaction has zero flux based on
of k reactions (i.e., a knockout strategy) in which the the functional state of a node in the traversal tree, it is
elimination of these reactions results in a new engineered excluded from the target space of that node. However,
strain, coupling the overproduction of the biochemical of in the children of that node, the functional states may
interest with cell growth. change and the reaction can get nonzero flux. Thus, it

---

<!-- Page 5 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 5 of 22
Fig. 1 The traversal tree: All possible solutions are identified through a depth-first traversal of the tree. First, the identifyTargetSpace function
is applied in the root node to the reduced wild-type network to determine the target space. Each reaction in this set is individually selected
and removed from the network in Level 1. For each deleted reaction (or equally node) in Level 1, the identifyTargetSpace function is recalled
to obtain the target space for the next level. For simplicity, we show only two levels of the traversal of the tree, which is enough to identify all single
and double deletions
might reappear in the search space when we explore all reactions that could potentially be added to deleted_
the descendants at consequent levels. This dynamic rxns for investigation at the next level.
and effective pruning of the search space enhances the Determining the target space at each node is critical,
efficiency of the algorithm. and it allows us to avoid the combinatorial explosion of
Algorithm 1 represents the definition of a node in the the tree that would inevitably result from an exhaustive
tree, as well as, the main procedure of the FastKnock search. In particular, while we investigate drastically
algorithm. Each instance of the Node contains the model, fewer subsets of reactions at the children nodes in Level
the set of the removed reactions, the search space, and L + 1, our analysis guarantees that FastKnock will find
the target space for the next level (Fig. 1). Specifically, at every candidate solution (Additional file 1: Supplement
each node X of the tree at level L, we investigate a set of F).
L reactions (deleted_rxns) to determine (a) whether X is a In Algorithm 1, the traversal of the tree shown in Fig. 1
solution and (b) the new target space, which is the set of is represented by a set of queues: queue to queue
1 target_
. Each queue contains a set of nodes. At each moment
level

---

<!-- Page 6 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 6 of 22
during the execution of the algorithm, queue l contains all We elaborate on these functions in the following
children of a certain node at level l-1 being investigated. subsections. Firstly, we determine the target space and
In this way, the subtrees are gradually constructed and subsequently describe the search procedure—detailing
removed (pruned). how the traversal tree is partially constructed and
traversed. In our implementation, we enhanced the
Algorithm 1: The FastKnock main procedure
1: Object Node
2: level ▷ Level of the node.
3: deleted_rxns ▷ List of deleted reac(cid:7)ons for the node.
4: target_space ▷ Target space of the node.
5: flux_dist ▷ Op(cid:7)mal flux distribu(cid:7)on of the model in which deletex_rxns are knocked out.
1: func(cid:7)on FastKnock (model, Removable, target_level) Returns results
2: Input:
model: the reduced metabolic model,
Removable: the set of removable reac(cid:7)ons in the model,
target_level: the predefined number of desired simultaneous reac(cid:7)on knockout
Output:
results: a set of all solu(cid:7)on subsets
3: for l = 1 to target_level do
4: queue = [] The nodes that must be inves(cid:7)gated at level l.
l ▷
5: checked = [] Set of all previously checked reac(cid:7)ons in level l that do not require
l ▷
further inves(cid:7)ga(cid:7)on in level l.
6: solu(cid:7)ons = [] Solu(cid:7)ons with l reac(cid:7)ons knocked out.
l ▷
7: root = new Node Create the root node, which contains all reac(cid:7)ons aŒer preprocessing
▷
8: root.target_space = iden(cid:27)fyTargetSpace(root, model, Removable) Iden(cid:7)fy the target space of root
▷
9: level_one = constructSubTree(root, target_level, checked , queue , solu(cid:7)ons , model, Removable)
1 1 1
10: traverseTree (queue , checked , solu(cid:7)ons , target_level)
level_one level_one level_one
11: results = [solu(cid:7)ons for l = 1 to target_level] The results set is a set of all obtained
l ▷
solu(cid:7)on subsets in each level
12: return results
The main algorithm consists of three functions: quality of the obtained solutions by ensuring a minimal
identifyTargetSpace, constructSubTree, and traverseTree. chemical production rate (Additional file 1: Supplement
For each node, we compute a target space and a flux I) and increased the speed of the algorithm through
distribution using the identifyTargetSpace function. parallel processing (Additional file 1: Supplement G).
This function temporarily narrows the search space for
the whole subtree of the node. The subtree of a node is Identifying the target space
constructed using the constructSubTree function. The At steady state, a specific flux range for each reaction
traverseTree function recursively navigates the tree, based r is obtained (minFlux ≤ f ≤ maxFlux ), which leads
r r r
on a depth-first traversal. to the optimal cellular objective (e.g., maximizing the
biomass formation flux). Knocking out a reaction r is

---

<!-- Page 7 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 7 of 22
implemented by setting the allowable flux range [62] of The search procedure
the reaction to zero (i.e., lb = ub = 0 in the optimization Here, we introduce a depth-first search procedure
r r
problem of Equations a.1 and a.5 in Additional file 1: based on the traversal tree shown in Fig. 1. Each node
Supplement A). Note that when a reaction is reversible of the tree has its own subtree, which is traversed before
(i.e., the obtained flux range of a reaction includes zero moving on to its sibling nodes. This depth-first search
minFlux ≤ 0 ≤ maxFlux ), knocking out that reaction procedure is implemented using the traverseTree function
r r
alone has no effect on the optimal linear objective value of Algorithm 3.
of the network in FBA (Additional file 1: Supplement F). In each call, the traverseTree function visits a certain
Here, the main idea is to prune the target space by con- node X (i.e., the first node of the queue ) and, if
level
sidering only the set of reactions with nonzero flux values. needed, calls the constructSubTree function to create
This approach significantly reduces the size of the target the corresponding subtree of the node (Algorithm 4).
space and thus reduces the execution time of the algorithm. The constructSubTree function creates the children
We denote reactions that lack a zero value in their nodes of X, which is a set of nodes that are placed
obtained flux range as Rxns+ in each node of the tree: in level = X.level + 1. For each child, deleted_rxns is
initialized by adding one of the reactions in X.target_
Rxns+ = {r ∈ Rxns | minFlux r > 0 or maxFlux r < 0}. space to the X.deleted_rxns.
The target space of each node, which is the set of reac- It is clear that the order of the knocked-out reactions
tions that could be appropriate for deletion, is obtained is not important. In FastKnock, repetitive permutations
using the identifyTargetSpace function (Algorithm 2). of the reactions are ignored using a checked queue for
level
The search operation at each node is limited to each level of the tree. Generally, N levels are considered
Rxns+ ∩ Removable, as shown in Line 6 of Algorithm 2. for simultaneously knocking out N reactions from the
It is worth mentioning that by any manipulation of the cell. Precisely, the reaction selected for the ith level is
model, the fluxes of other reactions may change. Therefore, not allowed in the (i + 1)th to Nth levels. To generate all
the functional states (i.e., flux distributions) should be ana- combinations of these reactions, the checked queue is
L
lyzed repeatedly after each modification (i.e., after each reac- used at level L. At level L, by deleting a reaction r from
tion knockout) using FBA to identify the reactions that carry the target space, r is added to the checked . This excludes
L
nonzero flux in the network (model ) (Lines 4–5). The flux_ the reaction from the target space of the subsequent
X
dist variable of the node is updated at Line 4. The intersec- levels.
tion of these reactions and the Removable set construct the
target space of node X in Line 6.
Algorithm 2: Identifying target space for each node
1: func(cid:24)on iden(cid:27)fyTargetSpace (Node X, model, Removable)
2: Input:
X: a node of the tree,
model: reduced metabolic model,
Removable: the set of removable reac(cid:24)ons in the model
Updates X.target_space and X.flux_dist
3: Construct model from model by se(cid:3)ng the upper and lower bounds of all reac(cid:24)ons in X.deleted_rxns
X
to zero
4: X.flux_dist = FBA (model ) FBA returns an op(cid:24)mal flux distribu(cid:24)on of the reac(cid:24)ons
X ▷
5: iden(cid:15)fy Rxns+, which is the list of reac(cid:24)ons that have nonzero flux.
6: X.target_space = Rxns+ ∩ Removable

---

<!-- Page 8 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 8 of 22
Algorithm 3: Traversing the tree
1: func(cid:24)on traverseTree (queue , checked , solu(cid:31)ons , target_level) Returns null
level level level
2: Input:
queue : the queue of the level
level
checked : the checked list of the level
level
solu(cid:31)ons : the solu(cid:24)ons list of the level
level
target_level: the final level of the algorithm
Output:
This recursive func(cid:24)on returns null and all of the queues are empty at the end.
3: if level == 0: All nodes of the tree are inves(cid:24)gated.
▷
4: return null
5: if queue is empty then All nodes in this level and their descendants have been
level ▷
inves(cid:24)gated. So, we must ascend one level.
6: checked = [] The checked list of the level is refreshed when the queue is empty
level ▷ level
7: return traverseTree (queue , checked , solu(cid:31)ons , target_level)
level -1 level-1 level-1
8: else: There is a node at this level to be inves(cid:24)gated.
▷
9: Node X = queue .remove () Remove node X from queue .
level ▷ level
10: next_level = constructSubTree(X, target_level, checked , queue , solu(cid:31)ons ,
next_level next_level next_level
model, Removable) Construct subtree of the node X.
▷
11: return traverseTree (queue , checked , solu(cid:31)ons , target_level) AŒer running
next_level next_level next_level ▷
this line, the next level has at least one node. So, the next level queue should now be traversed in a
depth-first fashion.

---

<!-- Page 9 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 9 of 22
Algorithm 4: Constructing subtrees of the traversal tree
1: func(cid:31)on constructSubTree (Node X, target_level, checked , queue , solu(cid:31)ons ,
next_level next_level current_level
model, Removable) Returns next_level
2: Input:
X: an object of type Node
target_level: final level of the algorithm, the predefined number of simultaneous knockouts
checked : the next checked list from the X.level or null if X.level equals target_level
next_level
queue : the queue of the next level from X.level
next_level
solu(cid:31)ons : set of the solu(cid:31)ons of the X.level
current_level
Output:
next_level: the next level to be inves(cid:31)gated, which can be X.level or X.level+1
3: current_level = X.level
4: if current_level == target_level: No need to a construct subtree for the nodes at the target_level nodes
▷
5: return target_level
6: else: construc(cid:31)ng subtree of node X
▷
7: for each rxn in X.target_space do For each reac(cid:31)on in target space of X that is not
▷
already checked, create a new node as a child of X
8: if rxn not in checked : The reac(cid:31)on has not been previously
current_level+1 ▷
inves(cid:31)gated at the lower levels
9: create node r such that
r.level = current_level +1,
r.deleted_rxns = {rxn} X.deleted_rxns,
r.target_space = NULL,
r.flux_dist = NULL
10: if r is a solu(cid:31)on then inves(cid:31)gate node r
▷
11: add r to solu(cid:30)ons .
current_level
12: r.target_space = iden(cid:31)fyTargetSpace(r, model, Removable)
13: queue +1.insert(r) insert r into the next level queue
current_level ▷
14: checked .add (rxn) add rxn to checked
current_level+1 ▷ current_level+1
15: return current_level + 1

---

<!-- Page 10 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 10 of 22
A traversal example specific reaction often leads to removing a predetermined
To illustrate the formation of the traversal tree, a sample set of reactions that are simultaneously knocked out.
node of Fig. 1 is explained here. Consider node X = {r , In fact, a reaction cannot be removed from a living cell
1
r } representing a double knockout of the reactions r while its genes are being manipulated in vivo. Therefore,
4 1
and r . Deletion of the reaction r as a single reaction the mapping of reactions to genes should be considered
4 1
knockout strategy has been checked in the parent node in the algorithm to reach realizable results. In other
{r } beforehand. Also, double knockout of the reactions words, a reaction is knocked out from the network based
1
r and r and triple knockout of {r , r , r }, {r , r , r }, on its associated gene rule. Furthermore, the clustering
1 2 1 2 3 1 2 4
and {r , r , r } have been checked in the sibling node of reactions based on the associated gene rules could
1 2 6
{r , r } and its children nodes before visiting node X. improve the efficiency of the search procedure for finding
1 2
Visiting node X corresponds to checking the removal the appropriate targets.
of {r , r } as a potential knockout strategy. Afterward, In the simplest form of gene rules, a reaction could
1 4
its subtree is generated to investigate the simultaneous be removed by knocking out at least one gene from a
removal of all the subsets of the removable reactions set of genes (logical AND relation) or by simultaneously
along with r and r . deleting a set of genes (logical OR relation). However, in
1 4
Naively, for each reaction in the removable set, we general form, gene rules describe complex relationships
should generate a child node for X (obviously except for between genes and reactions. Thus, well-known
the reactions r and r ). As mentioned in the root node knockout strategies for in silico strain design are based
1 4
of Fig. 1 in this example, the set of removable reactions is on reactions or genes but do not simultaneously consider
supposed to be {r , r , r , r , r , r }. In a very simple search both of them.
1 2 3 4 5 6
procedure, node X would have four child nodes (i.e., {r , For capturing the complexity of gene-reaction
1
r , r }, {r , r , r }, {r , r , r }, {r , r , r }). Generally in an relationships, in this work, we label a set of reactions
4 2 1 4 3 1 4 5 1 4 6
exhaustive search, for each node, we may have too many as co-knocked out if they are removed due to the
children nodes and such a branching factor leads to a elimination of a single gene. In the preprocessing phase
large search space and hence an excessive runtime. of the proposed framework, for each reaction r, a set
In FastKnock, the size of the target space determines of reactions named Co_KnockedOut is defined that
r
the number of children nodes of X, which is limited to contains all the reactions that are intrinsically removed
Rxns+ ∩ Removable, where Rxns+ consists of nonzero by the deletion of a set of genes that should be knocked
flux reactions (suppose {r , r , r } for node X). Because out for removing the reaction r. Supplement E elaborates
2 3 7
the reaction r is checked in the subtree of the sibling a modified version of the proposed algorithm based
2
node {r , r } (see checked = {r , r , r } in node X), and on knocking out genes rather than reactions, which
1 2 L2 1 2 4
the reaction r does not exist in the removable set of the discusses different forms of gene rules (See Additional
7
model, the target space of node X contains only r . In this file 1: Supplement E).
3
way, the search space is drastically narrowed down by Although the presented method enhances time
generating a limited number of children. efficiency, it can be excluded from the main method
In this example, the reaction r does not exist in the to obtain comparable results with the state-of-the-art
5
Rxns+ of node X, due to its zero flux. It means that the reaction-based approaches. On the other hand, this
node {r , r , r } will not be added as a child of X, because technique can be incorporated as a preprocessing step
1 4 5
it produces the same conditions as exist in node X (i.e., in other metabolic engineering algorithms and in silico
the same target space that results in a duplicate node). As strain design approaches.
discussed in Part 2 of Supplement F, no feasible solution
would be missed because of this search space reduction
(See Additional file 1: Supplement F). Results
It should be noted that the target space is temporarily We implemented the FastKnock algorithm using
reduced and its size may increase in the descendant Python language programming (Version 2.7) and the
nodes. In the node {r , r , r }, the set of nonzero flux COBRApy library (Version 0.15.4) [63]. We evaluated
1 4 3
reactions could include any of the reactions in the model. the performance of FastKnock using various examples,
and we compared these results to OptKnock and
Co‑knockout of the reactions MCSEnumerator approaches.
To assess FastKnock’s performance and demonstrate
For practical applications, one important feature of
its capabilities while addressing potential limitations
FastKnock is that it can optionally consider genes as the
of other methods, such as the impact of model size and
basis of candidate reactions for deletion. This is a realistic
culture medium richness on method performance,
assumption because knocking out genes to remove a

---

<!-- Page 11 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 11 of 22
we selected four highly-curated GEMs for E. coli (i.e., methylerythritol phosphate (MEP) pathway [66]) is
iJR904 [17], iAF1260 [18], iJO1366 [19], and iML1515 added to the wild-type E. coli model [39, 67, 68]. For
[20]) for our experiments. We investigated the excessive the second recombinant strain (Strain2), some other
production of renowned metabolites (succinate, modifications are applied based on [69]. This provides
lactate, 2-oxoglutarate, and lycopene, functioning an intracellular pool of pyruvate as the important pre-
as both primary and secondary biological products) cursor of lycopene production [70]. Additional file 2:
across various media types, including mineral and rich Tables S1 and S2 in Supplement J.I show the maximum
mediums, as diverse case studies. theoretical yield for the biosynthesis of the metabolites
We assessed the overproduction of the primary (i.e., maximum of v ) and our threshold for their
chemical
×
metabolites using these GEMs as wild-type models production (Th = 0.05 v ).
chemical chemical
(referred to as Strain0 in the in-silico experiments), Some results of the preprocessing phase is shown in
focusing on two mineral and one rich cultivation Additional file 2: Table S3 of Supplement J.I, illustrating
conditions. The first condition, CM1, involved iM9 the number of reactions excluded from the search
mineral medium supplemented with glucose (a space before the main exploration procedure and
maximum allowable glucose uptake rate of 10 mmol. before obtaining the removable reactions. The size of
gDW−1h −1) under aerobic conditions (a maximum the search space is drastically reduced to 20% of all the
allowable oxygen uptake rate of 15 mmol.gDW−1 h −1). reactions. In the Reduced_model, the blocked reactions
The second condition, CM2, included iM9 mineral and dead ends are removed [62]. Also, as described after
medium with the same glucose supplementation (a the preprocessing phase, the search space is reduced
maximum allowable glucose uptake rate of 10 mmol. iteratively and temporally during the search procedure
gDW−1h −1) under anaerobic conditions (an oxygen of the FastKnock algorithm. This significantly reduces
uptake rate of 0 mmol.gDW−1.h−1). In a complex and rich the number of linear programming problems (LPs)
environment, more inputs activate cellular functions, that must be solved. Specifically, compared to an
leading to the involvement of more pathways and exhaustive search, the reduction rates are 80%–85% for
reactions in the network. In order to further evaluate the single knockouts, 96%–97.5% for double knockouts,
exhaustive enumeration performance of the FastKnock 99.0–99.5% for triple knockouts, and above 99.8% for
algorithm in a rich cultivation condition, we conducted quadruple and quintuple knockouts (Table 1). The
additional in silico experiments considering succinate number of LPs is equal to the number of nodes in the
overproduction in Luri-Bertani (LB) medium. The iLB traversal tree shown in Fig. 1, and it is independent of
medium constraints were determined based on [64, 65]. the target metabolite to be produced.
The secondary metabolite, lycopene, as a heter- In comparison, in the exhaustive search the algorithm
ologous product is produced in E. coli only under must check all the combinations of the reactions in the
aerobic conditions. We considered two strains for search space. For instance, iJR904 in CM2 has 208 reac-
lycopene production. For the first recombinant strain tions in its search space. For finding double-knockout
(Strain1), the lycopene biosynthesis pathway (i.e., the results in the exhaustive search, the algorithm must
Table 1 The number of linear programming problems (LPs) solved by the FastKnock algorithm compared to an exhaustive search of
the preprocessed search space (Strain0 in CM2 cultivation medium)
Single Double Triple Quadruple Quintuple
Strain0 in CM2 iJR904 Exhaustive search 208 21,528 1,478,256 75,760,620 3,091,033,296
FastKnock 41 820 11,613 125,815 1,178,030
% Reduction 80.29 96.20 99.22 99.84 99.97
iAF1260 Exhaustive search 315 49,455 5,159,805 402,464,790 25,033,309,938
FastKnock 57 1,506 25,985 348,966 4,058,061
% Reduction 81.91 96.96 99.50 99.92 99.99
iJO1366 Exhaustive search 385 73,920 9,437,120 901,244,960 68,674,865,952
FastKnock 58 2,038 43,565 732,315 10,822,208
% Reduction 84.93 97.24 99.53 99.91 99.98
iML1515 Exhaustive search 403 81,003 10,827,401 1,082,740,100 86,402,659,980
FastKnock 61 2193 58,750 1,674,010 25,489,714
% Reduction 84.87 97.30 99.46 99.85 99.98

---

<!-- Page 12 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 12 of 22
check all the double combinations of the elements in the because either (a) the combination of each single dele-
search space (c(208, 2) = 21,528). Due to its time com- tion solution and a zero-flux reaction was inappropri-
plexity, the exhaustive approach is not feasible for high- ately considered as a double-deletion solution or (b)
order reaction knockouts; thus, we compared FastKnock the elimination of a reaction in the co-knocked-out sets
to a simple exhaustive search method for single, double, led to the removal of all the reactions in the set, while
or triple knockouts. Our experiments showed that a sig- in the exhaustive search, the removal of each reaction
nificant reduction in the number of LPs is critical because in the set is counted as a separate solution. For triple
it allows us to investigate and find all possible solutions. deletions, the exhaustive search found 39,407 solutions,
Table 2 presents the total number of solutions of which 887 were unique and acceptable. FastKnock
obtained (regarding CM2 cultivation medium) using found all the 887 solutions.
the FastKnock algorithm. The results are reported in Table 3 presents the best solutions found for iJR904
two cases: the maximum production rate (v ) and GEM (See also Additional file 2: Tables S4-S10). Sup-
max
the guaranteed production rate (v ) as discussed in plement J.II includes the results for the iAF1260 (Addi-
grnt
Supplement I. tional file 2: Tables S11-S17) and iJO1366 (Additional
We also compared our solutions to the results of file 2: Tables S18-S27) GEMs as well. As an example,
the exhaustive search for single, double, and triple we found that the best result for succinate overproduc-
deletions for succinate production in iJR904 to verify tion is obtained by deleting one reaction, ADHEr, which
the completeness of the FastKnock algorithm. Both is knocked out by the deletion of the gene b1241. Con-
approaches found two solutions for a single deletion. sequently, the deletion of the b1241 gene also causes the
The exhaustive search for a double deletion found 398 deletion of the LCADi_copy2 reaction. In this situation,
solutions, of which only 58 solutions were true double the growth rate is 0.16 (h−1) as shown in the “biomass
deletions. The rest of the solutions were not acceptable formation rate” column. After the deletion of ADHEr,
Table 2 The number of solutions in iJR904 (Strain0 in CM2 cultivation medium)
Order of reaction Strain0 in CM2
knockout
succinate 2‑oxoglutarate D‑lactate
v * v ** v v v v
max grnt max grnt max grnt
Single 2 1 0 0 0 0
Double 58 27 0 0 10 7
Triple 887 416 0 0 308 228
Quadruple 10,090 4794 0 0 4941 3790
Quintuple 98,300 48,693 29 0 58,481 13,639
* v
max
: maximum production rate (mmol.gDW− 1 h−1)
** v
grnt
: guaranteed production rate (mmol.gDW−1 h− 1)
Table 3 The guaranteed rate of succinate growth-coupled production in in iJR904 (Strain0 in CM2 cultivation medium)
Number of Deleted reactions Biomass Succinate SoGC (h−1) Deleted genes Co‑knockout reactions
knocked out formation production
reactions rate (h− 1) rate (mmol.
gDW−1 h− 1)
min max
Single ADHEr 0.16 5.11 9.50 1.41E-2 b1241 LCADi_copy2
Double ADHEr, LDH_D 0.15 8.08 9.51 1.43E-2 b1241, b2133, b1380 LCADi_copy2
Triple ADHEr, LDH_D, PFL 0.12 11.08 12.73 1.53E-2 b1241, b2133, b1380, LCADi_copy, OBTFL
b3114, b0902, b3951
Quadruple ADHEr, LDH_D, PFL, THD2 0.11 12.29 13.01 2.58E-2 b1241, b2133, b1380, LCADi_copy, OBTFL
b3114, b0902, b3951, b1602
Quintuple ADHEr, LDH_D, GLUDy, PFL, 0.10 12.34 13.06 2.61E-2 b1241, b2133, b1380, LCADi_copy, OBTFL
THD2 b1761, b3114, b0902,
b3951, b1602

---

<!-- Page 13 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 13 of 22
Fig. 2 Production envelopes for the best solutions presented in Table 3 regarding succinate production from single to quintuple reaction deletions
in iJR904. Knocking out more genes improves growth coupling. In particular, with quadruple and quintuple knockouts, significant production
is guaranteed for any growth rate
the succinate production can vary between 5.11 and For practical applications, various evaluation indices,
9.50 mmol.gDW−1 h −1, which is more than the consid- including product yield, SSP, and SoGC [55], and other
ered 0.85 mmol.gDW−1 h −1 threshold; hence, an accept- important indices reflecting environmental and opera-
able amount of succinate production is guaranteed. tional considerations, can be used to choose the most
Figure 2 presents the production envelopes calculated for appropriate cases from the solutions found by FastKnock
the best cases presented in Table 3. (Tables 7 and Table 8). In particular, the feasibility of C O
2
The analyses carried out with relatively older models, biofixation and minimal production of undesired or toxic
specifically iJR904, iAF1260, and iJO1366, were byproducts are also significant indexes for systems meta-
primarily focused on comparing the performance of bolic engineering purposes. For instance, an engineered
FastKnock with both earlier methods (i.e., OptKnock) strain that can simultaneously fix C O and produce a
2
along with experimental studies and more recent suitable biochemical might be preferred regarding envi-
approaches (i.e., MCSEnumerator) documented in the ronmental considerations. When all solutions are avail-
literature. As previously mentioned, additional tests able, the analysis and identification of such appropriate
were conducted to demonstrate that the effectiveness of cases is easily possible.
the FastKnock method remains unaffected by the size
of the model and the richness of the culture medium. Comparing FastKnock to OptKnock (case study: succinate
These supplementary examinations included assessing overproduction in E. coli iJR904)
succinate overproduction in medium CM2 using model We analyzed FastKnock solutions in order to find the
iML1515 and investigating succinate overproduction most appropriate outcomes based on three criteria,
in iLB rich environment under aerobic conditions yield, SSP, and SoGC (Table 8). Additionally, the feasibil-
using both iJR904 and iML1515. The maximum rates of ity of CO biofixation is also examined and the relevant
2
succinate growth-coupled production associated with results are summarized, where a negative CO exchange
2
these supplementary examinations are presented in flux represents a desirable C O uptake rate. We com-
2
Tables 4, 5, 6. pared these best solutions obtained by FastKnock with

---

<!-- Page 14 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 14 of 22
Table 4 The maximum rates of succinate growth-coupled production in iML1515 (Strain0 in CM2 cultivation medium)
Number of Deleted reactions Biomass Succinate production Deleted genes Co‑Knockout reactions
knocked out formation rate rate (mmol.
reactions (h− 1) gDW−1 h− 1)
Single ATPS4rpp 0.25 12.73 b3735, b3737, b3738, b3732, –
b3733, b3736, b3734, b3731,
b3739
Double ATPS4rpp, PGL 0.24 16.54 b3735, b3737, b3738, b3732, –
b3733, b3736, b3734, b3731,
b3739, b0767
Triple PGI, ATPS4rpp, G6PDH2r 0.17 23.16 b4025, b3734, b3733, b3736, –
b3732, b3737, b3731, b3738,
b3739, b3735, b1852
Quadruple PFL, ACALD, THD2pp, 0.19 23.49 b0351, b1241, b0903, b3951, OBTFL, ’ALCD2x’, ’ALCD19’
THD2pp b2579, b3952, b3114, b0902,
b1602, b2913
Table 5 The maximum rates of succinate growth-coupled production in iJR904 in rich medium (Strain0 in LB cultivation medium)
Number of Deleted reactions Biomass Succinate production Deleted genes Co‑Knockout reactions
knocked out formation rate (mmol.
reactions rate (h−1) gDW− 1 h−1)
Single ADHEr 1.35 20.10 b1241 LCADi_copy2
Double F6PA, PFK 1.28 33.69 b0825, b3946, b3916, b1723 −
Triple ACKr, GLCpts, PYK 0.56 54.88 b2296, b3115, b1849, b1819, DHAPT, GART, PPAKr
b2415, b2416, b1621, b1101,
b2417, b1817, b1818, b1854,
b1676
Quadruple ACKr, ARGDC, GLCpts, PYK 0.56 64.72 b2296, b3115, b1849, b2938, GART, PPAKr, DHAPTs
b4117, b1819, b2415, b2416,
b1621, b1101, b2417, b1817,
b1818, b1854, b1676
Table 6 The maximum rates of succinate growth-coupled production in iML1515 in rich medium (Strain0 in LB medium)
Number of Deleted reactions Biomass Succinate production Deleted genes Co‑Knockout reactions
knocked out formation rate (mmol.
reactions rate (h− 1) gDW−1 h− 1)
Single ARGDC 1.08 19.72 b4117 –
Double ARGDC, FADRx 1.05 22.09 b4117, b3844 FADRx, FE3Ri, FLVRx
Triple NDPK5, ASPTA, ARGDC 1.03 28.14 b0474, b2518, b0928, ADK1, NDPK2, ADNK1,
b4054, b4117 NDPK3, NDPK6, DADK,
ADK4, NDPK1, ADK3, NDPK4,
NDPK7, NDPK8, TYRTA,
PHETA1, LEUTAi
Quadruple NDPK5, PFL, LDH_D, 0.75 40.97 b0474, b2518, b2579, ADK1, NDPK2, ADNK1,
ACALD b3952, b0902, b3951, NDPK3, NDPK6, DADK,
b0903, b3114, b1380, ADK4, NDPK1, ADK3, NDPK4,
b0351, b1241 NDPK7, NDPK8, OBTFL,
ALCD2x, ALCD19
the associated OptKnock results as well as experi- single solution. Therefore, comparing it with FastKnock
mental data available in the literature [71–73]. Note in terms of computational costs is not meaningful.
that OptKnock aims at, and terminates on, finding a We found that a solution with the best production rate
or an optimal solution of the optimization algorithms

---

<!-- Page 15 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 15 of 22
409RJi
ni
)muidem
noitavitluc
2MC
ni
0niartS(
noitidnoc
ciboreana
rednu
noitcudorp
etaniccus
rof
sexedni
noitaulave
derised
eht
no
desab
snoitulos
tseb
ehT
7
elbaT
xedni
noitaulavE
fo
rebmuN dekconK
1
1
1
) −h(
CGoS
) h(
PSS
) −h(
PSS
−
noitcaer
tuo
)snoitaluclac
desab‑ABF(
)]26[
)snoitaluclac
desab‑AMoMraeniL(
)snoitaluclac
desab‑ABF(
1
1
1
)
h(
PSS
etaniccuS
ssamoiB
tseB
)
−h(
PSS
etaniccuS
ssamoiB
tseB
)
h(
PSS
etaniccuS
ssamoiB
tseB
−
−
01
noitcudorp
noitamrof
tuokconk
01
noitcudorp
noitamrof
tuokconk
01
noitcudorp
noitamrof
tuokconk
×
×
×
1
1
1
lomm(
etar
)
h(
etar
ygetarts
lomm(
etar
) −h(
etar
ygetarts
lomm(
etar
)
h(
etar
ygetarts
−
−
1
1
1
)
−WD
g
)
WD
g
)
−WD
g
−
43.1
83.2
30.0
rEHDA
80.0
83.2
30.0
rEHDA
41.0
38.0
61.0
rEHDA
1
53.1
37.8
61.0
,rEHDA
10.1
23.8
21.0
,rEHDA
34.1
37.8
61.0
,rEHDA
2
D_HDL
r4SPTA
D_HDL
10.3
09.8
61.0
,rEHDA
91.1
06.8
31.0
,rEHDA
35.1
42.21
21.0
,rEHDA
3
,r4SPTA
EPR
,r4SPTA
LFP
,D_HDL
D_HDL
90.3
88.9
31.0
,rEHDA
02.1
17.8
31.0
,rEHDA
35.1
42.21
21.0
,rEHDA
4
,D_HDL
,r4SPTA
,LFP
,D_HDL
2DHT
,1XEH
EPR
,D_HDL
2KIRU
01.3
78.9
31.0
,rEHDA
32.1
36.8
41.0
,rEHDA
45.1
52.21
21.0
,LFP
,P ,rEHDA
5
,D_HDL
,KYLG
,r4SPTA
,SAOCUS
,2DHT
,1XEH
EPR
,AP6F
3RDNR
APRD

---

<!-- Page 16 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 16 of 22
Table 8 Comparison of FastKnock, OptKnock and experimental results reported in the literature for succinate production. The iJR904
model (Strain0) is used in the in silico experimentations (M9 cultivation medium)
Knockout Knockout Method Biomass Succinate yield SSP (h− 1) × 10 SoGC CO 2 exchange
strategy formation rate production (h−1) × 100 flux (mmol.
(h−1) rate (mmol. gDW− 1 h−1)
gDW− 1 h−1)
Triple ADHEr, LDH_D, OptKnock [33], 0.08 9.37 0.94 0.75 0.79 −9.36 (uptake)
PTAr FastKnock
ADHEr, LDH_D, OptKnock, 0.12 12.24 1.22 1.46E 1.53 −5.87
PFL FastKnock (best (uptake)
production rate)
PTAr, PYK, GLCpts OptKnock, 0.09 9.32 0.93 0.83 0.87 3.24
FastKnock (production)
PFL, LDH_D, Experimental [71] 0.16 0.71 0.07 0.11 0.11 16.78
GLCpts (production (production)
is lower
than considered
threshold)
ADHEr, ATPS4r, FastKnock 0.16 8.90 0.89 1.42 3.01 −8.76
LDH_D (best SoGC) (uptake)
Quadruple PTAr, PYK, ATPS4r, OptKnock 0.16 1.18 0.11 0.18 0.01 9.03
SUCD1i (production)
ADHEr, LDH_D, FastKnock 0.11 12.72 1.27 1.39 2.85 −6.12
PFL, THD2 (best production (uptake)
rate)
ADHEr, LDH_D, FastKnock 0.13 9.88 0.98 1.28 3.09 −8.77
HEX1, THD2 (best SoGC) (uptake)
Quintuple ADHEr, LDH_D, OptKnock, 0.05 9.96 0.99 0.49 1.19 −9.51
PTAr, PYK, GLCpts FastKnock (uptake)
ADHEr, LDH_D, Experimental [71], 0.08 9.57 0.95 0.76 0.80 −9.16
PFL, ACKr, FORt FastKnock (uptake)
ADHEr, LDH_D, FastKnock 0.13 9.87 0.98 1.28 3.10 −8.76
HEX1, THD2, DRPA (best SoGC) (uptake)
ADHEr, LDH_D, FastKnock 0.10 12.77 1.27 1.27 2.61 −6.17
GLUDy, PFL, THD2 (best production (uptake)
rate)
such as OptKnock does not necessarily bring the best A more striking example is the comparison between
SoGC and the other desired indexes. However, by iden- the PTAr, PYK, ATPS4r, and SUCD1i quadruple
tifying all the possible solutions for the problem, Fast- knockout identified by OptKnock with the two solutions
Knock allows a comprehensive analysis. For example, with the best production rate (ADHEr, LDH_D, PFL,
knocking out ADHEr, ATPS4r, and LDH_D is expected and THD2) and the best SoGC (ADHEr, LDH_D, HEX1,
to lead to the best biomass formation rate (0.16 h−1) and and THD2) identified by FastKnock. While the biomass
the highest SoGC (3.01E-2 h−1), which is twice the best formation rate of the FastKnock solutions (0.11, 0.13 h−1,
SoGC provided by OptKnock solutions while the other respectively) are comparable with the OptKnock solution
indices corresponding to this knockout are comparable (0.16 h−1), the yield and SSP is an order of magnitude
with the best numbers shown in the table (i.e., a produc- higher for FastKnock solutions. A serious issue with this
tion rate of 8.90 vs. 12.24 mmol.gDW−1.h−1, a yield of OptKnock solution is the very low SoGC (1E-4 h−1),
0.89 vs. 1.22, an SSP 1.42E-1 vs. 1.46E-1 h−1, and a C O which indicates that the production rate would be hardly
2
exchange flux of −8.76 vs. −9.36 mmol.gDW−1.h−1). A coupled with growth. In comparison, the predicted SoGC
relatively high value of SoGC can also be desirable from a for FastKnock solutions are 2.85E-2 and 3.09E-2 h−1,
dynamic perspective because it indicates that even under respectively. Another disadvantage of OptKnock solution
non-optimal conditions, the biosynthesis of the target is a relatively high CO production rate of 9.03 mmol.
2
biochemical is coupled with the growth of the production gDW−1.h−1 while in the FastKnock solutions the CO
2
strain. This situation is usually encountered in batch and exchange fluxes are −6.12 and −8.77 mmol.gDW−1.h−1,
fed-batch cultivations in the logarithmic phase of growth. respectively.

---

<!-- Page 17 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 17 of 22
Among the quintuple knockouts, the predicted SSP We should discuss the effect of the MCSEnumerator
and SoGC for one of the FastKnock solutions (ADHEr, thresholds on its solution set. It would not be feasible to
LDH_D, GLUDy, PFL, and THD2) are almost twice those apply MCSEnumerator using thresholds that are relaxed
of the OptKnock solution (ADHEr, LDH_D, PTAr, PYK, enough to find all the solutions (Supplement H). We illus-
and GLCpts) while the other indices are comparable. trate this with an example in Fig. 3. The blue production
An important concern about OptKnock is possible envelope, which has the best SoGC value, is associated
false positive outcomes due to different scenarios. with a solution found by both MCSEnumerator and Fast-
Firstly, false positives could be obtained due to the Knock. The associated solutions (with the red and green
associated linear programming problem, focusing diagrams), which are the worst cases among the shown
on maximizing the target reaction flux neglecting envelopes, were not found by MCSEnumerator because
minimum possible production flux. In other words, of the production threshold considered. This illustrates
OptKnock relies on FBA, potentially leading to false the efficiency of the primary filtration of the MCSEnu-
positives by not considering flux variabilities [43]. In merator method. The starting point might not be the best
contrast, FastKnock could guarantee the minimum factor for filtering appropriate solutions. For example, the
production flux, regarding FVA. The second scenario minimum production rate based on the orange envelope
is about the nature of the associated primal bi-level is similar to the green envelope in Region Y3, which is
optimization problem, which is reformulated in below the threshold considered for ethanol production
the form of a single-level Mixed-Integer Linear flux. Nevertheless, the orange envelope may still be asso-
Programming (MILP) problem. To solve the MILP ciated with a proper solution due to its relatively high
problem, OptKnock utilizes the branch and bound SoGC, but it was not found by MCSEnumerator.
method, which may generate false positives and even Moreover, the predefined thresholds may result
pose a risk of the algorithm getting trapped in an in the situation where some solutions obtained by
infinite loop. In contrast, FastKnock employs a different MCSEnumerator are not necessarily and genuinely
approach based on a search problem to explore the minimal. This implies that an appropriate solution with a
entire solution space. With appropriate evaluation cardinality of ’n’ might exist but goes undiscovered, while
criteria, unlike OptKnock, if it fails to provide a it may appear in some higher-order solutions (> n) that
solution, it implies that no valid solution exists for the include irrelevant additional reactions.
given criteria. While the MCSEnumerator algorithm and its modified
It is also important to note that, in some cases, false versions may exhibit shorter execution times, the
positives stem from limitations of the models due to number of solutions they can provide, given certain
incomplete knowledge of the genotype–phenotype settings, constitutes only a very small percentage of
relationships of the (micro)organism at hand in the the total potential solutions. Therefore, comparing the
process of model development. In this case, any in MCSEnumerator and FastKnock algorithms based solely
silico strain design approach intrinsically produces false on execution time is not rational, as these algorithms
positives [19]. neither yield the same output nor pursue the same
objective.
Comparing FastKnock to MCSEnumerator (case study:
ethanol overproduction in E. coli iAF1260) Discussion
As mentioned previously, MCSEnumerator is a novel Overproduction of biochemicals of interest coupled with
method for metabolic engineering based on the significant growth rates might be optimistic and may
identification of minimal cut sets [50]. This approach not always be easily achievable due to e.g., competing
applies a filtering step to reduce the computation time, pathways in a metabolic network [43]. This can lead
which allows the user to find thousands (but not all) to weak coupling especially under suboptimal growth
of the most efficient knockout strategies in genome- conditions. Alternatively, strong coupling requires
scale metabolic models. MCSEnumerator can be that production must occur even without growth [14].
used to find a large number of metabolic engineering Specifically, product synthesis rate is said to be strongly
interventions, but it has various drawbacks. In this coupled with biomass formation if the product yields of
section, we compare MCSEnumerator with FastKnock. all steady-state flux vectors are equal to or larger than a
To aid in this comparison, we consider the case study predefined product yield threshold [15]. Accordingly,
of ethanol production in E. coli iAF1260 GEM with SoGC is defined as the square of the product yield per
an 18.5 mmol.gDW−1h −1 glucose uptake rate under unit substrate divided by the slope of the lower edge of
anaerobic conditions (iM9 medium) as presented in the the production curve [55] (see Fig. 2).
MCSEnumerator publication.

---

<!-- Page 18 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 18 of 22
Fig. 3 Five exemplar production envelopes for strategies identified by FastKnock for ethanol production in iAF1260, which is partitioned into four
regions based on the growth rate (x axis) and the production flux (y axis) as in [15]. The horizontal dashed line indicates the threshold for production
rate as considered in [15], and the vertical dashed line indicates the growth rate threshold. SoGC(× 100), product yield (Yp/s) and SSP(× 10)
of the quadruple knockout strategies are shown in the top right legend. Unlike FastKnock, MCSEnumerator finds none of these strategies
except the one shown in blue
SoGC is a non-linear objective function and thus Opt- biochemical. We reached this goal by significantly
Knock and most of the in silico strain design methods pruning the search space without omitting any solutions.
cannot be used to find knockouts with optimal SoGC. For example, in our experiments, FastKnock was required
OptGene [37] is a heuristic approach that can be used to to explore only 1% of the search space in the pruned
identify a single knockout strategy with optimal SoGC model when identifying all triple-knockout strategies.
[55]. However, knocking out the single identified solu- The rate of this reduction increases as more reactions are
tion by OptGene may not be practically feasible e.g., due knocked out (e.g., about 0.1% for quadruple-knockout
to the genes’ loci. Therefore, identification of all knock- strategies and about 0.01% for quintuple-knockout
out strategies by FastKnock is desired and provides the strategies) (Table 1). This drastic reduction of the search
expert experimentalists with the opportunity to choose space enables our novel FastKnock method to find the set
from a short list of knockout strategies that are filtered of all possible solutions in a feasible time duration.
for a relatively high SoGC, SSP, yield, etc. This shortlist Finding the best and most suitable trade-off between
can be investigated for advantageous solutions in terms cellular growth and the production of the desired
of environmental considerations such as CO biofixa- biochemical is one of the key benefits of FastKnock
2
tion [71, 72], minimal production of undesired or toxic results. Moreover, determining all possible solutions
byproducts, practicality of knocking or silencing genes, allows for the selection of the most appropriate strategy
etc. (Table 8) [6, 55, 73–75]. based on any desired evaluation index, including
We proposed an efficient next-generation algorithm, product yield, SSP, and SoGC (Tables 7 and 8). This is
FastKnock, which identifies all proper reaction or an important and useful feature of our search strategy,
gene knockout strategies (with predefined maximum especially for practical applications [59].
number of deletions) for the overproduction of a desired

---

<!-- Page 19 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 19 of 22
Fig. 4 The rate of presence of the ADHEr and PFL reactions in all the possible solutions counted in Table 7 for succinate production
We compared FastKnock to MCSEnumerator [50], such as richness and complexity of the cultivation
which has been shown to find more efficient solutions conditions or large size of the metabolic network of the
than the MCS methods [76–78]. We found that the solu- strain of interest. FastKnock identifies strategies, if exist,
tions identified by MCSEnumerator may not be minimal. with a production rate higher than the desired threshold
Also, due to initial filtering, MCSEnumerator misses determined by the user.
solutions that may be practically more appropriate than
Supplementary Information
the best solutions it finds. In comparison, FastKnock
identifies all minimal solutions, which can be mined later The online version contains supplementary material available at https:// doi.
org/ 10. 1186/ s12934- 023- 02277-x.
based on any desired criteria.
When all solutions are available, one interesting analy-
Additional file 1: Supplement A: Definitions and Overview of the
sis that can be conducted is to identify the reactions or Related Methods. Supplement B: The Optimization Methods. Supplement
genes that are common among a relatively large number C: Preprocessing. Supplement D: FastKnock Dictionary. Supplement E:
Co-Knockout Reactions. Supplement F: A Discussion about Finding all
of solutions. For instance, in the case of iJR904, to pro-
Knockout Strategies. Supplement G: Parallel implementation. Supplement
duce succinate in iM9 under anaerobic conditions (CM2), H: MCSEnumerator Thresholds. Supplement I: Production Rate Guarantee.
about 70% of solutions include at least one of ADHEr or Additional file 2: Supplement J.I: Model details and preprocessing
PFL reactions (Fig. 4). Moreover, when three or more results.
reactions are to be deleted, the best results in terms
of the succinate production rate include both ADHEr Acknowledgements
and PFL (Table 7). Collectively, this analysis suggests We express our gratitude to Mehdi Dehghan Manshadi for thoroughly
examining some of the drawbacks associated with the MCSEnumerator
that ADHEr and PFL reactions support pathways that
method, and we would like to gratefully thank Vincente LeCornu for his
compete with succinate production, and these path- valuable contribution in proofreading the paper. This work is supported by
ways are blocked when ADHEr and PFL are eliminated NIH–NIA (grant numbers: R01AG057896, 1RF1AG063507, R01AG068293,
1R01AG0665241A,1R01AG065301, P30 AG066546) and NIH–NINDS (grant
[79, 80]. Based on this analysis, we suggest using a heu-
numbers: RF1NS112391 and U19NS115388).
ristic for higher-level knockout combinations in which
one or more reactions (e.g., ADHEr or PFL) are removed Author contributions
LH performed the data preprocessing, and formal analysis, and contributed to
in searches for six or more knockouts. In this way, one
methodology development, coding and software development, visualization,
would need to search for fewer reactions to knockout. and writing the original draft. MRM supervised the research, performed
We believe this heuristic would reduce the search space the project administration, and conceptualization of research ideas, and
contributed to methodology development, software preparation, writing
by an order of magnitude at the expense of losing not
the original draft, reviewing and editing of the final manuscript. PS defined
more than half of the solutions. the problem statement and performed the methodology development, the
conceptualization of research ideas, formal analysis, data curation, resource
management, and validation, and contributed to writing the original draft,
rewriting, reviewing, and editing of the final manuscript. HZ performed
Conclusion
the project administration, methodology development, and contributed
While in silico strain design results do not necessarily to the visualization, supervision, writing, reviewing, and editing of the final
manuscript.
lead to in vivo overproduction, obtaining all possible
knockout strategies is critical for determining the best Funding
practical and most efficient strategy. The FastKnock This work is supported by NIH-NIA (grant numbers: R01AG057896,
1RF1AG063507, R01AG068293, 1R01AG0665241A,1R01AG065301, P30
algorithm is a general framework that can be used to
AG066546) and NIH-NINDS (grant numbers: RF1NS112391 and U19NS115388).
overproduce any metabolite. It is not limited by factors

---

<!-- Page 20 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 20 of 22
Availability of data and materials 15. Klamt S, Mahadevan R. On the feasibility of growth-coupled product
All data generated or analyzed during this study are included in this published synthesis in microbial strains. Metab Eng. 2015;30:166–78. https:// doi. org/
article [and its supplementary information files]. Our implementation of the 10. 1016/j. ymben. 2015. 05. 006.
FastKnock method in Python is publicly available at https:// github. com/ leila 16. Thiele I, Palsson BØ. A protocol for generating a high-quality genome-
hsn/ FastK nock. scale metabolic reconstruction. Nat Protoc. 2010;5(1):93–121. https:// doi.
org/ 10. 1038/ nprot. 2009. 203.
17. Reed JL, Vo ThD, Schilling ChH, Palsson BO. An expanded genome-
Declarations
scale model of Escherichia coli K-12 (iJR904 GSM/GPR). Genome Biol.
2003;4(9):R54. https:// doi. org/ 10. 1186/ gb- 2003-4- 9- r54.
Ethics approval and consent to participate
18. Feist AM, et al. A genome-scale metabolic reconstruction for Escherichia
Not applicable.
coli K-12 MG1655 that accounts for 1260 ORFs and thermodynamic infor-
mation. Mol Syst Biol. 2007;3(121):1–18. https:// doi. org/ 10. 1038/ msb41
Consent for publication
00155.
Not applicable.
19. Orth JD, et al. A comprehensive genome-scale reconstruction of Escheri-
chia coli metabolism-2011. Mol Syst Biol. 2011;7(535):1–9. https:// doi. org/
Competing interests
10. 1038/ msb. 2011. 65.
We declare that the authors have no competing interests as defined by BMC,
20. Monk JM, et al. iML1515, a knowledgebase that computes Escherichia coli
or other interests that might be perceived to influence the results and/or
traits. Nat Biotechnol. 2017;35(10):904–8.
discussion reported in this paper.
21. Nogales J, Palsson BØ, Thiele I. A genome-scale metabolic reconstruction
of Pseudomonas putida KT2440: iJN746 as a cell factory. BMC Syst Biol.
2008;2(1):79. https:// doi. org/ 10. 1186/ 1752- 0509-2- 79.
Received: 30 June 2023 Accepted: 15 December 2023
22. Nogales J, et al. High-quality genome-scale metabolic modelling of
Pseudomonas putida highlights its broad metabolic capabilities. Environ
Microbiol. 2020;22(1):255–269. https:// doi. org/ 10. 1111/ 1462- 2920. 14843.
23. Duarte NC, Herrgård MJ, Palsson BØ. Reconstruction and validation of
Saccharomyces cerevisiae iND750, a fully compartmentalized genome-
References scale metabolic model. Genome Res. 2004;14(7):1298–1309. https:// doi.
1. Nielsen J, Keasling JD. Engineering cellular metabolism. Cell. org/ 10. 1101/ gr. 22509 04.
2016;164(6):1185–97. https:// doi. org/ 10. 1016/j. cell. 2016. 02. 004. 24. Mo ML, Palsson BO, Herrgård MJ. Connecting extracellular metabo-
2. Park SY, Yang D, Ha SH, Lee SY. Metabolic engineering of microorganisms lomic measurements to intracellular flux states in yeast. BMC Syst Biol.
for the production of natural compounds. Adv Biosyst. 2017;2(1):1700190. 2009;3:37. https:// doi. org/ 10. 1186/ 1752- 0509-3- 37.
https:// doi. org/ 10. 1002/ adbi. 20170 0190. 25. H. Lu et al., A consensus S. cerevisiae metabolic model Yeast8 and its eco-
3. Luo Y, et al. Engineered biosynthesis of natural products in heterologous system for comprehensively probing cellular metabolism. Nat Commun.
hosts. Chem Soc Rev. 2015;44(15):5265–90. https:// doi. org/ 10. 1039/ 2019;10(1):3586. https:// doi. org/ 10. 1038/ s41467- 019- 11581-3.
C5CS0 0025d. 26. Oftadeh O, Salvy P, Masid M, Curvat M, Miskovic L, Hatzimanikatis V.
4. Lee JW, Na D, Park JM, Lee J, Choi S, Lee SY. Systems metabolic engineer- A genome-scale metabolic model of Saccharomyces cerevisiae that
ing of microorganisms for natural and non-natural chemicals. Nat Chem integrates expression constraints and reaction thermodynamics. Nat
Biol. 2012;8(6):536–46. https:// doi. org/ 10. 1038/ nchem bio. 970. Commun. 2021;12(1):4790. https:// doi. org/ 10. 1038/ s41467- 021- 25158-6.
5. Lee SY, Kim HU. Systems strategies for developing industrial microbial 27. Orth JD, Thiele I, Palsson BO. What is flux balance analysis? Nat Biotechnol.
strains. Nat Biotechnol. 2015;33(10):1061–72. https:// doi. org/ 10. 1038/ nbt. 2010;28(3):245–48. https:// doi. org/ 10. 1038/ nbt. 1614.
3365. 28. Mahadevan R, Schilling CH. The effects of alternate optimal solutions
6. Chae TU, Choi SY, Kim JW, Ko YS, Lee SY. Recent advances in systems in constraint-based genome-scale metabolic models. Metab Eng.
metabolic engineering tools and strategies. Curr Opin Biotechnol. 2003;5(4):264–76. https:// doi. org/ 10. 1016/j. ymben. 2003. 09. 002.
2017;47:67–82. https:// doi. org/ 10. 1016/j. copbio. 2017. 06. 007. 29. Lewis NE, Nagarajan H, Palsson BO. Constraining the metabolic geno-
7. Choi KR, Jang WD, Yang D, Cho JS, Park D, Lee SY. Systems metabolic type-phenotype relationship using a phylogeny of in silico methods. Nat
engineering strategies: integrating systems and synthetic biology with Rev Microbiol. 2012;10(4):291–305. https:// doi. org/ 10. 1038/ nrmic ro2737.
metabolic engineering. Trends Biotechnol. 2019;37(8):817–37. https:// doi. 30. Zeng YZL, Sun QY, Jin Y, Zhang Y, Lee WH. Molecular cloning and charac-
org/ 10. 1016/j. tibte ch. 2019. 01. 003. terization of a complement-depleting factor from king cobra, Ophiopha-
8. Curran KA, Alper HS. Expanding the chemical palate of cells by gus hannah. Toxicon. 2012;60(3):290–301. https:// doi. org/ 10. 1016/j. toxic
combining systems biology and metabolic engineering. Metab Eng. on. 2012. 04. 344.
2012;14(4):289–97. https:// doi. org/ 10. 1016/j. ymben. 2012. 04. 006. 31. Pharkya P, Maranas CD. An optimization framework for identifying reac-
9. Kim HU, Charusanti P, Lee SY, Weber T. Metabolic engineering with tion activation/inhibition or elimination candidates for overproduction in
systems biology tools to optimize production of prokaryotic secondary microbial systems. Metab Eng. 2006;8(1):1–13. https:// doi. org/ 10. 1016/j.
metabolites. Nat Prod Rep. 2016;33(8):933–41. https:// doi. org/ 10. 1039/ ymben. 2005. 08. 003.
c6np0 0019c. 32. Ranganathan S, Suthers PF, Maranas CD. OptForce: An optimization
10. Boghigian BA, Seth G, Kiss R, Pfeifer BA. Metabolic flux analysis and phar- procedure for identifying all genetic manipulations leading to targeted
maceutical production. Metab Eng. 2010;12(2):81–95. https:// doi. org/ 10. overproductions. PLoS Comput Biol. 2010;6(4):1–11. https:// doi. org/ 10.
1016/j. ymben. 2009. 10. 004. 1371/ journ al. pcbi. 10007 44.
11. Palsson B. Metabolic systems biology. FEBS Lett. 2009;583(24):3900–4. 33. Burgard AP, Pharkya P, Maranas CD. OptKnock: a Bilevel Programming
https:// doi. org/ 10. 1016/j. febsl et. 2009. 09. 031. framework for identifying gene knockout strategies for microbial strain
12. Oberhardt MA, Palsson BØ, Papin JA. Applications of genome-scale meta- optimization. Biotechnol Bioeng. 2003;84(6):647–57. https:// doi. org/ 10.
bolic reconstructions. Mol Syst Biol. 2009;5:320. https:// doi. org/ 10. 1038/ 1002/ bit. 10803.
msb. 2009. 77. 34. Ren S, Zeng B, Qian X. Adaptive bi-level programming for optimal
13. Reed JL, Senger RS, Antoniewicz MR, Young YJD. Computational gene knockouts for targeted overproduction under phenotypic
approaches in metabolic engineering. J Biomed Biotechnol. 2010;207414. constraints. BMC Bioinformatics, 2013;14:S17. https:// doi. org/ 10. 1186/
https:// doi. org/ 10. 1155/ 2010/ 207414. 1471- 2105- 14- S2- S17.
14. Von Kamp A, Klamt S. Growth-coupled overproduction is feasible for 35. Choon YW, Mohamad MS, Deris S, Illias RM. A hybrid of bees algorithm
almost all metabolites in five major production organisms. Nat Commun. and flux balance analysis (BAFBA) for the optimisation of microbial strains.
2017;8:15956. https:// doi. org/ 10. 1038/ ncomm s15956. Int J Data Min Bioinform. 2014;10(2):225–38. https:// doi. org/ 10. 1504/
ijdmb. 2014. 064016.

---

<!-- Page 21 -->

H assani et al. Microbial Cell Factories (2024) 23:37 Page 21 of 22
36. Gu D, Zhang C, Zhou S, Wei L, Hua Q. IdealKnock: a framework for products of Escherichia coli. Metab Eng. 2010;12(3):173–86. https:// doi.
efficiently identifying knockout strategies leading to targeted overpro- org/ 10. 1016/j. ymben. 2009. 10. 003.
duction. Comput Biol Chem. 2016;61:229–37. https:// doi. org/ 10. 1016/j. 56. Garcia S, Trinh CT. Multiobjective strain design: a framework for modular
compb iolch em. 2016. 02. 014. cell engineering. Metab Eng. 2019;51:110–20. https:// doi. org/ 10. 1016/j.
37. Rocha I, Maia P, Rocha M, Ferreira E. OptGene : a framework for in silico ymben. 2018. 09. 003.
metabolic engineering. 10th International Chemical and Biological Engi- 57. Brockman IM, Prather KLJ. Dynamic metabolic engineering: New
neering Conference – CHEMPOR 2008. strategies for developing responsive cell factories. Biotechnol J.
38. Fowler ZL, Gikandi WW, Koffas MAG. Increased malonyl coenzyme 2015;10(9):1360–69. https:// doi. org/ 10. 1002/ biot. 20140 0422.
A biosynthesis by tuning the Escherichia coli metabolic network 58. Zhuang K, Yang L, Cluett WR, Mahadevan R. Dynamic strain scanning
and its application to flavanone production. Appl Environ Microbiol. optimization: an efficient strain design strategy for balanced yield, titer,
2009;75(18):5831–39. https:// doi. org/ 10. 1128/ AEM. 00270- 09. and productivity. DySScO strategy for strain design. BMC Biotechnol.
39. Choi HS, Lee SY, Kim TY, Woo HM. In silico identification of gene amplifica- 2013;13:8. https:// doi. org/ 10. 1186/ 1472- 6750- 13-8.
tion targets for improvement of lycopene production. Appl Environ 59. Schneider P, Klamt S. Characterizing and ranking computed metabolic
Microbiol. 2010;76(10):3097–105. https:// doi. org/ 10. 1128/ AEM. 00115- 10. engineering strategies. Bioinformatics. 2019;35(17):3063–72. https:// doi.
40. Cotten C, Reed J. Constraint-based strain design using Continuous org/ 10. 1093/ bioin forma tics/ bty10 65.
Modifications (CosMos) of flux bounds finds new strategies for metabolic 60. Schneider P, Mahadevan R, Klamt S. Systematizing the different notions of
engineering. Biotechnol J. 2013;8(5):595–604. https:// doi. org/ 10. 1002/ growth-coupled product synthesis and a single framework for comput-
biot. 20120 0316. ing corresponding strain designs. Biotechnol J. 2021;16(12):e2100236.
41. Yen JY, Tanniche I, Fisher AK, Gillaspy GE, Bevan DR, Senger RS. Designing https:// doi. org/ 10. 1002/ biot. 20210 0236.
metabolic engineering strategies with genome-scale metabolic flux 61. Ruckerbauer DE, Jungreuthmayer C, Zanghellini J. Design of optimally
modeling. Adv Genomics Genet. 2015;5:93–105. https:// doi. org/ 10. 2147/ constructed metabolic networks of minimal functionality. PLoS One.
AGG. S58494. 2014;9(3):e92583. https:// doi. org/ 10. 1371/ journ al. pone. 00925 83
42. Çakır T, Khatibipour MJ. Metabolic network discovery by top-down 62. Heirendt L, et al. Creation and analysis of biochemical constraint-based
and bottom-up approaches and paths for reconciliation. Front Bioeng models using the COBRA Toolbox vol 3.0. Nat Protoc. 2019;14(3):639–702.
Biotechnol. 2014;2(62):1–11. https:// doi. org/ 10. 3389/ fbioe. 2014. 00062 https:// doi. org/ 10. 1038/ s41596- 018- 0098-2.
43. Tepper N, Shlomi T. Predicting metabolic engineering knockout strategies 63. Ebrahim A, Lerman JA, Palsson BO, Hyduke DR. COBRApy: COnstraints-
for chemical production: accounting for competing pathways. Bioin- based reconstruction and analysis for python. BMC Syst Biol. 2013;7(1):74.
formatics. 2009;26(4):536–43. https:// doi. org/ 10. 1093/ bioin forma tics/ https:// doi. org/ 10. 1186/ 1752- 0509-7- 74.
btp704. 64. Oh Y-K, Palsson BO, Park SM, Schilling CH, Mahadevan R. Genome-
44. Choon YW, Mohamad MS, Deris S. A hybrid of bees algorithm and flux scale reconstruction of metabolic network in Bacillus subtilis based on
balance analysis (BAFBA) for the optimisation of microbial strains. Int J high-throughput phenotyping and gene essentiality data. J Biol Chem.
Data Min Bioinforma. 2014;10(2):225–38. https:// doi. org/ 10. 1504/ IJDMB. 2007;282(39):28791-99. https:// doi. org/ 10. 1074/ jbc. M7037 59200.
2014. 064016. 65. Oberhardt MA, Jacek P, Fryer KE, Martins dos Santos VAP, Papin JA.
45. Pham DT, Ghanbarzadeh A, Koc E, Otri S, Rahim S, Zaidi M. The Bees Genome-scale metabolic network analysis of the opportunistic pathogen
Algorithm technical note. The Manufacturing Engineering Centre, Cardiff Pseudomonas aeruginosa PAO1. J Bacteriol. 2008;190(8):2790-803 https://
University, Queen’s University, 2005. doi. org/ 10. 1128/ JB. 01583- 07.
46. Meng H, Lu Z, Wang Y, Wang X, Zhang S. In silico improvement of heter- 66. Karp, PD et al. The BioCyc collection of microbial genomes and metabolic
ologous biosynthesis of erythromycin precursor 6-deoxyerythronolide b pathways. Brief Bioinformatics. 2019;20(4):1085–93. https:// doi. org/ 10.
in Escherichia coli. Biotechnol Bioprocess Eng. 2011;16(3):445–56. https:// 1093/ bib/ bbx085.
doi. org/ 10. 1007/ s12257- 010- 0321-7. 67. Jian X, Zhou S, Zhang C, Hua Q. In silico identification of gene amplifi-
47. Ranganathan S, et al. An integrated computational and experimen- cation targets based on analysis of production and growth coupling.
tal study for overproducing fatty acids in Escherichia coli. Metab Eng. Biosystems. 2016;145:1–8. https:// doi. org/ 10. 1016/j. biosy stems. 2016. 05.
2012;14(6):687–704. https:// doi. org/ 10. 1016/j. ymben. 2012. 08. 008. 002.
48. Suthers PF, Zomorrodi A, Maranas CD. Genome-scale gene/reaction 68. Niu FX, Lu Q, Bu YF, Liu JZ. Metabolic engineering for the microbial pro-
essentiality and synthetic lethality analysis. Mol Syst Biol. 2009;5:301. duction of isoprenoids: carotenoids and isoprenoid-based biofuels. Synth
https:// doi. org/ 10. 1038/ msb. 2009. 56. Syst Biotechnol. 2017;2(3):167–75. https:// doi. org/ 10. 1016/j. synbio. 2017.
49. Pratapa A, Balachandran S, Raman K. Fast-SL: an efficient algorithm to 08. 001.
identify synthetic lethal sets in metabolic networks. Bioinformatics. 69. Yang M, Zhang X. Construction of pyruvate producing strain with intact
2015;31(20):3299–305. https:// doi. org/ 10. 1093/ bioin forma tics/ btv352. pyruvate dehydrogenase and genome-wide transcription analysis.
50. von Kamp A, Klamt S. Enumeration of smallest intervention strate- World J Microbiol Biotechnol. 2017;33(3):59. https:// doi. org/ 10. 1007/
gies in genome-scale metabolic networks. PLoS Comput Biol. s11274- 016- 2202-5.
2014;10(1):e1003378. https:// doi. org/ 10. 1371/ journ al. pcbi. 10033 78. 70. Li M, et al. Recent advances of metabolic engineering strategies in natural
51. Klamt S, Mahadevan R, von Kamp A. Speeding up the core algorithm isoprenoid production using cell factories. Nat Prod Rep. 2020;37(1):80–
for the dual calculation of minimal cut sets in large metabolic net- 99. https:// doi. org/ 10. 1039/ C9NP0 0016J.
works. BMC Bioinformatics. 2020;21(1):510. https:// doi. org/ 10. 1186/ 71. Zhu LW, Tang YJ. Current advances of succinate biosynthesis in metaboli-
s12859- 020- 03837-3. cally engineered Escherichia coli. Biotechnol Adv. 2017;35(8):1040–48.
52. Schneider P, von Kamp A, Klamt S. An extended and generalized frame- https:// doi. org/ 10. 1016/j. biote chadv. 2017. 09. 007.
work for the calculation of metabolic intervention strategies based on 72. Liebal UW, Blank LM, Ebert BE. C O to succinic acid—Estimating the
2
minimal cut sets. PLoS Comput Biol. 2020;16(7):e1008110. https:// doi. org/ potential of biocatalytic routes. Metab Eng Commun. 2018;7:e00075.
10. 1371/ journ al. pcbi. 10081 10 https:// doi. org/ 10. 1016/j. mec. 2018. e00075.
53. Banerjee D, et al. Genome-scale metabolic rewiring improves titers rates 73. Ahn JH, Jang YS, Lee SY. Production of succinic acid by metabolically
and yields of the non-native product indigoidine at scale. Nat Commun. engineered microorganisms. Curr Opin Biotechnol. 2016;42:54–66.
2020;11(1):5385. https:// doi. org/ 10. 1038/ s41467- 020- 19171-4. https:// doi. org/ 10. 1016/j. copbio. 2016. 02. 034.
54. Alter TB, Ebert BE. Determination of growth-coupling strategies and their 74. Comba S, Arabolaza A, Gramajo H. Emerging engineering principles for
underlying principles.BMCBioinformatics. 2019;20(1):447. https:// doi. org/ yield improvement in microbial cell design. Comput Struct Biotechnol J.
10. 1186/ s12859- 019- 2946-7. 2012;3(4):e201210016. https:// doi. org/ 10. 5936/ csbj. 20121 0016.
55. Feist AM, Zielinski DC, Orth JD, Schellenberger J, Herrgard MJ, Palsson BØ. 75. Fisher AK, Freedman BG, Bevan DR, Senger RS. A review of metabolic
Model-driven evaluation of the production potential for growth-coupled and enzymatic engineering strategies for designing and optimizing

---

<!-- Page 22 -->

Hassani et al. Microbial Cell Factories (2024) 23:37 Page 22 of 22
performance of microbial cell factories. Comput Struct Biotechnol J.
2014;11(18):91–9. https:// doi. org/ 10. 1016/j. csbj. 2014. 08. 010.
76. Hädicke O, Klamt S. Computing complex metabolic intervention strate-
gies using constrained minimal cut sets. Metab Eng. 2011;13(2):204–13.
https:// doi. org/ 10. 1016/j. ymben. 2010. 12. 004.
77. Klamt S, Gilles ED. Minimal cut sets in biochemical reaction networks.
Bioinformatics. 2004;20(2):226–34. https:// doi. org/ 10. 1093/ bioin forma
tics/ btg395.
78. Klamt S. Generalized concept of minimal cut sets in biochemical net-
works. Biosystems. 2006;83(2–3):233–47. https:// doi. org/ 10. 1016/j. biosy
stems. 2005. 04. 009.
79. Burgard A, Van Dien S. Methods and organisms for the growth-coupled
production of succinate. 2007. https:// paten ts. google. com/ patent/ US200
70111 294A1/ en
80. Sun X, et al. Synthesis of chemicals by metabolic engineering of
microbes. Chem Soc Rev. 2015;44(11):3760–85. https:// doi. org/ 10. 1039/
c5cs0 0159e.
Publisher’s Note
Springer Nature remains neutral with regard to jurisdictional claims in
published maps and institutional affiliations.
