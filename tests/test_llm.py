"""
Unit tests per il modulo LLM.

Testa le funzionalità di base delle classi LLM, inclusa l'inizializzazione,
la factory e i metodi principali.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.llm import BaseLLM, LlamaLLM, LLMFactory
from src.llm.base import LLMError, ValidationError


class TestBaseLLM:
    """Test per la classe base BaseLLM."""
    
    def test_base_llm_is_abstract(self):
        """Verifica che BaseLLM non possa essere istanziata direttamente."""
        with pytest.raises(TypeError):
            BaseLLM("test-model")
    
    def test_base_llm_methods_exist(self):
        """Verifica che i metodi astratti siano definiti."""
        assert hasattr(BaseLLM, 'generate')
        assert hasattr(BaseLLM, 'generate_json')
        assert hasattr(BaseLLM, 'is_available')


class TestLlamaLLM:
    """Test per la classe LlamaLLM."""
    
    def test_initialization_default(self):
        """Testa l'inizializzazione con parametri di default."""
        llm = LlamaLLM()
        assert llm.model_name == "llama2"
        assert llm.base_url == "http://localhost:11434"
        assert llm.timeout == 120
    
    def test_initialization_custom_model(self):
        """Testa l'inizializzazione con modello personalizzato."""
        llm = LlamaLLM(model_name="llama3")
        assert llm.model_name == "llama3"
    
    def test_initialization_custom_url(self):
        """Testa l'inizializzazione con URL personalizzato."""
        custom_url = "http://192.168.1.100:11434"
        llm = LlamaLLM(base_url=custom_url)
        assert llm.base_url == custom_url
    
    def test_base_url_strips_trailing_slash(self):
        """Verifica che lo slash finale venga rimosso dall'URL."""
        llm = LlamaLLM(base_url="http://localhost:11434/")
        assert llm.base_url == "http://localhost:11434"
    
    def test_get_model_name(self):
        """Testa il metodo get_model_name."""
        llm = LlamaLLM(model_name="codellama")
        assert llm.get_model_name() == "codellama"
    
    def test_get_config(self):
        """Testa il metodo get_config."""
        llm = LlamaLLM(model_name="llama2", custom_param="test")
        config = llm.get_config()
        assert "custom_param" in config
        assert config["custom_param"] == "test"
    
    def test_is_available_success(self):
        """Testa is_available quando Ollama è disponibile."""
        # Mock della risposta API
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:latest"},
                {"name": "codellama:latest"}
            ]
        }
        mock_requests.get.return_value = mock_response
        
        llm = LlamaLLM(model_name="llama2")
        llm._client = mock_requests
        
        assert llm.is_available() is True
    
    def test_is_available_model_not_found(self):
        """Testa is_available quando il modello non è disponibile."""
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "models": [{"name": "other-model:latest"}]
        }
        mock_requests.get.return_value = mock_response
        
        llm = LlamaLLM(model_name="llama2")
        llm._client = mock_requests
        
        assert llm.is_available() is False
    
    def test_is_available_connection_error(self):
        """Testa is_available quando Ollama non è raggiungibile."""
        mock_requests = Mock()
        mock_requests.get.side_effect = Exception("Connection refused")
        
        llm = LlamaLLM()
        llm._client = mock_requests
        
        assert llm.is_available() is False
    
    def test_generate_success(self):
        """Testa la generazione di testo con successo."""
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Generated text response"
        }
        mock_requests.post.return_value = mock_response
        
        llm = LlamaLLM()
        llm._client = mock_requests
        
        result = llm.generate("Test prompt")
        
        assert result == "Generated text response"
        mock_requests.post.assert_called_once()
    
    def test_generate_with_schema(self):
        """Testa la generazione con schema JSON."""
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Generated text with schema"
        }
        mock_requests.post.return_value = mock_response
        
        llm = LlamaLLM()
        llm._client = mock_requests
        
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        result = llm.generate("Test prompt", schema=schema)
        
        assert result == "Generated text with schema"
        
        # Verifica che lo schema sia stato incluso nel prompt
        call_args = mock_requests.post.call_args
        payload = call_args[1]['json']
        assert "schema" in payload['prompt'].lower()
    
    def test_generate_with_temperature(self):
        """Testa la generazione con parametro temperature."""
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Text"}
        mock_requests.post.return_value = mock_response
        
        llm = LlamaLLM()
        llm._client = mock_requests
        
        llm.generate("Test", temperature=0.5)
        
        call_args = mock_requests.post.call_args
        payload = call_args[1]['json']
        assert payload['options']['temperature'] == 0.5
    
    def test_generate_api_error(self):
        """Testa la gestione degli errori API."""
        mock_requests = Mock()
        mock_requests.post.side_effect = Exception("API Error")
        
        llm = LlamaLLM()
        llm._client = mock_requests
        
        with pytest.raises(LLMError):
            llm.generate("Test prompt")
    
    def test_generate_json_success(self):
        """Testa la generazione JSON con successo."""
        mock_requests = Mock()
        json_output = {"name": "Test", "value": 42}
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": json.dumps(json_output)
        }
        mock_requests.post.return_value = mock_response
        
        llm = LlamaLLM()
        llm._client = mock_requests
        
        schema = {"type": "object"}
        result = llm.generate_json("Generate data", schema)
        
        assert result == json_output
    
    def test_generate_json_with_markdown(self):
        """Testa la generazione JSON con markdown code block."""
        mock_requests = Mock()
        json_output = {"name": "Test"}
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": f'```json\n{json.dumps(json_output)}\n```'
        }
        mock_requests.post.return_value = mock_response
        
        llm = LlamaLLM()
        llm._client = mock_requests
        
        schema = {"type": "object"}
        result = llm.generate_json("Generate", schema)
        
        assert result == json_output
    
    def test_generate_json_invalid(self):
        """Testa la gestione di JSON non valido."""
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Not a valid JSON"
        }
        mock_requests.post.return_value = mock_response
        
        llm = LlamaLLM()
        llm._client = mock_requests
        
        schema = {"type": "object"}
        
        with pytest.raises(ValidationError):
            llm.generate_json("Generate", schema)
    
    def test_get_available_models(self):
        """Testa il recupero dei modelli disponibili."""
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:latest"},
                {"name": "llama3:latest"},
                {"name": "codellama:latest"}
            ]
        }
        mock_requests.get.return_value = mock_response
        
        llm = LlamaLLM()
        llm._client = mock_requests
        
        models = llm.get_available_models()
        
        assert len(models) == 3
        assert "llama2:latest" in models
        assert "llama3:latest" in models


class TestLLMFactory:
    """Test per la factory LLMFactory."""
    
    def test_create_llama_default(self):
        """Testa la creazione del provider Llama con default."""
        llm = LLMFactory.create('llama')
        assert isinstance(llm, LlamaLLM)
        assert llm.model_name == "llama2"
    
    def test_create_llama_custom_model(self):
        """Testa la creazione con modello personalizzato."""
        llm = LLMFactory.create('llama', model_name='llama3')
        assert isinstance(llm, LlamaLLM)
        assert llm.model_name == "llama3"
    
    def test_create_ollama_alias(self):
        """Testa l'alias 'ollama' per Llama."""
        llm = LLMFactory.create('ollama')
        assert isinstance(llm, LlamaLLM)
    
    def test_create_case_insensitive(self):
        """Testa che il provider sia case-insensitive."""
        llm1 = LLMFactory.create('LLAMA')
        llm2 = LLMFactory.create('Llama')
        assert isinstance(llm1, LlamaLLM)
        assert isinstance(llm2, LlamaLLM)
    
    def test_create_unsupported_provider(self):
        """Testa l'errore per provider non supportato."""
        with pytest.raises(LLMError):
            LLMFactory.create('unsupported_provider')
    
    @patch.dict('os.environ', {'LLM_PROVIDER': 'llama'})
    def test_create_from_env(self):
        """Testa la creazione usando variabile d'ambiente."""
        llm = LLMFactory.create()
        assert isinstance(llm, LlamaLLM)
    
    @patch.dict('os.environ', {'LLAMA_MODEL': 'codellama'})
    def test_default_model_from_env(self):
        """Testa il modello di default da variabile d'ambiente."""
        llm = LLMFactory.create('llama')
        assert llm.model_name == "codellama"
    
    def test_create_with_custom_params(self):
        """Testa la creazione con parametri personalizzati."""
        llm = LLMFactory.create(
            'llama',
            model_name='llama2:13b',
            base_url='http://custom:11434',
            timeout=60
        )
        assert llm.model_name == "llama2:13b"
        assert llm.base_url == "http://custom:11434"
        assert llm.timeout == 60
    
    def test_get_available_providers(self):
        """Testa il recupero dei provider disponibili."""
        providers = LLMFactory.get_available_providers()
        assert 'llama' in providers
        assert 'ollama' in providers
    
    def test_register_provider(self):
        """Testa la registrazione di un provider personalizzato."""
        class CustomLLM(BaseLLM):
            def generate(self, prompt, **kwargs):
                return "custom"
            
            def generate_json(self, prompt, schema, **kwargs):
                return {}
            
            def is_available(self):
                return True
        
        LLMFactory.register_provider('custom', CustomLLM)
        
        llm = LLMFactory.create('custom', model_name='test')
        assert isinstance(llm, CustomLLM)
    
    def test_register_invalid_provider(self):
        """Testa l'errore per provider non valido."""
        class NotAnLLM:
            pass
        
        with pytest.raises(ValueError):
            LLMFactory.register_provider('invalid', NotAnLLM)
    
    def test_create_from_config(self):
        """Testa la creazione da dizionario di configurazione."""
        config = {
            'provider': 'llama',
            'model_name': 'llama2:13b',
            'base_url': 'http://localhost:11434',
            'timeout': 90
        }
        
        llm = LLMFactory.create_from_config(config)
        
        assert isinstance(llm, LlamaLLM)
        assert llm.model_name == "llama2:13b"
        assert llm.base_url == "http://localhost:11434"
        assert llm.timeout == 90
