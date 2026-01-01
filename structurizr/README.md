# Software Architecture Documentation (SWA)

## Viewing the documentation

1. Start the `structurizr-lite` container of `docker-compose.dev.yaml`.
2. Go to http://localhost:8080

## Why We Document Software Architecture (SWA)

Documenting Software Architecture and Architecture Decisions provides lasting value for **technical and non-technical stakeholders**. Good documentation makes the system easier to understand, evolve, and maintain.

### Benefits

* **Management / Stakeholders**
  Quickly see the high-level structure, goals, boundaries, and constraints of the system.

* **Product Owners / Tech Leads**
  Understand the architecture *and* the reasoning behind decisions, including how they evolved over time.

* **New Developers**
  Ramp up significantly faster by understanding the system context, domain boundaries, architectural style, and explicit design constraints — *without needing to read the entire codebase first*.

> **Good architecture documentation reduces onboarding time, improves consistency, and enables better long-term maintainability.**

To ensure quality across teams and projects, we define:

* a **template**, and
* a **tooling setup**

for writing Software Architecture Documentation.

### Our Criteria

The documentation approach must be:

* **Code-based** → fully versioned, reviewed via pull requests, reproducible
* **Template-driven** → clear expectations of what a SWA document must contain
* **Tool-supported** → simple to create & maintain plus pretty to look at and easy to navigate the documentation
* **Fast to learn** → should not require specialized tools or steep learning curves
* **High quality by default** → including all sections typically expected in a professional SWA document
* **Aligned with modern architecture documentation practices** → C4 model, ADRs, structured narratives

---

## Our solution: ARC42 + structurizr-lite incl. ADRs

Based on these criteria, we combine the ARC42 SWA documentation template with the structurizr-lite tool to create a structured, maintainable, and developer-friendly architecture documentation stack.

- ARC42 defines what a complete architecture document should contain (and includes ADRs)
- Architecture Decision Records (ADRs) capture why decisions were made.
- structurizr-lite provides the tooling to render documentation, diagrams, and ADRs.
- Structurizr DSL defines architecture models and views(=diagrams) of this model as code.

The following sections explain the concepts and reasoning behind this approach; practical setup and learning resources are covered later in this document.


### ARC42 — The SWA Document Template

**ARC42** is a widely used template for documenting software architectures.
It defines *what* a complete architecture document should contain:

* system goals, constraints
* the most important (non) functional requirements
* context and scope
* building blocks
* runtime scenarios
* cross-cutting concepts
* risk, quality, and design decisions

It is purely a **documentation structure**.
ARC42 Template Overview: [https://arc42.org/overview](https://arc42.org/overview)
ARC42 example documents: [https://arc42.org/examples#online-examples](https://arc42.org/examples#online-examples)

It ensures that important topics are covered systematically, while still allowing teams to keep individual sections lightweight where appropriate.

>ARC42 answers the question:   
“What information should a professional software architecture document contain?”

---

### structurizr-lite — Code-Based C4 Diagrams + Integrated Documentation

structurizr-lite is a lightweight, self-hosted web application for **viewing and navigating software architecture documentation**.

It renders:
* **C4 model views(=diagrams)** (static, dynamic, deployment)
* **Documentation** written in (extended) Markdown or AsciiDoc, which can include interactive C4 views(=diagrams)
* **Architecture Decision Records (ADRs)**

It provides an UI to:
* **adjust the layout of the views(=diagrams)** and saves those changes inside a `.json` alongside the code

All inputs to structurizr-lite are **code-based and version-controlled**:

* architecture models and views are defined using the Structurizr DSL
* documentation and ADRs are written in markdown (or AsciiDoc) and **live alongside the source code**

This enables architecture documentation that is:

* reviewable via pull requests
* tightly coupled to the actual system evolution



---

### Structurizr DSL

#### The **Structurizr DSL** (“Domain-Specific Language”) is a concise, code-based way of defining:

**The C4 model** of our software system, detailing:
* people, software systems, containers, and components
* relationships between them

**Views(diagrams) of this model:**
* static views ([system context](https://docs.structurizr.com/dsl/cookbook/system-context-view/#system-context-view), [container](https://docs.structurizr.com/dsl/cookbook/container-view/), [component](https://docs.structurizr.com/dsl/cookbook/component-view/), dynamic)
* [dynamic](https://docs.structurizr.com/dsl/cookbook/dynamic-view/) views (e.g.. runtime views of user strories)
* [deployment](https://docs.structurizr.com/dsl/cookbook/deployment-view/) views

Additionally, Structurizr DSL is used to **define imports for**
* [SWA Documentation](https://docs.structurizr.com/dsl/docs) and [ADR](https://docs.structurizr.com/dsl/adrs) imports, to view in the structurizr-lite web UI. 

#### Its features:
It is **simple, readable, Git-friendly**, and produces fully interactive diagrams inside **Structurizr Lite**.

A crucial aspect of Structurizr DSL is that **it is model-based, not view-based**.

Instead of drawing diagrams directly, we:

1. **Define a single, coherent architecture model** (people, systems, containers, components, relationships).
2. **Generate multiple views from that model** (system context, container view, component views, dynamic views, etc.).

This has important consequences:

* All diagrams **automatically stay consistent**, because they come from the same underlying model.
* Unlike traditional “drawn” diagrams (e.g., draw.io, Lucidchart), there is **no risk of diverging diagrams** that contradict each other over time.
* Architecture documentation scales better as systems grow and change.

> The model is the single source of truth.   
Diagrams are just different views of that truth.   

This is fundamentally different from manually drawn diagrams, where individual diagrams can easily drift apart or become outdated independently, making the documentation **trustworthy, maintainable, and scalable**.


#### Official Resources

* DSL reference: [https://docs.structurizr.com/dsl](https://docs.structurizr.com/dsl)
* C4 model overview: [https://c4model.com](https://c4model.com)
* Our internal *Video tutorial*: [https://nextcloud.wikimind.de/index.php/apps/files/files/3132?dir=/WikiMind%20Share/Knowledge%20base/Tutorial%20Videos/ARC42%2BStructurizr](https://nextcloud.wikimind.de/index.php/apps/files/files/3132?dir=/WikiMind%20Share/Knowledge%20base/Tutorial%20Videos/ARC42%2BStructurizr)

Quick recap:   
> **Structurizr DSL** = a code-based format for defining architecture models and diagrams.
> **Structurizr Lite** = a runtime that reads Structurizr DSL + Markdown → displays the complete architecture doc.

### Architecture Decision Records (ADRs)

ADRs document **why** architectural decisions were made, which constraints existed, what alternatives were considered, and what consequences the decision has.

To streamline creation and status management of ADRs (e.g. deprication relationships), we always use "[adr-tools](https://github.com/npryce/adr-tools)" cli tool to create new adrs.  

With it, we can simply mark previous adrs as superseded by a new one.
For example, this creates a new adr named `modulith`, which supersedes the adrs number three and five. 
```.sh
adr new -s 3 -s 5 modulith
```
With that, a new adr named modulith is created, and the adrs three and five are marked as being superseded by the new one.   
```
Superceded by [16. Modulith](0016-modulith.md)
```
This is official formatting and picked up in the structurizr-lite UIs ADR viewer and Decision tree viewer.


>*For windows user: you must install and use adr-tools via the WSL git bash*

#### Recommended Reading

* Original ADR blog post: [https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
* adr-tools format examples: [https://github.com/npryce/adr-tools/blob/master/doc/adr/0002-implement-as-shell-scripts.md](https://github.com/npryce/adr-tools/blob/master/doc/adr/0002-implement-as-shell-scripts.md)
* [adr-tools github repo](https://github.com/npryce/adr-tools)
* Structurizr ADR integration: [https://docs.structurizr.com/ui/decisions/](https://docs.structurizr.com/ui/decisions/)
* [Our previous tutorial on SWA with structurizr-lite](https://github.com/WikiMind-GmbH/structurizr-arc42-template?tab=readme-ov-file#software-architecture-documentation-with-arc42-and-structurizr-lite) 



## Structurizr-lite: Creating and maintaining SWA docs

### What the different components are and where we organise them

Our Structurizr-lite tool has one central file - `workspace.dsl`, whose content is the sole determinant for what we can see when we view our SWA in the Structurizr Web App. Here, all components are either explicitly defined in, or linked.

#### The C4 model and its views(=diagrams)
Are explicitly defined in `workspace.dsl`. Layout changes made to views in the web UI are read from and written to the `workspace.json` file.

* all Markdown/AsciiDoc files in the `docs/` folder
* all ADRs in the `adr/` folder

and render the complete:

* ARC42 documentation
* interactive C4 diagrams
* ADR timeline + navigation
* dynamic views

No build step is needed — changes update immediately.

---

### Creating SWA Documentation in Structurizr Lite

#### 1. Organizing Documentation Files

We place ARC42 chapters in the `docs/` directory as Markdown or AsciiDoc files.

Each file is named:

```
NN-<CHAPTER_NAME>.md
```

Example:

```
01-Introduction and Goals.md
03-System Scope and Context.md
05-Building Block View.md
```

#### 2. Headings and Structurizr Navigation

Structurizr expects:

* Each chapter file to start with the chapter title as an **H2 heading (`##`)**
  → not `#` (H1). Structurizr reserves H1 for top-level document metadata.

Example:

```md
## Building Block View – C4 System Context View
![](embed:SystemContextView)

### Whitebox Overall System — C4 Container Views
![](embed:ContainerView)

### Level 2 – C4 Component Views
#### ChatService
```

Rules:

* Use `##` for chapter start.
* Use `###` and `####` to structure content.
* H2 and H3 headings appear in Structurizr's navigation sidebar.

#### 3. Embedding Diagrams

You can embed diagrams you defined in `workspace.dsl` by referencing Structurizr DSL view keys:

* Markdown:

  ```md
  ![](embed:MyDiagramKey)
  ```

* AsciiDoc:

  ```adoc
  image::embed:MyDiagramKey[]
  ```

#### 4. Linking Documentation to the Workspace

Inside `workspace.dsl`, we point Structurizr to the docs folder:

```dsl
!docs docs
```

Structurizr Lite automatically displays the chapters in the UI.

More info:
[https://docs.structurizr.com/ui/documentation/](https://docs.structurizr.com/ui/documentation/)

---

### ADR Workflow

We manage ADRs **separately from the ARC42 doc** using Structurizr Lite’s dedicated UI.

Reasons:

* ADRs evolve over time (supersessions)
* ADRs are decision-focused, not narrative-focused
* Structurizr provides filtering, linking, status tracking, and automatic navigation

### Creating ADRs

We use **ADR Tools CLI** to create ADRs in a consistent format:

```bash
adr new "Decision title here"
```

This produces files like:

```
adr/
  0001-use-structurizr-adrs.md
  0002-decouple-authentication.md
```

We can mark a new adr to supercede previous ones:
```bash
adr new -s ${NumberOfADRToSupercede} Decision title here
```
e.g.
```bash
adr new -s 3 Modulith
```

### Importing ADRs into Structurizr

In `workspace.dsl`:

```dsl
!adrs adr
```

Structurizr Lite automatically imports, displays, and links the ADRs.

### Editing ADRs — Our Team Policy

* **Proposed/Open ADRs** may be edited freely.
* **Accepted ADRs** are immutable; to change one, create a new ADR that *supersedes* the previous one.
* Only stylistic or formatting corrections should be applied to accepted ADRs.