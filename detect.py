import sys, os, json

from python import darknet as dn
from threading import Thread
from Queue import Queue

if len(sys.argv) != 3:
	raise "Required arguments: <input path> <output path>"

in_path = sys.argv[1] + "/"
out_path = sys.argv[2] + "/"
queue = Queue()
num_gpus = 4

def worker(i, net, meta):
	dn.set_gpu(i)

	while True:
		in_file, out_file = queue.get()

		with open(out_file, "w+") as fd:
			print(in_file)
			items = dn.detect(net, meta, in_file)
			json.dump(items, fd)

		queue.task_done()

in_path_list = os.listdir(in_path)
out_path_list = os.listdir(out_path)
for in_file in in_path_list:
	out_file = os.path.basename(in_file) + ".json"
	if out_file not in out_path_list:
		queue.put((in_path + in_file, out_path + out_file))

if queue.empty():
	print("No images to analyze! We are all done")
	exit(0)
else:
	print("Analyzing %d images..." % (queue.qsize()))

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

queue.join()
print "DONE"
