#!/usr/bin/env python3

"""
This utility is used on an existing node to generate a new .env file for a new
node in the network. You run it with the name of the new node and it will write
the new .env to stdout. You can share this information with someone who is
starting up the new node.

./bootstrap warriorwomen > warriorwomen.env
"""

import json
import re
import subprocess
import sys

def main():
    # read in existing .env file
    env = open(".env").read()
    
    # remove existing cluster peer name
    env = re.sub("^CLUSTER_PEERNAME.+$", "", env)

    # peer_name
    if len(sys.argv) != 2:
        sys.exit("Usage: bootstrap.py <node_name>")
    peer_name = sys.argv[1]

    # talk to the running containers to get the relevant bootstrap info
    tailscale_ip = run("docker compose exec -ti tailscale tailscale ip --4")
    ipfs_id = run("docker compose exec -ti ipfs ipfs id -f <id>")
    ipfs_cluster = run("docker compose exec -ti ipfs-cluster ipfs-cluster-ctl --enc json id", parse_json=True)
    ipfs_cluster_id = ipfs_cluster["id"]

    extra = template.format(
        peer_name=peer_name,
        tailscale_ip=tailscale_ip,
        ipfs_id=ipfs_id,
        ipfs_cluster_id=ipfs_cluster_id

    )

    print(env + extra)


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


template = """\
# config for non-bootstrap node auto-discovery
CLUSTER_PEERNAME={peer_name}
IPFS_CLUSTER_BOOTSTRAP=/ip4/{tailscale_ip}/tcp/9096/ipfs/{ipfs_cluster_id}
IPFS_BOOTSTRAP=/ip4/{tailscale_ip}/tcp/4001/ipfs/{ipfs_id}
"""


if __name__ == "__main__":
    main()


