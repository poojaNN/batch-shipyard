def make_config(docker_image, fileshare):
    return \
        {
            "batch_shipyard": {
                "storage_account_settings": "mystorageaccount",
                "storage_entity_prefix": "shipyard"
            },
            "global_resources": {
                "docker_images": [
                    docker_image
                ],
                "docker_volumes": {
                    "shared_data_volumes": {
                        "shipyardvol": {
                            "volume_driver": "azurefile",
                            "storage_account_settings": "mystorageaccount",
                            "azure_file_share_name": fileshare,
                            "container_path": "$AZ_BATCH_NODE_SHARED_DIR/fileshare",
                            "mount_options": [
                                "filemode=0777",
                                "dirmode=0777",
                                "nolock=true"
                            ]
                        }
                    }
                }
            }
        }


def make_credentials(batch_account, batch_key, batch_url, storage_account, storage_key):
    return \
        {
            "credentials": {
                "batch": {
                    "account": batch_account,
                    "account_key": batch_key,
                    "account_service_url": batch_url
                },
                "storage": {
                    "mystorageaccount": {
                        "account": storage_account,
                        "account_key": storage_key,
                        "endpoint": "core.windows.net"
                    }
                }
            }
        }


def make_empty_job_spec():
    return \
        {
            "job_specifications": [

            ]
        }


def make_job(jobname, docker_image, command):
    return \
        {
            "id": jobname,
            "tasks": [
                {
                    "image": docker_image,
                    "remove_container_after_exit": True,
                    "shared_data_volumes": [
                        "shipyardvol"
                    ],
                    "command": command
                }
            ]
        }


def jobs_to_spec(jobs):
    job_spec = make_empty_job_spec()
    job_spec["job_specifications"] += jobs
    return job_spec


def make_pool(id, vm_count, vm_size="STANDARD_D11_V2"):
    return \
        {
            "pool_specification": {
                "id": id,
                "vm_size": vm_size,
                "vm_count": vm_count,
                "publisher": "Canonical",
                "offer": "UbuntuServer",
                "sku": "16.04.0-LTS",
                "ssh": {
                    "username": "docker"
                },
                "reboot_on_start_task_failed": False,
                "block_until_all_global_resources_loaded": True
            }
        }
