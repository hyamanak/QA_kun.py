import re
from TagProcessor import TagProcessor

class MxliffObj(list):
     #for tag searches
     source_tag = "<source>"
     target_tag = "<target>"
     source_close_tag = "</source>"
     target_close_tag = "</target>"
     special_tag = "<memsource:tag "
     tag_id_str = ""
     seg_num = "<group id="
     unit_tag = "<unit id="
     id_attr = "id="     
     
     
     #future ideas
     ## link check found/notfound would be nice.
     ##implementing spellcheck function 
     #regex for attributes
     segment_num_reg = "<group id=\"(.*?)\"" 
     
     '''
     source, target -> str 
     returns source and target segment without <source></source>
     tags are marked as <pc id='**'> for phrase
     
     segment_num -> int
     returns segment number of the current segment
     
     tag_info -> Obj of TagProcessor both source and target)
     (
          {
               0: {'id': '3', 'type': 'literal', 'content': '&lt;literal&gt;'}, 
               1: {'id': '4', 'type': 'emphasis', 'content': '&lt;emphasis&gt;'}
          }, 
          {
               0: {'id': '3', 'type': 'literal', 'content': '&lt;literal&gt;'}, 
               1: {'id': '4', 'type': 'emphasis', 'content': '&lt;emphasis&gt;'}
          }
     )
     
     source_with_tags, target_with_tags -> str
     returns segments with HTML tag format
     The actual location of the JBoss EAP installation should be used instead of &lt;literal&gt;&lt;emphasis&gt;EAP_HOME&lt;/emphasis&gt;&lt;/literal&gt; when performing administrative tasks.
     管理タスクを行う際には、 &lt;literal&gt;&lt;emphasis&gt;EAP_HOME&lt;/emphasis&gt;&lt;/literal&gt; を実際の JBoss EAP のインストール場所に置き換えてください。
     '''
     
     def __init__(self, group_list) -> None:
          self.group_list = group_list
          
          self.source = self.remove_source_target_tags(self.get_tag_element(self.group_list, self.source_tag)[0], self.source_tag, self.source_close_tag)
          self.target = self.remove_source_target_tags(self.get_tag_element(self.group_list, self.target_tag)[0], self.target_tag, self.target_close_tag)
          
          self.segment_num = self.get_segment_num()
          
          if self.has_tag():
               Tag_Obj = TagProcessor(
                    self.source, self.target, self.group_list
                    )
          
               self.tag_info = Tag_Obj.tag_info
               self.source_with_tags, self.target_with_tags = self.mtag2rtag()
          else:
               self.tag_info = None
     
     def remove_source_target_tags(self, segment, o_tag, c_tag):
               segment = segment.replace(o_tag, '')
               segment = segment.replace(c_tag, '')
               return segment
     
     def get_tag_element(self, list, tag) -> list:
          elements = [item for item in list if tag in item]
          return elements
     
     def make_close_tag(self, tag) -> str: 
          #takes type (literal) and return </literal>
          return '&lt;' + tag + '&gt;'
     
     def mtag2rtag(self) -> tuple:
          num = '' #tag_id such as 2, 3 ,4
          content = '' #actural tag such as literal, emphasis
          btw_txt = '' #in-btw text1
          
          mtag_open = '{{{}&gt;' #{1&gt;
          mtag_close = '&lt;{}}}' # &lt;1}
          
          rtag_open = '&lt;{}&gt;'
          rtag_close = '&lt;/{}&gt;'
          source, target = self.tag_info
          
          #sample source {1&gt;{2&gt;Insert&lt;2}&lt;1} to scroll up
          
          #{0: {'id': '1', 'type': 'literal', 'content': '&lt;literal&gt;'}, 
          # 1: {'id': '2', 'type': 'keycap', 'content': '&lt;keycap&gt;'}}, 
          def replace_tags(tag_set, segment):
               for value_dict in tag_set.values():
                    segment = segment.replace(mtag_open.format(value_dict['id']), rtag_open.format(value_dict['type']))
                    segment = segment.replace(mtag_close.format(value_dict['id']), rtag_close.format(value_dict['type']))
               return segment

          source_segment = replace_tags(source, self.source)
          target_segment = replace_tags(target, self.target)
          return source_segment, target_segment
      
     def has_tag(self) -> bool:
          for item in self.group_list:
               if '<m:tunit-metadata>' in item:
                    return True
          return False

     def get_segment_num(self) -> int:
          seg_num_seg = self.get_tag_element(self.group_list, self.seg_num)
          return int(re.search(self.segment_num_reg, seg_num_seg[0]).group(1)) + 1 ## id starts 0
          