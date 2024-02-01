from transformers import pipeline
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from fastapi.responses import JSONResponse
from fastapi import Body, Request

model_path = '/home/ubuntu/bertTrain/truth_testoutput/checkpoint-600'

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path,num_labels=2)
classifier = pipeline('text-classification',model=model, tokenizer=tokenizer)

label_dict = {
  "LABEL_0": "事实",
  "LABEL_1": "观点"
}

def bert_truth_judge(query: str = Body(..., examples=["samples"])):
  print("query=",query)
  ret = {
    "answer": ""
  }
  res = classifier(query)
  final_res = label_dict[res[0]["label"]]
  print(final_res)
  ret["answer"]=final_res
  return JSONResponse(ret)
