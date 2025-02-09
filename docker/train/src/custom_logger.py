import logging
import os
import subprocess

def set_permissions_of_host_volume_owner(host_uid, host_gid):
    """ pour mettre en place les permissions du propriétaire hôte des volumes 
        - sur chacun des volumes montés dans "/app/"
        - pour tous les dossiers et fichiers dans ces volumes
    """
    if host_uid and host_gid: # si les valeurs sont bien récupérées
        with open('/proc/mounts', 'r') as mounts_file:
            app_mounts = [line.split()[1] for line in mounts_file if line.split()[1].startswith("/app/")]

        for mount_point in app_mounts:
            try:
                subprocess.run(["chown", "-R", f"{host_uid}:{host_gid}", mount_point], check=True)
                logging.info(f"Permissions mises à jour pour {mount_point} avec UID={host_uid} et GID={host_gid}.")
            except subprocess.CalledProcessError as e:
                logging.error(f"Erreur lors de la modification des permissions de {mount_point} : {e}")
    else:
        logging.error("UID ou GID de l'hôte non définis.")

host_uid = os.getenv("HOST_UID")
host_gid = os.getenv("HOST_GID")

# Create logs directory if it doesn't exist
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
    

# Create logs.log file if it doesn't exist
log_file = os.path.join(logs_dir, "logs.log")
if not os.path.exists(log_file):
    open(log_file, 'a').close()

# Configure logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get a logger instance and expose it as part of the module
logger = logging.getLogger(__name__) 

# Example usage within the module (optional)
logger.info("Custom logger module initialized.")
set_permissions_of_host_volume_owner(host_uid, host_gid)

