# zabbix-templates-docker


## SElinux


```
grep zabbix_agent_t /var/log/audit/audit.log | grep denied | audit2allow -M zabbix_agent
semodule -i zabbix_agent.pp
```
