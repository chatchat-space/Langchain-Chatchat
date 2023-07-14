from langchain.docstore.document import Document
import feedparser
import html2text
import ssl
import time


class RSS_Url_loader:
    def __init__(self, urls=None,interval=60):
        '''可用参数urls数组或者是字符串形式的url列表'''
        self.urls = []
        self.interval = interval
        if urls is not None:
            try:
                if isinstance(urls, str):
                    urls = [urls]
                elif isinstance(urls, list):
                    pass
                else:
                    raise TypeError('urls must be a list or a string.')
                self.urls = urls
            except:
                Warning('urls must be a list or a string.')
    
    #定时代码还要考虑是不是引入其他类，暂时先不对外开放
    def scheduled_execution(self):
        while True:
            docs = self.load()
            return docs
            time.sleep(self.interval)

    def load(self):
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context
        documents = []
        for url in self.urls:
            parsed = feedparser.parse(url)
            for entry in parsed.entries:
                if "content" in entry:
                    data = entry.content[0].value
                else:
                    data = entry.description or entry.summary
                data = html2text.html2text(data)
                metadata = {"title": entry.title, "link": entry.link}
                documents.append(Document(page_content=data, metadata=metadata))
        return documents

if __name__=="__main__":
    #需要在配置文件中加入urls的配置，或者是在用户界面上加入urls的配置
    urls = ["https://www.zhihu.com/rss", "https://www.36kr.com/feed"]
    loader = RSS_Url_loader(urls)
    docs = loader.load()
    for doc in docs:
        print(doc)