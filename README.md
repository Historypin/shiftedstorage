# shifted-storage

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

*Note: if you are creating an shifted-storage node in an existing network jump down to the **Join** section below.*

The first node in a *shifted-storage* network is known as the bootstrap node. It requires a bit more setup than subsequent nodes because the Tailscale mesh network needs to be created and configured, and a couple secret keys need to be defined. This bootstrap node will be used by subsequent nodes to find the rest of the network when they join.

### Tailscale

Fill this in! The end goal is to get a `TS_AUTHKEY`.

### Keys

The security and privacy of your shifted-storage network is provided by two keys:

* IPFS Swarm Key
* IPFS Cluster Key

You will want to keep these in a secure place and onlye share them with others using a secure, end-to-end encrypted communication channel like Signal or WhatsApp.

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
CLUSTER_PEERNAME=<YOUR_PEER_NAME>
TS_AUTHKEY=<YOUR_TAILSCALE_AUTHKEY>
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

### Sharing with Others

In order to let others join the network you will need to share your `.env` file with them via a secure channel (e.g. WhatsApp or Signal). But before you do that you'll need to add three additional pieces of information to it. This information is used by the new node to discover the rest of the cluster.

#### BOOTSTRAP_TAILSCALE_IP

This is the IP address of your containers on the private mesh network that Tailscale helps you establish.

```
$ docker compose exec -ti tailscale tailscale ip --4
```

#### BOOTSTRAP_IPFS_PEER_ID

This is the unique identifier for your IPFS daemon:

```
$ docker compose exec -ti ipfs ipfs id -f "<id>"
```

#### BOOTSTRAP_IPFS_CLUSTER_PEER_ID

This is a unique identifier for your IPFS Cluster daemon:

```
$ docker compose exec -ti ipfs-cluster ipfs-cluster-ctl id
```

Note the ID is the first string in the output, for example the string `12D3KooWPR8q7wrGNbcdHsixXttBuujVS67kzTAjM8oN5zjR75Md`
in a line that looks like:

```
12D3KooWPR8q7wrGNbcdHsixXttBuujVS67kzTAjM8oN5zjR75Md | shifted-storage-edsu | Sees 0 other peers
```

#### Share!

Create a copy of your `.env` file called `env` and then add the following to it, while filling in the `<...>` templates:

```
# fill in the templated portions
BOOTSTRAP_TAILSCALE_IP=<YOUR BOOTSTRAP TAILSCALE IP HERE>
BOOTSTRAP_IPFS_PEER_ID=<YOUR BOOTSTRAP IPFS PEER ID HERE>
BOOTSTRAP_IPFS_CLUSTER_PEER_ID=<YOUR BOOTSTRAP IPFS CLUSTER PEER ID HERE>

# you can leave these alone
IPFS_CLUSTER_BOOTSTRAP=/ip4/$BOOTSTRAP_TAILSCALE_IP/tcp/9096/ipfs/$BOOTSTRAP_IPFS_CLUSTER_PEER_ID
IPFS_BOOTSTRAP=/ip4/$BOOTSTRAP_TAILSCALE_IP/tcp/4001/ipfs/$BOOTSTRAP_IPFS_PEER_ID
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

[Docker]: https://www.docker.com/get-started/
[Tailscale]: https://tailscale.com/
[IPFS Cluster]: https://ipfscluster.io/
[Git]: https://git-scm.com/
