import sys, os, json

from python import darknet as dn
from threading import Thread
from Queue import Queue

if len(sys.argv) != 3:
	raise "Required arguments: <input path> <output path>"

path_in = sys.argv[1]
path_out = sys.argv[2]
num_cpus = 2
folders = Queue()
folders.put((path_in, path_out))

queue = Queue()
num_gpus = 4
total_count = 0

def add_files_from(path_in, path_out):
	global total_count

	files_in = os.listdir(path_in)
	files_out = os.listdir(path_out)

	for file in files_in:
		inner_in = os.path.join(path_in, file)
		if os.path.isdir(inner_in):
			inner_out = os.path.join(path_out, file)
			if not os.path.isdir(inner_out):
				os.mkdir(inner_out)

			folders.put((inner_in, inner_out))
		elif file + ".json" in files_out:
			pass
		else:
			inner_out = os.path.join(path_out, os.path.basename(file) + ".json")
			total_count = total_count + 1
			queue.put((inner_in, inner_out))

def fill_queue():
	while True:
		path_in, path_out = folders.get()
		add_files_from(path_in, path_out)
		folders.task_done()

def worker(i, net, meta):
	dn.set_gpu(i)

	while True:
		in_file, out_file = queue.get()
		try:
			items = dn.detect(net, meta, in_file)
		except:
			print("\nError analyzing file ", in_file)
			continue

		with open(out_file, "w+") as fd:
			json.dump(items, fd)

		curr_count = queue.qsize()
		done_count = total_count - curr_count
		done_percent = int(float(done_count) / float(total_count) * 100)
		sys.stdout.write("\r%d%% %d/%d    " % (done_percent, done_count, total_count))
		sys.stdout.flush()

		queue.task_done()

for i in range(num_cpus):
	t = Thread(target=fill_queue, args = ())
	t.daemon = True
	t.start()

args = []
for i in range(num_gpus):
	dn.set_gpu(i)
	net = dn.load_net("cfg/yolov3.cfg", "yolov3.weights", 0)
	meta = dn.load_meta("cfg/coco.data")
	args.append((i, net, meta, ))

for i in range(num_gpus):
	t = Thread(target=worker, args = args[i])
	t.daemon = True
	t.start()

folders.join()
queue.join()
print("\nDONE")
