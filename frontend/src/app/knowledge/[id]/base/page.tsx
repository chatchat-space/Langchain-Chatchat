'use client';

import { Button, Table } from 'antd';
import type { TableColumnsType } from 'antd';
import React, { useState } from 'react';
import { Flexbox } from 'react-layout-kit';

import ModalAddFile from './features/ModalAddFile';

interface DataType {
  address: string;
  age: number;
  key: React.Key;
  name: string;
}

const columns: TableColumnsType<DataType> = [
  {
    dataIndex: 'index',
    title: '序号',
  },
  {
    dataIndex: 'name',
    title: '文档名称',
  },
  {
    dataIndex: 'loader',
    title: '文档加载器',
  },
  {
    dataIndex: 'loader',
    title: '文档加载器',
  },
  {
    dataIndex: 'splitter',
    title: '分词器',
  },
  {
    dataIndex: 'source',
    title: '源文件',
  },
  {
    dataIndex: 'vector',
    title: '向量库',
  },
];

const data: DataType[] = [];
for (let i = 0; i < 46; i++) {
  data.push({
    address: `London, Park Lane no. ${i}`,
    age: 32,
    key: i,
    name: `Edward King ${i}`,
  });
}

const App: React.FC = () => {
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [loading, setLoading] = useState(false);

  const start = () => {
    setLoading(true);
    // ajax request after empty completing
    setTimeout(() => {
      setSelectedRowKeys([]);
      setLoading(false);
    }, 1000);
  };

  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    console.log('selectedRowKeys changed:', newSelectedRowKeys);
    setSelectedRowKeys(newSelectedRowKeys);
  };

  const rowSelection = {
    onChange: onSelectChange,
    selectedRowKeys,
  };
  const hasSelected = selectedRowKeys.length > 0;

  return (
    <>
      <Flexbox width={'100%'}>
        <Flexbox direction="horizontal" justify="space-between" style={{ marginBottom: 16 }}>
          <Flexbox direction="horizontal" gap={20}>
            <Button disabled={!hasSelected} loading={loading} onClick={start} type="default">
              下载选中文档
            </Button>
            <Button disabled={!hasSelected} loading={loading} onClick={start} type="default">
              重新添加至向量库
            </Button>
            <Button disabled={!hasSelected} loading={loading} onClick={start} type="default">
              向量库删除
            </Button>
            <Button disabled={!hasSelected} loading={loading} onClick={start} type="default">
              从知识库中删除
            </Button>
            <span style={{ marginLeft: 8 }}>
              {hasSelected ? `Selected ${selectedRowKeys.length} items` : ''}
            </span>
          </Flexbox>
          <div>
            <Button loading={loading} onClick={start} type="primary">
              添加文件
            </Button>
          </div>
        </Flexbox>
        <Table
          columns={columns}
          dataSource={data}
          rowSelection={rowSelection}
          style={{ width: '100%' }}
        />
      </Flexbox>
      <ModalAddFile />
    </>
  );
};

export default App;
