import os
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import redis
import json
from datetime import datetime, timedelta
import logging
import re

class SearchEngine:
    def __init__(self, cache_ttl: int = 3600, use_redis: bool = False):
        """Initialize the search engine with embedding model and vector store."""
        # Initialize bi-encoder for semantic search
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize cross-encoder for re-ranking
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        # Initialize ChromaDB for document storage
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Initialize Redis for caching if enabled
        self.use_redis = use_redis
        if use_redis:
            try:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
                self.redis_client.ping()  # Test connection
            except redis.ConnectionError:
                print("Warning: Redis connection failed. Caching will be disabled.")
                self.use_redis = False
        
        self.cache_ttl = cache_ttl
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="parking_documents"
        )
        
    def process_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Process and store documents in the vector database."""
        for doc in documents:
            # Split text into chunks
            chunks = self.text_splitter.split_text(doc['text'])
            
            # Generate embeddings for chunks
            embeddings = self.model.encode(chunks)
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=chunks,
                metadatas=[doc['metadata']] * len(chunks),
                ids=[f"{doc['id']}_{i}" for i in range(len(chunks))]
            )
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using semantic search."""
        # Check cache first if Redis is enabled
        if self.use_redis:
            try:
                cache_key = f"search:{query}"
                cached_results = self.redis_client.get(cache_key)
                if cached_results:
                    return json.loads(cached_results)
            except redis.RedisError:
                print("Warning: Redis cache access failed. Proceeding without cache.")
        
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k * 2  # Get more results for re-ranking
        )
        
        # Process results
        search_results = []
        for i in range(len(results['documents'][0])):
            search_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': results['distances'][0][i]
            })
        
        # Rerank results
        reranked_results = self.rerank_results(search_results, query)
        
        # Cache results if Redis is enabled
        if self.use_redis:
            try:
                self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(reranked_results)
                )
            except redis.RedisError:
                print("Warning: Failed to cache results in Redis.")
        
        return reranked_results[:k]  # Return top k results after re-ranking
    
    def rerank_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rerank search results using cross-encoder."""
        if not results:
            return results
            
        # Prepare pairs for cross-encoder
        pairs = [(query, result['text']) for result in results]
        
        # Get scores from cross-encoder
        scores = self.reranker.predict(pairs)
        
        # Combine scores with original results
        for i, score in enumerate(scores):
            results[i]['rerank_score'] = float(score)
        
        # Sort by rerank score
        results.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return results
    
    def add_document(self, text: str, metadata: Dict[str, Any]) -> None:
        """Add a single document to the vector store."""
        chunks = self.text_splitter.split_text(text)
        embeddings = self.model.encode(chunks)
        
        doc_id = f"doc_{datetime.now().timestamp()}"
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=[metadata] * len(chunks),
            ids=[f"{doc_id}_{i}" for i in range(len(chunks))]
        )
    
    def clear_cache(self) -> None:
        """Clear the Redis cache if enabled."""
        if self.use_redis:
            try:
                self.redis_client.flushdb()
            except redis.RedisError:
                print("Warning: Failed to clear Redis cache.") 