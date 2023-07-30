# -*- coding: utf-8 -*-
from MxliffObj import MxliffObj
from QaEngine import QaEngine
import re, sys


html_end = """
</body>
</html>
"""

h2 = "<h2>{}: </h2>"

with open('test.mxliff', 'r', encoding='utf-8') as mxliff, open('output.html', 'w+', encoding='utf-8') as html:
    def set_issues(a_dict, source, target, seg_num):
        new_dict = {}
        for key, val in a_dict.items():
            if val != None:
                if key in new_dict and new_dict[key]:
                    new_dict[key] + {"seg_num":seg_num, "detail": {"source": source, "target": target, "issue": val}}
                else:
                    new_dict[key] = [{"seg_num":seg_num, "detail": {"source": source, "target": target, "issue": val}}]
        #print('1', new_dict['JP Parenthesis issues'])
        return new_dict
    
    def adding_issues(tmp_dict, issue_dict):
        #print('5', issue_dict)
        for key, val in tmp_dict.items():
            if key in issue_dict and issue_dict[key]:
                issue_dict[key] + val
            else:
                issue_dict[key] = val

    def rendering_html(issue_dict, mist_dict, choon_dict):
        highlight_tag = '<font color="red">{}</font>'
        for key, val in issue_dict.items():
            print("<h2 id=\"{}\">{}</h2>".format(key, key), file=html)
            for a_dict in val:
                #print(a_dict)
                seg_num = a_dict['seg_num']
                detail = a_dict['detail']
                print("<p><strong>Seg#{}</strong></p>".format(seg_num), file=html)
                num_issues = len(detail['issue'])
                issue_counter = 1
                for item in detail['issue']:
                    if issue_counter == 1 and num_issues == 1:
                        print("<p style=\"color:red\">" + item + "</p>", file=html)
                        issue_counter += 1
                    elif issue_counter == 1:
                        print("<p style=\"color:red\">" + item + ', ', file=html)
                        issue_counter += 1

                    elif issue_counter == num_issues:
                        print(item + "</p>", file=html)
                        issue_counter += 1
                    else:
                        print(item + ',', end='', file=html)
                        issue_counter += 1
                    
                target=detail['target']
                source=detail['source']
                for item in detail['issue']:
                    if key == 'Cho-on':
                        if '$' in item:
                            target = target.replace(item[:-1], item[0]+highlight_tag.format(item[1:-1]))
                        else:
                            target = target.replace(item, highlight_tag.format(item[:-1])+item[-1])
                    else:
                        target = target.replace(item, highlight_tag.format(item))
                    if key == 'Mistranslation':
                        for element in detail['issue']:
                            correct_term = mist_dict[element]
                            print('<p>"{}" maybe replaced with "{}"</p>'.format(element, correct_term), file=html)
                            
                    

                print("<p><strong>source:</strong> {}</p>".format(source), file=html)
                print("<p><strong>target:</strong> {}</p>".format(target), file=html)



    ##get a block
    mxliff_group_open= "<group id="
    mxliff_group_close = "</group>"
    mxliff_file_name = "<file original="
    filename_regex = r'<file original.*?\"(.*?)\"'
    storing = False
    block = []

    issue_dict = {}

    icon_sign = "<span><i class=\"fas fa-gear-sign\"></i></span>"

    
    html_start_header = """
<html>
    """
    html_header_rest = """
<head>
<style type="text/css">
<!--
h1 {
  position: relative;
  padding: 1em 2em;
  text-align: center;
}

h1:before,
h1:after {
  position: absolute;
  content: '';
}

h1:after {
  top: 20px;
  left: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-top: 2px solid #000;
  border-left: 2px solid #000;
}

h1:before {
  right: 10px;
  bottom: 10px;
  width: 50px;
  height: 50px;
  border-right: 2px solid #000;
  border-bottom: 2px solid #000;
}

h2 {
    background-color: whitesmoke;
    border-bottom: solid 2px black;
    border-left: solid 5px black;
    margin-left: 3%;
    margin-right: 20%;
    
}

h2:first-letter {
  font-size: 150%;
  color: #eb6100;
  border-bottom: 8px solid black;
}
p {
    line-height: 95%;
    margin-left: 5%;
    }
-->
</style>
</head>

<body>
    """

    
    for line in mxliff: ##block []
        if mxliff_file_name in line:
            title = re.search(filename_regex, line)
            print("<html>", file=html)
            print("<title>QA Report of {}</title>".format(title.group(1)), file=html)
            print(html_header_rest, file=html)
            print("<h1>QA Report of {}</h1>".format(title.group(1)), file=html)

        if mxliff_group_open in line:
            storing = True
        
        if mxliff_group_close in line:
            block.append(mxliff_group_close)
            storing = False
            #print(block)
            group = MxliffObj(block)
            if group.tag_info != None:
                segment = QaEngine(group.source_with_tags, group.target_with_tags, group.tag_info)
                if segment.existing_issues:
                    tmp_dict = set_issues(segment.issue_dict, group.source_with_tags, group.target_with_tags, group.segment_num)
                    print(segment.issue_dict)
                    adding_issues(tmp_dict, issue_dict)
            else:
                segment = QaEngine(group.source, group.target)
                if segment.existing_issues:
                    tmp_dict = set_issues(segment.issue_dict, group.source, group.target, group.segment_num)
                    adding_issues(tmp_dict, issue_dict)
            block = [] ##resetting obj

        if storing:
            block.append(line.strip("\n"))
    #print(issue_dict)
    rendering_html(issue_dict, segment.mistrans_dict, segment.cho_on_dict)
    print(html_end, file=html)



#{'Missing Space': [{'seg_num': 27,
#  'detail': {'source': 'For installation instructions, see the JBoss EAP &lt;link&gt;&lt;emphasis&gt;Installation Guide&lt;/emphasis&gt;&lt;/link&gt;.',
#  'target': 'インストールの手順は、JBoss EAPの『&lt;link&gt;&lt;emphasis&gt;Installation Guide&lt;/emphasis&gt;&lt;/link&gt;』を参照してください。',
#  'issue': ['Pの']}}], 'JP Parenthesis issues': [{'seg_num': 27, 'detail': {'source': 'For installation instructions, see the JBoss EAP &lt;link&gt;&lt;emphasis&gt;Installation Guide&lt;/emphasis&gt;&lt;/link&gt;.',
#  'target': 'インストールの手順は、JBoss EAPの『&lt;link&gt;&lt;emphasis&gt;Installation Guide&lt;/emphasis&gt;&lt;/link&gt;』を参照してくださ い。',
#  'issue': ['『', '』']}}],
#  'Mistranslation': [{'seg_num': 32, 'detail': {'source': 'JBoss EAP is supported on Red Hat Enterprise Linux, Windows Server,
#  and Oracle Solaris, and runs in either a standalone server or managed domain operating mode.',
#  'target': 'JBoss EAP は、Red Hat Enterprise Linux、Windows Server、および Oracle Solaris でサポートされ、スタンドアロンサーバーまたは管理対象ドメイン操作モードで実行されます。', 'issue': ['管理対象']}}]}