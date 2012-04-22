################################################################################
#
# This program is part of the RDBMS Zenpack for Zenoss.
# Copyright (C) 2009-2012 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""Database

Database is a Database

$Id: Database.py,v 1.6 2012/03/31 22:08:51 egor Exp $"""

__version__ = "$Revision: 1.6 $"[11:-2]

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.ZenModel.OSComponent import OSComponent
from Products.ZenModel.ZenDate import ZenDate
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from Products.ZenModel.ZenossSecurity import *
from Products.ZenUtils.Utils import convToUnits, prepId
from Products.ZenRelations.RelSchema import *
from Products.ZenWidgets import messaging


def manage_addDatabase(context, id, userCreated, REQUEST=None):
    """make a database"""
    dbid = prepId(id)
    db = Database(dbid)
    context._setObject(dbid, db)
    db = context._getOb(dbid)
    db.dbname = id
    if userCreated: db.setUserCreateFlag()
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(context.absolute_url()+'/manage_main') 

addDatabase = DTMLFile('dtml/addDatabase',globals())

class Database(ZenPackPersistence, OSComponent):
    """
    Database object
    """

    ZENPACKID = 'ZenPacks.community.RDBMS'

    portal_type = meta_type = 'Database'

    manage_editDatabaseForm = DTMLFile('dtml/manageDatabase',globals())

    dbname = ""
    type = "RDBMS Database"
    contact = ""
    version = ""
    activeTime = ""
    totalBlocks = 0L
    blockSize = 1L
    status = 2

    statusConversions = [
                'Unknown:1',
                'Active:2',
                'Available:3',
                'Restricted:4',
                'Unavailable:5',
                ]

    statusmap ={1: ('grey', 3, 'Unknown'),
                2: ('green', 0, 'Active'),
                3: ('yellow', 3, 'Available'),
                4: ('orange', 4, 'Restricted'),
                5: ('red', 5, 'Unavailable'),
                }

    _properties = OSComponent._properties + (
        {'id':'dbname', 'type':'string', 'mode':'w'},
        {'id':'type', 'type':'string', 'mode':'w'},
        {'id':'contact', 'type':'string', 'mode':'w'},
        {'id':'version', 'type':'string', 'mode':'w'},
        {'id':'activeTime', 'type':'string', 'mode':'w'},
        {'id':'totalBlocks', 'type':'long', 'mode':'w'},
        {'id':'blockSize', 'type':'long', 'mode':'w'},
        {'id':'status', 'type':'int', 'mode':'w'},
        )

    _relations = OSComponent._relations + (
        ("os", ToOne(ToManyCont, "Products.ZenModel.OperatingSystem", "softwaredatabases")),
        ("dbsrvinstance", ToOne(ToMany, "ZenPacks.community.RDBMS.DBSrvInst", "databases")),
        )

    factory_type_information = (
        {
            'id'             : 'Database',
            'meta_type'      : 'Database',
            'description'    : """Arbitrary device grouping class""",
            'icon'           : 'FileSystem_icon.gif',
            'product'        : 'RDBMS',
            'factory'        : 'manage_addDatabase',
            'immediate_view' : 'viewDatabase',
            'actions'        :
            (
                { 'id'            : 'status'
                , 'name'          : 'Status'
                , 'action'        : 'viewDatabase'
                , 'permissions'   : (ZEN_VIEW,)
                },
                { 'id'            : 'events'
                , 'name'          : 'Events'
                , 'action'        : 'viewEvents'
                , 'permissions'   : (ZEN_VIEW, )
                },
                { 'id'            : 'perfConf'
                , 'name'          : 'Template'
                , 'action'        : 'objTemplates'
                , 'permissions'   : (ZEN_CHANGE_DEVICE, )
                },
                { 'id'            : 'viewHistory'
                , 'name'          : 'Modifications'
                , 'action'        : 'viewHistory'
                , 'permissions'   : (ZEN_VIEW_MODIFICATIONS,)
                },
            )
          },
        )

    security = ClassSecurityInfo()

    security.declareProtected(ZEN_CHANGE_DEVICE, 'setDBSrvInst')
    def setDBSrvInst(self, instname):
        """
        Set the dbsrvinstance relationship to the DB Server Instance specified
        by the given instance name.
        """
        for inst in self.os().softwaredbsrvinstances():
            if inst.dbsiname != instname: continue
            self.dbsrvinstance.addRelation(inst)
            break

    security.declareProtected(ZEN_VIEW, 'getDBSrvInst')
    def getDBSrvInst(self):
        try: return self.dbsrvinstance()
        except: return None

    def getDBSrvInstLink(self):
        dbsi = self.dbsrvinstance()
        return dbsi and dbsi.urlLink(text=str(dbsi.dbsiname),
                                    attrs={'target':'_top'}) or ""

    def dbSrvInstName(self):
        """
        Return the Database Server Instance Name
        """
        dbsi = self.dbsrvinstance()
        return dbsi and dbsi.dbsiname or ""

    def totalBytes(self):
        """
        Return the number of allocated bytes
        """
        return long(self.totalBlocks) * long(self.blockSize)

    def totalString(self):
        """
        Return the number of allocated bytes in human readable form ie 10MB
        """
        sas = self.totalBytes()
        return convToUnits(sas)

    def usedBytes(self):
        """
        Return the number of used bytes
        """
        su = self.cacheRRDValue('sizeUsed_sizeUsed', 0)
        return long(su) * long(self.blockSize)

    def usedString(self):
        """
        Return the number of used bytes in human readable form ie 10MB
        """
        sus = self.usedBytes()
        return convToUnits(sus)

    def blockSizeString(self):
        """
        Return the size of unit in bytes in human readable form ie 10MB
        """
        sus = long(self.blockSize)
        return convToUnits(sus)

    def availString(self):
        """
        Return the Available bytes in human readable form ie 10MB
        """
        sa = long(self.totalBytes()) - long(self.usedBytes())
        if sa < 0: sa = 0 
        return convToUnits(sa)

    def capacity(self):
        """
        Return the percentage capacity of a database using its rrd file
        """
        __pychecker__='no-returnvalues'
        usedBytes = long(self.usedBytes())
        totalBytes = long(self.totalBytes())
        if usedBytes > 0  and totalBytes > 0:
            return int(100.0 * usedBytes / totalBytes)
        return 'Unknown'

    def getRRDNames(self):
        """
        Return the datapoint name of this Database
        """
        return ['sizeUsed_sizeUsed']

    def viewName(self): 
        """
        Return the name of a Database
        """
        return self.dbname

    security.declareProtected(ZEN_CHANGE_DEVICE, 'convertStatus')
    def convertStatus(self, status):
        """
        Convert status to the status string
        """
        return self.statusmap.get(status, ('grey', 3, 'Other'))[2]

    security.declareProtected(ZEN_CHANGE_DEVICE, 'getStatus')
    def getStatus(self, statClass=None):
        """
        Return the status number for this component of class statClass.
        """
        if not self.monitored() \
            or not self.device() \
            or not self.device().monitorDevice(): return 0
        return self.status

    def getStatusImgSrc(self, status=None):
        """
        Return the img source for a status number
        """
        if status is None: status = self.getStatus()
        src = self.statusmap.get(status, ('grey', 3, 'Other'))[0]
        return '/zport/dmd/img/%s_dot.png' % src

    def statusDot(self, status=None):
        """
        Return the img source for a status number
        Return the Dot Color based on maximal severity
        """
        if status is None:
            status = self.getStatus()
        return self.statusmap.get(status, ('grey', 3, 'Other'))[0]

    def statusString(self, status=None):
        """
        Return the status string
        """
        if status is None:
            status = self.getStatus()
        return self.getStatusString(status)

    def getRRDTemplates(self):
        """
        Return the RRD Templates list
        """
        for tmplName in (self.__class__.__name__, self.meta_type):
            template = self.getRRDTemplateByName(tmplName)
            if template is not None: break
        else:
            return []
        return [template]

    def manage_editDatabase(self, monitor=False,
                dbname=None, type=None, blockSizes=None, 
                totalBlocks=None, REQUEST=None):
        """
        Edit a Database from a web page.
        """
        if dbname:
            self.dbname = dbname
            self.type = type
            self.blockSize = blockSize
            self.totalBlocks = totalBlocks

        self.monitor = monitor
        self.index_object()

        if REQUEST:
            REQUEST['message'] = "Database updated"
            messaging.IMessageSender(self).sendToBrowser(
                'Database Updated',
                'Database %s was updated.' % dbname
            )
            return self.callZenScreen(REQUEST)

InitializeClass(Database)
