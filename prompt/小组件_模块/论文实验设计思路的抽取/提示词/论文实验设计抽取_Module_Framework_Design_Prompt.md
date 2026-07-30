\# Task:

\# Design the Framework Architecture for "论文实验设计抽取" Module



\## Background



We are building a Synthetic Biology DBTL Engineering OS.



One major module is:



"论文实验设计抽取"



Goal:



Automatically transform scientific papers into structured, evidence-linked, K12-adaptable experimental design knowledge.



This module is NOT a simple literature summarizer.



It must satisfy:



\- traceability

\- provenance

\- human governance

\- structured data exchange

\- minimal hallucination

\- reproducibility





\---



\# Objective



Before implementing individual Skills, first design the complete module framework.



Do NOT implement the 13 Skills yet.



Only build:



1\. Architecture

2\. Data Model

3\. Workflow State Machine

4\. Skill Interface Specification

5\. Logging System

6\. Error Handling System

7\. Human Review System

8\. Testing Framework





\---



\# Module Name



论文实验设计抽取





\---



\# Overall Workflow





User Input



↓



Research Intent Parsing



↓



Literature Retrieval



↓



Citation Validation



↓



PDF Acquisition



↓



PDF Parsing



↓



Markdown Cleaning



↓



Experimental Design Extraction



↓



Evidence Binding



↓



Quality Evaluation



↓



K12 Transfer Analysis



↓



Engineering Experiment Proposal



↓



QC + Human Review



↓



Frontend Presentation





\---



\# Required Skills





\## Skill0 Framework Layer



Responsible for:



\- unified schema

\- workflow state machine

\- logging

\- error codes

\- provenance

\- human review interface

\- memory interface





\## Skill1



用户需求解析与检索策略生成





Output:



Research Intent Object





Fields:



\- organism

\- strain

\- phenotype

\- engineering objective

\- keywords

\- inclusion criteria

\- exclusion criteria





\---



\## Skill2



Literature Retrieval





Support:



\- PubMed

\- Crossref

\- Europe PMC

\- Google Scholar

\- Web of Science

\- CNKI





Output:



Literature Candidate Object





\---



\## Skill3



Citation Validation





Check:



\- DOI existence

\- title consistency

\- author consistency

\- journal consistency

\- year consistency





Maximum retry:



3 times





\---



\## Skill4



PDF Acquisition





Need:



\- source tracking

\- checksum

\- version control





\---



\## Skill5



PDF Reconstruction





Convert PDF to structured markdown.



Preserve:



\- sections

\- figures

\- tables

\- references

\- supplement





\---



\## Skill6



Scientific Markdown Cleaning





Must:



\- remove headers/footers

\- repair tables

\- preserve citations

\- preserve figure/table numbering

\- preserve hierarchy





\---



\## Skill7



Experimental Design Extraction





Extract:



\- objective

\- hypothesis

\- strain

\- genotype

\- engineering method

\- experimental groups

\- controls

\- culture conditions

\- medium

\- dosage

\- time

\- replicates

\- assay

\- instruments

\- analysis methods

\- outcomes





No hallucination.



Unknown must remain unknown.





\---



\## Skill8



Evidence Binding





Every field must contain:



\- source location

\- extraction method

\- confidence

\- status





Allowed status:



\- reported

\- unknown

\- inferred





\---



\## Skill9



Quality Evaluation





Evaluate:



\- completeness

\- reproducibility

\- evidence level

\- missing information

\- extraction confidence





\---



\## Skill10



K12 Adaptation





Compare:



\- strain difference

\- engineering strategy

\- advantages

\- limitations

\- transferability risk





\---



\## Skill11



Engineering Experiment Proposal





Must separate:



Literature Experiment



and



AI Engineering Proposal





\---



\## Skill12



QC and Human Governance





Requirements:



\- automatic validation

\- human review queue

\- pipeline continues during review

\- all decisions logged





\---



\## Skill13



Frontend Adaptation





Output:



Frontend-ready schema.



Default:



Show concise experimental steps.



Expandable:



What

Why

How



Evidence



Risk



Alternative





\---



\# Global Requirements





Every Skill MUST have:



1\. Input Schema



2\. Output Schema



3\. Self-check mechanism



4\. Logging mechanism



5\. Error handling



6\. Test cases





\---



\# Hallucination Prevention





When information is unavailable:



Return:



unknown



or



empty value





Never infer missing experimental parameters.





\---



\# Provenance Requirement





Every important scientific statement should be traceable to:



\- paper

\- page

\- paragraph

\- figure

\- table





\---



\# Testing Requirement





Create testing framework including:



\- normal cases

\- missing information cases

\- invalid DOI cases

\- conflicting evidence cases

\- parsing failure cases

\- hallucination tests





\---



\# Final Deliverable





Create:



1\. Module architecture document



2\. Unified schema design



3\. Skill interface specification



4\. Workflow diagram



5\. State machine



6\. Logging design



7\. Error code system



8\. Human review design



9\. Testing framework





Do not implement individual Skills yet.



Only prepare the foundation for future Skill development.

