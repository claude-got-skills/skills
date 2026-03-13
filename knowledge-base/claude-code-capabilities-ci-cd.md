<!-- Sources: github-actions + gitlab-ci-cd | Scraped: 2026-03-13 -->

# Claude Code GitHub Actions

Claude Code GitHub Actions brings AI-powered automation to your GitHub workflow. With a simple `@claude` mention in any PR or issue, Claude can analyze your code, create pull requests, implement features, and fix bugs - all while following your project's standards. For automatic reviews posted on every PR without a trigger, see [GitHub Code Review](https://code.claude.com/docs/en/code-review).

Claude Code GitHub Actions is built on top of the [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview), which enables programmatic integration of Claude Code into your applications. You can use the SDK to build custom automation workflows beyond GitHub Actions.

**Claude Opus 4.6 is now available.** Claude Code GitHub Actions default to Sonnet. To use Opus 4.6, configure the [model parameter](https://code.claude.com/docs/en/github-actions#breaking-changes-reference) to use `claude-opus-4-6`.

## Why use Claude Code GitHub Actions?

- **Instant PR creation**: Describe what you need, and Claude creates a complete PR with all necessary changes
- **Automated code implementation**: Turn issues into working code with a single command
- **Follows your standards**: Claude respects your `CLAUDE.md` guidelines and existing code patterns
- **Simple setup**: Get started in minutes with our installer and API key
- **Secure by default**: Your code stays on Github's runners

## What can Claude do?

Claude Code provides a powerful GitHub Action that transforms how you work with code:

### Claude Code Action

This GitHub Action allows you to run Claude Code within your GitHub Actions workflows. You can use this to build any custom workflow on top of Claude Code. [View repository](https://github.com/anthropics/claude-code-action)

## Setup

### Quick setup

The easiest way to set up this action is through Claude Code in the terminal. Just open claude and run `/install-github-app`. This command will guide you through setting up the GitHub app and required secrets.

- You must be a repository admin to install the GitHub app and add secrets
- The GitHub app will request read & write permissions for Contents, Issues, and Pull requests
- This quickstart method is only available for direct Claude API users. If you're using AWS Bedrock or Google Vertex AI, please see the [Using with AWS Bedrock & Google Vertex AI](https://code.claude.com/docs/en/github-actions#using-with-aws-bedrock-%26-google-vertex-ai) section.

### Manual setup

If the `/install-github-app` command fails or you prefer manual setup, please follow these manual setup instructions:

1. **Install the Claude GitHub app** to your repository: [https://github.com/apps/claude](https://github.com/apps/claude)

   The Claude GitHub app requires the following repository permissions:
   - **Contents**: Read & write (to modify repository files)
   - **Issues**: Read & write (to respond to issues)
   - **Pull requests**: Read & write (to create PRs and push changes)

   For more details on security and permissions, see the [security documentation](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md).

2. **Add ANTHROPIC_API_KEY** to your repository secrets ([Learn how to use secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions))

3. **Copy the workflow file** from [examples/claude.yml](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) into your repository's `.github/workflows/`

After completing either the quickstart or manual setup, test the action by tagging `@claude` in an issue or PR comment.

## Upgrading from Beta

Claude Code GitHub Actions v1.0 introduces breaking changes that require updating your workflow files in order to upgrade to v1.0 from the beta version.

If you're currently using the beta version of Claude Code GitHub Actions, we recommend that you update your workflows to use the GA version. The new version simplifies configuration while adding powerful new features like automatic mode detection.

### Essential changes

All beta users must make these changes to their workflow files in order to upgrade:

1. **Update the action version**: Change `@beta` to `@v1`
2. **Remove mode configuration**: Delete `mode: "tag"` or `mode: "agent"` (now auto-detected)
3. **Update prompt inputs**: Replace `direct_prompt` with `prompt`
4. **Move CLI options**: Convert `max_turns`, `model`, `custom_instructions`, etc. to `claude_args`

### Breaking Changes Reference

| Old Beta Input | New v1.0 Input |
| --- | --- |
| `mode` | _(Removed - auto-detected)_ |
| `direct_prompt` | `prompt` |
| `override_prompt` | `prompt` with GitHub variables |
| `custom_instructions` | `claude_args: --append-system-prompt` |
| `max_turns` | `claude_args: --max-turns` |
| `model` | `claude_args: --model` |
| `allowed_tools` | `claude_args: --allowedTools` |
| `disallowed_tools` | `claude_args: --disallowedTools` |
| `claude_env` | `settings` JSON format |

### Before and After Example

**Beta version:**

```yaml
- uses: anthropics/claude-code-action@beta
  with:
    mode: "tag"
    direct_prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    custom_instructions: "Follow our coding standards"
    max_turns: "10"
    model: "claude-sonnet-4-6"
```

**GA version (v1.0):**

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    claude_args: |
      --append-system-prompt "Follow our coding standards"
      --max-turns 10
      --model claude-sonnet-4-6
```

The action now automatically detects whether to run in interactive mode (responds to `@claude` mentions) or automation mode (runs immediately with a prompt) based on your configuration.

## Example use cases

Claude Code GitHub Actions can help you with a variety of tasks. The [examples directory](https://github.com/anthropics/claude-code-action/tree/main/examples) contains ready-to-use workflows for different scenarios.

### Basic workflow

```yaml
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # Responds to @claude mentions in comments
```

### Using skills

```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Review this pull request for code quality, correctness, and security. Analyze the diff, then post your findings as review comments."
          claude_args: "--max-turns 5"
```

### Custom automation with prompts

```yaml
name: Daily Report
on:
  schedule:
    - cron: "0 9 * * *"
jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Generate a summary of yesterday's commits and open issues"
          claude_args: "--model opus"
```

### Common use cases

In issue or PR comments:

```
@claude implement this feature based on the issue description
@claude how should I implement user authentication for this endpoint?
@claude fix the TypeError in the user dashboard component
```

Claude will automatically analyze the context and respond appropriately.

## Best practices

### CLAUDE.md configuration

Create a `CLAUDE.md` file in your repository root to define code style guidelines, review criteria, project-specific rules, and preferred patterns. This file guides Claude's understanding of your project standards.

### Security considerations

Never commit API keys directly to your repository.

For comprehensive security guidance including permissions, authentication, and best practices, see the [Claude Code Action security documentation](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md). Always use GitHub Secrets for API keys:

- Add your API key as a repository secret named `ANTHROPIC_API_KEY`
- Reference it in workflows: `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
- Limit action permissions to only what's necessary
- Review Claude's suggestions before merging

Always use GitHub Secrets (for example, `${{ secrets.ANTHROPIC_API_KEY }}`) rather than hardcoding API keys directly in your workflow files.

### Optimizing performance

Use issue templates to provide context, keep your `CLAUDE.md` concise and focused, and configure appropriate timeouts for your workflows.

### CI costs

When using Claude Code GitHub Actions, be aware of the associated costs:

**GitHub Actions costs:**
- Claude Code runs on GitHub-hosted runners, which consume your GitHub Actions minutes
- See [GitHub's billing documentation](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions) for detailed pricing and minute limits

**API costs:**
- Each Claude interaction consumes API tokens based on the length of prompts and responses
- Token usage varies by task complexity and codebase size
- See [Claude's pricing page](https://claude.com/platform/api) for current token rates

**Cost optimization tips:**
- Use specific `@claude` commands to reduce unnecessary API calls
- Configure appropriate `--max-turns` in `claude_args` to prevent excessive iterations
- Set workflow-level timeouts to avoid runaway jobs
- Consider using GitHub's concurrency controls to limit parallel runs

## Configuration examples

The Claude Code Action v1 simplifies configuration with unified parameters:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "Your instructions here" # Optional
    claude_args: "--max-turns 5" # Optional CLI arguments
```

Key features:
- **Unified prompt interface** - Use `prompt` for all instructions
- **Skills** - Invoke installed [skills](https://code.claude.com/docs/en/skills) directly from the prompt
- **CLI passthrough** - Any Claude Code CLI argument via `claude_args`
- **Flexible triggers** - Works with any GitHub event

Visit the [examples directory](https://github.com/anthropics/claude-code-action/tree/main/examples) for complete workflow files.

When responding to issue or PR comments, Claude automatically responds to @claude mentions. For other events, use the `prompt` parameter to provide instructions.

## Using with AWS Bedrock & Google Vertex AI

For enterprise environments, you can use Claude Code GitHub Actions with your own cloud infrastructure. This approach gives you control over data residency and billing while maintaining the same functionality.

### Prerequisites

#### For Google Cloud Vertex AI:

1. A Google Cloud Project with Vertex AI enabled
2. Workload Identity Federation configured for GitHub Actions
3. A service account with the required permissions
4. A GitHub App (recommended) or use the default GITHUB_TOKEN

#### For AWS Bedrock:

1. An AWS account with Amazon Bedrock enabled
2. GitHub OIDC Identity Provider configured in AWS
3. An IAM role with Bedrock permissions
4. A GitHub App (recommended) or use the default GITHUB_TOKEN

### Step 1: Create a custom GitHub App (Recommended for 3P Providers)

For best control and security when using 3P providers like Vertex AI or Bedrock, we recommend creating your own GitHub App:

1. Go to [https://github.com/settings/apps/new](https://github.com/settings/apps/new)
2. Fill in the basic information:
   - **GitHub App name**: Choose a unique name (e.g., "YourOrg Claude Assistant")
   - **Homepage URL**: Your organization's website or the repository URL
3. Configure the app settings:
   - **Webhooks**: Uncheck "Active" (not needed for this integration)
4. Set the required permissions:
   - **Repository permissions**:
     - Contents: Read & Write
     - Issues: Read & Write
     - Pull requests: Read & Write
5. Click "Create GitHub App"
6. After creation, click "Generate a private key" and save the downloaded `.pem` file
7. Note your App ID from the app settings page
8. Install the app to your repository:
   - From your app's settings page, click "Install App" in the left sidebar
   - Select your account or organization
   - Choose "Only select repositories" and select the specific repository
   - Click "Install"
9. Add the private key as a secret to your repository:
   - Go to your repository's Settings > Secrets and variables > Actions
   - Create a new secret named `APP_PRIVATE_KEY` with the contents of the `.pem` file
10. Add the App ID as a secret:
    - Create a new secret named `APP_ID` with your GitHub App's ID

**Alternative for Claude API or if you don't want to setup your own Github app**: Use the official Anthropic app:
1. Install from: [https://github.com/apps/claude](https://github.com/apps/claude)
2. No additional configuration needed for authentication

### Step 2: Configure cloud provider authentication

Choose your cloud provider and set up secure authentication:

#### AWS Bedrock

**Configure AWS to allow GitHub Actions to authenticate securely without storing credentials.**

> **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

**Required Setup:**

1. **Enable Amazon Bedrock**: Request access to Claude models in Amazon Bedrock. For cross-region models, request access in all required regions.
2. **Set up GitHub OIDC Identity Provider**:
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`
3. **Create IAM Role for GitHub Actions**:
   - Trusted entity type: Web identity
   - Identity provider: `token.actions.githubusercontent.com`
   - Permissions: `AmazonBedrockFullAccess` policy
   - Configure trust policy for your specific repository

**Required Values**: After setup, you'll need:
- **AWS_ROLE_TO_ASSUME**: The ARN of the IAM role you created

OIDC is more secure than using static AWS access keys because credentials are temporary and automatically rotated. See [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html) for detailed OIDC setup instructions.

#### Google Vertex AI

**Configure Google Cloud to allow GitHub Actions to authenticate securely without storing credentials.**

> **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

**Required Setup:**

1. **Enable APIs** in your Google Cloud project:
   - IAM Credentials API
   - Security Token Service (STS) API
   - Vertex AI API
2. **Create Workload Identity Federation resources**:
   - Create a Workload Identity Pool
   - Add a GitHub OIDC provider with:
     - Issuer: `https://token.actions.githubusercontent.com`
     - Attribute mappings for repository and owner
     - **Security recommendation**: Use repository-specific attribute conditions
3. **Create a Service Account**:
   - Grant only `Vertex AI User` role
   - **Security recommendation**: Create a dedicated service account per repository
4. **Configure IAM bindings**:
   - Allow the Workload Identity Pool to impersonate the service account
   - **Security recommendation**: Use repository-specific principal sets

**Required Values**: After setup, you'll need:
- **GCP_WORKLOAD_IDENTITY_PROVIDER**: The full provider resource name
- **GCP_SERVICE_ACCOUNT**: The service account email address

Workload Identity Federation eliminates the need for downloadable service account keys, improving security. For detailed setup instructions, consult the [Google Cloud Workload Identity Federation documentation](https://cloud.google.com/iam/docs/workload-identity-federation).

### Step 3: Add Required Secrets

Add the following secrets to your repository (Settings > Secrets and variables > Actions):

#### For Claude API (Direct):

1. **For API Authentication**:
   - `ANTHROPIC_API_KEY`: Your Claude API key from [console.anthropic.com](https://console.anthropic.com/)
2. **For GitHub App (if using your own app)**:
   - `APP_ID`: Your GitHub App's ID
   - `APP_PRIVATE_KEY`: The private key (.pem) content

#### For Google Cloud Vertex AI

1. **For GCP Authentication**:
   - `GCP_WORKLOAD_IDENTITY_PROVIDER`
   - `GCP_SERVICE_ACCOUNT`
2. **For GitHub App (if using your own app)**:
   - `APP_ID`: Your GitHub App's ID
   - `APP_PRIVATE_KEY`: The private key (.pem) content

#### For AWS Bedrock

1. **For AWS Authentication**:
   - `AWS_ROLE_TO_ASSUME`
2. **For GitHub App (if using your own app)**:
   - `APP_ID`: Your GitHub App's ID
   - `APP_PRIVATE_KEY`: The private key (.pem) content

### Step 4: Create workflow files

Create GitHub Actions workflow files that integrate with your cloud provider.

#### AWS Bedrock workflow

**Prerequisites:**
- AWS Bedrock access enabled with Claude model permissions
- GitHub configured as an OIDC identity provider in AWS
- IAM role with Bedrock permissions that trusts GitHub Actions

**Required GitHub secrets:**

| Secret Name | Description |
| --- | --- |
| `AWS_ROLE_TO_ASSUME` | ARN of the IAM role for Bedrock access |
| `APP_ID` | Your GitHub App ID (from app settings) |
| `APP_PRIVATE_KEY` | The private key you generated for your GitHub App |

```yaml
name: Claude PR Action

permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude-pr:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    env:
      AWS_REGION: us-west-2
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
          aws-region: us-west-2

      - uses: anthropics/claude-code-action@v1
        with:
          github_token: ${{ steps.app-token.outputs.token }}
          use_bedrock: "true"
          claude_args: '--model us.anthropic.claude-sonnet-4-6 --max-turns 10'
```

The model ID format for Bedrock includes a region prefix (for example, `us.anthropic.claude-sonnet-4-6`).

#### Google Vertex AI workflow

**Prerequisites:**
- Vertex AI API enabled in your GCP project
- Workload Identity Federation configured for GitHub
- Service account with Vertex AI permissions

**Required GitHub secrets:**

| Secret Name | Description |
| --- | --- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload identity provider resource name |
| `GCP_SERVICE_ACCOUNT` | Service account email with Vertex AI access |
| `APP_ID` | Your GitHub App ID (from app settings) |
| `APP_PRIVATE_KEY` | The private key you generated for your GitHub App |

```yaml
name: Claude PR Action

permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude-pr:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}

      - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}

      - uses: anthropics/claude-code-action@v1
        with:
          github_token: ${{ steps.app-token.outputs.token }}
          trigger_phrase: "@claude"
          use_vertex: "true"
          claude_args: '--model claude-sonnet-4@20250514 --max-turns 10'
        env:
          ANTHROPIC_VERTEX_PROJECT_ID: ${{ steps.auth.outputs.project_id }}
          CLOUD_ML_REGION: us-east5
          VERTEX_REGION_CLAUDE_3_7_SONNET: us-east5
```

The project ID is automatically retrieved from the Google Cloud authentication step, so you don't need to hardcode it.

## Troubleshooting

### Claude not responding to @claude commands

Verify the GitHub App is installed correctly, check that workflows are enabled, ensure API key is set in repository secrets, and confirm the comment contains `@claude` (not `/claude`).

### CI not running on Claude's commits

Ensure you're using the GitHub App or custom app (not Actions user), check workflow triggers include the necessary events, and verify app permissions include CI triggers.

### Authentication errors

Confirm API key is valid and has sufficient permissions. For Bedrock/Vertex, check credentials configuration and ensure secrets are named correctly in workflows.

## Advanced configuration

### Action parameters

The Claude Code Action v1 uses a simplified configuration:

| Parameter | Description | Required |
| --- | --- | --- |
| `prompt` | Instructions for Claude (plain text or a [skill](https://code.claude.com/docs/en/skills) name) | No* |
| `claude_args` | CLI arguments passed to Claude Code | No |
| `anthropic_api_key` | Claude API key | Yes** |
| `github_token` | GitHub token for API access | No |
| `trigger_phrase` | Custom trigger phrase (default: "@claude") | No |
| `use_bedrock` | Use AWS Bedrock instead of Claude API | No |
| `use_vertex` | Use Google Vertex AI instead of Claude API | No |

*Prompt is optional - when omitted for issue/PR comments, Claude responds to trigger phrase

**Required for direct Claude API, not for Bedrock/Vertex

#### Pass CLI arguments

The `claude_args` parameter accepts any Claude Code CLI arguments:

```
claude_args: "--max-turns 5 --model claude-sonnet-4-6 --mcp-config /path/to/config.json"
```

Common arguments:
- `--max-turns`: Maximum conversation turns (default: 10)
- `--model`: Model to use (for example, `claude-sonnet-4-6`)
- `--mcp-config`: Path to MCP configuration
- `--allowed-tools`: Comma-separated list of allowed tools
- `--debug`: Enable debug output

### Alternative integration methods

While the `/install-github-app` command is the recommended approach, you can also:

- **Custom GitHub App**: For organizations needing branded usernames or custom authentication flows. Create your own GitHub App with required permissions (contents, issues, pull requests) and use the actions/create-github-app-token action to generate tokens in your workflows.
- **Manual GitHub Actions**: Direct workflow configuration for maximum flexibility
- **MCP Configuration**: Dynamic loading of Model Context Protocol servers

See the [Claude Code Action documentation](https://github.com/anthropics/claude-code-action/blob/main/docs) for detailed guides on authentication, security, and advanced configuration.

### Customizing Claude's behavior

You can configure Claude's behavior in two ways:

1. **CLAUDE.md**: Define coding standards, review criteria, and project-specific rules in a `CLAUDE.md` file at the root of your repository. Claude will follow these guidelines when creating PRs and responding to requests. Check out our [Memory documentation](https://code.claude.com/docs/en/memory) for more details.
2. **Custom prompts**: Use the `prompt` parameter in the workflow file to provide workflow-specific instructions. This allows you to customize Claude's behavior for different workflows or tasks.

Claude will follow these guidelines when creating PRs and responding to requests.

---

# Claude Code GitLab CI/CD

> Claude Code for GitLab CI/CD is currently in beta. Features and functionality may evolve as we refine the experience. This integration is maintained by GitLab. For support, see the following [GitLab issue](https://gitlab.com/gitlab-org/gitlab/-/issues/573776).

This integration is built on top of the [Claude Code CLI and Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview), enabling programmatic use of Claude in your CI/CD jobs and custom automation workflows.

## Why use Claude Code with GitLab?

- **Instant MR creation**: Describe what you need, and Claude proposes a complete MR with changes and explanation
- **Automated implementation**: Turn issues into working code with a single command or mention
- **Project-aware**: Claude follows your `CLAUDE.md` guidelines and existing code patterns
- **Simple setup**: Add one job to `.gitlab-ci.yml` and a masked CI/CD variable
- **Enterprise-ready**: Choose Claude API, AWS Bedrock, or Google Vertex AI to meet data residency and procurement needs
- **Secure by default**: Runs in your GitLab runners with your branch protection and approvals

## How it works

Claude Code uses GitLab CI/CD to run AI tasks in isolated jobs and commit results back via MRs:

1. **Event-driven orchestration**: GitLab listens for your chosen triggers (for example, a comment that mentions `@claude` in an issue, MR, or review thread). The job collects context from the thread and repository, builds prompts from that input, and runs Claude Code.
2. **Provider abstraction**: Use the provider that fits your environment:
   - Claude API (SaaS)
   - AWS Bedrock (IAM-based access, cross-region options)
   - Google Vertex AI (GCP-native, Workload Identity Federation)
3. **Sandboxed execution**: Each interaction runs in a container with strict network and filesystem rules. Claude Code enforces workspace-scoped permissions to constrain writes. Every change flows through an MR so reviewers see the diff and approvals still apply.

Pick regional endpoints to reduce latency and meet data-sovereignty requirements while using existing cloud agreements.

## What can Claude do?

Claude Code enables powerful CI/CD workflows that transform how you work with code:

- Create and update MRs from issue descriptions or comments
- Analyze performance regressions and propose optimizations
- Implement features directly in a branch, then open an MR
- Fix bugs and regressions identified by tests or comments
- Respond to follow-up comments to iterate on requested changes

## Setup

### Quick setup

The fastest way to get started is to add a minimal job to your `.gitlab-ci.yml` and set your API key as a masked variable.

1. **Add a masked CI/CD variable**
   - Go to **Settings** > **CI/CD** > **Variables**
   - Add `ANTHROPIC_API_KEY` (masked, protected as needed)

2. **Add a Claude job to `.gitlab-ci.yml`**

```yaml
stages:
  - ai

claude:
  stage: ai
  image: node:24-alpine3.21
  # Adjust rules to fit how you want to trigger the job:
  # - manual runs
  # - merge request events
  # - web/API triggers when a comment contains '@claude'
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    GIT_STRATEGY: fetch
  before_script:
    - apk update
    - apk add --no-cache git curl bash
    - curl -fsSL https://claude.ai/install.sh | bash
  script:
    # Optional: start a GitLab MCP server if your setup provides one
    - /bin/gitlab-mcp-server || true
    # Use AI_FLOW_* variables when invoking via web/API triggers with context payloads
    - echo "$AI_FLOW_INPUT for $AI_FLOW_CONTEXT on $AI_FLOW_EVENT"
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Review this MR and implement the requested changes'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
```

After adding the job and your `ANTHROPIC_API_KEY` variable, test by running the job manually from **CI/CD** > **Pipelines**, or trigger it from an MR to let Claude propose updates in a branch and open an MR if needed.

To run on AWS Bedrock or Google Vertex AI instead of the Claude API, see the [Using with AWS Bedrock & Google Vertex AI](https://code.claude.com/docs/en/gitlab-ci-cd#using-with-aws-bedrock--google-vertex-ai) section below for authentication and environment setup.

### Manual setup (recommended for production)

If you prefer a more controlled setup or need enterprise providers:

1. **Configure provider access**:
   - **Claude API**: Create and store `ANTHROPIC_API_KEY` as a masked CI/CD variable
   - **AWS Bedrock**: Configure GitLab > AWS OIDC and create an IAM role for Bedrock
   - **Google Vertex AI**: Configure Workload Identity Federation for GitLab > GCP
2. **Add project credentials for GitLab API operations**:
   - Use `CI_JOB_TOKEN` by default, or create a Project Access Token with `api` scope
   - Store as `GITLAB_ACCESS_TOKEN` (masked) if using a PAT
3. **Add the Claude job to `.gitlab-ci.yml`** (see examples below)
4. **(Optional) Enable mention-driven triggers**:
   - Add a project webhook for "Comments (notes)" to your event listener (if you use one)
   - Have the listener call the pipeline trigger API with variables like `AI_FLOW_INPUT` and `AI_FLOW_CONTEXT` when a comment contains `@claude`

## Example use cases

### Turn issues into MRs

In an issue comment:

```
@claude implement this feature based on the issue description
```

Claude analyzes the issue and codebase, writes changes in a branch, and opens an MR for review.

### Get implementation help

In an MR discussion:

```
@claude suggest a concrete approach to cache the results of this API call
```

Claude proposes changes, adds code with appropriate caching, and updates the MR.

### Fix bugs quickly

In an issue or MR comment:

```
@claude fix the TypeError in the user dashboard component
```

Claude locates the bug, implements a fix, and updates the branch or opens a new MR.

## Using with AWS Bedrock & Google Vertex AI

For enterprise environments, you can run Claude Code entirely on your cloud infrastructure with the same developer experience.

### AWS Bedrock Prerequisites

1. An AWS account with Amazon Bedrock access to the desired Claude models
2. GitLab configured as an OIDC identity provider in AWS IAM
3. An IAM role with Bedrock permissions and a trust policy restricted to your GitLab project/refs
4. GitLab CI/CD variables for role assumption:
   - `AWS_ROLE_TO_ASSUME` (role ARN)
   - `AWS_REGION` (Bedrock region)

### AWS Bedrock Setup Instructions

Configure AWS to allow GitLab CI jobs to assume an IAM role via OIDC (no static keys).

**Required setup:**
1. Enable Amazon Bedrock and request access to your target Claude models
2. Create an IAM OIDC provider for GitLab if not already present
3. Create an IAM role trusted by the GitLab OIDC provider, restricted to your project and protected refs
4. Attach least-privilege permissions for Bedrock invoke APIs

**Required values to store in CI/CD variables:**
- `AWS_ROLE_TO_ASSUME`
- `AWS_REGION`

Add variables in Settings > CI/CD > Variables:

```
# For AWS Bedrock:
- AWS_ROLE_TO_ASSUME
- AWS_REGION
```

### Google Vertex AI Prerequisites

1. A Google Cloud project with:
   - Vertex AI API enabled
   - Workload Identity Federation configured to trust GitLab OIDC
2. A dedicated service account with only the required Vertex AI roles
3. GitLab CI/CD variables for WIF:
   - `GCP_WORKLOAD_IDENTITY_PROVIDER` (full resource name)
   - `GCP_SERVICE_ACCOUNT` (service account email)

### Google Vertex AI Setup Instructions

Configure Google Cloud to allow GitLab CI jobs to impersonate a service account via Workload Identity Federation.

**Required setup:**
1. Enable IAM Credentials API, STS API, and Vertex AI API
2. Create a Workload Identity Pool and provider for GitLab OIDC
3. Create a dedicated service account with Vertex AI roles
4. Grant the WIF principal permission to impersonate the service account

**Required values to store in CI/CD variables:**
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`

Add variables in Settings > CI/CD > Variables:

```
# For Google Vertex AI:
- GCP_WORKLOAD_IDENTITY_PROVIDER
- GCP_SERVICE_ACCOUNT
- CLOUD_ML_REGION (for example, us-east5)
```

## Configuration examples

### Basic .gitlab-ci.yml (Claude API)

```yaml
stages:
  - ai

claude:
  stage: ai
  image: node:24-alpine3.21
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    GIT_STRATEGY: fetch
  before_script:
    - apk update
    - apk add --no-cache git curl bash
    - curl -fsSL https://claude.ai/install.sh | bash
  script:
    - /bin/gitlab-mcp-server || true
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Summarize recent changes and suggest improvements'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  # Claude Code will use ANTHROPIC_API_KEY from CI/CD variables
```

### AWS Bedrock job example (OIDC)

**Prerequisites:**
- Amazon Bedrock enabled with access to your chosen Claude model(s)
- GitLab OIDC configured in AWS with a role that trusts your GitLab project and refs
- IAM role with Bedrock permissions (least privilege recommended)

**Required CI/CD variables:**
- `AWS_ROLE_TO_ASSUME`: ARN of the IAM role for Bedrock access
- `AWS_REGION`: Bedrock region (for example, `us-west-2`)

```yaml
claude-bedrock:
  stage: ai
  image: node:24-alpine3.21
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  before_script:
    - apk add --no-cache bash curl jq git python3 py3-pip
    - pip install --no-cache-dir awscli
    - curl -fsSL https://claude.ai/install.sh | bash
    # Exchange GitLab OIDC token for AWS credentials
    - export AWS_WEB_IDENTITY_TOKEN_FILE="${CI_JOB_JWT_FILE:-/tmp/oidc_token}"
    - if [ -n "${CI_JOB_JWT_V2}" ]; then printf "%s" "$CI_JOB_JWT_V2" > "$AWS_WEB_IDENTITY_TOKEN_FILE"; fi
    - >
      aws sts assume-role-with-web-identity
      --role-arn "$AWS_ROLE_TO_ASSUME"
      --role-session-name "gitlab-claude-$(date +%s)"
      --web-identity-token "file://$AWS_WEB_IDENTITY_TOKEN_FILE"
      --duration-seconds 3600 > /tmp/aws_creds.json
    - export AWS_ACCESS_KEY_ID="$(jq -r .Credentials.AccessKeyId /tmp/aws_creds.json)"
    - export AWS_SECRET_ACCESS_KEY="$(jq -r .Credentials.SecretAccessKey /tmp/aws_creds.json)"
    - export AWS_SESSION_TOKEN="$(jq -r .Credentials.SessionToken /tmp/aws_creds.json)"
  script:
    - /bin/gitlab-mcp-server || true
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Implement the requested changes and open an MR'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  variables:
    AWS_REGION: "us-west-2"
```

Model IDs for Bedrock include region-specific prefixes (for example, `us.anthropic.claude-sonnet-4-6`). Pass the desired model via your job configuration or prompt if your workflow supports it.

### Google Vertex AI job example (Workload Identity Federation)

**Prerequisites:**
- Vertex AI API enabled in your GCP project
- Workload Identity Federation configured to trust GitLab OIDC
- A service account with Vertex AI permissions

**Required CI/CD variables:**
- `GCP_WORKLOAD_IDENTITY_PROVIDER`: Full provider resource name
- `GCP_SERVICE_ACCOUNT`: Service account email
- `CLOUD_ML_REGION`: Vertex region (for example, `us-east5`)

```yaml
claude-vertex:
  stage: ai
  image: gcr.io/google.com/cloudsdktool/google-cloud-cli:slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  before_script:
    - apt-get update && apt-get install -y git && apt-get clean
    - curl -fsSL https://claude.ai/install.sh | bash
    # Authenticate to Google Cloud via WIF (no downloaded keys)
    - >
      gcloud auth login --cred-file=<(cat <<EOF
      {
        "type": "external_account",
        "audience": "${GCP_WORKLOAD_IDENTITY_PROVIDER}",
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${GCP_SERVICE_ACCOUNT}:generateAccessToken",
        "token_url": "https://sts.googleapis.com/v1/token"
      }
      EOF
      )
    - gcloud config set project "$(gcloud projects list --format='value(projectId)' --filter="name:${CI_PROJECT_NAMESPACE}" | head -n1)" || true
  script:
    - /bin/gitlab-mcp-server || true
    - >
      CLOUD_ML_REGION="${CLOUD_ML_REGION:-us-east5}"
      claude
      -p "${AI_FLOW_INPUT:-'Review and update code as requested'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  variables:
    CLOUD_ML_REGION: "us-east5"
```

With Workload Identity Federation, you do not need to store service account keys. Use repository-specific trust conditions and least-privilege service accounts.

## Best practices

### CLAUDE.md configuration

Create a `CLAUDE.md` file at the repository root to define coding standards, review criteria, and project-specific rules. Claude reads this file during runs and follows your conventions when proposing changes.

### Security considerations

**Never commit API keys or cloud credentials to your repository**. Always use GitLab CI/CD variables:

- Add `ANTHROPIC_API_KEY` as a masked variable (and protect it if needed)
- Use provider-specific OIDC where possible (no long-lived keys)
- Limit job permissions and network egress
- Review Claude's MRs like any other contributor

### Optimizing performance

- Keep `CLAUDE.md` focused and concise
- Provide clear issue/MR descriptions to reduce iterations
- Configure sensible job timeouts to avoid runaway runs
- Cache npm and package installs in runners where possible

### CI costs

When using Claude Code with GitLab CI/CD, be aware of associated costs:

- **GitLab Runner time**: Claude runs on your GitLab runners and consumes compute minutes. See your GitLab plan's runner billing for details.
- **API costs**: Each Claude interaction consumes tokens based on prompt and response size. Token usage varies by task complexity and codebase size. See [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing) for details.
- **Cost optimization tips**:
  - Use specific `@claude` commands to reduce unnecessary turns
  - Set appropriate `max_turns` and job timeout values
  - Limit concurrency to control parallel runs

## Security and governance

- Each job runs in an isolated container with restricted network access
- Claude's changes flow through MRs so reviewers see every diff
- Branch protection and approval rules apply to AI-generated code
- Claude Code uses workspace-scoped permissions to constrain writes
- Costs remain under your control because you bring your own provider credentials

## Troubleshooting

### Claude not responding to @claude commands

- Verify your pipeline is being triggered (manually, MR event, or via a note event listener/webhook)
- Ensure CI/CD variables (`ANTHROPIC_API_KEY` or cloud provider settings) are present and unmasked
- Check that the comment contains `@claude` (not `/claude`) and that your mention trigger is configured

### Job can't write comments or open MRs

- Ensure `CI_JOB_TOKEN` has sufficient permissions for the project, or use a Project Access Token with `api` scope
- Check the `mcp__gitlab` tool is enabled in `--allowedTools`
- Confirm the job runs in the context of the MR or has enough context via `AI_FLOW_*` variables

### Authentication errors

- **For Claude API**: Confirm `ANTHROPIC_API_KEY` is valid and unexpired
- **For Bedrock/Vertex**: Verify OIDC/WIF configuration, role impersonation, and secret names; confirm region and model availability

## Advanced configuration

### Common parameters and variables

Claude Code supports these commonly used inputs:

- `prompt` / `prompt_file`: Provide instructions inline (`-p`) or via a file
- `max_turns`: Limit the number of back-and-forth iterations
- `timeout_minutes`: Limit total execution time
- `ANTHROPIC_API_KEY`: Required for the Claude API (not used for Bedrock/Vertex)
- Provider-specific environment: `AWS_REGION`, project/region vars for Vertex

Exact flags and parameters may vary by version of `@anthropic-ai/claude-code`. Run `claude --help` in your job to see supported options.

### Customizing Claude's behavior

You can guide Claude in two primary ways:

1. **CLAUDE.md**: Define coding standards, security requirements, and project conventions. Claude reads this during runs and follows your rules.
2. **Custom prompts**: Pass task-specific instructions via `prompt`/`prompt_file` in the job. Use different prompts for different jobs (for example, review, implement, refactor).
