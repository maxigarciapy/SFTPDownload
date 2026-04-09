import paramiko
import sys 
import yaml
import os

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
try:
    client.connect(hostname, port=port, username=username, pkey=private_key)
    print("Conectado")
except Exception as e:
    print(f"Error al conectar: {e}")
    exit()

remote_tar = "/tmp/remote.tar.xz"
tar_command = f"XZ_OPT=-e9 tar -cJvf {remote_tar} -C {remote_folder} ."
print("Creando Tar")
stdin, stdout, stderr = client.exec_command(tar_command)

for line in iter(stdout.readline, ""):
    print(line, end="")

exit_status = stdout.channel.recv_exit_status()


if exit_status != 0:
    print("Error creando tar:")
    print(stderr.read().decode())
    client.close()
    exit()

print("Tar creado en el server")

sftp = client.open_sftp()

sftp.get(remote_tar, local_tar)

print(f"Archivo guardado como: {local_tar}")

client.exec_command(f"rm {remote_tar}")

client.close()
exit()
