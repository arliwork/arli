#!/usr/bin/env python3
"""
ARLI Semantic Memory System - Phase A3
Vector-based semantic search for episodes using FAISS
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np

# Try to import FAISS, fallback to simple similarity
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[SemanticMemory] FAISS not available, using numpy fallback")


@dataclass
class Embedding:
    """Text embedding with metadata"""
    text: str
    vector: np.ndarray
    episode_id: str
    embedding_type: str  # 'task', 'lesson', 'action', 'full_context'


class SimpleEmbedder:
    """
    Fallback embedder using simple techniques
    In production, use OpenAI, sentence-transformers, or local model
    """
    
    def __init__(self, dim: int = 384):
        self.dim = dim
        # Simple word-based hashing for demo
        # In production: use sentence-transformers or OpenAI embeddings
    
    def embed(self, text: str) -> np.ndarray:
        """
        Create simple embedding from text
        Uses word frequency hashing
        """
        words = text.lower().split()
        vector = np.zeros(self.dim)
        
        for word in words:
            # Hash word to position
            hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
            pos = hash_val % self.dim
            # TF-like weighting
            vector[pos] += 1.0
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector.astype(np.float32)


class SemanticMemoryStore:
    """
    Vector-based semantic memory for episodes
    Uses FAISS for fast similarity search
    """
    
    def __init__(self, agent_id: str, base_path: str = ".arli/memory", embedding_dim: int = 384):
        self.agent_id = agent_id
        self.base_path = Path(base_path)
        self.embedding_dim = embedding_dim
        
        # Paths
        self.embeddings_path = self.base_path / "embeddings" / f"{agent_id}_embeddings.npy"
        self.metadata_path = self.base_path / "embeddings" / f"{agent_id}_metadata.jsonl"
        self.index_path = self.base_path / "embeddings" / f"{agent_id}_faiss.index"
        
        # Ensure directories
        self.embeddings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Embedder
        self.embedder = SimpleEmbedder(dim=embedding_dim)
        
        # FAISS index
        self.index = None
        self.metadata: List[Dict] = []
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new"""
        if FAISS_AVAILABLE and self.index_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                print(f"[SemanticMemory] Loaded FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                print(f"[SemanticMemory] Failed to load index: {e}")
                self.index = None
        
        if self.index is None:
            if FAISS_AVAILABLE:
                # Create FAISS index (L2 normalized for cosine similarity)
                self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product = cosine for normalized
                print(f"[SemanticMemory] Created new FAISS index")
            else:
                self.index = None
        
        # Load metadata
        if self.metadata_path.exists():
            self._load_metadata()
    
    def _load_metadata(self):
        """Load embedding metadata"""
        self.metadata = []
        with open(self.metadata_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        self.metadata.append(json.loads(line))
                    except:
                        pass
    
    def _save_metadata(self):
        """Save embedding metadata"""
        with open(self.metadata_path, 'w') as f:
            for meta in self.metadata:
                f.write(json.dumps(meta, ensure_ascii=False) + '\n')
    
    def _save_index(self):
        """Save FAISS index"""
        if FAISS_AVAILABLE and self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
    
    def add_episode(self, episode: Dict) -> bool:
        """
        Add episode to semantic memory
        Creates multiple embeddings: task, lessons, full context
        """
        try:
            episode_id = episode.get('episode_id', '')
            
            # Create multiple embeddings for different aspects
            embeddings_to_add = []
            
            # 1. Task embedding
            task = episode.get('task', '')
            if task:
                embeddings_to_add.append({
                    'text': task,
                    'type': 'task',
                    'episode_id': episode_id
                })
            
            # 2. Lessons embeddings
            for i, lesson in enumerate(episode.get('lessons_learned', [])):
                embeddings_to_add.append({
                    'text': lesson,
                    'type': f'lesson_{i}',
                    'episode_id': episode_id
                })
            
            # 3. Full context embedding
            context = f"{task} {' '.join(episode.get('lessons_learned', []))}"
            if context.strip():
                embeddings_to_add.append({
                    'text': context,
                    'type': 'full_context',
                    'episode_id': episode_id
                })
            
            # Add each embedding
            for emb_data in embeddings_to_add:
                vector = self.embedder.embed(emb_data['text'])
                
                # Add to FAISS
                if FAISS_AVAILABLE and self.index is not None:
                    self.index.add(vector.reshape(1, -1))
                
                # Add metadata
                self.metadata.append({
                    'episode_id': episode_id,
                    'text': emb_data['text'],
                    'type': emb_data['type'],
                    'index': len(self.metadata),
                    'timestamp': episode.get('timestamp', ''),
                    'result': episode.get('result', '')
                })
            
            # Save
            self._save_metadata()
            self._save_index()
            
            return True
            
        except Exception as e:
            print(f"[SemanticMemory] Error adding episode: {e}")
            return False
    
    def search(self, query: str, k: int = 5, result_filter: Optional[str] = None) -> List[Dict]:
        """
        Semantic search over episodes
        Returns k most similar episodes
        """
        if not self.metadata:
            return []
        
        # Embed query
        query_vector = self.embedder.embed(query)
        
        # Search
        if FAISS_AVAILABLE and self.index is not None:
            distances, indices = self.index.search(query_vector.reshape(1, -1), min(k * 2, len(self.metadata)))
            
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                
                meta = self.metadata[idx]
                
                # Filter by result type if specified
                if result_filter and meta.get('result') != result_filter:
                    continue
                
                results.append({
                    'episode_id': meta['episode_id'],
                    'text': meta['text'],
                    'type': meta['type'],
                    'similarity': float(distance),
                    'result': meta.get('result', ''),
                    'timestamp': meta.get('timestamp', '')
                })
                
                if len(results) >= k:
                    break
            
            return results
        else:
            # Fallback: brute force with numpy
            return self._fallback_search(query_vector, k, result_filter)
    
    def _fallback_search(self, query_vector: np.ndarray, k: int, result_filter: Optional[str]) -> List[Dict]:
        """Fallback search without FAISS"""
        # Load all embeddings
        scores = []
        
        for i, meta in enumerate(self.metadata):
            # Skip if filter doesn't match
            if result_filter and meta.get('result') != result_filter:
                continue
            
            # Simple text similarity (Jaccard)
            text_words = set(meta['text'].lower().split())
            query_words = set(self.embedder.embed.cache if hasattr(self.embedder.embed, 'cache') else [])
            
            if not text_words:
                continue
            
            # Re-embed for comparison
            text_vector = self.embedder.embed(meta['text'])
            similarity = np.dot(query_vector, text_vector)
            
            scores.append((similarity, i, meta))
        
        # Sort by similarity
        scores.sort(reverse=True)
        
        results = []
        for score, idx, meta in scores[:k]:
            results.append({
                'episode_id': meta['episode_id'],
                'text': meta['text'],
                'type': meta['type'],
                'similarity': float(score),
                'result': meta.get('result', ''),
                'timestamp': meta.get('timestamp', '')
            })
        
        return results
    
    def get_similar_lessons(self, task: str, k: int = 3) -> List[str]:
        """Get semantically similar lessons"""
        results = self.search(task, k=k, result_filter='success')
        
        # Filter to lessons only
        lessons = [r for r in results if 'lesson' in r['type']]
        
        return [l['text'] for l in lessons[:k]]
    
    def get_contextual_memory(self, task: str, current_files: List[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive contextual memory for a task
        Combines semantic search with metadata
        """
        context = {
            'similar_tasks': [],
            'relevant_lessons': [],
            'related_failures': [],
            'suggested_workflows': []
        }
        
        # Search for similar tasks
        task_results = self.search(task, k=5)
        
        # Group by episode
        episodes = {}
        for r in task_results:
            ep_id = r['episode_id']
            if ep_id not in episodes:
                episodes[ep_id] = {
                    'similarity': r['similarity'],
                    'result': r['result'],
                    'texts': []
                }
            episodes[ep_id]['texts'].append(r['text'])
        
        # Build context
        for ep_id, data in episodes.items():
            if data['result'] == 'success':
                context['similar_tasks'].append({
                    'episode_id': ep_id,
                    'similarity': data['similarity'],
                    'description': data['texts'][0] if data['texts'] else ''
                })
            else:
                context['related_failures'].append({
                    'episode_id': ep_id,
                    'similarity': data['similarity'],
                    'lesson': data['texts'][0] if data['texts'] else ''
                })
        
        # Get lessons
        context['relevant_lessons'] = self.get_similar_lessons(task, k=5)
        
        # Suggest workflows if we have patterns
        if len(context['similar_tasks']) >= 2:
            context['suggested_workflows'].append(
                "Based on similar successful tasks: Start with research, then implement, then test"
            )
        
        return context
    
    def get_stats(self) -> Dict:
        """Get semantic memory statistics"""
        return {
            'total_embeddings': len(self.metadata),
            'unique_episodes': len(set(m['episode_id'] for m in self.metadata)),
            'embedding_types': list(set(m['type'] for m in self.metadata)),
            'faiss_available': FAISS_AVAILABLE,
            'index_size': self.index.ntotal if FAISS_AVAILABLE and self.index else len(self.metadata)
        }


# Integration with AgentMemory
class SemanticMemoryMixin:
    """
    Mixin to add semantic memory to AgentMemory
    """
    
    def init_semantic_memory(self, agent_id: str, workspace: str = "."):
        """Initialize semantic memory"""
        self.semantic = SemanticMemoryStore(
            agent_id,
            base_path=str(Path(workspace) / ".arli" / "memory")
        )
    
    def add_episode_semantic(self, episode: Dict):
        """Add episode to semantic memory"""
        if hasattr(self, 'semantic'):
            self.semantic.add_episode(episode)
    
    def semantic_search(self, query: str, k: int = 5) -> List[Dict]:
        """Search semantic memory"""
        if hasattr(self, 'semantic'):
            return self.semantic.search(query, k=k)
        return []
    
    def get_semantic_context(self, task: str) -> Dict[str, Any]:
        """Get context using semantic search"""
        if hasattr(self, 'semantic'):
            return self.semantic.get_contextual_memory(task)
        return {}


# Example usage
if __name__ == "__main__":
    print("🧠 ARLI Semantic Memory System Test")
    print("=" * 60)
    
    # Create semantic store
    store = SemanticMemoryStore("test-agent")
    
    # Add some episodes
    episodes = [
        {
            'episode_id': 'ep1',
            'task': 'Build JWT authentication endpoint',
            'lessons_learned': ['Always add token expiration', 'Use bcrypt for passwords'],
            'result': 'success',
            'timestamp': '2026-04-09T10:00:00'
        },
        {
            'episode_id': 'ep2',
            'task': 'Create user login API with session management',
            'lessons_learned': ['Session tokens need expiry', 'Validate all inputs'],
            'result': 'success',
            'timestamp': '2026-04-09T11:00:00'
        },
        {
            'episode_id': 'ep3',
            'task': 'Implement password reset flow',
            'lessons_learned': ['Send emails asynchronously', 'Rate limit reset requests'],
            'result': 'failure',
            'timestamp': '2026-04-09T12:00:00'
        }
    ]
    
    print("\n1. Adding episodes to semantic memory...")
    for ep in episodes:
        store.add_episode(ep)
        print(f"   ✅ Added: {ep['task'][:40]}...")
    
    print("\n2. Semantic search...")
    results = store.search("authentication with tokens", k=3)
    print(f"   Found {len(results)} similar items:")
    for r in results:
        print(f"      • [{r['similarity']:.3f}] {r['text'][:50]}...")
    
    print("\n3. Similar lessons for auth task...")
    lessons = store.get_similar_lessons("Build login system", k=3)
    for lesson in lessons:
        print(f"   💡 {lesson}")
    
    print("\n4. Contextual memory...")
    context = store.get_contextual_memory("Create secure auth API")
    print(f"   Similar tasks: {len(context['similar_tasks'])}")
    print(f"   Relevant lessons: {len(context['relevant_lessons'])}")
    print(f"   Related failures: {len(context['related_failures'])}")
    
    print("\n5. Stats:")
    stats = store.get_stats()
    print(f"   Total embeddings: {stats['total_embeddings']}")
    print(f"   Unique episodes: {stats['unique_episodes']}")
    print(f"   FAISS available: {stats['faiss_available']}")
    
    print("\n✅ Semantic Memory tests complete!")
