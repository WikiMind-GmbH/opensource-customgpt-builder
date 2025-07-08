# Project Setup

This project uses Docker Compose for managing development and production environments.

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your system.
- [Docker Compose](https://docs.docker.com/compose/) installed.
- It is advised to use VSCode and to install all the necessary extensions published by Microsoft for Docker (Docker, Container Tools) and the Python Debugger extension. These change from time to time -check the VSCode Pop Ups which recommend fitting extensions.
- Please also install the VSCode black formatter extension from Microsoft and use it to format the python code with it. For JS/TS and CSS use the Prettier Formatter extension from Prettier.
- For local development, mkcert must be used to create ssl certs. The Readme.md in the nginx folder explains how to do this.
- The frontend uses a client generated from the fastapi openapi documentation to reach the endpoints and provide interfaces detailing the expected structure of the bodys. When changing endpoint signatures or adding new endpoints, you must use `make generate-client-prod`

## Environment Setup

- The project uses a single `.env` file for environment variables. Ensure that it is correctly set up before running the containers. Copy the `.env.example`, paste it in the same folder, rename the copy to `.env` and fill in the values that are not defaults. Some values are only needed for the prod environment, no need to set them for development.


## Development
You must install mkcert for https to work. See nginx/README.md on how to do it.


(*All `sh`/`bash` commands must be executed from the repo root path (`mudita-full`)*)

Start the application via the `docker-compose.dev.yaml` file.    

```sh
docker-compose -f docker-compose.dev.yaml up -d
```

For VSCode, debugging configs are provided in the `.vscode` folder. Please use them when debugging front or backend. You must open the root folder of the repo (the parent folder of this readme) for vscode to automatically detect and provide them.

Live reloading & bind mounts are set up for back and frontend. The changes you make in the code locally will be reflected immediatly after saving in the app.

Use the React debugging config of launch.json to makes sure that you will not use a cached version of the frontend.

You can set in the `.env` file if you want the backend debugger to wait for connections. If you set `WAIT_FOR_DEBUGGER_IN_BACKEND` in `.env` to true, the server will not start until you connect to the debugger (e.g via the `launch.json` config `Backend debugger`)
Generelly, this is not necessary.

*Keep the automatically generated frontend client up-to-date and use it!*    
If you add or change endpoints in the backend, you need to run the makefile and change the base path in `OpenAPI.ts`. In this way, the client will always expect the correct properties/body structure of backend answers, query parameters,  request body.


## Production

To start the production environment

### Utilizing VSCodes UI features and quality of life improvements on the remote server
Connect via vscode+ssh to the server.

Installing the docker extension inside the server.

-> Control docker via vscode UI instead of cmd tool. No manual docker &docker-compose install needed either

Utilize the Version Control UI in VSCoder -> Vscode authenticates you to git, no set up of ssh key & manual setup needed

### Set up the Certificates
1. Correctly fill out the following files:
a) `.env`
For example:
```sh
CERTBOT_DOMAINS="-d url.de -d www.albert.wikimind.de"
CERTBOT_EMAIL=albert.sandritter@wikimind.de
```
b) nginx_lets_encrypt_setup.conf + nginx_prod.conf
```

server {
    listen 80;
    server_name albert-test.wikimind.de www.albert-test.wikimind.de;
}
```
```
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN}; <---- !!!
    # ACME challenge (Let’s Encrypt)
    ...
}

server {
    listen 443 ssl ;
    http2 on;
    server_name ${DOMAIN}; <---- !!!

    ssl_certificate     /etc/letsencrypt/live/${DOMAIN}/fullchain.pem; <---- !!!
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem; <---- !!!
```
2. from the repo root, spin up the `docker-compose.letsencryptsetup.yaml`
```sh
docker compose -f docker-compose.letsencryptsetup.yaml up
```
3. Check the logs of the certbot container if it worked.
```sh
docker ps -a # check the name of the certbot container
docker logs ${name_of_certbot_container}
```
It should read like this:
```sh
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Account registered.
Requesting a certificate for albert.wikimind.de and www.albert.wikimind.de

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/albert.wikimind.de/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/albert.wikimind.de/privkey.pem
This certificate expires on 2025-08-17.
These files will be updated when the certificate renews.
NEXT STEPS:
- The certificate will need to be renewed before it expires. Certbot can automatically renew the certificate in the background, but you may need to take steps to enable that functionality. See https://certbot.org/renewal-setup for instructions.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```
4. Shut down the containers with 
```sh
docker-compose -f docker-compose.letsencryptsetup.yaml down
```

5. Set up Basic Auth
Install apache2-utils to get htpasswd
```bash
sudo apt update
sudo apt install apache2-utils
```
Create the .htpasswd file
```sh
htpasswd -c ./nginx/.htpasswd ${userName}
```
Create a password, write it down


### If the certificates & `.htpasswd` were created, start the prod docker compose
1. Start up the prod docker compose
```sh
docker-compose -f docker-compose.prod.yaml up -d
```

2. Make sure to correctly set the `BASE_PATH` in `OpenApi.ts`
```ts
export const OpenAPI: OpenAPIConfig = {
    BASE: 'https://${hostname}/api',
```



## Nginx Configuration

For production, set the `server_name` in `nginx_prod.conf` to match your domain or IP address.

## Best practices
The FastAPI backend API must be documented in enought detail to understand all endpoints and their functionality soley by reading the openapi config/looking at the swag ui API documenttation at `app/docs`



## Additional Notes

- Make sure to update `nginx_prod.conf` before deploying in production.
- The same `.env` file is used across both environments.
- If needed, modify the `docker-compose` files to suit your setup.
