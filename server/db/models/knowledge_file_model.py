from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, func

from server.db.base import Base


class KnowledgeFileModel(Base):
    """
    知识文件模型
    """
    __tablename__ = 'knowledge_file'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='知识文件ID')
    file_name = Column(String(255), comment='文件名')
    file_ext = Column(String(10), comment='文件扩展名')
    kb_name = Column(String(50), comment='所属知识库名称')
    document_loader_name = Column(String(50), comment='文档加载器名称')
    text_splitter_name = Column(String(50), comment='文本分割器名称')
    file_version = Column(Integer, default=1, comment='文件版本')
    file_mtime = Column(Float, default=0.0, comment="文件修改时间")
    file_size = Column(Integer, default=0, comment="文件大小")
    custom_docs = Column(Boolean, default=False, comment="是否自定义docs")
    docs_count = Column(Integer, default=0, comment="切分文档数量")
    create_time = Column(DateTime, default=func.now(), comment='创建时间')

    def __repr__(self):
        return f"<KnowledgeFile(id='{self.id}', file_name='{self.file_name}', file_ext='{self.file_ext}', kb_name='{self.kb_name}', document_loader_name='{self.document_loader_name}', text_splitter_name='{self.text_splitter_name}', file_version='{self.file_version}', create_time='{self.create_time}')>"
