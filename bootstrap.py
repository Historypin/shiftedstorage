#!/usr/bin/env python3

"""
This utility is used on an existing shifted-cluster node to generate a
compose.yml file for a new node in the network. You run bootstrap.py with the 
name of the new node and it will write the compose.yaml file to stdout. You 
can share this information with someone who is starting up the new node.

./bootstrap warriorwomen > warriorwomen-compose.yml
"""

import json
import os
import re
import subprocess
import sys

import dotenv


def main():
    # read in existing .env file
    dotenv.load_dotenv()

    # get the existing compose file
    compose = open("compose.yml").read()
    
    # peer_name is the only argument to this program
    if len(sys.argv) != 2:
        sys.exit("Usage: bootstrap.py <node_name>")
    peer_name = sys.argv[1]


    # talk to the running containers to get the relevant bootstrap info
    tailscale_ip = run("docker compose exec -ti tailscale tailscale ip --4")
    ipfs_id = run("docker compose exec -ti ipfs ipfs id -f <id>")
    ipfs_cluster = run("docker compose exec -ti ipfs-cluster ipfs-cluster-ctl --enc json id", parse_json=True)
    ipfs_cluster_id = ipfs_cluster["id"]

    # construct multiaddr for bootstrapping ipfs and ipfs cluster
    ipfs_cluster_bootstrap = f"/ip4/{tailscale_ip}/tcp/9096/ipfs/{ipfs_cluster_id}"
    ipfs_bootstrap = f"/ip4/{tailscale_ip}/tcp/4001/ipfs/{ipfs_id}"

    # get some other things from the environment and add to the compose file
    compose = fillin("CLUSTER_PEERNAME", peer_name, compose)
    compose = fillin("IPFS_BOOTSTRAP", ipfs_bootstrap, compose)
    compose = fillin("IPFS_CLUSTER_BOOTSTRAP", ipfs_cluster_bootstrap, compose)
    compose = fillin("CLUSTER_SECRET", os.environ.get("CLUSTER_SECRET"), compose)
    compose = fillin("IPFS_SWARM_KEY", os.environ.get("IPFS_SWARM_KEY"), compose)
    compose = fillin("TS_AUTHKEY", os.environ.get("TS_AUTHKEY"), compose)

    compose += f"""
# you may need to run these commands in ipfs container once it is up
#
# ipfs bootstrap rm all
# ipfs bootstrap add "{ipfs_bootstrap}"
# ipfs config --json Addresses.Swarm '["/ip4/0.0.0.0/tcp/4001", "/ip6/::/tcp/4001"]'
# ipfs config --json Addresses.Announce [\"/ip4/{tailscale_ip}/tcp/4001\"]
#
"""

    print(compose)


def run(cmd, parse_json=False) -> str:
    out = subprocess.run(
        cmd.split(" "),
        capture_output=True,
        check=True,
    )
    if parse_json:
        return json.loads(out.stdout.decode('utf8'))
    else:
        return out.stdout.decode('utf8').strip()


def fillin(name, value, text):
    return re.sub(r'\$\{' + name + r'\}', value, text, flags=re.MULTILINE)


if __name__ == "__main__":
    main()


