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

    def get_writable_string(self, inc_children=True):
        
        IndentStr = self.indent * '\t'

        if (self.type == SectionTypes.DataModule):
            comment_str = f" // {self.comment}" if self.comment else ""
            to_write =  f"{IndentStr}{self.property}{comment_str}\n"
        elif (self.type == SectionTypes.Property):
            comment_str = f" // {self.comment}" if self.comment else ""
            to_write = f"{IndentStr}{self.property} = {self.value}{comment_str}\n"
        elif (self.type == SectionTypes.Comment):
            to_write = f"{IndentStr}/* {self.comment} */\n"
        elif (self.type == SectionTypes.Empty):
            to_write = f"{self.content}\n"
        
        if (inc_children):
            return to_write + ''.join([child.get_writable_string() for child in self.children])
        else:
            return to_write

