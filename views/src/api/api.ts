import request from './axios'
export const api = async (data: object): Promise<any> => {
  return await request({
    ...data,
  })
}
