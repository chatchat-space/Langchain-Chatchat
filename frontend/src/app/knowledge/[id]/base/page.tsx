'use client';

import { Button, Table, message, Spin, Modal } from 'antd';
import type { TableColumnsType } from 'antd';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import React, { useState } from 'react';
import { Flexbox } from 'react-layout-kit';
import { useKnowledgeStore } from '@/store/knowledge';
import { useRouter } from 'next/navigation';
import { UndoOutlined, DeleteOutlined, DownloadOutlined, PlusOutlined, ExclamationCircleOutlined } from '@ant-design/icons';

import type { KnowledgeUpdateDocsParams } from '@/types/knowledge';

const ModalAddFile = dynamic(() => import('./features/ModalAddFile'));
interface DataType {
  id: React.Key;
  name: string;
  loader: string;
  splitter: string;
  source: string;
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
    useFetcUpdateDocs
  ] = useKnowledgeStore((s) => [
    s.filesData,
    s.useFetchKnowledgeFilesList,
    s.useFetchKnowledgeDownloadDocs,
    s.useFetcDelInknowledgeDB,
    s.useFetcDelInVectorDB,
    s.useFetcRebuildVectorDB,
    s.useFetchKnowledgeDel,
    s.useFetcUpdateDocs
  ]);
  const { isLoading, mutate } = useFetchKnowledgeFilesList(params.id);

  const [downloadLoading, setDownloadLoading] = useState(false);
  const [delDocsLoading, setDelDocsLoading] = useState(false);
  const [delVSLoading, setDelVSLoading] = useState(false);
  const [rebuildVectorDBLoading, setRebuildVectorDBLoading] = useState(false);

  // rebuild progress
  const [rebuildProgress, setRebuildProgress] = useState("0%");
  const data: DataType[] = filesData.map(({ No, file_name, text_splitter, in_folder, in_db }, i) => ({
    index: No,
    id: file_name,
    name: file_name,
    loader: "",
    splitter: text_splitter,
    source: in_folder ? "✔️" : "❌",
    vector: in_db ? "✔️" : "❌",
  }));
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
      render: (text, rowData) => <Link href={`/knowledge/${params.id}/base/${encodeURIComponent(rowData.name)}`}>{text}</Link>,
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
    console.log('selectedRowKeys', selectedRowKeys)
    selectedRowKeys.forEach((docName) => {
      console.log('docName', docName)
      useFetchKnowledgeDownloadDocs(params.id, docName).catch(() => {
        message.error(`下载 ${docName} 失败`);
      })
    })
    // setDownloadLoading(false);
  };
  const reAddVectorDB = async () => {
    Modal.confirm({
      title: `确认将所选数据重新添加至向量库吗?`,
      icon: <ExclamationCircleOutlined />,
      onOk() {
        return new Promise(async (resolve) => {
          const _params: KnowledgeUpdateDocsParams = {
            knowledge_base_name: params.id,
            override_custom_docs: false,
            to_vector_store: true,
            zh_title_enhance: false,
            not_refresh_vs_cache: false,
            chunk_size: 250,
            chunk_overlap: 50,
            file_names: selectedRowKeys.map(decodeURIComponent),
            docs: ""
          }
          await useFetcUpdateDocs(_params).catch(() => {
            message.error(`更新失败`);
          })
          mutate();
          resolve(true)
        })
      },
    });

  }
  const rebuildVectorDB = async () => {
    Modal.confirm({
      title: `确认依据源文件重建 ${params.id} 的向量库吗?`,
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        setRebuildVectorDBLoading(true);
        try {
          useFetcRebuildVectorDB({
            "knowledge_base_name": params.id,
            "allow_empty_kb": true,
            "vs_type": "faiss",
            "embed_model": "text-embedding-v1",
            "chunk_size": 250,
            "chunk_overlap": 50,
            "zh_title_enhance": false,
            "not_refresh_vs_cache": false,
          }, {
            onFinish: async () => {
              message.success(`重建向量库成功`);
              setRebuildVectorDBLoading(false);
              mutate();
            },
            onMessageHandle: (text) => {
              // console.log('text', text)
              setRebuildProgress(text)
            }
          })
        } catch (err) {
          message.error(`请求错误`);
          setRebuildVectorDBLoading(false);
        }
      },
    });

  }
  const delInVectorDB = async () => {
    setDelVSLoading(true);
    await useFetcDelInVectorDB({
      "knowledge_base_name": params.id,
      "file_names": [...selectedRowKeys],
      "delete_content": false, // 不删除文件
      "not_refresh_vs_cache": false
    }).catch(() => {
      message.error(`删除失败`);
    })
    setDelVSLoading(false);
    setSelectedRowKeys([]);
    mutate();
  }
  const delInknowledgeDB = async () => {
    setDelDocsLoading(true);
    await useFetcDelInknowledgeDB({
      "knowledge_base_name": params.id,
      "file_names": [...selectedRowKeys],
      "delete_content": true,
      "not_refresh_vs_cache": false
    }).catch(() => {
      message.error(`删除失败`);
    })
    setDelDocsLoading(false);
    setSelectedRowKeys([]);
    mutate();
  }
  const delKnowledge = async () => {
    Modal.confirm({
      title: `确认删除 ${params.id} 吗?`,
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        const { code: resCode, msg: resMsg } = await useFetchKnowledgeDel(params.id)
        if (resCode !== 200) {
          message.error(resMsg)
        } else {
          message.success(resMsg);
          router.push('/knowledge')
        }
        return Promise.resolve();
      },
    });

  }
  return (
    <>
      <Flexbox width={'100%'}>
        <Flexbox direction="horizontal" justify="space-between" style={{ marginBottom: 16 }}>
          <Flexbox direction="horizontal" gap={20}>
            <Button disabled={!hasSelected} loading={downloadLoading} type="default" onClick={download} icon={<DownloadOutlined />}>
              下载选中文档
            </Button>
            <Button disabled={!hasSelected} loading={loading} type="default" onClick={reAddVectorDB}>
              重新添加至向量库
            </Button>
            <Button danger disabled={!hasSelected} loading={delVSLoading} type="default" onClick={delInVectorDB} icon={<DeleteOutlined />}>
              向量库删除
            </Button>
            <Button danger disabled={!hasSelected} loading={delDocsLoading} type="default" onClick={delInknowledgeDB} icon={<DeleteOutlined />}>
              从知识库中删除
            </Button>
          </Flexbox>
          <Flexbox direction="horizontal" gap={20}>
            <Button danger loading={loading} onClick={delKnowledge} type="primary" icon={<DeleteOutlined />}>
              删除知识库
            </Button>
            <Button loading={loading} onClick={() => { setIsRebuildVectorDB(false); setModal(true) }} type="primary" icon={<PlusOutlined />}>
              添加文件
            </Button>
          </Flexbox>
        </Flexbox>
        <Spin spinning={rebuildVectorDBLoading} tip={rebuildProgress}>
          <Table
            columns={columns}
            dataSource={data}
            rowSelection={{
              onChange: onSelectChange,
              selectedRowKeys,
            }}
            size="middle"
            style={{ width: '100%' }}
            rowKey={"name"}
            loading={isLoading}
            footer={() => <div>
              <Button danger loading={rebuildVectorDBLoading} onClick={rebuildVectorDB} icon={<UndoOutlined />}>
                {rebuildVectorDBLoading ? rebuildProgress : ''} 依据源文件重建向量库
              </Button>
            </div>}
          />
        </Spin>
      </Flexbox >
      <ModalAddFile open={isShowModal} setModalOpen={setModal} kbName={params.id} selectedRowKeys={selectedRowKeys} setSelectedRowKeys={setSelectedRowKeys} isRebuildVectorDB={isRebuildVectorDB} />
    </>
  );
};

export default App;
