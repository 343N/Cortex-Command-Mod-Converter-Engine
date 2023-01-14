from pathlib import Path
from addict import Dict as DotDict
from src.section import Section, SectionTypes


class InvalidFile(Exception):
    pass


class IniReader:
    def __init__(self) -> None:
        pass

    
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
        ML_MULTIPLE_LINE = False

        sec = Section()
        max_ind = len(content) - 1
        for i, char in enumerate(content):


            IN_COMMENT = IN_SINGLE_COMMENT or IN_MULTI_COMMENT
            if IN_COMMENT:
                if char == "\n":
                    if IN_MULTI_COMMENT:
                        ML_MULTIPLE_LINE = True
                    if IN_SINGLE_COMMENT:
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
                        comment_stack.append(i-1)
                    elif (char in ("=", "\n")):
                        IN_PROPERTY = False
                        cur_property = cur_property.strip()
                    else:
                        cur_property += char
                else:
                    cur_value += char
                    if (char == "/" and content[i-1] == "/"):
                        IN_SINGLE_COMMENT = True
                        cur_value = cur_value[:-2]
                    elif (char == "*" and content[i-1] == "/"):
                        cur_value = cur_value[:-2]
                        IN_MULTI_COMMENT = True
                        comment_stack.append(i-1)
                
            if ((char == '\n' or ML_MULTIPLE_LINE) and not IN_MULTI_COMMENT) or i == max_ind:
                ML_MULTIPLE_LINE = False
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


            