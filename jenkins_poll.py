import os
import json
import jenkins
from six.moves.urllib.request import Request


# environment variables used for connecting to Jenkins REST API

ENV_JENKINS_POLL_CLIENT_USERNAME = 'jenkins_poll_client:username'
ENV_JENKINS_POLL_CLIENT_PASSWORD = 'jenkins_poll_client:password'
ENV_JENKINS_POLL_CLIENT_URL = 'jenkins_poll_client:url'
ENV_JENKINS_POLL_CLIENT_JOB = 'jenkins_poll_client:job'
ENV_JENKINS_POLL_CLIENT_scm_name = 'jenkins_poll_client:scm_name'
PYTHON_JENKINS_SCM_POLL = '%(folder_url)sjob/%(short_name)s/polling'


class JenkinsServer(jenkins.Jenkins):
    """ we extend Jenkins to support SCM polling
    """
    def build_poll_scm_name(self, scm_name, job):
        folder_url, short_name = self._get_job_folder(job)
        locals_ = {'folder_url': folder_url, 'short_name': short_name}
        poll_scm_name = self._build_url(PYTHON_JENKINS_SCM_POLL, locals_)
        return poll_scm_name

    def poll_scm(self, scm_name, job):
        request = Request(self.build_poll_scm_name(scm_name, job), b"")
        self.jenkins_open(request, True)


class JenkinsConnection(object):
    """ stores connection information required
    to use the Jenkins REST API
    """
    def __init__(self, config):
        if config is None:
            raise ValueError("config cannot be None")
        self.server = make_jenkins_server(config)
        self.job = config.job
        self.scm_name = config.scm_name


class JenkinsConfig(object):
    """ stores Jenkins configuration info
    """
    def __init__(self, username, password, url, job, scm_name):
        if username is None:
            raise ValueError("username cannot be None")
        if password is None:
            raise ValueError("password cannot be None")
        if url is None:
            raise ValueError("url cannot be None")
        if job is None:
            raise ValueError("job cannot be None")
        if scm_name is None:
            raise ValueError("scm_name cannot be None")
        self.url = url
        self.username = username
        self.password = password
        self.job = job
        self.scm_name = scm_name


def load_json_from_file(filepath):
    if filepath is None:
        raise ValueError("filepath cannot be None")
    config = None
    with open(filepath) as config_file:
        config = json.load(config_file)
    if config is None:
        raise ValueError("config didn\'t properly load")
    return config


def make_jenkins_config_json(filepath):
    config = load_json_from_file(filepath)
    url = config['url']
    job = config['job']
    scm_name = config['scm_name']
    auth_header = config['auth']
    username = auth_header['username']
    password = auth_header['password']
    return JenkinsConfig(
        username=username,
        password=password,
        url=url,
        job=job,
        scm_name=scm_name)


def get_env_variable(key):
    return os.environ.get(key)


def make_jenkins_config_env():
    url = get_env_variable(ENV_JENKINS_POLL_CLIENT_URL)
    job = get_env_variable(ENV_JENKINS_POLL_CLIENT_JOB)
    scm_name = get_env_variable(ENV_JENKINS_POLL_CLIENT_scm_name)
    username = get_env_variable(ENV_JENKINS_POLL_CLIENT_USERNAME)
    password = get_env_variable(ENV_JENKINS_POLL_CLIENT_PASSWORD)
    return JenkinsConfig(
        username=username,
        password=password,
        url=url,
        job=job,
        scm_name=scm_name)


# builds a "Jenkins" objects used to connect
# to a Jenkins server

def make_jenkins_server(config):
    uri = config.url
    username = config.username
    password = config.password

    server = JenkinsServer(
        uri,
        username=username,
        password=password
        )
    return server


#  connects to a Jenkins REST API and requests

def jenkins_whoami(connection):
    server = connection.server
    return server.get_whoami()


def jenkins_build_job(connection):
    server = connection.server
    job = connection.job
    return server.build_job(job)


def jenkins_poll_scm(connection):
    server = connection.server
    job = connection.job
    scm_name = connection.scm_name
    server.poll_scm(scm_name, job)
