Ceph API
========

This project generates helper functions to interact with Ceph over JSON
rather than using subprocess.popen, check_call, check_output, etc.  If you
are considering importing subprocess into your project stop and use this
library instead.  You'll save yourself many future headaches.

The utility that generates these helper functions is located here:
`Ceph Command Parser <https://github.com/cholcombe973/ceph_command_parser>`_

Please install python-ceph for this library to function properly.
