# LLM Infrastructure

A unified **LiteLLM proxy** that provides seamless access to multiple LLM providers through a single OpenAI-compatible endpoint. Route requests to OpenAI, Anthropic, and other providers with automatic model discovery and robust health monitoring.

## Features

- **Universal Model Support** - Handle any OpenAI or Anthropic model with wildcard routing (`openai/*`, `anthropic/*`)
- **Single Endpoint** - One API endpoint for all your LLM needs
- **Health Monitoring** - Automatic health checks ensure reliable service
- **Docker Ready** - Containerized deployment with Docker Compose
- **Secure Configuration** - Environment-based API key management
- **Load Balancing** - 8 workers for high-throughput scenarios

## Quick Start

### Prerequisites

- Docker and Docker Compose
- API keys for desired providers (OpenAI, Anthropic)

### Setup

1. **Clone and configure environment**:

   ```bash
   git clone <repository-url>
   cd llm-infra
   cp .env.template .env
   ```

2. **Add your API keys to `.env`**:

   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. **Start the proxy**:

   ```bash
   docker compose up -d
   ```

The proxy will be available at `http://localhost:4000`.

## Usage

### Basic Chat Completion

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Supported Model Patterns

The proxy automatically routes requests based on model names:

- **OpenAI models**: `openai/gpt-4o`, `openai/gpt-4o-mini`, `openai/gpt-3.5-turbo`
- **Anthropic models**: `anthropic/claude-3-5-sonnet-20241022`, `anthropic/claude-3-opus-20240229`

### Health Check

```bash
curl http://localhost:4000/health
```

## Configuration

### Model Routing

The `litellm-config.yaml` defines wildcard patterns for automatic model discovery:

```yaml
model_list:
  - model_name: "openai/*"
    litellm_params:
      model: openai/*
      api_key: os.environ/OPENAI_API_KEY
    model_info:
      health_check_model: openai/gpt-4o-mini
```

### Scaling

Adjust worker count in `docker-compose.yaml`:

```yaml
command: ["--config", "/app/config.yaml", "--port", "4000", "--num_workers", "16"]
```

## Development

### Adding New Providers

1. Add provider configuration to `litellm-config.yaml`:

   ```yaml
   - model_name: "provider/*"
     litellm_params:
       model: provider/*
       api_key: os.environ/PROVIDER_API_KEY
     model_info:
       health_check_model: provider/specific-model
   ```

2. Add API key to `.env.template` and `.env`

3. Restart the proxy: `docker compose restart`

### Testing New Models

```bash
# Test any supported model
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "provider/new-model-name",
    "messages": [{"role": "user", "content": "Test message"}]
  }'
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Change the host port in docker-compose.yaml
ports:
  - "4001:4000"  # Use port 4001 instead
```

#### API Key Errors

- Verify `.env` file contains valid API keys
- Ensure environment variable names match `litellm-config.yaml`
- Restart container after changing environment variables

#### Model Not Found

- Check if model name matches provider patterns (`provider/model-name`)
- Verify provider API key is valid and has access to the model
- Review proxy logs: `docker compose logs litellm`

### Logs and Monitoring

```bash
# View real-time logs
docker compose logs -f litellm

# Check container status
docker compose ps
```

## Architecture

```text
Client Request
     ↓
LiteLLM Proxy (Port 4000)
     ↓
Wildcard Router
     ↓
┌─────────────┬─────────────┐
│ OpenAI API  │ Anthropic   │
│             │ API         │
└─────────────┴─────────────┘
```

The proxy acts as a unified gateway, automatically routing requests to the appropriate provider based on model name patterns while maintaining OpenAI-compatible request/response formats.
