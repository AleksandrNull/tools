#!/usr/bin/env python
# coding: utf-8

import sys, getopt
from oslo.config import cfg
from oslo import messaging
import logging
import eventlet
import threading
import time

eventlet.monkey_patch()

counter = 0

# logging
logging.basicConfig()
log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

class NotificationHandler(object):
    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        if publisher_id == 'testing':
            global counter
            counter+=1
#            log.info('Handled')
            return messaging.NotificationResult.HANDLED

    def warn(self, ctxt, publisher_id, event_type, payload, metadata):
        log.info('WARN')

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        log.info('ERROR')

def help():
   print 'This is utility for performance/stability testing of oslo.messaging library and messaging cluster with using of multiple entry point'
   print 'Usage of testing.py:'
   print '   --receiver | -r <rabbit_server:[port]>'
   print '   --sender   | -s <rabbit_server:[port]>'
   print '   --size     | -z <msg_size_in_bytes> , default = 1 Megabyte'
   print '   --num      | -n <num_of_messages> , default = 100'
   print '   --password | -p <rabbit_passwd>'
   print '   --user     | -u <rabbit_user>'
   print '   --sthreads  | -t <num_of_sender_threads> , default = 1'

def main(argv):
   size = 10**6
   msg_num = 100
   sthreads = 1

   rabbit_username = ''
   rabbit_password = ''
   rabbit_host_srv = ''
   rabbit_host_client = ''

   try:
      opts, args = getopt.getopt(argv,"hr:s:u:p:z:n:t:",["--receiver","--sender","--password","--user","--size","--num","--sthreads"])
   except getopt.GetoptError:
      help()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         help()
         sys.exit()
      elif opt in ("-z", "--size"):
         size = int(arg)
      elif opt in ("-n", "--num"):
         msg_num = int(arg)
      elif opt in ("-r", "--receiver"):
         rabbit_host_srv = arg
      elif opt in ("-s", "--sender"):
         rabbit_host_client = arg
      elif opt in ("-u", "--user"):
         rabbit_username = arg
      elif opt in ("-p", "--password"):
         rabbit_password = arg
      elif opt in ("-t","--sthreads"):
         sthreads =  int(arg)

   if ( rabbit_host_srv == '' or rabbit_host_client == '' or rabbit_username == '' or rabbit_password == '' ) :
       help()
       print '--sender, --receiver, --password and --user are mandatory options'
       sys.exit(2)

   msg = "t" * size

   log.info('Configuring connection')
   transport_url_server = 'rabbit://'+rabbit_username+':'+rabbit_password+'@'+rabbit_host_srv+'/'
   transport_server = messaging.get_transport(cfg.CONF, transport_url_server)

   targets = [messaging.Target(topic='heavy_load')]
   endpoints = [NotificationHandler()]

   server = messaging.get_notification_listener(transport_server, targets, endpoints, allow_requeue=True, executor='eventlet')
   
   transport_url_client = 'rabbit://'+rabbit_username+':'+rabbit_password+'@'+rabbit_host_client+'/'
   transport_client = messaging.get_transport(cfg.CONF, transport_url_client)

   notifier = messaging.Notifier(transport_client, driver='messaging', publisher_id='testing', topic='heavy_load')

   def send():
     for x in range(0, msg_num):
        notifier.info({'some': 'context'}, 'just.testing', {'heavy': msg })

   def receive():
     server.start()

   def watch():
     while counter < msg_num*sthreads:
	time.sleep(1)
     server.stop()
     server.wait()
     print 'Serviced ', counter, ' messages in', time.clock() - time_start ,'seconds'

   try:

     receiver = threading.Thread(name='Receiver', target=receive)
     watcher = threading.Thread(name='Watcher', target=watch)

     receiver.start()

     time_start=time.clock()

     sender_threads = []
     for i in range(sthreads):
    	t = threading.Thread(target=send)
        sender_threads.append(t)
        t.start()
     
     watcher.start()

     watcher.join()
   except:
      print 'Unable to start threads'
 
if __name__ == "__main__":
   main(sys.argv[1:])

