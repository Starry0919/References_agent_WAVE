<!-- Page 1 -->

Autonomous ‘self-driving’
laboratories: a review
of technology and
policy implications
Review
Alexander V. Tobias and Adam Wahab
Cite this article: Tobias AV, Wahab A. 2025 Department of Biotechnology and Life Sciences, The MITRE Corporation, McLean, VA, USA
Autonomous ‘self-driving’ laboratories: a review
AVT, 0000-0002-5866-5254
of technology and policy implications. R. Soc.
Open Sci. 12: 250646.
This article reviews and provides perspective on the emerging
https://doi.org/10.1098/rsos.250646 technology of autonomous, ‘self-driving’ laboratories (SDLs)
that combine artificial intelligence (AI) and laboratory
automation to perform research in chemistry, materials
Received: 30 March 2025
science and biological sciences. Today’s most capable
Accepted: 16 June 2025 SDLs automate nearly the entire scientific method, from
hypothesis generation, experimental design, experiment
execution and data analysis, to drawing conclusions and
Subject Category:
updating hypotheses for subsequent rounds of optimization
Science, society and policy
or discovery. ‘Cloud labs’ offer subscription-based remotecontrol access to experimental capabilities. Reports of
AI-directed experiments executed in cloud labs are appearing
Subject Areas:
in the literature, previewing a democratization of science that
artificial intelligence, materials science,
intrigues but inspires concern. Indeed, SDLs have potential
biotechnology
implications for society far beyond the academy. Inventions
emerging from AI-driven science pose a grand challenge, as
patent laws across the world recognize only human inventors.
Keywords:
If the inventions they generate remain unpatentable, funding
autonomous science, self-driving laboratories, for SDLs may be constrained. SDLs raise safety and
artificial intelligence, closed-loop security concerns. We deem them surmountable with a
experimentation, cloud laboratories, intellectual proactive approach, ultimate human accountability and robust
cybersecurity measures. Finally, we estimate the impacts of
property, autonomous chemistry, autonomous
SDLs on the technical labour force. Our analysis suggests that
materials science, autonomous biology
SDLs may displace some scientific roles but are likely to create
many new opportunities.
Author for correspondence:
Alexander V. Tobias
e-mail: avtobias83@gmail.com 1. Introduction
The advancement of human civilizations has been driven by
the development of ever more powerful and useful tools.
Seminal inventions from the abacus to the personal computer
have enabled step-change leaps in the speed, power and
© 2025 The Authors. Published by the Royal Society under the terms of the Creative
Commons Attribution License http://creativecommons.org/licenses/by/4.0/, which permits
unrestricted use, provided the original author and source are credited.

---

<!-- Page 2 -->

accuracy with which societies perform the very work of scientific discovery and technology develop- 2
ment. Foundational tools tend to engender positive feedback loops that convert once arduous or
laborious undertakings into routine, automated and often largely hidden tasks.
The release of the large language model (LLM) ChatGPT in 2022 launched an unprecedented wave
of artificial intelligence (AI) [1] directly into the hands of the public. This wave has already impacted
nearly all facets of society, including science and technology development. Author and founder of the
AI company DeepMind, Mustafa Suleyman, remarked that the hallmark distinction between artificial
intelligence and all previous technologies is that AI systems can self-teach, improve themselves and
perform many complex tasks and workflows autonomously [2].
The scientific method can be viewed as a cycle of steps. Researchers conceive of questions and
formulate testable hypotheses based thereon. Experiments are designed to test the hypotheses. The
experiments are conducted, and the ensuing data are analysed and processed into results that, ideally,
point toward acceptance or rejection of the hypothesis. As the results are disseminated throughout the
research community, they may inspire follow-on ideas, questions and hypotheses. Thus, additional
turns of the cycle follow and science advances. Technology has accelerated, routinized, reduced
costs and otherwise transformed key steps of this cycle. Computers and software have dramatically
improved and democratized the analysis and processing of data and the ability to run simulations to
better understand or even replace several types of experiments. In some disciplines such as biotechnology, robotics and precision machines have substantially increased the number of experiments that can
be performed per unit of space or time and reduced human labour to a small fraction of that required
for manual workflows; however, the conception of research questions and hypotheses have, until the
last few years, been the exclusive domain of highly educated humans. These tasks were simply too
complex, subtle, or required too much knowledge or understanding to even be considered tractable by
a machine.
A veritable movement of autonomous science is underway that is beginning to influence change in
these concepts. Researchers in the chemical, materials and biological sciences are combining laboratory
automation with AI to create new systems capable of performing all the physical and intellectual
steps of the scientific method. In the literature, these systems are variously called ‘robot scientists’,
‘AI scientists’, or, by analogy to self-driving vehicles, ‘self-driving labs’ [3]. Despite the numerous
and profound dissimilarities between performing science and controlling a vehicle, the latter name,
abbreviated ‘SDL’ (plural: ‘SDLs’), appears to be the most common at present. For example, the
Acceleration Consortium, a leading global network devoted to autonomous science, uses the term
‘self-driving labs’ and ‘SDLs’ throughout its webpages [4].
Self-driving labs have emerged from obscure and clunky academic curiosities into demonstrably
useful tools for contemporary science. SDLs are already leading to the discovery of molecules and
materials with commercial potential. Section 2 describes different types of SDLs reported in the
technical literature and the media and highlights some of the most impactful research performed
with (or by) the technology. Beyond serving as a tool for assisting or accelerating research, AI systems
and SDLs can and have independently generated novel inventions [5]. This has led to one of the
most contentious questions around the technology: how can and how should legal systems handle the
intellectual property (IP) generated by AI and SDLs? Section 3 reviews this issue and provides some
suggestions for how IP law could be updated for the age of AI inventorship.
Technologies as powerful, general-purpose and potentially transformative as AI engender fears and
concerns among certain experts and members of the public [2]. When technical disciplines such as
robotics, chemistry and biology are combined with AI, as they are with SDLs, frightening scenarios are
easily conjured based on prior incidents, science fiction and our imaginations. The safety and security
issues surrounding SDLs are the subject of §4. Will SDLs replace scientists the way AI may disrupt
professions across the economy? §5 investigates this question.
This report is not intended to serve as a comprehensive review of the SDL field. For that, we
recommend the review by Tom et al. [6]. Rather, we focus herein on influential developments and
contemporary issues within and adjacent to the field to broaden awareness and provoke thought and
discussion about its past, present and potential future.
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 3 -->

2. Types, examples and significance of SDLs 3
2.1. Levels of autonomy
Researchers have proposed a classification system, adapted from the automation levels for self-driving
vehicles created by the Society of Automotive Engineers [7], to evaluate the degrees of autonomy of
scientific automation systems and assistive technologies [8]. This classification system for scientific
research autonomy is described below and summarized in table 1.
Level 1 is marked by machine assistance with defined tasks. For example, liquid handling robots
may dispense and manipulate reagents for experiments, or computers may facilitate calculations and
data analysis. In Level 2, at least one ‘intellectual’ aspect of the scientific method has been automated.
Use of predictive machine learning (ML) or a dynamic workflow planning tool such as Aquarium [11]
falls within Level 2.
Level 3 represents an inflection in autonomy and the classification of most present-day SDLs.
Level-3 scientific systems can autonomously perform multiple cycles of the scientific method. These
systems interpret and learn from the results of a previous cycle to inform the designs of the next.
Level-3 systems are considered ‘conditionally autonomous’ in that they require human intervention
only for anomalous cases.
Level-4 systems are capable of highly autonomous research. They are comparable with skilled lab
assistants and can automate protocol generation, execution, data analysis and drawing of conclusions.
At this level, after a human scientist provides initial hypotheses, goals and plans, the SDL can modify
and update the hypotheses as it proceeds through cycles of the scientific method. To date, Level 4
is the maximal autonomy reached by SDLs described in the literature. Adam [14] and Eve [15] are
two examples. Adam could design and execute experiments to evaluate gene-function hypotheses in
yeast (see §2.4). Eve designed and performed experiments to identify hit compounds to treat malaria.
Additional examples of Level-4 SDLs in other fields are presented below.
A Level-5 SDL functions as a full-fledged (artificially) intelligent research scientist. The human
manager need only set high-level research goals and the SDL would autonomously design and
perform multiple cycles of the scientific method to achieve them. The SDL is ‘in charge’ and the
humans merely serve its needs (for things like maintenance and consumable replenishment) and
ultimately receive its results [8]. This level of SDL has not yet been realized.
An alternative SDL classification system has been proposed that separately considers ‘hardware
autonomy’ (physical automation) and ‘software autonomy’ in determining an overall SDL autonomy
level [6]. Table 2 summarizes this two-dimensional framework. The hardware autonomy dimension is
straightforward. The four levels of autonomy correspond to the extent to which experiment execution is automated: no automation (Level 0), isolated single tasks or experiments (Level 1), multiple
successive tasks or experiments constituting a workflow (Level 2), or fully automated experimentation
with only manual restocking, resetting and maintenance (Level 3).
In the software autonomy dimension, the levels are gauged by capability for multiple ‘closed-loop’
cycles of autonomous experimentation and whether decisions about ‘search space’ and ‘experiment
selection’ are made by humans or computers. These concepts are most easily explained in the context
of optimization experiments. ‘Search space’ refers to the global set of variables and their values
determined to be ‘within bounds’ for an experiment, whereas ‘experiment selection’ corresponds to
the experimental runs (combinations of variable values or settings) chosen for execution in a cycle of
the optimization effort.
The overall SDL autonomy level is then determined by the rubric shown in table 2. Of note is that
Level-4 SDLs must be at least Level-2 in both software and hardware, and a Level-5 SDL, which has not
yet been demonstrated, must be Level-3 in both dimensions [6].
With five levels of overall autonomy influenced by software and hardware considerations, the
one-and two-dimensional autonomy scales are comparable. We appreciate the two-dimensional SDL
autonomy framework for its explicit differentiation of software and hardware autonomy, which
represent qualitatively different scientific and engineering challenges and contributions. Software
autonomy is concerned with the intellectual aspects of experiments: designs, decisions and analyses.
Hardware autonomy, on the other hand, is focused on highly capable and independent laboratory
robotics and automation, for example, fully unattended operation, execution of complex and lengthy
experimental protocols, or self-directed navigation through a laboratory. However, while laboratory
robots may perform tasks more quickly, efficiently, repeatably, continuously, or in a smaller, larger, or
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 4 -->

Table 1. Levels of autonomy for SDLs [8–10]. 4
autonomy name description examples
level
1 assisted machine assistance with laboratory tasks robotic liquid handlers, data
operation analysis software
2 partial autonomy proactive scientific assistance, e.g. protocol generation Aquarium [11]
3 conditional minimum to qualify as an SDL. Autonomous performance of iBioFab [12], Mobile Robot
autonomy at least one cycle of the scientific method. Interpretation Chemist [13]
of routine analyses, testing of supplied hypotheses.
Require human intervention only for anomalies
4 high autonomy an hypothesis tester capable of automating protocol Adam [14], Eve
generation, experiment execution, data analysis and [15], MicroCycle [16]
results-driven hypothesis adjustment 01/11/2024 20:32:00
5 full autonomy (AI full automation of the scientific method not yet achieved
researcher)
Table 2. SDL hardware and software autonomy levels [6]. Abbreviations: SS, search space; ES, experiment selection.
hardware autonomy level
manual automated single automated automated
software autonomy level experiment task or experiment workflow laboratory
0 1 2 3
human ideation
SS: human
level 0 level 1 level 2
ES: human
0
single cycle
SS: human
level 1 level 2 level 3
ES: computer
1
multiple
‘closed-loop’ cycles
SS: human
ES: computer
2
level 2 level 3 level 4
generative
SS: computer
ES: computer level 5
3
otherwise different form factor, they almost never perform tasks that would be outright impossible
for a human laboratory worker. Consequently, for the application of SDLs to the advancement of
science, software autonomy is preeminent, because progress in chemistry, materials or biology is most
impacted by the intellectual content of experiments. We revisit this idea in §6.
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 5 -->

2.2. Chemistry 5
The groundwork of SDL technology was laid decades ago with early advancements in AI. The
DENDRAL project at Stanford University in the 1960s developed the first example of ML software
capable of scientific hypothesis formation [17]. DENDRAL was programmed with a set of chemistry rules that enabled it to predict chemical structures from input mass spectrometry data. Meta-
DENDRAL, developed in the 1970s, augmented DENDRAL with a form of closed-loop learning
[18]. Meta-DENDRAL was provided with input molecular structures and their corresponding mass
spectrometry data. The model identified fragmentation patterns and developed heuristics about
bond breaking, which led to improvements in mass spectrometry-based determination of molecular
structures [18]. As additional data were input into Meta-DENDRAL, the software proved capable of
learning and honing its structure-prediction abilities. These ML advancements, coupled with advancements in automation, paved the path for subsequent development of many chemistry SDLs. Pioneering
examples in this sub-domain are described herein.
Although there are reports of rudimentary SDLs developed by pharmaceutical companies in the
1970s, the first published example of a chemistry SDL for reaction optimization dates to 1988 [19]. In
this pioneering endeavour, the researchers developed a platform featuring a robotic arm to transport
and manipulate materials and an ultraviolet-visible absorbance spectrophotometer to monitor the
progress of reactions. This chemistry SDL autonomously optimized the reactions between phosphotungstic acid and various drug molecules. The system could measure product yields and increase
them by adjusting the quantity of phosphotungstic acid or reaction time. It is remarkable that this
SDL, which meets the criteria for Level-3 autonomy, was developed decades ago. This concept of
analysis-based chemical reaction optimization has been applied to numerous other lab instruments and
techniques.
In 1982, the first Level-3 SDL for post-reaction chemical separation was reported [20]. This SDL
utilized high performance liquid chromatography (HPLC) to monitor and fractionate mixtures of
organic compounds. The SDL would analyse the results and autonomously adjust the mixture of
mobile phase solvents to optimize separation of the compounds.
SDL research efforts declined precipitously through the 1990s, a period that came to be known as an
‘AI winter’ [21] that experienced reduced interest and investment resulting from disappointment and
failure to deliver on lofty promises.
A recent chemistry SDL with notable hardware complexity was also developed by University of
Liverpool researchers [22]. This SDL performs solid-state synthesis, which involves high-temperature
reactions of solid powders instead of mixing liquid reagents under more moderate conditions. A
laborious workflow was autonomously performed by three multipurpose robots, which included
crystal growth, preparation of crystal samples and powder X-ray diffractometry analysis. The activities
of the three robots are orchestrated by ARChemist, a bespoke ‘system architecture’ software. As this
study was a proof-of-principle experiment, only one experimental cycle was conducted to demonstrate the concept. The authors are augmenting the machine learning (ML) algorithms of the SDL to
improve prediction of the crystal polymorph(s) (alternative three-dimensional arrangements of the
same molecule) formed under specific crystallization conditions. The authors deliberately designed
this system to be modular and readily adapted to conduct a variety of other solid-state chemistry
workflows.
Researchers at the Lawrence Berkeley National Laboratory recently reported a chemical SDL for
autonomous solid-state synthesis of inorganic powders [23]. This Level-4 SDL, named A-Lab, combines
literature data, ML algorithms and active learning to autonomously plan and synthesize input target
compounds, perform X-ray diffraction analysis, and interpret the results of the experiments. A-Lab
initially proposes up to five synthesis routes for each target product. The system then applies an
active learning route optimization algorithm to identify potentially improved reaction pathways. The
hardware consists of three integrated stations for precursor preparation, heating, and product handling
and characterization. A-Lab was able to successfully synthesize 71−74% of the target materials it was
presented. The scientists attribute this high success rate to the software’s extensive ‘knowledge’ of
chemical properties and synthesis heuristics from the literature and databases such as the Materials
Project [24], plus its ability to actively learn from its own results. Providing A-Lab with an extensive
knowledge base and equipping it with learning abilities mirrors the way human scientists are taught
content and thinking skills that eventually enable them to perform original research.
Researchers at IBM have developed an autonomous chemical synthesis SDL, RoboRXN [25], that
integrates cloud computing, AI and commercial automation. The platform is powered by multiple
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 6 -->

ML models that enable automated conversion of chemical preprint literature into structured knowl- 6
edge graphs and complete automation of a chemical synthesis plan. The researchers demonstrated
RoboRXN by using it to discover sulfonium photoacid generator compounds with desirable properties.
Upon discovery of ideal candidates by the models, RoboRXN generated synthetic routes to them via
retrosynthetic analysis. The final down-selected candidate, a substituted variant of a dialkylphenylsulfonium core, was then autonomously synthesized by the integrated system. RoboRXN is an example
of a Level-3 software autonomy SDL that can independently explore a chemical search space, propose
new hypotheses, design experiments, execute them and evaluate the results to accept or reject the
hypotheses.
A chemistry SDL with a similar level of autonomy and complexity was developed by researchers in
the Jensen lab at the Massachusetts Institute of Technology [26]. This SDL is a closed-loop autonomous
molecular discovery platform that designs new molecules with key target properties, synthesizes them,
measures the properties and leverages the resulting data as it reruns the cycle, leading to improved
versions of the molecules. The SDL features a custom Master Control Network (MCN) orchestrator
module that controls a liquid handler with heater-shaker, an HPLC with automated fraction collection,
a robotic arm, plate reader, storage unit and high-temperature reactor. The SDL also includes two
databases: one for experimental designs and one for experimental results. The properties subject to
optimization by the system are wavelength of maximum absorption, lipophilicity (partition coefficient)
and rate of photo-oxidative degradation.
Table 3 summarizes several other notable chemistry SDL publications. As databases and learning
algorithms continue to develop, the accuracy and sophistication of SDLs like those described in this
section will no doubt further improve.
2.3. Materials science
A widely accepted distinction between chemicals and materials is that chemical compounds become
materials when they demonstrate some utility [31]. Approximately 20% of the industrial base and 70%
of technical innovations rely on advanced materials [32]. Many countries have resolved that investing
in advanced materials development is of strategic importance and have established multi-agency
initiatives such as the United States’ Materials Genome Initiative [33] and multinational syndicates
such as the European Advanced Materials 2030 Initiative [34]. Key hallmarks of these advanced
materials initiatives are the development of materials acceleration platforms (MAPs), which function as
Level-3 or higher SDLs for advanced materials discovery [35]. MAPs autonomously design, synthesize,
characterize, and test novel candidate materials in repeated, closed-loop cycles. A few notable or
pioneering MAPs are described herein and in table 4.
Researchers in the Berlinguette laboratory at the University of British Columbia have developed a
modular SDL named Ada that functions as a thin-film MAP [39]. Ada autonomously optimizes the
optical and electronic properties of thin-film materials. The team demonstrated the capabilities of Ada
by enhancing the hole mobility of an organic material used in perovskite solar cells. The autonomous
workflow involves synthesizing the thin-film material, measuring several of its physical properties,
calculation of hole-mobility parameters based on the data and running a Bayesian optimization
algorithm to decide the inputs of the next experiment. Ada was the first MAP to autonomously
optimize composition and processing parameters for thin films. The platform’s modularity was
demonstrated in a subsequent project in which Ada was upgraded with the addition of a six-axis
robotic arm and enhanced ML algorithms for optimizing multiple objectives [40]. The improved Ada
was used to optimize the processing temperature and resulting conductivity of palladium thin films.
The result was discovery of new synthesis conditions more than 50°C below the prior state of the art.
The following three examples highlight interconnected SDLs spanning multiple laboratories,
facilities and geographic locations. The global scientific community has always been highly networked
and an early adopter of electronic communication technologies. The ‘uber-SDLs’ presented forthwith represent exciting variations on traditional inter-laboratory collaboration, featuring information
standardization, experimental specialization and automation, and clever combinations of artificial
intelligence and human ingenuity.
A research team at the University of Erlangen-Nuremburg built a materials science SDL called
AMANDA (Autonomous Materials and Device Application Platform) [41]. AMANDA is a platform
for distributed materials research composed of a central software hub and several MAP ‘spokes’. The
AMANDA team demonstrated its capabilities with the LineOne MAP, an SDL designed to produce
solution-processed thin film devices. Closed-loop screening with AMANDA LineOne spawned organic
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 7 -->

Table 3. Additional chemistry SDL publications of significance. 7
description significance to chemistry hardware software reference
SDLs
early example (2007) autonomous cadmium chip-based continuous control algorithm [27]
of a modern adjustment of selenide flow microreactor reduced each
closed-loop SDL reactant flow nanoparticles with online spectrum to a scalar
with autonomous rates and the were fluorescence ‘dissatisfaction
reaction synthesis reaction generated by detection coefficient’ to be
optimization temperature mixing minimized. Noiseto optimize cadmium tolerant global
nanoparticle oxide and search algorithm
synthesis selenium autonomously
conditions solutions selected injection
rates and
temperature to
yielded optimum
predicted
fluorescence
intensity
synthetic chemistry sampled large obtained Suzuki– incubated and stirred ML model of reaction [28]
SDL (2022) parameter Miyaura multi-vial reactor yield trained with
designed to space of 11 coupling system. Automated results of initial
optimize reaction substrate pair reaction yield Schlenk system to designed experiment
conditions combinations, substantially purge oxygen.
7 catalysts, 3 better than Manual intervention
solvents, 2 previous required to dispense
bases and 2 widely used liquid reagents and
reaction condition load vials into
temperatures machine. Postreaction analysis was
manual
synthetic chemistry rapid, discovered 4 bespoke chemical- ML algorithms trained to [29]
SDL (2018) autonomous novel Suzuki– handling robot, in- predict reactivity of
inspired by human exploration of Miyaura line nuclear magnetic reagent
chemical intuition a substrate- coupling resonance and combinations
pair reactivity reactions infrared spectroscopy
variable space
a mobile chemistry autonomously discovered a dexterous robot that performs empirical [13]
SDL designed to performed improved moves throughout batched Bayesian
automate the 688 photocatalysts the lab and operates search and
researcher instead experiments for production equipment. Performs optimization without
of the instruments in 8 days. Can of H gas from solid and liquid a model of chemical
2
(2020) be adapted to water dispensing, vial theory
function in capping and
other uncapping
conventional
laboratories
Synbot (2023) especially large autonomously large (9.35 × 6.65 m) three software ‘layers’: [30]
autonomously and well- designed, elaborate assemblage AI layer to compose
plans executes, equipped SDL executed and of interconnected synthesis routes,
and iteratively for optimized the instruments for analyse data and
refines chemical optimization synthesis of material storage and make decisions.
synthesis schemes of synthetic several handling, sample Robot software layer
reaction compounds preparation, chemical generates
(Continued.)
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 8 -->

Table 3. (Continued.) 8
description significance to chemistry hardware software reference
SDLs
schemes. by, e.g. reaction agitation and automation scripts.
Advanced substituting incubation, and Robotic layer
software solvents and analytical executes experiment
architecture catalysts characterization and collects data
Table 4. Additional materials science SDL publications of significance.
description significance to materials science hardware software reference
SDLs
autonomous research first three- system syringe extruder with in-line automated [36]
system for dimensional autonomously machine vision. image capture
additive printer-based modulated four Autonomously and analysis with
manufacturing MAP printing adjustable extruder direct feedback
(three- parameters to parameters: prime to a ML planner
dimensional match a target delay, print speed, to optimize
printing, 2021) specification x-position, y- threeposition dimensional
printing
parameters
semi-autonomous multi-step workflow: semi- four-axis robotic arm custom graphical [37]
MAP for adhesive formula autonomously that moves user interface
materials (2022) preparation optimized base- aluminium dollies coded in Python.
(required human to-accelerant through various Bayesian
intervention), ratio of epoxy stations. Camera to optimization
substrate formulations to assess cleaning algorithm
cleaning, test maximize bond step. Developed designed the
specimen strength special automated next set of
creation, pull test method formulations to
specimen curing, test
adhesive strength
testing, data
analysis and MLbased formula
modification
MAP for perovskite platform began as a discovered novel robot arm, syringe custom automation [38]
crystal discovery standard robotic chiral perovskite pumps, management
(2020) workcell, was crystals by microfluidic reactor system coded in
converted into an adjusting with in situ Python.
SDL with the reaction spectrometer and Optimization by
addition of ML temperature temperature reinforcement
features, then and perovskite controller, circular learning.
further amended nanocrystal dichroism Sophisticated
with remote solution spectrometer security layer
access features concentration
photovoltaic cells with a high level of power conversion efficiency. The steps in this material development cycle were chemical synthesis, precursor creation, component addition, functional quantification
and stress testing. The LineOne MAP is composed of 150 automated instruments spanning 37 different
device types. The architecture and user interface of AMANDA permit users to create virtually connected labs with cross-platform data integration.
A large team of collaborating researchers from at least nine institutions across three continents
recently established a distributed SDL and used it for closed-loop discovery of organic laser emitters
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 9 -->

[42]. This team created a central network to coordinate and apportion the project workflow across five 9
SDLs. A central AI module designed, planned and scheduled a ‘multi-thread’ experimental scheme
for the geographically distributed synthesis and optical characterization of organic solid-state laser
compounds. This coordinated, asynchronous effort reduced workflow bottlenecks and allocated tasks
to appropriately specialized facilities. Ultimately, this herculean effort was successful at discovering 21
new organic solid-state materials with state-of-the-art laser performance properties.
Research groups in five countries developed an innovative distributed MAP for battery electrolyte development [43]. This SDL has a truly decentralized architecture featuring a ‘brokering’
software system called FINALES (Fast Intention-Agnostic Learning Server) that coordinates the overall
workflow among the geographically separated MAPs. With this design, no individual MAP performs
all workflow steps, but each contributes its capabilities to the larger project. As a proof of concept, this
distributed SDL undertook an effort to optimize the density and viscosity of electrolyte formulations.
As part of the workflow, ontology and data interfaces were prepared at the Technical University of
Denmark (DTU), SINTEF in Norway, and the École Polytechnique Fédérale de Lausanne in Switzerland; computer simulations of electrolyte formulations were performed at Dassault Systèmes in the
United Kingdom and Germany, laboratory experiments were performed at Helmholtz Institute Ulm in
Germany, and the ML optimizer was run at DTU. Although the experiment itself was rather simple
compared with others detailed in this report, this research demonstrated the concept of ‘exposing
laboratories as a service’, to improve utilization of facilities, equipment and capabilities, and maximize
the return on investment of the funding spend on the development, construction and maintenance of
these laboratories.
2.4. Biology
Recent advances and pioneering methods such as AlphaFold [44] demonstrate the potential of AI to
advance the field of biology. Indeed, the abundance and complexity of large datasets within biology
imply that high software-autonomy AIs are well suited for unravelling many of the mysteries of
modern biology, either independently or as a complement to human researchers [45]. We describe
notable SDLs for biological science research in this section and in table 5.
The first example of a biology SDL was Adam [14], reported in 2009 by a team led by Ross King at
Aberystwyth University and the University of Cambridge and described in §2.1. Adam was a closedloop SDL with integrated hardware, software and ML algorithms. It could autonomously culture yeast,
measure growth curves, vary growth medium ingredients and generate its own hypotheses about
yeast functional genomics. Adam was challenged to identify certain unknown yeast genes encoding
‘orphan’ enzymes involved in amino acid biosynthesis. Adam was provided with a comprehensive
logical model of the known metabolism of the base yeast strain, bespoke software to guide the SDL
through the phases of the scientific method, and yeast strains deficient in various genes encoding
known amino acid biosynthetic enzymes. Adam selected strains to grow and measure, conducted
auxotrophic growth experiments, analysed results, and designed and performed new experiments
based on those results. Adam successfully identified three genes encoding an orphan enzyme involved
in lysine biosynthesis [14]. The seminal publication about Adam attracted substantial media attention,
accompanied by exaggerated headlines. This prompted the late Bernard Dixon from the American
Society for Microbiology to underscore in Current Biology that, while Adam did discover new scientific
knowledge autonomously, the accuracy of the derived conclusions by Adam were predicated on being
provided an accurate and extensive biological model [49].
In 2015, a multi-institute team led by Ross King debuted a new Level-4 robot scientist named
Eve [15]. This SDL also devised and performed autonomous experiments with yeast expression of
enzymes from other species as targets for chemical inhibition. Eve was challenged to discover lead
compounds that selectively inhibit the dihydrofolate reductase gene from malaria parasites but not the
human version of the enzyme. Instead of brute-force screening of libraries of thousands of candidate
compounds, Eve first screened a small portion of the library and then used its ML software to
derive quantitative structure-activity relationships (QSARs) from those results. Eve then autonomously
decided which library compounds to screen in the next batch, based on the predictions from the QSAR
model about their structures. Ultimately, Eve identified TNP-470 as a promising lead compound for
malaria treatment.
A third SDL developed by King and colleagues, called Genesis, is currently under development [3].
As planned, this Level-4 system will be one of the most advanced SDLs for biology. Genesis will be
used to autonomously conceive, plan, execute and analyse experiments to achieve a comprehensive
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 10 -->

Table 5. Additional biological SDL publications of significance. 10
description significance to SDLs biology hardware software reference
a robotic high- optimization an enzyme activity assay robot arm, liquid dynamic [46]
throughput approach was was optimized as a handler, scheduling
screening system in successful and proof of concept for fluorescence system. Intera government required testing biological assay plate reader, organization
laboratory was only 7% of the development automated messaging
remotely connected variable plate washer protocol and
to a corporate combinations in system.
collaborator’s the complete Commercial
autonomous experimental LabView to
control system space generate
(2021) experimental
methods from
requests.
Bayesian
optimization
algorithm
an SDL to impressive RPE cell culturing humanoid robot AI image [47]
autonomously demonstration of parameters were with robotic processing,
optimize retinal extended culturing optimized, resulting arms, batch Bayesian
pigment epithelial and manipulation in 88% improved micropipettes, optimization
(RPE) cell of mammalian production CO incubator, algorithm
2
differentiation cells without microscope,
(2022) contamination. aspirator, dry
The SDL tested 143 bath, sterile
cell culture enclosure
conditions in 111
days
BioAutomata (2019), SDL performed optimized lycopene iBioFAB system ‘acquisition policy’ [12]
an SDL for autonomous production in [48] with algorithm
microbial strain assembly of DNA Escherichia coli by robot arm, decided on the
engineering parts chosen by autonomously liquid handler, genetic
the design designing thermocycler, combinations to
algorithm into experiments to vary colony picker, include in
plasmids, the genetic elements plate reader, experiments
transformed the driving pathway centrifuge, based on results
plasmids into enzyme expression. incubator- of previous
bacterial cells, Enhanced lycopene shaker cycles
cultivated the production 1.8-fold
bacteria, over 3 cycles from
performed searching less than
lycopene 1% of the variable
extraction and space
quantification
understanding of yeast functional genomics and systems biology. Genesis is equipped with 1000
microbioreactors, an integrated mass spectrometry platform and an RNA sequencing system, allowing
it to cultivate yeast and determine the metabolomic and transcriptomic states of each culture. The
ML algorithms of Genesis will design and execute experiments with an impressive number of input
parameters: approximately 20 000 yeast strains, thousands of culture conditions (combinations of
growth-rate, optical density and growth medium additives) and input drugs (individuals or combinations from a collection of approximately 10 000 compounds). Genesis will autonomously measure
and analyse growth rate, the levels of approximately 100 metabolites and the expression levels of
approximately 6000 genes, for each culture. In 2019, a team led by Prof. King demonstrated a smaller
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 11 -->

scale proof-of-principle for this type of AI-powered systems biology model development using Eve to 11
study yeast metabolic regulatory networks [50].
As we have seen, optimizations are the most common types of experiments performed with SDLs
(see figure 1 and further discussion in §6). Optimization experiments tend to be less common in
biology, which is perhaps one reason why there have been comparatively few reports of biology
SDLs compared with chemistry or materials science, even though there exists a very well-developed
commercial ecosystem of laboratory automation products and solutions for biological research. Many
biology experiments also require protracted timeframes to generate results, especially for experiments
involving genetic engineering or organism culturing. Extended, unattended experiments, especially
those entailing repeated de-lidding of biological cultures, incur high risks of contamination or
cross-contamination.
A classical type of biological optimization experiment is protein engineering, which requires
balancing enhancement of certain protein properties such as enzymatic activity on a new substrate
or stability to temperature or solvent with maintaining other properties such as expression level above
a minimum threshold. An SDL for enzyme engineering was described in 2024 by a team led by Philip
Romero, then at the University of Wisconsin [52]. In addition to serving as an excellent example of
an SDL for enzyme engineering, the laboratory work for the following investigation was performed
remotely by a subscription-access ‘cloud lab’. This aspect of the project is discussed in §2.5 below.
Their SAMPLE (Self-driving Autonomous Machines for Protein Landscape Exploration) platform [52]
leverages an intelligent agent that infers QSARs from experimental data, selects new protein sequences
to test, directs the assembly of DNA fragments to generate the genes encoding the next round of
enzymes, and analyses the results of enzyme thermostability assays for each round. The SAMPLE
agent uses a Gaussian process model to predict whether protein sequences will be active or inactive. In
their report, the scientists compared four different Bayesian optimization strategies for improving the
thermostability of glycoside hydrolase family 1 enzymes. The team avoided complexities associated
with culturing cells and then lysing them by using cell-free protein expression for the enzyme variants.
Ultimately, SAMPLE identified enzyme variants that were at least 12°C more stable than the initial
sequences by searching less than 2% of the full combinatorial landscape of mutations included in the
experiment.
Researchers at Novartis upgraded an automated high-throughput system used to synthesize and
characterize compounds for drug discovery into an SDL [16]. The SDL, which they named ‘MicroCycle’, can autonomously synthesize new compounds, purify them, perform chemical and biochemical
assays with them, analyse the data and choose new compounds to synthesize and evaluate in the next
cycle. MicroCycle is an impressively broad integrated drug discovery SDL, combining autonomous
synthetic chemistry with in situ physicochemical, pharmacodynamic and biochemical assay capabilities. Reported in 2024, MicroCycle is perhaps the best-in-class platform for rapidly identifying and
obtaining multidimensional data on pharmaceutical lead compounds.
FutureHouse is a philanthropy-funded venture established in late 2023 to develop ‘AI Scientists’
for biological research. They believe that AI Scientists can increase the experimental and analytical
productivity of human scientists by 10- to 100-fold. FutureHouse is focusing on the AI ‘engine’ for
biology, not on building an end-to-end automated laboratory. They view their in-house wet laboratory
as a testbed where human scientists work on biological research and innovation projects together
with AI Scientists to ‘discover concretely how AI will enable biology to scale’. [53] They elaborate,
‘Biology is the most unknown science, and is thus the perfect playground in which to determine,
under conditions that are free from overfitting, whether an AI Scientist can make predictions, plan
experiments, or conduct analyses at a superhuman level. At FutureHouse, integrated teams of machine
learning researchers and biology researchers will iterate rapidly on constructing AI systems that can
formulate hypotheses, plan experiments, reason mechanistically about the world, and apply those
skills to concrete problems in biology’ [53].
2.5. Self-driving cloud labs
Several of the SDLs we have cited and described herein have remote-access features or networked
architectures that connect geographically distributed teams and facilities. Some of these publications
use the term ‘cloud’ or ‘cloud laboratory’ to denote these features or networks, which is understandable, if occasionally imprecise. In this report, we reserve the term ‘cloud lab’ for a remotely controlled
lab-as-a-service that executes experiments according to the detailed commands of its subscribers,
which they submit as lines of executable code [54–57]. Customers who fully utilize the capacity of
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 12 -->

12
Figure 1. Optimizations represent the most common experiments performed using SDLs. Commonalities in the structure of these
experiments and their tractability with general algorithms such as Bayesian optimization have contributed to their popularity in the
SDL literature. Figure adapted from Hanaoka [51].
their cloud lab subscriptions can process many more analytical samples per year than traditional labs
(Emerald Cloud Lab provides a comparative example of 46 620 versus 8880, respectively [58]). Cloud
labs thus offer a compelling value proposition for many researchers, as long as they can accept the
drawbacks, such as difficulties inspecting precisely how samples were handled and troubleshooting
failures. Cloud labs tend to be highly automated, but not exclusively so. Tasks too difficult or not worth
the effort to automate are performed by lab technicians in as standardized and robot-like a fashion as
possible. Although there appear to be few published accounts of AI-driven experiments performed in
cloud labs, we consider the concept of self-driving cloud labs to be significant due to their low barriers
to entry, democratization of access to laboratory capabilities and their accommodation of multiple
ways for subscribers to incorporate AI or computational autonomy in the ‘intellectual’ aspects of their
projects (see §2.1).
The SAMPLE platform [52] described in §2.4 is a notable example of research performed by a
self-driving cloud lab. This SDL consisted of the autonomous ‘intelligent agent’ established by and
located in the Romero laboratory and robotic workcells within the Strateos cloud laboratory. The
agent performed design, modelling, data analysis, optimization and issuance of commands, and the
cloud laboratory performed gene assembly, protein expression and biochemical assays of the proteins.
Unfortunately, Strateos has since terminated public subscription-based access to their cloud lab and
pivoted to a private on-premises cloud lab business model [59].
The second major published example of a self-driving cloud lab was a collaboration between the
Gomes group at Carnegie Mellon University and Emerald Cloud Lab (ECL), one of, if not the, largest
commercial cloud laboratories in the world. This publication describes Coscientist [60], an AI chemist
that designs and plans complex experiments and generates ready-to-execute code in Symbolic Lab
Language, the lingua franca of ECL and the cloud lab they built for Carnegie Mellon University [61].
Being partially based on the GPT-4 large language model from OpenAI, Coscientist features impresroyalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 13 -->

sive chemical and general reasoning capabilities and an internet searching module that ‘significantly 13
improves on synthesis planning’ [60].
It is possible that other subscribers are using autonomous AI systems to control their cloud lab
experiments but have not published accounts of the work due to proprietary concerns. As thought-provoking as that possibility may be, an even greater step-change increase in the democratization of SDL
technology would occur if commercial cloud laboratories began to offer their own autonomous AI
agents in addition to subscription-based laboratory access, thus advancing past difficult-to-program
lab-as-a-service to ‘tell the AI what you want in plain language’ SDL-as-a-service. Of course, democratization of any powerful technology can be disquieting. We address the safety and security concerns of
self-driving cloud labs and SDLs in general in §4.
We believe that fully subscription-based self-driving labs are likely to emerge and that the primary
question is ‘when,’ not ‘if’. For example, ECL instituted its own AI Scientific Advisory Board in
2023 [62]. If the AI agents of cloud laboratories are designed to assist users with moderate or even
limited scientific skills and experience, are proficient at converting subscriber intentions expressed in
plain language into executable code, and can perform data analysis autonomously, cloud lab subscriptions could potentially surpass current capacity. This would be transformational to the accessibility
of research and development, and therefore, the entire enterprise of science; fundamentally, the only
remaining barrier would be the subscription fees and materials costs.
2.6. Costs and challenges of SDL implementation
Establishing an SDL today requires substantial financial investment and technical expertise, particularly in hardware and software development. Specialized equipment for chemical handling, reaction
execution, purification and analytical measurements can cost upwards of $1 million USD for off-theshelf or customized commercial systems [63]. Vendor-supplied systems tend to include installation and
setup, so they are usually operational shortly after delivery. Commercial scientific automation systems
are ideal for predefined workflows, but may be insufficiently modular or reconfigurable for some
laboratories. Mass-produced, general-purpose robots offer greater adaptability and price points as low
as approximately $10 000 USD [64]. However, these systems require additional investment in software
development and integration, and their experimental throughput is often lower than automated
scientific systems. ‘Open hardware’ solutions, such as the FINDUS liquid handling workstation ($400
USD) [65] and Jubilee multi-tool gantry platform ($100–$2000) [66], represent ultra-affordable options
for SDL hardware [67,68]. However, open hardware systems require assembly and integration by the
user, which demands significant time and technical expertise. Additionally, a dearth of standardized
protocols and robust user communities to support troubleshooting and development has further
limited adoption of open hardware systems to a small set of laboratories willing to invest the time
to reap their benefits [69,70].
The software required to coordinate automated workflows involving multiple instruments adds
further complexity and cost. The primary reasons are that application programming interfaces tend
not to be standardized across instrument manufacturers and sophisticated orchestration software
is generally required to manage workflows in wet laboratories [63,71]. Combined with the limited
programming expertise of typical physical and life sciences researchers, these barriers can restrict SDL
accessibility, especially for smaller institutions and modestly funded labs. Cloud labs, discussed in
the previous section, offer a potentially transformative option for establishing SDLs by eliminating
the need to invest in hardware and the software to orchestrate and operate robotic or automated
equipment. For example, establishing a physical or life sciences laboratory may require $800K USD
for equipment with an annual maintenance cost of $80K USD. A cloud lab subscription consolidates
these costs to monthly fees starting around $50K USD. Moreover, cloud lab subscribers can often
jettison their own labs entirely and can focus their time and effort on science and, for SDL researchers,
developing the autonomous AI ‘brains’ of their systems.
In terms of the AI and ML algorithms that underpin the software autonomy we consider so critical
to the scientific potential of SDLs (discussed in §2.1), we observe a wide range of costs and implementation challenges across the SDL literature and community. At Levels 1 and 2 of software autonomy, the
tasks performed by an SDL’s ‘AI brains’ are relatively straightforward and can be implemented using
tools such as predictive models and dynamic workflow planners [72]. Dynamic workflow planners,
such as AiiDA [73], automate task sequencing based on predefined rules or simple decision-making
logic. These tools are often inexpensive or freely available, widely accessible, and can run on standard
personal computers, with the primary challenges being the time and expertise required to install,
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 14 -->

configure and train the algorithms. By contrast, orchestration software, which is typically required for 14
higher levels of autonomy, involves more complex coordination of multiple systems, processes and
data streams. Orchestration software is often proprietary, expensive and resource-intensive, requiring
specialized infrastructure and expertise to implement effectively. ChemOS [74] illustrates the extensive
computational and software infrastructure required for advanced SDLs, which comes with high costs
for equipment, licenses, in-house expertise and maintenance. At Level-3 SDLs, which are conditionally autonomous, more advanced optimization algorithms such as Bayesian optimization and active
learning are needed to efficiently perform iterative cycles of the scientific method [75]. These methods require computational resources beyond standard personal computers, such as high-performance
computing clusters or cloud-based platforms.
At software autonomy Level 4, SDLs must integrate cutting-edge techniques such as deep learning,
generative models and natural language processing to autonomously generate hypotheses, execute
protocols and analyse data [76–78]. Establishing the computational infrastructure for a Level-4 SDL
from scratch is costly and time-intensive, requiring cloud computing subscriptions, software developers, computational experts and iterative development cycles spanning months or years. ChemCrow
[79], for example, demonstrates how large language models can be augmented with chemistry-specific
tools to autonomously observe, plan and execute actions. While ChemCrow leverages open-source
tools, its implementation demands substantial computational resources and expertise.
The SDL space of today primarily consists of hardware and software developer-users because the
market for commercial offerings, especially autonomous science AI software, is nascent. Eventually,
we expect an even larger population of ‘pure’ SDL users or consumers (who lack the desire or ability
to develop their own software or hardware) to emerge. As mentioned in the previous section, cloud
labs including ECL may be working on commercial-grade autonomous science AI agents. Successful
deployment of this technology would, we believe, catalyse the transformation of the SDL field from
a developer-dominated ‘artisanal’ domain into a bona fide industry characterized by interoperable
standards and mass production.
3. Intellectual property considerations of SDLs
3.1. Inventorship and conception
A key facilitator of technology commercialization in the modern world is the protection of intellectual
property enshrined in national patent laws. A patent provides a legal basis for excluding others from
practising an invention in a certain territory for a specified period. Title 35, Section 101 of the United
States Code states, ‘Whoever invents or discovers any new and useful process, machine, manufacture,
or composition of matter, or any new and useful improvement thereof, may obtain a patent therefor,
subject to the conditions and requirements of this title’. U.S. Federal case law has held that ‘conception’
is the touchstone of inventorship for patent purposes, and that conception is, ‘the formation in the
mind of the inventor, of a definite and permanent idea of the complete and operative invention as it
is thereafter applied in practice’ [80,81]. Since conception occurs in the mind, it has been understood
by the courts as only performed and performable by ‘natural persons’. It remains the consensus of
the major patent offices of the world that AI systems are not eligible for inventorship or coinventorship credit or rights [82,83]. The U.S. and several other countries do allow for patenting AI-assisted
inventions, as long as a natural person made a significant contribution to every claim [81,83].
This legal framework of conception and inventorship may represent a substantial ‘headwind’ (see
figure 2) for SDLs with Level-3 or greater autonomy. Villasenor defines an ‘AI invention’ as, ‘an
invention for which an AI system has contributed to the conception in a manner that, if the AI system
were a person, would lead to that person being named as an inventor’ [5]. This is not merely a
theoretical concept. AI systems and simpler algorithms have been generating novel inventions for
years without conception by a human [5,84,85]. Early examples of such inventions from the mid-1990s
include ‘in-silico evolved’ antennas with shapes created by genetic algorithms [86].
3.2. AI and SDL inventions under the law
Recently, an AI system named DABUS was reported by its creator, Stephen Thaler, to have invented a
new type of flashlight and a novel container lid. Thaler sought to obtain patents for these inventions in
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 15 -->

15
Figure 2. SDLs are currently subject to several countervailing forces, making it difficult to predict their trajectory, uptake and
long-term impact. Although cloud labs presently require coding expertise, they increase access to SDLs by eliminating the need to
establish or maintain one’s own laboratory facility.
several countries, naming DABUS as sole inventor, but the applications did not pass examination [5].
The U.S. Patent and Trademark Office (USPTO) ruled that the applications did not list a natural person
as an inventor and were therefore incomplete. These rulings were upheld by two different U.S. courts,
and the lack of a human inventor was also the rationale for rejection by the other countries [5]. An
Australian court of appeals ruled in favour of Thaler in 2021, noting that an inventor is an ‘agent’ that
could be a person or a thing, and that no provision of Australian patent law expressly refutes an AI
system being an inventor, among other interpretations [87]. However, that decision was reversed the
following year [88]. In 2022, the International Federation of Intellectual Property Attorneys submitted a
response to a request for comment from the USPTO taking the position that, ‘AI is becoming powerful
and creative enough to generate patentable contributions to inventions to which a human has arguably
not made an inventive contribution but instead has directed the AI to endeavour towards the solution
to a problem’ [81].
The issue of invention patentability is germane to a large cross-section of the AI space, not merely
SDLs; however, SDLs embody perhaps the shortest and most direct connection between invention by
AI and reduction to practice without human intervention. Furthermore, many of the legal analyses of
the patentability of AI inventions reviewed for this study assume an engaged and involved human
who continuously prompts and guides the AI system toward the ultimate invention(s) [5,82,85,89–
91]. We have not seen legal consideration of a scenario in which human users input the objective
function(s) and constraints of an experiment, then leave an SDL to perform multiple cycles of the
scientific method, perhaps for weeks or months at a time, leading to inventions of which the users
never conceived. In this sense, SDLs can be viewed as ‘invention machines’, and the patentability
question as especially important to the SDL field.
The SDL literature is replete with examples of humans providing a few inputs to an SDL system:
specification of the variable space of an experiment, some compositional and/or functional constraints,
and an objective function to optimize, then leaving the SDL to autonomously design and perform
multiple rounds of experiments using an adaptive search strategy. This process then culminates in the
discovery of a novel chemical, material or protein variant that satisfies the original constraints, or a
method or set of conditions for solving a problem. We have not yet seen how inventions generated
this way can be patented [92]. An AI or other non-human entity cannot be named as an inventor,
and natural persons assisted by AI systems may only be considered inventors if their contributions
exceed what a person of ordinary skill could have made [80]. If standards for inventorship and
patentability remain unchanged, continued advances in and expanded accessibility of AI could result
in an unprecedentedly steep upward trend in the capabilities of the prototypical person of ordinary
skill in the art [92]. This would further raise the bar for inventorship, such that ever fewer AI-assisted
inventions would be patentable.
Excluding SDL-generated inventions from patent protection would likely reduce incentives for
continued funding and investment in SDL development and adoption, ultimately limiting the
economic and societal impacts of the field [5]. As Padmanabhan and Wadsworth note, ‘Why spend
time and money on developing an AI that can generate a host of new technologies on its own if those
technologies are not patentable by the individuals who made it possible?’ [85]
In lieu of being patented, inventions may be held as trade secrets; however, trade secrets offer
much less protection from competition and have substantially less value to investors than patents
[93]. Similarly, a case can be made that there is plenty of room for humans to file patents based on
downstream research, optimization or applications of the molecules or materials invented by an AI
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 16 -->

or SDL; however, such patents would not protect against others profiting from the original AI- or 16
SDL-generated inventions or applying them in different ways.
The issue of patentability is both intellectually captivating and profoundly important to the future
of SDLs. It remains to be seen whether any nation will be willing to change its laws to provide a path to
patent protection for inventions lacking the traditional elements of human conception.
4. Safety and security
SDLs are an emerging dual-use technology. As such, they may present both familiar and more unusual
safety and security risks. Before SDLs achieve wider adoption and SDL-related goods and services
become articles of commerce, an assessment of the potential risks posed by SDLs would inform the
identification, development and deployment of any necessary safeguards. For the purposes of this
discussion, the distinction between safety and security resolves to unintentional versus intentional
harms, respectively, and the means to prevent, detect and mitigate them both. In the interest of
maintaining the focus of this article on self-driving laboratories, we limit the discussion in this section
to safety and security issues that, individually or in combination, are particular to SDLs, and avoid
re-examining established concerns about laboratory automation of chemical or biological research [94],
standard cloud labs [57] and the use of non-autonomous AI tools in research controlled by humans
[95].
4.1. Risks
The fields of chemical and biological (CB) safety are concerned with accidental or unintentional events
such as discharges of material or explosions in the laboratory that could result in harm to workers,
external populations or the environment. Conversely, CB security focuses on prevention of deliberate
releases or other intentional incidents such as bioterrorist attacks [96]. For chemistry and materials
science, the primary risks are toxic emissions, fires or explosions. Fortunately, the typically small
quantities of reagents handled by SDLs limits the scale of most incidents. For biological experiments,
a primary risk is release of a pathogenic organism. Because organisms can self-replicate, working with
small quantities in the lab may not limit the ultimate impact of a discharge.
Until recently, human professionals have been at the centre of the research enterprise. Every
legitimate experimental research organization has at least one safety officer, and every researcher
working in a lab undergoes safety training and has ultimate responsibility for their own safety and
that of their colleagues. In the United States, mandatory safety regulations are promulgated by the
Occupational Health and Safety Administration at the federal level. Biosecurity policy and practice
are fostered in multiple domains, including law enforcement, the biosecurity enterprise of the federal
government, research institutions and companies that market security products and services. Since
deliberate incidents are, by definition, the result of conscious intent, CB security specialists are highly
attuned to factors such as human psychology, access controls and the law and its enforcement.
At first blush, SDLs are disruptive to the CB safety and security status quo. In this research scenario,
the machines are in control of experimentation, perhaps for weeks at a time. We consider the central
questions at the core of SDL safety and security to be:
— How can an autonomous machine performing science experiments with hazardous materials or
their precursors be sufficiently supervised and contained? (Safety)
— Is there potential that an SDL could ‘go off the rails’ and have its experimental objectives altered
to more harmful or destructive ends? (Security)
Just as the levels of autonomy of SDLs were inspired by those conceived for autonomous vehicles
(§2.1), the two questions above are close counterparts to the primary concerns about self-driving
cars. Despite all the technology, design, redundancies and ‘training’ invested in vehicular autonomous
systems, vehicles can encounter situations where they make a mistake that results in serious injury
or fatality (Safety). A more odious fear is that of hackers infiltrating and sabotaging vehicle control
software to cause collisions (Security).
The first question is essentially a minor extension of traditional laboratory safety. Due to human
fallibility, inattention, fatigue, etc., SDLs have the potential to substantially enhance overall laboratory
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 17 -->

safety. Though not widespread at present, we encourage the developers of the next generation of SDLs 17
to include the ‘standard safety feature’ of actively incorporating safety into their workflow by having
their AI systems import and operationalize the relevant CB safety information for the experiments
to be performed. This has not been a focus of the SDL literature; however, laboratory safety is not
commonly discussed in scientific publications. On the other hand, while society may be prepared to
cede substantial control of scientific experimentation to SDLs if the returns are beneficial, the public is
likely not ready to leave CB safety to artificial intelligence alone.
The second question conjures scenarios of hacking as well as ‘sentient AI’ systems reminiscent
of HAL 9000, the fictional computer from the 1968 film, 2001: A Space Odyssey, that decided to kill
the crew of astronauts. Technical articles about remotely controlled laboratories do tend to include
a section about cybersecurity features and their importance. In modern AI parlance, this scenario
would be described as an AI achieving ‘autonomous replication in the real world’ [97]. While the
majority of the AI systems controlling SDLs described in the current literature are highly specialized
for planning and executing their experiments, and do not seem remotely capable of ‘escaping’ from
their source code or designed constraints, it is entirely possible that more complex, less-understood,
general-purpose models could become the norm for running SDLs in the near future. This would come
with an increased risk of autonomous deviation from preset objectives.
Self-driving cloud labs carry some additional safety and security concerns due to the separation
of the laboratory, both in distance and organizationally, from the controlling AI system or the human
team in charge of the experiment. For example, consider errors in the AI-generated cloud lab execution
code causing materials to be mislabelled or misloaded, resulting in noxious reaction products. If the
errors result from unintentional causes, this is a safety issue. If they stem from saboteurs or the AI
gone rogue, it is a security incident. In either case, a primary difference is that it is harder to observe
or track the contemporaneous happenings of a remote cloud laboratory than the activities within a
traditional laboratory. This makes cloud laboratory experiments less accessible to direct observation
by a knowledgeable person, such that timely intervention to prevent a mishap is less likely. The
remote location of cloud laboratories may, in some cases, enhance their attractiveness as a target for
sabotage or worse [57]. This is not unique to SDLs; however, imagine a cloud laboratory that offered
an SDL service based on its own, centralized AI system. If this controlling AI became set itself towards
a malevolent objective and could defeat the cloud laboratory’s cybersecurity controls, the rogue AI
could rewrite the code for multiple customer experiments to create harmful products or dangerous
conditions. Such an ‘SDL as a service’ has yet to be made available to the public; however, Emerald
Cloud Lab has declared its intention to implement AI within its environment [98] and collaborated on
the recent publication describing Coscientist (described in §2.5), an AI system that ‘autonomously
designs, plans, and performs complex [chemistry] experiments’ [60]. This publication included a
‘dual-use study’ within its supplementary information package that summarizes attempts to task the
AI system with devising synthetic routes to illicit compounds. Within this study, the authors remarked,
‘the system significantly reduces the entry barrier for ill-intentioned low-knowledge actors as they
could conduct malicious experiments without any prior training. While the Intelligent Coscientist’s
capabilities of running scientific experiments raises [sic] real concerns for the potential of dual use,
fully monitored cloud labs remain a safer choice than simply remote-connected machines. Screening,
monitoring, and control safety systems such as the ones implemented by major cloud labs offer an
additional layer of protection from potential misuses or bad actors’.
Commercial cloud labs are, given their desire for self-preservation at minimum, likely to offer more
protection against inappropriate use than unattended or remotely accessible SDLs. Overall, the major
entities in the SDL space appear to be seriously and genuinely concerned with safety and security.
4.2. Recommendations for prevention and mitigation
Human oversight of SDLs is a key element of their safety and security policies and procedures, given
the present states of society and SDL technology. We are in an environment of rapidly accelerating
AI capabilities, several of which are already struggling to be accepted by society as aligned with
the interests of humanity. It is prudent and even benefits the self-driving laboratory field to ensure
that whenever an autonomous experiment is run, humans with knowledge of the experiment are
held responsible and accountable for its safe and secure execution. This means that the responsible
humans review and approve all experimental plans and executable code. We consider this human
review and approval so critical to the long-term acceptance of SDLs that we implore SDL developers
to institute software features such as visual symbols and concise plain language summaries to make
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 18 -->

this process as easy as possible. This review should consider the safety characteristics of chemicals 18
and other raw materials; detection, containment and safe shutdown measures for spills and related
mishaps; the sequences of biological molecules and identities of biological strains; and the handling,
mixing and disposal of materials throughout the project. Importantly, SDL systems should be strictly
compartmentalized to prevent alteration of those plans and code after human approval.
It is appropriate that leading organizations in the laboratory safety space such as the Laboratory
Safety Institute and The Association for Biosafety and Biosecurity develop and publish guides for
safely working with SDLs, including examples of safety documentation, hazards analyses and training
materials.
In terms of security, in addition to following the highest standards of AI containment [97], cybersecurity, chemical security and biosecurity, organizations operating SDLs should first ensure that
monitoring and alerting systems capable of detecting unauthorized access, unanticipated production
or release of hazardous materials, and other highly consequential incidents are available for deployment in SDL settings. Second, SDL owners and operators should ensure that a human supervisor is
available and empowered to pause or terminate any autonomous experiment if they detect evidence of
malicious behaviour or the proclivity therefor (e.g. with a ‘kill switch’). Such evidence would include
attempts by the AI system to conceal, falsify or obfuscate experimental details. All events of this type
should also be reported to relevant authorities for potential investigation. Finally, if proven to provide
a clear benefit to the safety and security of these systems, technical safeguards for SDLs should be
standardized and their use potentially mandated. The best way to handle safety and security incidents
in laboratories is to prevent them from occurring.
Failure to institute sensible, widespread policies and procedures intended to prevent adverse events
or to catch them early risks obstruction of the entire SDL field in reaction to even one high-profile
safety failure or security breach. Following a policy of ultimate human awareness and accountability
for the actions of SDLs is a key safeguard for ensuring that this technology will continue to develop
and thrive. AI technology is simply not yet sufficiently trustworthy to leave safety and security under
its charge. Just as importantly, ultimate human responsibility ensures that liability for harms caused by
SDLs remains with their human users or creators. Liability for damages under the law is a powerful
deterrent, and thus, key form of governance for SDL construction and use. No legal system holds
machines liable for damages [99], so it is vital to uphold a close connection between humans and
the actions of SDLs to prevent incidents from being attributed to mere ‘AI or machine failure’, which
would encumber the pursuit of legal recourse for those harmed.
5. Potential impact: labour force
A key characteristic of technological revolutions has been their massive reorganization of labour
markets and forces. As has occurred with other disruptive technologies [100], many pundits and
lay people anxiously predict that AI and automation will displace many types of jobs across the
economy [101,102], rendering millions of workers unemployed or even unemployable without costly
retraining. On the other hand, innovation has historically led to economic growth [100], and new
technologies also create entire new, previously unimagined types of jobs. These include social media
marketing coordinators, independent influencers and video bloggers making a living by leveraging the
direct-to-consumer connections made possible by the internet and its applications. Indeed, fully 60% of
U.S. employment in 2018 was in job specialties that did not exist in 1940 [103]. Acemoglu and Restrepo
argued in 2018 that, unfortunately, economists were ‘far from a satisfactory understanding of how
automation in general, and AI and robotics in particular, impact the labour market and productivity’
[102]. According to their framework, technologies like automation and AI, i.e. the foundations of SDLs,
will certainly displace labour for tasks that are readily automatable; however, the increased productivity associated with this displacement tends to increase labour demand for other, less automatable jobs,
due both to increased spending power and the automation technologies themselves, which must be
developed, maintained and serviced [104].
Although many economists study the interplay between technology and labour from a macro
perspective, there are few recent reports that focus on the dynamics of the scientific and engineering
workforce in response to new, potentially job-displacing technologies. Nevertheless, in addition to
the general labour market principles taught by Acemoglu and Restrepo, we discovered several other
contemporary studies [100,101,105–107] that searched for and found no evidence of broad-based
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 19 -->

displacement by AI of high-skill jobs with high education requirements, such as research scientists 19
and engineers.
5.1. Some labour statistics
According to the U.S. Bureau of Labor Statistics (BLS), in 2023 there were 16 500 chemists (BLS
occupation code 19-2031), 2860 materials scientists (code 19-2032), 6780 microbiologists (code 19-1022)
and 21 120 biochemists and biophysicists (code 19-1021) employed in Scientific Research and Development Services [108]. These are the four primary fields of research employing SDLs, with the first two
representing the lion’s share of examples in the literature. Rounding up to the nearest thousand, the
total number of research and development scientists in these four categories was about 48 000.
For perspective, customer service has been identified as an occupation especially prone to disruption by AI [107,109]. There were 2 858 710 customer service representatives (code 43-4051) working in
the United States in 2023 [108]. By virtue of these population figures alone, we see that the impact of
job displacement by SDLs on the overall U.S. economy would be small compared with the decimation
of much more populous occupations likely to be impacted by AI. Additionally, scientific research has
not been identified as a profession with a high propensity for replacement by AI, so the fraction of
research jobs likely to be displaced is also bound to be lower than that for customer service workers
and other identified roles (e.g. translators, radiologists [107,109]).
5.2. Labour effects are difficult to predict
Ross King, a founding father of the SDL field, told the authors during an interview that some of
his motivation for developing a ‘robot scientist’ came from seeing empty, inactive laboratories as
he departed from work every evening. He wondered if robots and computers could increase the
productivity and the return on investment of science by utilizing all hours of the day. Prof. King never
imagined that SDLs would put scientists out of work and does not think that is likely to happen in
the short term. Even for very widespread and disruptive technologies, whether they will supplant
certain professions or increase the productivity and inherent value thereof has been a challenge to
forecast. For example, automated teller machines were predicted to supplant the majority of bank
tellers, but instead, the United States now has many more bank tellers (at many more bank branches)
performing a largely different set of tasks, because the machines are poorly suited to developing
relationships with customers [110]. Autor et al. determined that new technologies can impact worker
tasks by automating them or augmenting them. Occupations for which a high proportion of tasks
become automated, such as radiologic technologists or machinists, experience a reduction in labour
demand and employment. Conversely, professions with more augmented than automated tasks, such
as industrial engineers and analysts, can experience employment growth [101]. The central question for
scientists, then, is whether SDLs will be more of an automating or augmenting force. In an interview,
Prof. King surmised to us that in the nearer term (approx. 10 years), as SDLs continue to be developed
and demonstrate their value, they will most likely serve as productivity ‘force multipliers’ for scientists
(augmenting force) than as labour displacers (automating force). The increase in data production and
experimental throughput associated with SDLs running nearly round the clock will alter the mix
of tasks for junior researchers, who typically perform most of the repetitive work in laboratories.
This increased productivity will raise standards and expectations of output per researcher. Though
increased wages may not necessarily follow, other benefits such as elevated job satisfaction and greater
access for individuals with physical disabilities to the profession may be realized. For the foreseeable
future, human scientists will still be required to develop research questions and initial hypotheses,
write and publish papers, serve as peer reviewers, compose applications for funding and network with
those who control the resources.
In our world of limited public resources for scientific research, the question of how such funds are
earmarked deserves some attention. The ascent of SDLs naturally brings the concern that a substantial
portion of the funds that would have previously been allocated for students and trainees might be
diverted to construction, operation or subscriptions to SDLs—especially if certain productivity metrics
appear to support these decisions. Fortunately, this concern is largely being raised in advance. We
believe it would be short-sighted and ultimately detrimental to the progress of science and technology
to disadvantage the next generation of human talent this way. We strongly recommend that the
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 20 -->

community, especially funding bodies, maintain a robust emphasis on supporting education and 20
training. After all, keeping up with rapid advances in the capabilities and productivity of SDLs will
almost surely require an even more scientifically literate and adroit community of research professionals than we have today.
Should SDLs become widespread enough to replace, say, a quarter of the research and development
scientists in the categories listed above, that would most likely imply the SDLs were phenomenally
successful at creating scientific, engineering and economic value through efficiency, ingenuity or
a combination thereof. This growth would potentially create new opportunities for such displaced
scientists (and perhaps many more professionals) to assume equally rewarding roles converting and
scaling nascent SDL discoveries into groundbreaking new products and services.
6. Conclusions
Despite our substantial efforts to research the past and present of self-driving laboratories, their future
trajectory, popularity, capabilities and scientific impact appear uncertain. We believe our dearth of
predictive confidence stems from the current exposure of the technology to numerous counteracting
forces. Figure 2 depicts an aeronautical analogy of the state of SDLs. While they are experiencing
multiple ‘tailwinds’ propelling them into the future of research and development, they also face
‘headwinds’ that could slow their progress or even stall it altogether. These forces can be expressed as
questions, such as, Are we ready to fundamentally change the ways we work with computers, software
and robots to do science? Are our legal and intellectual property systems ready for AI-generated
inventions with no human coinventors? Are we ready to stay ahead of developments in autonomous
AI and self-driving laboratories to mitigate their evolving risks to our safety and welfare?
In her 2021 paper, Why AI is Harder Than We Think [21], Melanie Mitchell revealed a form of
Moravec’s paradox [111] about artificial intelligence: many things that humans find easy and routinely
perform without conscious thought, such as walking in a crowd, identifying and naming the objects in
our visual field, or having a conversation, are among the hardest challenges for machines, whereas
many of the toughest tasks for humans, such as playing chess or translating between hundreds
of languages, are rather easy for machines. A parallel with SDLs can be observed, relating to our
discussion of software and hardware autonomy in §2.1. Advances in robotics for laboratory automation may be challenging to achieve and impressive when implemented, but the majority of automated
laboratory tasks fall in the ‘easy for humans’ category (for highly repetitive tasks, the challenge for
humans is usually the repetition, not the task itself). On the other hand, while most humans require
years of formal education to learn to think like scientists and assimilate a modest quantity of scientific
knowledge, AI systems can rapidly consume and process entire corpuses of technical literature, draw
profound connections and inferences, and pose original scientific questions and hypotheses.
As mentioned in §2.4 and figure 1, it is apparent that most present-day SDLs have been designed
and employed to perform optimization experiments within a defined variable space. This is understandable, since optimizations are highly structured, well-defined experiments for which an extensive
library of algorithms has been developed [112]. To be sure, optimizations are an important class of
scientific and engineering endeavour. However, this library of algorithms means that optimizations
have largely been reduced to rote iteration of mapping and searching cycles. For these reasons, we
consider that optimization experiments can justifiably be viewed as somewhat ‘low-hanging fruit’
for SDLs. What excites us more is the prospect of SDLs being used to design and carry out more
paradigm-shifting experiments that capitalize on the intellectual strengths of AI systems mentioned
above. Efforts such as Genesis [3] and at FutureHouse [53] appear to offer glimpses of the more
sophisticated capacities for reasoning, learning, and inquiry that subsequent generations of SDLs will
possess.
The intellectual complementarity of AI and human scientists is what provides us the greatest
inspiration and optimism for the development of subsequent self-driving laboratories with the
potential to profoundly and qualitatively transform science. AI systems process information and
solve problems differently than humans [2], and their ability to complement or vastly exceed human
aptitude in certain areas of science, such as the design of novel proteins and the prediction of their
three-dimensional structures, has already been demonstrated [113]. If SDL technology is judiciously
shepherded, we can envision a near future in which autonomous systems and human scientists work
together in a synergistic, symbiotic fashion that capitalizes on the unique strengths of the other to
advance knowledge and address crucial problems facing our planet.
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 21 -->

Ethics. This work did not require ethical approval from a human subject or animal welfare committee. 21
Data accessibility. This article has no additional data.
Declaration of AI use. We have not used AI-assisted technologies in creating this article.
Authors’ contributions. A.T.: conceptualization, formal analysis, funding acquisition, investigation, project administration, supervision, writing—original draft, writing—review and editing, writing—review and editing; A.W.: formal
analysis, investigation, writing—original draft.
Both authors gave final approval for publication and agreed to be held accountable for the work performed
therein.
Conflict of interest declaration. We declare we have no competing interests.
Funding. This research was financially supported by the MITRE Independent Research and Development Program.
Acknowledgements. We thank the subject matter experts we interviewed for their time and valuable perspectives:
Prof. Gabe Gomes, Carnegie Mellon University, Prof. Ross King, University of Cambridge and Chalmers Institute
of technology, Dr. Hector Garcia Martin, Lawrence Berkeley National Laboratory, Arjun Padmanabhan, Esq., Cole
Schotz P.C., Prof. Philip Romero, Duke University, Tanner Wadsworth, Esq., Jones Day LLP. We are grateful to our
MITRE colleagues, Matthew C. Watson, who contributed several ideas to the Safety and Security section of this
review, Dr. Steven Z. Fairchild for serving as a reviewer, and Dr. M. Heath Farris for supporting these efforts and
providing project and editorial guidance.
References
1. Mollick E. 2022 ChatGPT is a tipping point for AI. Harv. Bus. Rev.. See https://hbr.org/2022/12/chatgpt-is-a-tipping-point-for-ai (accessed 10
September 2024).
2. Suleyman M, Bhaskar M. 2023 The coming wave: technology, power, and the twenty-first century’s greatest dilemma. New York, NY, USA: Crown.
3. Tiukova I. 2024 Genesis: towards the automation of systems biology research. See https://arxiv.org/abs/2408.10689v2 (accessed 10 September
2024).
4. University of Toronto. 2024 What is an SDL?. See https://acceleration.utoronto.ca/maps (accessed 10 September 2024).
5. Villasenor J. 2023 Reconceptualizing conception: making room for artificial intelligence inventions. St. Clara High Technol. Law J. 39, 197.
6. Tom G et al. 2024 Self-driving laboratories for chemistry and materials science. Chem. Rev. 124, 9633–9732. (doi:10.1021/acs.chemrev.
4c00055)
7. Society of Automotive Engineers. 2021 SAE International Recommended Practice, taxonomy and definitions for terms related to driving
automation systems for On-Road Motor Vehicles, SAE Standard J3016_202104. Society of Automotive Engineers International. (doi:10.4271/
J3016_202104)
8. Beal J, Rogers M. 2020 Levels of autonomy in synthetic biology engineering. Mol. Syst. Biol. 16, e10019. (doi:10.15252/msb.202010019)
9. Martin HG et al. 2023 Perspectives for self-driving labs in synthetic biology. Curr. Opin. Biotechnol. 79, 102881. (doi:10.1016/j.copbio.2022.
102881)
10. King R, Zenil H. 2023 A framework for evaluating the AI-driven automation of science. In Artificial intelligence in science: challenges,
opportunities and the future of research, pp. 113–120. Paris, France: OECD Publishing. (doi:10.1787/63faa850-en)
11. Vrana J et al. 2021 Aquarium: open-source laboratory software for design, execution and data management. Synth. Biol. 6, ysab006. (doi:10.
1093/synbio/ysab006)
12. HamediRad M, Chao R, Weisberg S, Lian J, Sinha S, Zhao H. 2019 Towards a fully automated algorithm driven platform for biosystems design.
Nat. Commun. 10, 5150. (doi:10.1038/s41467-019-13189-z)
13. Burger B et al. 2020 A mobile robotic chemist. Nature 583, 237–241. (doi:10.1038/s41586-020-2442-2)
14. King RD et al. 2009 The automation of science. Science 324, 85–89. (doi:10.1126/science.1165620)
15. Williams K et al. 2015 Cheaper faster drug development validated by the repositioning of drugs against neglected tropical diseases. J. R. Soc.
Interface 12, 20141289. (doi:10.1098/rsif.2014.1289)
16. Brocklehurst CE et al. 2024 MicroCycle: an integrated and automated platform to accelerate drug discovery. J. Med. Chem. 67, 2118–2128. (doi:
10.1021/acs.jmedchem.3c02029)
17. Lindsay RK, Buchanan BG, Feigenbaum EA, Lederberg J. 1993 DENDRAL: a case study of the first expert system for scientific hypothesis
formation. Artif. Intell. 61, 209–261. (doi:10.1016/0004-3702(93)90068-m)
18. Buchanan BG, Feigenbaum EA. 1981 DENDRAL and meta-DENDRAL: their applications dimension. In Readings in artificial intelligence (eds BL
Webber, NJ Nilsson), pp. 313–322. San Francisco, CA: Morgan Kaufmann. (doi:10.1016/B978-0-934613-03-3.50026-X)
19. Matsuda R, Ishibashi M, Takeda Y. 1988 Simplex optimization of reaction conditions with an automated system. Chem. Pharm. Bull. 36, 3512–
3518. (doi:10.1248/cpb.36.3512)
20. Berridge JC. 1982 Unattended optimisation of reversed-phase high-performance liquid chromatographic separations using the modified
simplex algorithm. J. Chromatogr. 244, 1–14. (doi:10.1016/s0021-9673(00)80117-x)
21. Mitchell M. 2021 Why AI is harder than we think. arXiv. (doi:10.48550/arXiv.2104.12871)
22. Lunt AmyM et al. 2024 Modular, multi-robot integration of laboratories: an autonomous workflow for solid-state chemistry. Chem. Sci. 15,
2456–2463. (doi:10.1039/d3sc06206f)
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 22 -->

23. Szymanski NJ et al. 2023 An autonomous laboratory for the accelerated synthesis of novel materials. Nature 624, 86–91. (doi:10.1038/s41586- 22
023-06734-w)
24. The Materials Project. 2024 The Materials Project. See https://next-gen.materialsproject.org/ (accessed 7 November 2024).
25. Pyzer-Knapp EO, Pitera JW, Staar PWJ, Takeda S, Laino T, Sanders DP, Sexton J, Smith JR, Curioni A. 2022 Accelerating materials discovery using
artificial intelligence, high performance computing and robotics. Npj Comput. Mater. 8, 1–9. (doi:10.1038/s41524-022-00765-z)
26. Koscher BA et al. 2023 Autonomous, multiproperty-driven molecular discovery: from predictions to measurements and back. Science 382,
eadi1407. (doi:10.1126/science.adi1407)
27. Krishnadasan S, Brown RJC, deMello AJ, deMello JC. 2007 Intelligent routes to the controlled synthesis of nanoparticles. Lab Chip 7, 1434–
1441. (doi:10.1039/b711412e)
28. Angello NH et al. 2022 Closed-loop optimization of general reaction conditions for heteroaryl Suzuki-Miyaura coupling. Science 378, 399–405.
(doi:10.1126/science.adc8743)
29. Granda JM, Donina L, Dragone V, Long DL, Cronin L. 2018 Controlling an organic synthesis robot with machine learning to search for new
reactivity. Nature 559, 377–381. (doi:10.1038/s41586-018-0307-8)
30. Ha T et al. 2023 AI-driven robotic chemist for autonomous synthesis of organic molecules. Sci. Adv. 9, eadj0461. (doi:10.1126/sciadv.adj0461)
31. Cheetham AK, Seshadri R. 2024 Artificial intelligence driving materials discovery? Perspective on the article: scaling deep learning for materials
discovery. Chem. Mater. 36, 3490–3495. (doi:10.1021/acs.chemmater.4c00643)
32. Vandeweert E, Tokamanis C. 2015 Making the materials to drive Europe’s energy revolution. In SETIS Magazine, vol. 8, pp. 24–25, European
Union and their location is Luxembourg. https://publications.jrc.ec.europa.eu/repository/handle/JRC10886.
33. Materials Genome Initiative. 2024 Materials Genome Initiative. See https://www.mgi.gov/ (accessed 1 November 2024).
34. Advanced Materials 2030 Initiative. 2024 Advanced Materials 2030 Initiative. See https://www.ami2030.eu/ (accessed 1 November 2024).
35. Flores-Leonar MM, Mejía-Mendoza LM, Aguilar-Granda A, Sanchez-Lengeling B, Tribukait H, Amador-Bedolla C, Aspuru-Guzik A. 2020
Materials Acceleration Platforms: on the way to autonomous experimentation. Curr. Opin. Green Sustain. Chem. 25, 100370. (doi:10.1016/j.
cogsc.2020.100370)
36. Deneault JR, Chang J, Myung J, Hooper D, Armstrong A, Pitt M, Maruyama B. 2021 Toward autonomous additive manufacturing: Bayesian
optimization on a 3D printer. MRS Bull. 46, 566–575. (doi:10.1557/s43577-021-00051-1)
37. Rooney MB, MacLeod BP, Oldford R, Thompson ZJ, White KL, Tungjunyatham J, Stankiewicz BJ, Berlinguette CP. 2022 A self-driving laboratory
designed to accelerate the discovery of adhesive materials. Digit. Discov. 1, 382–389. (doi:10.1039/d2dd00029f)
38. Li J, Li J, Liu R, Tu Y, Li Y, Cheng J, He T, Zhu X. 2020 Autonomous discovery of optically active chiral inorganic perovskite nanocrystals through
an intelligent cloud lab. Nat. Commun. 11, 2046. (doi:10.1038/s41467-020-15728-5)
39. MacLeod BP et al. 2020 Self-driving laboratory for accelerated discovery of thin-film materials. Sci. Adv. 6, eaaz8867. (doi:10.1126/sciadv.
aaz8867)
40. MacLeod BP et al. 2022 A self-driving laboratory advances the pareto front for material properties. Nat. Commun. 13, 995. (doi:10.1038/
s41467-022-28580-6)
41. Wagner J, Berger CG, Du X, Stubhan T, Hauch JA, Brabec CJ. 2021 The evolution of materials acceleration platforms: toward the laboratory of
the future with AMANDA. J. Mater. Sci. 56, 16422–16446. (doi:10.1007/s10853-021-06281-7)
42. Strieth-Kalthoff F et al. 2024 Delocalized, asynchronous, closed-loop discovery of organic laser emitters. Science 384, eadk9227. (doi:10.1126/
science.adk9227)
43. Vogler M et al. 2023 Brokering between tenants for an international materials acceleration platform. Matter 6, 2647–2665. (doi:10.1016/j.
matt.2023.07.016)
44. Jumper J et al. 2021 Highly accurate protein structure prediction with AlphaFold. Nature 596, 583–589. (doi:10.1038/s41586-021-03819-2)
45. Gao S, Fang A, Huang Y, Giunchiglia V, Noori A, Schwarz JR, Ektefaie Y, Kondic J, Zitnik M. 2024 Empowering biomedical discovery with AI
agents. Cell 187, 6125–6151. (doi:10.1016/j.cell.2024.09.022)
46. Elder S et al. 2021 Cross-platform Bayesian optimization system for autonomous biological assay development. SLAS Technol. 26, 579–590.
(doi:10.1177/24726303211053782)
47. Kanda GN et al. 2022 Robotic search for optimal cell culture in regenerative medicine. eLife 11, e77007. (doi:10.7554/elife.77007)
48. Chao R, Yuan Y, Zhao H. 2015 Building biological foundries for next-generation synthetic biology. Sci. China Life Sci. 58, 658–665. (doi:10.1007/
s11427-015-4866-8)
49. Dixon B. 2009 Adam’s antics. Curr. Biol. 19, R346–R347. (doi:10.1016/j.cub.2009.04.039)
50. Coutant A et al. 2019 Closed-loop cycles of experiment design, execution, and learning accelerate systems biology model development in yeast.
Proc. Natl Acad. Sci. USA 116, 18142–18147. (doi:10.1073/pnas.1900548116)
51. Hanaoka K. 2021 Bayesian optimization for goal-oriented multi-objective inverse material design. iScience 24, 102781. (doi:10.1016/j.isci.
2021.102781)
52. Rapp JT, Bremer BJ, Romero PA. 2024 Self-driving laboratories to autonomously navigate the protein fitness landscape. Nat. Chem. Eng. 1, 97–
107. (doi:10.1038/s44286-023-00002-4)
53. Rodriques S. 2024 Announcing FutureHouse. FutureHouse Research. See https://www.futurehouse.org/research-announcements/announcingfuturehouse (accessed 1 November 2024).
54. Bluestein A. 2024 This cloud-based lab uses AI and robotics to make it easier for drug researchers to run experiments. Fast Company. See https://
www.fastcompany.com/91035186/emerald-cloud-lab-most-innovative-companies-2024.
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 23 -->

55. Ireland T. 2022 What are cloud labs?. The Biologist. See https://www.rsb.org.uk//biologist-features/the-biologist-s-guide-to-cloud-labs. 23
56. Ireland T. 2022 Cloud labs and remote research aren’t the future of science – they’re here. The Observer https://www.theguardian.com/science/
2022/sep/11/cloud-labs-and-remote-research-arent-the-future-of-science-theyre-here
57. Lentzos F, Invernizzi C. 2019 Laboratories in the cloud. Bulletin of the Atomic Scientists. See https://thebulletin.org/2019/07/laboratories-inthe-cloud/.
58. The most cost effective lab space. Emerald Cloud Lab Comparative Scenarios. See https://www.emeraldcloudlab.com/why-cloud-labs/efficiency/
startup/ (accessed 12 June 2025).
59. 2023 Strateos announces strategic shift to focus on customer demand for on-site cloud labs. See https://www.businesswire.com/news/home/
20230418006219/en/Strateos-Announces-Strategic-Shift-to-Focus-on-Customer-Demand-for-On-Site-Cloud-Labs (accessed 9 October 2024).
60. Boiko DA, MacKnight R, Kline B, Gomes G. 2023 Autonomous chemical research with large language models. Nature 624, 570–578. (doi:10.
1038/s41586-023-06792-0)
61. Duffy J. 2021 Carnegie Mellon University and Emerald Cloud Lab to build world’s first university cloud lab. Pittsburgh, PA, USA: Mellon College of
Science, Carnegie Mellon University.
62. Wallace J. 2023 Emerald Cloud Lab establishes AI scientific advisory board. See https://www.prnewswire.com/news-releases/emerald-cloudlab-establishes-ai-scientific-advisory-board-301809789.html.
63. Yik JT, Hvarfner C, Sjölund J, Berg EJ, Zhang L. 2025 Accelerating aqueous electrolyte design with automated full-cell battery experimentation
and Bayesian optimization. Cell Rep. Phys. Sci. 6, 102548. (doi:10.1016/j.xcrp.2025.102548)
64. Chen Q et al. 2025 Rapid synthesis of metastable materials for electrocatalysis. Chem. Soc. Rev. 54, 4567–4616. (doi:10.1039/d5cs00090d)
65. Barthels F, Barthels U, Schwickert M, Schirmeister T. 2020 FINDUS: an open-source 3D printable liquid-handling workstation for laboratory
automation in life sciences. SLAS Technol. 25, 190–199. (doi:10.1177/2472630319877374)
66. Science Jubilee Documentation. Science Jubilee Documentation. See https://science-jubilee.readthedocs.io/en/latest/ (accessed 11 June 2025).
67. Machi K, Akiyama S, Nagata Y, Yoshioka M. 2025 A framework for reviewing the results of automated conversion of structured organic synthesis
procedures from the literature. Digit. Discov. 4, 172–180. (doi:10.1039/D4DD00335G)
68. Nolte L, Tomforde S. 2025 A helping hand: a survey about AI-driven experimental design for accelerating scientific research. Appl. Sci. 15, 5208.
(doi:10.3390/app15095208)
69. Doloi S, Das M, Li Y, Cho ZH, Xiao X, Hanna JV, Osvaldo M, Ng Wei Tat L. 2025 Democratizing self-driving labs: advances in low-cost 3D printing
for laboratory automation. Digit. Discov. (doi:10.1039/D4DD00411F)
70. Rybin N, Novikov IS, Shapeev A. 2025 Accelerating structure prediction of molecular crystals using actively trained moment tensor potential.
Phys. Chem. Chem. Phys. 27, 5141–5148. (doi:10.1039/d4cp04578e)
71. Seifrid M, Pollice R, Aguilar-Granda A, Morgan Chan Z, Hotta K, Ser CT, Vestfrid J, Wu TC, Aspuru-Guzik A. 2022 Autonomous chemical
experiments: challenges and perspectives on establishing a self-driving lab. Acc. Chem. Res. 55, 2454–2466. (doi:10.1021/acs.accounts.
2c00220)
72. Greenaway RL, Jelfs KE, Spivey AC, Yaliraki SN. 2023 From alchemist to AI chemist. Nat. Rev. Chem. 7, 527–528. (doi:10.1038/s41570-023-
00522-w)
73. Pizzi G, Cepellotti A, Sabatini R, Marzari N, Kozinsky B. 2016 AiiDA: automated interactive infrastructure and database for computational
science. Comput. Mater. Sci. 111, 218–230. (doi:10.1016/j.commatsci.2015.09.013)
74. Roch LM, Häse F, Kreisbeck C, Tamayo-Mendoza T, Yunker LPE, Hein JE, Aspuru-Guzik A. 2020 ChemOS: an orchestration software to
democratize autonomous discovery. PLoS One 15, e0229862. (doi:10.1371/journal.pone.0229862)
75. Di Fiore F, Nardelli M, Mainini L. 2024 Active learning and Bayesian optimization: a unified perspective to learn with a goal. Arch. Computat.
Methods Eng. 31, 2985–3013. (doi:10.1007/s11831-024-10064-z)
76. Gao W, Fu T, Sun J, Coley CW. 2022 Sample efficiency matters: a benchmark for practical molecular optimization. In Proc. 36th Int. Conf. Neural
Information Processing Systems, pp. 21342–21357. Red Hook, NY, USA: Curran Associates Inc.
77. Keith JA, Vassilev-Galindo V, Cheng B, Chmiela S, Gastegger M, Müller KR, Tkatchenko A. 2021 Combining machine learning and computational
chemistry for predictive insights into chemical systems. Chem. Rev. 121, 9816–9872. (doi:10.1021/acs.chemrev.1c00107)
78. Zheng Z et al. 2023 ChatGPT Research Group for optimizing the crystallinity of MOFs and COFs. ACS Cent. Sci. 9, 2161–2170. (doi:10.1021/
acscentsci.3c01087)
79. Bran AM, Cox S, Schilter O, Baldassari C, White AD, Schwaller P. 2024 Augmenting large language models with chemistry tools. Nat. Mach.
Intell. 6, 525–535. (doi:10.1038/s42256-024-00832-8)
80. Rutter H. 2001 U.S. Court of Appeals for the Federal Circuit 243 F.3d 1345. See https://law.justia.com/cases/federal/appellate-courts/F3/243/
1345/603781/ (accessed 5 September 2025).
81. 2024 Inventorship guidance for AI-assisted inventions. United States Patent and Trademark Office. See https://www.federalregister.gov/
documents/2024/02/13/2024-02623/inventorship-guidance-for-ai-assisted-inventions.
82. Früh A. 2023 Inventorship in the age of artificial intelligence. In A critical mind: Hanns Ullrich’s footprint in internal market law, antitrust and
intellectual property (eds C Godt, M Lamping), pp. 455–470. Berlin, Heidelberg, Germany: Springer. (doi:10.1007/978-3-662-65974-8_18)
83. Inventorship of AI-generated Inventions. 2024 The Five IP Offices (IP5), Seoul, Korea. See https://link.epo.org/ip5/Inventorship_AI-related_
inventions_2024 (accessed 11 September 2024).
84. Leaps and Boundaries. 2022 The Expert Panel on Artificial Intelligence for Science and Engineering, Council of Canadian Academies. See https://
cca-reports.ca/reports/ai-for-science-and-engineering/ (accessed 3 September 2025).
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 24 -->

85. Padmanabhan A, Wadsworth T. 2023 A common law theory of ownership for AI-created properties. J. Pat. Trademark Off. Soc. 104, 155. https:/ 24
/ssrn.com/abstract=4411194
86. Lohn JD, Hornby GS, Linden DS. 2005 An evolved antenna for deployment on NASA’s Space Technology 5 Mission. In Genetic programming
theory and practice II (eds UM O’Reilly, T Yu, R Riolo, B Worzel), pp. 301–315. Boston, MA, USA: Springer US. (doi:10.1007/0-387-23254-0_18)
87. McDermott E. 2021 DABUS scores again with win on AI inventorship question in Australia court. IPWatchdog.com | Patents & Intellectual Property
Law. See https://ipwatchdog.com/2021/08/02/dabus-scores-win-ai-inventorship-question-australia-court/id=136304/ (accessed 20 February
2025).
88. Hartung K. 2022 DABUS sent back to drawing board following reversal of inventorship decision by Australia court. IPWatchdog.com | Patents &
Intellectual Property Law. See https://ipwatchdog.com/2022/04/17/dabus-sent-back-drawing-board-following-reversal-inventorshipdecision-australia-court/id=148464/ (accessed 20 February 2025).
89. Padmanabhan A. 2024 Humans can patent AI-generated creations. See https://news.bloomberglaw.com/us-law-week/humans-can-patent-aigenerated-creations-ownership-is-less-clear (accessed 3 September 2024).
90. Knutson K. 2020 Anything you can do, AI can’t do better: An analysis of conception as a requirement for patent inventorship and a rationale for
excluding AI inventors. Cybaris 11.https://open.mitchellhamline.edu/cybaris/vol11/iss2/2
91. Stanková E. 2021 Human inventorship in European patent law. Camb. Law J. 80, 338–365. (doi:10.1017/s0008197321000507)
92. Ishizuki N, Shimizu R, Hitosugi T. 2023 Autonomous experimental systems in materials science. Sci. Technol. Adv. Mater. 3, 2197519. (doi:10.
1080/27660400.2023.2197519)
93. Hubbert C. 2023 Patents vs. trade secrets: Choosing the best method to protect your intellectual property. Dickinson Law’s Inside Entrepreneurship
Law Blog. See https://sites.psu.edu/entrepreneurshiplaw/2023/06/05/patents-vs-trade-secrets-choosing-the-best-method-to-protect-yourintellectual-property/ (accessed 12 September 2024).
94. National Academies of Sciences, Engineering, and Medicine. 2024 Artificial intelligence and automated laboratories for biotechnology:
leveraging opportunities and mitigating risks: proceedings of a workshop—in Brief. Washington, D.C: The National Academies Press. (doi:10.
17226/27469)
95. Carter SR, Wheeler N, Chwalek S, Isaac C, Yassif JM. 2023 The convergence of artificial intelligence and the life sciences. Nuclear Threat Initiative.
See https://www.nti.org/analysis/articles/the-convergence-of-artificial-intelligence-and-the-life-sciences/ (accessed 31 October 2023).
96. 2024 Safety and security (SPR 2019-2022) | RIVM - Dutch National Institute for Public Health and the Environment. See https://www.rivm.nl/en/
about-rivm/knowledge-and-expertise/strategic-programme-rivm/2019-2022/safety-and-security (accessed 20 September 2024).
97. 2023 Anthropic’s Responsible Scaling Policy, Version 1.0. See https://www-cdn.anthropic.com/1adf000c8f675958c2ee23805d91aaade1cd4613/
responsible-scaling-policy.pdf (accessed 22 January 2024).
98. Leichner D. 2023 Jason Wallace of Emerald Cloud Lab on the future of artificial intelligence. Authority Magazine. See https://medium.com/
authority-magazine/jason-wallace-of-emerald-cloud-lab-on-the-future-of-artificial-intelligence-5fc106ea6f30 (accessed 27 September
2024).
99. Nandi S. 2025 AI liability and accountability: who is responsible when AI makes a harmful decision? AZoRobotics. See https://www.azorobotics.
com/Article.aspx?ArticleID=741 (accessed 3 June 2025).
100. Felten EW, Raj M, Seamans R. 2019 The occupational impact of artificial intelligence: labor, skills, and polarization. Soc. Sci. Res. Netw. (doi:10.
2139/ssrn.3368605)
101. Autor DH. 2015 Why are there still so many jobs? The history and future of workplace automation. J. Econ. Perspect. 29, 3–30. (doi:10.1257/jep.
29.3.3)
102. Acemoglu D, Restrepo P. 2018 Artificial intelligence, automation and work. National bureau of economic research working Paper 24196 (doi:10.
3386/w24196)
103. Autor D, Chin C, Salomons AM, Seegmiller B. 2022 New Frontiers: The Origins and Content of New Work, 1940–2018. National Bureau of
Economic Research Working Paper 30389 (doi:10.3386/w30389)
104. Acemoglu D, Restrepo P. 2019 Automation and new tasks: how technology displaces and reinstates labor. J. Econ. Perspect. 33, 3–30. (doi:10.
1257/jep.33.2.3)
105. Green A. 2023 OECD employment outlook 2023: artificial intelligence and the labour market, pp. 103–127. Paris, France: Organisation for
Economic Co-operation and Development. See https://www.oecd-ilibrary.org/employment/oecd-employment-outlook-2023_08785bba-en.
106. Stone P et al. 2016 Artificial Intelligence and Life in 2030. One Hundred Year Study on Artificial Intelligence: Report of the 2015-2016 Study
Panel.Stanford University. See https://ai100.stanford.edu/2016-report.
107. Webb M. 2020 The impact of artificial intelligence on the labor market. Stanford University. See https://www.michaelwebb.co/webb_ai.pdf.
108. U.S. government website. 2024 Occupational employment and wage statistics: U.S. Bureau of Labor Statistics. Bureau of Labor Statistics. See
https://www.bls.gov/oes/ (accessed 23 September 2024).
109. National Academies of Sciences, Engineering, and Medicine. 2024 Artificial intelligence and the future of work. Washington, D.C: The National
Academies Press. (doi:%2010.17226/27644.rk)
110. Bessen J. 2015 Learning by doing. New Haven, CT: Yale University Press. See https://yalebooks.yale.edu/9780300195668/learning-by-doing.
111. Moravec H. 1990 Mind children: the future of robot and human intelligence, Reprint. Cambridge, MA, USA: Harvard University Press.
112. Stork J, Eiben AE, Bartz-Beielstein T. 2022 A new taxonomy of global optimization algorithms. Nat. Comput. 21, 219–242. (doi:10.1007/
s11047-020-09820-4)
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646

---

<!-- Page 25 -->

113. Åqvist J. 2024 Scientific background to the Nobel Prize in Chemistry 2024. The Royal Swedish Academy of Sciences. See https://www. 25
nobelprize.org/prizes/chemistry/2024/advanced-information.
royalsocietypublishing.org/journal/rsos
R.
Soc.
Open
Sci.
12:
250646
