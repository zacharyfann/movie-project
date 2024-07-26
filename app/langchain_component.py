# from transformers import AutoTokenizer, AutoModel
# import torch
# from neo4j import GraphDatabase
# import os
#
#
#
#
# class EmbeddingGenerator:
#     def __init__(self, model_name="text-embedding-3-small"):
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#         self.model = AutoModel.from_pretrained(model_name)
#
#     def generate_embedding(self, text):
#         inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
#         with torch.no_grad():
#             outputs = self.model(**inputs)
#         return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
#
#
# class Neo4jHandler:
#     def __init__(self, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD):
#         self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
#
#     def close(self):
#         self.driver.close()
#
#     def create_node_with_embedding(self, label, plot, embedding):
#         with self.driver.session() as session:
#             session.write_transaction(self._create_node, label, plot, embedding)
#
#     @staticmethod
#     def _create_node(tx, label, plot, embedding):
#         query = (
#             f"CREATE (n:{label} {{plot: $plot, embedding: $embedding}})"
#         )
#         tx.run(query, plot=plot, embedding=embedding.tolist())
#
#
# class VectorEmbeddingChain:
#     def __init__(self, embedding_generator, neo4j_handler, label):
#         self.embedding_generator = embedding_generator
#         self.neo4j_handler = neo4j_handler
#         self.label = label
#
#     def run(self, plot):
#         embedding = self.embedding_generator.generate_embedding(plot)
#         self.neo4j_handler.create_node_with_embedding(self.label, plot, embedding)
#
#
# OPENAI_API_KEY = 'sk-svcacct-7sctRz2dR7Xq9N7rieDFT3BlbkFJ2Bc57yICCR8DjBG5gROX'
# NEO4J_URI = 'bolt+s://25692c506ed88008fc9319624a853934'
# NEO4J_DATABASE = 'neo4j'
# NEO4J_USERNAME = 'neo4j'
# NEO4J_PASSWORD = 'sidewalk-guard-statements'
# # Example usage
# neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
# embedding_generator = EmbeddingGenerator()
#
# vector_embedding_chain = VectorEmbeddingChain(embedding_generator, neo4j_handler, "Movie")
#
# plot = "A brave hero fights against evil forces."
# vector_embedding_chain.run(plot)
#
