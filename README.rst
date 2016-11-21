============================
An entrypoint for containers
============================

`entrypoing` is a Python library that provides an ability to retrieve
configuration settings at a start point from etcd. By preserving an ability
to use local settings which are present in a container or attached through
a volume.

The following snippet of the code shows the common usage pattern of
the library::

    import entrypoint
    from entrypoint import catalog
    from entrypoint import config

    CONF = config.CONF

    ...

    entrypoint.process_entrypoint(
        "ceagle", default_config_path="/etc/ceagle/config.json")

    ...

    elasticsearch = catalog.get_endpoint("elasticsearch")

    print(endpoint.protocol) #-> None or "http"
    print(endpoint.address) #-> "127.0.0.1"
    print(endpoint.port) #-> 8234
    print(endpoint.url()) #-> "http://127.0.0.1:8234/"



The main assumption is that before to use `CONF` the `process_entrypoint`
function have to be called to populate it. Right now there are only two
required variables, such as `service_name` and `default_config_path`.

Be default the entrypoint expect that configuration is present locally but this
behaviour can be changed through the envrinment variable `ENVIRONMENT`. There
are two possible values for this variable, such as `etcd` and `local`.

=============================
Fetch configuration from etcd
=============================

The first value `etcd` means that configuration is present in etcd and will be
fetched from it. In this cahse etcd hosts have to be specified in the env
variable `ETCD_HOSTS`, they will be used to try to connect to them and fetch
configuration.

`entrypoint` expects in etcd the following key patter for configuration of
services::

    /<service_name>/config

Before to run application the configuration file for a service have to set in
etcd, it could be done by the next command (for the `ceagle` service)::

    etcdctl set /ceagle/config < config.json

Only JSON-serialized configuration is supported.

To run a container from an image that uses `entrypoint`, the following
command can be used::

    cat > ceagle-env-vars <<EOF
    ENVIRONMENT=etcd
    ETCD_HOSTS="172.17.0.4:2379 172.17.0.5:2379"
    EOF
    docker run --env-vars=ceagle-env-vars --name=ceagle ceagle:latest

==========================
Read configuration locally
==========================

The second value `local` means that the configuration will be read from a local
filesystem by a path which is specified in the variable
`<SERVICE_NAME>_CONFIG_FILE`, e.g. `CEAGLE_CONFIG_FILE` in case of
`service_name="ceagle"`. If the `*_CONFIG_FILE` variable is not speicified,
then the default filename will be used, which is specified by the
`default_config_path` variable in a code of an application.

Nothing specially have to be specified to run a container with the
configuration which is shipped by an image.

To use non-default configuration path, e.g. through mounting a host directory,
an container can be run in the following way::

    cat > ceagle-env-vars <<EOF
    CEAGLE_CONFIG_FILE=/etc/ms/ceagle/config.json
    EOF
    docker run --env-vars=ceagle-env-vars --name=ceagle \
        -v /local/ceagle:/etc/ms/ceagle
        ceagle:latest

==============================
A List of Supported Parameters
==============================

The full list of supported arguments and environment variables are listed here:

=====================  ===========================  =====================================
Argument               Environment variable         Default value (type)
=====================  ===========================  =====================================
--environment          ENVIRONMENT                  local (etcd/local)
--etcd-hosts           ETCD_HOSTS                   - (a space-delimited list of str:int)
--etcd-attempts        ETCD_ATTEMPTS                10 (int)
--etcd-attempts-delay  ETCD_ATTEMPTS_DELAY          6 (int)
--config-file          <SERVICE_NAME>_CONFIG_FILE   <default_config_path> (str)
=====================  ===========================  =====================================

=========
Endpoints
=========

A service have to has a definition of its endpoints in etcd in the following key::

    /<service_name>/endpoints

The only supported format for endpoints is JSON with the next structure::

    {
        "private": {
            "protocol": "http",
            "address": "127.0.0.1",
            "port": 8000,
        }
    }

Where the `private` type of endpoints have to be used for the cross service
communication. The `protocol` is an optional parameter and in case of using
the `Endpoint.url` method will be replaced by `"http"`.

====
TODO
====

What we want:

* Add support to handle dependencies between services throught.
* Reporting status of services.
