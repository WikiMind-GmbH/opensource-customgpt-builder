# Why SWA Documentation
Documenting Software Architecture and Sofware Architecture Decisions brings many advantages for multiple stakeholders.   
Everyone, including from technical to non-technical people can get a basic understanding of the Software System, its requirements and architecture in multiple depths.  
- Management can quickly get a high-level view of the architecture and its goals 
- the Product owner or Tech lead will be able to see the Architecture and the reasoning behind Architecture decisions and their development over time
- New developers will be able to quickly understand the software system without a deep dive into the code and the explicitly documented constraints and decisions will enable them to create code in accordance to the teams previous decisions.

## Arc42
[ARC42 examples](https://arc42.org/examples#online-examples)
## Architecture Decision Records (ADRS)
[ADR Blogpost](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

[adr-tools cli tool](https://github.com/npryce/adr-tools/blob/master/doc/adr/0002-implement-as-shell-scripts.md) could make the creation easier and automate Status updates


## Structurizr
### Creating SWA Document in Structurizr

#### Integrate markdown or Asciidoc file(s)
In your workspace.dsl, you can write `!docs ${docs_foldername}` to include all Markdown and AsciiDoc files of the folder `{docs_foldername}` residing in the same directory as the workspace.dsl file.

Chapters are created from ## and ### headers and linked automatically in the structurizr UI.    
You can include live diagrams/views in the documentation. via `![](embed:MyDiagramKey)`in .md and `image::embed:MyDiagramKey[]` in .ascii

[SWA Document integration](https://docs.structurizr.com/ui/documentation/)

#### Architecture Decision Records integration
There is a good integration of Architecture Decision Records into the structurizr UI so *it is strongly adviced to use this functionality instead of directly documenting the ADRs in the document*.
[ADRs in StructuriztUI](https://docs.structurizr.com/ui/decisions/)

## Arc42


# Resources

## Structurizr
#### 

## Arc42