<!-- Page 1 -->

Available online at www.sciencedirect.com
Perspectives for self-driving labs in synthetic biology
]]
1,2,3,4 1,2,3 16 ]]
Hector G Martin , Tijana Radivojevic , Jeremy Zucker ,
]]]]]]
1,5,6 3,15 5,8
Kristofer Bouchard , Jess Sustarich , Sean Peisert ,
7 1,2,3 2,13
Dan Arnold , Nathan Hillson , Gyorgy Babnigg ,
1,2,3,9 1
Jose M Marti , Christopher J Mungall ,
2,17 18 12
Gregg T Beckham , Lucas Waldburger , James Carothers ,
10,11 5
ShivShankar Sundaram , Deb Agarwal ,
1,2,3 1,3
Blake A Simmons , Tyler Backman ,
1,3 1,2,14
Deepanwita Banerjee , Deepti Tanjore ,
5 3,10
Lavanya Ramakrishnan and Anup Singh
Self-driving labs (SDLs) combine fully automated 15 Biomaterials and Biomanufacturing Division, Sandia National
Laboratories, Livermore, CA, United States
experiments with artificial intelligence (AI) that decides the
16 Earth and Biological Sciences Division, Pacific Northwest National
next set of experiments. Taken to their ultimate expression,
Laboratories, Richland, WA, United States
SDLs could usher a new paradigm of scientific research, 17 Resources and Enabling Sciences Center, National Renewable
where the world is probed, interpreted, and explained by Energy Laboratory, Golden, CO 80401, United States
machines for human benefit. While there are functioning 18 Department of Bioengineering, University of California, Berkeley, CA,
United States
SDLs in the fields of chemistry and materials science, we
contend that synthetic biology provides a unique opportunity
Corresponding author: Martin, Hector G (hgmartin@lbl.gov)
since the genome provides a single target for affecting the
incredibly wide repertoire of biological cell behavior.
Current Opinion in Biotechnology 2023, 79:102881
However, the level of investment required for the creation of
biological SDLs is only warranted if directed toward solving This review comes from a themed issue on Systems Biology
difficult and enabling biological questions. Here, we discuss Edited by Howard Salis
challenges and opportunities in creating SDLs for synthetic
For complete overview of the section, please refer to the article
biology.
collection, “Systems Biology (2023)”
Available online 3 January 2023
Addresses
1 Lawrence Berkeley National Laboratory, Biological Systems and https://doi.org/10.1016/j.copbio.2022.102881
Engineering Division, Berkeley, CA, United States
0958–1669/© 2022 The Author(s). Published by Elsevier Ltd. This is
2 Department of Energy, Agile BioFoundry, Emeryville, CA, United States
an open access article under the CC BY license (http://
3 Joint BioEnergy Institute, Emeryville, CA, United States
creativecommons.org/licenses/by/4.0/).
4 BCAM, Basque Center for Applied Mathematics, Bilbao, Spain
5 Lawrence Berkeley National Laboratory, Scientific Data Division,
Berkeley, CA, United States
6 Helen Wills Neuroscience Institute and Redwood Center for
Theoretical Neuroscience, Berkeley, CA, United States
7 Lawrence Berkeley National Laboratory, Energy Storage and
Distributed Resources Division, Berkeley, CA, United States What is a self-driving lab?
8 University of California, Davis, Department of Computer Science, Self-driving labs (SDLs), or autonomous experimentation,
Davis, CA, United States
combine robotics for automated experiments and data col-
9 Global Security Computing Applications Division, Lawrence Livermore
National Laboratory, Livermore, CA, United States lection, with artificial intelligence (AI) systems that use
10 Engineering Directorate, Lawrence Livermore National Laboratory, these data to recommend follow-up experiments [1–3]
Livermore, CA, United States (Fig. 1). These recommendations potentially involve not
11 Center for Bioengineering, Lawrence Livermore National Laboratory,
just the conditions and parts to be used for the next ex-
Livermore, CA, United States
12 Department of Chemical Engineering, Molecular Engineering & periment, but also which underlying hypothesis to test.
Sciences Institute and Center for Synthetic Biology, University of
Washington, Seattle, WA, United States A possible example of a SDL in synthetic biology could
13 Biosciences Division, Argonne National Laboratory, Argonne, IL, involve a DNA assembly microfluidic chip that auto-
United States
matically produces variants of a given pathway producing a
14 Advanced Biofuels and Bioproducts Process Development Unit,
metabolite of interest (e.g. the biofuel precursor
Lawrence Berkeley National Laboratory, Berkeley, CA, United States
www.sciencedirect.com Current Opinion in Biotechnology 2023, 79:102881

---

<!-- Page 2 -->

2 Systems Biology
Figure 1 Figure 2
Current Opinion in Biotechnology
SDLs combine automated robotic platforms and data collection with AI
that processes these data to decide the next set of experiments to
perform and, potentially, which hypotheses and theories to test.
bisabolene), transforms them into a host (e.g. a bacteria
such as E. coli, P. putida, or R. toruloides), and is able to
culture this host and measure the corresponding bisabo- Current Opinion in Biotechnology
lene production. This automated experiment setup would
SDLs are level-3 autonomy systems. Autonomy levels for SDLs describe
be coupled with an AI recommendation engine that takes
the degree of independence from human intervention. At level 0, all
these experimental data and proposes different pathway
experimental design and execution, as well as data capture, is handled
variants with the goal of maximizing bisabolene produc- by humans. At level 1, some repetitive tasks are outsourced to robots.
tion. A conceivable expansion could add the ability to Level 2 requires systematic digital description of protocols and
replace specific genetic parts beyond the bisabolene experiments, as well as machine-interpretable data, such as in the
laboratory work planner Aquarium [5]. Level 3 involves the closed
pathway, so as to have an effect on precursor supply. The
Design–Build–Test–Learn cycles that can be considered the minimum
hypotheses generated by the AI in terms of recommended
requisite for a SDL, along with interpretations of routine analyses and
pathway variants and gene edits would be tested by the flagging anomalies for humans to handle. Level 4 involves robotic
automated microfluidic chip in the next cycle. protocol execution and routine data analyses, as in ‘Adam’ and ‘Eve’
[6,7], with humans involved only as setting goals and plans (i.e. SDL
works as a lab assistant to humans). At level 5, humans just set goals
The SDL concept requires full autonomy from humans. A
and receive results (i.e. SDL behaves as investigator and human as
partially automated system, or one that requires human in-
manager).
tervention to finish the cycle of experimentation/planning is Adapted from Beal and Rogers [4].
not, rigorously speaking, a SDL. Full automation for the
cycle is not a whimsical requirement, but rather enables the
full potential of SDLs. Completely automated systems can
reach duty cycles (e.g. 24/7/365 operation), experiment-to- car industry to entertain the concept of ‘Degrees of au-
experiment reproducibility, and efficiency that are un- tonomy’ in self-driving cars. For this reason, a similar set
attainable by humans. Furthermore, they are potentially of ‘Autonomy levels’ has been proposed to both describe
linearly scalable (e.g. simply acquire more copies of the the current technological capabilities and incentivize the
equipment), and, as a consequence, can produce large gradual development into fully autonomous systems [4]
amounts of high-quality data and metadata. Such large vo- (see Fig. 2). In practical terms, systems displaying an
lumes of high-quality data can make AI systems particularly autonomy level of three or above can be considered
effective and insightful: artificial neural networks, for ex- SDLs, since they display closed Design–Build–Tes-
ample, are known to be most effective once a certain t–Learn loops.
threshold of training data is available. These benefits will be
critical to produce improved scientific understanding, and Some examples of existing self-driving labs
significantly decrease time to the desired bioproducts. SDLs are not unattainable fantasies: there are indeed
several published examples, although focused on narrow
However crucial, the requirement of full autonomy may tasks. In chemistry and materials science, SDLs are
be too stringent for the current state of technology, so it enjoying an upsurge in popularity, and several examples
is useful to consider intermediate steps toward the rea- are now available. In biology, there are some budding
lization of SDLs. Similar considerations have moved the examples, which show the promise of this approach.
Current Opinion in Biotechnology 2023, 79:102881 www.sciencedirect.com

---

<!-- Page 3 -->

Self-driving labs in synthetic biology Martin et al. 3
In chemistry [3] and material sciences [2], the maturity of can now be easily manipulated via gene-editing techni-
automation platforms and the availability of machine ques or evolutionary approaches. In material sciences,
learning (ML) methods has enabled the creation of several the Young’s modulus or hole mobility of a material de-
SDLs or almost fully automated processes. For example, pends on a variety of structural and chemical elements
Granda et al. [8] developed a platform that explores the that are distributed over the material, and can be com-
chemical space using an organic synthesis robot combined plicated to locate and modify. In biology, a cell’s phe-
with an ML model to predict reactivity of possible reagent notype is determined primarily by a combination of its
combinations. More recently, Christensen et al. [9] devel- environment and its genome. The genome’s capability
oped an automated closed-loop system for parallel process to encode an incredibly varied set of phenotypes is
optimization in reactors to optimize the yield of a stereo- showcased by the fantastic diversity provided by evo-
selective Suzuki–Miyaura cross-coupling reaction. Wang lution on Earth over the last three billion years. These
et al. [10] developed a self-optimizing millifluidic reactor for phenotypes range from metabolic adaptation to extreme
scaling the manufacturing of nanomaterials with improved environments, carbon capture from atmosphere, pro-
optical properties. In material sciences, Macleod et al. used duction of valuable chemicals and bioproducts, and
the modular robotic platform Ada capable of autonomously multicellular coordination, to the emergence of con-
optimizing the hole mobility of the materials commonly sciousness and intelligence. Furthermore, the genome is
used in perovskite solar cells and consumer electronics [11], now more accessible than ever before through recent
as well as discovering new synthesis conditions for opti- advances in CRISPR-enabled gene-editing tools [22],
mized conductivities and processing temperatures for pal- and evolutionary approaches comprising, for example,
ladium films [12]. Robotics coupled with Bayesian targeted mutagenesis and natural selection [23,24]. This
optimization were used in multiple cases: autonomous combination of accessibility, centralization, evolvability,
synthesis and resistance minimization of thin films [13], and ability to produce very diverse outcomes is un-
optimizing mechanical properties of structures for a given paralleled and holds the promise of unique societal
application [14], improving adhesive formulations [15], impact.
achieving targeted 3D print features in additive manu-
facturing [16], discovering novel battery electrolytes [17], Conversely, distinctive hurdles involve automation cap-
and search for photocatalyst mixtures with improved activity abilities that are nascent compared with other fields, and
for hydrogen production from water [18]. biology curricula that do not currently emphasize the
backgrounds in mathematics and robotics that are critical
Biology saw the first published closed-loop systems for for creating SDLs (see section ‘Gaps for realizing self-
scientific discovery in the form of Adam, a robot scientist driving labs’ for further discussion).
that determined gene function through gene deletion
and auxotrophic experiments in S. cerevisiae [6]. Eve Benefits of self-driving labs
followed for the repurposing of drugs, identifying an The main appeal for SDLs is their ability to enable
angiogenesis-inhibiting anticancer drug for antimalarial significant scientific advances, which justifies their sig-
use [7]. More recently, Si et al. [19] developed an au- nificant cost. These scientific advances involve, first,
tomated platform for multiplex genome-scale en- solving difficult biology questions that are intractable
gineering in S. cerevisiae, Hamedirad et al. [20] used the with current approaches. Second, and arguably more
BioAutomata fully automated platform to optimize pro- importantly, they involve upending the development of
moter choice in lycopene-producing E. coli, and Kanda science as we know it, to accelerate it by leveraging AI.
et al. [21] used an autonomous robotic system to find the
optimal conditions for inducing stem cell differentiation The high level of investment needed to enable biolo-
into retinal pigment epithelial cells. gical SDLs is only warranted if directed toward solving
important and difficult biological problems. These in-
While funding for SDLs is still limited, there are in- volve biological problems that could take decades, or
stances from the US National Science Foundation (NSF), even centuries, to solve otherwise: for example, the
the Canadian National Research Council, and (Defense prediction of protein structure from sequence [25]. Some
Advanced Research Projects Agency) DARPA. examples of remaining difficult biological problems, in-
cluding both topics of fundamental and practical im-
portance, are:
The special case of biology
SDLs present unique opportunities and challenges in 1. Systematic increase of Titer, Rate, and Yield (TRY) for
biology, as compared with other disciplines in which bioengineered microbial strains. A significant obstacle in
they have been deployed. developing commercially viable processes is reaching
economically viable levels of TRY of a biologically
A unique opportunity is the collection of the cellular produced small molecule. The traditional approach
instructions in a single repository (genomic DNA) that involves heuristic combinatorial processes that rely on
www.sciencedirect.com Current Opinion in Biotechnology 2023, 79:102881

---

<!-- Page 4 -->

4 Systems Biology
Figure 3
Current Opinion in Biotechnology
We envision SDLs working in a network of other SDLs and humans. To start with, in order for the SDL to make progress with respect to the current
state of scientific knowledge, it must be able to draw information from existing literature. The SDL should also be able to communicate with other SDLs
so as to efficiently partition the scientific phase space (i.e. the abstract space conformed by all possible configurable experiment parameter choices) to
be explored (e.g. SDL focuses on one promoter set and SDL focuses on another promoter set). Current technical limitations limit our ability to
1 2
automate all experiments, so SDLs should be able to produce unequivocal instructions for humans to follow in traditional labs, and ingest the data so
produced. The final result of the operation of this network will be a digital twin of the system under study. This digital twin will likely start as a very crude
and qualitative description of system parts and their connections, which will evolve as new information is obtained into more sophisticated
mechanistic, quantitatively predictive models of the system under study (à la whole-cell model [28], sporting accurate predictions). These digital twins
would be used by humans to access the scientific knowledge generated through this hybrid network and suggest their own recommendations.
Whole-cell model figure adapted from Kerr et al. [28].
strain-specific in-depth metabolic knowledge (i.e. limited in space, due to the very high logistic cost of
the‘pull-push-block’ approach [26]), and do not transporting them to orbit and beyond [32].
transfer well to other products, pathways, and hosts.
2. Mapping of regulatory networks. Perhaps the largest Each of these challenges will require very different ro-
hurdle in predicting an organism’s metabolism is to botic setups for the corresponding SDL. The cost of
understand how it is regulated, which involves the each of these SDLs would be directly related to its
mechanistic understanding of a large part of its scope: SDLs exploring a large phase space and using
genomic complement [27]. sophisticated assays are bound to be costly, whereas
3. Elucidating the genotype-to-phenotype link. This chal- simpler SDLs can potentially be quite affordable.
lenge is, arguably, the central problem in biology, but
despite promising advances [28–30], it remains be- Perhaps, the most important impact of SDLs in science
yond our reach to predict accurately and quantita- would come from the ability to automatically build sci-
tively the behavior of an organism given its genome. entific knowledge. By scientific knowledge, we mean a
4. Inverse design of microbiomes. Microbial communities generalized body of facts, laws, and theories able to ex-
exhibit remarkable capabilities, from driving Earth’s plain and predict the behavior of the system under
biogeochemical cycles to increasing crop productivity study. We envision SDLs to be able to draw from prior
[31]. However, we currently lack the knowledge to knowledge and external sources as needed to perform
design communities to meet a specification: for ex- experiments that improve this knowledge (Fig. 3). This
ample, remain stable over a year, or remove X grams/ improvement would be reflected in increased mechan-
liter/hour of phosphorus from wastewater. istic understanding and predictive power. We envisage
5. Exploring biological behavior outside Earth. that a SDL would store its accumulating knowledge as a
Understanding how biological systems react to being digital twin, whose role evolves as more is learned about
in deep space or on another planet/satellite is fun- the biological system it is analyzing. Digital twins are
damental to enable space exploration, and the pro- virtual replicas of real-world products, systems, beings,
liferation of humankind beyond a single planet. communities, or even cities, and have become critical
However, workforce and equipment are extremely assets for industry [33]. The initial role, in many cases, of
Current Opinion in Biotechnology 2023, 79:102881 www.sciencedirect.com

---

<!-- Page 5 -->

Self-driving labs in synthetic biology Martin et al. 5
the digital twin would be simply to suggest experiments instrumentation, are very difficult to link together in the
that identify the parts and their associations. Once suf- seamless manner SDLs require (Fig. 2). Microfluidics
ficient experimental data have been generated to iden- offer the opportunity to provide this seamless integration
tify these associations, the role of the digital twin would by encapsulating cells and reagents into droplets, and
be to suggest experiments that determine which corre- manipulating them precisely. Indeed, microfluidic plat-
lations are causal. Once causal effects have been eluci- forms have been proposed for miniaturization of biolo-
dated, the role of the digital twin would evolve into gical reactions, including DNA synthesis and assembly
designing experiments to validate a mechanistic theory [40], transformation [41,42], cell-free expression [43], and
capable of explaining and quantitatively predicting these phenotypic screening by fluorescence [44] and mass
causal effects. Once this theory is calibrated, the role of spectrometry [45]. Truly disruptive functionalities can be
the digital twin would transition into designing experi- achieved by combining these capabilities with new de-
ments that enable new biological systems to be built to a velopments in molecular sensors embedded on semi-
desired specification (inverse design). In the words of conductor chips [46], wireless optically activated
Feynman, “What I cannot create, I do not understand”. microscopic sensors [47], monitoring of free radicals
We anticipate that this strategy to build scientific through fluorescent nanodiamonds [48], metabolic mod-
knowledge would involve a hybrid approach, combining ulation through optogenetics [49], or manipulation of cells
pure SDLs with humans, traditional labs, and existing with light [50]. Microfluidic sampling from bioreactors can
literature (Fig. 3). also enable real-time sensing and imaging of cells in their
environments, enabling continuous data capture. More-
Admittedly, this type of AI technology is not yet avail- over, these microfluidic platforms are far more affordable
able, despite significant recent advances in question- and use less reagents than robotic workstations, permit-
answering and summarization [34], integrating prior ting a much larger number of experiments and demo-
knowledge into AI systems [35], and automated deriva- cratizing the access to synthetic biology. Their routine use
tion of generalizable rules [36,37]. Massive language in synthetic biology, however, necessitates sustained in-
models such as GTP-3 are able to perform impressive vestment to enable seamless functioning and the auto-
tasks that appear to mimic natural language under- mation of the full range of synthetic biology processes.
standing, but these systems are ungrounded and are
essentially performing pattern matching, and much Novel AI algorithms are needed to make SDLs a reality in
needs to be done to unite classical symbolic reasoning synthetic biology. Although current algorithms can guide
systems with deep learning approaches [38]. Indeed, the the metabolic engineering process effectively [51], wide-
scientific process of developing and experimentally spread adoption of SDLs will require the AI to understand
testing hypotheses, to create a falsifiable worldview that context, and the ability to produce interpretable knowl-
can be used to make quantitative predictions and inform edge. This means the ability to 1) use prior knowledge to
decision-making, comes quite close to the definition of inform the AI in the SDL, and 2) extract knowledge out of
artificial general intelligence. the predictive capabilities of the AI such that it can be
extrapolated to related, but different, experimental con-
ditions by other human researchers or SDLs (Fig. 3). The
Gaps for realizing self-driving labs ability to leverage and produce extrapolatable knowledge
The benefits of SDLs necessitate several technological is critical if we are to benefit from a large amount of SDLs.
and social advances to become a reality. The gaps in- Otherwise, humans would become the bottleneck in
volve limitations in current automation technologies, AI transferring the knowledge accumulated in the digital
algorithms, data management, and, importantly, socio- twins from and to the SDLs (Fig. 3). One possibility to
logical hurdles. introduce this much-needed context may lie in the use of
foundational models [52], trained on massive datasets, and
While automation of synthetic biology processes using adapted to specific use cases.
liquid-handling commercial robotic workstations is
gaining momentum, this approach has limitations for Data management is a critical link between automation
SDLs that new technologies may help ease. Companies and AI algorithms that has been often neglected in the
such as, for example, Ginkgo Bioworks or Amyris auto- past. While often considered a burdensome chore, there
mate their discovery process using these workstations, is simply no AI without data, and there are no SDLs
and a few are even providing automation as a service [39]. without AI. General ontologies and extensible standards
However, the processes automated in the chemistry and for data and protocols are critical if large amounts of data
material sciences SDLs discussed above are only a subset are to be collected and seamlessly integrated into an
of the ones needed in synthetic biology. Typical mole- ecosystem involving continuous data exchange among
cular biology processes such as cell transformations via SDLs and human researchers.
electroporation, colony picking, plating, and outgrowth,
while doable through liquid handlers and other
www.sciencedirect.com Current Opinion in Biotechnology 2023, 79:102881

---

<!-- Page 6 -->

6 Systems Biology
Another important obstacle for the creation of SDLs in (https://abpdu.lbl.gov/), and the DOE Joint BioEnergy Institute (http://
biology involves the sociological challenges in having www.jbei.org), supported by the U. S. Department of Energy, Energy
Efficiency and Renewable Energy, Bioenergy Technologies Office, and the
computer scientists and automation engineers work to-
Office of Science, through contract DE-AC02-05CH11231 between
gether with molecular and synthetic biologists. These
Lawrence Berkeley National Laboratory and the U.S. Department of
two worlds embody very different scientific cultures, Energy. S.P. and D.A. were supported by Laboratory Directed Research
which are reflected not only in how they solve problems, and Development (LDRD) funds provided by Lawrence Berkeley
National Laboratory, operated for the U.S. Department of Energy under
but also which problems they consider worth solving
the same contract. H.G.M. was also supported by the Basque Government
[53]. Having them work together constructively is, ar- through the BERC 2018–2021 program and by the Spanish Ministry of
guably, harder than the technological challenges faced Economy and Competitiveness MINECO: BCAM Severo Ochoa ex-
by SDLs in biology. Currently, computational and bench cellence accreditation SEV-2017-0718. K.E.B. was funded by the
Department of Energy, Advanced Scientific Computing Research. J.M.M.
scientists are trained very differently: a critical first step
was supported by the U.S. Department of Energy (DOE), Office of
is to design a training curriculum that exposes them to Science, Office of Biological and Environmental Research, Lawrence
each other's world. Livermore National Laboratory (LLNL) SFA “From Sequence to Cell to
Population: Secure and Robust Biosystems Design for Environmental
Microorganisms,” under Contract DE-AC52-07NA27344 (LLNL-JRNL-
Conclusion 837127). J.M.C. was supported in part by the U.S. Department of Energy,
While SDLs are bound to be costly endeavors, the ex- Energy Efficiency and Renewable Energy, Bioenergy Technologies Office
under contract DE-EE0008927. Gy.B. was supported by the “Rapid Design
pected returns make them worthwhile undertakings. A
and Engineering of Smart and Secure Microbiological Systems” project
fully functioning network of SDLs and human re-
funded by the Biological Systems Science Division’s Genomic Science
searchers (Fig. 3) would not only provide significant Program, within the U.S. Department of Energy, Office of Science,
biological knowledge, but also the ability to fully exploit Biological and Environmental Research. Argonne National Laboratory is
managed by UChicago Argonne, LLC for DOE under contract number
synthetic biology for biomanufacturing purposes. Fur-
DE-AC02-06CH11357. LW was funded by the US National Science
thermore, they would provide the opportunity to un- Foundation Graduate Research Fellowship. The views and opinions of the
derstand and improve the process of constructing authors expressed herein do not necessarily state or reflect those of the
scientific knowledge. In that sense, the large project of United States Government or any agency thereof. Neither the United
States Government nor any agency thereof, nor any of their employees,
creating SDLs mirrors the Human Genome Project, in
makes any warranty, expressed or implied, or assumes any legal liability or
that they show a potential to fundamentally transform responsibility or the accuracy, completeness, or usefulness of any in-
the field of biology. formation, apparatus, product, or process disclosed, or represents that its use
would not infringe privately owned rights. The United States Government
retains and the publisher, by accepting the article for publication, ac-
We must, however, be aware of the risks associated with knowledges that the United States Government retains a nonexclusive,
SDLs: their use for nefarious purposes (e.g. virus paid-up, irrevocable, worldwide license to publish or reproduce the pub-
synthesis), including the ability to be manipulated via lished form of this paper, or allow others to do so, for United States
Government purposes. The Department of Energy will provide public
remote cyberattacks. A more subtle risk involves the
access to these results of federally sponsored research in accordance with
possible long-term misalignment with our values and the DOE Public Access Plan (http://energy.gov/downloads/doe-public-
goals, which can be challenging to fully encode in a access-plan). Funding for open-access charge: US Department of Energy.
machine-readable manner, potentially allowing the
system to act in an unintended or undesired manner.
References and recommended reading
Despite the risks and challenges, we believe that SDLs Papers of particular interest, published within the period of review, have
represent the next leap forward in the progress of sci- been highlighted as:
entific research, and that synthetic biology poses a un- •• of special interest
ique opportunity for their development. •• of outstanding interest.
1. Häse F, Roch LM, Aspuru-Guzik A: Next-generation
Conflict of interest statement experimentation with self-driving laboratories. Trends Chem
The authors declare the following financial interests/ 2019, 1:282-291, https://doi.org/10.1016/j.trechm.2019.02.007
personal relationships that may be considered as po- 2. Soldatov MA, Butova VV, Pashkov D, Butakova MA, Medvedev PV,
tential competing interests: Nathan Hillson has financial Chernov AV, et al.: Self-driving laboratories for development of
new functional materials and optimizing known reactions.
interests in TeselaGen Biotechnologies and Ansa Nanomater. 2021, 11:619, https://doi.org/10.3390/nano11030619
Biotechnologies.
3. Bennett JA, Abolhasani M: Autonomous chemical science and
engineering enabled by self-driving laboratories. Curr Opin
Data Availability Chem Eng 2022, 36:100831, https://doi.org/10.1016/j.coche.2022.
100831
No data were used for the research described in the ar- 4. Beal J, Rogers M: Levels of autonomy in synthetic biology
engineering. Mol Syst Biol 2020, 16:e10019, https://doi.org/10.
ticle. 15252/msb.202010019
5. Vrana J, de Lange O, Yang Y, Newman G, Saleem A, Miller A, et al.:
Acknowledgements Aquarium: open-source laboratory software for design,
This work was part of the DOE Agile BioFoundry (http://agilebiofoundry. execution and data management. Synth Biol 2021, 6:ysab006,
https://doi.org/10.1093/synbio/ysab006
org), the Advanced Biofuels and Bioproducts Process Development Unit
Current Opinion in Biotechnology 2023, 79:102881 www.sciencedirect.com

---

<!-- Page 7 -->

Self-driving labs in synthetic biology Martin et al. 7
6. King RD, Whelan KE, Jones FM, Reiser PGK, Bryant CH, 21. Kanda GN, Tsuzuki T, Terada M, Sakai N, Motozawa N, Masuda T,
• Muggleton SH, et al.: Functional genomic hypothesis generation et al.: Robotic search for optimal cell culture in regenerative
and experimentation by a robot scientist. Nature 2004, medicine. eLife 2022, 11:e77007, https://doi.org/10.7554/eLife.77007
427:247-252, https://doi.org/10.1038/nature02236.
Adam is the first published example of a closed-loop system that de- 22. Knott GJ, Doudna JA: CRISPR-Cas guides the future of genetic
signs and executes experiments to test inferred hypotheses. A classic engineering. Science 2018, 361:866-869, https://doi.org/10.1126/
well before SDLs became of widespread interest. science.aat5011
23. Zhong Z, Wong BG, Ravikumar A, Arzumanyan GA, Khalil AS, Liu
7. Williams K, Bilsland E, Sparkes A, Aubrey W, Young M, Soldatova
• LN, et al.: Cheaper faster drug development validated by the CC: Automated continuous evolution of proteins in vivo. ACS
Synth Biol 2020, 9:1270-1276, https://doi.org/10.1021/acssynbio.
repositioning of drugs against neglected tropical diseases. J R
0c00135
Soc Interface 2015, 12:20141289, https://doi.org/10.1098/rsif.
2014.1289. 24. Javanpour AA, Liu CC: Evolving small-molecule biosensors with
Eve constitutes an outstanding example of the use of SDLs to alleviate improved performance and reprogrammed ligand preference
the large cost of drug discovery. using OrthoRep. ACS Synth Biol 2021, 10:2705-2714, https://doi.
org/10.1021/acssynbio.1c00316
8. Granda JM, Donina L, Dragone V, Long D-L, Cronin L: Controlling
•• an organic synthesis robot with machine learning to search for 25. Jumper J, Evans R, Pritzel A, Green T, Figurnov M, Ronneberger O,
new reactivity. Nature 2018, 559:377-381, https://doi.org/10.1038/ et al.: Highly accurate protein structure prediction with
s41586-018-0307-8. AlphaFold. Nature 2021, 596:583-589, https://doi.org/10.1038/
A great example of the potential of SDLs, showing how a robot is able to s41586-021-03819-2
systematically explore chemical space and successfully predict re-
activity. 26. Yan Q, Pfleger BF: Revisiting metabolic engineering strategies
for microbial synthesis of oleochemicals. Metab Eng 2020,
9. Christensen M, Yunker LPE, Adedeji F, Häse F, Roch LM, Gensch 58:35-46, https://doi.org/10.1016/j.ymben.2019.04.009
T, et al.: Data-science driven autonomous process
optimization. Commun Chem 2021, 4:112, https://doi.org/10. 27. Herrgård MJ, Covert MW, Palsson BØ: Reconstruction of
1038/s42004-021-00550-x microbial transcriptional regulatory networks. Curr Opin
Biotechnol 2004, 15:70-77, https://doi.org/10.1016/j.copbio.2003.
10. Wang L, Karadaghi LR, Brutchey RL, Malmstadt N: Self-optimizing 11.002
parallel millifluidic reactor for scaling nanoparticle synthesis.
Chem Commun 2020, 56:3745-3748, https://doi.org/10.1039/ 28. Karr JR, Sanghvi JC, Macklin DN, Gutschow MV, Jacobs JM,
d0cc00064g • Bolival B, et al.: A whole-cell computational model predicts
phenotype from genotype. Cell 2012, 150:389-401, https://doi.
11. MacLeod BP, Parlane FGL, Morrissey TD, Häse F, Roch LM, org/10.1016/j.cell.2012.05.044.
Dettelbach KE, et al.: Self-driving laboratory for accelerated One of the first examples of a whole-cell model, accounting for all an-
discovery of thin-film materials. Sci Adv 2020, 6:eaaz8867, notated gene functions in Mycoplasma genitalium, and validated against
https://doi.org/10.1126/sciadv.aaz8867 a broad range of data.
12. MacLeod BP, Parlane FGL, Rupnow CC, Dettelbach KE, Elliott MS, 29. Macklin DN, Ahn-Horst TA, Choi H, Ruggero NA, Carrera J, Mason
Morrissey TD, et al.: A self-driving laboratory advances the JC, et al.: Simultaneous cross-evaluation of heterogeneous E.
Pareto front for material properties. Nat Commun 2022, 13:995, coli datasets via mechanistic simulation. Science 2020, 369
https://doi.org/10.1038/s41467-022-28580-6 (6502), https://doi.org/10.1126/science.aav3751
13. Shimizu R, Kobayashi S, Watanabe Y, Ando Y, Hitosugi T: 30. Thornburg ZR, Bianchi DM, Brier TA, Gilbert BR, Earnest TM, Melo
Autonomous materials synthesis by machine learning and MCR, et al.: Fundamental behaviors emerge from simulations of
robotics. APL Mater 2020, 8:111110, https://doi.org/10.1063/5. a living minimal cell. Cell 2022, 185:345-360.e28, https://doi.org/
0020370 10.1016/j.cell.2021.12.025
31. Lawson CE, Harcombe WR, Hatzenpichler R, Lindemann SR,
14. Gongora AE, Xu B, Perry W, Okoye C, Riley P, Reyes KG, et al.: A
Löffler FE, O’Malley MA, et al.: Common principles and best
Bayesian experimental autonomous researcher for mechanical
practices for engineering microbiomes. Nat Rev Microbiol 2019,
design. Sci Adv 2020, 6:eaaz1708, https://doi.org/10.1126/sciadv.
17:725-741, https://doi.org/10.1038/s41579-019-0255-9
aaz1708
32. Lauren, Yang J, Scott R, Qutub A, Martin H, Berrios D, et al.:
15. Rooney MB, MacLeod BP, Oldford R, Thompson ZJ, White KL,
Beyond Low Earth Orbit: Biological Research, Artificial
Tungjunyatham J, et al.: A self-driving laboratory designed to
Intelligence, and Self-Driving Labs.
accelerate the discovery of adhesive materials. Digit Discov
2022 1:382-389, https://doi.org/10.1039/D2DD00029F 33. Jiang Y, Yin S, Li K, Luo H, Kaynak O: Industrial applications of
• digital twins. Philos Trans A Math Phys Eng Sci 2021,
16. Deneault JR, Chang J, Myung J, Hooper D, Armstrong A, Pitt M,
379:20200360, https://doi.org/10.1098/rsta.2020.0360.
et al.: Toward autonomous additive manufacturing: Bayesian
Good introduction to digital twins, and how they are becoming an in-
optimization on a 3D printer. MRS Bull 2021, 46:566-575, https://
dustry staple.
doi.org/10.1557/s43577-021-00051-1
34. Neves M, Leser U: Question answering for biology. Methods
17. Dave A, Mitchell J, Kandasamy K, Wang H, Burke S, Paria B, et al.: 2015, 74:36-46, https://doi.org/10.1016/j.ymeth.2014.10.023
Autonomous discovery of battery electrolytes with robotic
experimentation and machine learning. Cell Rep Phys Sci 2020, 35. Cai S, Mao Z, Wang Z, Yin M, Karniadakis GE: Physics-informed
1:100264, https://doi.org/10.1016/j.xcrp.2020.100264 •• neural networks (PINNs) for fluid mechanics: a review. Acta
Mech Sin 2021, 37:1727-1738, https://doi.org/10.1007/s10409-
18. Burger B, Maffettone PM, Gusev VV, Aitchison CM, Bai Y, Wang X, 021-01148-1.
•• et al.: A mobile robotic chemist. Nature 2020, 583:237-241, An informative review on how to embed prior knowledge in AI, in this
https://doi.org/10.1038/s41586-020-2442-2. case for fluid dynamics in the form of PINNs (physics-informed neural
An inspiring use of a mobile robotic arm to automate the researcher networks). Similar approaches would be needed for biology.
rather than the instruments, opening the transition to SDLs for any tra-
ditional lab. 36. Liu Z, Tegmark M: Machine learning conservation laws from
trajectories. Phys Rev Lett 2021, 126:180604, https://doi.org/10.
19. Si T, Chao R, Min Y, Wu Y, Ren W, Zhao H: Automated multiplex 1103/PhysRevLett.126.180604
genome-scale engineering in yeast. Nat Commun 2017, 8:15187,
https://doi.org/10.1038/ncomms15187 37. Guimerà R, Reichardt I, Aguilar-Mogas A, Massucci FA, Miranda M,
•• Pallarès J, et al.: A Bayesian machine scientist to aid in the
20. HamediRad M, Chao R, Weisberg S, Lian J, Sinha S, Zhao H: solution of challenging scientific problems. Sci Adv 2020,
Towards a fully automated algorithm driven platform for 6:eaav6971, https://doi.org/10.1126/sciadv.aav6971.
biosystems design. Nat Commun 2019, 10:5150, https://doi.org/ A stimulating demonstration of the power of ‘machine scientists’, able to
10.1038/s41467-019-13189-z extract closed mathematical models automatically out of data.
www.sciencedirect.com Current Opinion in Biotechnology 2023, 79:102881

---

<!-- Page 8 -->

8 Systems Biology
38. d’Avila GA, Lamb LC: Neurosymbolic AI: the 3rd wave. arXiv activity. Proc Natl Acad Sci USA (5) 2022, 119:e2112812119,
2020, https://doi.org/10.48550/arxiv.2012.05876 https://doi.org/10.1073/pnas.2112812119.
A very interesting report on the possibilities created by embedding
39. Arnold C: Cloud labs: where robots do the research. Nature single molecules in electronic chips.
2022, 606:612-613, https://doi.org/10.1038/d41586-022-01618-x
47. Cortese AJ, Smart CL, Wang T, Reynolds MF, Norris SL, Ji Y, et al.:
40. Lee C-C, Snyder TM, Quake SR: A microfluidic oligonucleotide
Microscopic sensors using optical wireless integrated circuits.
synthesizer. Nucleic Acids Res 2010, 38:2514-2521, https://doi.
Proc Natl Acad Sci USA 2020, 117:9173-9179, https://doi.org/10.
org/10.1093/nar/gkq092
1073/pnas.1919677117
41. Gach PC, Shih SCC, Sustarich J, Keasling JD, Hillson NJ, Adams
48. Nie L, Nusantara AC, Damle VG, Sharmin R, Evans EPP, Hemelaar
• PD, et al.: A droplet microfluidic platform for automating
SR, et al.: Quantum monitoring of cellular metabolic activities in
genetic engineering. ACS Synth Biol 2016, 5:426-433, https://doi.
single mitochondria. Sci Adv (21) 2021, 7:eabf0573, https://doi.
org/10.1021/acssynbio.6b00011.
org/10.1126/sciadv.abf0573
A nice demonstration of what microfluidics can achieve in terms of
automating synthetic biology protocols.
49. Wegner SA, Barocio-Galindo RM, Avalos JL: The bright frontiers
42. Iwai K, Wehrs M, Garber M, Sustarich J, Washburn L, Costello Z, of microbial metabolic optogenetics. Curr Opin Chem Biol 2022,
et al.: Scalable and automated CRISPR-based strain 71:102207, https://doi.org/10.1016/j.cbpa.2022.102207
engineering using droplet microfluidics. Micro Nanoeng 2022,
50. Rienzo M, Lin K-C, Mobilia KC, Sackmann EK, Kurz V, Navidi AH,
8:31, https://doi.org/10.1038/s41378-022-00357-3
•• et al.: High-throughput optofluidic screening for improved
43. Hori Y, Kantak C, Murray RM, Abate AR: Cell-free extract based microbial cell factories via real-time micron-scale productivity
optimization of biomolecular circuits with droplet monitoring. Lab Chip 2021, 21:2901-2912, https://doi.org/10.
microfluidics. Lab Chip 2017, 17:3037-3042, https://doi.org/10. 1039/d1lc00389e.
1039/c7lc00552k This paper demonstrates the use of microfluidics and automated cell
manipulation through light for synthetic biology, providing a promising
44. Iwai K, Ando D, Kim PW, Gach PC, Raje M, Duncomb TA, et al.: platform for SDLs.
Automated flow-based/digital microfluidic platform integrated
with onsite electroporation process for multiplex genetic 51. Lawson CE, Martí JM, Radivojevic T, Jonnalagadda SVR, Gentz R,
engineering applications. In Proceedings of the 2018 IEEE Micro • Hillson NJ, et al.: Machine learning for metabolic engineering: a
Electro Mechanical Systems (MEMS). IEEE; 2018:1229–1232. review. Metab Eng 2021, 63:34-60, https://doi.org/10.1016/j.
doi:10.1109/MEMSYS.2018.8346785. ymben.2020.10.005.
Interesting review on the current and possible applications of AI in
45. Heinemann J, Deng K, Shih SCC, Gao J, Adams PD, Singh AK, metabolic engineering and synthetic biology.
et al.: On-chip integration of droplet microfluidics and
nanostructure-initiator mass spectrometry for enzyme 52. On the Opportunities and Risks of Foundation Models; 2021
screening. Lab Chip 2017, 17:323-331, https://doi.org/10.1039/ [cited 15 Aug 2022]. Available from: 〈https://fsi.stanford.edu/
c6lc01182a publication/opportunities-and-risks-foundation-models〉.
46. Fuller CW, Padayatti PS, Abderrahim H, Adamiak L, Alagar N, 53. Eslami M, Adler A, Caceres RS, Dunn JG, Kelley-Loughnane N,
•• Ananthapadmanabhan N, et al.: Molecular electronics sensors Varaljay VA, et al.: Artificial intelligence for synthetic biology.
on a scalable semiconductor chip: a platform for single- Commun ACM 2022, 65:88-97, https://doi.org/10.1145/3500922
molecule measurement of binding kinetics and enzyme
Current Opinion in Biotechnology 2023, 79:102881 www.sciencedirect.com
