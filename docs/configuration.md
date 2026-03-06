# Kili Python SDK Configuration Guide

## Overview

The Kili Python SDK supports multiple configuration methods with a clear priority order. Configuration can be set via:

1. Function parameters (highest priority)
2. Environment variables
3. Configuration file (`sdk-config.json`)
4. Default values (lowest priority)

## Configuration File

### Location

The SDK searches for `sdk-config.json` in the following locations (in order):

1. Current working directory
2. Home directory (`~`)

### Format

Create `sdk-config.json` with the following structure:

```json
{
  "api_key": "your-api-key-here",
  "api_endpoint": "https://cloud.kili-technology.com/api/label/v2/graphql",
  "verify_ssl": true,
  "disable_tqdm": false
}
```

## Configuration Options

### 1. API Key (`api_key`)

Your Kili API key for authentication.

**Configuration Methods:**
```python
# 1. Function parameter (highest priority)
kili = Kili(api_key="your-api-key")

# 2. Environment variable
export KILI_API_KEY="your-api-key"

# 3. Configuration file
{
  "api_key": "your-api-key"
}

# 4. Interactive prompt (if not set and terminal is available)
# The SDK will prompt you to enter the API key
```

**Example:**
```python
from kili.client import Kili

# Method 1: Direct parameter
kili = Kili(api_key="abc123")

# Method 2: Environment variable
# $ export KILI_API_KEY="abc123"
kili = Kili()  # Will use env var

# Method 3: Config file (sdk-config.json)
kili = Kili()  # Will use config file
```

---

### 2. API Endpoint (`api_endpoint`)

The GraphQL endpoint URL for Kili API.

**Configuration Methods:**
```python
# 1. Function parameter
kili = Kili(api_endpoint="https://custom.kili.com/api/label/v2/graphql")

# 2. Environment variable
export KILI_API_ENDPOINT="https://custom.kili.com/api/label/v2/graphql"

# 3. Configuration file
{
  "api_endpoint": "https://custom.kili.com/api/label/v2/graphql"
}

# 4. Default value
# "https://cloud.kili-technology.com/api/label/v2/graphql"
```

**Example:**
```python
from kili.client import Kili

# For on-premise installations
kili = Kili(
    api_key="your-api-key",
    api_endpoint="https://your-company.kili.com/api/label/v2/graphql"
)

# Or via environment variable
# $ export KILI_API_ENDPOINT="https://your-company.kili.com/api/label/v2/graphql"
kili = Kili(api_key="your-api-key")
```

---

### 3. TLS Verification (`verify` / `verify_ssl`)

Controls TLS certificate verification for HTTPS requests.

**Values:**

- `True` (default): Verify TLS certificates
- `False`: Disable verification (not recommended for production)
- `str`: Path to CA bundle file

**Configuration Methods:**
```python
# 1. Function parameter (uses 'verify')
kili = Kili(verify=False)

# 2. Environment variable
export KILI_VERIFY=false  # or "true", "1", "yes"

# 3. Configuration file (uses 'verify_ssl')
{
  "verify_ssl": false
}

# Note: The config file also supports 'verify' for backward compatibility

# 4. Default value: True
```

**Example:**
```python
from kili.client import Kili

# Disable verification for local development (NOT RECOMMENDED FOR PRODUCTION)
kili = Kili(
    api_key="your-api-key",
    verify=False
)

# Use custom CA bundle
kili = Kili(
    api_key="your-api-key",
    verify="/path/to/ca-bundle.crt"
)

# Via environment variable for testing
# $ export KILI_VERIFY=false
kili = Kili(api_key="your-api-key")
```

---

### 4. Disable Progress Bars (`disable_tqdm`)

Globally disable progress bars (tqdm) for all operations. Individual function calls can still override this setting.

**Values:**

- `None` (default): Use each function's default behavior
- `True`: Disable progress bars globally
- `False`: Enable progress bars globally

**Configuration Methods:**
```python
# 1. Function parameter (highest priority)
kili = Kili(disable_tqdm=True)

# 2. Environment variable
export KILI_DISABLE_TQDM=true  # or "false", "1", "yes"

# 3. Configuration file
{
  "disable_tqdm": true
}

# 4. Default: None (each function uses its own default)
```

**Priority for Individual Operations:**

1. Function parameter: `kili.assets(project_id="id", disable_tqdm=True)`
2. Client global setting: `Kili(disable_tqdm=True)`
3. Function default (usually `False` to show progress)

**Example:**
```python
from kili.client import Kili

# Disable progress bars globally for automated scripts
kili = Kili(api_key="your-api-key", disable_tqdm=True)

# All operations will have progress bars disabled
assets = kili.assets(project_id="your-project-id")
projects = kili.projects()

# Override for specific operations
labels = kili.labels(
    project_id="your-project-id",
    disable_tqdm=False  # Show progress bar just for this call
)

# Via environment variable for CI/CD
# $ export KILI_DISABLE_TQDM=true
kili = Kili(api_key="your-api-key")  # Progress bars disabled
```

---

## Environment Variables Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KILI_API_KEY` | string | None | Your Kili API key |
| `KILI_API_ENDPOINT` | string | `https://cloud.kili-technology.com/api/label/v2/graphql` | GraphQL API endpoint |
| `KILI_VERIFY` | boolean/string | `true` | TLS certificate verification |
| `KILI_DISABLE_TQDM` | boolean | None | Disable progress bars globally |

**Boolean Environment Variables:**

- Truthy values: `"true"`, `"1"`, `"yes"` (case-insensitive)
- Falsy values: `"false"`, `"0"`, `"no"` (case-insensitive)

---

## Example : Production Configuration

```json
{
  "api_endpoint": "https://cloud.kili-technology.com/api/label/v2/graphql",
  "verify_ssl": true,
  "disable_tqdm": false
}
```

```bash
export KILI_API_KEY="your-production-key"
```

```python
from kili.client import Kili

# Loads settings from env var and config file
kili = Kili()
```

## Configuration Priority Summary

For each setting, the priority order is:

1. **Function parameter** (highest)
   ```python
   Kili(api_key="key", verify=False, disable_tqdm=True)
   ```

2. **Environment variable**
   ```bash
   export KILI_API_KEY="key"
   export KILI_VERIFY=false
   export KILI_DISABLE_TQDM=true
   ```

3. **Configuration file** (`sdk-config.json`)
   ```json
   {
     "api_key": "key",
     "verify_ssl": false,
     "disable_tqdm": true
   }
   ```

4. **Default value** (lowest)

    - `api_endpoint`: `https://cloud.kili-technology.com/api/label/v2/graphql`
    - `verify`: `True`
    - `disable_tqdm`: `None`
