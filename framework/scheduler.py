#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

import sys
import logging
import signal
import uuid
import json
import datetime
from threading import Thread, current_thread

import mesos.interface
from mesos.interface import mesos_pb2
import mesos.native


logging.basicConfig(level=logging.DEBUG)


def run_driver(*args, **kwargs):
    """
    Starts mesos driver in separate thread.
    Stops driver in case when SIGINT is received at the main thread.

    """

    driver = mesos.native.MesosSchedulerDriver(*args, **kwargs)

    def run_driver_async():
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()
        sys.exit(status)

    framework_thread = Thread(target=run_driver_async)
    framework_thread.daemon = True
    framework_thread.start()

    if current_thread().name == "MainThread":
        signal.signal(signal.SIGINT, lambda signal, frame: driver.stop())


class FailureScheduler(mesos.interface.Scheduler):
    """
    Starts executor for each failure config.
    Passes needed config for running failure using task.data.

    """

    def __init__(self, executor, logger, task_retry):
        self.executor = executor
        self.services_statuses = {}
        self.logger = logger
        self.task_retry = task_retry

    def make_task_prototype(self, offer, cpus, mem, service_name):
        """
        Creates task with needed resources
        """

        task = mesos_pb2.TaskInfo()
        task_id = uuid.uuid4().hex
        task.task_id.value = task_id
        task.slave_id.value = offer.slave_id.value
        task.name = "pisaura-failure-runner-{}".format(service_name.replace(" ", "-"))

        cpus_r = task.resources.add()
        cpus_r.name = "cpus"
        cpus_r.type = mesos_pb2.Value.SCALAR
        cpus_r.scalar.value = cpus

        mem_r = task.resources.add()
        mem_r.name = "mem"
        mem_r.type = mesos_pb2.Value.SCALAR
        mem_r.scalar.value = mem

        return task

    def add_service(self, service):
        self.services_statuses[service['service']] = {
            'service': service,
            'status': mesos_pb2.TASK_STAGING,
            'tasks': [],
            'logs': [],
            'updated': str(datetime.datetime.utcnow()),
            'created': str(datetime.datetime.utcnow())
        }

    def make_task(self, offer, service):
        task = self.make_task_prototype(
            offer, service['cpus'], service['mem'], service['service'])
        task.data = json.dumps(service)
        task.executor.MergeFrom(self.executor)

        if service['service'] in self.services_statuses:
            self.services_statuses[service['service']]['status'] = None
            self.services_statuses[service['service']]['tasks'].append(task.task_id.value)
        else:
            self.services_statuses[service['service']] = {
                'service': service,
                'status': None,
                'tasks': [task.task_id.value]
            }
        return task

    def registered(self, driver, frameworkId, masterInfo):
        self.logger.info("Registered with framework ID %s" % frameworkId.value)

    def log_offer_stat(self, offer):
        offerCpus = 0
        offerMem = 0
        for resource in offer.resources:
            if resource.name == "cpus":
                offerCpus += resource.scalar.value
            elif resource.name == "mem":
                offerMem += resource.scalar.value

        self.logger.debug(
            "Received offer %s with cpus: %s and mem: %s", offer.id.value,
            offerCpus, offerMem)

    def get_next_service(self):
        retry_statuses = [mesos_pb2.TASK_ERROR, mesos_pb2.TASK_FAILED, mesos_pb2.TASK_STAGING]

        for service_name in self.services_statuses:
            self.logger.debug("Trying to commit %s as next service", service_name)

            tasks_count = len(self.services_statuses[service_name]['tasks'])
            status = self.services_statuses[service_name]['status']

            if status not in retry_statuses:
                continue

            if status is None and tasks_count:
                continue

            if tasks_count < self.task_retry:
                return self.services_statuses[service_name]['service']
            else:
                self.logger.debug(
                    "retry count exceeded for service %s", service_name)

    def resourceOffers(self, driver, offers):
        for offer in offers:
            self.log_offer_stat(offer)
            service = self.get_next_service()

            self.logger.debug("Next service is %s", service)

            if not service:
                driver.declineOffer(offer.id)
                return

            task = self.make_task(offer, service)
            self.logger.info("Launching task {task} "
                             "using offer {offer}.".format(task=task.task_id.value,
                                                           offer=offer.id.value))
            tasks = [task]
            driver.launchTasks(offer.id, tasks)

    def statusUpdate(self, driver, update):
        self.logger.debug(
            "Task %s is in state %s, message: %s" % (
                update.task_id.value, mesos_pb2.TaskState.Name(update.state), update.message))

        for service_name in self.services_statuses:
            if update.task_id.value in self.services_statuses[service_name]['tasks']:
                self.logger.info(
                    "Move service %s to the state %s",
                    service_name, mesos_pb2.TaskState.Name(update.state))
                self.services_statuses[service_name]['status'] = update.state
                self.services_statuses[service_name]['logs'] = json.loads(update.data or "[]")
                self.services_statuses[service_name]['updated'] = str(datetime.datetime.utcnow())

    def frameworkMessage(self, driver, executor_id, slave_id, message):
        self.logger.info("Received framework message %s", message)


def init_executor(app_config):
    """
    Creates mesos executor using given config dict.

    """

    uris = app_config['resources']

    executor = mesos_pb2.ExecutorInfo()
    executor.executor_id.value = "%s-executor" % app_config['framework_name']
    executor.command.value = app_config['executor_command']

    for uri in uris:
        uri_proto = executor.command.uris.add()
        uri_proto.value = uri

        uri_proto.extract = False if not uri.endswith(".tar.gz") else True

    executor.name = app_config['framework_name'].capitalize()
    return executor


def run(application_config):
    """
    Main function for setup and run FailureScheduler.

    """

    executor = init_executor(application_config)

    framework = mesos_pb2.FrameworkInfo()
    framework.user = ""  # Have Mesos fill in the current user.
    framework.name = application_config['framework_name']
    logger = logging.getLogger("pisaura.scheduler")
    scheduler = FailureScheduler(
        executor, logger, application_config['task_retry'])

    run_driver(scheduler, framework, application_config['master'])
    return scheduler
