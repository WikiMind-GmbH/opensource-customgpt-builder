## Introduction and Goals

This document describes the Opensource CustomGPT Builder Software system. It can be used to create your own CustomGPTs outside of the OpenAI Software System.   
The goal of this system is to have a baseline product onto which we can build more customized solutions for clients. The aim is to have a product that targets a broad audience. We hope that this makes for broader adaption of our products and lead to more follow-up projects.  
The goal this system achives for the users is the following:   
They want to use the capabilities of CustomGPTs without directly giving their data to OpenAI while still getting a very simimalar user experience.  
(Requirements describe what the system should do. Goals describe how the system will help the organization)

This specific project also has as goal for the team to learn&utilize design and architecture patterns as well as follow SWA documentation best practices.
### Requirements Overview

1. The UI must display a history of previous chats. Previous chats can be viewed, continued and deleted
2. The user must be able to create, modify and delete CustomGPTs
3. Document upload for OpenDocument Format files and PDFs is possible
4. The information inside these documents is processed and CustomGPT will use and reference it in conversations
5. The user can see all the data that is used by a CustomGPT, including the documents uploaded.

### Quality Goals

#### Usability
- The UI must be similar to ChatGPT to enable fast adaption of new users.
The Feedback give to user input must be clear such that users know why a certain operation, like uploading unsupported document types, did not succeed.
#### Performance
*Latency*
- A user interaction must trigger a UX response in 500ms. The answer of the backend, when serving assistant messages, can be slow, though other responses shall not exceed 1s response time. Uploading documents shall lead to a fast response initial response once the documents are saved to the backend. Afterwards, the Preprocessing shall take no longer than 10 minutes before the user can use the CustomGPT
*Throughput*
- The system is not designed for high throughput, so 2 concurrent preprocessing tasks can be made in parallel with the expected latency.
#### Security
- Basic Auth and https will suffice for this POC
#### Reliability
*Concurrent Users*
- The system expects 5 concurrent users max as of now
*Data volume*
- The uploaded files are expected to not exceed 20MB and the storage for documents is expected to grow less then 10GB per year
*Load*
- The system should handle 4 preprocessing requests in parallel. the other tasks are less computationally heavy are expected to take more concurrent requests

#### Transferability
- The software system should be designed in such a way that enabling the usage of other LLM Apis is not too much work
### Stakeholders
#### Product Owner
Product owner must have a overview of the SWA to check if all features are implemented, which features can be implemented more easily and check the architecture decisions
#### Management
Management wants a quick overview of the SWA capabilities
#### Dev team
The dev team needs a place to document and reference architecture and architecture decisions
