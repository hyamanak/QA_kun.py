import re
class TagProcessor():
     s_tag_info_open = '<m:tunit-metadata>'
     t_tag_info_open = '<m:tunit-target-metadata>'
     s_tag_info_close = '</m:tunit-metadata>'
     t_tag_info_close = '</m:tunit-target-metadata>'
     id_regex = 'id=\"(.*?)\"'
     m_type_regex = '<m:type>(.*?)</m:type>'
     m_content_regex = '<m:content>(.*?)</m:content>'
     
     def __init__(self, source, target, group_list):
          self.source = source
          self.target = target
          self.group_list = group_list
          
          self.tag_info = self.get_tag_info()
          
          #guilabel

          #し､し
          #括弧開始､閉じ
     ##return {source:
     ##     {id:[type, content]}, {id:[type, content]},
     ##     {target:
     ##          {id:[type, content]}, {id:[type, content]}}...}
     
     
     def get_element(self, seg_group):
          counter = 0
          c = 0
          tag_element = {}
          temp_dict = {}
          
          for item in seg_group:
               if '<m:mark id' in item:
                    counter += 1
                    
          while (c < counter):
               for item in seg_group:
                    if '<m:mark id' in item:
                         temp_dict['id'] = re.search(self.id_regex, item).group(1)
                    
                    if '<m:type>' in item:
                         temp_dict['type'] = re.search(self.m_type_regex, item).group(1)
                    
                    if '<m:content>' in item:
                         temp_dict['content'] = re.search(self.m_content_regex, item).group(1)
                         tag_element[c] = temp_dict
                         temp_dict = {}
                         c += 1       
          return tag_element
     
     def get_tag_group(self, open_tag, close_tag):
          storing = False # 
          tag_group = []
          for item in self.group_list:
               if open_tag in item:
                    storing = True
                    continue
                    
               if close_tag in item:
                    storing = False
               
               if storing and item != '</m:mark>':
                    tag_group.append(item)
          return tag_group
                    
     def get_tag_info(self) -> tuple:
          source_group = self.get_tag_group(self.s_tag_info_open, self.s_tag_info_close)
          target_group = self.get_tag_group(self.t_tag_info_open, self.t_tag_info_close)
          
          
          source = self.get_element(source_group)
          target = self.get_element(target_group)
          
          return source, target