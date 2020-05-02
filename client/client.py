#!/usr/bin/env python
import pika
from pathlib import Path
import os
import shutil
import json
import argparse

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='Input file name', required=False)
    args = vars(parser.parse_args())

    if args['url']:
        connection = pika.BlockingConnection(
        	pika.URLParameters(args['url']))
        channel = connection.channel()
    else:
        connection = pika.BlockingConnection(
        	pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

    def callback(ch, method, properties, body):
        my_path = Path('result')
        for file in my_path.iterdir():
           if file.is_dir():
                shutil.rmtree(file)
           else:
                os.remove(file)
        for file in json.loads(body):
            if file['type'] == 'file':
                with open('{}/{}'.format(my_path, file['name']), "w+") as f:
                    f.write(file['binary'])
                    f.close()
            else:
                Path('{}/{}'.format(my_path, file['name'])).mkdir(parents=True, exist_ok=True)

    channel.basic_consume(
        queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
