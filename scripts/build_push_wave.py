__author__ = "Pradipta Ghosh, Pranav Sakulkar, Quynh Nguyen, Jason A Tran,  Bhaskar Krishnamachari"
__copyright__ = "Copyright (c) 2018, Autonomous Networks Research Group. All rights reserved."
__license__ = "GPL"
__version__ = "2.0"

import sys
sys.path.append("../")

import os
import jupiter_config


def build_push_wave():
    """Build WAVE home and worker image from Docker files and push them to the Dockerhub.
    """
    jupiter_config.set_globals()
    
    os.system("cp " + jupiter_config.APP_PATH + "configuration.txt " 
                    + jupiter_config.WAVE_PATH + "DAG.txt")

    os.system("cp " + jupiter_config.APP_PATH + "input_node.txt " 
                    + jupiter_config.WAVE_PATH + "input_node.txt")

    os.system("cp " + jupiter_config.HERE + "jupiter_config.ini " 
                    + jupiter_config.WAVE_PATH + "jupiter_config.ini")

    os.chdir(jupiter_config.WAVE_PATH)

    os.system("sudo docker build --build-arg port_expose=%s -f home.Dockerfile . -t %s" %
                                 (jupiter_config.FLASK_DOCKER, jupiter_config.WAVE_HOME_IMAGE))
    os.system("sudo docker push " + jupiter_config.WAVE_HOME_IMAGE)
    
    os.system("sudo docker build --build-arg port_expose=%s -f worker.Dockerfile . -t %s" %
                                 (jupiter_config.FLASK_DOCKER, jupiter_config.WAVE_WORKER_IMAGE))
    os.system("sudo docker push " + jupiter_config.WAVE_WORKER_IMAGE)

    os.system("rm DAG.txt")
    os.system("rm input_node.txt")
    os.system("rm jupiter_config.ini")


if __name__ == '__main__':
    build_push_wave()