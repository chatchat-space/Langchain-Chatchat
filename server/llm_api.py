from fastapi import Body
from configs import logger, log_verbose, LLM_MODEL, HTTPX_DEFAULT_TIMEOUT
from server.utils import BaseResponse, fschat_controller_address, list_llm_models, get_httpx_client



def list_running_models(
    controller_address: str = Body(None, description="Fastchat controller服务器地址", examples=[fschat_controller_address()]),
    placeholder: str = Body(None, description="该参数未使用，占位用"),
) -> BaseResponse:
    '''
    从fastchat controller获取已加载模型列表
    '''
    try:
        controller_address = controller_address or fschat_controller_address()
        with get_httpx_client() as client:
            r = client.post(controller_address + "/list_models")
            return BaseResponse(data=r.json()["models"])
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}',
                        exc_info=e if log_verbose else None)
        return BaseResponse(
            code=500,
            data=[],
            msg=f"failed to get available models from controller: {controller_address}。错误信息是： {e}")


def list_config_models() -> BaseResponse:
    '''
    从本地获取configs中配置的模型列表
    '''
    return BaseResponse(data=list_llm_models())


def stop_llm_model(
    model_name: str = Body(..., description="要停止的LLM模型名称", examples=[LLM_MODEL]),
    controller_address: str = Body(None, description="Fastchat controller服务器地址", examples=[fschat_controller_address()])
) -> BaseResponse:
    '''
    向fastchat controller请求停止某个LLM模型。
    注意：由于Fastchat的实现方式，实际上是把LLM模型所在的model_worker停掉。
    '''
    try:
        controller_address = controller_address or fschat_controller_address()
        with get_httpx_client() as client:
            r = client.post(
                controller_address + "/release_worker",
                json={"model_name": model_name},
            )
            return r.json()
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}',
                        exc_info=e if log_verbose else None)
        return BaseResponse(
            code=500,
            msg=f"failed to stop LLM model {model_name} from controller: {controller_address}。错误信息是： {e}")


def change_llm_model(
    model_name: str = Body(..., description="当前运行模型", examples=[LLM_MODEL]),
    new_model_name: str = Body(..., description="要切换的新模型", examples=[LLM_MODEL]),
    controller_address: str = Body(None, description="Fastchat controller服务器地址", examples=[fschat_controller_address()])
):
    '''
    向fastchat controller请求切换LLM模型。
    '''
    try:
        controller_address = controller_address or fschat_controller_address()
        with get_httpx_client() as client:
            r = client.post(
                controller_address + "/release_worker",
                json={"model_name": model_name, "new_model_name": new_model_name},
                timeout=HTTPX_DEFAULT_TIMEOUT, # wait for new worker_model
            )
            return r.json()
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}',
                        exc_info=e if log_verbose else None)
        return BaseResponse(
            code=500,
            msg=f"failed to switch LLM model from controller: {controller_address}。错误信息是： {e}")
