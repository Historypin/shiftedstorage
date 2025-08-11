# ⇧📁 shifted-storage

*shifted-storage* is a specific configuration of [Docker], [IPFS Cluster] and
[Tailscale] that provides decentralized storage for a trusted network of participants or peers.
The goal of *shifted-storage* is to serve as an alternative to bigtech storage services, 
that is:

- *Decentralized* instead of *Centralized*: the software is open source and can
  be deployed on infrastructure that is operated by the members in their data centers,
  offices and homes. Members can join at any time to increase the capacity of the
  network, and can leave without disrupting the remaining members.
- *Trustfull* instead of *Trustless*: members have shared values and goals in
  order to join the network. It is up to specific communities to decide what this means for them.
- *Mutable* instead of *Immutable*: data doesn't get replicated outside of the
  trusted network, and it's possible to remove data from the entire network at
  any time.
- *Private* instead of *Public*: many peer-to-peer and distributed web systems
  are built around the idea of data being globally available, and easy to
  replicate. Data in *shifted-storage* is not made available to the
  wider IPFS network. The use of Tailscale allows peers to communicate
  directly with each other using a virtual private mesh network, that only they
  can see.

*shifted-storage* is essentially just a Docker Compose configuration for bringing up three containers so that they can talk to other similarly configured shifted-storage instances. The containers are:

* *tailscale*: a Tailscale client that establishes your node's connection to other trusted nodes in the mesh network.
* *ipfs*: an IPFS daemon running on the Tailscale network.
* *ipfs-cluster*: an IPFS Cluster daemon configured to talk to the IPFS service using the Tailscale network.

## Setup Bootstrap Node

*Note: if you are creating a shifted-storage node in an existing network jump down to the [Let Others Join](#let-others-join) section below.*

The first node in a *shifted-storage* network is known as the bootstrap node. It requires a bit more setup than subsequent nodes because the Tailscale mesh network needs to be created and configured, and a couple secret keys need to be defined. This bootstrap node will be used by subsequent nodes to find the rest of the network when they join.

### Tailscale

Fill this in! The end goal is to get a `TS_AUTHKEY`.

### Keys

The security and privacy of your shifted-storage network is provided by two keys:

* IPFS Swarm Key
* IPFS Cluster Key

You will want to keep these in a secure place and only share them with others using a secure, end-to-end encrypted communication channel like Signal or WhatsApp.

To create the keys you can:

```
$ openssl rand -hex 32 > swarm.key
$ openssl rand -hex 32 > ipfs-cluster.key
```

### Cluster Peer Name

You will need to create a name for your node. This name will be used to create a Tailscale host name in your virtual private network. You could use an abbreviated form of your organization name, or your personal name.

### Get the Docker Configuration

```
$ git clone https://github.com/historypin/shifted-storage
$ cd shifted-storage
```

### Environment File

Create a `.env` file:

```
IPFS_SWARM_KEY="/key/swarm/psk/1.0.0/
/base16/
<YOUR_SWARM_KEY>"

CLUSTER_SECRET=<YOUR_CLUSTER_SECRET>
TS_AUTHKEY=<YOUR_TAILSCALE_AUTHKEY>
CLUSTER_PEERNAME=<YOUR_PEER_NAME>
```

### Run

Now we are ready to run!

```bash
$ docker compose up -d
```

If you want to stop the service at any time you can execute this command, as long as you are in the `shifted-storage` directory:

```
$ docker compose stop
```

### Let Others Join

In order to let others join the network you will need to share a modified version of your `.env` file with them via a secure channel (e.g. WhatsApp or Signal).

The provided `bootstrap.py` utility will read your existing `.env` file and execute some commands in your running docker containers to determine additional information for new nodes to use when bootstrapping into the network:

- Tailscale IP
- IPFS Peer ID
- IPFS Cluster Peer ID

You need to supply a "node name" for the new node in your cluster. It's good to use a name without spaces or punctuation that will help you identify the node later since this is the hostname that it will appear under in the Tailscale network. For example, if you have are adding a node for "Warrior Women Project" you could:

The new configuration will be printed to `stdout`, which you could redirect to a file for sharing. 

```
./bootstrap.py warriorwomen > warriorwomen.env
```

## Joining a Network

In order to join an existing *shifted-storage* network you will need to be given a `.env` file by one of the other members. You will also need to install [Docker].

Download the `shifted-storage` configuration files from Github, and unzip it:

https://github.com/edsu/shifted-storage/archive/refs/heads/main.zip

**TODO: move repo to historypin github account**

This will create a directory `shifted-storage`. Put the `env` file into the `shifted-storage` directory using the name `.env`. It's important to have the `.` prefix in the name!

Run the node with:

```
$ docker compose up -d
```

If you want to stop the shifted-storage service at any time you can run:

```
$ docker compose stop
```

## Working With Storage

### Adding Content

TODO

### Checking Status

TODO

### Removing Content

TODO

[Docker]: https://www.docker.com/get-started/
[Tailscale]: https://tailscale.com/
[IPFS Cluster]: https://ipfscluster.io/
[Git]: https://git-scm.com/
