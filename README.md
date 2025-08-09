# shifted-storage

*shifted-storage* provides decentralized, private storage for community
archives that want to back up each others files. It is a [Docker Compose]
configuration for running a *private* [IPFS Cluster] using a IPFS client that
is disconnected from the public IPFS network.

* nodes talk to each other
* nodes can come and go
* private cluster
* private ipfs
* private network (tailscale)

## Configure Tailscale

## Setup Bootstrap Node

## Environment File

Create a `.env` file:

```
IPFS_SWARM_KEY="/key/swarm/psk/1.0.0/
/base16/
<YOUR_SWARM_KEY>"

CLUSTER_SECRET=<YOUR_CLUSTER_SECRET>
CLUSTER_PEERNAME=shifted-storage-edsu
TS_AUTHKEY=<YOUR_TAILSCALE_AUTHKEY>
```

## Run

```bash
$ docker compose up
```
