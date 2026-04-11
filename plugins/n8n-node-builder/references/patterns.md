# Implementation Patterns

Quick-reference for all recurring patterns. Load this when generating code.

---

## Node type decision

```
Does the service push HTTP events to a URL?
  YES → Webhook Trigger (Node + webhook())
  NO  → Does it only offer "list recent" API?
          YES → Polling Trigger (INodeType + poll())
          NO  → Action Node (VersionedNodeType + execute())

Is it just sending an outbound HTTP call with no auth?
  → Webhook Sender (VersionedNodeType + simple execute())
```

## Node type → class + method

| Type | Base class | Interface | Method | `inputs` | Special description keys |
|------|-----------|-----------|--------|----------|--------------------------|
| Action | `VersionedNodeType` | `IExecuteFunctions` | `execute()` | `[Main]` | — |
| Polling trigger | `INodeType` | `IPollFunctions` | `poll()` | `[]` | `polling: true` |
| Webhook trigger | `Node` | `IWebhookFunctions` | `webhook()` | `[]` | `webhooks: [...]` |
| Webhook sender | `VersionedNodeType` | `IExecuteFunctions` | `execute()` | `[Main]` | — |

---

## VersionedNodeType entry (always use for action nodes)

```typescript
export class MyService extends VersionedNodeType {
  constructor() {
    const baseDescription: INodeTypeBaseDescription = {
      displayName: 'MyService', name: 'myService',
      icon: 'file:myService.svg', group: ['transform'],
      description: '...', defaultVersion: 1,
    };
    super({ 1: new MyServiceV1(baseDescription) }, baseDescription);
  }
}
```

## V1 action node class

> **File naming**: V1 file MUST be `MyServiceV1.ts` — NOT `MyServiceV1.node.ts`.
> `CustomDirectoryLoader` globs `**/*.node.js` and would load it as a standalone node, breaking icons.

```typescript
// MyServiceV1.ts  ← no .node suffix
export class MyServiceV1 implements INodeType {
  description: INodeTypeDescription;
  constructor(baseDescription: INodeTypeBaseDescription) {
    this.description = { ...baseDescription, ...versionDescription, usableAsTool: true };
  }
  methods = { listSearch, loadOptions };  // only if needed
  async execute(this: IExecuteFunctions) { return await router.call(this); }
}
```

---

## Router pattern

```typescript
export async function router(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
  const resource = this.getNodeParameter('resource', 0) as string;
  const operation = this.getNodeParameter('operation', 0) as string;
  let returnData: INodeExecutionData[] = [];
  switch (resource) {
    case 'record':
      returnData = await (record as any)[operation].execute.call(this, this.getInputData());
      break;
    default:
      throw new NodeOperationError(this.getNode(), `Unknown resource: "${resource}"`);
  }
  return [returnData];
}
```

## Operation execute loop (standard)

```typescript
for (let i = 0; i < items.length; i++) {
  try {
    // ... get params, make request ...
    returnData.push(...this.helpers.constructExecutionMetaData(
      this.helpers.returnJsonArray(responseData), { itemData: { item: i } },
    ));
  } catch (error) {
    if (this.continueOnFail()) {
      returnData.push({ json: { error: error.message }, pairedItem: { item: i } });
      continue;
    }
    throw error;
  }
}
```

---

## Pagination patterns

**Offset-based (Airtable):**
```typescript
let offset: string | undefined;
do {
  if (offset) query.offset = offset;
  const response = await apiRequest.call(this, 'GET', endpoint, {}, query);
  returnData.push(...response.records);
  offset = response.offset;
} while (offset);
```

**Cursor-based:**
```typescript
let cursor: string | undefined;
do {
  if (cursor) query.after = cursor;
  const response = await apiRequest.call(this, 'GET', endpoint, {}, query);
  returnData.push(...(response.data ?? []));
  cursor = response.meta?.next_cursor;
} while (cursor);
```

**Page-based:**
```typescript
let page = 1;
while (true) {
  const response = await apiRequest.call(this, 'GET', endpoint, {}, { page, per_page: 100 });
  returnData.push(...(response.data ?? []));
  if (!response.meta?.has_next_page) break;
  page++;
}
```

---

## Credential patterns

**API key → header:**
```typescript
authenticate: IAuthenticateGeneric = {
  type: 'generic',
  properties: { headers: { 'Authorization': '=Bearer {{$credentials.apiKey}}' } },
};
test: ICredentialTestRequest = { request: { baseURL: '...', url: '/me', method: 'GET' } };
```

**API key → query param:**
```typescript
authenticate: IAuthenticateGeneric = {
  type: 'generic',
  properties: { qs: { 'api_key': '={{$credentials.apiKey}}' } },
};
```

**OAuth2:**
```typescript
export class MyServiceOAuth2Api implements ICredentialType {
  name = 'myServiceOAuth2Api';
  extends = ['oAuth2Api'];
  properties: INodeProperties[] = [
    { name: 'grantType',      type: 'hidden', default: 'authorizationCode' },
    { name: 'authUrl',        type: 'hidden', default: 'https://...' },
    { name: 'accessTokenUrl', type: 'hidden', default: 'https://...' },
    { name: 'scope',          type: 'hidden', default: 'read write' },
    { name: 'authentication', type: 'hidden', default: 'header' },
  ];
}
```

---

## Webhook patterns

**Simple webhook (T24):** one entry, POST only, header auth
```typescript
webhooks: [{ name: 'default', httpMethod: 'POST', responseMode: 'onReceived', path: 'webhook' }]
```

**Dual-webhook (T25 — Facebook/Meta/GitHub):** GET for ownership challenge + POST for events
```typescript
webhooks: [
  { name: 'setup',   httpMethod: 'GET',  responseMode: 'onReceived', path: 'webhook' },
  { name: 'default', httpMethod: 'POST', responseMode: 'onReceived', path: 'webhook' },
]
// dispatch: if (this.getWebhookName() === 'setup') { ... handle challenge ... }
```

**IWebhookResponseData shapes:**
```typescript
return { workflowData: [[item]] };          // trigger workflow
return { noWebhookResponse: true };         // suppress response (after res.end())
return {};                                  // silent reject — no workflow, no error
return { webhookResponse: 'ok', workflowData: [[item]] }; // custom body + trigger
```

**HMAC verification:**
```typescript
import { createHmac, timingSafeEqual } from 'crypto';
const computed = createHmac('sha256', secret).update(req.rawBody).digest('hex');
const received = (header as string)?.replace('sha256=', '') ?? '';
if (!timingSafeEqual(Buffer.from(computed), Buffer.from(received))) return {};
```

**Webhook registration:**
```typescript
webhookMethods = {
  default: {
    async checkExists(this: IHookFunctions) { ... },
    async create(this: IHookFunctions) {
      const url = this.getNodeWebhookUrl('default') as string;
      const r = await apiRequest.call(this, 'POST', '/webhooks', { url, verify_token: this.getNode().id });
      this.getWorkflowStaticData('node').webhookId = r.id;
      return true;
    },
    async delete(this: IHookFunctions) {
      const d = this.getWorkflowStaticData('node');
      if (d.webhookId) { await apiRequest.call(this, 'DELETE', `/webhooks/${d.webhookId}`); delete d.webhookId; }
      return true;
    },
  },
};
```

---

## listSearch (resourceLocator dropdowns)

```typescript
export async function searchItems(
  this: ILoadOptionsFunctions, filter?: string, paginationToken?: string,
): Promise<INodeListSearchResult> {
  const qs: IDataObject = {};
  if (paginationToken) qs.offset = paginationToken;
  if (filter) qs.search = filter;
  const response = await apiRequest.call(this, 'GET', '/items', {}, qs);
  return {
    results: (response.items ?? []).map((i: IDataObject) => ({ name: i.name as string, value: i.id as string })),
    paginationToken: response.offset ?? undefined,
  };
}
```

## Rate limiting (Discord-style)

```typescript
const remaining = Number(response.headers['x-ratelimit-remaining']);
const resetAfter = Number(response.headers['x-ratelimit-reset-after']) * 1000;
if (remaining === 0) await new Promise(r => setTimeout(r, resetAfter));
else await new Promise(r => setTimeout(r, 20));  // 50 req/s global
```

## 429 retry loop

```typescript
let maxTries = 5;
do {
  try { response = await this.helpers.request(opts); break; }
  catch (error) {
    if (error.statusCode === 429) {
      await new Promise(r => setTimeout(r, (error.response?.headers['retry-after'] ?? 1) * 1000));
      continue;
    }
    throw error;
  }
} while (--maxTries);
if (maxTries <= 0) throw new NodeApiError(this.getNode(), { error: 'Max retries reached' });
```

## Batch processing (10 at a time)

```typescript
const batchSize = 10;
for (let j = 0; j < Math.ceil(records.length / batchSize); j++) {
  const batch = records.slice(j * batchSize, (j + 1) * batchSize);
  const r = await apiRequest.call(this, 'PATCH', endpoint, { records: batch });
  results.push(...(r.records as IDataObject[]));
}
```

## Binary file download

```typescript
const buffer = await apiRequest.call(this, 'GET', '', {}, {}, fileUrl, { json: false, encoding: null });
item.binary = { data: await this.helpers.prepareBinaryData(Buffer.from(buffer as string), fileName, mimeType) };
```

## Multiple outputs

```typescript
// description:
outputs: [NodeConnectionTypes.Main, NodeConnectionTypes.Main],
outputNames: ['Matched', 'Unmatched'],
// execute():
return [matchedItems, unmatchedItems];
```

## displayOptions

```typescript
displayOptions: { show: { resource: ['record'], operation: ['create'] } }
displayOptions: { hide: { returnAll: [true] } }
displayOptions: { show: { operation: ['create', 'update'] } }  // OR within array
```

## package.json n8n section

```json
"n8n": {
  "n8nNodesApiVersion": 1,
  "strict": true,
  "credentials": ["dist/credentials/MyServiceApi.credentials.js"],
  "nodes": ["dist/nodes/MyService/MyService.node.js"]
}
```
