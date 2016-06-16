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

import argparse
import logging
import time
import os
import sys

from framework.scheduler import run as scheduler_run
from framework.executor import main as executor_main
from framework.api import run_api

logging.basicConfig(level=logging.DEBUG)


def handle_arguments():
    parser = argparse.ArgumentParser(description='Pisaura Mesos framework')
    parser.add_argument(
        'type', nargs='?', choices=["scheduler", "executor"],
        help="Select what part of framework is needed")
    parser.add_argument(
        '--master', dest='master', action='store', default=None,
        help='Mesos master url')
    parser.add_argument(
        '--api', dest='api', action='store', default="0.0.0.0:8000",
        help='host:port for REST API')
    parser.add_argument(
        '--resource', dest='resource', action='append', default=[],
        help='Resource will be copied to the executor')
    parser.add_argument(
        '--framework-name', dest='framework_name', action='store',
        default="pisaura", help='Displayed title of framework')
    parser.add_argument(
        '--task-retry', dest='task_retry', action='store', default=5,
        help='How many times mesos tasks will be restarted if it failed')
    parser.add_argument(
        '--executor-command', dest='executor_command', action='store',
        help='Executor command')

    args = parser.parse_args()
    parsed_options = (args.type, args.master, args.api, args.resource,
                      args.framework_name, args.task_retry, args.executor_command)
    is_all_options_correct = all(map(lambda i: i is not None, parsed_options))

    if not is_all_options_correct and args.type == "scheduler":
        sys.exit("Not all required args are given: " + str(args))

    return parsed_options


def scheduler_main(master, api, resource, framework_name, task_retry, executor_command):
    resources = []

    for res in resource:
        resources.append(os.path.join(os.getcwd(), res))

    application_config = {
        'master': master, 'api': api, 'resources': resource,
        'framework_name': framework_name, 'task_retry': task_retry,
        'executor_command': executor_command
    }
    logger = logging.getLogger("pisaura.cli")
    logger.debug(application_config)
    scheduler = scheduler_run(application_config)
    # TODO: add validation
    api_host, api_port = application_config['api'].split(":")
    api_port = int(api_port)
    thread = run_api(scheduler, api_host, api_port)

    try:
        # wait threads
        while thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()


def main():
    ftype, master, api, resource, framework_name, task_retry, executor_command = handle_arguments()

    if ftype == "scheduler":
        scheduler_main(master, api, resource, framework_name, task_retry, executor_command)
    elif ftype == "executor":
        executor_main()
    else:
        sys.exit("Unknown error")

if __name__ == '__main__':
    main()
