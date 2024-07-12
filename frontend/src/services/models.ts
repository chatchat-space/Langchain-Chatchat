import { getMessageError } from "@/utils/fetch";
import { API_ENDPOINTS } from "./_url";
import { createHeaderWithAuth } from "./_auth";
import { ModelsResponse } from "@/types/models";
import { GlobalLLMProviderKey } from "@/types/settings/modelProvider";


class ModelsServer{
  getModels = async (provider: GlobalLLMProviderKey): Promise<ModelsResponse> => {
    const headers = await createHeaderWithAuth({ provider, headers: { 'Content-Type': 'application/json' } });

    try {
      const res = await fetch(API_ENDPOINTS.models(provider), {
        headers,
      });

      if (!res.ok) {
        throw await getMessageError(res);
      }

      return res.json();
    } catch (error) {
      return {  error: JSON.stringify(error) };
    }
  }
}

export const modelsServer = new ModelsServer();