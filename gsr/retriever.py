import json
from rank_bm25 import BM25Okapi


class RetrievalEngine:
    def __init__(self, json_path):
        self.data = self.load_data(json_path)
        self.sentences, self.contents = self.prepare_data(self.data)
        self.tokenized_sentences = [sentence.split(" ") for sentence in self.sentences]
        self.bm25 = BM25Okapi(self.tokenized_sentences)

    def load_data(self, json_path):
        with open(json_path, 'r') as file:
            data = json.load(file)
        return data

    def prepare_data(self, data):
        sentences = []
        contents = []
        for entry in data:
            title = entry.get('title', '')
            body = entry.get('body', '')
            comments = [(comment.get('user', {}).get('login', ''), comment.get('body', '')) for comment in entry.get('comments', [])]
            # content = f"{title} {body} {comments}"
            # Merge title, body, and comments into a single string, with ### Title, ### Body, and ### Response [user_login] prefixes
            sentences.append(
                f'**Title**\n{title}\n**Body**\n{body}\n' + '\n'.join([f'**Response** [{user_login}]\n{comment}' for user_login, comment in comments])
            )
            contents.append({'title': title, 'body': body, 'comments': comments})
        return sentences, contents

    def query(self, query_sentence, top_k=3):
        tokenized_query = query_sentence.split(" ")
        # doc_scores = self.bm25.get_scores(tokenized_query)
        top_n_indices = self.bm25.get_top_n(tokenized_query, self.sentences, n=top_k)
        return top_n_indices

# Example usage
if __name__ == "__main__":
    json_path = '/home/yijia/git-bench/assets/contriever.json'
    engine = RetrievalEngine(json_path)
    query_sentence = "Example Query"
    top_k_results = engine.query(query_sentence, top_k=3)
    for result in top_k_results:
        print(f"{result}\n")



# import json
# # from src.contriever import Contriever
# import torch
# from transformers import AutoTokenizer, AutoModel
# import faiss
# import torch


# class RetrievalEngine:
#     def __init__(self, json_path, model_id='facebook/contriever-msmarco'):
#         self.model_id = model_id
#         # self.model = Contriever.from_pretrained(self.model_id)
#         # self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
#         self.model = AutoModel.from_pretrained(self.model_id)
#         self.index = None
#         self.data = self.load_data(json_path)
#         self.sentences, self.contents = self.prepare_data(self.data)
#         self.embeddings = self.get_embeddings(self.sentences)
#         self.build_index(self.embeddings)

#     def load_data(self, json_path):
#         with open(json_path, 'r') as file:
#             data = json.load(file)
#         return data

#     def prepare_data(self, data):
#         sentences = []
#         contents = []
#         for entry in data:
#             title = entry.get('title', '')
#             body = entry.get('body', '')
#             comments_str = '\n### Response\n' + '\n\n### Response\n'.join(comment.get('body', '') for comment in entry.get('comments', []))
#             # comments = [comment.get('body', '') for comment in entry.get('comments', [])]
#             comments = [(comment.get('user', '').get('login', ''), comment.get('body', '')) for comment in entry.get('comments', [])]
#             content = f"{title} {body} {comments}"
#             # sentences.append(content)
#             sentences.append(f"# Title\n{title}\n# Body\n{body}")
#             # contents.append({'title': '### Title\n' + title, 'body': '### Body\n' + body, 'comments': comments})
#             contents.append({'title': title, 'body': body, 'comments': comments})
#             # print(comments_str)

#         return sentences, contents

#     def get_embeddings(self, sentences):
#         inputs = self.tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
#         with torch.no_grad():
#             model_output = self.model(**inputs)
        
#         # return model_output.last_hidden_state.mean(dim=1).numpy()
#         # return model_output.numpy()

#         def mean_pooling(token_embeddings, mask):
#             token_embeddings = token_embeddings.masked_fill(~mask[..., None].bool(), 0.)
#             sentence_embeddings = token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
#             return sentence_embeddings

#         embeddings = mean_pooling(model_output[0], inputs['attention_mask'])
#         return embeddings.numpy()

#     def build_index(self, embeddings):
#         dimension = embeddings.shape[1]
#         self.index = faiss.IndexFlatL2(dimension)
#         self.index.add(embeddings)

#     def query(self, query_sentence, top_k=3):
#         query_embedding = self.get_embeddings([query_sentence])
#         distances, indices = self.index.search(query_embedding, top_k)
#         results = [
#             {
#                 'title': self.contents[idx]['title'],
#                 'body': self.contents[idx]['body'],
#                 'comments': self.contents[idx]['comments'],
#                 'distance': distances[0][i]
#             } 
#             for i, idx in enumerate(indices[0])
#         ]
#         return results


# # Example usage
# if __name__ == "__main__":
#     # json_path = '/home/yijia/git-bench/assets/contriever.json'
#     # engine = RetrievalEngine(json_path)

#     # query_sentence = "Tokenization script removed?"
#     # query_sentence = "Model and Code Sharing."
#     # query_sentence = "Code"
#     # top_k_results = engine.query(query_sentence, top_k=3)

#     # for result in top_k_results:
#     #     print(f"Title: {result['title']}\nBody: {result['body']}\nComments: {result['comments']}\nDistance: {result['distance']}\n")

#     from rank_bm25 import BM25Okapi

#     corpus = [
#         "Hello there good man!",
#         "It is quite windy in London",
#         "How is the weather today?"
#     ]

#     tokenized_corpus = [doc.split(" ") for doc in corpus]

#     bm25 = BM25Okapi(tokenized_corpus)
#     # <rank_bm25.BM25Okapi at 0x1047881d0>

#     query = "windy London"
#     tokenized_query = query.split(" ")

#     doc_scores = bm25.get_scores(tokenized_query)
#     # array([0.        , 0.93729472, 0.        ])
#     print(bm25.get_top_n(tokenized_query, corpus, n=1))











# from src.contriever import Contriever
# from transformers import AutoTokenizer
# import faiss
# import torch

# # Model ID
# MODEL_ID = 'facebook/contriever-msmarco'
# # Initialize the model and tokenizer
# model = Contriever.from_pretrained(MODEL_ID) 
# tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

# # Define your sentences
# sentences = [
#     # "Where was Marie Curie born?",
#     # "Who are you?",
#     "November",
#     "Maria Sklodowska, later known as Marie Curie, was born on November 7, 1867.",
#     "Born in Paris on 15 May 1859, Pierre Curie was the son of Eugène Curie, a doctor of French Catholic origin from Alsace."
# ]

# # Tokenize the sentences
# inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")

# # Get embeddings
# with torch.no_grad():
#     model_output = model(**inputs)

# # The model output is already in the shape (3, 768)
# embeddings = model_output.numpy()

# # Create a FAISS index
# dimension = embeddings.shape[1]
# index = faiss.IndexFlatL2(dimension)

# # Add embeddings to the index
# index.add(embeddings)

# # Query with the first sentence
# query_embedding = embeddings[0].reshape(1, -1)

# # Perform the search
# k = 3  # Number of nearest neighbors
# distances, indices = index.search(query_embedding, k)

# # Print the results
# for i, idx in enumerate(indices[0]):
#     print(f"Sentence: {sentences[idx]}, Distance: {distances[0][i]}")

