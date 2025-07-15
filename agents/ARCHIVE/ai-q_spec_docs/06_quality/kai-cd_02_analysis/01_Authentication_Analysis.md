---
title: "Authentication Analysis"
description: "Technical specification for authentication analysis"
type: "analysis"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing authentication analysis"
---

# Kai-CD Service Authentication Summary

## Agent Context
**For AI Agents**: This analysis documents authentication requirements for all Kai-CD service connectors. Use when debugging service authentication issues or adding new services to understand required authentication patterns.

**Implementation Notes**: Covers bearer tokens, API keys, and no-auth services. Each service type has specific authentication patterns documented with technical details and fixes applied.
**Quality Requirements**: Keep authentication patterns synchronized with service definitions. Verify all service authentication methods are current and functional.
**Integration Points**: Links directly to service definitions in src/connectors/definitions/ and service forms in UI components.

---

## Services that DON'T need authentication (type: 'none')
- **Ollama** - Works out of the box, no API key needed
- **A1111 WebUI** - No authentication required  
- **ComfyUI** - No authentication required
- **Chroma** - Vector database, no auth by default
- **Reticulum** - Uses cryptographic identities, not traditional auth

## Services that REQUIRE authentication

### Bearer Token (type: 'bearer_token')
- **Open WebUI** - JWT token from browser after login ✅ FIXED
- **OpenAI** - API key from OpenAI platform
- **Anthropic** - API key from Anthropic console (uses x-api-key header)
- **Hugging Face** - User access token
- **Dropbox** - OAuth access token
- **LM Studio** - Bearer token
- **vLLM** - Bearer token
- **Llama.cpp** - Bearer token
- **Milvus** - Username:password as bearer token

### API Key (type: 'api_key')
- **n8n** - X-N8N-API-KEY header
- **Anthropic** - x-api-key header

### Cloud Services (type: 'bearer_token')
- **Civitai** - API key for model downloads
- **OpenAI Compatible** - Various providers

## FIXES APPLIED:
1. ✅ Added missing authentication to Open WebUI definition
2. ✅ Enhanced ServiceForm with credential field for auth-required services  
3. ✅ Added validation to prevent creating services without required credentials
4. ✅ Enhanced ParameterControl to load dynamic options (models, samplers, etc.)
5. ✅ Fixed API stream error logging with proper context
6. ✅ Added service prop to ImageGenerationView parameter controls

## USER TESTING NEEDED:
- Open WebUI: Create credential with JWT token, verify model loading
- A1111: Verify samplers, models, upscalers load in dropdowns
- ComfyUI: Verify models and samplers populate
- Ollama: Verify chat works without credentials
