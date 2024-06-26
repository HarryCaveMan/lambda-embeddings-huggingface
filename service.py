from transformers import AutoTokenizer, AutoModel
from onnxruntime import InferenceSession, SessionOptions, ExecutionMode, GraphOptimizationLevel
import torch
import torch.nn.functional as F
from os import environ as env
from os import sched_getaffinity as ls_cpu
from typing import List,Dict,Union,Any
from json import loads as from_json
from json import dumps as to_json

LAMBDA_TASK_ROOT=env.get("LAMBDA_TASK_ROOT")
MODEL_NAME=env.get("MODEL_NAME")
MODEL_PATH=f"{LAMBDA_TASK_ROOT}/{MODEL_NAME}"
env["OMP_NUM_THREADS"] = str(len(ls_cpu(0)))
env["OMP_WAIT_POLICY"] = 'ACTIVE'

print(f"{len(ls_cpu(0))} CPUs available for OpenMP")

class Singleton(type):
    _instance = None
    def __call__(cls,*args,**kwargs):
        if not cls._instance:
            cls._instance = super(Singleton,cls).__call__(*args,**kwargs)
        return cls._instance

class EncoderService(metaclass=Singleton):
    def __init__(self,model_path: str) -> None:
        opts = SessionOptions()
        opts.graph_optimization_level = GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.execution_mode = ExecutionMode.ORT_PARALLEL
        opts.intra_op_num_threads = int(env["OMP_NUM_THREADS"])
        opts.inter_op_num_threads = int(env["OMP_NUM_THREADS"])
        self.onnx = InferenceSession(f"{model_path}/model_onnx.bin", providers=["CPUExecutionProvider"],sess_options=opts)
        # self.model = AutoModel.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
    #Mean Pooling and normalization - Take attention mask into account for correct averaging
    def get_normalized_sentence_embeddings(self,token_embeddings,attention_mask):
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1),min=1e-9)
        return F.normalize(embeddings, p=2, dim=1).tolist()
    #Get embedding vectors for list of sentences
    def encode(self,sentences:List[str]) -> List[float]:
        encoded_input = self.tokenizer(sentences,padding=True,truncation=True,return_tensors="pt")
        onnx_input = {k: v.cpu().detach().numpy() for k, v in encoded_input.items()}
        # Compute token embeddings
        # with torch.no_grad():
        #     token_embeddings = self.model(**encoded_input)[0]
        token_embeddings = torch.from_numpy(self.onnx.run(None,onnx_input)[0])
        # call pooling/norm method and return the normalized sentence embeddings
        return self.get_normalized_sentence_embeddings(token_embeddings,encoded_input["attention_mask"])

def handler(event: Dict[str,Any],context: Any) -> Dict[str,Union[str,int]]:
    req_json: Dict[str,Union[int,List[str]]] = from_json(event["body"])
    crid: int = req_json["crid"]
    print(f"Received request, crid: {crid}")
    service: EncoderService = EncoderService(MODEL_PATH)
    sentences: List[str] = req_json["sentences"]
    response_json: Dict[str,Union[str,List[float]]] = {
        "crid":crid,
        "sentence_embeddings":service.encode(sentences)
    }
    print(f"Request {crid} complete")
    return {
        "headers":{"Content-type":"application/json"},
        "statusCode":200,
        "body":to_json(response_json)
    }