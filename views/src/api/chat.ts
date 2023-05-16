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

export const getfilelist = (knowledge_base_id: any) => {
  return api({
    url: '/local_doc_qa/list_files',
    method: 'get',
    params: { knowledge_base_id },

  })
}
export const bing_search = (search_text: any) => {
  return api({
    url: '/bing_search',
    method: 'get',
    params: { search_text },

  })
}
export const deletefile = (params: any) => {
  return api({
    url: '/local_doc_qa/delete_file',
    method: 'post',
    data: JSON.stringify(params),
  })
}
export const web_url = () => {
  return window.location.origin
}
export const setapi = () => {
  return window.baseApi
}
