# SFTPDownload
Download a tar.xz file of a folder on a server via sftp

# Usage
Download the repo and run
```bash
source bin/activate
```
then, edit ```config.yaml``` with your parameters and run
```bash
python main.py config
```
If instead of the config file you want to use arguments, the structure of the command is:
```bash
python main.py <hostname> <port> <username> <key_path> <server folder> <local file (.tar.xz)>
```
