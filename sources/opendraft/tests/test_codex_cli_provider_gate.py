import pytest
from opendraft import cli

@pytest.mark.parametrize('provider,key', [('claude','ANTHROPIC_API_KEY'),('openai','OPENAI_API_KEY'),('gemini','GOOGLE_API_KEY'),('gemini','GEMINI_API_KEY')])
def test_cli_accepts_selected_provider_without_google_key(monkeypatch,provider,key):
 for name in ['GOOGLE_API_KEY','GEMINI_API_KEY','OPENAI_API_KEY','ANTHROPIC_API_KEY']:monkeypatch.delenv(name,raising=False)
 monkeypatch.setenv('AI_PROVIDER',provider);monkeypatch.setenv(key,'test-only-placeholder')
 monkeypatch.setattr(cli,'get_saved_config',lambda:{})
 assert cli.has_api_key()

def test_wrong_provider_key_does_not_pass_gate(monkeypatch):
 monkeypatch.setenv('AI_PROVIDER','openai');monkeypatch.delenv('OPENAI_API_KEY',raising=False)
 monkeypatch.setenv('GOOGLE_API_KEY','test-only-placeholder')
 assert not cli.has_api_key()
