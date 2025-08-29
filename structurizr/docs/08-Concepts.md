## Crosscutting Concepts

### Internal vs external apis
One aspect that 
The only service that is reachable from outside the docker network -which is not a documentation or reverse proxy- is the gateway server.
Thus we have only one service that the clients need to authenticate to and this service then forwards the call to the corresponding services, where no further authentication is needed.  
All the other services ()
