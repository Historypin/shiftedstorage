# ⇧📁 shifted-storage

*shifted-storage* is a tailored configuration of [Docker], [IPFS Cluster] and [Tailscale] that allows a trusted network of archives to cooperatively back up each other's data. This work is part of [Shift Collective]'s [Modeling Sustainable Futures: Exploring Decentralized Digital Storage for Community Based Archives] project, which was funded by the [Filecoin Foundation for the Decentralized Web]. For more details you can read reports linked from the project's homepage.

In a nutshell, the goal of *shifted-storage* is to provide an alternative to "big-tech" storage services, that is:

- *Decentralized* instead of *Centralized*: the software is open source and can
  be deployed on infrastructure that is operated by the members in their data centers,
  offices and homes. Members can join at any time to increase the capacity of the
  network, and can leave without disrupting the remaining members.
- *Trustful* instead of *Trustless*: members have shared values and goals in
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

*shifted-storage* is really just a Docker Compose configuration for reliably bringing up Docker services that allows a network of shifted-storage instances to talk to each other. The containers are:

* *tailscale*: a Tailscale client that establishes your node's connection to other trusted nodes in the mesh network.
* *ipfs*: an IPFS daemon running on the Tailscale network.
* *ipfs-cluster*: an IPFS Cluster daemon configured to talk to the IPFS service using the Tailscale network.

Of course it's not all rainbows and unicorns, there are tradeoffs to this approach:

* The data in the storage cluster is only as stable as the people and organizations that are helping host it.
* Participants in the cluster can potentially access and delete data that does not belong to them.
* Unlike polished big-tech storage platforms (e.g. Google Drive, Box, etc) there are usability challenges to adding and removing content from the storage cluster.
* The IPFS and Tailscale software being used is open source, but the people maintaining it may change their minds, and focus on other things.
* Tailscale makes establishing a virtual private mesh network easy using the open source Wireguard software and some of their own open source code and infrastructure. Howevver Tailscale are a company and could decide to change how they do things at any time.
* Tailscale doesn't have access to any of the stored data, but they do know the network topology of the IPFS cluster, and could be issued a subpoena in some jurisdictions that forces them to share who is a member of the network. Read more about this [here](https://tailscale.com/blog/tailscale-privacy-anonymity).

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
IPFS_SWARM_KEY=<YOUR_SWARM_KEY>
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

In order to let others join the network you will need to share a modified version of the compose file with them via a secure channel (e.g. WhatsApp or Signal).

The provided `bootstrap.py` utility will read your existing `compose.yml` and `.env` file and execute some commands in your running docker containers to determine additional information for new nodes to use when bootstrapping into the network:

- Tailscale IP
- IPFS Peer ID
- IPFS Cluster Peer ID

You need to supply a "node name" for the new node in your cluster. It's good to use a name without spaces or punctuation that will help you identify the node later since this is the hostname that it will appear under in the Tailscale network. For example, if you have are adding a node for "Warrior Women Project" you could:

The new configuration will be printed to `stdout`, which you could redirect to a file for sharing. 

```
./bootstrap.py warriorwomen > warriorwomen.env
```

## Joining a Network

In order to join an existing *shifted-storage* network you will need to be given a `compose.yml` file by one of the other members.

You should be able to run this using Docker, but gor our project we have been standardizing on QNAP devices that are running the Container Station application.

1. Install Container Station from Apps if it's not already available.
2. Open Container Station.
3. Click `Applications` option in the menu on the left.
4. Click the `Create` button.
5. In the Application Name box enter `shifted-storage`
6. Paste the contents of the supplied `compose.yml` file into the text box.
7. Click the `create` button.
8. Click the `Containers` option in the menu on the left.
9. Verify that you see three containers running.

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
[Filecoin Foundation for the Decentralized Web]: https://ffdweb.org/
[Modeling Sustainable Futures: Exploring Decentralized Digital Storage for Community Based Archives]: https://www.shiftcollective.us/ffdw
[Shift Collective]: https://www.shiftcollective.us/
