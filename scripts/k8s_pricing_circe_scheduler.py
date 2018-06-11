__author__ = "Quynh Nguyen, Pradipta Ghosh, Pranav Sakulkar, Jason A Tran,  Bhaskar Krishnamachari"
__copyright__ = "Copyright (c) 2018, Autonomous Networks Research Group. All rights reserved."
__license__ = "GPL"
__version__ = "3.0"

import sys
sys.path.append("../")

import time
import os
from os import path
from multiprocessing import Process
from write_circe_service_specs import *
from write_circe_specs import *
import yaml
from kubernetes import client, config
from pprint import *
import jupiter_config
from utilities import *



def check_status_circe_controller(dag):
    """
    This function prints out all the tasks that are not running.
    If all the tasks are running: return ``True``; else return ``False``.
    """

    jupiter_config.set_globals()

    sys.path.append(jupiter_config.CIRCE_PATH)
    """
        This loads the kubernetes instance configuration.
        In our case this is stored in admin.conf.
        You should set the config file path in the jupiter_config.py file.
    """
    config.load_kube_config(config_file = jupiter_config.KUBECONFIG_PATH)
    namespace = jupiter_config.DEPLOYMENT_NAMESPACE


    # We have defined the namespace for deployments in jupiter_config

    # Get proper handles or pointers to the k8-python tool to call different functions.
    extensions_v1_beta1_api = client.ExtensionsV1beta1Api()
    v1_delete_options = client.V1DeleteOptions()
    core_v1_api = client.CoreV1Api()

    result = True
    for key, value in dag.items():
        # First check if there is a deployment existing with
        # the name = key in the respective namespac    # Check if there is a replicaset running by using the label app={key}
        # The label of kubernets are used to identify replicaset associate to each task
        label = "app=" + key

        resp = None

        resp = core_v1_api.list_namespaced_pod(namespace, label_selector = label)
        # if a pod is running just delete it
        if resp.items:
            a=resp.items[0]
            if a.status.phase != "Running":
                print("Pod Not Running", key)
                result = False

            # print("Pod Deleted. status='%s'" % str(del_resp_2.status))

    if result:
        print("All the task controllers GOOOOO!!")
    else:
        print("Wait before trying again!!!!")

    return result

def check_status_circe_computing():
    """
    This function prints out all the tasks that are not running.
    If all the tasks are running: return ``True``; else return ``False``.
    """

    jupiter_config.set_globals()

    path1 = jupiter_config.HERE + 'nodes.txt'
    nodes = k8s_get_nodes(path1)

    sys.path.append(jupiter_config.CIRCE_PATH)
    """
        This loads the kubernetes instance configuration.
        In our case this is stored in admin.conf.
        You should set the config file path in the jupiter_config.py file.
    """
    config.load_kube_config(config_file = jupiter_config.KUBECONFIG_PATH)
    namespace = jupiter_config.DEPLOYMENT_NAMESPACE


    # We have defined the namespace for deployments in jupiter_config

    # Get proper handles or pointers to the k8-python tool to call different functions.
    extensions_v1_beta1_api = client.ExtensionsV1beta1Api()
    v1_delete_options = client.V1DeleteOptions()
    core_v1_api = client.CoreV1Api()

    result = True
    for key in nodes:
        # First check if there is a deployment existing with
        # the name = key in the respective namespac    # Check if there is a replicaset running by using the label app={key}
        # The label of kubernets are used to identify replicaset associate to each task
        label = "app=" + key 

        resp = None

        resp = core_v1_api.list_namespaced_pod(namespace, label_selector = label)
        # if a pod is running just delete it
        if resp.items:
            a=resp.items[0]
            if a.status.phase != "Running":
                print("Pod Not Running", key)
                result = False

            # print("Pod Deleted. status='%s'" % str(del_resp_2.status))

    if result:
        print("All the computing nodes GOOOOO!!")
    else:
        print("Wait before trying again!!!!")

    return result

# if __name__ == '__main__':
def k8s_pricing_circe_scheduler(dag_info , temp_info, profilers_ips, execution_ips):
    """
        This script deploys CIRCE in the system. 
    """

    jupiter_config.set_globals()
    
    sys.path.append(jupiter_config.CIRCE_PATH)

    path1 = jupiter_config.HERE + 'nodes.txt'
    nodes = k8s_get_nodes(path1)

    """
        This loads the kubernetes instance configuration.
        In our case this is stored in admin.conf.
        You should set the config file path in the jupiter_config.py file.
    """
    config.load_kube_config(config_file = jupiter_config.KUBECONFIG_PATH)
    
    """
        We have defined the namespace for deployments in jupiter_config
    """
    namespace = jupiter_config.DEPLOYMENT_NAMESPACE
    
    """
        Get proper handles or pointers to the k8-python tool to call different functions.
    """
    api = client.CoreV1Api()
    k8s_beta = client.ExtensionsV1beta1Api()

    #get DAG and home machine info
    first_task = dag_info[0]
    dag = dag_info[1]
    hosts = temp_info[2]
    print("hosts:")
    pprint(hosts)
    print(len(dag_info))
    pprint(dag_info[0])
    pprint(dag_info[1])
    pprint(dag_info[2])
    service_ips = {}; #list of all service IPs including home and task controllers
    computing_service_ips = {}

    print('-------- First create the home node service')
    """
        First create the home node's service.
    """
    home_body = write_circe_service_specs(name = 'home')
    ser_resp = api.create_namespaced_service(namespace, home_body)
    print("Home service created. status = '%s'" % str(ser_resp.status))

    try:
        resp = api.read_namespaced_service('home', namespace)
    except ApiException as e:
        print("Exception Occurred")

    service_ips['home'] = resp.spec.cluster_ip

    """
        Iterate through the list of tasks and run the related k8 deployment, replicaset, pod, and service on the respective node.
        You can always check if a service/pod/deployment is running after running this script via kubectl command.
        E.g., 
            kubectl get svc -n "namespace name"
            kubectl get deployement -n "namespace name"
            kubectl get replicaset -n "namespace name"
            kubectl get pod -n "namespace name"
    """ 

    print('-------- Create task controllers service')
    """
        Create task controllers' service
    """
   
    for key, value in dag.items():

        task = key
        nexthosts = ''
 
        """
            Generate the yaml description of the required service for each task
        """
        body = write_circe_service_specs(name = task)

        # Call the Kubernetes API to create the service
        ser_resp = api.create_namespaced_service(namespace, body)
        print("Service created. status = '%s'" % str(ser_resp.status))
    
        try:
            resp = api.read_namespaced_service(task, namespace)
        except ApiException as e:
            print("Exception Occurred")

        # print resp.spec.cluster_ip
        service_ips[task] = resp.spec.cluster_ip
    
    
    all_node_ips = ':'.join(service_ips.values())
    all_node = ':'.join(service_ips.keys())
    print('-------- Create computing nodes service')

    """
        Create computing nodes' service
    """

    for node in nodes:
 
        """
            Generate the yaml description of the required service for each computing node
        """
        if node != 'home':
            body = write_circe_service_specs(name = node)

            # Call the Kubernetes API to create the service
            ser_resp = api.create_namespaced_service(namespace, body)
            print("Service created. status = '%s'" % str(ser_resp.status))
        
            try:
                resp = api.read_namespaced_service(task, namespace)
            except ApiException as e:
                print("Exception Occurred")

            # print resp.spec.cluster_ip
            computing_service_ips[node] = resp.spec.cluster_ip

    all_computing_ips = ':'.join(computing_service_ips.values())
    all_computing = ':'.join(computing_service_ips.keys())
    print(all_computing)
    

    """
    Start circe
    """

    print('--------- Start task controllers')
    """
        Start task controllers
    """
    for key, value in dag.items():

        task = key
        nexthosts = ''
        next_svc = ''

        """
            We inject the host info for the child task via an environment variable valled CHILD_NODES to each pod/deployment.
            We perform it by concatenating the child-hosts via delimeter ':'
            For example if the child nodes are k8node1 and k8node2, we will set CHILD_NODES=k8node1:k8node2
            Note that the k8node1 and k8node2 in the example are the unique node ids of the kubernets cluster nodes.
        """
        inputnum = str(value[0])
        flag = str(value[1])

        for i in range(2,len(value)):
            if i != 2:
                nexthosts = nexthosts + ':'
            nexthosts = nexthosts + str(hosts.get(value[i])[0])

        for i in range(2, len(value)): 
            if i != 2:
                next_svc = next_svc + ':'
            next_svc = next_svc + str(service_ips.get(value[i]))
        print("NEXT HOSTS")
        print(nexthosts)
        print("NEXT SVC")
        print(next_svc)
    
        
        #Generate the yaml description of the required deployment for each task
        dep = write_circe_deployment_specs(flag = str(flag), inputnum = str(inputnum), name = task, node_name = hosts.get(task)[1],
            image = jupiter_config.WORKER_CONTROLLER_IMAGE, child = nexthosts, 
            child_ips = next_svc, host = hosts.get(task)[1], dir = '{}',
            home_node_ip = service_ips.get("home"),
            own_ip = service_ips[key],
            all_node = all_node,
            all_node_ips = all_node_ips)
        pprint(dep)
        

        # # Call the Kubernetes API to create the deployment
        resp = k8s_beta.create_namespaced_deployment(body = dep, namespace = namespace)
        print("Deployment created. status = '%s'" % str(resp.status))

    print('---------  Start computing nodes')
    """
        Start computing nodes
    """

    for i in nodes:

        # print nodes[i][0]
        
        """
            We check whether the node is a home / master.
            We do not run the controller on the master.
        """
        if i != 'home':

            """
                Generate the yaml description of the required deployment for WAVE workers
            """
            dep = write_circe_computing_specs(name = i, label =  i, image = jupiter_config.WORKER_COMPUTING_IMAGE,
                                             host = nodes[i][0], all_node = all_computing,
                                             all_node_ips = all_computing_ips,
                                             self_ip = computing_service_ips[i],
                                             profiler_ip = profiler_ips[i],
                                             all_profiler_ips = all_profiler_ips,
                                             execution_ip = execution_ips[i],
                                             all_execution_ips = all_execution_ips)
            # # pprint(dep)
            # # Call the Kubernetes API to create the deployment
            resp = k8s_beta.create_namespaced_deployment(body = dep, namespace = namespace)
            print("Deployment created. status ='%s'" % str(resp.status))

    while 1:
        if check_status_circe_controller(dag) and check_status_circe_computing():
            break
        time.sleep(30)

    print('-------- Start home node')

    home_dep = write_circe_home_specs(image = jupiter_config.HOME_IMAGE, 
                                host = jupiter_config.HOME_NODE, 
                                child = jupiter_config.HOME_CHILD,
                                child_ips = service_ips.get(jupiter_config.HOME_CHILD), 
                                dir = '{}')
    resp = k8s_beta.create_namespaced_deployment(body = home_dep, namespace = namespace)
    print("Home deployment created. status = '%s'" % str(resp.status))

    pprint(service_ips)
    