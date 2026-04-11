# Templates: Credentials

Load this when generating credential files.
All templates use `{{PLACEHOLDER}}` substitution — see SKILL.md for the full table.

---

## T3: Credential — API Key (header)

Sourced from: `n8n-nodes-starter-master/credentials/GithubIssuesApi.credentials.ts`

```typescript
// credentials/{{CREDENTIAL_NAME}}.credentials.ts
import type {
  IAuthenticateGeneric,
  Icon,
  ICredentialTestRequest,
  ICredentialType,
  INodeProperties,
} from 'n8n-workflow';

export class {{CREDENTIAL_NAME}} implements ICredentialType {
  name = '{{service}}Api';

  displayName = '{{SERVICE}} API';

  icon: Icon = { light: 'file:{{service-slug}}.svg', dark: 'file:{{service-slug}}.dark.svg' };

  documentationUrl = '{{DOCS_URL}}';

  properties: INodeProperties[] = [
    {
      displayName: '{{TOKEN_DISPLAY_NAME}}',  // e.g. 'API Key', 'Access Token', 'API Token'
      name: '{{tokenFieldName}}',             // e.g. 'apiKey', 'accessToken', 'apiToken'
      type: 'string',
      typeOptions: { password: true },
      default: '',
    },
  ];

  authenticate: IAuthenticateGeneric = {
    type: 'generic',
    properties: {
      headers: {
        // Common patterns — pick one and delete the rest:
        // Bearer token:    'Authorization': '=Bearer {{$credentials?.{{tokenFieldName}}}}'
        // Token prefix:    'Authorization': '=token {{$credentials?.{{tokenFieldName}}}}'
        // Custom header:   'X-API-Key': '={{$credentials?.{{tokenFieldName}}}}'
        Authorization: '=Bearer {{$credentials?.{{tokenFieldName}}}}',
      },
    },
  };

  test: ICredentialTestRequest = {
    request: {
      baseURL: '{{BASE_URL}}',
      url: '{{TEST_ENDPOINT}}',  // cheapest read-only endpoint, e.g. /me or /status
      method: 'GET',
    },
  };
}
```

## T4: Credential — OAuth2

Sourced from: `n8n-nodes-starter-master/credentials/GithubIssuesOAuth2Api.credentials.ts`

```typescript
// credentials/{{CREDENTIAL_NAME}}OAuth2Api.credentials.ts
import type { Icon, ICredentialType, INodeProperties } from 'n8n-workflow';

export class {{CREDENTIAL_NAME}}OAuth2Api implements ICredentialType {
  name = '{{service}}OAuth2Api';

  extends = ['oAuth2Api'];

  displayName = '{{SERVICE}} OAuth2 API';

  icon: Icon = { light: 'file:{{service-slug}}.svg', dark: 'file:{{service-slug}}.dark.svg' };

  documentationUrl = '{{DOCS_URL}}';

  properties: INodeProperties[] = [
    {
      displayName: 'Grant Type',
      name: 'grantType',
      type: 'hidden',
      default: 'authorizationCode',
    },
    {
      displayName: 'Authorization URL',
      name: 'authUrl',
      type: 'hidden',
      default: '{{AUTH_URL}}',
      required: true,
    },
    {
      displayName: 'Access Token URL',
      name: 'accessTokenUrl',
      type: 'hidden',
      default: '{{TOKEN_URL}}',
      required: true,
    },
    {
      displayName: 'Scope',
      name: 'scope',
      type: 'hidden',
      default: '{{SCOPE}}',
    },
    {
      displayName: 'Auth URI Query Parameters',
      name: 'authQueryParameters',
      type: 'hidden',
      default: '',
    },
    {
      displayName: 'Authentication',
      name: 'authentication',
      type: 'hidden',
      default: 'header',
    },
  ];
}
```
