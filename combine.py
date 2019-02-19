import os, sys, re, json

start_path = sys.argv[1]
out_path = sys.argv[2]

regex = re.compile('(.*?)_(\d{4})-(\d{2})-(\d{2})-(\d{2}):(\d{2}):(\d{2})')
obj = {}

def handle_folder(path):
	print path
	files = os.listdir(path)
	for file in files:
		file_path = os.path.join(path, file)
		if os.path.isdir(file_path):
			handle_folder(file_path)
			continue

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

		with open(file_path) as fd:
			try:
				obj[day][name] = json.load(fd)
			except:
				print("Error when handling ", file)

handle_folder(start_path)
for day in obj:
	with open(out_path + "/" + day + ".json", "w+") as fd:
		json.dump(obj[day], fd)
