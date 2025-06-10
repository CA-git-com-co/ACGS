# Task Master Configuration

## Security Notice

The `config.json` file contains API key references that should be set as environment variables. Never commit actual API keys to version control.

## Setup Instructions

1. Copy the template configuration:
   ```bash
   cp config.json.template config.json
   ```

2. Set your API keys as environment variables:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   export GOOGLE_API_KEY="your-google-api-key"
   export XAI_API_KEY="your-xai-api-key"
   # Add other API keys as needed
   ```

3. Or create a `.env` file in the project root:
   ```bash
   ANTHROPIC_API_KEY=your-anthropic-api-key
   GOOGLE_API_KEY=your-google-api-key
   XAI_API_KEY=your-xai-api-key
   ```

## Configuration Format

The configuration uses environment variable substitution with `${VARIABLE_NAME}` syntax. The Task Master system will automatically resolve these at runtime.

## Security Best Practices

- Never commit actual API keys to version control
- Use environment variables or secure secret management
- Regularly rotate API keys
- Monitor API key usage for unauthorized access
