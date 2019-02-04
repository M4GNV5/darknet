import os, sys, re, json

path = sys.argv[1]
out_path = sys.argv[2]
files = os.listdir(path)
regex = re.compile('(.*?)_(\d{4})-(\d{2})-(\d{2})-(\d{2}):(\d{2}):(\d{2})')

obj = {}
for file in files:
	basename = os.path.basename(file)
	match = regex.match(basename)
	if match is None:
		print("Invalid file name ", basename)
		continue

	prefix, year, month, day, hour, minute, seconds = match.groups()
	day = prefix + "-" + year + "-" + month + "-" + day
	if day not in obj:
		obj[day] = {}

	name = basename.split(".")[0]

	with open(path + file) as fd:
		try:
			obj[day][name] = json.load(fd)
		except:
			print("Error when handling ", file)

for day in obj:
	with open(out_path + "/" + day + ".json", "w+") as fd:
		json.dump(obj[day], fd)
