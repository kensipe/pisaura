copy:
	aws s3 cp framework.zip_ s3://elodina-cobra-demo-kafka --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers; \
    aws s3 cp failure_producer.sh s3://elodina-cobra-demo-kafka --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers; \
    aws s3 cp healthcheck.py s3://elodina-cobra-demo-kafka --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers; \
    aws s3 cp pykafka_centos7.zip_ s3://elodina-cobra-demo-kafka --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers; \
    scp infrastructure.sh terminal:~/; \
    ssh terminal "chmod +x infrastructure.sh"

create_failure:
	curl -s -X POST -d@failure_scenario.json -H "Content-Type: application/json" http://`curl -s -H "Content-Type: application/json" http://leader.mesos.service.$(cluster_name):18080/v2/apps/pisaura | jq -r '.app | .tasks[] | .host'`:8000/

status_failure:
	@curl -s -H "Content-Type: application/json" http://`curl -s -H "Content-Type: application/json" http://leader.mesos.service.$(cluster_name):18080/v2/apps/pisaura | jq -r '.app | .tasks[] | .host'`:8000/ | python -m json.tool

app_create:
	@curl -s -X PUT -d@pisaura.json -H "Content-Type: application/json" http://leader.mesos.service.$(cluster_name):18080/v2/apps/pisaura | python -m json.tool

app_restart:
	@curl -s -X POST -H "Content-Type: application/json" http://leader.mesos.service.$(cluster_name):18080/v2/apps/pisaura/restart | python -m json.tool && sleep 5
