import sys
import maya.api.OpenMaya as om
import pymel.core as pmc

def maya_useNewAPI():
    pass


class Node(om.MPxNode):
    nodeName = 'controlCurveCreator'
    nodeClass = 'general'
    nodeId = om.MTypeId(0x000fc)

    aMatrices = om.MObject()

    aOutCurve = om.MObject()

    def __init__(self):
        om.MPxNode.__init__(self)

    @staticmethod
    def create():
        return Node()

    @staticmethod
    def initialize():
        tAttr = om.MFnTypedAttribute()
        mAttr = om.MFnMatrixAttribute()

        Node.aMatrices = mAttr.create(
            'matrices', 'ms', om.MFnMatrixAttribute.kDouble)
        mAttr.readable = False
        mAttr.array = True
        Node.addAttribute(Node.aMatrices)

        Node.aOutCurve = tAttr.create(
            'outCurve', 'oc', om.MFnNurbsCurveData.kNurbsCurve)
        tAttr.writable = False
        Node.addAttribute(Node.aOutCurve)

        Node.attributeAffects(Node.aMatrices, Node.aOutCurve)

    def compute(self, plug, data):

        if plug == Node.aOutCurve:

            matricesHandle = data.inputArrayValue(Node.aMatrices)
            curveHandle = data.outputValue(Node.aOutCurve)
            points = om.MPointArray()
            while True:
                mat = matricesHandle.inputValue().asMatrix()

                p = om.MPoint(0, 0, 0, 1)
                points.append(p*mat)
                p = om.MPoint(0, 0.1, 0, 1)
                points.append(p*mat)

                if not matricesHandle.next():
                    break
            
            print points
            curveDataCreator = om.MFnNurbsCurveData()
            curveData = curveDataCreator.create()
            curveFn = om.MFnNurbsCurve()
            curve = curveFn.create(
                points, range(len(points)), 1,
                om.MFnNurbsCurve.kOpen, False, False, curveData)

            curveHandle.setMObject(curveData)

            data.setClean(plug)


class createCurveCmd(om.MPxCommand):
    commandName = 'createCurve'
    
    def __init__(self):
        om.MPxCommand.__init__(self)
        
    @staticmethod
    def create():
        return createCurveCmd()
        
    def doIt(self, args):
        selected = pmc.ls(sl=True)
        creatorNode = pmc.createNode('controlCurveCreator')
        fitNode = pmc.createNode('fitBspline')
        curveNode = pmc.createNode('nurbsCurve')
        
        for i,t in enumerate(selected):
            t.matrix >> creatorNode.matrices[i]
            
        creatorNode.outCurve >> fitNode.inputCurve
        fitNode.outputCurve >> curveNode.create
        fitNode.tolerance.set(0.01)
        

##########################################################
# Plug-in initialization.
##########################################################
def initializePlugin(mobject):

    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.registerNode(
            Node.nodeName,
            Node.nodeId,
            Node.create,
            Node.initialize,
            om.MPxNode.kDependNode,
            Node.nodeClass)
    except:
        sys.stderr.write(
            'Failed to register node: ' + Node.nodeName)
        raise
        
    try:
        mplugin.registerCommand(
            createCurveCmd.commandName,
            createCurveCmd.create)
    except:
        sys.stderr.write(
            'Failed to register createCurveCmd: ' + createCurveCmd.commandName)
        raise


def uninitializePlugin(mobject):
    ''' Uninitializes the plug-in '''
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(Node.nodeId)
    except:
        sys.stderr.write(
            'Failed to deregister node: ' + Node.nodeName)
        raise
        
    try:
        mplugin.deregisterCommand(createCurveCmd.commandName)
    except:
        sys.stderr.write(
            'Failed to unregister createCurveCmd: ' + createCurveCmd.commandName)
        raise

