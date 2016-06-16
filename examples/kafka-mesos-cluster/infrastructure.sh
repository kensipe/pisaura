#!/bin/sh

export cluster_name=pisaurakafkatest

printf '\n>> run Exhibitor'
wget http://elodina-demo.s3.amazonaws.com/exhibitor.json

printf '\n>> put exhibitor json to marathon\n'
curl -X PUT -d@exhibitor.json -H "Content-Type: application/json" http://leader.mesos.service.${cluster_name}:18080/v2/apps/exhibitor-mesos

printf '\n>> Check to ensure DNS entries are created\n'
service="exhibitor-mesos"
until host ${service}.service; do
    echo "$service is not yet responding"
    sleep 5
done
until curl -qs http://leader.mesos.service.${cluster_name}:18080/v2/apps/${service} | jq .app.tasksRunning | grep -q -v 0; do
    echo "$service is still dead"
    sleep 5
done
echo "$service is alive"

printf '\n>> export EM_API\n'
export EM_API=http://exhibitor-mesos.service:31100

printf '\n>> get mesos-exhibitor jar\n'
wget http://repo.elodina.s3.amazonaws.com/mesos-exhibitor-0.1.jar

printf '\n>> get sh script\n'
wget http://repo.elodina.s3.amazonaws.com/exhibitor-mesos.sh
chmod a+x exhibitor-mesos.sh

printf '\n>> add servers\n'
./exhibitor-mesos.sh add 20..22 --cpu 0.2 --mem 768 --port 31150

printf '\n>> configure servers\n'
./exhibitor-mesos.sh config 20..22 --configtype zookeeper --zkconfigconnect zookeeper.service:2181 --zkconfigzpath /exhibitor/config --zookeeper-install-directory /tmp/zookeeper --zookeeper-data-directory /tmp/zkdata

printf '\n>> start servers\n'
./exhibitor-mesos.sh start 20..22 --timeout 5min

printf '\n>> run DSE\n'
wget http://elodina-demo.s3.amazonaws.com/dse.json

printf '\n>> put DSE json to marathon\n'
curl -X PUT -d@dse.json -H "Content-Type: application/json" http://leader.mesos.service.${cluster_name}:18080/v2/apps/dse-mesos

printf '\n>> Check to ensure DNS entries are created\n'
service="dse-mesos"
until host ${service}.service; do
    echo "$service is not yet responding"
    sleep 5
done
until curl -qs http://leader.mesos.service.${cluster_name}:18080/v2/apps/${service} | jq .app.tasksRunning | grep -q -v 0; do
    echo "$service is still dead"
    sleep 5
done
echo "$service is alive"

until tcping -q -t 1 exhibitor-20.service 2181; do
    echo "zookeeper is not yet live"
    sleep 5
done
echo "zookeeper is alive"

printf '\n>> run Kafka\n'
wget http://elodina-demo.s3.amazonaws.com/kafka.json

printf '\n>> put kafka json to marathon\n'
curl -X PUT -d@kafka.json -H "Content-Type: application/json" http://leader.mesos.service.${cluster_name}:18080/v2/apps/kafka-mesos

printf '\n>> Check to ensure DNS entries are created\n'
service="kafka-mesos"
until host ${service}.service; do
    echo "$service is not yet responding"
    sleep 5
done
until curl -qs http://leader.mesos.service.${cluster_name}:18080/v2/apps/${service} | jq .app.tasksRunning | grep -q -v 0; do
    echo "$service is still dead"
    sleep 5
done
echo "$service is alive"

printf '\n>> export KM_API\n'
export KM_API=http://kafka-mesos.service:6999

printf '\n>> get kafka-mesos tgz\n'
wget http://elodina-demo.s3.amazonaws.com/kafka-mesos.tar.gz
tar -xzf kafka-mesos.tar.gz

printf '\n>> add servers\n'
./kafka-mesos.sh broker add 0..2 --cpus 0.1 --mem 1024 --options log.retention.hours=12,log.retention.bytes=104857600 --constraints hostname=unique --port 31250

printf '\n>> start servers\n'
./kafka-mesos.sh broker start 0..2 --timeout 300s

printf '\n>> run schema registry\n'
wget http://elodina-demo.s3.amazonaws.com/schema-registry.json

printf '\n>> put schema registry json to marathon\n'
curl -X PUT -d@schema-registry.json -H "Content-Type: application/json" http://leader.mesos.service.${cluster_name}:18080/v2/apps/schema-registry

service="schema-registry"
until host ${service}.service; do
    echo "$service is not yet responding"
    sleep 5
done
until curl -qs http://leader.mesos.service.${cluster_name}:18080/v2/apps/${service} | jq .app.tasksRunning | grep -q -v 0; do
    echo "$service is still dead"
    sleep 5
done
echo "$service is alive"

echo "wait a little bit..."
sleep 60
