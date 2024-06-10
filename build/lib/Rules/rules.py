import re
import os

class RuleSet:
    def extract_content_sections(self, content, file_name):
        raise NotImplementedError("This method should be implemented by subclasses")

    def post_process_html(self, html_content, dir, file_name):
        return html_content

# Variants
class VariantsRuleSet(RuleSet):
    variant_classes = {
        "cosmic": "cosmic",
        "elemental": "elemental",
        "ethereal": "ethereal",
        "guardian": "guardian",
        "lucky": "lucky",
        "mythical": "mythical",
        "nature": "nature",
        "nightmare": "nightmare",
        "rage": "rage",
        "resource": "resource",
        "summoner": "summoner",
        "unstable": "unstable",
        "utility": "utility"
    }
    
    def extract_content_sections(self, content, file_name):
        if os.path.basename(file_name) == "index.txt":
            isIndexFile = True
        else:
            isIndexFile = False
        # Discard the beginning of the text file
        content = re.sub(r'^<span style=.*?</span>:', '', content)

        # Split the content into header and rest based on -----
        header_info, *rest = re.split(r'-{4,}', content.strip())
        rest_content = rest[0] if rest else ""

        # In the header, replace single newlines with spaces (to merge lines) and double newlines with a unique separator
        header_info = re.sub(r'\n(?!\n)', ' ', header_info)
        header_info = re.sub(r'\n(?!\n)', '\n\n', header_info)

        # Extract key:value pairs and categorize them
        key_value_pattern = re.compile(r"^(.*?):\s(.*?)$", re.MULTILINE)
        if isIndexFile:
            sections = ["", "", ""] #Initialize with 3 sections
        else:
            sections = ["", "", "", ""]  # Initialize with 4 sections
        section_content = []

        if isIndexFile and len(rest) > 1:
            sections[2] = rest[1]

        in_variant_info = False
        in_other_info = False

        for line in rest_content.splitlines():
            line = line.strip()
            if not line:
                continue
            if key_value_pattern.match(line):
                key, value = key_value_pattern.match(line).groups()
                # Wrap "Taking Damage" and "Dealing Damage" in their respective CSS classes
                if "Taking Damage" in key:
                    key = key.replace("Taking Damage", '<span class="taking-damage">Taking Damage</span>')
                if "Dealing Damage" in key:
                    key = key.replace("Dealing Damage", '<span class="dealing-damage">Dealing Damage</span>')
                section_content.append(f'<span class="key">{key}:</span> <span class="value">{value}</span>')
            else:
                if 'Variant Information:' in line:
                    sections[1] = "\n".join(section_content)  # Finish Section 2
                    section_content = []
                    section_content.append(f'<h2>{line}</h2>')
                    in_variant_info = True
                    in_other_info = False
                elif 'Other Information:' in line:
                    sections[2] = "\n".join(section_content)  # Finish Section 3
                    section_content = []
                    section_content.append(f'<h2>{line}</h2>')
                    in_variant_info = False
                    in_other_info = True
                else:
                    section_content.append(f'{line}')

        sections[0] = header_info.strip()
        if isIndexFile:
            sections[1] = "\n".join(section_content)
        else:
            sections[3] = "\n".join(section_content)  # Finish Section 4

        return sections

    def post_process_html(self, html_content, dir, file_name):
        dir_path, dir_name = os.path.split(dir)
        variant_class = self.variant_classes.get(dir_name.lower(), "default")
        html_content = html_content.replace("VariantClass", variant_class)
        if os.path.basename(file_name) == "index.txt":
            if variant_class == "default":
                html_content = html_content.replace("Index", "Variants")
            else:
                html_content = html_content.replace("Index", variant_class.upper())
            
        return html_content

#Dinos
class DinosRuleSet(RuleSet):

    def extract_content_sections(self, content, file_name):
        if os.path.basename(file_name) == "index.txt":
            isIndexFile = True
        else:
            isIndexFile = False
        # Extract key:value pairs and categorize them
        key_value_pattern = re.compile(r"^(.*?):\s(.*?)$", re.MULTILINE)
        if isIndexFile:
            sections = [""] #Initialize with 1 sections
        else:
            sections = ["", "", "", "", "", "", "", ""]  # Initialize with 8 sections
        section_content = []

        section = 0
        foodSection = False
        for line in content.splitlines():
            line = line.strip()
            if not line:
                #increment section
                sections[section] = "\n".join(section_content)
                section += 1
                section_content = []
                continue
            if key_value_pattern.match(line):
                    key, value = key_value_pattern.match(line).groups()
                    section_content.append(f'<span class="dino-key">{key}:</span> <span class="dino-value">{value}</span>')
            elif isIndexFile:
                    section_content.append(f'{line}')
            else:
                if re.match(r'.*:$', line):
                    section_content.append(f'<h3>{line}</h3>')
                    if "Food Types" in line:
                        foodSection = True
                        section_content.append(f'\n<ul>')
                else:
                    if foodSection is True:
                        section_content.append(f'<li>{line}</li>')

        #finish final section
        if foodSection is True:
            section_content.append(f'</ul>')
            sections[section] = "".join(section_content)
        else:
            sections[section] = "\n".join(section_content)

        return sections

    def post_process_html(self, html_content, dir, file_name):
        html_content = html_content.replace("default", "")
        dir_path, dir_name = os.path.split(dir)
        dir_name = dir_name.split(' ', 1)[1]

        if os.path.basename(file_name) == "index.txt":
            html_content = html_content.replace("Index", dir_name)
        return html_content


# Most lists and text files
class listRuleSet(RuleSet):

    def extract_content_sections(self, content, file_name):

        # Preprocess the content to handle newlines. Combine lines seperated with a single newline
        # unless the next line beings with a digit or a -, indicating that it's a list item.
        def preprocess_newlines(text):
            text = re.sub(r'\n(?!\n|\d|-)', ' ', text)
            return text

        # Preprocess the content first
        preprocessed_content = preprocess_newlines(content.strip())

        # Split the content into header and rest based on -----
        header_info, *rest = re.split(r'-{4,}', preprocessed_content)

        rest_content = rest[0] if rest else ""

        # Extract key:value pairs and categorize them
        key_value_pattern = re.compile(r"^(\b\w+\b\s?){0,3}:\s(.*?)$", re.MULTILINE)
        sections = ["", ""]  # Initialize with 2 sections
        section_content = []

        if not rest_content:
            rest_content = header_info
            oneSection = True
        else:
            oneSection = False

        listStart = False
        bulletListStart = False
        for line in rest_content.splitlines():
            line = line.strip()
            if not line:
                continue
            if key_value_pattern.match(line):
                key, value = key_value_pattern.match(line).groups()
                section_content.append(f'<span class="list-key">{key}:</span> <span class="list-value">{value}</span>')
            elif line.startswith('- ') or line.startswith('-'):
                if not bulletListStart:
                    section_content.append('<ul>')
                    bulletListStart = True
                section_content.append(f'<li>{line[1:]}</li>')
            elif re.match(r'^\d+\.\)', line) or re.match(r'^\d+\.', line):
                if bulletListStart:
                    section_content.append('</ul>')
                    bulletListStart = False
                line = re.sub(r'^\d+\.\)?', '', line).strip()
                if not listStart:
                    section_content.append('<ol>')
                    listStart = True
                section_content.append(f'<li>{line}</li>')
            else:
                if listStart:
                    section_content.append('</ol>')
                    listStart = False
                if bulletListStart:
                    section_content.append('</ul>')
                    bulletListStart = False
                section_content.append(f'{line}\n<br>')

        if listStart:  # Close the ordered list if it's still open
            section_content.append('</ol>')
        if bulletListStart:  # Close the unordered list if it's still open
            section_content.append('</ul>')

        if oneSection is False:
            sections[0] = header_info.strip()
            sections[1] = "\n".join(section_content) if section_content else ""
        else:
            sections[0] = "".join(section_content)

        return sections

    def post_process_html(self, html_content, dir, file_name):
        html_content = html_content.replace("default", "")
        dir_path, dir_name = os.path.split(dir)
        dir_name = dir_name.split(' ', 1)[1]

        if os.path.basename(file_name) == "index.txt":
            html_content = html_content.replace("Index", dir_name)
        return html_content

#Bosses
# Most lists and text files
class BossesRuleSet(RuleSet):

    def extract_content_sections(self, content, file_name):

        # Preprocess the content to handle newlines. Combine lines seperated with a single newline
        # unless the next line beings with a digit or a -, indicating that it's a list item.
        def preprocess_newlines(text):
            text = re.sub(r'\n(?!\n|\d|-)', ' ', text)
            return text

        # Preprocess the content first
        preprocessed_content = preprocess_newlines(content.strip())

        # Split the content into header and rest based on -----
        header_info, *rest = re.split(r'-{4,}', preprocessed_content)

        rest_content = rest[0] if rest else ""

        # Extract key:value pairs and categorize them
        key_value_pattern = re.compile(r"^(\b\w+\b\s?){0,3}:\s(.*?)$", re.MULTILINE)
        sections = ["", ""]  # Initialize with 2 sections
        section_content = []

        if not rest_content:
            rest_content = header_info
            oneSection = True
        else:
            oneSection = False

        listStart = False
        bulletListStart = False
        for line in rest_content.splitlines():
            line = line.strip()
            if not line:
                continue
            if key_value_pattern.match(line):
                key, value = key_value_pattern.match(line).groups()
                section_content.append(f'<span class="list-key"><h3>{key}:</h3>\n</span>')
                section_content.append(f'{value}')
            elif line.startswith('- ') or line.startswith('-'):
                if not bulletListStart:
                    section_content.append('<ul>')
                    bulletListStart = True
                section_content.append(f'<li>{line[1:]}</li>')
            elif re.match(r'^\d+\.\)', line) or re.match(r'^\d+\.', line):
                if bulletListStart:
                    section_content.append('</ul>')
                    bulletListStart = False
                line = re.sub(r'^\d+\.\)?', '', line).strip()
                if not listStart:
                    section_content.append('<ol>')
                    listStart = True
                section_content.append(f'<li>{line}</li>')
            else:
                if listStart:
                    section_content.append('</ol>')
                    listStart = False
                if bulletListStart:
                    section_content.append('</ul>')
                    bulletListStart = False
                section_content.append(f'{line}\n')

        if listStart:  # Close the ordered list if it's still open
            section_content.append('</ol>')
        if bulletListStart:  # Close the unordered list if it's still open
            section_content.append('</ul>')

        if oneSection is False:
            sections[0] = header_info.strip()
            sections[1] = "\n".join(section_content) if section_content else ""
        else:
            sections[0] = "".join(section_content)

        return sections

    def post_process_html(self, html_content, dir, file_name):
        html_content = html_content.replace("default", "")
        dir_path, dir_name = os.path.split(dir)
        dir_name = dir_name.split(' ', 1)[1]

        if os.path.basename(file_name) == "index.txt":
            html_content = html_content.replace("Index", dir_name)
        return html_content

# default Rules
class defaultRuleSet(RuleSet):

    def extract_content_sections(self, content, file_name):

        # Split the content into header and rest based on -----
        header_info, *rest = re.split(r'-{4,}', content.strip())
        rest_content = rest[0] if rest else ""

        # In the header, replace single newlines with spaces (to merge lines) and double newlines with a unique separator
        header_info = re.sub(r'\n(?!\n)', ' ', header_info)
        header_info = re.sub(r'\n(?!\n)', '\n\n', header_info)

        # Extract key:value pairs and categorize them
        sections = [""]  # Initialize with 1 sections
        section_content = []

        for line in rest_content.splitlines():
            line = line.strip()
            if not line:
                continue
            section_content.append(f'{line}')

        sections[0] = header_info.strip()

        return sections

    def post_process_html(self, html_content, dir, file_name):
        html_content = html_content.replace("default", "")
        dir_path, dir_name = os.path.split(dir)
        dir_name = dir_name.split(' ', 1)[1]

        if os.path.basename(file_name) == "index.txt":
            html_content = html_content.replace("Index", dir_name)
        return html_content
