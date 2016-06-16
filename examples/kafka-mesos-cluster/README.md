# Requirements

## AWS
- mesos
- marathon
- mesos-consul
- marathon-consul
- kafka-mesos

## Local
- aws cli
- aws creadentials
- sshkey `reference.pem` for accessing to the aws cluster

Part of this stuff could be installed with [cloud deploy grid](https://github.com/elodina/cloud-deploy-grid#common-usage-scenario-for-mesos-on-aws)
and other part is described later in `README`.
Turn on VPN connection to the [cluster](https://github.com/elodina/dexter#mesos-cluster-vpn-access)

# Setup infrastructure

## Add ability for user `manager` to ssh with keys
- ssh to the `_access_ip` provided from `dexter` steps `ssh centos@_access_ip -i path/to/reference.pem`
- `sudo -i`
- `cat /home/centos/.ssh/authorized_keys >> /home/manager/.ssh/authorized_keys`
- add config to the local `~/.ssh/config`:
```
Host terminal
    HostName _access_ip
    User manager
    IdentityFile /path/to/reference.pem
```
- try to connect `ssh terminal` if successfull, then disconnect

## Create basic infrastructure
- `cd examples/kafka-mesos-cluster/`
- copy all artifacts to the s3 and terminal `make copy`
- `ssh terminal`
- create basic infrastructure `./infrastructure.sh`

## Setup pisaura and failure
- Create `pisaura` application at the marathon `make app_create`
- update `failure_scenario.json` with hostnames from `mesos ui`, update section `hosts` with list of hostnames of kafka-mesos
where failure should be produced, update section `failures -> healthcheck` with brokers hostsname
- create failure `make create_failure`
- status of failure could be fetched `make status_failure`

## Failure steps
- make sure tested service is ok before inuducing failure
- make failure(block kafka port with iptables)
- check status of service after failure
- revert service status by remove iptables rule
