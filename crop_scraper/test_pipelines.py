from itemadapter import ItemAdapter
import json


class TestPipeline:
    def process_item(self, item, spider):
        return item


class JsonOnlyPipeline:
    def open_spider(self, spider):
        self.file = open('test_output.json', 'w', encoding='utf-8')
        self.items = []
    
    def close_spider(self, spider):
        json.dump(self.items, self.file, indent=2, ensure_ascii=False)
        self.file.close()
    
    def process_item(self, item, spider):
        self.items.append(ItemAdapter(item).asdict())
        return item
