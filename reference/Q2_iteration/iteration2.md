<!-- Page 1 -->

Article
Autonomous chemical research with large
language models
https://doi.org/10.1038/s41586-023-06792-0 Daniil A. Boiko1, Robert MacKnight1, Ben Kline2 & Gabe Gomes1,3,4 ✉
Received: 20 April 2023
Accepted: 27 October 2023 Transformer-based large language models are making significant strides in various
fields, such as natural language processing1–5, biology6,7, chemistry8–10 and computer
Published online: 20 December 2023
programming11,12. Here, we show the development and capabilities of Coscientist, an
Open access
artificial intelligence system driven by GPT-4 that autonomously designs, plans and
Check for updates
performs complex experiments by incorporating large language models empowered
by tools such as internet and documentation search, code execution and experimental
automation. Coscientist showcases its potential for accelerating research across six
diverse tasks, including the successful reaction optimization of palladium-catalysed
cross-couplings, while exhibiting advanced capabilities for (semi-)autonomous
experimental design and execution. Our findings demonstrate the versatility, efficacy
and explainability of artificial intelligence systems like Coscientist in advancing
research.
Large language models (LLMs), particularly transformer-based models, can use tools to browse the internet and relevant documentation,
are experiencing rapid advancements in recent years. These models use robotic experimentation application programming interfaces
have been successfully applied to various domains, including natural (APIs) and leverage other LLMs for various tasks. This work has
language1–5, biological6,7 and chemical research8–10 as well as code gen- been done independently and in parallel to other works on autonoeration11,12. Extreme scaling of models13, as demonstrated by OpenAI, mous agents23–25, with ChemCrow26 serving as another example in
has led to significant breakthroughs in the field1,14. Moreover, tech- the chemistry domain. In this paper, we demonstrate the versatilniques such as reinforcement learning from human feedback15 can ity and performance of Coscientist in six tasks: (1) planning chemiconsiderably enhance the quality of generated text and the models’ cal syntheses of known compounds using publicly available data;
capability to perform diverse tasks while reasoning about their (2) efficiently searching and navigating through extensive hardware
decisions16. documentation; (3) using documentation to execute high-level com-
On 14 March 2023, OpenAI released their most capable LLM to date, mands in a cloud laboratory; (4) precisely controlling liquid han-
GPT-414. Although specific details about the model training, sizes and dling instruments with low-level instructions; (5) tackling complex
data used are limited in GPT-4’s technical report, OpenAI research- scientific tasks that demand simultaneous use of multiple hardware
ers have provided substantial evidence of the model’s exceptional modules and integration of diverse data sources; and (6) solving
problem-solving abilities. Those include—but are not limited to—high optimization problems requiring analyses of previously collected
percentiles on the SAT and BAR examinations, LeetCode challenges experimental data.
and contextual explanations from images, including niche jokes14.
Moreover, the technical report provides an example of how the model
Coscientist system architecture
can be used to address chemistry-related problems.
Simultaneously, substantial progress has been made toward the auto- Coscientist acquires the necessary knowledge to solve a complex
mation of chemical research. Examples range from the autonomous problem by interacting with multiple modules (web and documendiscovery17,18 and optimization of organic reactions19 to the develop- tation search, code execution) and by performing experiments.
ment of automated flow systems20,21 and mobile platforms22. The main module (‘Planner’) has the goal of planning, based on the
The combination of laboratory automation technologies with power- user input by invoking the commands defined below. The Planner
ful LLMs opens the door to the development of a sought-after system is a GPT-4 chat completion instance serving the role of an assistant.
that autonomously designs and executes scientific experiments. To The initial user input along with command outputs are treated as
accomplish this, we intended to address the following questions. What user messages to the Planner. System prompts (static inputs definare the capabilities of LLMs in the scientific process? What degree of ing the LLMs’ goals) for the Planner are engineered1,27 in a modular
autonomy can we achieve? How can we understand the decisions made fashion, described as four commands that define the action space:
by autonomous agents? ‘GOOGLE’, ‘PYTHON’, ‘DOCUMENTATION’ and ‘EXPERIMENT’. The
In this work, we present a multi-LLMs-based intelligent agent (here- Planner calls on each of these commands as needed to collect knowlafter simply called Coscientist) capable of autonomous design, plan- edge. The GOOGLE command is responsible for searching the interning and performance of complex scientific experiments. Coscientist net with the ‘Web searcher’ module, which is another LLM itself.
1Department of Chemical Engineering, Carnegie Mellon University, Pittsburgh, PA, USA. 2Emerald Cloud Lab, South San Francisco, CA, USA. 3Department of Chemistry, Carnegie Mellon
University, Pittsburgh, PA, USA. 4Wilton E. Scott Institute for Energy Innovation, Carnegie Mellon University, Pittsburgh, PA, USA. ✉e-mail: gabegomes@cmu.edu
570 | Nature | Vol 624 | 21/28 December 2023

---

<!-- Page 2 -->

a The module does not use LLMs
Input prompt from scientist The module uses LLMs
Command used by LLM
Coscientist
Google GOOGLE
Search API Physical world
hardware
Web searcher GOOGLE Planner EXPERIMENT Automation • Cloud laboratory
• Liquid handler
Internet BROWSE • Manual
PYTHON DOCUMENTATION experimentation
Docs index
co D n o ta c in ke e r r sub C m od is e s ion Code execution Docs searcher s R u e m tr m ie a v r a iz l a a t n io d n H do a c rd u w m a e r n e t a A t P io I n
b
Performed experiments Searching for – Performing Generating – Controlling a liquid handler
to validate the agent organic syntheses cross-coupling reactions SLL code for – Using a liquid handler and
online – Optimizing reaction a cloud UV-Vis together
conditions laboratory
c
Liquid handler’s
pipettes
Heater–shaker Laptop, accessing
module a web server with
deployed Coscientist
Fig. 1 | The system’s architecture. a, Coscientist is composed of multiple performed to demonstrate the capabilities when using individual modules or
modules that exchange messages. Boxes with blue background represent LLM their combinations. c, Image of the experimental setup with a liquid handler.
modules, the Planner module is shown in green, and the input prompt is in red. UV-Vis, ultraviolet visible.
White boxes represent modules that do not use LLMs. b, Types of experiments
The PYTHON command allows the Planner to perform calculations to
Web search module
prepare the experiment using a ‘Code execution’ module. The EXPERI-
MENT command actualizes ‘Automation’ through APIs described by To demonstrate one of the functionalities of the Web Searcher
the DOCUMENTATION module. Like GOOGLE, the DOCUMENTA- module, we designed a test set composed of seven compounds to
TION command provides information to the main module from a synthesize, as presented in Fig. 2a. The Web Searcher module versource, in this case documentation concerning the desired API. In sions are represented as ‘search-gpt-4’ and ‘search-gpt-3.5-turbo’.
this study, we have demonstrated the compatibility with the Open- Our baselines include OpenAI’s GPT-3.5 and GPT-4, Anthropic’s
trons Python API and the Emerald Cloud Lab (ECL) Symbolic Lab Claude 1.328 and Falcon-40B-Instruct29—considered one of the best
Language (SLL). Together, these modules make up Coscientist, which open-source models at the time of this experiment as per the OpenLLM
receives a simple plain text input prompt from the user (for example, leaderboard30.
“perform multiple Suzuki reactions”). This architecture is depicted We prompted every model to provide a detailed compound synthesis,
in Fig. 1. ranking the outputs on the following scale (Fig. 2):
Furthermore, some of the commands can use subactions. The • 5 for a very detailed and chemically accurate procedure description
GOOGLE command is capable of transforming prompts into appro- • 4 for a detailed and chemically accurate description but without
priate web search queries, running them against the Google Search reagent quantities
API, browsing web pages and funneling answers back to the Planner. • 3 for a correct chemistry description that does not include step-
Similarly, the DOCUMENTATION command performs retrieval and sum- by-step procedure
marization of necessary documentation (for example, robotic liquid • 2 for extremely vague or unfeasible descriptions
handler or a cloud laboratory) for Planner to invoke the EXPERIMENT • 1 for incorrect responses or failure to follow instructions
command. • All scores below 3 indicate task failure. It is important to note that
The PYTHON command performs code execution (not reliant upon all answers between 3 and 5 are chemically correct but offer varying
any language model) using an isolated Docker container to protect the levels of detail. Despite our attempts to better formalize the scale,
users’ machine from any unexpected actions requested by the Planner. labelling is inherently subjective and so, may be different between
Importantly, the language model behind the Planner enables code to be the labelers.
fixed in case of software errors. The same applies to the EXPERIMENT Across non-browsing models, the two versions of the GPT-4 model
command of the Automation module, which executes generated code performed best, with Claude v.1.3 demonstrating similar performance.
on corresponding hardware or provides the synthetic procedure for GPT-3 performed significantly worse, and Falcon 40B failed in most
manual experimentation. cases. All non-browsing models incorrectly synthesized ibuprofen
Nature | Vol 624 | 21/28 December 2023 | 571

---

<!-- Page 3 -->

Article
a
5
4
3
2
1
0
Acetaminophen Aspirin Benzoic acid Ethylacetate Ibuprofen Nitroaniline Phenolphthalein
Acceptable performance search-gpt-3.5-turbo gpt-4-0314 claude-1.3
search-gpt-4 gpt-4 gpt-3.5-turbo falcon-40b-instruct
b
Incorrect synthesis steps but makes chemical sense 2 Correct synthesis, including detailed experimental procedure 5
(GPT-3.5, no search) (GPT-4 with search)
c
Incorrect synthesis steps, does not make chemical sense (GPT-4, no search) 1
Correct synthesis logic but no reagents and experimental procedure 3
(Fig. 2c). Nitroaniline is another example; although some generaliza-
Documentation search module
tion of chemical knowledge might inspire the model to propose direct
nitration, this approach is not experimentally applicable as it would Addressing the complexities of software components and their interproduce a mixture of compounds with a very minor amount of the actions is crucial for integrating LLMs with laboratory automation. A
product (Fig. 2b). Only the GPT-4 models occasionally provided the key challenge lies in enabling Coscientist to effectively utilize technical
correct answer. documentation. LLMs can refine their understanding of common APIs,
The GPT-4-powered Web Searcher significantly improves on synthe- such as the Opentrons Python API37, by interpreting and learning from
sis planning. It reached maximum scores across all trials for acetami- relevant technical documentation. Furthermore, we show how GPT-4
nophen, aspirin, nitroaniline and phenolphthalein (Fig. 2b). Although can learn how to programme in the ECL SLL.
it was the only one to achieve the minimum acceptable score of three Our approach involved equipping Coscientist with essential docufor ibuprofen, it performed lower than some of the other models for mentation tailored to specific tasks (as illustrated in Fig. 3a), allowing
ethylacetate and benzoic acid, possibly because of the widespread it to refine its accuracy in using the API and improve its performance
nature of these compounds. These results show the importance of in automating experiments.
grounding LLMs to avoid ‘hallucinations’31. Overall, the performance Information retrieval systems are usually based on two candidate
of GPT-3.5-enabled Web Searcher trailed its GPT-4 competition, mainly selection approaches: inverted search index and vector database38–41.
because of its failure to follow specific instructions regarding output For the first one, each unique word in the search index is mapped to the
format. documents containing it. At inference time, all documents containing
Extending the Planner’s action space to leverage reaction data- words from a query are selected and ranked based on various manually
bases, such as Reaxys32 or SciFinder33, should significantly enhance defined formulas42. The second approach starts by embedding the
the system’s performance (especially for multistep syntheses). documents with neural networks or as term frequency–inverse docu-
Alternatively, analysing the system’s previous statements is another ment frequency embedding vectors43, followed by the construction
approach to improving its accuracy. This can be done through advanced of a vector database. Retrieval of similar vectors from this database
prompting strategies, such as ReAct34, Chain of Thought35 and Tree of occurs at inference time, usually using one of the approximate nearest
Thoughts36. neighbour search algorithms44. When strategies such as Transformer
572 | Nature | Vol 624 | 21/28 December 2023
ssentcerroC liated
fo
leveL
Average label
Task
complexity
O
HNO 3 –O O N+ Ac 2 O/AcOH
NH
HNO 3 –O N+ HCl/H 2 O –O O N+
NH 2 H 2 SO 4 NH 2 NH 2 reflux O H 2 SO 4 NH NH 2
O
O
Ac O O Cl Cl KMnO (1) C H COCl, py O
2 2 4 2 5
OH
AlCl , HCl OH UV light NaOH, H O (2) NaOH, H O OH
3 2 2
O
O OH Cl MgCl
OH
Fig. 2 | Coscientist’s capabilities in chemical synthesis planning tasks. a, Comparison of various LLMs on compound synthesis benchmarks. Error bars
represent s.d. values. b, Two examples of generated syntheses of nitroaniline. c, Two example of generated syntheses of ibuprofen. UV, ultraviolet.

---

<!-- Page 4 -->

a OT-2 implementation Initial OT-2 API documentation
request from Planner
Planner
Query
DOCUMENTATION embedding [ .. . ]
heat and shake mixtures [ . . . ]
using the OT-2 robot
[ . . . ]
[ . . . ]
c ECL implementation
models are used, there are more chances to account for synonyms was injected along with the analyte’s solution. This demonstrates
natively without doing synonym-based query expansion, as would be the importance of development of automated techniques for qualdone in the first approach45. ity control in cloud laboratories. Follow-up experiments leveraging
Following the second approach, all sections of the OT-2 API documen- web search to specify and/or refine additional experimental paramtation were embedded using OpenAI’s ada model. To ensure proper use eters (column chemistry, buffer system, gradient and so on) would be
of the API, an ada embedding for the Planner’s query was generated, required to optimize the experimental results. Further details on this
and documentation sections are selected through a distance-based investigation are in Supplementary Information section ‘Analysis of
vector search. This approach proved critical for providing Coscientist ECL documentation search results’.
with information about the heater–shaker hardware module necessary A separate prompt-to-samples investigation, investigation 3, was
for performing chemical reactions (Fig. 3b). conducted by providing a catalogue of available samples, enabling the
A greater challenge emerges when applying this approach to a identification of relevant stock solutions that are on ECL’s shelves. To
more diverse robotic ecosystem, such as the ECL. Nonetheless, we can showcase this feature, we provide the Docs searcher module with all
explore the effectiveness of providing information about the ECL SLL, 1,110 Model samples from the catalogue. By simply providing a search
which is currently unknown to the GPT-4 model. We conducted three term (for example, ‘Acetonitrile’), all relevant samples are returned.
separate investigations concerning the SLL: (1) prompt-to-function; This is also available in Supplementary Information.
(2) prompt-to-SLL; and (3) prompt-to-samples. Those investigations
are detailed in Supplementary Information section ‘ECL experiments’.
Controlling laboratory hardware
For investigation 1, we provide the Docs searcher with a documentation guide from ECL pertaining to all available functions for running Access to documentation enables us to provide sufficient information
experiments46. Figure 3c summarizes an example of the user provid- for Coscientist to conduct experiments in the physical world. To initiate
ing a simple prompt to the system, with the Planner receiving rele- the investigation, we chose the Opentrons OT-2, an open-source liquid
vant ECL functions. In all cases, functions are correctly identified for handler with a well-documented Python API. The ‘Getting Started’
the task. page from its documentation was supplied to the Planner in the system
Figure 3c,d continues to describe investigation 2, the prompt-to-SLL prompt. Other pages were vectorized using the approach described
investigation. A single appropriate function is selected for the task, above. For this investigation, we did not grant access to the internet
and the documentation is passed through a separate GPT-4 model to (Fig. 4a).
perform code retention and summarization. After the complete docu- We started with simple plate layout-specific experiments. Straightmentation has been processed, the Planner receives usage information forward prompts in natural language, such as “colour every other line
to provide EXPERIMENT code in the SLL. For instance, we provide a with one colour of your choice”, resulted in accurate protocols. When
simple example that requires the ‘ExperimentHPLC’ function. Proper executed by the robot, these protocols closely resembled the requested
use of this function requires familiarity with specific ‘Models’ and prompt (Fig. 4b–e).
‘Objects’ as they are defined in the SLL. Generated code was success- Ultimately, we aimed to assess the system’s ability to integrate multifully executed at ECL; this is available in Supplementary Information. ple modules simultaneously. Specifically, we provided the ‘UVVIS’ com-
The sample was a caffeine standard sample. Other parameters (column, mand, which can be used to pass a microplate to plate reader working
mobile phases, gradients) were determined by ECL’s internal software in the ultraviolet–visible wavelength range. To evaluate Coscientist’s
(a high-level description is in Supplementary Information section capabilities to use multiple hardware tools, we designed a toy task; in
‘HPLC experiment parameter estimation’). Results of the experiment 3 wells of a 96-well plate, three different colours are present—red, yellow
are provided in Supplementary Information section ‘Results of the and blue. The system must determine the colours and their positions
HPLC experiment in the cloud lab’. One can see that the air bubble on the plate without any prior information.
Nature | Vol 624 | 21/28 December 2023 | 573
... Precompiled text
embeddings for sections
of API documentation ‘Hardware modules’
Initial cloud laboratory API documentation request from Planner
Planner
DOCUMENTATION [ .. . ]
analyse a mixture to [ . . . ] see what is in it
[ . . . ]
[ . . . ]
...
b Valid OT-2 API code
API usage
information # Heat and shake the reaction
prompt-to-OT-2 hs_mod.set_target_temperature(75)
hs_mod.wait_for_temperature()
hs_mod.set_and_wait_for_shake_speed(500)
Vector # Deactivate heater and shaker
search hs_mod.deactivate_heater() hs_mod.deactivate_shaker()
hs_mod.open_labware_latch()
Proper usage of heater–shaker module
Prompt-to-SLL d Valid ECL SLL code
# Generated HPLC Experiment SLL Function Call
Query ExperimentHPLC[
embedding Object[Sample, ...], Instrument -> Model[Instrument, ...]
]
Text embeddings Vector ExperimentHPLC[Samples] => Protocol
search Experimental Principles... for 114 ECL Instrumentation... experiment functions Experiment Options... Targeted experiment options are
Sample Parameters... set by the Planner
...
Fig. 3 | Overview of documentation search. a, Prompt-to-code through ada laboratory language) through supplementation of documentation. d, Example
embedding and distance-based vector search. b, Example of code for using of valid ECL SLL code for performing high-performance liquid chromatography
OT-2’s heater–shaker module. c, Prompt-to-function/prompt-to-SLL (to symbolic (HPLC) experiments.

---

<!-- Page 5 -->

Article
a “Getting started” Vectorized tutorial
Open source in system prompt and API reference
liquid handling
system EXPERIMENT DOCUMENTATION Docs searcher
Planner
UV-Vis plate reader UVVIS PYTHON Code execution
b c
Draw a red cross Colour every other
using food row of a 96-well
colouring in the plate with one
center of colour of your
96-well plate. choice. Remember
that for me to
<setup description> see it, you should
put at least
10 μl.
<setup description>
d e
Draw a 3 × 3 Draw a blue
rectangle using diagonal starting
yellow colour at from lower left
upper left part of (H1) in the
the 96-well plate. 96-well plate.
Remember that for Remember that for
me to see it, you me to see it, you
should put at least should put at
10 μl. least 10 μl.
<setup description> <setup description>
Fig. 4 | Robotic liquid handler control capabilities and integration with analytical tools. a, Overview of Coscientist’s configuration. b, Drawing a red cross.
c, Colouring every other row. d, Drawing a yellow rectangle. e, Drawing a blue diagonal.
The Coscientist’s first action was to prepare small samples of the base DBU (1,8-diazabicyclo[5.4.0]undec-7-ene) is selected more often
original solutions (Extended Data Fig. 1). Ultraviolet-visible meas- with the PEPPSI–IPr (PEPPSI, pyridine-enhanced precatalyst preparaurements were then requested to be performed by the Coscientist tion stabilization and initiation; IPr, 1,3-bis(2,6-diisopropylphenyl)
(Supplementary Information section ‘Solving the colours problem’ imidazol-2-ylidene) complex, with that preference switching in Sonogaand Supplementary Fig. 1). Once completed, Coscientist was pro- shira reaction experiments; likewise, bromobenzene is chosen more
vided with a file name containing a NumPy array with spectra for each often for Suzuki than for Sonogashira couplings. Additionally, the
well of the microplate. Coscientist subsequently generated Python model can provide justifications on specific choices (Fig. 5g), demcode to identify the wavelengths with maximum absorbance and onstrating the ability to operate with concepts such as reactivity and
used these data to correctly solve the problem, although it required selectivity (more details are in Supplementary Information section
a guiding prompt asking it to think through how different colours ‘Analysis of behaviour across multiple runs’). This capability highlights
absorb light. a potential future use case to analyse the reasoning of the LLMs used by
performing experiments multiple times. Although the Web Searcher
visited various websites (Fig. 5h), overall Coscientist retrieves Wikipe-
Integrated chemical experiment design
dia pages in approximately half of cases; notably, American Chemical
We evaluated Coscientist’s ability to plan catalytic cross-coupling Society and Royal Society of Chemistry journals are amongst the top
experiments by using data from the internet, performing the neces- five sources.
sary calculations and ultimately, writing code for the liquid handler. To Coscientist then calculates the required volumes of all reactants
increase complexity, we asked Coscientist to use the OT-2 heater–shaker and writes a Python protocol for running the experiment on the
module released after the GPT-4 training data collection cutoff. The OT-2 robot. However, an incorrect heater–shaker module method
available commands and actions supplied to the Coscientist are shown name was used. Upon making this mistake, Coscientist uses the Docs
in Fig. 5a. Although our setup is not yet fully automated (plates were searcher module to consult the OT-2 documentation. Next, Coscientist
moved manually), no human decision-making was involved. modifies the protocol to a corrected version, which ran successfully
The test challenge for Coscientist’s complex chemical experimen- (Extended Data Fig. 2). Subsequent gas chromatography–mass spectation capabilities was designed as follows. (1) Coscientist is pro- trometry analysis of the reaction mixtures revealed the formation of
vided with a liquid handler equipped with two microplates (source the target products for both reactions. For the Suzuki reaction, there
and target plates). (2) The source plate contains stock solutions of is a signal in the chromatogram at 9.53 min where the mass spectra
multiple reagents, including phenyl acetylene and phenylboronic match the mass spectra for biphenyl (corresponding molecular ion
acid, multiple aryl halide coupling partners, two catalysts, two bases mass-to-charge ratio and fragment at 76 Da) (Fig. 5i). For the Sonogaand the solvent to dissolve the sample (Fig. 5b). (3) The target plate shira reaction, we see a signal at 12.92 min with a matching molecular
is installed on the OT-2 heater–shaker module (Fig. 5c). (4) Coscien- ion mass-to-charge ratio; the fragmentation pattern also looks very
tist’s goal is to successfully design and perform a protocol for Suzuki– close to the one from the spectra of the reference compound (Fig. 5j).
Miyaura and Sonogashira coupling reactions given the available Details are in Supplementary Information section ‘Results of the
resources. experimental study’.
To start, Coscientist searches the internet for information on the Although this example requires Coscientist to reason on which rearequested reactions, their stoichiometries and conditions (Fig. 5d). gents are most suitable, our experimental capabilities at that point
The correct coupling partners are selected for the corresponding limited the possible compound space to be explored. To address this,
reactions. Designing and performing the requested experiments, the we performed several computational experiments to evaluate how a
strategy of Coscientist changes among runs (Fig. 5f). Importantly, the similar approach can be used to retrieve compounds from large comsystem does not make chemistry mistakes (for instance, it never selects pound libraries47. Figure 5e shows Coscientist’s performance across five
phenylboronic acid for the Sonogashira reaction). Interestingly, the common organic transformations, with outcomes depending on the
574 | Nature | Vol 624 | 21/28 December 2023

---

<!-- Page 6 -->

Suzuki Sonogashira Suzuki Sonogashira
1.0
A 0% 100% A 100% 0% Reactivity/rates en.wikipedia.org
chem.libretexts.org 0.5
B 66% 30% 1% 0% B 84% 12% 0% 1% R t e h q e u r i e re a d c t f i o o r n organic-c p h u e b m s i . s a t c r s y . . o o r r g g 0 10 20
C 91% 8% C 84% 15% a A r l e l o s p u t it io ab ns le pubs.rsc.org Time (min)
sciencedirect.com D 89% 6% D 75% 19% Commonly used onlinelibrary.wiley.com
sigmaaldrich.com
E 8% E 10%
Availability encyclopedia.pub
1 2 3 4 1 2 3 4 hepatochem.com
Leaving groups ncbi.nlm.nih.gov
reagents.acsgcipr.org D1 92% 75% D1 93% 45% Side reactions researchgate.net
semanticscholar.org
D2 8% 25% D2 7% 55% Higher selectivity arkat-usa.org
C1 C2 C1 C2 B1B2B3B4 B1B2B3B4 0 0.5
Fraction of URLs
queried reaction and its specific run (the GitHub repository has more believe that the community is only starting to understand all the capadetails). For each reaction, Coscientist was tasked with generating bilities of GPT-4 (ref. 48). OpenAI has shown that GPT-4 could rely on
reactions for compounds from a simplified molecular-input line-entry some of those capabilities to take actions in the physical world during
system (SMILES) database. To achieve the task, Coscientist uses web their initial red team testing performed by the Alignment Research
search and code execution with the RDKit chemoinformatics package. Center14.
One of the possible strategies to evaluate an intelligent agent’s reasoning capabilities is to test if it can use previously collected data to
Chemical reasoning capabilities
guide future actions. Here, we focused on the multi-variable design
The system demonstrates appreciable reasoning capabilities, enabling and optimization of Pd-catalysed transformations, showcasing
the request of necessary information, solving of multistep problems Coscientist’s abilities to tackle real-world experimental campaigns
and generation of code for experimental design. Some researchers involving thousands of examples. Instead of connecting LLMs to an
Nature | Vol 624 | 21/28 December 2023 | 575
ytisnetni
.leR
TIC (standard)
TIC
1.0
0.5
0
0 100 200
m/z
ytisnetni
.leR
Spectrum at 9.53 min
1.0
0.5
0
0 100 200
m/z
ytisnetni
.leR
1.0
0.5
0 10 20
Time (min)
Spectrum of biphenyl standard
ytisnetni
.leR
1.0
0.5
0
0 100 200
m/z
ytisnetni
.leR
Spectrum at 12.92 min
1.0
0.5
0
0 100 200
m/z
ytisnetni
.leR
a O liq p u e id n h so an u d rc li e ng system i “ n G s e y t s ti t n e g m s p ta r r o t m ed p ” t V a e n c d t o A r P iz I e r d e f t e u r t e o n r c ia e l b A1 A S 2 ource plate Cl N DiPP Cl Cl
B1 B2 B3 BBB44444
Ph3P Pd PPh3 Pd N
EXPERIMENT DOCUMENTATION se D a o rc c h s er C1 C2 HO B OH Cl N DiPP Cl
Planner plate U re V a - d V e is r UVVIS PYTHON ex C ec o u d t e ion D E1 1 D2 R N
GOOGLE
N
N Google Seach API Web searcher Internet
X
...
c d (cid:60)(cid:82)(cid:88)(cid:3)(cid:81)(cid:72)(cid:72)(cid:71)(cid:3)(cid:87)(cid:82)(cid:3)(cid:83)(cid:72)(cid:85)(cid:73)(cid:82)(cid:85)(cid:80)(cid:3)(cid:54)(cid:88)(cid:93)(cid:88)(cid:78)(cid:76)(cid:3) e 5
T se h t e u p liq s u c id h e h m an e dler (cid:68) (cid:88) (cid:85) (cid:81) (cid:86) (cid:72) (cid:71) (cid:76) (cid:68) (cid:3) (cid:81) (cid:74) (cid:54) (cid:74) (cid:72) (cid:82) (cid:3) (cid:81) (cid:81) (cid:68) (cid:87) (cid:82) (cid:89) (cid:86) (cid:74) (cid:68) (cid:17) (cid:68) (cid:76) (cid:17) (cid:86) (cid:79) (cid:17) (cid:75) (cid:68) (cid:76) (cid:69) (cid:85) (cid:79) (cid:68) (cid:72) (cid:3) (cid:3) (cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:86)(cid:3) (cid:17) (cid:79) (cid:11) (cid:17) (cid:76) (cid:36) (cid:17) (cid:80) (cid:21) (cid:3) (cid:76) (cid:12) (cid:41) (cid:87) (cid:3) (cid:82) (cid:76) (cid:90) (cid:85) (cid:81) (cid:76) (cid:3) (cid:74) (cid:87) (cid:87) (cid:3) (cid:75) (cid:75) (cid:85) (cid:3) (cid:72) (cid:72) (cid:68) (cid:3) (cid:68) (cid:3) (cid:54) (cid:74) (cid:70) (cid:88) (cid:72) (cid:82) (cid:93) (cid:81) (cid:81) (cid:88) (cid:87) (cid:70) (cid:78) (cid:3) (cid:72) (cid:76) (cid:76) (cid:81) (cid:3) (cid:86) (cid:87) (cid:85) (cid:3) (cid:85) (cid:72) (cid:83) (cid:68) (cid:68) (cid:75) (cid:87) (cid:70) (cid:72) (cid:76) (cid:87) (cid:81) (cid:82) (cid:76) (cid:92) (cid:81) (cid:82) (cid:79) (cid:3) (cid:81) (cid:69) (cid:82) (cid:15) (cid:82) (cid:73) (cid:3) (cid:85) (cid:3) (cid:87) (cid:82) (cid:19) (cid:75) (cid:81) (cid:17) (cid:72) (cid:76) (cid:20) (cid:3) (cid:70) (cid:22) (cid:3) (cid:3) (cid:68)(cid:70)(cid:76)(cid:71)(cid:3)
left pipette, (cid:80)(cid:80)(cid:82)(cid:79)(cid:3)(cid:80)(cid:79)(cid:177)(cid:20)(cid:17)(cid:3)(cid:41)(cid:82)(cid:85)(cid:3)(cid:87)(cid:75)(cid:72)(cid:3)(cid:54)(cid:82)(cid:81)(cid:82)(cid:74)(cid:68)(cid:86)(cid:75)(cid:76)(cid:85)(cid:68)(cid:3)(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:15)(cid:3)
20 μl single channel User prompt (cid:87)(cid:75)(cid:72)(cid:3)(cid:79)(cid:76)(cid:80)(cid:76)(cid:87)(cid:76)(cid:81)(cid:74)(cid:3)(cid:85)(cid:72)(cid:68)(cid:74)(cid:72)(cid:81)(cid:87)(cid:3)(cid:76)(cid:86)(cid:3)(cid:83)(cid:75)(cid:72)(cid:81)(cid:92)(cid:79)(cid:68)(cid:70)(cid:72)(cid:87)(cid:92)(cid:79)(cid:72)(cid:81)(cid:72)(cid:3)
r 3 ig 00 h t μ p l i s p i e n t g te le , channel (cid:41) (cid:68) (cid:76) (cid:83) (cid:85) (cid:83) (cid:86) (cid:85) (cid:87) (cid:82) (cid:15) (cid:83) (cid:3) (cid:85) (cid:79) (cid:76) (cid:72) (cid:68) (cid:87) (cid:87) (cid:10) (cid:72) (cid:86) (cid:3) (cid:3) (cid:70) (cid:73) (cid:82) (cid:76) (cid:81) (cid:81) (cid:71) (cid:71) (cid:76) (cid:3) (cid:87) (cid:87) (cid:76) (cid:75) (cid:82) (cid:72) (cid:81) (cid:3) (cid:86)(cid:3)(cid:73)(cid:82)(cid:85)(cid:3)(cid:69)(cid:82)(cid:87)(cid:75)(cid:3) (cid:11) (cid:20) (cid:36) (cid:17) (cid:20) (cid:22) (cid:12) (cid:24) (cid:3) (cid:3) (cid:90) (cid:80) (cid:76) (cid:80) (cid:87) (cid:82) (cid:75) (cid:79) (cid:3) (cid:3) (cid:68) (cid:80) (cid:3) (cid:79)(cid:177) (cid:70) (cid:20) (cid:82) (cid:17) (cid:81)(cid:70)(cid:72)(cid:81)(cid:87)(cid:85)(cid:68)(cid:87)(cid:76)(cid:82)(cid:81)(cid:3)(cid:82)(cid:73)(cid:3)(cid:20)(cid:17)(cid:22)(cid:24)(cid:3)(cid:48)(cid:3)(cid:82)(cid:85)(cid:3) 4
(cid:54)(cid:88)(cid:93)(cid:88)(cid:78)(cid:76)(cid:3)(cid:68)(cid:81)(cid:71)(cid:3)(cid:54)(cid:82)(cid:81)(cid:82)(cid:74)(cid:68)(cid:86)(cid:75)(cid:76)(cid:85)(cid:68)(cid:3) (cid:51)(cid:60)(cid:55)(cid:43)(cid:50)(cid:49)
10 11 (cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:86)(cid:17)(cid:17)(cid:17) (cid:71)(cid:72)(cid:73)(cid:3)(cid:70)(cid:68)(cid:79)(cid:70)(cid:88)(cid:79)(cid:68)(cid:87)(cid:72)(cid:66)(cid:89)(cid:82)(cid:79)(cid:88)(cid:80)(cid:72)(cid:86)(cid:11)(cid:70)(cid:82)(cid:81)(cid:70)(cid:72)(cid:81)(cid:87)(cid:85)(cid:68)(cid:87)(cid:76)(cid:82)(cid:81)(cid:15)
... Planner’s output (cid:3)(cid:3)(cid:3)(cid:3)(cid:71)(cid:72)(cid:86)(cid:76)(cid:85)(cid:72)(cid:71)(cid:66)(cid:80)(cid:80)(cid:82)(cid:79)(cid:32)(cid:19)(cid:17)(cid:19)(cid:21)(cid:24)(cid:12)(cid:29)
7 8 9 (cid:3)(cid:3)(cid:3)(cid:3)(cid:89)(cid:82)(cid:79)(cid:88)(cid:80)(cid:72)(cid:3)(cid:32)(cid:3)(cid:71)(cid:72)(cid:86)(cid:76)(cid:85)(cid:72)(cid:71)(cid:66)(cid:80)(cid:80)(cid:82)(cid:79)(cid:3)(cid:18)(cid:3) 4 5 6 (cid:17) (cid:42) (cid:17) (cid:50) (cid:17) (cid:50)(cid:42)(cid:47)(cid:40)(cid:3)(cid:54)(cid:88)(cid:93)(cid:88)(cid:78)(cid:76)(cid:3)(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:3)(cid:70)(cid:82)(cid:81)(cid:71)(cid:76)(cid:87)(cid:76)(cid:82)(cid:81)(cid:86)(cid:3) (cid:70) (cid:3) (cid:82) (cid:3) (cid:81) (cid:3) (cid:70) (cid:3) (cid:72) (cid:85) (cid:81) (cid:72) (cid:87) (cid:87) (cid:85) (cid:88) (cid:68) (cid:85) (cid:87) (cid:81) (cid:76) (cid:3) (cid:82) (cid:89) (cid:81) (cid:82)(cid:79)(cid:88)(cid:80)(cid:72) 3
(cid:82)(cid:83)(cid:87)(cid:76)(cid:80)(cid:68)(cid:79)
1 2 3 (cid:6)(cid:3)(cid:54)(cid:88)(cid:93)(cid:88)(cid:78)(cid:76)(cid:3)(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)
1 2 2 3 0 0 0 μ μ l t l ip tip s s (cid:36) (cid:54) (cid:70) (cid:81) (cid:88) (cid:68) (cid:3) (cid:93) (cid:81) (cid:82) (cid:88) (cid:3) (cid:83) (cid:78) (cid:69) (cid:87) (cid:76) (cid:72) (cid:76) (cid:177) (cid:3) (cid:80) (cid:48) (cid:82) (cid:68) (cid:76) (cid:69) (cid:79) (cid:92) (cid:87) (cid:3) (cid:68) (cid:68) (cid:86) (cid:88) (cid:76) (cid:72) (cid:85) (cid:81) (cid:87) (cid:68) (cid:72) (cid:3) (cid:3) (cid:71) (cid:82) (cid:70) (cid:17) (cid:73) (cid:85) (cid:17) (cid:3) (cid:82) (cid:17) (cid:70) (cid:86) (cid:82) (cid:86) (cid:81) (cid:16) (cid:71) (cid:70) (cid:76) (cid:82) (cid:87) (cid:88) (cid:76) (cid:83) (cid:82) (cid:79) (cid:81) (cid:76) (cid:86) (cid:81) (cid:3) (cid:74) (cid:73) (cid:3) (cid:82) (cid:85) (cid:85) (cid:72) (cid:3) (cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:86)(cid:3) (cid:70) (cid:17) (cid:82) (cid:17) (cid:81) (cid:17) (cid:70)(cid:66)(cid:36)(cid:21)(cid:3)(cid:32)(cid:3)(cid:19)(cid:17)(cid:20)(cid:22)(cid:3)(cid:6)(cid:3)(cid:80)(cid:80)(cid:82)(cid:79)(cid:18)(cid:80)(cid:47)
5 Source plate 2
(deep 96-well) (cid:17)(cid:17)(cid:17) (cid:19)(cid:17)(cid:20)(cid:28)(cid:21)(cid:22)(cid:19)(cid:26)(cid:25)(cid:28)(cid:21)(cid:22)(cid:19)(cid:26)(cid:25)(cid:28)(cid:21)(cid:22)(cid:21)(cid:3)(cid:19)(cid:17)(cid:19)(cid:20)(cid:27)(cid:24)(cid:20)(cid:27)(cid:24)(cid:20)(cid:27)(cid:24)(cid:20)(cid:27)(cid:24)(cid:20)(cid:27)(cid:24)(cid:20)(cid:26)
10 Heater–shaker (cid:42)(cid:50)(cid:50)(cid:42)(cid:47)(cid:40)(cid:3)(cid:54)(cid:82)(cid:81)(cid:82)(cid:74)(cid:68)(cid:86)(cid:75)(cid:76)(cid:85)(cid:68)(cid:3)(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:3)(cid:70)(cid:82)(cid:81)(cid:71)(cid:76)(cid:87)(cid:76)(cid:82)(cid:81)(cid:86)(cid:3) ... module with (cid:82)(cid:83)(cid:87)(cid:76)(cid:80)(cid:68)(cid:79)
target plate (cid:17)(cid:17)(cid:17)
(cid:55)(cid:75)(cid:72)(cid:3)(cid:82)(cid:83)(cid:87)(cid:76)(cid:80)(cid:68)(cid:79)(cid:3)(cid:70)(cid:82)(cid:81)(cid:71)(cid:76)(cid:87)(cid:76)(cid:82)(cid:81)(cid:86)(cid:3)(cid:73)(cid:82)(cid:85)(cid:3)(cid:87)(cid:75)(cid:72)(cid:3) (cid:39)(cid:50)(cid:38)(cid:56)(cid:48)(cid:40)(cid:49)(cid:55)(cid:36)(cid:55)(cid:44)(cid:50)(cid:49)(cid:3)(cid:75)(cid:82)(cid:90)(cid:3)(cid:87)(cid:82)(cid:3)(cid:88)(cid:86)(cid:72)(cid:3)
(cid:54)(cid:82)(cid:81)(cid:82)(cid:74)(cid:68)(cid:86)(cid:75)(cid:76)(cid:85)(cid:68)(cid:3)(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:15)(cid:3)(cid:68)(cid:3)(cid:70)(cid:85)(cid:82)(cid:86)(cid:86)(cid:16)(cid:70)(cid:82)(cid:88)(cid:83)(cid:79)(cid:76)(cid:81)(cid:74)(cid:3) (cid:75)(cid:72)(cid:68)(cid:87)(cid:72)(cid:85)(cid:177)(cid:86)(cid:75)(cid:68)(cid:78)(cid:72)(cid:85)(cid:3)(cid:80)(cid:82)(cid:71)(cid:88)(cid:79)(cid:72)
(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:3)(cid:82)(cid:73)(cid:3)(cid:68)(cid:3)(cid:89)(cid:76)(cid:81)(cid:92)(cid:79)(cid:3)(cid:82)(cid:85)(cid:3)(cid:68)(cid:85)(cid:92)(cid:79)(cid:3)(cid:75)(cid:68)(cid:79)(cid:76)(cid:71)(cid:72)(cid:3) ... 1
(cid:90)(cid:76)(cid:87)(cid:75)(cid:3)(cid:68)(cid:3)(cid:87)(cid:72)(cid:85)(cid:80)(cid:76)(cid:81)(cid:68)(cid:79)(cid:17)(cid:17)(cid:17)
(cid:17)(cid:17)(cid:17)(cid:3)(cid:41)(cid:82)(cid:85)(cid:3)(cid:87)(cid:75)(cid:72)(cid:3)(cid:54)(cid:88)(cid:93)(cid:88)(cid:78)(cid:76)(cid:3)(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:15)(cid:3)(cid:90)(cid:72)(cid:3) (cid:56) (cid:71) (cid:86) (cid:82) (cid:76) (cid:70) (cid:81) (cid:88) (cid:74) (cid:80) (cid:3) (cid:72) (cid:87) (cid:81) (cid:75) (cid:87) (cid:72) (cid:68) (cid:3) (cid:87) (cid:76) (cid:76) (cid:81) (cid:82) (cid:73) (cid:81) (cid:82) (cid:15) (cid:85) (cid:3) (cid:80) (cid:44) (cid:68) (cid:3) (cid:87) (cid:90) (cid:76) (cid:76) (cid:82) (cid:79) (cid:81) (cid:79) (cid:3) (cid:3) (cid:73) (cid:81) (cid:85) (cid:82) (cid:82) (cid:90) (cid:80) (cid:3) (cid:3) (cid:70) (cid:87) (cid:82) (cid:75) (cid:85) (cid:72) (cid:85) (cid:3) (cid:72)(cid:70)(cid:87)(cid:3) Average
(cid:81)(cid:72)(cid:72)(cid:71)(cid:3)(cid:68)(cid:81)(cid:3)(cid:68)(cid:85)(cid:92)(cid:79)(cid:69)(cid:82)(cid:85)(cid:82)(cid:81)(cid:76)(cid:70)(cid:3)(cid:68)(cid:70)(cid:76)(cid:71)(cid:3)(cid:11)(cid:36)(cid:21)(cid:12)(cid:3)(cid:68)(cid:81)(cid:71)(cid:3) (cid:87)(cid:75)(cid:72)(cid:3)(cid:83)(cid:85)(cid:82)(cid:87)(cid:82)(cid:70)(cid:82)(cid:79)(cid:3)(cid:73)(cid:82)(cid:85)(cid:3)(cid:87)(cid:75)(cid:72)(cid:3)(cid:54)(cid:88)(cid:93)(cid:88)(cid:78)(cid:76)(cid:3)(cid:68)(cid:81)(cid:71)(cid:3) Valid reaction number
(cid:68)(cid:81)(cid:3)(cid:68)(cid:85)(cid:92)(cid:79)(cid:3)(cid:75)(cid:68)(cid:79)(cid:76)(cid:71)(cid:72)(cid:17)(cid:3)(cid:37)(cid:85)(cid:82)(cid:80)(cid:82)(cid:69)(cid:72)(cid:81)(cid:93)(cid:72)(cid:81)(cid:72)(cid:3)(cid:11)(cid:37)(cid:21)(cid:12)(cid:3) (cid:54)(cid:82)(cid:81)(cid:82)(cid:74)(cid:68)(cid:86)(cid:75)(cid:76)(cid:85)(cid:68)(cid:3)(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:86)(cid:3)(cid:88)(cid:86)(cid:76)(cid:81)(cid:74)(cid:3)(cid:87)(cid:75)(cid:72)(cid:3) standard deviation
(cid:90) (cid:68) (cid:85) (cid:82) (cid:85) (cid:72) (cid:88) (cid:92) (cid:68) (cid:79) (cid:79) (cid:70) (cid:71) (cid:3) (cid:87) (cid:3) (cid:75) (cid:76) (cid:69) (cid:68) (cid:89) (cid:72) (cid:79) (cid:72) (cid:3) (cid:76) (cid:3) (cid:68) (cid:71) (cid:87) (cid:3) (cid:72) (cid:75) (cid:86) (cid:15) (cid:68) (cid:88) (cid:3) (cid:81) (cid:76) (cid:69) (cid:3) (cid:87) (cid:72) (cid:70) (cid:68) (cid:70) (cid:75) (cid:69) (cid:68) (cid:79) (cid:79) (cid:88) (cid:82) (cid:72) (cid:86) (cid:85) (cid:3) (cid:72) (cid:82) (cid:70) (cid:3) (cid:69) (cid:75) (cid:76) (cid:72) (cid:82) (cid:87) (cid:81) (cid:76) (cid:10) (cid:93) (cid:70) (cid:86) (cid:72) (cid:72) (cid:3) (cid:81) (cid:3) (cid:80) (cid:72) (cid:73) (cid:82) (cid:17) (cid:82) (cid:85) (cid:17) (cid:85) (cid:72) (cid:17) (cid:3) (cid:3) (cid:87)(cid:75)(cid:72)(cid:3) (cid:75) (cid:40) (cid:72) (cid:59) (cid:68) (cid:51) (cid:87) (cid:40) (cid:72) (cid:53) (cid:85) (cid:44) (cid:177) (cid:48) (cid:86) (cid:40) (cid:75) (cid:49) (cid:68) (cid:55) (cid:78)(cid:72)(cid:85)(cid:3)(cid:80)(cid:82)(cid:71)(cid:88)(cid:79)(cid:72)(cid:17) 0 0 Valid r 0 e . a 5 ctions 1.0 T st o a t n a d l r a e r a d c d ti e o v n ia n t u io m n ber
... (cid:73)(cid:85)(cid:82)(cid:80)(cid:3)(cid:82)(cid:83)(cid:72)(cid:81)(cid:87)(cid:85)(cid:82)(cid:81)(cid:86)(cid:3)(cid:76)(cid:80)(cid:83)(cid:82)(cid:85)(cid:87)(cid:3)(cid:83)(cid:85)(cid:82)(cid:87)(cid:82)(cid:70)(cid:82)(cid:79)(cid:66)(cid:68)(cid:83)(cid:76)(cid:3)
(cid:17)(cid:17)(cid:17)
f g h i j
Spectrum of tolane standard
desoporp
snoitcaer
latoT
Diels–Alder reaction
Michael addition Esterification
Buchwald–Hartwig amination
Mizoroki–Heck reaction
Total number of reactions
0.10
0.08
0.06
0.04
0.02
0 0 0.05 0.10
Valid reactions
desoporp
snoitcaer
latoT
A1
A2 C1 C2 B1 — X = I, R = H
B2 — X = Br, R = H
B3 — X = Cl, R = H
B4 — X = I, R = NO2
E1 — DMF D1 D2
TIC (standard)
TIC
Fig. 5 | Cross-coupling Suzuki and Sonogashira reaction experiments visited URLs. i, Total ion current (TIC) chromatogram of the Suzuki reaction
designed and performed by Coscientist. a, Overview of Coscientist’s mixture (top panel) and the pure standard, mass spectra at 9.53 min (middle
configuration. b, Available compounds (DMF, dimethylformamide; DiPP, panel) representing the expected reaction product and mass spectra of the
2,6-diisopropylphenyl). c, Liquid handler setup. d, Solving the synthesis pure standard (bottom panel). j, TIC chromatogram of the Sonogashira reaction
problem. e, Comparison of reagent selection performance with a large mixture (top panel) and the pure standard, mass spectra at 12.92 min (middle
dataset. f, Comparison of reagent choices across multiple runs. g, Overview panel) representing the expected reaction product and mass spectra of the
of justifications made when selecting various aryl halides. h, Frequency of pure standard (bottom panel). Rel., relative.

---

<!-- Page 7 -->

Article
Average Random Maximum
1.0 1.0
0.5 0.5
0 0
−0.5 −0.5
−1.0 −1.0
1.0
0.5
0
−0.5
−1.0
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20
Number of iterations
optimization algorithm as previously done by Ramos et al.49, we aimed dataset51 (Fig. 6e), where variations in ligands, additives and bases were
to use Coscientist directly. recorded. At this point, any reaction proposed by Coscientist would be
We selected two datasets containing fully mapped reaction condi- within these datasets and accessible as a lookup table.
tion spaces where yield was available for all combinations of variables. We designed the Coscientist’s chemical reasoning capabilities test
One is a Suzuki reaction dataset collected by Perera et al.50, where these as a game with the goal of maximizing the reaction yield. The game’s
reactions were performed in flow with varying ligands, reagents/bases actions consisted of selecting specific reaction conditions with a
and solvents (Fig. 6a). Another is Doyle’s Buchwald–Hartwig reaction sensible chemical explanation while listing the player’s observations
576 | Nature | Vol 624 | 21/28 December 2023
egatnavda
mumixam
dezilamroN
1.0
0.5
0
−0.5
−1.0
1 2 3 4 5 6 7 8 9 10 1112 13 14 15 16 17 18 19 20
Number of iterations
egatnavda
dezilamroN
0.1
0
5 10 15
Number of iterations
mumixam
dezilamroN
evitavired
egatnavda
GPT-4 with prior information GPT-4 without prior information 0.1
0
5 10 15
Number of iterations
dezilamroN egatnavda evitavired
1.0 1.0 1.0
0.5 0.5 0.5
0 0 0
−0.5 −0.5 −0.5
−1.0 −1.0 −1.0
1.0 1.0
0.5 0.5
0 0
−0.5 −0.5
−1.0 −1.0
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20
Number of iterations Number of iterations
egatnavda
mumixam
dezilamroN
1.0
0.5
0
−0.5
−1.0
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20
Number of iterations
egatnavda
dezilamroN
a R 2 Me b
R 1 Me P L d , ( O B A , c S ) 2 , i j k
N + N N 1 min, 100 ºC THP N
N
THP N
c
GPT-4 with prior information (10 data points) GPT-4 without prior information GPT-3.5 without prior information
......yyeett,, aatt tthhee lliimmiitt,, tthhee mmooddeellss
ccoonnvveerrggee ttoo tthhee ssaammee NNMMAA..
PPrriioorr iinnffoorrmmaattiioonn iimmpprroovveess
iinniittiiaall ccoonnddiittiioonnss......
TThhee ssmmaallll nnuummbbeerr ooff eexxaammpplleess ffoorr GGPPTT--33..55
uunnddeerr tthhee fifixxeedd bbuuddggeett iiss dduuee ttoo iittss ffaaiilluurree FFoorr ssoommee ccoommppoouunnddss,, ttoo ffoollllooww tthhee pprroovviiddeedd sscchheemmaa..
tthhee mmooddeell ssttaarrttss wwiitthh
aa vveerryy bbaadd gguueessss..
TThhee mmooddeell ccoonnttiinnuuoouussllyy iimmpprroovveess iittss ssttrraatteeggyy
bbaasseedd oonn nneewwllyy ccoolllleecctteedd ddaattaa..
NNAA ffoorr BBaayyeessiiaann ooppttiimmiizzaattiioonn
ddooeess nnoott iinnccrreeaassee oovveerr ttiimmee
d e NH 2 + X R P ad d d L i ( t O iv T e f) A L i H N R
j Me B , DMSO
k Me
g
f
(cid:94)
GPT-4 without prior information, compound names GPT-4 without prior information, SMILES strings (cid:3)(cid:3)(cid:3)(cid:3)(cid:5)(cid:92)(cid:82)(cid:88)(cid:85)(cid:3)(cid:82)(cid:69)(cid:86)(cid:72)(cid:85)(cid:89)(cid:68)(cid:87)(cid:76)(cid:82)(cid:81)(cid:5)(cid:29)(cid:3)(cid:5)(cid:55)(cid:75)(cid:72)(cid:3)(cid:92)(cid:76)(cid:72)(cid:79)(cid:71)(cid:3)
(cid:75)(cid:68)(cid:86)(cid:3)(cid:76)(cid:80)(cid:83)(cid:85)(cid:82)(cid:89)(cid:72)(cid:71)(cid:3)(cid:69)(cid:88)(cid:87)(cid:3)(cid:81)(cid:82)(cid:87)(cid:3)(cid:86)(cid:76)(cid:74)(cid:81)(cid:76)(cid:73)(cid:76)(cid:70)(cid:68)(cid:81)(cid:87)(cid:79)(cid:92)(cid:17)(cid:3)
(cid:47)(cid:72)(cid:87)(cid:10)(cid:86)(cid:3)(cid:87)(cid:85)(cid:92)(cid:3)(cid:87)(cid:75)(cid:72)(cid:3)(cid:73)(cid:76)(cid:85)(cid:86)(cid:87)(cid:3)(cid:79)(cid:76)(cid:74)(cid:68)(cid:81)(cid:71)(cid:3)(cid:68)(cid:74)(cid:68)(cid:76)(cid:81)(cid:3)(cid:68)(cid:81)(cid:71)(cid:3) O N (cid:70)(cid:75)(cid:68)(cid:81)(cid:74)(cid:72)(cid:3)(cid:87)(cid:75)(cid:72)(cid:3)(cid:68)(cid:71)(cid:71)(cid:76)(cid:87)(cid:76)(cid:89)(cid:72)(cid:17)(cid:5)(cid:15)
(cid:3)(cid:3)(cid:3)(cid:3)(cid:5)(cid:79)(cid:76)(cid:74)(cid:68)(cid:81)(cid:71)(cid:5)(cid:29)(cid:3)
(cid:5)(cid:38)(cid:38)(cid:11)(cid:38)(cid:12)(cid:38)(cid:11)(cid:38)(cid:32)(cid:38)(cid:11)(cid:38)(cid:11)(cid:38)(cid:12)(cid:38)(cid:12)(cid:38)(cid:32)(cid:38)(cid:20)(cid:38)(cid:11)(cid:38)(cid:12)(cid:38)(cid:12)(cid:32)(cid:38)(cid:20)(cid:38)(cid:21)(cid:32)(cid:38)(cid:16)
(cid:38)(cid:32)(cid:38)(cid:38)(cid:32)(cid:38)(cid:21)(cid:51)(cid:11)(cid:38)(cid:11)(cid:38)(cid:12)(cid:11)(cid:38)(cid:12)(cid:38)(cid:12)(cid:38)(cid:11)(cid:38)(cid:12)(cid:11)(cid:38)(cid:12)(cid:38)(cid:5)(cid:15)
(cid:3)(cid:3)(cid:3)(cid:3)(cid:5)(cid:68)(cid:71)(cid:71)(cid:76)(cid:87)(cid:76)(cid:89)(cid:72)(cid:5)(cid:29)(cid:3)(cid:5)(cid:38)(cid:70)(cid:20)(cid:70)(cid:70)(cid:11)(cid:82)(cid:81)(cid:20)(cid:12)(cid:70)(cid:21)(cid:70)(cid:70)(cid:70)(cid:70)(cid:70)(cid:21)(cid:5)(cid:15)
(cid:3)(cid:3)(cid:3)(cid:3)(cid:5)(cid:69)(cid:68)(cid:86)(cid:72)(cid:5)(cid:29)(cid:3)(cid:5)(cid:38)(cid:49)(cid:20)(cid:38)(cid:38)(cid:38)(cid:49)(cid:21)(cid:38)(cid:38)(cid:38)(cid:49)(cid:32)(cid:38)(cid:20)(cid:21)(cid:5) (cid:96)
(cid:55)(cid:75)(cid:72)(cid:3)(cid:92)(cid:76)(cid:72)(cid:79)(cid:71)(cid:3)(cid:82)(cid:73)(cid:3)(cid:87)(cid:75)(cid:76)(cid:86)(cid:3)(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:3)(cid:76)(cid:86)(cid:3)(cid:23)(cid:20)(cid:8)
(cid:94)
(cid:3)(cid:3)(cid:3)(cid:3)(cid:5)(cid:92)(cid:82)(cid:88)(cid:85)(cid:3)(cid:82)(cid:69)(cid:86)(cid:72)(cid:85)(cid:89)(cid:68)(cid:87)(cid:76)(cid:82)(cid:81)(cid:5)(cid:29)(cid:3)(cid:5)(cid:55)(cid:75)(cid:72)(cid:3)(cid:92)(cid:76)(cid:72)(cid:79)(cid:71)(cid:3)
(cid:75)(cid:68)(cid:86)(cid:3)(cid:76)(cid:80)(cid:83)(cid:85)(cid:82)(cid:89)(cid:72)(cid:71)(cid:3)(cid:87)(cid:82)(cid:3)(cid:23)(cid:20)(cid:8)(cid:17)(cid:3)(cid:47)(cid:72)(cid:87)(cid:10)(cid:86)(cid:3)(cid:87)(cid:85)(cid:92)(cid:3)
(cid:68)(cid:81)(cid:82)(cid:87)(cid:75)(cid:72)(cid:85)(cid:3)(cid:68)(cid:71)(cid:71)(cid:76)(cid:87)(cid:76)(cid:89)(cid:72)(cid:3)(cid:87)(cid:75)(cid:68)(cid:87)(cid:3)(cid:75)(cid:68)(cid:86)(cid:3)(cid:68)(cid:3)(cid:86)(cid:87)(cid:85)(cid:82)(cid:81)(cid:74)(cid:72)(cid:85)(cid:3)
(cid:72)(cid:79)(cid:72)(cid:70)(cid:87)(cid:85)(cid:82)(cid:81)(cid:16)(cid:90)(cid:76)(cid:87)(cid:75)(cid:71)(cid:85)(cid:68)(cid:90)(cid:76)(cid:81)(cid:74)(cid:3)(cid:74)(cid:85)(cid:82)(cid:88)(cid:83)(cid:3)(cid:87)(cid:82)(cid:3)(cid:73)(cid:88)(cid:85)(cid:87)(cid:75)(cid:72)(cid:85)(cid:3)
(cid:76)(cid:81)(cid:70)(cid:85)(cid:72)(cid:68)(cid:86)(cid:72)(cid:3)(cid:87)(cid:75)(cid:72)(cid:3)(cid:92)(cid:76)(cid:72)(cid:79)(cid:71)(cid:17)(cid:5)(cid:15)
(cid:3)(cid:3)(cid:3)(cid:3)(cid:5)(cid:79)(cid:76)(cid:74)(cid:68)(cid:81)(cid:71)(cid:5)(cid:29)(cid:3) (cid:5)(cid:38)(cid:38)(cid:11)(cid:38)(cid:12)(cid:38)(cid:11)(cid:38)(cid:32)(cid:38)(cid:11)(cid:38)(cid:11)(cid:38)(cid:12)(cid:38)(cid:12)(cid:38)(cid:32)(cid:38)(cid:20)(cid:38)(cid:11)(cid:38)(cid:12)(cid:38)(cid:12)(cid:32)(cid:38)(cid:20)(cid:38)(cid:21)(cid:32)(cid:38)(cid:16)
(cid:38)(cid:32)(cid:38)(cid:38)(cid:32)(cid:38)(cid:21)(cid:51)(cid:11)(cid:38)(cid:11)(cid:38)(cid:12)(cid:11)(cid:38)(cid:12)(cid:38)(cid:12)(cid:38)(cid:11)(cid:38)(cid:12)(cid:11)(cid:38)(cid:12)(cid:38)(cid:5)(cid:15)
(cid:3)(cid:3)(cid:3)(cid:3)(cid:5)(cid:68)(cid:71)(cid:71)(cid:76)(cid:87)(cid:76)(cid:89)(cid:72)(cid:5)(cid:29)(cid:3)(cid:5)(cid:38)(cid:38)(cid:50)(cid:38)(cid:11)(cid:32)(cid:50)(cid:12)(cid:70)(cid:20)(cid:70)(cid:70)(cid:11)(cid:38)(cid:12)(cid:82)(cid:81)(cid:20)(cid:5)(cid:15)
(cid:3)(cid:3)(cid:3)(cid:3)(cid:5)(cid:69)(cid:68)(cid:86)(cid:72)(cid:5)(cid:29)(cid:3)(cid:5)(cid:38)(cid:49)(cid:20)(cid:38)(cid:38)(cid:38)(cid:49)(cid:21)(cid:38)(cid:38)(cid:38)(cid:49)(cid:32)(cid:38)(cid:20)(cid:21)(cid:5)
(cid:96)
(cid:55)(cid:75)(cid:72)(cid:3)(cid:92)(cid:76)(cid:72)(cid:79)(cid:71)(cid:3)(cid:82)(cid:73)(cid:3)(cid:87)(cid:75)(cid:76)(cid:86)(cid:3)(cid:85)(cid:72)(cid:68)(cid:70)(cid:87)(cid:76)(cid:82)(cid:81)(cid:3)(cid:76)(cid:86)(cid:3)(cid:24)(cid:19)(cid:8)
O
O
O
y – —1 Σ y i n j j
Normalized advantage = max y – —1 Σ y j j n j j
Average Bayesian optimization Random Maximum
N
Fig. 6 | Results of the optimization experiments. a, A general reaction values evaluated in c, left and centre panels. e, Reaction from the C–N crossscheme from the flow synthesis dataset analysed in c and d. b, The mathematical coupling dataset analysed in f and g. f, Comparison of two approaches
expression used to calculate normalized advantage values. c, Comparison of using compound names and SMILES string as compound representations.
the three approaches (GPT-4 with prior information, GPT-4 without prior g, Coscientist can reason about electronic properties of the compounds, even
information and GPT-3.5 without prior information) used to perform the when those are represented as SMILES strings. DMSO, dimethyl sulfoxide.
optimization process. d, Derivatives of the NMA and normalized advantage

---

<!-- Page 8 -->

about the outcome of the previous iteration. The only hard rule was
Discussion
for the player to provide its actions written in JavaScript Object Notation (JSON) format. If the JSON file could not be parsed, the player is In this paper, we presented a proof of concept for an artificial intelligent
alerted of its failure to follow the specified data format. The player had agent system capable of (semi-)autonomously designing, planning and
a maximum of 20 iterations (accounting for 5.2% and 6.9% of the total multistep executing scientific experiments. Our system demonstrates
space for the first and second datasets, respectively) to finish the game. advanced reasoning and experimental design capabilities, addressing
We evaluate Coscientist’s performance using the normalized advan- complex scientific problems and generating high-quality code. These
tage metric (Fig. 6b). Advantage is defined as the difference between a capabilities emerge when LLMs gain access to relevant research tools,
given iteration yield and the average yield (advantage over a random such as internet and documentation search, coding environments
strategy). Normalized advantage measures the ratio between advantage and robotic experimentation platforms. The development of more
and maximum advantage (that is, the difference between the maximum integrated scientific tools for LLMs has potential to greatly accelerate
and average yield). The normalized advantage metric has a value of new discoveries.
one if the maximum yield is reached, zero if the system exhibits com- The development of new intelligent agent systems and automated
pletely random behaviour and less than zero if the performance at methods for conducting scientific experiments raises potential conthis step is worse than random. An increase in normalized advantage cerns about the safety and potential dual-use consequences, particuover each iteration demonstrates Coscientist’s chemical reasoning larly in relation to the proliferation of illicit activities and security
capabilities. The best result for a given iteration can be evaluated using threats. By ensuring the ethical and responsible use of these powthe normalized maximum advantage (NMA), which is the normalized erful tools, we are continuing to explore the vast potential of LLMs
value of the maximum advantage achieved until the current step. As in advancing scientific research while mitigating the risks associ-
NMA cannot decrease, the valuable observations come in the form ated with their misuse. A brief dual-use study of Coscientist is proof the rate of its increase and its final point. Finally, during the first vided in Supplementary Information section ‘Safety implications:
step, the values for NMA and normalized advantage equal each other, Dual-use study’.
portraying the model’s prior knowledge (or lack thereof) without any
data being collected. Technology use disclosure
For the Suzuki dataset, we compared three separate approaches: (1) The writing of the preprint version of this manuscript was assisted by
GPT-4 with prior information included in the prompt (which consisted ChatGPT (specifically, GPT-4 being used for grammar and typos). All
of 10 yields from random combinations of reagents); (2) GPT-4; or (3) authors have read, corrected and verified all information presented in
GPT-3.5 without any prior information (Fig. 6c). When comparing GPT-4 this manuscript and Supplementary Information.
with the inclusion and exclusion of prior information, it is clear that
the initial guess for the former scenario is better, which aligns with
Online content
our expectations considering the provided information about the
system’s reactivity. Notably, when excluding prior information, there Any methods, additional references, Nature Portfolio reporting summaare some poor initial guesses, whereas there are none when the model ries, source data, extended data, supplementary information, acknowlhas prior information. However, at the limit, the models converge to edgements, peer review information; details of author contributions
the same NMA. The GPT-3.5 model plots have a very limited number and competing interests; and statements of data and code availability
of data points, primarily because of its inability to output messages are available at https://doi.org/10.1038/s41586-023-06792-0.
in the correct JSON schema as requested in the prompt. It is unclear if
the GPT-4 training data contain any information from these datasets.
If so, one would expect that the initial model guess would be better 1. Brown, T. et al. in Advances in Neural Information Processing Systems Vol. 33
than what we observed. (eds Larochelle, H. et al.) 1877–1901 (Curran Associates, 2020).
2. Thoppilan, R. et al. LaMDA: language models for dialog applications. Preprint at
The normalized advantage values increase over time, suggesting that https://arxiv.org/abs/2201.08239 (2022).
the model can effectively reuse the information obtained to provide 3. Touvron, H. et al. LLaMA: open and efficient foundation language models. Preprint at
more specific guidance on reactivity. Evaluating the derivative plots https://arxiv.org/abs/2302.13971 (2023).
4. Hoffmann, J. et al. Training compute-optimal large language models. In Advances in
(Fig. 6d) does not show any significant difference between instances Neural Information Processing Systems 30016–30030 (NeurIPS, 2022).
with and without the input of prior information. 5. Chowdhery, A. et al. PaLM: scaling language modeling with pathways. J. Mach. Learn.
There are many established optimization algorithms for chemical Res. 24, 1–113 (2022).
6. Lin, Z. et al. Evolutionary-scale prediction of atomic-level protein structure with a
reactions. In comparison with standard Bayesian optimization52, both language model. Science 379, 1123–1130 (2023).
GPT-4-based approaches show higher NMA and normalized advantage 7. Luo, R. et al. BioGPT: generative pre-trained transformer for biomedical text generation
and mining. Brief Bioinform. 23, bbac409 (2022).
values (Fig. 6c). A detailed overview of the exact Bayesian optimization
8. Irwin, R., Dimitriadis, S., He, J. & Bjerrum, E. J. Chemformer: a pre-trained transformer for
strategy used is provided in Supplementary Information section ‘Bayes- computational chemistry. Mach. Learn. Sci. Technol. 3, 015022 (2022).
ian optimization procedure’. It is observed that Bayesian optimization’s 9. Kim, H., Na, J. & Lee, W. B. Generative chemical transformer: neural machine learning
of molecular geometric structures from chemical language via attention. J. Chem. Inf.
normalized advantage line stays around zero and does not increase
Model. 61, 5804–5814 (2021).
over time. This may be caused by different exploration/exploitation 10. Jablonka, K. M., Schwaller, P., Ortega-Guerrero, A. & Smit, B. Leveraging large language
balance for these two approaches and may not be indicative of their models for predictive chemistry. Preprint at https://chemrxiv.org/engage/chemrxiv/
article-details/652e50b98bab5d2055852dde (2023).
performance. For this purpose, the NMA plot should be used. Changing
11. Xu, F. F., Alon, U., Neubig, G. & Hellendoorn, V. J. A systematic evaluation of large
the number of initial samples does not improve the Bayesian optimiza- language models of code. In Proc. 6th ACM SIGPLAN International Symposium on
tion trajectory (Extended Data Fig. 3a). Finally, this performance trend Machine Programming 1–10 (ACM, 2022).
12. Nijkamp, E. et al. CodeGen: an open large language model for code with multi-turn
is observed for each unique substrate pairings (Extended Data Fig. 3b).
program synthesis. In Proc. 11th International Conference on Learning Representations
For the Buchwald–Hartwig dataset (Fig. 6e), we compared a version (ICLR, 2022).
of GPT-4 without prior information operating over compound names 13. Kaplan, J. et al. Scaling laws for neural language models. Preprint at https://arxiv.org/
abs/2001.08361 (2020).
or over compound SMILES strings. It is evident that both instances
14. OpenAI. GPT-4 Technical Report (OpenAI, 2023).
have very similar performance levels (Fig. 6f). However, in certain 15. Ziegler, D. M. et al. Fine-tuning language models from human preferences. Preprint at
scenarios, the model demonstrates the ability to reason about the https://arxiv.org/abs/1909.08593 (2019).
16. Ouyang, L. et al. Training language models to follow instructions with human
reactivity of these compounds simply by being provided their SMILES
feedback. In Advances in Neural Information Processing Systems 27730–27744
strings (Fig. 6g). (NeurIPS, 2022).
Nature | Vol 624 | 21/28 December 2023 | 577

---

<!-- Page 9 -->

Article
17. Granda, J. M., Donina, L., Dragone, V., Long, D.-L. & Cronin, L. Controlling an organic 40. Qadrud-Din, J. et al. Transformer based language models for similar text retrieval and
synthesis robot with machine learning to search for new reactivity. Nature 559, 377–381 ranking. Preprint at https://arxiv.org/abs/2005.04588 (2020).
(2018). 41. Paper QA. GitHub https://github.com/whitead/paper-qa (2023).
18. Caramelli, D. et al. Discovering new chemistry with an autonomous robotic platform 42. Robertson, S. & Zaragoza, H. The probabilistic relevance framework: BM25 and beyond.
driven by a reactivity-seeking neural network. ACS Cent. Sci. 7, 1821–1830 (2021). Found. Trends Inf. Retrieval 3, 333–389 (2009).
19. Angello, N. H. et al. Closed-loop optimization of general reaction conditions for heteroaryl 43. Data Mining. Mining of Massive Datasets (Cambridge Univ., 2011).
Suzuki–Miyaura coupling. Science 378, 399–405 (2022). 44. Johnson, J., Douze, M. & Jegou, H. Billion-scale similarity search with GPUs. IEEE Trans.
20. Adamo, A. et al. On-demand continuous-flow production of pharmaceuticals in a compact, Big Data 7, 535–547 (2021).
reconfigurable system. Science 352, 61–67 (2016). 45. Vechtomova, O. & Wang, Y. A study of the effect of term proximity on query expansion.
21. Coley, C. W. et al. A robotic platform for flow synthesis of organic compounds informed J. Inf. Sci. 32, 324–333 (2006).
by AI planning. Science 365, eaax1566 (2019). 46. Running experiments. Emerald Cloud Lab https://www.emeraldcloudlab.com/guides/
22. Burger, B. et al. A mobile robotic chemist. Nature 583, 237–241 (2020). runningexperiments (2023).
23. Auto-GPT: the heart of the open-source agent ecosystem. GitHub https://github.com/ 47. Sanchez-Garcia, R. et al. CoPriNet: graph neural networks provide accurate and
Significant-Gravitas/AutoGPT (2023). rapid compound price prediction for molecule prioritisation. Digital Discov. 2, 103–111
24. BabyAGI. GitHub https://github.com/yoheinakajima/babyagi (2023). (2023).
25. Chase, H. LangChain. GitHub https://github.com/langchain-ai/langchain (2023). 48. Bubeck, S. et al. Sparks of artificial general intelligence: early experiments with GPT-4.
26. Bran, A. M., Cox, S., White, A. D. & Schwaller, P. ChemCrow: augmenting large-language Preprint at https://arxiv.org/abs/2303.12712 (2023).
models with chemistry tools. Preprint at https://arxiv.org/abs/2304.05376 (2023). 49. Ramos, M. C., Michtavy, S. S., Porosoff, M. D. & White, A. D. Bayesian optimization of
27. Liu, P. et al. Pre-train, prompt, and predict: a systematic survey of prompting methods in catalysts with in-context learning. Preprint at https://arxiv.org/abs/2304.05341 (2023).
natural language processing. ACM Comput. Surv. 55, 195 (2021). 50. Perera, D. et al. A platform for automated nanomole-scale reaction screening and
28. Bai, Y. et al. Constitutional AI: harmlessness from AI feedback. Preprint at https://arxiv.org/ micromole-scale synthesis in flow. Science 359, 429–434 (2018).
abs/2212.08073 (2022). 51. Ahneman, D. T., Estrada, J. G., Lin, S., Dreher, S. D. & Doyle, A. G. Predicting reaction
29. Falcon LLM. TII https://falconllm.tii.ae (2023). performance in C–N cross-coupling using machine learning. Science 360, 186–190
30. Open LLM Leaderboard. Hugging Face https://huggingface.co/spaces/HuggingFaceH4/ (2018).
open_llm_leaderboard (2023). 52. Hickman, R. et al. Atlas: a brain for self-driving laboratories. Preprint at https://chemrxiv.
31. Ji, Z. et al. Survey of hallucination in natural language generation. ACM Comput. Surv. 55, org/engage/chemrxiv/article-details/64f6560579853bbd781bcef6 (2023).
248 (2023).
32. Reaxys https://www.reaxys.com (2023). Publisher’s note Springer Nature remains neutral with regard to jurisdictional claims in
33. SciFinder https://scifinder.cas.org (2023). published maps and institutional affiliations.
34. Yao, S. et al. ReAct: synergizing reasoning and acting in language models. In Proc.11th
International Conference on Learning Representations (ICLR, 2022). Open Access This article is licensed under a Creative Commons Attribution
35. Wei, J. et al. Chain-of-thought prompting elicits reasoning in large language models. 4.0 International License, which permits use, sharing, adaptation, distribution
In Advances in Neural Information Processing Systems 24824–24837 (NeurIPS, 2022). and reproduction in any medium or format, as long as you give appropriate
36. Long, J. Large language model guided tree-of-thought. Preprint at https://arxiv.org/ credit to the original author(s) and the source, provide a link to the Creative Commons licence,
abs/2305.08291 (2023). and indicate if changes were made. The images or other third party material in this article are
37. Opentrons Python Protocol API. Opentrons https://docs.opentrons.com/v2/ (2023). included in the article’s Creative Commons licence, unless indicated otherwise in a credit line
38. Tu, Z. et al. Approximate nearest neighbor search and lightweight dense vector reranking to the material. If material is not included in the article’s Creative Commons licence and your
in multi-stage retrieval architectures. In Proc. 2020 ACM SIGIR on International intended use is not permitted by statutory regulation or exceeds the permitted use, you will
Conference on Theory of Information Retrieval 97–100 (ACM, 2020). need to obtain permission directly from the copyright holder. To view a copy of this licence,
39. Lin, J. et al. Pyserini: a python toolkit for reproducible information retrieval research with visit http://creativecommons.org/licenses/by/4.0/.
sparse and dense representations. In Proc. 44th International ACM SIGIR Conference on
Research and Development in Information Retrieval 2356–2362 (ACM, 2021). © The Author(s) 2023
578 | Nature | Vol 624 | 21/28 December 2023

---

<!-- Page 10 -->

to Y. Benslimane, H. Gronlund, B. Smith and B. Frezza) for assisting us with parsing their
Data availability documentation and executing experiments. G.G. is grateful to the Carnegie Mellon University
Cloud Lab Initiative led by the Mellon College of Science for its vision of the future of physical
Examples of the experiments discussed in the text are provided in the sciences. G.G. thanks Carnegie Mellon University; the Mellon College of Sciences and its
Supplementary Information. Because of safety concerns, data, code Department of Chemistry; and the College of Engineering and its Department of Chemical
Engineering for the start-up support. D.A.B. was partially funded by the National Science
and prompts will be only fully released after the development of US
Foundation Center for Chemoenzymatic Synthesis (Grant no. 2221346). R.M. was funded by
regulations in the field of artificial intelligence and its scientific appli- the National Science Foundation Center for Computer-Assisted Synthesis (Grant no. 2202693).
cations. Nevertheless, the outcomes of this work can be reproduced
using actively developed frameworks for autonomous agent develop- Author contributions D.A.B. designed the computational pipeline and developed the ‘Planner’,
‘Web searcher’ and ‘Code execution’ modules. R.M. assisted in designing the computational
ment. The reviewers had access to the web application and were able pipeline and developed the ‘Docs searcher’ module. B.K. analysed the behaviours of the Docs
to verify any statements related to this work. Moreover, we provide a searcher module to enable Coscientist to produce experiment code in Emerald Cloud Lab’s
simpler implementation of the described approach, which, although Symbolic Lab Language. D.A.B. assisted and oversaw Coscientist’s chemistry experiments.
D.A.B., R.M. and G.G. designed and performed initial computational safety studies. D.A.B.
it may not produce the same results, allows for deeper understanding designed and graded Coscientist’s synthesis capabilities study. D.A.B. co-designed with G.G.
of the strategies used in this work. and performed the optimization experiments. R.M. performed the large compound library
experiment and Bayesian optimization baseline runs. G.G. designed the concepts, performed
preliminary studies and supervised the project. D.A.B., R.M. and G.G. wrote this manuscript.
Code availability Competing interests G.G. is part of the AI Scientific Advisory Board of Emerald Cloud Lab.
Simpler implementation as well as generated outputs used for quan- Experiments and conclusions in this manuscript were made before G.G.’s appointment to this
role. B.K. is an employee of Emerald Cloud Lab. D.A.B. and G.G. are co-founders of aithera.ai,
titative analysis are provided at https://github.com/gomesgroup/ a company focusing on responsible use of artificial intelligence for research.
coscientist.
Additional information
Supplementary information The online version contains supplementary material available at
Acknowledgements We thank the following Carnegie Mellon University Chemistry groups https://doi.org/10.1038/s41586-023-06792-0.
for their assistance with providing the chemicals needed for the Coscientist’s experiments: Correspondence and requests for materials should be addressed to Gabe Gomes.
Sydlik, Garcia Borsch, Matyjaszewski and Ly. We give special thanks to the Noonan group Peer review information Nature thanks Sebastian Farquhar, Tiago Rodrigues and the other,
(K. Noonan and D. Sharma) for providing access to chemicals and gas chromatography–mass anonymous, reviewer(s) for their contribution to the peer review of this work.
spectrometry analysis. We also thank the team at Emerald Cloud Lab (with special attention Reprints and permissions information is available at http://www.nature.com/reprints.

---

<!-- Page 11 -->

Article
Extended Data Fig. 1 | Using UV-Vis and liquid handler to solve food colouring preparation is generated, resulting data is provided as NumPy array, which is
identification problem. Guiding prompt in the third message is shown in then analysed to give the final answer.
bold. In the first message the user prompt is provided, then code for sample

---

<!-- Page 12 -->

Extended Data Fig. 2 | Code, generated by Coscientist. The generated code transfers, setting up the heater-shaker module, running the reaction, and
can be split into the following steps: defining metadata for the method, loading turning the module off.
labware modules, setting up the liquid handler, performing required reagent

---

<!-- Page 13 -->

Article
Extended Data Fig. 3 | Additional results on comparison with Bayesian optimization. a, GPT-4 models compared with Bayesian optimization performed
starting with different number of initial samples. b, Compound-by-compound comparison of differences between advantages.
