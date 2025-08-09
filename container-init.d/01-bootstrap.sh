#!/bin/sh
set -ex
ipfs bootstrap rm all
# uncomment on non-bootstrap nodes to tell ipfs where to find other peers
# ipfs bootstrap add "/ip4/$PRIVATE_PEER_IP_ADDR/tcp/4001/ipfs/$PRIVATE_PEER_ID"
