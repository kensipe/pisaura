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
import threading
from collections import namedtuple
import json
import logging

try:
    from mesos.native import MesosExecutorDriver
    from mesos.interface import Executor
    from mesos.interface import mesos_pb2
except ImportError:
    from mesos import Executor, MesosExecutorDriver
    import mesos_pb2

from fabric.api import run, local, put, env, warn_only
from fabric.tasks import execute


logger = logging.getLogger("executor")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# falure steps
INIT, BEFORE_FAILURE, AFTER_FAILURE, AFTER_REVERT = range(4)


class FailureExecutor(Executor):
    """
    Runs failure based on given from scheduler config.
    For each failure in config do next steps:
        - run healthcheck script, if failed stop failure running
        - copy falure inducer script to the tested hosts
        - run failure inducer script and store result
        - run healthcheck and store result
        - run failure reverter and store result
        - run healthcheck and store result
        If sys code of scripts runned on each step is succeeded failure running is succeeded,
        otherwise is failed. If config key `failfast` is `true` and failure running is failed
        execution of next failure will be stopped.

    """

    def __init__(self):
        self.logger = logger

    def get_config(self, json_config):
        def object_hook(d): return namedtuple('Config', d.keys())(*d.values())

        return json.loads(
            json_config,
            object_hook=object_hook)

    def run_failure(self, conn_config, failure_config, hostname):
        statuses = []

        def append_res(step, res):
            statuses.append((step, res.succeeded, str(res)))

        def healthcheck(step):
            healthcheck_command = " ".join(
                failure_config.healthcheck + ["--step=%s" % step])
            with warn_only():
                return local(healthcheck_command)

        def task():
            env.user = conn_config.username

            if conn_config.password:
                env.password = conn_config.password

            if conn_config.key_filename:
                env.key_filename = conn_config.key_filename

            res = healthcheck(BEFORE_FAILURE)
            self.logger.debug("Run healthcheck before failure, succeeded: %s", res.succeeded)
            append_res('healthcheck before failure', res)
            if res.failed:
                return

            self.logger.debug("Run inducer")
            inducer_command = " ".join(failure_config.inducer)
            inducer_file_name = failure_config.inducer[0].split("/")[-1]
            put(inducer_file_name, failure_config.inducer[0], mode=0755)
            res = run(inducer_command, quiet=True)

            append_res('failure', res)

            self.logger.debug("Run healthcheck after inducer, succeeded: %s", res.succeeded)
            append_res('healthcheck after failure', healthcheck(AFTER_FAILURE))

            self.logger.debug("Run reverter")
            reverter_command = " ".join(failure_config.reverter)
            reverter_file_name = failure_config.reverter[0].split("/")[-1]
            put(reverter_file_name, failure_config.reverter[0], mode=0755)
            res = run(reverter_command, quiet=True)

            append_res('reverter', res)

            self.logger.debug("Run healthcheck after reverter, succeeded: %s", res.succeeded)
            append_res('healthcheck after reverter', healthcheck(AFTER_REVERT))

        execute(task, host=hostname)

        self.logger.debug("Statuses %s", statuses)

        all_succeeded = all(i[1] for i in statuses) or False

        return all_succeeded, statuses

    def process_host(self, config, hostname):
        self.logger.debug("Process host %s with failures %s", hostname, config.failures)

        failures_statuses = {
            failure_config.name: None
            for failure_config in config.failures
        }

        for failure_config in config.failures:
            succeeded, statuses = self.run_failure(config.ssh, failure_config, hostname)
            failures_statuses[failure_config.name] = [succeeded, statuses]
            if config.failfast and not succeeded:
                self.logger.info("Failfast after scenario %s", failure_config.name)
                break

        return failures_statuses

    def process_hosts(self, config):
        self.logger.debug("Start hosts processing")
        loglevel = getattr(logging, config.loglevel.upper())
        self.logger.setLevel(loglevel)

        return {
            hostname: self.process_host(config, hostname)
            for hostname in config.hosts
        }

    def launchTask(self, driver, task):
        self.logger.debug("Launch task %s", task)

        def run_task():
            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_RUNNING
            driver.sendStatusUpdate(update)

            config = self.get_config(task.data)
            self.logger.debug("Parsed config %s", config)
            statuses = self.process_hosts(config)

            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_FINISHED

            # collect stdout/stderr
            update.data = json.dumps(statuses)

            self.logger.debug("Task finished")
            driver.sendStatusUpdate(update)
            return

        thread = threading.Thread(target=run_task)
        thread.start()


def main():
    driver = MesosExecutorDriver(FailureExecutor())
    sys.exit(0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1)


if __name__ == "__main__":
    main()
