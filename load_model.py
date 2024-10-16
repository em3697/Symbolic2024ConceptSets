# Load model directly
import torch
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("yinghy2018/CoRTEx")
model = AutoModel.from_pretrained("yinghy2018/CoRTEx")


from generate_faiss_index import get_instructor_embed
phrase_list = []
model= torch.load(ori_Instructor_path).to(device)
get_instructor_embed(phrase_list, model, batch_size=128)