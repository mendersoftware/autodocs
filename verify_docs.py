# Simply check the swagger yaml files to make sure that every path:
# contains a "summary"
# "tags" are not present
#
# returns an exit code accordingly

import yaml
import sys
errored = False
yfile = sys.argv[1]
with open(yfile, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

for i in cfg["paths"]:
    for j in cfg["paths"][i]:
        k = cfg["paths"][i][j]

        if "summary" not in k:
            print "Error: summary missing from Swagger doc in: ", i
            errored = True
        if "tags" in k:
            print "Error: tags exists in, %s, remove it" % (i)

sys.exit(errored)
