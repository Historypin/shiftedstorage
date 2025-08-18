import os
import re
import socket
from unittest.mock import Mock

import yaml

from shiftedstorage import compose


def test_create(tmp_path):
    compose_path = tmp_path / "compose.yml"

    compose.create(
        output=compose_path.open("w"),
        cluster_peername="bootstrap",
        ts_authkey="abc123def",
    )

    assert compose_path.is_file()
    doc = yaml.load(compose_path.open("r"), Loader=yaml.Loader)

    assert doc["name"] == "shiftedstorage"
    assert doc["services"]["tailscale"]["hostname"] == "bootstrap"
    assert doc["services"]["tailscale"]["environment"]["TS_AUTHKEY"] == "abc123def"

    m = re.match(
        "IPFS_SWARM_KEY=/key/swarm/psk/1.0.0/\n/base16/\n(.+)",
        doc["services"]["ipfs"]["environment"][0],
        flags=re.MULTILINE,
    )
    assert m
    assert len(m.group(1)) == 64

    assert len(doc["services"]["ipfs-cluster"]["environment"]["CLUSTER_SECRET"]) == 64


def test_clone(tmp_path, monkeypatch):
    # generate some known secrets so we can test that they show correctly in the
    # generated compose file
    ipfs_swarm_key = os.urandom(32).hex()
    cluster_secret = os.urandom(32).hex()

    # first create a compose file
    compose_path = tmp_path / "compose.yml"
    compose.create(
        output=compose_path.open("w"),
        cluster_peername="bootstrap",
        ts_authkey="abc123def",
        ipfs_swarm_key=ipfs_swarm_key,
        cluster_secret=cluster_secret,
    )
    assert compose_path.is_file()

    # mock the lookup of a hostname and two system calls
    monkeypatch.setattr(socket, "gethostbyname", lambda _: "192.168.1.15")
    monkeypatch.setattr(
        compose,
        "run",
        Mock(
            side_effect=[
                "12D3KooWRy3uoprJ3ijtQHqwS3mUkchBXeqmwk9HhLQYwif9hD2C",  # ipfs id
                {
                    "id": "12D3KooWHuxBMn6M5dqwhFpaCRpj5BXoomEq8rncbJeXpLG12qs2"
                },  # ipfs cluster id
            ]
        ),
    )

    # create a clone of the compose file configured for a new node
    new_compose_path = tmp_path / "clone-compose.yml"

    compose.clone(
        input=compose_path.open("r"),
        output=new_compose_path.open("w"),
        cluster_peername="clone",
        bootstrap_host="bootstrap",
    )

    doc = yaml.load(new_compose_path.open("r"), Loader=yaml.Loader)

    assert doc["name"] == "shiftedstorage"
    assert doc["services"]["tailscale"]["hostname"] == "clone"
    assert doc["services"]["tailscale"]["environment"]["TS_AUTHKEY"] == "abc123def"
    assert (
        doc["services"]["ipfs-cluster"]["environment"]["CLUSTER_SECRET"]
        == cluster_secret
    )

    assert (
        doc["services"]["ipfs"]["environment"][0]
        == "IPFS_BOOTSTRAP=/ip4/192.168.1.15/tcp/4001/ipfs/12D3KooWRy3uoprJ3ijtQHqwS3mUkchBXeqmwk9HhLQYwif9hD2C"
    )

    m = re.match(
        "IPFS_SWARM_KEY=/key/swarm/psk/1.0.0/\n/base16/\n(.+)",
        doc["services"]["ipfs"]["environment"][1],
        flags=re.MULTILINE,
    )
    assert m.group(1) == ipfs_swarm_key

    assert (
        doc["services"]["ipfs-cluster"]["environment"]["CLUSTER_PEERADDRESSES"]
        == "/ip4/192.168.1.15/tcp/9096/ipfs/12D3KooWHuxBMn6M5dqwhFpaCRpj5BXoomEq8rncbJeXpLG12qs2"
    )
