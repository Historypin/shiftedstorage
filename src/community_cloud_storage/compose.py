import json
import os
import socket
import subprocess
from io import TextIOWrapper
from pathlib import Path

import yaml


def create(
    output: TextIOWrapper,
    cluster_peername: str,
    ts_authkey: str,
    cluster_secret: str = None,  # these will be gereated if not passed in
    ipfs_swarm_key: str = None,  # but are useful to define when testing
) -> None:
    """
    Create a new compose.yml for a new cluster. This node will act as a
    bootstrap node for subsequent nodes in the cluster.
    """

    # generate secret keys if needed
    ipfs_swarm_key = ipfs_swarm_key or os.urandom(32).hex()
    cluster_secret = cluster_secret or os.urandom(32).hex()

    output.write(
        compose_text(
            cluster_peername=cluster_peername,
            ipfs_swarm_key=ipfs_swarm_key,
            cluster_secret=cluster_secret,
            ts_authkey=ts_authkey,
        )
    )


def clone(
    input: TextIOWrapper,
    output: TextIOWrapper,
    cluster_peername: str,
    bootstrap_host: str,
) -> None:
    """
    This function will clone a new node based on the compose file of a bootstrap
    node, and the IDs that can be retrieved by talking to the bootstrap host
    using the ipfs and ipfs-cluster-ctl command (which must be installed).

    We need to be given:
    - an existing compose.yml file as input
    - an output handle to write the new compose text
    - a new cluster peer name for the clone

    We read these values from the existing compose.yaml file since they are
    carried through unchanged:
    - TS_AUTHKEY
    - IPFS_SWARM_KEY
    - CLUSTER_SECRET

    And we generate these new environment variables by talking to the running
    bootstrap host to get its Tailscale IP and the IPFS IDs:
    - IPFS_BOOTSTRAP
    - IPFS_CLUSTER_BOOTSTRAP
    """

    # load the existing compose doc
    bootstrap_doc = yaml.load(input, Loader=yaml.Loader)

    # talk to the running containers to get the relevant bootstrap info
    tailscale_ip = socket.gethostbyname(bootstrap_host)
    ipfs_id = run(f"ipfs --api /dns/{bootstrap_host}/tcp/5001 id -f <id>")
    ipfs_cluster = run(
        f"ipfs-cluster-ctl --host /dns4/{bootstrap_host}/tcp/9094 --enc json id",
        parse_json=True,
    )
    ipfs_cluster_id = ipfs_cluster["id"]

    # construct multiaddr for bootstrapping ipfs and ipfs cluster
    ipfs_cluster_bootstrap = f"/ip4/{tailscale_ip}/tcp/9096/ipfs/{ipfs_cluster_id}"
    ipfs_bootstrap = f"/ip4/{tailscale_ip}/tcp/4001/ipfs/{ipfs_id}"

    # write out the compose text for the clone!
    output.write(
        compose_text(
            cluster_peername=cluster_peername,
            ipfs_swarm_key=bootstrap_doc["services"]["ipfs"]["environment"][0],
            cluster_secret=bootstrap_doc["services"]["ipfs-cluster"]["environment"][
                "CLUSTER_SECRET"
            ],
            ts_authkey=bootstrap_doc["services"]["tailscale"]["environment"][
                "TS_AUTHKEY"
            ],
            ipfs_bootstrap=ipfs_bootstrap,
            ipfs_cluster_bootstrap=ipfs_cluster_bootstrap,
        )
    )


def reset_bootstrap_peers(host: str) -> None:
    """
    When IPFS nodes start up they should have bootstrap peers removed.
    """
    run(f"ipfs --api /dns/{host}/tcp/5001 bootstrap rm all")


def set_bootstrap_peer(cluster_peername: str, bootstrap_host: str) -> None:
    """
    When IPFS nodes start up they may need to be given the bootstrap node explicitly.
    """

    # ensure we have a blank slate
    reset_bootstrap_peers(cluster_peername)

    # determine the IP of the bootstrap node
    tailscale_ip = socket.gethostbyname(bootstrap_host)

    # tell the cluster node to use bootstrap IP for bootstrapping
    run(
        f"""ipfs --api /dns/{cluster_peername}/tcp/5001 config --json Addresses.Swarm ["/ip4/0.0.0.0/tcp/4001","/ip6/::/tcp/4001"]"""
    )
    run(
        f"""ipfs --api /dns/{cluster_peername}/tcp/5001 config --json Addresses.Announce ["/ip4/{tailscale_ip}/tcp/4001"]"""
    )

    # create multiaddr format for bootstrap node
    ipfs_id = run(f"ipfs --api /dns/{bootstrap_host}/tcp/5001 id -f <id>")
    ipfs_bootstrap_multi = f"/ip4/{tailscale_ip}/tcp/4001/ipfs/{ipfs_id}"

    # add the bootstrap node
    run(
        f"ipfs --api /dns/{cluster_peername}/tcp/5001 bootstrap add {ipfs_bootstrap_multi}"
    )


def compose_text(
    cluster_peername,
    ts_authkey,
    ipfs_swarm_key,
    cluster_secret,
    ipfs_bootstrap=None,
    ipfs_cluster_bootstrap=None,
):
    # read in the compose template
    template_path = Path(__file__).parent / "compose.yml"
    doc = yaml.load(template_path.open("r"), Loader=yaml.Loader)

    doc["services"]["tailscale"]["hostname"] = cluster_peername
    doc["services"]["tailscale"]["environment"]["TS_AUTHKEY"] = ts_authkey
    doc["services"]["ipfs-cluster"]["environment"]["CLUSTER_PEERNAME"] = (
        cluster_peername
    )
    doc["services"]["ipfs-cluster"]["environment"]["CLUSTER_SECRET"] = cluster_secret

    # The IPFS Swarm Key is a bit difficult because it needs to be packaged as a multiline string for the
    # environment, simulating a file on disk.
    if "IPFS_SWARM_KEY=" not in ipfs_swarm_key:
        ipfs_swarm_key = (
            f"IPFS_SWARM_KEY=/key/swarm/psk/1.0.0/\n/base16/\n{ipfs_swarm_key}"
        )
    doc["services"]["ipfs"]["environment"] = [ipfs_swarm_key]

    # if we've been given the ipfs bootstrap info add that to the ipfs environment
    if ipfs_bootstrap:
        env_list = doc["services"]["ipfs"]["environment"]
        env_str = f"IPFS_BOOTSTRAP={ipfs_bootstrap}"
        if env_str not in env_list:
            # not sure why but the qnap yaml parser doesn't like it if this
            # environment variable shows up after the multiline IPFS_SWARM_KEY
            env_list.insert(0, env_str)

    # similarly if we've been given the ipfs cluster bootstrap info, we can add
    # that to the ipfs cluster environment
    if ipfs_cluster_bootstrap:
        doc["services"]["ipfs-cluster"]["environment"]["CLUSTER_PEERADDRESSES"] = (
            ipfs_cluster_bootstrap
        )

    # return the serialized yaml
    return yaml.dump(doc)


def add(path: Path, host: str) -> str:
    """
    Add a given file or directory to the cluster.
    """
    cmd = f"ipfs-cluster-ctl --host /dns4/{host}/tcp/9094 add"

    if path.is_dir():
        cmd += " --recursive"

    cmd += f" {path}"

    return run(cmd)


def status(cid: str, host: str) -> str:
    """
    Add a given file or directory to the cluster.
    """
    return run(f"ipfs-cluster-ctl --host /dns4/{host}/tcp/9094 status {cid}")


def ls(host: str) -> str:
    """
    List CIDs that are pinned in the cluster.
    """
    return run(f"ipfs-cluster-ctl --host /dns4/{host}/tcp/9094 pin ls")


def rm(cid: str, host: str) -> str:
    """
    Remove a CID from the cluster.
    """
    return run(f"ipfs-cluster-ctl --host /dns4/{host}/tcp/9094 pin rm {cid}")


def get(cid: str, host: str, output: Path) -> str:
    """
    Remove a CID from the cluster.
    """
    run(f"ipfs --api /dns/{host}/tcp/5001 get --output {output} {cid}")


def run(cmd, parse_json=False) -> str:
    """
    Run a system command and return the output, optionally parsing JSON output.
    """
    out = subprocess.run(
        cmd.split(" "),
        capture_output=True,
        check=True,
    )
    if parse_json:
        return json.loads(out.stdout.decode("utf8"))
    else:
        return out.stdout.decode("utf8").strip()
