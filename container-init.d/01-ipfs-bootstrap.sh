#!/bin/sh
set -ex

# remove any preexisting bootstrap nodes since we want to keep all traffic private
ipfs bootstrap rm all

# non-bootstrap nodes will need to define a bootstrap to learn about the network
if [[ -n "${IPFS_BOOTSTRAP}" ]]; then
    ipfs bootstrap add "${IPFS_BOOTSTRAP}"
fi

TAILSCALE_IP=`ip -f inet addr show tailscale0 | sed -En -e 's/.*inet ([0-9.]+).*/\1/p'`

ipfs config --json Addresses.Swarm '["/ip4/0.0.0.0/tcp/4001", "/ip6/::/tcp/4001"]'
ipfs config --json Addresses.Announce [\"/ip4/${TAILSCALE_IP}/tcp/4001\"]
