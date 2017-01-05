import shipyard as sy
from templates import *
import convoy.fleet as cf
import logging
import json
from itertools import product
from os.path import join, split

logger = logging.getLogger('shipyard')

class ApiContext(sy.CliContext):
    def __init__(self,
                 docker_image,
                 fileshare,
                 batch_account,
                 batch_key,
                 batch_url,
                 storage_account,
                 storage_key
                 ):
        super(self.__class__, self).__init__()

        self.docker_image = docker_image
        self.config = make_config(docker_image, fileshare)
        self.config.update(make_credentials(batch_account, batch_key, batch_url, storage_account, storage_key))
        # set internal config kv pairs
        self.config['_verbose'] = self.verbose
        self.config['_auto_confirm'] = self.yes
        if self.verbose:
            logger.debug('config:\n' + json.dumps(self.config, indent=4))
        self.are_clients_initialized = False

    def _update_clients(self, ):
        clients = cf.initialize(self.config)
        self._set_clients(*clients)
        self.are_clients_initialized = True

    def _add_pool_helper(self):
        cf.action_pool_add(
            self.batch_client,
            self.blob_client,
            self.queue_client,
            self.table_client,
            self.config)

    def add_pool(self, pool, recreate=False):
        self.config.update(pool.object)
        self._update_clients()
        if not recreate and self.batch_client.pool.exists(pool.id):
            print "using existing pool"
        else:
            self._add_pool_helper()

    def list_pools(self):
        return self.batch_client.pool.list()

    def delete_pool(self, id):
        self.batch_client.pool.delete(id)

    def add_job(self, job_spec, recreate):
        self.config.update(job_spec)
        self._update_clients()
        cf.action_jobs_add(
            self.batch_client,
            self.blob_client,
            self.config,
            recreate,
            tail=None)

class Pool(object):
    def __init__(self, api_context, id, vm_count, vm_size, recreate=False):
        self.api_context = api_context
        self.vm_count = vm_count
        self.vm_size = vm_size
        self.id = id
        self.object = make_pool(id, vm_count, vm_size)
        self.api_context.add_pool(self, recreate)

    def delete(self):
        self.api_context.delete_pool(self.id)

    def submit(self, job, recreate=False, **kwargs):
        command = job.get_command(**kwargs)
        job_obj = make_job(job.jobname, self.api_context.docker_image, command)
        job_spec = jobs_to_spec([job_obj])
        self.api_context.add_job(job_spec, recreate)

    def grid_submit(self, job, param_space, recreate=False):
        def param_product(param_dict):
            param_lists = []
            for key, values in param_dict.iteritems():
                param_lists.append([(key, value) for value in values])
            return [dict(elem) for elem in product(*param_lists)]

        param_combos = param_product(param_space)
        jobs = []
        for i, params in enumerate(param_combos):
            command = job.get_command(**params)
            jobs.append(make_job(job.jobname + str(i), self.api_context.docker_image, command))
        job_spec = jobs_to_spec(jobs)
        self.api_context.add_job(job_spec, recreate)


class Job(object):
    def __init__(self, jobname, path_to_script, ingressed_path_args=None, shared_path_args=None):
        self.jobname = jobname
        self.path_to_script = path_to_script
        self.ingressed_path_args = ingressed_path_args
        self.shared_path_args = shared_path_args

    def get_command(self, **kwargs):
        template = "/bin/bash -c \"pwd; cd $AZ_BATCH_NODE_SHARED_DIR{base_path}; ls; python {file} {argument_string}\""
        replace_dict = {
            "base_path": join(*split(self.path_to_script)[0:-1]),
            "file": split(self.path_to_script)[-1],
            "argument_string": " ".join(["--" + k + " " + str(v) for (k, v) in kwargs.iteritems()])
        }
        return template.format(**replace_dict)




