import os, sys, json

path = sys.argv[1]
files = os.listdir(path)

obj = {}
for file in files:
	name = os.path.basename(file).split(".")[0]

	with open(path + file) as fd:
		try:
			obj[name] = json.load(fd)
		except:
			print("Error when handling ", file)

with open("data.json", "w+") as fd:
	json.dump(obj, fd)
