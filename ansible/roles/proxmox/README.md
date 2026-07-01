Role Name
=========

Configure Proxmox Virtual Environment OS, NFS mounts for hosted VM's, and routine backups to a known Proxmox Backup Server

Requirements
------------

- Host is running firewalld (installed in common role)
- System user who owns the nfs mount data must exist on this host and remote hosts
- Host is running Proxmox Virtual Environment (PVE)
- PVE host contains manually configured ZFS datasets
- PVE host is configured to access a Proxmox Backup Server (PBS)

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

*vars used in vars/main.yml:*

- proxmox_packages: List of required packages to install
- proxmox_services: List of required services to start on boot
- proxmox_ports: List of ports to open on firewalld
- proxmox_nfs_mounts: Dictionary of NFS mount data, has the following format:
  { path: "/mount/path", owner: remote_user,
      group: nfs_group, mode: "0770" }
- proxmox_cron_jobs: Dictionary of cron jobs used to run backup jobs, has the format:
  { name: "Backup media, Monday at 3AM",
      minute: "0",
      hour: "3",
      weekday: "1",
      job: "proxmox-backup-client backup media.pxar:/hdd_mirror/media 
  }
- proxmox_pbs_repository: Vaulted string identifying the Proxmox Backup Server (PBS) repository that the backup script targets
- proxmox_pbs_password: Vaulted string used to connect to Proxmox Backup Server (PBS)

*vars used in group_vars/all:*

- admin_users: Dictionary of admin users given access to NFS data, has the following format:
  { name: "chasty2", uid: "1001", gid: "1001" }

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: lab
      roles:
         - common
         - proxmox

License
-------

GPL 3.0

Author Information
------------------

Cody Hasty
