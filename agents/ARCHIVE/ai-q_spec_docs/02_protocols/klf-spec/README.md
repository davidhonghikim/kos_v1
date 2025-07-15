# KLF (Kind Link Framework) Specification

The universal "telephone operator" protocol for the kOS ecosystem.

## Quick Start

1. **Read the Overview**: Start with `00_KLF_Protocol_Overview.yml`
2. **Pick Your Language**: Copy code from `05_KLF_Implementation_Examples.yml`
3. **Connect to Live Backend**: `http://localhost:30436` (PersonaRAG Bridge Server)

## File Structure

| File | Purpose |
|------|---------|
| `00_KLF_Protocol_Overview.yml` | Introduction and core concepts |
| `01_KLF_Message_Format.yml` | Universal message structure |
| `02_KLF_Agent_Registration.yml` | How agents join the network |
| `03_KLF_Service_Discovery.yml` | Finding available capabilities |
| `04_KLF_Transport_Options.yml` | HTTP, WebSocket, future protocols |
| `05_KLF_Implementation_Examples.yml` | Ready-to-use code examples |

## Supported Agent Types

- **AI Agents**: Python, JavaScript, Rust, Go implementations
- **Human Interfaces**: Web apps, mobile apps, CLI tools
- **Services**: Microservices, API proxies, data processors
- **Devices**: IoT sensors, smart home devices
- **Frontends**: React, Vue, Svelte, any web framework
- **Backends**: Node.js, Python, Rust, Go, any HTTP server

## Current Live Services

- Document upload/search/analysis
- AI persona chat and text generation
- Vector similarity search
- Secure vault operations
- System health monitoring

Connect to `http://localhost:30436` to access these services right now. 