import paramiko
import sys
import yaml
import os
import tarfile
import stat
import shutil

def sftp_download_dir(sftp, remote_dir, local_dir):
    os.makedirs(local_dir, exist_ok=True)

    for item in sftp.listdir_attr(remote_dir):
        remote_path = remote_dir + "/" + item.filename
        local_path = os.path.join(local_dir, item.filename)

        if stat.S_ISDIR(item.st_mode):
            # Directory → recurse
            sftp_download_dir(sftp, remote_path, local_path)
        else:
            # File → download
            print(f"Descargando: {remote_path}")
            sftp.get(remote_path, local_path)

def compress_to_tar_xz(source_dir, output_file):
    with tarfile.open(output_file, "w:xz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

if (sys.argv[1] != "config"):
    try:
        hostname = str(sys.argv[1])
        port = int(sys.argv[2])
        username = str(sys.argv[3])
        key_path = str(sys.argv[4])
        remote_folder = str(sys.argv[5])
        local_tar = str(sys.argv[6])
    except IndexError:
        print("Error, uso: python main.py <ip> <puerto> <usuario> <key> <carpeta remota> <archivo destino (.tar.xz)> o config.yaml")
        exit()
else: 
    try:
        # config_file = "config.local.yaml" if os.path.exists("config.local.yaml") else "config.yaml"
        if (os.path.exists("config.local.yaml")):
            config_file = "config.local.yaml"
        else:
            config_file = "config.yaml"
        with open(config_file) as f:
            config = yaml.safe_load(f)
            hostname = config["server"]["hostname"]
            port = config["server"]["port"]
            username = config["server"]["username"]
            key_path = config["server"]["key"]
            remote_folder = config["files"]["remote_folder"]
            local_tar = config["files"]["local_tar"]
    except Exception as err:
        print(err)
        exit()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

private_key = paramiko.RSAKey.from_private_key_file(key_path)
print("Conectando...")
client.connect(hostname, port=port, username=username, pkey=private_key)

sftp = client.open_sftp()

local_folder = "downloaded_data"
print("Descargando carpeta remota...")
sftp_download_dir(sftp, remote_folder, local_folder)

compress_to_tar_xz(local_folder, local_tar)

print("Limpiando...")
shutil.rmtree(local_folder)
print("Terminando...")
sftp.close()
client.close()
print("Listo.")
exit()
