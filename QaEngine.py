# -*- coding: utf-8 -*-
import re, csv, os
from pathlib import Path

class QaEngine():
    extra_space_regex_list = ['^ +.{2,}',
                              '､ ',
                              ' ､',
                              '｡ ',
                              ' ｡',
                              '\( +',
                              ' +\)',
                              '[ぁ-んァ-ンー-龥]\s{1,}[ぁ-んァ-ンー-龥]',
                              ': $',
                              '[ぁ-んァ-ンー-龥]\s{2,}&lt;/.*?&gt;|&gt; {2,}[ぁ-んァ-ンー-龥]',
                             ]
    
    missing_space_regex_list = [
          '[A-Za-z0-9:?!|%$#\)][ぁ-んァ-ンー-龥]',
          '[ぁ-んァ-ンー-龥][A-Za-z0-9?!%$#|\(]',
          '[ぁ-んァ-ンー-龥]&lt;[^/].*?&gt;|&lt;/.*?&gt;[ぁ-んァ-ンー-龥]',
    ]

    zenkaku_non_jp_chars = '[Ａ-Ｚａ-ｚ０-９：！？＋＊＆＾％＄＃＠；／｛｝［］]'

    # zenkaku_special = '[＞＜＆’”]'
    # zenkaku_special_dict = {'＞':'&gt;', '＜':'&lt;', '＆':'&amp;', "’":'&apos;', '”':'&quot;'}

    jp_parenthesis = '[「」『』（）]'

    method = r'\b[a-zA-Z_.$#*-]+\(\)'

    segment_status = None
    
    literal_content_regex = '&lt;literal&gt;.*?&lt;/literal&gt;'
    punctuation = r"jp_char.$"

    

    def __init__(self, source, target, tag_info=None):
        #TODO: get lists of issues
        #TODO: 

        self.mistranslation_file = self.get_file_location('config/mistranslation.csv')
        self.cho_on_file = self.get_file_location('config/cho_on.csv')
        self.critical_term_file = self.get_file_location('config/critical_terms.txt')

        self.mistrans_dict = self.csv2dict(self.mistranslation_file)
        self.cho_on_dict = self.csv2dict(self.cho_on_file)

        self.source = source
        self.target = target
        self.tag_info = tag_info

        self.literal_content = self.get_literal_content()
        ##{0: {'id': '1', 'type': 'literal', 'content': '&lt;literal&gt;'},
        #  1: {'id': '2', 'type': 'emphasis', 'content': '&lt;emphasis&gt;'}}

        
        self.literal_content_issues = self.get_literal_content_issues()
        self.cho_on_issues = self.get_cho_on_issue()
        self.mistrans_issues = self.get_mistrans_issues()
        self.critical_term_issues = self.get_critical_term_issues()

        self.extra_space = self.get_space_issues(self.extra_space_regex_list)
        self.missing_space = self.get_space_issues(self.missing_space_regex_list)

        self.zenkaku_issues = self.get_zenkaku_issues(self.zenkaku_non_jp_chars)
        self.jp_parenthesis_issues = self.get_zenkaku_issues(self.jp_parenthesis)
        self.method_issues = self.get_method_issues(self.method)

        self.issue_dict = {
            "Extra Space": self.extra_space,
            "Missing Space": self.missing_space,
            "Character Byte": self.zenkaku_issues,
            "JP Parenthesis issues": self.jp_parenthesis_issues,
            "Mistranslation": self.mistrans_issues,
            "Cho-on": self.cho_on_issues,
            "Critical Terms": self.critical_term_issues,
            "Non-Translatable": self.literal_content_issues,
            "Method": self.method_issues,
        }

        self.existing_issues = self.get_issues(self.issue_dict)

        self.existing_issues_dict = self.get_existing_obj(self.issue_dict)
    
    def get_existing_obj(self, issue_dict):
        new_dict = {key:val for key, val in issue_dict.items() if key in issue_dict and issue_dict[key]}
        return new_dict

    def csv2dict(self, filename) -> dict:
        result_dict = {}
        with open(filename, 'r', encoding='utf-8', newline='') as mistrans_list:
            for line in mistrans_list:
                key, value = line.strip().split(',')
                result_dict[key] = value
        return result_dict
    
    def get_method_issues(self, method_regex) -> list or None:
        method_list = []
        match = re.findall(method_regex, self.source)
        if match:
            for method in match:
                if method not in self.target:
                    method_list.append(method)
        return method_list if method_list else None
                
    def get_issues(self, issue_dict):
        match = [issue_type for issue_type, issue_content in issue_dict.items() if not issue_content == None]
        return match if match else None
    
    def get_literal_content(self) -> list or None:
        match = re.findall(self.literal_content_regex, self.source)
        return match if match else None
    
    def get_literal_content_issues(self) -> list or None:
        match = False
        if self.literal_content != None:
            for item in self.literal_content:
                if item not in self.target:
                    match = re.findall('&lt;literal&gt;.*?&lt;/literal&gt;', self.target)
            return match if match else None
    
    def get_file_location(self, filename):
        current_dir = Path.cwd()
        return current_dir / filename

    def get_style_issue(self, regex: str) -> bool:
        return bool(re.search(regex, self.target))
    
    def get_cho_on_issue(self) -> list or None:
        cho_on_issues = []
        for key, value in self.cho_on_dict.items():
            match = re.findall(key+'.', self.target)
            end_match = re.findall('.'+key+'$', self.target)
            if match:
                 for element in match:
                     if element != value:
                        cho_on_issues.append(element)
            
            if end_match:##ending a sentence with a cho-on missing word
                for element in end_match:
                    if element[1:] == key:
                        cho_on_issues.append(element+'$')

            if key == self.target:
                cho_on_issues.append(key)
                
        return cho_on_issues if cho_on_issues else None
    
    def get_space_issues(self, regex_list):
        space_issues = []

        for regex in regex_list:
            match = re.findall(regex, self.target)
            print(match)
            if match:
                space_issues.extend(item for item in match)
        
        return space_issues if space_issues else None

    def get_mistrans_issues(self) -> list or None:
        mistrans_issues = []
        for key in self.mistrans_dict.keys():
            match = re.search(key, self.target)
            if match:
                mistrans_issues.append(match.group())
        return mistrans_issues if mistrans_issues else None
    
    def get_zenkaku_issues(self, regex) -> list or None:
        match = list(set(re.findall(regex, self.target)))
        return match if match else None

    def get_critical_term_issues(self) -> list or None:
        with open(self.critical_term_file, 'r', encoding='utf-8') as file:
            result = [item.rstrip() for item in file if item.rstrip() in self.source and item.rstrip() not in self.target]
            return result if result else None

    def has_issue_from_list(self, regex_list):
        return any(self.has_issue(regex) for regex in regex_list)
    
    def get_issue_list(self, regex):
        return re.findall(regex, self.target)
    
    def has_bf_af_tag_space_issues(self) -> bool:
        #space no space between chars  and tags, (Ex. xxx<literal>aaa</literal>aaa)
        regex = r"\S<(.*?)>|<(.*?)>\S"
        return self.has_issues(regex)

    def has_tag_colon_space_issues(self) -> bool:
        #sapce between tag and colon </literal>^: (this should not exist)
        regex = r'&gt; +:'
        return self.has_issues(regex)
    

source = "Since the installation abc.ecb() location of JBoss EAP will vary between host machines, this guide refers to the installation location as. &lt;literal&gt;&lt;emphasis&gt;abc&lt;/emphasis&gt;&lt;/literal&gt;"
target = "target: １２３ホストマシンによって JBoss EAPをインス abc.ecb () サ（（）ーバー１2３トールする場所が異なるため、サーバ  本ガイドではインストール「」場所を &lt;literal&gt;&lt;emphasis&gt;あいう&lt;/emphasis&gt;&lt;/literal&gt; と示しています。サーバ"
tag_info = '''({0: {'id': '1', 'type': 'emphasis', 'content': '&lt;emphasis role="strong"&gt;'}}, {0: {'id': '1', 'type': 'emphasis', 'content': '&lt;emphasis role="strong"&gt;'}})'''

sample = QaEngine(source, target, tag_info)
#print(sample.source)
#print(sample.target)
#print(sample.issue_dict)
#print(sample.existing_issues)
print(sample.issue_dict)
#print(sample.existing_issues_dict)

##TODO: return segment_info
##{seg_num:{}
