import subprocess
import json

json_file = subprocess.run("wdtaxonomy Q634 -f json", shell=True, stdout=subprocess.PIPE).stdout.decode('utf8')

print(json.loads(json_file))

