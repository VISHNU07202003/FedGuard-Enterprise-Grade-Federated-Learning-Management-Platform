# FedGuard Copilot (AWS Bedrock)

FedGuard Copilot is an in-app AI assistant designed to help researchers and administrators understand federated training runs, privacy metrics, and client reliability.

## Architecture

The Copilot uses a **backend-only** LLM architecture to ensure security and prevent credentials from leaking to the frontend.
All prompts and contextual data are built in the FastAPI backend before being dispatched to the language model.

### 1. Mock vs. Bedrock

To support seamless local development without requiring AWS credentials, the application provides two `LLMClient` implementations:
- `MockLLMClient`: The default. Returns simulated, grounded responses based on context strings found in the payload.
- `BedrockLLMClient`: Uses `boto3` to communicate with the AWS Bedrock Converse API. 

**Configuration:**
Set `LLM_PROVIDER=bedrock` in your `.env` file to activate the real AWS connection.

### 2. Context Grounding

To prevent "hallucination," the LLM is not allowed to query the database using raw SQL. Instead, the backend intercepts the chat request, identifies the requested resource (e.g., `run_id`), retrieves the concrete data from PostgreSQL (via `ContextBuilder`), and passes a JSON summary inside the hidden system prompt.

### 3. Guardrails

The Copilot is equipped with **two layers** of guardrails:
- **Local Heuristics**: Regex-based blocks to prevent extraction of secrets or fabrication of metrics.
- **AWS Bedrock Guardrails**: (Optional) Enforces AWS-managed safety filters if `AWS_BEDROCK_GUARDRAIL_ID` is configured.

### 4. RAG / Knowledge Bases

Currently, the Copilot uses a simple fallback RAG implementation that reads local Markdown files (like `PRIVACY.md`) and injects them into the prompt. Future iterations could use Amazon Bedrock Knowledge Bases.
