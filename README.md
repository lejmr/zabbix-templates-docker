# zabbix-templates-docker


## SElinux


```
grep zabbix_agent_t /var/log/audit/audit.log | grep denied | audit2allow -M zabbix_agent2
semodule -i zabbix_agent.pp
```
https://github.com/monitoringartist/zabbix-docker-monitoring

```
type=AVC msg=audit(1560622014.990:33496): avc:  denied  { write } for  pid=30423 comm="python" name="tmp" dev="dm-0" ino=33554504 scontext=system_u:system_r:zabbix_agent_t:s0 tcontext=system_u:object_r:tmp_t:s0 tclass=dir
type=AVC msg=audit(1560622181.498:33526): avc:  denied  { connectto } for  pid=3515 comm="python" path="/run/docker.sock" scontext=system_u:system_r:zabbix_agent_t:s0 tcontext=system_u:system_r:container_runtime_t:s0 tclass=unix_stream_socket
```

checkmodule -M -m -o zabbix-docker.mod zabbix-docker.te
semodule_package -o zabbix-docker.pp -m zabbix-docker.mod
semodule -i zabbix-docker.pp
