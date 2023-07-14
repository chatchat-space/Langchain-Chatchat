import { api } from './api'

export const chat = (params: any) => {
  return api({
    url: '/chat',
    method: 'post',
    data: JSON.stringify(params),
  })
}

export const chatfile = (params: any) => {
  return api({
    url: '/local_doc_qa/local_doc_chat',
    method: 'post',
    data: JSON.stringify(params),
  })
}

export const getKbsList = () => {
  return api({
    url: '/local_doc_qa/list_knowledge_base',
    method: 'get',

  })
}

export const deleteKb = (knowledge_base_id: any) => {
  return api({
    url: '/local_doc_qa/delete_knowledge_base',
    method: 'delete',
    params: {
      knowledge_base_id,
    },
  })
}

export const getfilelist = (knowledge_base_id: any) => {
  return api({
    url: '/local_doc_qa/list_files',
    method: 'get',
    params: { knowledge_base_id },

  })
}
export const bing_search = (params: any) => {
  return api({
    url: '/local_doc_qa/bing_search_chat',
    method: 'post',
    data: JSON.stringify(params),

  })
}
export const deletefile = (params: any) => {
  return api({
    url: '/local_doc_qa/delete_file',
    method: 'delete',
    params,
  })
}
export const web_url = () => {
  return window.location.origin
}
export const setapi = () => {
  return window.baseApi
}
export const getkblist = (knowledge_base_id: any) => {
  return api({
    url: '/local_doc_qa/list_knowledge_base',
    method: 'get',
    params: {},

  })
}
export const deletekb = (params: any) => {
  return api({
    url: '/local_doc_qa/delete_knowledge_base',
    method: 'post',
    data: JSON.stringify(params),
  })
}
