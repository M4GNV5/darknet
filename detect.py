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
total_count = 0

def fill_queue():
	global total_count

	in_path_list = os.listdir(in_path)
	out_path_list = os.listdir(out_path)
	for in_file in in_path_list:
		out_file = os.path.basename(in_file) + ".json"
		if out_file not in out_path_list:
			queue.put((in_path + in_file, out_path + out_file))
			total_count = total_count + 1

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

queue_filler = Thread(target=fill_queue, args = ())
queue_filler.start()

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

queue_filler.join()
queue.join()
print("\nDONE")
