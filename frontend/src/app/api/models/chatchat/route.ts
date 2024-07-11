import { getServerConfig } from '@/config/server';
import { createErrorResponse } from '@/app/api/errorResponse';
import { LOBE_CHAT_AUTH_HEADER, OAUTH_AUTHORIZED } from '@/const/auth';
import { getJWTPayload } from '../../chat/auth';

export const GET = async (req: Request) => {

  // get Authorization from header
  const authorization = req.headers.get(LOBE_CHAT_AUTH_HEADER);
  
  const { CHATCHAT_PROXY_URL } = getServerConfig();
  
  let baseURL = CHATCHAT_PROXY_URL;

  // 为了方便拿到 endpoint，这里直接解析 JWT
  if (authorization) {
    const jwtPayload = await getJWTPayload(authorization);
    if (jwtPayload.endpoint) {
      baseURL = jwtPayload.endpoint;
    }
  }

  let res: Response;

  try {
    console.log('get models from:', baseURL)

    res = await fetch(`${baseURL}/models`);

    if (!res.ok) {
      // throw new Error(`Failed to fetch models: ${res.status}`);
      return createErrorResponse(500, { error: `Failed to fetch models: ${res.status}` });
    }

    return res;

  } catch (e) {
    return createErrorResponse(500, { error: e });
  }
}