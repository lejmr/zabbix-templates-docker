#!/usr/bin/env python
import docker
import json
import sys
import grp
import os
import pickle
import time


CACHE_PATH = "/tmp/"
CACHE_TIME_S = 60


def _zbx_unsupported(msg):
  print(": ".join(["ZBX_NOTSUPPORTED", msg]))
  sys.exit(1)

def get_discovery(client):
  disc = [ {"{#NAME}":x.name, "{#ID}": x.id} for x in client.containers.list()]
  return json.dumps({"data": disc})

def _cache_data(fp, client, contid):
  x = client.containers.get(contid)
  data = x.stats(stream=False, decode=True)
  with open(fp, "w") as f:
    pickle.dump(data, f)
  return data

def _get_stats(client, contid):
  fp = os.path.join(CACHE_PATH, "zbx_docker_stats.cache")
  if not os.path.exists(fp):   
    return _cache_data(fp, client, contid)
  if time.time() - os.stat(fp).st_mtime > CACHE_TIME_S:
    return _cache_data(fp, client, contid)
  with open(fp, "r") as f:
    return pickle.load(f)

def _get_attrs(client, contid):
  return client.containers.get(contid).attrs

def get_mem(client, contid, tp="usage"):
  stats = _get_stats(client, contid)
  extp = None
  if "/" in tp:
    tp, extp = tp.split("/")[:2]

  if not tp in stats["memory_stats"]:
    _zbx_unsupported("unsupported argument {}".format(tp))

  if extp:
    if not extp in stats["memory_stats"][tp]: 
      _zbx_unsupported("unsupported argument {}".format(extp))
    return stats["memory_stats"][tp][extp]
  return stats["memory_stats"][tp]
  
def get_cpu(client, contid, tp="total_usage"):
  # https://github.com/moby/moby/blob/eb131c5383db8cac633919f82abad86c99bffbe5/cli/command/container/stats_helpers.go#L175
  stats = _get_stats(client, contid)
  cpu_delta = stats["cpu_stats"]["cpu_usage"][tp] - stats["precpu_stats"]["cpu_usage"][tp]
  system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
  return  100.0*cpu_delta/system_delta*len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])

def get_net(client, contid, metric="rx_bytes"):
  stats = _get_stats(client, contid)
  metrics = set([item for x in stats["networks"].items() for item in x[1].keys()])
  if not metric in metrics:
    _zbx_unsupported("unsupported metric {}".format(metric))
  it = [x[1][metric] for x in stats["networks"].items()]
  return sum(it)

def get_blkio(client, contid, metric="read"):
 stats = _get_stats(client, contid)
 blkio = {}
 for i in stats["blkio_stats"]["io_service_bytes_recursive"]:
   op = i["op"].lower()
   if not op in blkio:
     blkio[op] = 0.0
   blkio[op] += i["value"]
 if not metric in blkio:
   _zbx_unsupported("unsupported metric {}".format(metric))
 return blkio[metric]

def get_id(client, contid):
  x = client.containers.get(contid)
  return x.id

def get_status(client, contid):
  x = client.containers.get(contid)
  return x.status

def get_created(client, contid):
  attrs = _get_attrs(client, contid)
  return attrs["Created"]
 
if __name__ == "__main__":
  # Validate access rights
  if not "docker" in [x.gr_name for x in grp.getgrall()]:
    print("ZBX_NOTSUPPORTED: agent needs docker group do be assigned")
    sys.exit(1)

  # Connect to docker socket
  client = docker.from_env()

  # Handle arguments
  allowed = ["discovery", "mem", "cpu", "net", "blkio", "id", "status", "created"]
  if len(sys.argv) < 2:
    _zbx_unsupported("Undefined argument. Allowed arguments {}".format(", ".join(allowed)))
  if not sys.argv[1] in allowed:
    print("ZBX_NOTSUPPORTED: Unsupported argument {}".format(sys.argv[1]))
    sys.exit(1)
 
  # Call requested function
  func = locals()["get_{}".format(sys.argv[1]).lower()]
  args = sys.argv[1:]
  args[0] = client
  ret = func(*args)
  print(ret)
