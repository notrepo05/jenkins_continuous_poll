import time
import sys
import signal
import argparse
import jenkins_client as jc


DEFAULT_SCM_POLL_DELAY = 5  # seconds
ORIGINAL_HANDLER = signal.getsignal(signal.SIGINT)
DESCRIPTION = \
    '''
    jenkins_continuous_poll.py
    Continuously trigger SCM polling for Jenkins through the REST API.
    Press ctrl+c to exit.
    '''
BEGIN_POLL_TEXT = \
    '''Running continous SCM poll with %s second interval.
    '''


def scm_poll(options):
    config = config_scm(options)
    connection = jc.JenkinsConnection(config)
    jc.jenkins_poll_scm(connection)


def continous_scm_poll(options):
    time_interval = options.set_time_interval[0]
    assert(time_interval > 0)
    while True:
        scm_poll(options)
        time.sleep(time_interval)


def graceful_exit(signum, frame):
    signal.signal(signal.SIGINT, ORIGINAL_HANDLER)
    print("Exiting!")
    sys.exit(1)


def setup_cli_arguments(argv):
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-cjv", "--config-json-variables", type=str,
                       help="configure using a json file",
                       nargs=1)
    group.add_argument("-cev", "--config-environmental-variables",
                       help="configure using environmental variables",
                       action="store_true",
                       default=False)
    parser.add_argument("-t", "--set-time-interval", type=int,
                        help="set the interval between polls in seconds",
                        default=DEFAULT_SCM_POLL_DELAY,
                        nargs=1)
    options = parser.parse_args(argv)
    return options


def config_scm(options):
    config = None
    if options.config_environmental_variables:
        config = jc.make_jenkins_config_env()
    else:
        filepath = options.config_json_variables[0]
        config = jc.make_jenkins_config_json(filepath)
    return config


def main(argv):
    signal.signal(signal.SIGINT, graceful_exit)
    options = setup_cli_arguments(argv)
    time_interval = options.set_time_interval[0]
    print(BEGIN_POLL_TEXT % time_interval)
    continous_scm_poll(options)


if __name__ == '__main__':
    main(sys.argv[1:])
