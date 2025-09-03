from pathlib import Path

import click

from shiftedstorage import compose


@click.group()
def cli():
    pass


@cli.command()
@click.option("--cluster-peername", required=True)
@click.option("--ts-authkey", required=True)
@click.option("--output", type=click.File("w"), default="-")
def create(output: click.File, cluster_peername: str, ts_authkey: str):
    """
    Create a new shiftedstorage Docker Compose file.
    """
    compose.create(output, cluster_peername=cluster_peername, ts_authkey=ts_authkey)


@cli.command()
@click.option("--cluster-peername", required=True)
@click.option("--input", type=click.File("r"), required=True)
@click.option("--output", type=click.File("w"), default="-")
@click.option("--bootstrap-host", required=True)
def clone(
    cluster_peername: str, input: click.File, output: click.File, bootstrap_host: str
):
    """
    Use an existing compose file, and running containers, to generate a
    configuration for a new node in the cluster.
    """
    compose.clone(
        input, output, cluster_peername=cluster_peername, bootstrap_host=bootstrap_host
    )


@cli.command()
@click.option("--cluster-peername", required=True)
def reset_bootstrap_peers(cluster_peername: str) -> None:
    """
    Reset the bootstrap peers for a given node in the cluster. Useful on first
    setup of a node to ensure it isn't trying to talk to other peers.
    """
    compose.reset_bootstrap_peers(cluster_peername)


@cli.command()
@click.option("--cluster-peername", required=True)
@click.option("--bootstrap-host", required=True)
def set_bootstrap_peer(cluster_peername: str, bootstrap_host: str) -> None:
    """
    Add the bootstrap host as a peer to the IPFS container in the cluster node.
    This is useful when first setting up a new node in the cluster to ensure it
    can talk to the bootstrap node.
    """
    compose.set_bootstrap_peer(cluster_peername, bootstrap_host)


@cli.command()
@click.option("--cluster-peername", required=True)
@click.argument("path", type=click.Path(exists=True, path_type=Path), required=True)
def add(cluster_peername: str, path: click.Path) -> None:
    """
    Add a file or directory to the storage cluster using a peer hostname.
    """
    print(f"adding {path} to {cluster_peername}")
    print(compose.add(path, host=cluster_peername))


@cli.command()
@click.option("--cluster-peername", required=True)
@click.argument("cid", required=True)
def status(cid: str, cluster_peername: str) -> None:
    """
    Output the status of a CID in the cluster.
    """
    print(compose.status(cid, host=cluster_peername))


@cli.command()
@click.option("--cluster-peername", required=True)
def ls(cluster_peername: str) -> None:
    """
    List CIDs that are pinned in the cluster.
    """
    print(compose.ls(host=cluster_peername))


@cli.command()
@click.option("--cluster-peername", required=True)
@click.argument("cid", required=True)
def rm(cid: str, cluster_peername: str) -> None:
    """
    Remove a CID from the cluster.
    """
    print(compose.rm(cid, host=cluster_peername))


@cli.command()
@click.argument("cid", required=True)
@click.option("--cluster-peername", required=True)
@click.option("--output", type=click.Path(exists=False, path_type=Path), required=True)
def get(cid: str, cluster_peername: str, output: click.File) -> None:
    """t
    Get contents of a file and write to STDOUT or a file.
    """
    compose.get(cid, host=cluster_peername, output=output)
