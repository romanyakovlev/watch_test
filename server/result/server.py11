import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import pika
import json
from pathlib import Path
import argparse


lists = []

def check_out_path(target_path, level=0):

    def print_indented(file, level):
        print(file)

        if not file.is_dir():
            f=open(file,'rb')
            i=f.read()
            lists.append({
            	'type': 'file', 
            	'binary': i.decode('utf-8'),
            	'name': file.name,
            })
        else:
        	lists.append({
            	'type': 'folder', 
            	'name': file.name,
            })

    print_indented(target_path, level)
    for file in target_path.iterdir():
        if file.is_dir():
            check_out_path(file, level+1)
        else:
            print_indented(file, level+1)


if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help='Input folder', required=True)
    args = vars(parser.parse_args())
    folder_path = Path(args['folder'])

    def send_data():
        lists.clear()
        check_out_path(folder_path)
        channel.basic_publish(exchange='', routing_key='hello', body=json.dumps(lists))

    def on_created(event):
        print(f" {event.src_path} has been created!")
        send_data()

    def on_deleted(event):
        print(f"{event.src_path}  has been deleted!")
        send_data()

    def on_modified(event):
        print(f"{event.src_path} has been modified")
        send_data()

    def on_moved(event):
        print(f"{event.src_path}moved to {event.dest_path}")
        send_data()

    connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')

    send_data()

    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(
    	patterns, ignore_patterns, ignore_directories, case_sensitive
    )
    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved

    path = "."
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
        connection.close()