# pilot\default\deploy.py

DEPLOY_DEFAULTS = {
    'pipeline_type': 'remote_docker',  # ou 'ecs'
    'docker_context': './docker',
    'remote_host': 'remote.host.address',
    'ecr_repo': 'my_ecr_repo',
    'task_definition': 'my_task_def',
    'cluster_name': 'my_cluster',
    'service_name': 'my_service'
}