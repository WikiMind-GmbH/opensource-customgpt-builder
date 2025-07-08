# HTTPS certificates
## Mac
### Local - mkcert

On the host machine, run -from the project root path:
```sh
brew install mkcert        # macOS helper -for Linux/Win see below
brew install nss           # For firefox to trust own ca
mkcert -install            # adds root CA into macOS Keychain
mkcert -key-file nginx/certs/dev.key \
       -cert-file nginx/certs/dev.crt \
       localhost 127.0.0.1

```

## Windows
Open powershell as an administrator.
### Install chocolatey package manager
Run the following com
```.ps
Set-ExecutionPolicy Bypass -Scope Process -Force; `
[System.Net.ServicePointManager]::SecurityProtocol = `
[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
check if it is added to the path
```
choco --version
```
otherwise is add it manually to the environment variables path 

### For Firefox compatibility install nss
Download manually the most recent version from 
https://ftp.mozilla.org/pub/security/nss/releases/

Copy the file into a folder where you can keep it.
Extracted via `tar -xvzf ${yourfile}.tar.gz`




### 1. Install mkcert
run
```powershell choco install mkcert ```









| OS | Command |
|----|---------|
| **macOS** (Homebrew) | ```bash brew install mkcert nss # nss only needed for Firefox ``` |
| **Windows** (Chocolatey) | ```powershell choco install mkcert ``` |
| **Windows** (Scoop) | ```powershell scoop install mkcert ``` |
| **Linux – Debian/Ubuntu** | ```bash sudo apt install libnss3-tools curl -fsSL https://github.com/FiloSottile/mkcert/releases/latest/download/mkcert-$(uname -s)-amd64 -o mkcert && chmod +x mkcert && sudo mv mkcert /usr/local/bin ``` |
| **Linux – Fedora** | ```bash sudo dnf install mkcert nss-tools ``` |
| **Linux – Arch** | ```bash sudo pacman -S mkcert nss ``` |

> **Firefox users (any OS):** you need the extra `nss`/`libnss3-tools` package; Chrome/Edge/Safari pick up the cert from the OS store automatically.

### 2. Install the certificates

Run from the root of the repo the following command:
```
mkcert -key-file nginx/certs/dev.key \
       -cert-file nginx/certs/dev.crt \
       localhost 127.0.0.1
```