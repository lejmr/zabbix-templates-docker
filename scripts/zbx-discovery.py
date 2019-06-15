#!/usr/bin/env python
import docker
import json

client = docker.from_env()
disc = [ {"#NAME":x.name, "#ID": x.id} for x in client.containers.list()]
ret = {"DATA": disc}

print(json.dumps(ret))
print(x)
stats = x.stats(stream=False, decode=True)
#print(json.dumps(stats))

# https://github.com/moby/moby/blob/eb131c5383db8cac633919f82abad86c99bffbe5/cli/command/container/stats_helpers.go#L175
# CPU 
cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
util = 100.0*cpu_delta/system_delta*len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
print(util)

# NETWORK
rx = [x[1]["rx_bytes"] for x in stats["networks"].items()]
tx = [x[1]["tx_bytes"] for x in stats["networks"].items()]
print(sum(rx))
print(sum(tx))

# blkio
blkio = {}
for i in stats["blkio_stats"]["io_service_bytes_recursive"]:
  op = i["op"].lower()
  if not op in blkio:
    blkio[op] = 0.0
  blkio[op] += i["value"]

print(blkio)



