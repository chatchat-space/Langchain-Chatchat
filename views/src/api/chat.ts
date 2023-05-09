import qs from 'qs'
import { api } from './api'

export const chat = (params: any) => {
  return api({
    url: '/chat-docs/chatno',
    method: 'post',
    data: JSON.stringify(params),
  })
}

export const chatfile = (params: any) => {
  return api({
    url: '/chatfile',
    method: 'post',
    data: qs.stringify(params),
  })
}

export const getfilelist = () => {
  return api({
    url: '/chat-docs/list',
    method: 'get',
    params: {
      knowledge_base_id: '123',
    },

  })
}

export const deletefile = (params: any) => {
  return api({
    url: '/chat-docs/delete',
    method: 'post',
    data: JSON.stringify(params),
  })
}
