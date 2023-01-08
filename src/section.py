class SectionTypes():
    DataModule = 0
    Comment = 1
    Property = 2
    Empty = 3

class NoParentException(Exception):
    pass

class Section():


    def __init__(self) -> None:
        self.type = SectionTypes.Empty
        # the property, if any
        self.property = ""
        # the value, if any
        self.value = ""
        # the comments, if any
        self.comment = ""
        # the content, if any
        self.content = ""
        self.parent = None
        self.indent = 0
        self.children = []
        

    def add_child(self, child: "Section"):
        self.children.append(child)
        child.parent = self

    def add_sibling(self, siblling: "Section"):
        if (not self.parent):
            raise NoParentException()
        self.parent.add_child(siblling)