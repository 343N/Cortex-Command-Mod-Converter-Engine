from pathlib import Path
from addict import Dict as DotDict
from src.section import Section, SectionTypes


class InvalidFile(Exception):
    pass


class IniReader:
    def __init__(self) -> None:
        pass

    class States:
        Property = 0
        Value = 1
        Newline = 2
    
    @classmethod
    def read_file(cls, path: Path) -> list[Section]:
        if path.suffix != ".ini":
            raise InvalidFile(
                "The file being read is not an ini file! Something went wrong!"
            )

        # We ignore
        f = open(path, encoding="utf-8", errors="ignore")
        return cls.read_str(f.read())

    

    
    @classmethod
    def read_str(cls, content: str) -> list[Section]:
        # storing each section in a stack (each block of data)
        sections = []

        indents = 0
        spaces = 0
        sections = []
        comment_stack = []
        comments = []
        cur_section_comment = ""
        cur_property = ""
        cur_value = ""
        
        
        IN_PROPERTY = True
        IN_SINGLE_COMMENT = False
        IN_MULTI_COMMENT = False

        sec = Section()
        max_ind = len(content) - 1
        for i, char in enumerate(content):


            IN_COMMENT = IN_SINGLE_COMMENT or IN_MULTI_COMMENT
            if IN_COMMENT:
                if IN_SINGLE_COMMENT and char == "\n":
                    IN_SINGLE_COMMENT = False
                    IN_COMMENT = IN_MULTI_COMMENT
                elif (char not in ('/', '*')):
                    cur_section_comment += char
                elif IN_MULTI_COMMENT:
                    if char == '/':
                        if content[i-1] == '*':
                            start = comment_stack.pop()
                            end = i
                            comments.append((start, end, content[start:end]))
                            sec.comment += content[start:end-1]
                            IN_MULTI_COMMENT = len(comment_stack) > 0
                    


            if not IN_COMMENT:
                if not cur_property:
                    if char == "\t":
                        indents += 1
                        continue
                    elif char == " ":
                        spaces += 1
                        if (spaces == 4):
                            indents += 1
                            spaces = 0
                        continue
                    else: 
                        IN_PROPERTY = True

                if IN_PROPERTY:
                    if (char == "/" and content[i-1] == "/" and not IN_MULTI_COMMENT):
                        IN_SINGLE_COMMENT = True
                        cur_property = cur_property[:-2]    
                    elif (char == "*" and content[i-1] == "/" and not IN_SINGLE_COMMENT):
                        cur_property = cur_property[:-2]
                        IN_MULTI_COMMENT = True
                        # comment_stack.append(i-1)
                    elif (char in ("=", "\n")):
                        IN_PROPERTY = False
                        cur_property = cur_property.strip()
                    else:
                        cur_property += char
                else:
                    cur_value += char
                    if (char == "/" and content[i-1] == "/"):
                        IN_SINGLE_COMMENT = True
                        cur_value = cur_value[:-1]
                    elif (char == "*" and content[i-1] == "/"):
                        cur_property = cur_value[:-1]
                        IN_MULTI_COMMENT = True
                        comment_stack.append(i-1)
                
            if (char == '\n' and not IN_MULTI_COMMENT) or i == max_ind:
                if cur_property:
                    sec.property = cur_property.strip()
                    cur_property = ""
                if cur_value:
                    sec.value = cur_value.strip()
                    cur_value = ""
                if cur_section_comment:
                    sec.comment = cur_section_comment
                    cur_section_comment = ""
                if indents:
                    sec.indent = indents
                    indents = 0
                    spaces = 0
                
                if sec.value:
                    sec.type = SectionTypes.Property
                else: 
                    if sec.property and sec.property.strip() == "DataModule":
                        sec.type = SectionTypes.DataModule
                    elif(sec.comment):
                        sec.type = SectionTypes.Comment
                    else: 
                        sec.type = SectionTypes.Empty
                sections.append(sec)
                sec = Section()
                continue
  

        parent = None        
        final_tree = []
        prop_dict = DotDict()
        val_dict = DotDict()

        for sec in sections:
            last_ind = parent.indent if parent else 0 
            if sec.indent == 0:
                final_tree.append(sec)
                parent = sec
            elif sec.type:
                if sec.indent == last_ind + 1:
                    parent.add_child(sec)
                elif sec.indent == last_ind:
                    if (parent):
                        parent.add_sibling(sec)
                elif sec.indent > last_ind:
                    for i in range(sec.indent - last_ind):
                        parent = parent.parent
            
            parent = sec
            if (sec.property):
                if (sec.property in prop_dict):
                    prop_dict[sec.property].append(sec)
                else: 
                    prop_dict[sec.property] = [sec]
            if (sec.value):
                if (sec.value in val_dict):
                    val_dict[sec.value].append(sec)
                else:
                    val_dict[sec.value] = [sec]

            
        return final_tree, prop_dict, val_dict


            





    @classmethod
    def get_line_data(cls, line: str):
        # get indent
        indent = cls.get_line_indent(line)

        # prepare to read the string for indexes
        sl_cmt = None
        ml_cmt = []
        eq_ind = None
       
        open_block_comments = 0
        property_ind = None
        value_ind = None
        property = None
        value = None

        # parse the line:
        #   get the indexes of important characters
        #   get the property and value
        sl_cmt
        preceding_slash = False
        preceding_star = False
        


        max_ind = len(line) - 1
        for i, char in enumerate(line):
            # write comment if we're in a block comment
            if (open_block_comments > 0):
                comment += char
            # check for comments
            if char == "/":
                if preceding_slash:
                    sl_cmt = i
                    sl_comment = line[sl_cmt-1:]
                elif preceding_star:
                    preceding_star = False
                    ml_cmt.append(("close", i))
                    comment = comment[:-2]
                    open_block_comments -= 1

                preceding_slash = True
                continue
            elif char == "*":
                preceding_star = True
                if preceding_slash:
                    open_block_comments += 1
                    ml_cmt.append(("open", i - 1))
                continue
            elif char == "=":
                if (not eq_ind): eq_ind = i
                if (property_ind):
                    property = line[property_ind:i].strip()
            elif char.isspace():
                pass
            elif (eq_ind):
                if (not value_ind and open_block_comments <= 0):
                    value_ind = i
            else:
                if (not property_ind and open_block_comments <= 0):
                    property_ind = i
                    continue

            if(i == max_ind):
                if (property_ind and not eq_ind):
                    property = line[property_ind-1:i+1].strip()
                elif (eq_ind and value_ind):
                    value = line[value_ind-1:i+1].strip()
            
            preceding_star = False
            preceding_slash = False


        # dot notation is a blessing
        res = DotDict()
        res.indent = indent
        res.has_sl_comment = bool(sl_cmt)
        res.block_comments = ml_cmt
        res.open_block_change = open_block_comments
        res.property = property
        res.value = value
        res.isDataModule = bool(property == "DataModule")
        res.comment = comment

        return res

    @classmethod
    def get_line_indent(cls, line: str):

        pre = len(line) - len(line.lstrip())

        indent = 0
        spaces = 0
        for i in range(pre):
            if line[i] == " ":
                spaces += 1
            else:
                indent += 1

            if spaces == 4:
                indent += 1
                spaces = 0
            # assume it's a tab character. should we be seeing anything else?

        return indent
