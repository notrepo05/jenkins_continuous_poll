# jenkins_continuous_poll 
## What?
Continuously trigger SCM polling for Jenkins through the REST API. This was written for Python 2.7.10, but it's probably forwards compatible. 

## Why?
This tool simply POSTS to /job/:job/polling to trigger regular SCM polls. The reason behind this is because Jenkins (by default) only permits
around 1 poll per 2 minutes. Since I couldn't create a tunnel nor port forward to my Jenkins server so SCM could issue notices, this is the
next (or third.. or fourth) best thing. I didn't want to write a plugin.

## How?
At the moment this tool only supports basic authorization. I plan on eventually adding tokens, but for the time being you must specify your
credentials either in the environmental variables or in a json document. 

Here is an example json configuration file:

```json
{
    "auth": {
        "username": "admin",
        "password": "abc123"
    },
    "url": "http://localhost:8080",
    "job": "my_special_job"
}
```
I would suggest you simply copy and paste this to get started.

Or, alternatively, you can provide the following equivalent environmental variables:

- jenkins_poll_client:username
- jenkins_poll_client:password
- jenkins_poll_client:url
- jenkins_poll_client:job

### Examples:

Finally, you simply run the Python 2.7.10 program and specify which configuration you're using:
#### Using environmental variables
```
> python ./jenkins_continuous_poll.py --config-environmental-variables
```
Equivalently,
```
> python ./jenkins_continuous_poll.py -cev
```
#### Using a json configuration file
```
> python ./jenkins_continuous_poll.py --config-json-variables path/to/config.json
```
Equivalently,
```
> python ./jenkins_continuous_poll.py -cjv path/to/config.json
```

### Specify polling interval
You can also specify how many seconds the interval should be with `-t <second>`. The default is 5 seconds.
It might be advisable to avoid polling servers you aren't hosting faster than the default rate.
```
> python ./jenkins_continuous_poll.py --config-json-variables path/to/config.json --set-time-interval 10
```
Equivalently,
```
> python ./jenkins_continuous_poll.py --cjv path/to/config.json -t 10
```
