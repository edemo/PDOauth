from pydoctor.templatewriter.writer import TemplateWriter
import os
from pydoctor import model
from xml.dom.minidom import getDOMImplementation
from sourcecodegen.generation import generate_code

class MyWriter(TemplateWriter):
    
    def prepOutputDirectory(self):
        if not os.path.exists(self.base):
            os.mkdir(self.base)

    def writeModuleIndex(self, system):
        pass

    def writeDocsFor(self, ob, functionpages):
        self.f = open(os.path.join(self.base, "doc.xml"), 'w')
        impl = getDOMImplementation()
        self.doc = impl.createDocument(None, "documentation", None)
        top_element = self.doc.documentElement
        isfunc = ob.documentation_location == model.DocLocation.PARENT_PAGE
        if (isfunc and functionpages) or not isfunc:
            self.writeDocsForOne(ob, top_element)
        self.doc.writexml(self.f,indent=" ", addindent=" ", newl="\n")
        self.f.close()

    def setAttrIf(self, element, item, attname, modifier=unicode):
        v = getattr(item,attname,None)
        if v is not None:
            element.setAttribute(attname, modifier(v))


    def addChildsIf(self, element, item, name, xmlName, modifier=unicode, chooser = None, builder=None):
        argspec = getattr(item, name, None)
        if argspec is not None:
            if chooser is not None:
                argspec = chooser(argspec)
            for arg in argspec:
                a = self.doc.createElement(xmlName)
                if builder is None:
                    t = self.doc.createTextNode(modifier(arg))
                else:
                    t = builder(a, arg)
                a.appendChild(t)
                element.appendChild(a)

    def getFullName(self,ob):
        return ob.fullName()
    
    def getFirstItem(self, ob):
        return ob[0]
    
    def getDecorator(self,parent, ob):
        source = generate_code(ob)
        return self.doc.createTextNode(source)
    
    def writeElementForOne(self, child, item):
        e = self.doc.createElement(unicode(item.kind))
        child.appendChild(e)
        self.setAttrIf(e, item, "name")
        self.setAttrIf(e, item, "parentMod", self.getFullName)
        self.setAttrIf(e, item, "parent", self.getFullName)
        self.setAttrIf(e, item, "linenumber")
        self.setAttrIf(e, item, "filepath")
        self.addChildsIf(e, item, "bases", "base")
        self.addChildsIf(e, item, "subclasses", "subclass", modifier=self.getFullName)
        self.addChildsIf(e, item, "argspec", "arg", chooser=self.getFirstItem)
        self.addChildsIf(e, item, "decorators", "decorator", builder=self.getDecorator)
        if item.docstring is not None:
            t = self.doc.createTextNode(item.docstring)
            e.appendChild(t)
        return e

    def writeDocsForOne(self, ob, element):
        child = self.writeElementForOne(element, ob)
        element.appendChild(child)
        for item in ob.orderedcontents:
            e = self.writeElementForOne(child, item)
            oc = getattr(item,'orderedcontents', None)
            if oc is not None:
                for item in oc:
                    self.writeDocsForOne(item, e)
