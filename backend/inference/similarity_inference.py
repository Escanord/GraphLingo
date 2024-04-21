from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embedding(text):
    if text == []:
        return text
    return model.encode(text, convert_to_tensor=True)

def cosine_score(embedding1, embedding2):
    cosine_scores = util.pytorch_cos_sim(embedding1, embedding2)
    
    return cosine_scores.item()

def similarity_score(text1, text2):
    embedding1, embedding2 = embedding([text1, text2])

    return cosine_score(embedding1, embedding2)