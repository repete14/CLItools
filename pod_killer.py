from kubernetes import config, client
from datetime import datetime, timedelta
import pytz, os, sys, logging, logging.config


def main():
    # set up logging configuration
    config_file = os.path.join(sys.path[0], 'logging.conf')
    logging.config.fileConfig(config_file)
    logger = logging.getLogger('output')

    installations_kill_count = {}

    while True:
        # run the main pod information script, and catch any ctl-c script end command
        pod_list_stuck = get_stuck_pods()
        pod_kill_request = str(raw_input("Enter numbers for pods you want to kill (comma separated, a=all, r=recheck, q=quit): "))

        # parse input commands
        if pod_kill_request == 'a':
            # set list to all pods
            pod_to_kill_id_list = range(0,len(pod_list_stuck)-1,1)
        elif pod_kill_request == "r":
            continue
        elif pod_kill_request == "q":
            quit()
        elif 0 < len(pod_kill_request) < 3:
            pod_to_kill_id_list = [int(pod_kill_request)]
        elif pod_kill_request.__contains__(","):
            pod_to_kill_id_list = pod_kill_request.strip("(").strip(")").split(",")
        else:
            logger.debug("invalid input, try again")
            continue

        # kill requested pods
        killed_namespaces = kill_pod(pod_to_kill_id_list, pod_list_stuck)

        # report on the number of times each namespace has had a pod killed
        for namespace in killed_namespaces:
            if namespace in installations_kill_count:
                installations_kill_count[namespace] = installations_kill_count[namespace] + 1
            else:
                installations_kill_count[namespace] = 1
        logger.debug("namespace\t\tnumber of pods killed:")
        for namespace in installations_kill_count:
            logger.debug("%s:\t%s" % (namespace, installations_kill_count[namespace]))


def get_stuck_pods():
    # set up logging configuration
    config_file = os.path.join(sys.path[0], 'logging.conf')
    logging.config.fileConfig(config_file)
    logger = logging.getLogger('output')

    # filters for get pods
    label_selector = "jcx.inst.component=webapp"
    limit = 100

    # initializing stuck pod data
    pod_list_stuck = []
    pod_list_starting = []
    pod_list_old = []
    starting_cutoff = timedelta(minutes=10)
    old_cutoff = timedelta(hours=12)

    # collecting list of webapp pods from jcx-prod-us-east
    config.load_kube_config(context="jcx-prod-us-east")
    api = client.CoreV1Api()
    pod_list_us = api.list_pod_for_all_namespaces(label_selector=label_selector,limit=limit)

    # collecting list of webapp pods from jcx-prod-eu
    config.load_kube_config(context="jcx-prod-eu")
    api = client.CoreV1Api()
    pod_list_eu = api.list_pod_for_all_namespaces(label_selector=label_selector,limit=limit)

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
    pod_id = 0
    # subprocess.call("clear")
    logger.debug("{:<3} {:^33} {:^16} {:^19} {:^6} {:^20}".format("pod_id",
                                                                  "namespace",
                                                                  "Pod",
                                                                  "Age (H:M:S)",
                                                                  "Loc",
                                                                  "installation name"))

    logger.debug("{:^94}".format("--------------- STUCK PODS (>10 mins) ---------------"))
    print_pod_list(pod_list_stuck, pod_id)
    pod_id = pod_id + len(pod_list_stuck)

    logger.debug("{:^94}".format("------------ IN PROGRESS PODS (<10 mins) ------------"))
    print_pod_list(pod_list_starting, pod_id)
    pod_id = pod_id + len(pod_list_starting)

    logger.debug("{:^94}".format("----------- VERY OLD DEAD PODS (>12 hours) -----------"))
    print_pod_list(pod_list_old, pod_id)

    # return list of all stuck pods
    pod_list_all = pod_list_stuck + pod_list_starting + pod_list_old
    return pod_list_all


def kill_pod(pods_to_kill, pod_list):
    # set up logging configuration
    config_file = os.path.join(sys.path[0], 'logging.conf')
    logging.config.fileConfig(config_file)
    logger = logging.getLogger('output')

    # kill just the pod listed
    body = client.V1DeleteOptions()
    namespaces_killed = []
    for pod_id in pods_to_kill:
        name = pod_list[int(pod_id)].metadata.name
        namespace = pod_list[int(pod_id)].metadata.namespace
        if pod_list[int(pod_id)].metadata.labels[u'jcx.environment'] == 'aws-us-east-1-infra-prod':
            context = "jcx-prod-us-east"
        else:
            context = "jcx-prod-eu"
        config.load_kube_config(context=context)
        api = client.CoreV1Api()

        logger.debug("deleting %s\t%s",namespace,name)
        api.delete_namespaced_pod(name=name,namespace=namespace,body=body)
        namespaces_killed.append(namespace)

    return namespaces_killed


def print_pod_list(pod_list,pod_id):
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
        logger.debug("{:<3} {:<33} {:^16} {:^19} {:^6} {:<20}".format(str(pod_id) + ")",
                                                                      namespace,
                                                                      webapp,
                                                                      age,
                                                                      location,
                                                                      installation))
        pod_id += 1

    logger.debug("")


main()
