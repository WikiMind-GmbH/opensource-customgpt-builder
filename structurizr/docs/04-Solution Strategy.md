## Solution Strategy
>Contents  
A short summary and explanation of the fundamental decisions and solution strategies, that shape the system’s architecture. These include.  
-technology decisions  
-decisions about the top-level decomposition of the system, e.g. usage of an architectural pattern or design pattern  
-decisions on how to achieve key quality goals  
-relevant organizational decisions, e.g. selecting a development process or delegating certain tasks to third parties

This projects main goal is getting closer to creating a structure and outline for our modular LLM/AI product. As a result, most system architecture desicions are made with the goal of learning to get closer to a structure that we can use well into the future, instead of one that fits the current scope of the project and it being a POC best.
Thus, the decision was made that these are the top priorities that the SWA should achieve:
1. Highly Modular architecture -> Microservices: i) as dev: add, remove or extend functionalities(/services) easily and ii) being able to deploy and run the software system easily with different sets of functionalities(/services) -i.e. I can deploy an instance which does not use the rag functionality but the customgpt functionality, or the other way around
2. Using/implementing Good software design patterns
3. Using/implementing Good software architecture: i) Creating (and learning) good SWA documentation practices ii) following Microservises patterns

While some corners are cut as of now, the following will be implemented:
### Software design patterns
#### Three layer architecutre
Web layer.  
service layer.  
data layer.  

+
repository pattern with dependency inversion

(intro see Fastapi ch. 1, detailed: ch. )


### Microservice Architecture
[While the current scope does not necessarily need this seperation of concerns yet, it will be super helpful in the future, if we want to extend the functionality of existing services, add new services and  split work and being able to give a team member the responsibility of only one service sucht that they need to only understand this narrow scope]