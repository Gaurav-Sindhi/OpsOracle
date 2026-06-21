import json
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np

class RAGEngine:
    """RAG-based incident retrieval and analysis"""
    
    def __init__(self):
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.incident_memory = []  # In-memory incident store (replace with Pinecone/OpenSearch in production)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        logger.info("✅ RAG Engine initialized")
    
    def add_incident(self, incident: Dict) -> Dict:
        """Add an incident to the knowledge base"""
        try:
            # Create document from incident
            incident_text = self._format_incident_text(incident)
            
            # Generate embedding
            embedding = self.embeddings_model.encode(incident_text)
            
            # Store incident with embedding
            incident_record = {
                'id': incident.get('id', str(datetime.now().timestamp())),
                'incident': incident,
                'text': incident_text,
                'embedding': embedding.tolist(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.incident_memory.append(incident_record)
            
            logger.info(f"✅ Incident added to knowledge base: {incident.get('id')}")
            return {
                'status': 'success',
                'incident_id': incident_record['id']
            }
            
        except Exception as e:
            logger.error(f"❌ Error adding incident: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def search_similar_incidents(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for similar incidents using semantic similarity"""
        try:
            if not self.incident_memory:
                logger.warning("⚠️  No incidents in knowledge base")
                return []
            
            # Generate query embedding
            query_embedding = self.embeddings_model.encode(query)
            
            # Calculate similarity scores
            similarities = []
            for incident_record in self.incident_memory:
                incident_embedding = np.array(incident_record['embedding'])
                similarity = np.dot(query_embedding, incident_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(incident_embedding) + 1e-10
                )
                similarities.append({
                    'incident': incident_record['incident'],
                    'similarity_score': float(similarity),
                    'text': incident_record['text']
                })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Return top-k
            results = similarities[:top_k]
            logger.info(f"🔍 Found {len(results)} similar incidents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching incidents: {str(e)}")
            return []
    
    def _format_incident_text(self, incident: Dict) -> str:
        """Format incident for storage and embedding"""
        parts = [
            f"Incident ID: {incident.get('id', 'unknown')}",
            f"Error Type: {incident.get('error_type', 'unknown')}",
            f"Root Cause: {incident.get('root_cause', 'unknown')}",
            f"Service: {incident.get('service', 'unknown')}",
            f"Affected Services: {', '.join(incident.get('affected_services', []))}",
            f"Duration: {incident.get('duration_minutes', 0)} minutes",
            f"Fix Applied: {incident.get('fix_applied', 'unknown')}",
            f"Log Excerpt: {incident.get('log_excerpt', '')[:200]}"
        ]
        return '\n'.join(parts)
    
    def generate_incident_context(self, error_type: str, current_logs: str) -> str:
        """Generate context for LLM by searching similar incidents"""
        try:
            # Search for similar incidents
            similar = self.search_similar_incidents(current_logs, top_k=3)
            
            if not similar:
                return "No similar historical incidents found."
            
            context_parts = ["Similar incidents from history:\n"]
            
            for idx, result in enumerate(similar, 1):
                incident = result['incident']
                confidence = result['similarity_score']
                
                context_parts.append(f"\n{idx}. Incident from {incident.get('timestamp', 'unknown')} (similarity: {confidence:.2%})")
                context_parts.append(f"   - Root Cause: {incident.get('root_cause', 'N/A')}")
                context_parts.append(f"   - Fix Applied: {incident.get('fix_applied', 'N/A')}")
                context_parts.append(f"   - Resolution Time: {incident.get('duration_minutes', 'N/A')} minutes")
            
            return '\n'.join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Error generating context: {str(e)}")
            return "Could not generate historical context"
    
    def batch_add_incidents(self, incidents: List[Dict]) -> Dict:
        """Add multiple incidents at once"""
        try:
            results = []
            for incident in incidents:
                result = self.add_incident(incident)
                results.append(result)
            
            successful = sum(1 for r in results if r.get('status') == 'success')
            logger.info(f"✅ Added {successful}/{len(incidents)} incidents")
            
            return {
                'status': 'success',
                'total_added': successful,
                'total_incidents': len(self.incident_memory)
            }
            
        except Exception as e:
            logger.error(f"❌ Error batch adding incidents: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def get_knowledge_base_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        try:
            error_types = {}
            services = {}
            
            for record in self.incident_memory:
                incident = record['incident']
                error_type = incident.get('error_type', 'unknown')
                service = incident.get('service', 'unknown')
                
                error_types[error_type] = error_types.get(error_type, 0) + 1
                services[service] = services.get(service, 0) + 1
            
            return {
                'total_incidents': len(self.incident_memory),
                'error_types': error_types,
                'services': services,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {str(e)}")
            return {'error': str(e)}

# Singleton instance
rag_engine = RAGEngine()