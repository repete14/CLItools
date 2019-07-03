from datetime import datetime, timedelta

import logging
import logging.config
import os
import pytz
import sys
from kubernetes import client, config


def main():
    while True:
        # run the main pod information script, and catch any ctl-c script end command
        try:
            get_stuck_pods()
        except KeyboardInterrupt:
            break


def get_stuck_pods():
    # set up logging configuration
    config_file = os.path.join(sys.path[0], 'logging.conf')
    logging.config.fileConfig(config_file)
    logger = logging.getLogger('output')

    # filters for get pods
    label_selector = "jcx.inst.component=webapp"
    limit = 100

    # initializing stuck pod variables
    pod_list_stuck = []
    pod_list_starting = []
    pod_list_old = []
    starting_cutoff = timedelta(minutes=10)
    old_cutoff = timedelta(hours=8)

    # collecting list of webapp pods from jcx-prod-us-east
    config.load_kube_config(context="jcx-prod-us-east")
    api = client.CoreV1Api()
    pod_list_us = api.list_pod_for_all_namespaces(label_selector=label_selector, limit=limit)

    # collecting list of webapp pods from jcx-prod-eu
    config.load_kube_config(context="jcx-prod-eu")
    api = client.CoreV1Api()
    pod_list_eu = api.list_pod_for_all_namespaces(label_selector=label_selector, limit=limit)

    # combine eu and us pod lists
    pod_list = pod_list_us.items + pod_list_eu.items

    # filter pods into category lists based on age of pod
    if len(pod_list) != 0:
        for pod in pod_list:
            try:
                if not pod.status.container_statuses[0].ready:
                    age = datetime.now(pytz.utc) - pod.metadata.creation_timestamp
                    if age < starting_cutoff:
                        pod_list_starting.append(pod)
                    elif age > old_cutoff:
                        pod_list_old.append(pod)
                    else:
                        pod_list_stuck.append(pod)
            except Exception as e:
                logger.debug("failed on pod: ", pod.metadata.namespace, "  ", pod.metadata.name, e)

        # display results
        os.system('cls||clear')
        logger.debug("{:^33} {:^16} {:^19} {:^6} {:^20}".format("namespace",
                                                                "Pod",
                                                                "Age (H:M:S)",
                                                                "Loc",
                                                                "installation name"))

        logger.debug("{:^94}".format("--------------- STUCK PODS (>10 mins) ---------------"))
        print_pod_list(pod_list_stuck)

        logger.debug("{:^94}".format("------------ IN PROGRESS PODS (<10 mins) ------------"))
        print_pod_list(pod_list_starting)

        logger.debug("{:^94}".format("----------- VERY OLD DEAD PODS (>8 hours) -----------"))
        print_pod_list(pod_list_old)

    else:
        logger.debug("No stuck pods. Continue to monitor")


def print_pod_list(pod_list):
    # set up logging configuration
    config_file = os.path.join(sys.path[0], 'logging.conf')
    logging.config.fileConfig(config_file)
    logger = logging.getLogger('output')

    for pod in pod_list:
        # gather pod data
        namespace = pod.metadata.namespace
        webapp = pod.metadata.name
        age = datetime.now(pytz.utc) - pod.metadata.creation_timestamp
        age = str(age)[0:len(str(age)) - 7]
        location = pod.metadata.labels[u'jcx.environment'][4:6]
        installation = pod.spec.containers[0].env[2].value

        # print results
        logger.debug("{:<33} {:^16} {:^19} {:^6} {:<20}".format(namespace,
                                                                webapp,
                                                                age,
                                                                location,
                                                                installation))

    logger.debug("")


main()
