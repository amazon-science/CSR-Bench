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
