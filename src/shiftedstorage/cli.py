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
