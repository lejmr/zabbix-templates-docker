# zabbix-templates-docker


## SElinux

```
checkmodule -M -m -o zabbix-docker.mod selinux/zabbix-docker.te
semodule_package -o zabbix-docker.pp -m zabbix-docker.mod
semodule -i zabbix-docker.pp
```
