#!/bin/sh
set -ex

# remove any preexisting bootstrap nodes since we want to keep all traffic private
ipfs bootstrap rm all

# non bootstrap nodes will define a bootstrap to learn about the network
if [[ -n "${IPFS_BOOTSTRAP}" ]]; then
    ipfs bootstrap add "${IPFS_BOOTSTRAP}"
fi
