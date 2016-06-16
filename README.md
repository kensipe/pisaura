# PISAURA - A Failure runner on Mesos Scheduler

Pisaura is is a scheduler that runs failure scenarios on Mesos.

Pisaura is being actively developed by Elodina Inc as an open source project distributed under the Apache License, Version 2.0. We welcome others to try to run pisaura and provide new fatebooks for new systems and collaborate around a full system for helping to provide confidence that what we are running is always able to fail sucesfully.

# Requirements
- mesos==0.23.0
- Mesos master/slave
    * [python mesos egg](https://open.mesosphere.com/downloads/mesos/#apache-mesos-0.23.0)
    * pycrypto
- Docker(locally for building dist)

# Failure scenario
```python
{
    'service': 'tested service',
    'cpu': 1,
    'mem': 200,
    'hosts': ['hostname1', 'hostname2'],
    'ssh': {
        'username': '',
        'password': '',
        'identity_file': ''
    },
    'loglevel': 'debug',
    'failfast': True,
    'failures': [
        {
            'name': '',
            'inducer': ["/path/to/inducer1.sh", "arg1", "argN"],
            'reverter': ["/path/to/reverter1.sh", "arg1", "argN"],
            'healthcheck': ["/path/to/healthcheck1.sh", "arg1", "argN"]
        },
        {
            'name': '',
            'inducer': ["/path/to/inducerN.sh", "arg1", "argN"],
            'reverter': ["/path/to/reverterN.sh", "arg1", "argN"],
            'healthcheck': ["/path/to/healthcheckN.sh", "arg1", "argN"]
        }
    ]
}
```

## Main config

| Section | Value |
| --------| ------|
| service | title of tested service |
| cpu | needed cpu resources for handling tasks |
| mem | needed memory resources for handling tasks|
| hosts | list of service's hosts |
| ssh | parameters for ssh connection, used for copy inducer and reverter to the hosts and execute them |
| loglevel | level of verbosity, output of logs is stdout/stderr |
| failfast | stop testing if healthcheck didn't passed |
| failures | list of objects with faliures and revertes |


## Failure config

| Section | Value |
| --------| ------|
| name    | output name for failure |
| inducer | script for producing failure, represented as a list, format: `["/path/to/script.sh", "arg1", "argN"]`, will be copied to the tested host |
| reverter | script for reverting state of service, represented as a list, format: `["/path/to/script.sh", "arg1", "argN"]`, will be copied to the tested host |
| healthcheck | script for checking is service in the working state, represented as a list, format: `["/path/to/script.sh", "arg1", "argN"]`, `won't` be copied to the tested host |


## Build zipapp(currently only Centos 7 is supported)
- `make build_zip_centos7`


## Examples
- [Kafka-mesos](examples/kafka-mesos-cluster/README.md)
