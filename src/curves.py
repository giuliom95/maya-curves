import maya.api.OpenMaya as om


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

        Node.aMatrices = tAttr.create(
            'matrices', 'ms', om.MFnMatrixData.kMatrix)
        tAttr.readable = False
        tAttr.array = True
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

                print mat
                print
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


def uninitializePlugin(mobject):
    ''' Uninitializes the plug-in '''
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(Node.nodeId)
    except:
        sys.stderr.write(
            'Failed to deregister node: ' + Node.nodeName)
        raise
