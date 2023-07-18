from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generator
import traceback
from collections import deque
from queue import Queue
from threading import Thread
from langchain.callbacks.manager import CallbackManagerForChainRun
from models.loader import LoaderCheckPoint
from pydantic import BaseModel
import torch
import transformers


class ListenerToken:
    """
    观测结果
    """

    input_ids: torch.LongTensor
    _scores: torch.FloatTensor

    def __init__(self, input_ids: torch.LongTensor, _scores: torch.FloatTensor):
        self.input_ids = input_ids
        self._scores = _scores


class AnswerResult(BaseModel):
    """
    消息实体
    """
    history: List[List[str]] = []
    llm_output: Optional[dict] = None


class AnswerResultStream:
    def __init__(self, callback_func=None):
        self.callback_func = callback_func

    def __call__(self, answerResult: AnswerResult):
        if self.callback_func is not None:
            self.callback_func(answerResult)


class AnswerResultQueueSentinelTokenListenerQueue(transformers.StoppingCriteria):
    """
     定义模型stopping_criteria 监听者，在每次响应时将队列数据同步到AnswerResult
     实现此监听器的目的是，不同模型的预测输出可能不是矢量信息，hf框架可以自定义transformers.StoppingCriteria入参来接收每次预测的Tensor和损失函数，
     通过给 StoppingCriteriaList指定模型生成答案时停止的条件。每个 StoppingCriteria 对象表示一个停止条件
     当每轮预测任务开始时，StoppingCriteria都会收到相同的预测结果，最终由下层实现类确认是否结束
     输出值可用于 generatorAnswer generate_with_streaming的自定义参数观测，以实现更加精细的控制
    """

    listenerQueue: deque = deque(maxlen=1)

    def __init__(self):
        transformers.StoppingCriteria.__init__(self)

    def __call__(self, input_ids: torch.LongTensor, _scores: torch.FloatTensor, **kwargs) -> bool:
        """
        每次响应时将数据添加到响应队列
        :param input_ids:
        :param _scores:
        :param kwargs:
        :return:
        """
        self.listenerQueue.append(ListenerToken(input_ids=input_ids, _scores=_scores))
        return False


class Iteratorize:
    """
    Transforms a function that takes a callback
    into a lazy iterator (generator).
    """

    def __init__(self, func, kwargs={}):
        self.mfunc = func
        self.q = Queue()
        self.sentinel = object()
        self.kwargs = kwargs
        self.stop_now = False

        def _callback(val):
            """
            模型输出预测结果收集
            通过定义generate_with_callback收集器AnswerResultStream，收集模型预测的AnswerResult响应结果，最终由下层实现类确认是否结束
            结束条件包含如下
                1、模型预测结束、收集器self.q队列收到 self.sentinel标识
                2、在处理迭代器队列消息时返回了break跳出迭代器，触发了StopIteration事件
                3、模型预测出错
            因为当前类是迭代器，所以在for in 中执行了break后 __exit__ 方法会被调用，最终stop_now属性会被更新，然后抛出异常结束预测行为
            迭代器收集的行为如下
                创建Iteratorize迭代对象，
                定义generate_with_callback收集器AnswerResultStream
                启动一个线程异步预测结果来调用上游checkpoint的实现方法_generate_answer
                _generate_answer通过generate_with_callback定义的收集器，收集上游checkpoint包装的AnswerResult消息体
                由于self.q是阻塞模式，每次预测后会被消费后才会执行下次预测
                这时generate_with_callback会被阻塞
                主线程Iteratorize对象的__next__方法调用获取阻塞消息并消费
                    1、消息为上游checkpoint包装的AnswerResult消息体，返回下游处理
                    2、消息为self.sentinel标识，抛出StopIteration异常
                主线程Iteratorize对象__exit__收到消息，最终stop_now属性会被更新
                异步线程检测stop_now属性被更新，抛出异常结束预测行为
            迭代行为结束
            :param val:
            :return:
            """
            if self.stop_now:
                raise ValueError
            self.q.put(val)

        def gen():
            try:
                ret = self.mfunc(callback=_callback, **self.kwargs)
            except ValueError:
                pass
            except:
                traceback.print_exc()
                pass

            self.q.put(self.sentinel)

        self.thread = Thread(target=gen)
        self.thread.start()

    def __iter__(self):
        return self

    def __next__(self):
        obj = self.q.get(True, None)
        if obj is self.sentinel:
            raise StopIteration
        else:
            return obj

    def __del__(self):
        """
        暂无实现
        :return:
        """
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ break 后会执行 """
        self.stop_now = True


class BaseAnswer(ABC):
    """上层业务包装器.用于结果生成统一api调用"""

    @property
    @abstractmethod
    def _check_point(self) -> LoaderCheckPoint:
        """Return _check_point of llm."""
    def generatorAnswer(self,
                        inputs: Dict[str, Any],
                        run_manager: Optional[CallbackManagerForChainRun] = None,) -> Generator[Any, str, bool]:
        def generate_with_callback(callback=None, **kwargs):
            kwargs['generate_with_callback'] = AnswerResultStream(callback_func=callback)
            self._generate_answer(**kwargs)

        def generate_with_streaming(**kwargs):
            return Iteratorize(generate_with_callback, kwargs)

        with generate_with_streaming(inputs=inputs, run_manager=run_manager) as generator:
            for answerResult in generator:
                yield answerResult

    @abstractmethod
    def _generate_answer(self,
                         inputs: Dict[str, Any],
                         run_manager: Optional[CallbackManagerForChainRun] = None,
                         generate_with_callback: AnswerResultStream = None) -> None:
        pass
