# Copyright (c) 2015 Scott Christensen
#
# This file is part of htpython modified from condorpy
#
# condorpy/htpython is free software: you can redistribute it and/or modify it under
# the terms of the BSD 2-Clause License. A copy of the BSD 2-Clause License
# should have be distributed with this file.

import os
import re
import subprocess

from .logger import log
from .exceptions import HTCondorError



class HTCondorObjectBase(object):
    """

    """

    def __init__(self,
                 remote_input_files=None,
                 working_directory='.'):
        """


        """
        object.__setattr__(self, '_cluster_id', 0)
        object.__setattr__(self, '_remote_input_files', remote_input_files or None)
        object.__setattr__(self, '_cwd', working_directory)

    @property
    def cluster_id(self):
        """
        The id assigned to the job (called a cluster in HTConodr) when the job is submitted.
        """
        return self._cluster_id

    def set_cwd(fn):
        """
        Decorator to set the specified working directory to execute the function, and then restore the previous cwd.
        """
        def wrapped(self, *args, **kwargs):
            log.info('Calling function: %s with args=%s', fn, args if args else [])
            cwd = os.getcwd()
            log.info('Saved cwd: %s', cwd)
            os.chdir(self._cwd)
            log.info('Changing working directory to: %s', self._cwd)
            try:
                return fn(self, *args, **kwargs)
            finally:
                os.chdir(cwd)
                log.info('Restored working directory to: %s', cwd)

        return wrapped

    def submit(self, args):
        """


        """
        out, err = self._execute(args)
        if err:
            if re.match('WARNING|Renaming', err):
                log.warning(err)
            else:
                raise HTCondorError(err)
        log.info(out)
        try:
            self._cluster_id = int(re.search('(?<=cluster |\*\* Proc )(\d*)', out).group(1))
        except:
            self._cluster_id = -1
        return self.cluster_id

    def remove(self, options=[], sub_job_num=None):
        """Removes a job from the job queue, or from being executed.

        Args:
            options (list of str, optional): A list of command line options for the condor_rm command. For
                details on valid options see: http://research.cs.wisc.edu/htcondor/manual/current/condor_rm.html.
                Defaults to an empty list.
            job_num (int, optional): The number of sub_job to remove rather than the whole cluster. Defaults to None.

        """
        args = ['condor_rm']
        args.extend(options)
        job_id = '%s.%s' % (self.cluster_id, sub_job_num) if sub_job_num else str(self.cluster_id)
        args.append(job_id)
        out, err = self._execute(args)
        return out,err

    @set_cwd
    def _execute(self, args, shell=False):
        out = None
        err = None

        log.info('Executing local command %s', ' '.join(args))
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        out, err = process.communicate()

        log.info('Execute results - out: %s, err: %s', out, err)
        return out, err

    @set_cwd
    def _copy_input_files_to_remote(self):
        self._remote.put(self.remote_input_files, self._remote_id)

    @set_cwd
    def _copy_output_from_remote(self):
        self._remote.get(os.path.join(self._remote_id, self.initial_dir))

    @set_cwd
    def _open(self, file_name, mode='w'):
        return open(file_name, mode)

    @set_cwd
    def _make_dir(self, dir_name):
        try:
            log.info('making directory %s', dir_name)
            os.makedirs(dir_name)
        except OSError:
            log.warn('Unable to create directory %s. It may already exist.', dir_name)
