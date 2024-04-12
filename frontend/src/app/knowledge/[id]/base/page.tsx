'use client';

import { Button, Table } from 'antd';
import type { TableColumnsType } from 'antd';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import React, { useState } from 'react';
import { Flexbox } from 'react-layout-kit';

// import ModalAddFile from './features/ModalAddFile';
const ModalAddFile = dynamic(() => import('./features/ModalAddFile'));
interface DataType {
  address: string;
  age: number;
  key: React.Key;
  name: string;
}

const data: DataType[] = [];
for (let i = 0; i < 46; i++) {
  data.push({
    address: `London, Park Lane no. ${i}`,
    age: 32,
    index: i,
    key: i,
    name: `Edward King ${i}`,
  });
}

const App: React.FC<{ params }> = ({ params }) => {
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [loading, setLoading] = useState(false);
  const [isShowModal, setModal] = useState(false);
  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    console.log('selectedRowKeys changed:', newSelectedRowKeys);
    setSelectedRowKeys(newSelectedRowKeys);
  };
  const columns: TableColumnsType<DataType> = [
    {
      dataIndex: 'index',
      title: '序号',
    },
    {
      dataIndex: 'name',
      render: (text) => <Link href={`/knowledge/${params.id}/base/2`}>{text}</Link>,
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
  const rowSelection = {
    onChange: onSelectChange,
    selectedRowKeys,
  };
  const hasSelected = selectedRowKeys.length > 0;
  console.log(params);
  return (
    <>
      <Flexbox width={'100%'}>
        <Flexbox direction="horizontal" justify="space-between" style={{ marginBottom: 16 }}>
          <Flexbox direction="horizontal" gap={20}>
            <Button disabled={!hasSelected} loading={loading} type="default">
              下载选中文档
            </Button>
            <Button disabled={!hasSelected} loading={loading} type="default">
              重新添加至向量库
            </Button>
            <Button disabled={!hasSelected} loading={loading} type="default">
              向量库删除
            </Button>
            <Button disabled={!hasSelected} loading={loading} type="default">
              从知识库中删除
            </Button>
          </Flexbox>
          <div>
            <Button loading={loading} onClick={() => setModal(true)} type="primary">
              添加文件
            </Button>
          </div>
        </Flexbox>
        <Table
          columns={columns}
          dataSource={data}
          rowSelection={rowSelection}
          size="middle"
          style={{ width: '100%' }}
        />
      </Flexbox>
      <ModalAddFile open={isShowModal} setModalOpen={setModal} />
    </>
  );
};

export default App;
