from InstructorEmbedding import INSTRUCTOR
model = INSTRUCTOR('yinghy2018/CoRTEx')
term = "fever"
term_definition = "xxxx"
instruction = "Represent the biomedical term for identifying synonymous terms. Input: "
instruction2 = "Represent the meaning of the biomedical term for retrieval. Input: "
embeddings = model.encode([[instruction,term]])
embeddings = model.encode([[instruction2,term_definition]])
print(embeddings)





# run the code below, or you can go to the original file to change the codes.
from generate_faiss_index import get_instructor_embed
import torch
model= torch.load(ori_Instructor_path).to(device)

phrase_list = []

# Here the "phrase_list" is a python list containing the terms you want to encode.
get_instructor_embed(phrase_list, model, batch_size=128)