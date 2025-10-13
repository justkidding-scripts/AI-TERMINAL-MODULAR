#!/usr/bin/env python3
"""
Test suite for RAG system functionality
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules', 'rag_integration'))

try:
    from rag import RAGSkill, _simple_embed, _read_text
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

@pytest.mark.skipif(not RAG_AVAILABLE, reason="RAG system not available")
class TestRAGSystem:
    """Test RAG system functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test files
        (self.temp_path / "test.txt").write_text("This is a test document about Python programming.")
        (self.temp_path / "code.py").write_text("def hello_world():\n    print('Hello, World!')")
        (self.temp_path / "data.json").write_text('{"name": "test", "value": 42}')
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_simple_embedding(self):
        """Test simple embedding function"""
        text = "This is a test document"
        embedding = _simple_embed(text)
        
        assert embedding is not None
        assert len(embedding) == 256  # Should be 256-dimensional
        assert embedding.dtype.name.startswith('float')
    
    def test_read_text(self):
        """Test text reading functionality"""
        # Test plain text
        txt_content = _read_text(self.temp_path / "test.txt")
        assert "Python programming" in txt_content
        
        # Test Python code
        py_content = _read_text(self.temp_path / "code.py")
        assert "def hello_world" in py_content
        assert "# File:" in py_content  # Should add metadata
        
        # Test JSON
        json_content = _read_text(self.temp_path / "data.json")
        assert '"name": "test"' in json_content
    
    def test_rag_skill_initialization(self):
        """Test RAG skill initialization"""
        rag = RAGSkill()
        assert rag is not None
        assert hasattr(rag, 'handle')
        assert hasattr(rag, 'can_handle')
    
    def test_can_handle(self):
        """Test command recognition"""
        rag = RAGSkill()
        
        # Should handle these commands
        assert rag.can_handle("rag add /path/to/file")
        assert rag.can_handle("rag ask What is Python?")
        assert rag.can_handle("rag status")
        assert rag.can_handle("rag help")
        
        # Should not handle these
        assert not rag.can_handle("ls -la")
        assert not rag.can_handle("python script.py")
        assert not rag.can_handle("random command")
    
    def test_help_command(self):
        """Test help command"""
        rag = RAGSkill()
        help_text = rag.handle("rag help")
        
        assert "RAG System Commands" in help_text
        assert "rag add" in help_text
        assert "rag ask" in help_text
        assert "rag status" in help_text
    
    def test_status_command(self):
        """Test status command"""
        rag = RAGSkill()
        status = rag.handle("rag status")
        
        assert "RAG System Status" in status
        assert "Ollama" in status
    
    def test_add_text_command(self):
        """Test adding text directly"""
        rag = RAGSkill()
        result = rag.handle("rag add_text test_doc :: This is a test document about machine learning")
        
        assert "Added" in result
        assert "test_doc" in result
    
    def test_add_file_command(self):
        """Test adding files"""
        rag = RAGSkill()
        result = rag.handle(f"rag add {self.temp_path / 'test.txt'}")
        
        assert "Indexed" in result
        assert "documents" in result


class TestEmbeddingFunction:
    """Test embedding functionality without RAG dependency"""
    
    def test_embedding_dimensions(self):
        """Test embedding dimensions"""
        if not RAG_AVAILABLE:
            pytest.skip("RAG not available")
            
        embedding = _simple_embed("test text")
        assert len(embedding) == 256
    
    def test_embedding_normalization(self):
        """Test that embeddings are normalized"""
        if not RAG_AVAILABLE:
            pytest.skip("RAG not available")
            
        import numpy as np
        embedding = _simple_embed("test text")
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-6  # Should be normalized
    
    def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings"""
        if not RAG_AVAILABLE:
            pytest.skip("RAG not available")
            
        import numpy as np
        emb1 = _simple_embed("This is about Python programming")
        emb2 = _simple_embed("This is about machine learning")
        
        # Should not be identical
        assert not np.array_equal(emb1, emb2)
    
    def test_similar_texts_similar_embeddings(self):
        """Test that similar texts produce similar embeddings"""
        if not RAG_AVAILABLE:
            pytest.skip("RAG not available")
            
        import numpy as np
        emb1 = _simple_embed("Python programming language")
        emb2 = _simple_embed("Python programming code")
        
        # Should have high similarity
        similarity = np.dot(emb1, emb2)
        assert similarity > 0.8  # High similarity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])