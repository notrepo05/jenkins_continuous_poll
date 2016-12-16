import os
import json
import jenkins
import socket
from six.moves.urllib.request import Request


# environment variables used for connecting to Jenkins REST API

ENV_JENKINS_POLL_CLIENT_USERNAME = 'jenkins_poll_client:username'
ENV_JENKINS_POLL_CLIENT_PASSWORD = 'jenkins_poll_client:password'
ENV_JENKINS_POLL_CLIENT_URL = 'jenkins_poll_client:url'
ENV_JENKINS_POLL_CLIENT_JOB = 'jenkins_poll_client:job'

PYTHON_JENKINS_SCM_POLL = '%(folder_url)sjob/%(short_name)s/polling'


class JenkinsServer(jenkins.Jenkins):
    """ we extend jenkins.Jenkins to support SCM polling
    """
    def __init__(self, job, url, username=None, password=None,
                 timeout=socket.getdefaulttimeout(),
                 ):
        self.job = job
        super(JenkinsServer, self).__init__(url, username, password, timeout)

    def build_poll_scm_name(self):
        folder_url, short_name = self._get_job_folder(self.job)
        locals_ = {'folder_url': folder_url, 'short_name': short_name}
        poll_scm_name = self._build_url(PYTHON_JENKINS_SCM_POLL, locals_)
        return poll_scm_name

    def poll_scm(self):
        request = Request(self.build_poll_scm_name(), b"")
        self.jenkins_open(request, True)


class JenkinsConnection(object):
    """ stores connection information required
    to use the Jenkins REST API. we essentially
    use this to help decouple ourselves from 
    jenkins.Jenkins
    """
    def __init__(self, config):
        if config is None:
            raise ValueError("config cannot be None")
        self.server = make_jenkins_server(config)


class JenkinsConfig(object):
    """ stores Jenkins configuration info
    """
    def __init__(self, username, password, url, job):
        if username is None:
            raise ValueError("username cannot be None")
        if password is None:
            raise ValueError("password cannot be None")
        if url is None:
            raise ValueError("url cannot be None")
        if job is None:
            raise ValueError("job cannot be None")
        self.url = url
        self.username = username
        self.password = password
        self.job = job


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
    auth_header = config['auth']
    username = auth_header['username']
    password = auth_header['password']
    return JenkinsConfig(
        username=username,
        password=password,
        url=url,
        job=job)


def get_env_variable(key):
    return os.environ.get(key)


def make_jenkins_config_env():
    url = get_env_variable(ENV_JENKINS_POLL_CLIENT_URL)
    job = get_env_variable(ENV_JENKINS_POLL_CLIENT_JOB)
    username = get_env_variable(ENV_JENKINS_POLL_CLIENT_USERNAME)
    password = get_env_variable(ENV_JENKINS_POLL_CLIENT_PASSWORD)
    return JenkinsConfig(
        username=username,
        password=password,
        url=url,
        job=job)


# builds a "Jenkins" objects used to connect
# to a Jenkins server

def make_jenkins_server(config):
    uri = config.url
    job = config.job
    username = config.username
    password = config.password

    server = JenkinsServer(
        job,
        uri,
        username=username,
        password=password
        )
    return server


#  connects to a Jenkins REST API and polls SCM

def jenkins_poll_scm(connection):
    server = connection.server
    server.poll_scm()
