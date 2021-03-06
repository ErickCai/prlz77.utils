# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 05/06/2017
"""
Simple script for keeping track of the available GPUs and run experiments on them when available.
"""

import time
import subprocess
import os


class GPU_Handler():
    """
    Keeps track of the available GPUs and runs experiments when available.
    """
    def __init__(self, gpus, timeout=3.0):
        """ Constructor

        Args:
            gpus (list): list of gpu slots. Repetition is allowed.
            timeout (float): waiting time for polling (in seconds). Defaults to 3 seconds.
        """
        self.current_gpu = 0
        self.gpu_list = [None]*len(gpus)
        self.gpu_nums = gpus
        self.timeout = timeout

    def poll(self):
        """
        Check and update gpu status.
        """
        if self.gpu_list[self.current_gpu].poll() is not None :
            self.gpu_list[self.current_gpu] = None
        else:
            time.sleep(self.timeout)
            self.current_gpu = (self.current_gpu + 1) % len(self.gpu_nums)

    def allocate_and_run(self, command):
        """ Finds the next available gpu and runs the command.

        Args:
            command (list): command to run in the next available gpu.
        """
        while self.gpu_list[self.current_gpu] is not None:
            self.poll()
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = str(self.gpu_nums[self.current_gpu])
        self.gpu_list[self.current_gpu] = subprocess.Popen(command, env=env)
        self.current_gpu = (self.current_gpu + 1) % len(self.gpu_nums)

    def isempty(self):
        """ Check gpu availability

        Returns: True if all gpus are idle.

        """
        empty = True
        for i in range(len(self.gpu_nums)):
            if self.gpu_list[i] is not None:
                empty = False
        return empty

    def wait(self):
        """
        Block until all processes finished.
        """
        while not self.isempty():
            self.poll()

