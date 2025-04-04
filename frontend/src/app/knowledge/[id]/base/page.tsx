'use client';

import {
  DeleteOutlined,
  DownloadOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
  UndoOutlined,
} from '@ant-design/icons';
import { Button, Modal, Spin, Table, message } from 'antd';
import type { TableColumnsType } from 'antd';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';
import { Flexbox } from 'react-layout-kit';

import { useKnowledgeStore } from '@/store/knowledge';
import type { KnowledgeUpdateDocsParams } from '@/types/knowledge';

const ModalAddFile = dynamic(() => import('./features/ModalAddFile'));
interface DataType {
  id: React.Key;
  loader: string;
  name: string;
  source: string;
  splitter: string;
  vector: string;
}

const App: React.FC<{ params: { id: string } }> = ({ params }) => {
  const router = useRouter();
  const [
    filesData,
    useFetchKnowledgeFilesList,
    useFetchKnowledgeDownloadDocs,
    useFetcDelInknowledgeDB,
    useFetcDelInVectorDB,
    useFetcRebuildVectorDB,
    useFetchKnowledgeDel,
    useFetcUpdateDocs,
  ] = useKnowledgeStore((s) => [
    s.filesData,
    s.useFetchKnowledgeFilesList,
    s.useFetchKnowledgeDownloadDocs,
    s.useFetcDelInknowledgeDB,
    s.useFetcDelInVectorDB,
    s.useFetcRebuildVectorDB,
    s.useFetchKnowledgeDel,
    s.useFetcUpdateDocs,
  ]);
  const { isLoading, mutate } = useFetchKnowledgeFilesList(params.id);

  const [downloadLoading, setDownloadLoading] = useState(false);
  const [delDocsLoading, setDelDocsLoading] = useState(false);
  const [delVSLoading, setDelVSLoading] = useState(false);
  const [rebuildVectorDBLoading, setRebuildVectorDBLoading] = useState(false);

  // rebuild progress
  const [rebuildProgress, setRebuildProgress] = useState('0%');
  const data: DataType[] = filesData.map(
    ({ No, file_name, text_splitter, in_folder, in_db }, i) => ({
      id: file_name,
      index: No,
      loader: '',
      name: file_name,
      source: in_folder ? '✔️' : '❌',
      splitter: text_splitter,
      vector: in_db ? '✔️' : '❌',
    }),
  );
  // const data = [
  //   { id: '1', name: 'name1', loader: "loader", splitter: "splitter", source: "source", vector: "vector" },
  //   { id: '2', name: 'name2', loader: "loader", splitter: "splitter", source: "source", vector: "vector" },
  // ];

  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [isShowModal, setModal] = useState(false);
  const [isRebuildVectorDB, setIsRebuildVectorDB] = useState(false);
  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    setSelectedRowKeys(newSelectedRowKeys as string[]);
  };
  const columns: TableColumnsType<DataType> = [
    {
      dataIndex: 'index',
      title: '序号',
    },
    {
      dataIndex: 'name',
      render: (text, rowData) => (
        <Link href={`/knowledge/${params.id}/base/${encodeURIComponent(rowData.name)}`}>
          {text}
        </Link>
      ),
      title: '文档名称',
    },
    // {
    //   dataIndex: 'loader',
    //   title: '文档加载器',
    // },
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
  const hasSelected = selectedRowKeys.length > 0;

  const download = async () => {
    // setDownloadLoading(true);
    console.log('selectedRowKeys', selectedRowKeys);
    selectedRowKeys.forEach((docName) => {
      console.log('docName', docName);
      useFetchKnowledgeDownloadDocs(params.id, docName).catch(() => {
        message.error(`下载 ${docName} 失败`);
      });
    });
    // setDownloadLoading(false);
  };
  const reAddVectorDB = async () => {
    Modal.confirm({
      icon: <ExclamationCircleOutlined />,
      onOk() {
        return new Promise(async (resolve) => {
          const _params: KnowledgeUpdateDocsParams = {
            chunk_overlap: 50,
            chunk_size: 250,
            docs: '',
            file_names: selectedRowKeys.map(decodeURIComponent),
            knowledge_base_name: params.id,
            not_refresh_vs_cache: false,
            override_custom_docs: false,
            to_vector_store: true,
            zh_title_enhance: false,
          };
          await useFetcUpdateDocs(_params).catch(() => {
            message.error(`更新失败`);
          });
          mutate();
          resolve(true);
        });
      },
      title: `确认将所选数据重新添加至向量库吗?`,
    });
  };
  const rebuildVectorDB = async () => {
    Modal.confirm({
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        setRebuildVectorDBLoading(true);
        try {
          useFetcRebuildVectorDB(
            {
              allow_empty_kb: true,
              chunk_overlap: 50,
              chunk_size: 250,
              embed_model: 'text-embedding-v1',
              knowledge_base_name: params.id,
              not_refresh_vs_cache: false,
              vs_type: 'faiss',
              zh_title_enhance: false,
            },
            {
              onFinish: async () => {
                message.success(`重建向量库成功`);
                setRebuildVectorDBLoading(false);
                mutate();
              },
              onMessageHandle: (text) => {
                // console.log('text', text)
                setRebuildProgress(text);
              },
            },
          );
        } catch {
          message.error(`请求错误`);
          setRebuildVectorDBLoading(false);
        }
      },
      title: `确认依据源文件重建 ${params.id} 的向量库吗?`,
    });
  };
  const delInVectorDB = async () => {
    setDelVSLoading(true);
    await useFetcDelInVectorDB({
      delete_content: false,
      file_names: [...selectedRowKeys],
      knowledge_base_name: params.id, // 不删除文件
      not_refresh_vs_cache: false,
    }).catch(() => {
      message.error(`删除失败`);
    });
    setDelVSLoading(false);
    setSelectedRowKeys([]);
    mutate();
  };
  const delInknowledgeDB = async () => {
    setDelDocsLoading(true);
    await useFetcDelInknowledgeDB({
      delete_content: true,
      file_names: [...selectedRowKeys],
      knowledge_base_name: params.id,
      not_refresh_vs_cache: false,
    }).catch(() => {
      message.error(`删除失败`);
    });
    setDelDocsLoading(false);
    setSelectedRowKeys([]);
    mutate();
  };
  const delKnowledge = async () => {
    Modal.confirm({
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        const { code: resCode, msg: resMsg } = await useFetchKnowledgeDel(params.id);
        if (resCode !== 200) {
          message.error(resMsg);
        } else {
          message.success(resMsg);
          router.push('/knowledge');
        }
        return;
      },
      title: `确认删除 ${params.id} 吗?`,
    });
  };
  return (
    <>
      <Flexbox width={'100%'}>
        <Flexbox direction="horizontal" justify="space-between" style={{ marginBottom: 16 }}>
          <Flexbox direction="horizontal" gap={20}>
            <Button
              disabled={!hasSelected}
              icon={<DownloadOutlined />}
              loading={downloadLoading}
              onClick={download}
              type="default"
            >
              下载选中文档
            </Button>
            <Button
              disabled={!hasSelected}
              loading={loading}
              onClick={reAddVectorDB}
              type="default"
            >
              重新添加至向量库
            </Button>
            <Button
              danger
              disabled={!hasSelected}
              icon={<DeleteOutlined />}
              loading={delVSLoading}
              onClick={delInVectorDB}
              type="default"
            >
              向量库删除
            </Button>
            <Button
              danger
              disabled={!hasSelected}
              icon={<DeleteOutlined />}
              loading={delDocsLoading}
              onClick={delInknowledgeDB}
              type="default"
            >
              从知识库中删除
            </Button>
          </Flexbox>
          <Flexbox direction="horizontal" gap={20}>
            <Button
              danger
              icon={<DeleteOutlined />}
              loading={loading}
              onClick={delKnowledge}
              type="primary"
            >
              删除知识库
            </Button>
            <Button
              icon={<PlusOutlined />}
              loading={loading}
              onClick={() => {
                setIsRebuildVectorDB(false);
                setModal(true);
              }}
              type="primary"
            >
              添加文件
            </Button>
          </Flexbox>
        </Flexbox>
        <Spin spinning={rebuildVectorDBLoading} tip={rebuildProgress}>
          <Table
            columns={columns}
            dataSource={data}
            footer={() => (
              <div>
                <Button
                  danger
                  icon={<UndoOutlined />}
                  loading={rebuildVectorDBLoading}
                  onClick={rebuildVectorDB}
                >
                  {rebuildVectorDBLoading ? rebuildProgress : ''} 依据源文件重建向量库
                </Button>
              </div>
            )}
            loading={isLoading}
            rowKey={'name'}
            rowSelection={{
              onChange: onSelectChange,
              selectedRowKeys,
            }}
            size="middle"
            style={{ width: '100%' }}
          />
        </Spin>
      </Flexbox>
      <ModalAddFile
        isRebuildVectorDB={isRebuildVectorDB}
        kbName={params.id}
        open={isShowModal}
        selectedRowKeys={selectedRowKeys}
        setModalOpen={setModal}
        setSelectedRowKeys={setSelectedRowKeys}
      />
    </>
  );
};

export default App;
