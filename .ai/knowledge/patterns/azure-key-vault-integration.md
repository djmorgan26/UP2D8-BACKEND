---
type: pattern
name: Azure Key Vault Integration
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - shared/key_vault_client.py
  - dependencies.py
  - main.py
related:
  - .ai/knowledge/components/dependencies.md
tags: [security, azure, key-vault, secrets, credentials]
---

# Azure Key Vault Integration Pattern

## What It Is

A secure secrets management pattern using Azure Key Vault with DefaultAzureCredential for seamless authentication across local development and production environments. Eliminates the need to store secrets in code or environment variables.

## How It Works

The pattern uses a singleton Key Vault client with lazy initialization and Azure's DefaultAzureCredential for automatic authentication.

**Key files:**
- `shared/key_vault_client.py:6-28` - Key Vault client implementation
- `dependencies.py:18-36` - Secret initialization
- `main.py:25-30` - Global secret loading

### Key Vault Client (shared/key_vault_client.py)

**Singleton Pattern:**
```python
_secret_client = None

def get_secret_client() -> SecretClient:
    global _secret_client
    if _secret_client is None:
        load_dotenv()
        key_vault_uri = os.environ["KEY_VAULT_URI"]
        credential = DefaultAzureCredential()
        _secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
    return _secret_client
```

**Benefits:**
- Single SecretClient instance reused across application
- Lazy initialization (only created when first needed)
- Reduces authentication overhead
- Thread-safe for async operations

**KeyVaultClient class:**
```python
class KeyVaultClient:
    def __init__(self):
        self.client = get_secret_client()

    def get_secret(self, secret_name: str) -> str:
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            print(f"Error retrieving secret {secret_name}: {e}")
            raise
```

### DefaultAzureCredential Authentication

**Local Development:**
1. Developer runs `az login` via Azure CLI
2. DefaultAzureCredential detects Azure CLI credentials
3. Uses logged-in user's identity to access Key Vault
4. User must have "Get" permissions on secrets in Key Vault

**Production (Azure App Service):**
1. App Service has System-Assigned Managed Identity enabled
2. DefaultAzureCredential detects Managed Identity
3. Uses Managed Identity to access Key Vault
4. Managed Identity must have "Get" permissions on secrets

**Credential Chain (in order):**
1. Environment variables
2. Managed Identity (Azure resources)
3. Azure CLI (local development)
4. Azure PowerShell
5. Interactive browser (fallback)

### Secret Initialization (dependencies.py)

**Module-level initialization:**
```python
def initialize_secrets():
    kv_client = get_key_vault_client_instance()
    secrets = {
        "MONGO_DB_CONNECTION_STRING": kv_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8"),
        "GEMINI_API_KEY": kv_client.get_secret("UP2D8-GEMINI-API-Key"),
        "SMTP_KEY": kv_client.get_secret("UP2D8-SMTP-KEY"),
        "GOOGLE_CLIENT_ID": kv_client.get_secret("GOOGLE-CLIENT-ID"),
        "GOOGLE_CLIENT_SECRET": kv_client.get_secret("GOOGLE-CLIENT-SECRET"),
    }
    global GEMINI_API_KEY, SMTP_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    GEMINI_API_KEY = secrets["GEMINI_API_KEY"]
    SMTP_KEY = secrets["SMTP_KEY"]
    GOOGLE_CLIENT_ID = secrets["GOOGLE_CLIENT_ID"]
    GOOGLE_CLIENT_SECRET = secrets["GOOGLE_CLIENT_SECRET"]
    genai.configure(api_key=GEMINI_API_KEY)
    return secrets
```

**Called at startup:**
- `main.py:25` - Secrets loaded before app initialization
- `main.py:30` - Gemini API configured with retrieved key

## Important Decisions

- **DefaultAzureCredential**: Chosen over explicit credential types for environment flexibility
- **Singleton Pattern**: Single SecretClient instance to avoid repeated authentication
- **Module-Level Init**: Secrets loaded at import time, not per-request (reduces latency)
- **Global Variables**: Some secrets stored as globals for libraries requiring module-level config (like genai)
- **Single .env Variable**: Only `KEY_VAULT_URI` in .env file, all other secrets in Key Vault
- **Error Handling**: Exceptions propagate to caller (fail-fast approach)
- **Secret Name Mapping**: Descriptive Key Vault names mapped to app-friendly variable names

## Usage Example

### Local Development Setup

```bash
# 1. Login to Azure CLI
az login

# 2. Create .env file
echo 'KEY_VAULT_URI="https://your-vault.vault.azure.net/"' > .env

# 3. Ensure you have "Get" permissions on secrets
# Azure Portal → Key Vault → Access Policies → Add your user
```

### Using Secrets in Code

```python
from dependencies import initialize_secrets

# Get all secrets at once
secrets = initialize_secrets()
mongo_uri = secrets["MONGO_DB_CONNECTION_STRING"]

# Or access global variables (for libraries)
from dependencies import GEMINI_API_KEY
print(GEMINI_API_KEY)  # Already configured

# Using KeyVaultClient directly
from shared.key_vault_client import KeyVaultClient

kv_client = KeyVaultClient()
secret_value = kv_client.get_secret("MY-SECRET-NAME")
```

### Production Deployment

```bash
# 1. Enable Managed Identity on App Service
# Azure Portal → App Service → Identity → System assigned → On

# 2. Grant access to Key Vault
# Key Vault → Access Policies → Add → Select Managed Identity

# 3. Set environment variable
# App Service → Configuration → Application Settings
KEY_VAULT_URI=https://your-vault.vault.azure.net/
```

## Common Issues

- **No Azure Login**: If `az login` not run locally, DefaultAzureCredential fails
- **Missing Permissions**: User/Managed Identity needs "Get" permission on secrets
- **Wrong KEY_VAULT_URI**: Must match exact Key Vault URL (including https://)
- **Secret Name Typos**: Key Vault secret names are case-sensitive
- **Managed Identity Not Enabled**: Production fails if Managed Identity not configured
- **Network Access**: Key Vault firewall may block requests (check network rules)

## Testing

- Test files: `tests/`
- Testing approach:
  - Mock KeyVaultClient for unit tests
  - Use test Key Vault for integration tests
  - Validate credential chain with different auth methods

## Comparison with Alternatives

### Environment Variables (.env files)
❌ Secrets visible in code/repos
❌ Difficult to rotate
❌ No audit trail
✅ Azure Key Vault eliminates these issues

### AWS Secrets Manager
Similar pattern, different cloud provider
Azure Key Vault chosen for Azure-native deployment

### HashiCorp Vault
More complex setup
Key Vault chosen for Azure integration

## Related Knowledge

- [Dependencies Component](../components/dependencies.md)
- [MongoDB Integration Pattern](./mongodb-integration.md)

## Best Practices

✅ **DO:**
- Use DefaultAzureCredential for all Azure services
- Rotate secrets regularly in Key Vault
- Use Managed Identity in production
- Log secret retrieval errors (not values!)
- Keep KEY_VAULT_URI in environment config

❌ **DON'T:**
- Store secrets in .env files (only Key Vault URI)
- Log secret values
- Commit KEY_VAULT_URI to public repos
- Create multiple SecretClient instances
- Hard-code secret names (use constants)

## Future Ideas

- [ ] Add secret caching to reduce Key Vault API calls
- [ ] Implement secret rotation without app restart
- [ ] Add retry logic for transient Key Vault failures
- [ ] Monitor secret access with Azure Monitor
- [ ] Add secret version pinning for consistency
- [ ] Implement secret validation on startup
- [ ] Create secret refresh mechanism
- [ ] Add circuit breaker for Key Vault unavailability
