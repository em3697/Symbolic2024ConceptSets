from InstructorEmbedding import INSTRUCTOR
model = INSTRUCTOR('yinghy2018/CoRTEx')
term = "fever"
term_definition = "xxxx"
instruction = "Represent the biomedical term for identifying synonymous terms. Input: "
instruction2 = "Represent the meaning of the biomedical term for retrieval. Input: "
embeddings = model.encode([[instruction,term]])
embeddings = model.encode([[instruction2,term_definition]])
print(embeddings)

# Load model directly
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("yinghy2018/CoRTEx")
model = AutoModel.from_pretrained("yinghy2018/CoRTEx")