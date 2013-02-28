================================
ZenPacks.community.RDBMS
================================

About
=====

This ZenPack provides basic "Database" and "DBSrvInst" component class. This
ZenPack also provide community.snmp.DatabaseMap collector plugin for  generic
RDBMS databases (o.e. Posgresql with pgsnmpd agent) modelin and following
components templates on /Server Device Class.

Requirements
============

Zenoss
------

You must first have, or install, Zenoss 2.5.2 or later. This ZenPack was tested
against Zenoss 2.5.2, Zenoss 3.2 and Zenoss 4.2. You can download the free Core
version of Zenoss from http://community.zenoss.org/community/download.

ZenPacks
--------

Only if you are using Zenoss 2.5, you need:

- `Advanced Device Details ZenPack <http://community.zenoss.org/docs/DOC-3452>`_

Installation
============

Normal Installation (packaged egg)
----------------------------------

Download the `RDBMS ZenPack <http://community.zenoss.org/docs/DOC-3447>`_.
Copy this file to your Zenoss server and run the following commands as the zenoss
user.

    ::

        zenpack --install ZenPacks.community.RDBMS-2.5.0.egg
        zenoss restart

Developer Installation (link mode)
----------------------------------

If you wish to further develop and possibly contribute back to the RDBMS
ZenPack you should clone the git `repository <https://github.com/epuzanov/ZenPacks.community.RDBMS>`_,
then install the ZenPack in developer mode using the following commands.

    ::

        git clone git://github.com/epuzanov/ZenPacks.community.RDBMS.git
        zenpack --link --install ZenPacks.community.RDBMS
        zenoss restart


Usage
=====

Installing the ZenPack will add the following items to your Zenoss system.

Modeler Plugins
---------------

- community.snmp.DatabaseMap

Monitoring Templates
--------------------

- DBSrvInst
- Database

Performance graphs
------------------

**DBSrvInst**

- Operations
- Disk Reads
- Disk Writes
- Logical Reads
- Logical Writes
- Page Reads
- Page Writes
- Requests
- Handled Requests
- Transactions
- Finished

**Database**

- Usage
- Used
- Total

MIBs
----

- RDBMS-MIB

Peformance Reports
------------------

- Database Util Report
