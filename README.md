# ⇧📁 shiftedstorage

[![Test](https://github.com/historypin/shiftedstorage/actions/workflows/test.yml/badge.svg)](https://github.com/historypin/shiftedstorage/actions/workflows/test.yml)

*shiftedstorage* is a small Python command line utility that lets you create and manage a [Docker] based, trusted, decentralized storage system for community archives. All the heavy lifting is done by [IPFS Cluster] and [Tailscale] which provides a virtual private mesh network for the cluster participants that the rest of the world can't see. The familiar value proposition here is that yes, "Lots of Copies Keeps Stuff Safe", but also, that it can help if those copies are in different geopolitical regions.

This work is part of [Shift Collective]'s [Modeling Sustainable Futures: Exploring Decentralized Digital Storage for Community Based Archives] project, which was funded by the [Filecoin Foundation for the Decentralized Web]. For more details you can read reports linked from the project's homepage.

In a nutshell, the goal of *shiftedstorage* is to provide an alternative to "big-tech" storage services, that is:

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
  replicate. Data in *shiftedstorage* is not made available to the
  wider IPFS network. The use of Tailscale allows peers to communicate
  directly with each other using a virtual private mesh network, that only they
  can see.

*shiftedstorage* is really just a Docker Compose configuration for reliably bringing up Docker services that allows a network of shiftedstorage instances to talk to each other. The containers are:

* *tailscale*: a Tailscale client that establishes your node's connection to other trusted nodes in the mesh network.
* *ipfs*: an IPFS daemon running on the Tailscale network.
* *ipfs-cluster*: an IPFS Cluster daemon configured to talk to the IPFS service using the Tailscale network.

Of course it's not all rainbows and unicorns, there are tradeoffs to this approach:

* The data in the storage cluster is only as stable as the people and organizations that are helping host it.
* Participants in the cluster can potentially access and delete data that does not belong to them.
* Unlike polished "big-tech" storage platforms (e.g. Google Drive, Box, etc) there are usability challenges to adding and removing content from the storage cluster.
* The IPFS and Tailscale software being used is open source, but the people maintaining it may change their minds, and focus on other things.
* Tailscale makes establishing a virtual private mesh network easy using the open source Wireguard software and some of their own open source code and infrastructure. However, Tailscale are a company and could decide to change how they do things at any time.
* Tailscale doesn't have access to any of the stored data, but they do know the network topology of the IPFS cluster, and could be issued a subpoena in some jurisdictions that forces them to share who is a member of the network. Read more about this [here](https://tailscale.com/blog/tailscale-privacy-anonymity).

In short, shiftedstorage doesn't solve the Governance Problem. You have to decide who is in your trusted network, and everyone in your network needs to decide what your values are, and specifically what norms are around deleting content, and growing the network.

## Install

First, install the `ipfs` and `ipfs-cluster-ctl` command line utilities, and make sure they are in your system path. You don't need to run the cluster on your workstation, however having these utilities available makes it easy for the `shiftedstorage` command line tool to talk to running nodes.

* `ipfs`: https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions
* `ipfs-cluster-ctl`: https://dist.ipfs.tech/#ipfs-cluster-ctl

You will want to install [Docker] on whatever machine you are planning to run your node on.

You will also need to install the `shiftedstorage` utility which helps create the Docker compose file for the bootstrap node and then clone that for subsequent nodes in your network.

The preferred way to run `shiftedstorage` is with the `uvx` utility from [uv]. uv makes it easy to run Python utilities without needing to download and install them, or even have Python available.

```
uvx shiftedstorage
```

Alternatively, you can install shiftedstorage using Python's package manager with:

```
pip install shiftedstorage
```

The rest of the documentation uses examples with `uvx` but if you install with `pip` you should be able to remove that part of the command.

## Setup Bootstrap Node

*Note: if you are creating a shiftedstorage node in an existing network jump down to the [Let Others Join](#let-others-join) section below.*

The first node in a *shiftedstorage* network is known as the bootstrap node. It requires a bit more setup than subsequent nodes because the Tailscale mesh network needs to be created and configured, and a couple secret keys need to be defined. This bootstrap node will be used by subsequent nodes to find the rest of the network when they join.

### Tailscale

TBD! The end goal is to get a `TS_AUTHKEY`.

Be sure to also mention that any admins should get invited to the Tailscale so they can see it from their workstation.

### Create Compose File

Use your Tailscale token to create your bootstrap node, which here is named `bootstrap` but can be whatever you like. This will be the hostname of the bootstrap node in your Tailscale network.

```
uvx shiftedstorage create --ts-authkey "YOUR KEY HERE" --cluster-peername bootstrap --output compose.yml
```

This should write a Docker Compose configuration to `compose.yaml`.

**DANGER: Be careful to not make this compose file public since it contains secret keys!**

### Start Bootstrap

You can now start up your bootstrap node with:

```bash
$ docker compose up -d
```

If you want to stop the service at any time you can execute this command, as long as you are in the `shiftedstorage` directory:

```
$ docker compose stop
```

### Let Others Join

In order to let others join the network you will need to share a modified version of the compose file with them via a secure channel (e.g. WhatsApp or Signal).

```
uvx shiftedstorage clone --input compose.yml --cluster-peername acme --output acme-compose.yml --bootstrap-host boostrap
```

This will write out a `acme-compose.yml` file which you can share via a secure channel with someone running a machine at that organization.

You should be able to run this using `docker compose`, but for the original Shift-FFDW project we have been standardizing on partners using a [QNAP NAS](https://www.qnap.com/en-us/product/tbs-h574tx) which makes is easy to set up. You can use whatever device you want as long as you can run Docker on it and it has at least 4GB of memory (more couldn't hurt).

For people with a QNAP you can:

1. Install Container Station from Apps if it's not already available.
2. Open Container Station.
3. Click `Applications` option in the menu on the left.
4. Click the `Create` button.
5. In the Application Name box enter `shiftedstorage`
6. Paste the contents of the supplied `compose.yml` file into the text box.
7. Click the `create` button.
8. Click the `Containers` option in the menu on the left.
9. Verify that you see three containers running.

## Working With Storage

The shiftedstorage utility offers some functionality to add and remove content from storage. These are really just wrappers around the `ipfs-cluster-ctl` command, which you can choose to use directly of course.

### Adding Content

Add a file:

```
uvx shiftedstorage add --cluster-peername acme my-file.pdf
```

or a directory:

```
uvx shiftedstorage add --cluster-peername acme my-directory/
```

### Checking Status

See what the status of a given CID is in the cluster:

```
uvx shiftedstorage status --cluster-peername acme <cid>
```

### Get a CID

Fetch a CID and store as a local file:

```
uvx shiftedstorage get --cluster-peername acme --output /path/to/file <cid>
```

### Removing Content

Remove a CID from the cluster:

```
uvx shiftedstorage rm --cluster-peername acme <cid>
```

[uv]: https://docs.astral.sh/uv/getting-started/installation/
[Docker]: https://www.docker.com/get-started/
[Tailscale]: https://tailscale.com/
[IPFS Cluster]: https://ipfscluster.io/
[Git]: https://git-scm.com/
[Filecoin Foundation for the Decentralized Web]: https://ffdweb.org/
[Modeling Sustainable Futures: Exploring Decentralized Digital Storage for Community Based Archives]: https://www.shiftcollective.us/ffdw
[Shift Collective]: https://www.shiftcollective.us/
