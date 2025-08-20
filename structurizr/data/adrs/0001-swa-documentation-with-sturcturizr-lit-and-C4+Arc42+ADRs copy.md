# SWA documentation with Structurizr lite and C4+Arc42+ADRs

Date: 2025-08-04

## Status

ACCEPTED    

## Context

We need to document software architecture. Creating a template&process and finding tools that can be used across projects will set clear expectations of quality and structure and make it easier to create quality documentation. This project will be a test-run for it

Criteria: 
- Code-based for easier versioning and maintainability
- Template must specify the content a SWA documentation must have
- Template must specify the tooling used to create this documentation
- Learning to utilize the tools must be as easy as possible to assure adaption
- Creating the documentation utilizing the tools must be as frictionless and fast as possible
- The structure the template gives must be of high quality and include all parts usually expected of a SWA document

## Decision

We will use a minimalistic combination of the arc42 template for SWA documentation together with the code based diagramming C4 tool Structurizr lite. The ADRs will not be added to the Arc42 document but to structurizr lite directly, and all diagrams will be created via structurizr dsl and embedded into the document.


## Consequences

Every technical stakeholder must familiarize themselves with utilizing arc42+structurizr lite+ ADRs. 
Albert must create documentation for this.
We have a default structure of SWA docs leading to consistent SWA documentation standards.
We have a nice and easily readable UI for SWA documentation including ADRs and interactive diagrams.
Creating and maintaing diagrams is fast.