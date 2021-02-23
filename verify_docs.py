#!/usr/bin/python3

# Simply check the swagger yaml files to make sure that every path:
# contains a "summary"
# "tags" are not present
#
# returns an exit code accordingly

import sys
import yaml
import copy

from distutils.version import StrictVersion


def verify_swagger(spec):
    api_version = StrictVersion(spec["swagger"])
    if api_version.version[0] != 2:
        # Major version must be 2
        print(
            "Error: swagger version '%s' not supported; major version must be 2"
            % api_version
        )
        return True
    errored = False
    for i in spec["paths"]:
        for j in spec["paths"][i]:
            k = spec["paths"][i][j]
            if "summary" not in k:
                print("Error: summary missing from Swagger doc in: %s" % (i))
                errored = True
    return errored


def verify_openapi(spec):
    api_version = StrictVersion(spec["openapi"])
    if api_version.version[0] != 3:
        # Major version must be 3
        print(
            "Error: OpenAPI version '%s' not supported; major version must be 3"
            % api_version
        )
        return True
    errored = False
    for i in spec["paths"]:
        for j in spec["paths"][i]:
            k = spec["paths"][i][j]
            if "summary" not in k:
                print("Error: summary missing from OpenAPI doc in: %s" % (i))
                errored = True
    return errored


def verify_asyncapi_1(spec):
    msgs = spec["components"].get("messages", {})
    errored = False
    for name, msg in msgs.items():
        if "summary" not in msg:
            print("Error: #components/messages/%s is missing a summary" % name)
            errored = True
    return errored


def verify_docs_files(files):
    errored = False
    for yfile in files:
        with open(yfile, "r") as ymlfile:
            spec = yaml.load(ymlfile, Loader=yaml.SafeLoader)

        if "openapi" in spec:
            return verify_openapi(spec)
        elif "swagger" in spec:
            return verify_swagger(spec)
        elif "asyncapi" in spec:
            api_version = StrictVersion(spec["asyncapi"])
            if api_version.version[0] == 1:
                # We currently only support major version 1.
                return verify_asyncapi_1(spec)
            else:
                print(
                    "Error: cannot verify AsyncAPI version %s; major version must be 1"
                    % api_version
                )
                return True

        else:
            print("Error: unable to identify API spec kind.")
            return True


if __name__ == "__main__":
    sys.exit(verify_docs_files(sys.argv[1:]))
