# tools for testing

testing.py

This is utility for performance/stability testing of oslo.messaging library and messaging cluster with using of multiple entry point
Usage of testing.py:
   --receiver | -r <rabbit_server:[port]>
   --sender   | -s <rabbit_server:[port]>
   --size     | -z <msg_size_in_bytes> , default = 1 Megabyte
   --num      | -n <num_of_messages> , default = 100
   --password | -p <rabbit_passwd>
   --user     | -u <rabbit_user>
   --sthreads  | -t <num_of_sender_threads> , default = 1




