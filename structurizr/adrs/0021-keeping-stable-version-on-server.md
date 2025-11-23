# 21. keeping stable version on server

Date: 2025-11-21

## Status

Accepted

## Context

We need to have a process similar to splitting a repo into staging prod and dev.   
Each version of the app is necessary for a different purpose:  
We need dev and feature branches to improve the software and include new features.   
We need a stable version that we can deploy for customers.   
And we need a testing branch that is more stable than the dev and feature branches, where we can have testers test new versions of our software.  

All of this only works if there are clear guidelines that qualify when our code qualifys to move from dev to testing to prod.   
For each transition, we need qualifyers that evaluate if the quality of the code is up to standard.    
This can be simple things like unit/e2e tests that need to written and passed, code reviews or enought time being tested by test users for a version of code to move from testing to prod.    

Additionally, we must consider practicality: it is important that we start somewhere fast, and improve it itearitevly
## Decision
We create two additional branches: `prod` `testing`
### Testing
Testing branch will be used for local testing and in the future also be available for testing online
For code to be allowed to merge into `Testing`, it must fulfill these criteria:   
- e2e are passed
- if there is the introduction of a major feature that opens a new use case: a new (backend) e2e test must be written.
- for each new adapter, a test module must be written
- for each new service function, a test module must be written
- all the previous tests must be passed -if we introduce a new adapter for a port, we must also change our service function tests to use this instead of the deprecated one. If both adapters should be used, we must copy the test module and run it with the new adapter as well

### Prod
For code to be allowed to merge into `Testing`, it must fulfill these criteria:
- Only code from testing can be merged into prod
- The code was on testing and was run and actively tested for at least one hour (for now) -future: was tested by client testers for 2 weeks.

## Consequences

We will always be able to showcase two (more or less) working version -testing and prod.   
Being incentiviced to creat 'checkpoints' on working versions by merging into testing, thus shortening the cycle between working versions, resulting in a faster feedback loop.
