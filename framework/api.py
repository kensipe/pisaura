from wsgiref import simple_server
from threading import Thread, current_thread
import falcon
import signal
import json
import jsonschema
from copy import copy

from mesos.interface import mesos_pb2

from framework.api_schema import schema


class TestedServices(object):
    def __init__(self, scheduler):
        self.scheduler = scheduler

    def on_get(self, req, res):
        """
        Returns list of failures with states and info.

        """

        res.status = falcon.HTTP_200
        services = [
            {
                'name': service_name,
                'created': service_data['created'],
                'updated': service_data['updated'],
                'logs': service_data['logs'],
                'tasks': service_data['tasks'],
                'status': mesos_pb2.TaskState.Name(service_data['status'])
            }
            for service_name, service_data in self.scheduler.services_statuses.items()
        ]
        res.body = json.dumps(services)

    def on_post(self, req, res):
        """
        Creates failure config.

        """

        req_body = req.stream.read().decode('utf-8')
        doc = json.loads(req_body)
        validator = jsonschema.Draft3Validator(schema)
        errors = list(validator.iter_errors(doc))

        if errors:
            res.status = falcon.HTTP_400
            res.body = json.dumps(errors)

        # check if service already present and it's status is RUNNING
        existent_service = self.scheduler.services_statuses.get(doc['service'])
        if_service_cant_be_added = existent_service and existent_service['status'] == mesos_pb2.TASK_RUNNING

        if if_service_cant_be_added:
            res.status = falcon.HTTP_400
            message = ['Service already exists']
            res.body = json.dumps(message)
        else:
            res.status = falcon.HTTP_201
            self.scheduler.add_service(copy(doc))


def prepare_api(scheduler):
    app = falcon.API()
    tested_services = TestedServices(scheduler)

    app.add_route('/', tested_services)
    app.add_route('/services', tested_services)

    return app


def run_api(scheduler, address, port):
    app = prepare_api(scheduler)
    httpd = simple_server.make_server(address, port, app)

    if current_thread().name == "MainThread":
        signal.signal(signal.SIGINT, lambda s, f: httpd.shutdown())

    api_thread = Thread(target=httpd.serve_forever)
    api_thread.daemon = True
    api_thread.start()

    return api_thread
