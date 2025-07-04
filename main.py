import json
from random import choice
import shutil

from typing import List, Union, Optional, Literal, TypedDict, Set

# --- Structured Content Types ---

class StructuredContentData(TypedDict, total=False):
    # Arbitrary key-value data attributes
    # For simplicity, using str->str
    pass

class StructuredContentStyle(TypedDict, total=False):
    fontStyle: Literal["normal", "italic"]
    fontWeight: Literal["normal", "bold"]
    fontSize: str
    color: str
    background: str
    backgroundColor: str
    textDecorationLine: Union[
        Literal["none", "underline", "overline", "line-through"],
        List[Literal["underline", "overline", "line-through"]]
    ]
    textDecorationStyle: Literal["solid", "double", "dotted", "dashed", "wavy"]
    textDecorationColor: str
    borderColor: str
    borderStyle: str
    borderRadius: str
    borderWidth: str
    clipPath: str
    verticalAlign: Literal["baseline", "sub", "super", "text-top", "text-bottom", "middle", "top", "bottom"]
    textAlign: Literal["start", "end", "left", "right", "center", "justify", "justify-all", "match-parent"]
    textEmphasis: str
    textShadow: str
    margin: str
    marginTop: Union[str, int]
    marginLeft: Union[str, int]
    marginRight: Union[str, int]
    marginBottom: Union[str, int]
    padding: str
    paddingTop: str
    paddingLeft: str
    paddingRight: str
    paddingBottom: str
    wordBreak: Literal["normal", "break-all", "keep-all"]
    whiteSpace: str
    cursor: str
    listStyleType: str

StructuredContent = Union[
    str,
    List["StructuredContent"],
    "StructuredContentObject"
]

class StructuredContentObjectBase(TypedDict, total=False):
    data: StructuredContentData
    lang: str
    content: 'StructuredContent'
    style: StructuredContentStyle
    title: str
    open: bool

class ImgTag(StructuredContentObjectBase):
    tag: Literal["img"]
    path: str
    width: Optional[float]
    height: Optional[float]
    alt: Optional[str]
    description: Optional[str]
    pixelated: Optional[bool]
    imageRendering: Optional[Literal["auto", "pixelated", "crisp-edges"]]
    appearance: Optional[Literal["auto", "monochrome"]]
    background: Optional[bool]
    collapsed: Optional[bool]
    collapsible: Optional[bool]
    verticalAlign: Optional[str]
    border: Optional[str]
    borderRadius: Optional[str]
    sizeUnits: Optional[Literal["px", "em"]]

class ATag(StructuredContentObjectBase):
    tag: Literal["a"]
    href: str

class GenericTag(StructuredContentObjectBase):
    tag: Literal["ruby", "rt", "rp", "table", "thead", "tbody", "tfoot", "tr", "td", "th", "span", "div", "ol", "ul", "li", "details", "summary", "br"]
    colSpan: Optional[int]
    rowSpan: Optional[int]

StructuredContentObject = Union[ImgTag, ATag, GenericTag]

# --- Definitions ---

class TextDefinition(TypedDict):
    type: Literal["text"]
    text: str

class ImageDefinition(TypedDict):
    type: Literal["image"]
    path: str
    width: int
    height: int
    title: Optional[str]
    alt: Optional[str]
    description: Optional[str]
    pixelated: Optional[bool]
    imageRendering: Optional[Literal["auto", "pixelated", "crisp-edges"]]
    appearance: Optional[Literal["auto", "monochrome"]]
    background: Optional[bool]
    collapsed: Optional[bool]
    collapsible: Optional[bool]

class StructuredDefinition(TypedDict):
    type: Literal["structured-content"]
    content: StructuredContent

Definition = Union[
    str,
    TextDefinition,
    ImageDefinition,
    StructuredDefinition,
    List[Union[str, List[str]]]  # deinflection: [base, [rules]]
]

# --- Dictionary Entry ---

DictionaryEntry = List[
    Union[
        str,                          # 0: term
        str,                          # 1: reading
        Optional[str],                # 2: def tags
        str,                          # 3: deinflection rules
        float,                        # 4: score
        List[Definition],             # 5: definitions
        int,                          # 6: sequence number
        str                           # 7: term tags
    ]
]

import re

def convert_to_deinflection(entry: DictionaryEntry) -> DictionaryEntry:
    term, reading, def_tags, rules, score, definitions, seq, term_tags = entry

    # Try to extract the base form from the string definition
    if isinstance(definitions, list) and len(definitions) == 1 and isinstance(definitions[0], str):
        match = re.search(r'of (\w+)', definitions[0])
        if match:
            base_form = match.group(1)
            # Build the new definitions field
            new_definitions: List[Definition] = [[base_form, rules.split()] if rules else [base_form, []]]
            return [term, reading, def_tags, rules, score, new_definitions, seq, term_tags]

    return entry  # unchanged if no match

def extract_base_and_form(definition: str) -> Optional[List[Union[str, List[str]]]]:
    """
    Given a definition string, returns [base_form, [inflection rules]].
    Returns None if no base form is found.
    """
    # Find all "of <word>" matches
    of_matches = list(re.finditer(r'\bof (\w+)', definition))
    if not of_matches:
        return None

    # Use the last match as the base form
    last_match = of_matches[-1]
    base = last_match.group(1)

    # Get everything before the last "of"
    form_text = definition[:last_match.start()]

    # Remove text in {...} and (...)
    form_text = re.sub(r'\{.*?\}|\(.*?\)', '', form_text).strip()

    # Split on whitespace and slashes
    form_parts = re.split(r'[ /]+', form_text)

    # Filter out junk tokens like '->' or empty strings
    form_parts = [part for part in form_parts if part and part != '->']

    return [base, form_parts]

seen_list: Set[str] = set()
def convert_filler_definition(entry: DictionaryEntry) -> Optional[DictionaryEntry]:
    term, reading, def_tags, rules, score, definitions, seq, term_tags = entry

    if def_tags != "non-lemma":
        seen_list.add(term)
        # print(f"seen non-lemma term: {term}")
        # print("seen ", term)
        return entry

    if isinstance(definitions, list) and isinstance(definitions[0], str):
        if term in seen_list:
            # print(f"already seen {term}!")
            return None
        definition = definitions[0].replace("the", "")

        if not any(map(lambda x: re.search(r'\(\->(.+)\)', x), definitions)):
            print(f"[err] couldn't figure out base for {term}: {definition}")
            return entry

        # if not any(map(lambda x: re.search(r'\bof \w+', x), definitions)):
        #     return entry


        def uniq(lst: iter):
            last = object()
            for item in lst:
                if item == last:
                    continue
                yield item
                last = item


        def process_definition(definition: str):
            definition = definition.replace("the", "")
            raw_base = re.search(r'\(\->(.+)\)', definition)

            # if not re.search(r'\bof \w+', definition):
            #     return None

            base = raw_base.group(1)

            form_match = re.search(r'\}(.+)\(', definition)
            if not form_match:
                return None

            # form_text = definition[:form_match.start()]
            form_text = form_match.group(1)
            form_text = re.sub(r'\{.*?\}|\(.*?\)', '', form_text)  # remove {...} and (...)
            form_text = form_text.strip()
            form_parts = re.split(r'[ /]+', form_text)
            form_parts = [part for part in form_parts if part and part not in ['->', "of", "the"]]

            return [base, form_parts]

        processed_definitions = list(uniq(filter(lambda x: x is not None, [process_definition(definition) for definition in definitions])))

        return [term, reading, def_tags, rules, score, processed_definitions, seq, term_tags]

    return entry


from tqdm import tqdm

with open("term_bank_1.json") as file:
    data: List[DictionaryEntry] = json.load(file)

    # term = choice([term for term in data if/ term[0] == "prenez"])
    # term = data[90031]
    # print(term)
    # term = [i for i in data if i[0] == "génuflexés"][0]
    # term = [i for i in data if i[0] == "abluent"][0]
    # terms = [i for i in data if i[0] == "lire"]

    # print(convert_filler_definition(term))
    # for term in terms:
    #     print(convert_filler_definition(term))

    print(len(data))
    exit()
    with open("compat-dict/term_bank_1.json", "w") as file:
        newdict = []
        for term in tqdm(data):
            newdef = convert_filler_definition(term)
            if newdef:
                newdict.append(newdef)
        json.dump(newdict, file, ensure_ascii=False)
    print("making zip.")
    shutil.make_archive("compat-dict", 'zip', "compat-dict")
