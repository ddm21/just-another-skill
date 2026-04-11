# Best Practices & Common Error Fixes

Real-world patterns, fixes, and anti-patterns discovered building n8n community nodes against REST APIs. Reference this when debugging runtime errors or designing node operations.

---

## API Response Unwrapping — The #1 Runtime Crash

### The error
```
TypeError: Spread syntax requires ...iterable[Symbol.iterator] to be a function
```

### Root cause
Many APIs wrap paginated responses under a `data` key:
```json
{ "status": "success", "data": { "items": [...], "total": 50, "page": 1 } }
```

If your transport/pagination helper does `responseData[itemsKey]` directly, it looks at the **top level** of the response — where `itemsKey` (e.g., `'items'`) doesn't exist. It falls back to `responseData.data`, which is an **object** (not an array). Trying to spread an object (`...items`) causes the `Symbol.iterator` crash.

### Fix — Always unwrap `response.data` first
```typescript
// ❌ WRONG — looks at top level, misses nested data
const items = responseData[itemsKey] ?? responseData.data ?? responseData ?? [];

// ✅ CORRECT — unwrap .data first, then look for itemsKey
const inner = responseData?.data ?? responseData ?? {};
const items = inner[itemsKey] ?? inner ?? [];
if (!Array.isArray(items)) break; // safety guard
```

Apply this pattern to **both** pagination helpers:
- **Page-based** (`apiRequestAllItemsPages`): also fix `total` extraction — it's at `inner.total`, not `responseData.total`
- **Cursor-based** (`apiRequestAllItemsCursor`): also fix `searchAfter` extraction — check `inner.searchAfter` first

### Full corrected page-based pagination helper
```typescript
export async function apiRequestAllItemsPages(
  this: IExecuteFunctions | ILoadOptionsFunctions | IPollFunctions,
  method: IHttpRequestMethods,
  endpoint: string,
  body: IDataObject = {},
  query: IDataObject = {},
  itemsKey = 'data',
): Promise<IDataObject[]> {
  const returnData: IDataObject[] = [];
  query.limit = query.limit ?? 100;
  let page = 1;

  do {
    query.page = page;
    const responseData = await apiRequest.call(this, method, endpoint, body, query);
    const inner = responseData?.data ?? responseData ?? {};
    const items: IDataObject[] = inner[itemsKey] ?? inner ?? [];
    if (!Array.isArray(items)) break;
    returnData.push(...items);
    const total: number = inner.total ?? responseData.total ?? 0;
    const limit = query.limit as number;
    if (items.length < limit || (total > 0 && returnData.length >= total)) break;
    page++;
  } while (true);

  return returnData;
}
```

### Full corrected cursor-based pagination helper
```typescript
export async function apiRequestAllItemsCursor(
  this: IExecuteFunctions | ILoadOptionsFunctions | IPollFunctions,
  method: IHttpRequestMethods,
  endpoint: string,
  body: IDataObject = {},
  query: IDataObject = {},
  itemsKey = 'data',
): Promise<IDataObject[]> {
  const returnData: IDataObject[] = [];
  query.limit = query.limit ?? 100;
  let searchAfter: string | undefined;

  do {
    if (searchAfter) query.searchAfter = searchAfter;
    const responseData = await apiRequest.call(this, method, endpoint, body, query);
    const inner = responseData?.data ?? responseData ?? {};
    const items: IDataObject[] = inner[itemsKey] ?? inner ?? [];
    if (!Array.isArray(items)) break;
    returnData.push(...items);
    searchAfter = inner.searchAfter ?? responseData.searchAfter ?? responseData.meta?.searchAfter ?? undefined;
    if (!searchAfter || items.length < (query.limit as number)) break;
  } while (true);

  return returnData;
}
```

---

## GetAll operations — Missing `page` parameter

### The error
Empty results when `returnAll` is off (limit is set), even though data exists.

### Root cause
Some APIs require both `page` AND `limit` query params. If you only send `limit` without `page=1`, the API may return empty results.

### Fix
Always send `page=1` in the non-returnAll path:
```typescript
if (returnAll) {
  responseData = await apiRequestAllItemsPages.call(this, 'GET', endpoint, {}, qs, 'items');
} else {
  const limit = this.getNodeParameter('limit', i) as number;
  qs.limit = limit;
  qs.page = 1; // ← Always include this
  const response = await apiRequest.call(this, 'GET', endpoint, {}, qs);
  const data = response?.data ?? response ?? {};
  responseData = (data.items ?? data ?? []) as IDataObject[];
  if (!Array.isArray(responseData)) responseData = [];
  responseData = responseData.slice(0, limit); // ← Client-side safety
}
```

---

## Client-side limit enforcement

### When to use
Some API endpoints (especially resource-scoped ones like `GET /contacts/:id/notes`) **ignore** pagination parameters entirely and always return all items. The limit the user sets in n8n has no effect.

### Fix — Sort + slice client-side
```typescript
// Sort newest first, then slice to limit
responseData.sort((a, b) => {
  const dateA = new Date(a.createdAt as string).getTime();
  const dateB = new Date(b.createdAt as string).getTime();
  return dateB - dateA;
});
responseData = responseData.slice(0, limit);
```

**When to apply:** Always add `slice(0, limit)` as a safety net in the non-returnAll path, even if the API claims to support pagination. It's harmless when the API works correctly and saves you when it doesn't.

---

## Scope-specific features — Hide unsupported fields

### Problem
An API has two scopes for the same resource (e.g., "Contact Notes" vs "Workspace Notes"), but only one scope supports certain query parameters (like `search`).

### Fix
Use `displayOptions` to show the field only for the scope that supports it:
```typescript
{
  displayName: 'Additional Fields',
  name: 'additionalFields',
  type: 'collection',
  // Only show for workspace scope — contact scope doesn't support search
  displayOptions: { show: { resource: ['note'], operation: ['getAll'], scope: ['workspace'] } },
  options: [
    { displayName: 'Search', name: 'search', type: 'string', default: '' },
  ],
}
```

In the execute function, only read `additionalFields` when the scope matches:
```typescript
if (scope === 'workspace') {
  const additionalFields = this.getNodeParameter('additionalFields', i) as IDataObject;
  Object.assign(qs, additionalFields);
}
```

---

## loadOptions for external/non-standard endpoints

### Problem
The API has an endpoint that doesn't share the same base URL as other endpoints. `apiRequest` always prepends the base URL.

### Fix — Use the URI override parameter
```typescript
async getWorkspaceUsers(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
  // This endpoint is at https://api.example.com/accounts (no /api prefix)
  const response = await apiRequest.call(
    this, 'GET', '', {}, {}, 'https://api.example.com/accounts',
  );
  // ...
}
```

The `apiRequest` function should accept an optional `uri` parameter that overrides the default `BASE_URL + endpoint` construction:
```typescript
export async function apiRequest(
  this: ...,
  method: IHttpRequestMethods,
  endpoint: string,
  body: IDataObject = {},
  query: IDataObject = {},
  uri?: string,        // ← Override full URL
  option: IDataObject = {},
): Promise<any> {
  const options: IRequestOptions = {
    uri: uri ?? `${BASE_URL}${endpoint}`, // ← Use override if provided
    // ...
  };
}
```

---

## Tag/label APIs — name vs ID confusion

### Problem
Some APIs use the resource **name** (e.g., `"vip"`) to reference items, not the **_id**. When building a dropdown via loadOptions, if you set `value: item._id`, the API call fails silently or applies the wrong item.

### Fix
Read the API docs carefully for what identifier the endpoint expects. Common patterns:
- **Update/delete endpoints** → usually take `_id` in the URL path
- **Association endpoints** (e.g., "add tag to contact") → often take `name` in the request body

```typescript
// For association endpoints that expect tag names
async getWorkspaceTags(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
  // ...
  return tags.map((t) => ({
    name: `${t.label} (${t.color})`,
    value: t.name,  // ← API expects name, not _id
  }));
}
```

---

## Shared color constants

### Problem
Multiple operations need the same color picker (tags, select/multiselect options, etc.). Duplicating the 26-color array everywhere is error-prone.

### Fix — Create a shared constants file
```typescript
// v1/colors.ts
import type { INodePropertyOptions } from 'n8n-workflow';

export const TAG_COLORS = [
  'amber', 'blue', 'bronze', 'brown', 'crimson', 'cyan', 'gold', 'grass',
  'gray', 'green', 'indigo', 'iris', 'jade', 'lime', 'mint', 'orange',
  'pink', 'plum', 'purple', 'red', 'ruby', 'sky', 'teal', 'tomato',
  'violet', 'yellow',
] as const;

export const COLOR_OPTIONS: INodePropertyOptions[] = [
  { name: 'Random', value: 'random', description: 'Automatically pick a random color' },
  ...TAG_COLORS.map((c) => ({
    name: c.charAt(0).toUpperCase() + c.slice(1),
    value: c,
  })),
];

export function resolveColor(color: string): string {
  if (!color || color === 'random') {
    return TAG_COLORS[Math.floor(Math.random() * TAG_COLORS.length)];
  }
  return color;
}
```

Usage in operations:
```typescript
import { COLOR_OPTIONS, resolveColor } from '../../colors';

// In description — use shared options with "Random" as default
{ type: 'options', options: COLOR_OPTIONS, default: 'random' }

// In execute — resolve before sending to API
color: resolveColor(this.getNodeParameter('color', i) as string),
```

---

## Auto-generate internal names from labels

### Problem
APIs often require both a human-readable `label` and a machine-friendly internal `name` (e.g., `"My Event" → "my_event"`). Exposing both to the user is unnecessary complexity.

### Fix — Auto-generate in the execute function
```typescript
function generateInternalName(label: string): string {
  return label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '');
}

// In execute:
const label = this.getNodeParameter('name', i) as string;
body.label = label;
body.name = generateInternalName(label);
```

**When to apply:** Any API that takes both `label` and `name` where `name` is a slug-like identifier. Don't add an "Internal Name" field to the UI unless the API requires specific naming that can't be derived.

---

## Dynamic detection of built-in vs custom properties

### Problem
APIs return a mix of built-in (system) and custom properties. Built-in properties are sent as-is (`firstName`), custom properties need a prefix (`customProperties.firstName`). Hardcoding a list of built-in names is fragile.

### Fix — Use API metadata to detect dynamically
```typescript
// ❌ WRONG — hardcoded, breaks when API adds new system properties
const BUILT_IN = new Set(['firstName', 'lastName', 'email']);
const value = BUILT_IN.has(p.name) ? p.name : `customProperties.${p.name}`;

// ✅ CORRECT — detect from API response metadata
const isBuiltIn = p.createdBy?.type === 'system';
const value = isBuiltIn ? p.name : `customProperties.${p.name}`;
```

**When to apply:** Any API that distinguishes between system and user-defined fields. Look for metadata like `createdBy.type`, `isSystem`, `origin`, or `source` in the API response.

---

## Nested API response structures

### Problem
Some API endpoints return deeply nested data that doesn't match the expected pattern:
```json
{ "data": { "pipelines": { "pipelines": [...] } } }
```

### Fix — Use defensive fallback chains
```typescript
// Handle varying nesting depths
const pipelines =
  response?.data?.pipelines?.pipelines ??  // doubly nested
  response?.data?.pipelines ??              // singly nested (array)
  [];
```

**Best practice:** When first integrating an API, always log the raw response structure to understand nesting. Don't assume `response.data.items` — verify with a test call or browser network tab.

---

## V1 file naming — NEVER use `.node.ts` suffix on version files

### The error
Node icon disappears, node loads without `baseDescription`, or duplicate node entries appear in the palette.

### Root cause
n8n's `CustomDirectoryLoader` globs `**/*.node.js` and loads every match as a standalone node. If your V1 class file is named `SwipeOneV1.node.ts`, it gets compiled to `SwipeOneV1.node.js` and loaded independently — without the icon and baseDescription from the versioned entry point.

### Fix
- Entry point: `nodes/Service/Service.node.ts` — **ONLY** this file gets `.node.ts`
- Version class: `nodes/Service/v1/ServiceV1.ts` — **NO** `.node.ts` suffix
- Verify after build: `find dist -name '*.node.js'` should return ONLY the entry point(s)

---

## Icon property — only in baseDescription

### The error
Node icon is broken (shows placeholder) even though the SVG file exists.

### Root cause
n8n resolves `file:xxx.svg` relative to the file that defines `icon`. If you set `icon` in `versionDescription.ts`, it resolves relative to `v1/actions/` instead of the entry point directory where the SVG lives.

### Fix
```typescript
// ✅ Set icon ONLY in the VersionedNodeType entry (Service.node.ts)
const baseDescription = {
  displayName: 'Service',
  name: 'service',
  icon: 'file:service.svg',  // ← resolved relative to THIS file
  // ...
};

// ❌ NEVER set icon in versionDescription.ts
export const versionDescription = {
  // icon: 'file:service.svg',  ← DELETE THIS — causes wrong path resolution
};
```

Place the SVG file next to the entry `.node.ts` file, not in `v1/` or `icons/`.

---

## Unofficial/undocumented API endpoints

### When you need them
Sometimes core features (like pipelines, deals) aren't in the official API docs but are used by the service's own web UI. You can discover them from the browser's Network tab.

### Best practices
1. **Verify auth works the same way** — unofficial endpoints usually accept the same API key/token
2. **Document in decisions log** that these are unofficial — they may break without notice
3. **Test thoroughly** — undocumented endpoints often have inconsistent response formats
4. **Add fallback chains** for response extraction — the format may differ from documented endpoints
5. **Note any missing endpoints** — e.g., "Get All Deals" may not exist even though individual CRUD does

---

## CI/CD Setup — Node Version & ESLint Cloud Compliance

### Problem 1: CI fails with `isolated-vm` compilation error
```
npm error ../src/isolate/platform_delegate.h:15:77: error: 'SourceLocation' in namespace 'v8' does not name a type
```

### Root cause
`n8n-workflow` depends on `@n8n/ai-utilities` → `isolated-vm`, which requires **Node >= 22** to compile native C++ modules. The V8 API in Node 20 lacks `v8::SourceLocation`.

### Fix — Use Node 22 in all CI workflows
```yaml
# .github/workflows/ci.yml
- uses: actions/setup-node@v4
  with: { node-version: '22', cache: 'npm' }  # ← NOT '20'
```
Apply to BOTH `ci.yml` and `publish.yml`. This is required as of n8n-workflow v1.x+ (2025+).

---

### Problem 2: CI fails with "eslint.config.mjs not found"
```
Strict mode violation: eslint.config.mjs not found. Expected default configuration.
```

### Root cause
n8n's linter (`n8n-node lint`) requires an `eslint.config.mjs` file when cloud support/strict mode is enabled. Without it, `npm run lint` exits with code 1.

### Fix — Generate the default config
```bash
npx n8n-node cloud-support enable
```
This creates `eslint.config.mjs` and enables strict mode in `package.json`. Commit both files.

The generated config is minimal:
```javascript
import { config } from '@n8n/node-cli/eslint';
export default config;
```

---

### Problem 3: 100+ ESLint errors after enabling cloud compliance

After enabling cloud support, expect many errors. Here's the fix strategy:

**Step 1 — Auto-fix (handles ~75% of errors):**
```bash
npx eslint --fix "nodes/**/*.ts" "credentials/**/*.ts"
```
This fixes: title case display names, missing descriptions for returnAll/limit, dynamic options hint text, alphabetized option lists.

**Step 2 — Manual fixes for remaining errors:**

| Error | Fix |
|-------|-----|
| `icon-validation` on credentials | Add `icon = 'file:service.svg' as const` to credential class, copy SVG to `credentials/` folder |
| `node-param-collection-type-unsorted-items` | Alphabetize `options` array in `collection` type fields by `name` |
| `node-param-options-type-unsorted-items` (non-autofix) | Alphabetize `options` array in `options` type fields by `name` |
| `no-useless-catch` | Remove try/catch that only re-throws |
| `no-explicit-any` | Type your modules/imports properly (see router typing below) |
| `no-deprecated-workflow-functions` | Migrate transport (see below) |
| `no-constant-condition` (`do {} while (true)`) | Change to `for (;;)` |
| `node-filename-against-convention` on versionDescription.ts | Add `/* eslint-disable n8n-nodes-base/node-filename-against-convention */` — do NOT rename (breaks V1 pattern) |

---

## Transport Migration — requestWithAuthentication → httpRequestWithAuthentication

### The lint errors
```
'IRequestOptions' is deprecated. Use 'IHttpRequestOptions' instead
'requestWithAuthentication' is deprecated. Use 'httpRequestWithAuthentication' instead
```

### Fix — Migrate the entire transport layer

**Before (deprecated):**
```typescript
import type { IRequestOptions } from 'n8n-workflow';

const options: IRequestOptions = {
  headers: { 'Content-Type': 'application/json' },
  method,
  body,
  qs: query,
  uri: uri ?? `${BASE_URL}${endpoint}`,
  json: true,
};
return await this.helpers.requestWithAuthentication.call(this, 'swipeOneApi', options);
```

**After (current):**
```typescript
import type { IHttpRequestOptions } from 'n8n-workflow';

const options: IHttpRequestOptions = {
  method,
  url: uri ?? `${BASE_URL}${endpoint}`,  // ← 'url' not 'uri'
  body,
  qs: query,
  json: true,
  // No 'headers' needed — httpRequestWithAuthentication handles Content-Type
};
return await this.helpers.httpRequestWithAuthentication.call(this, 'swipeOneApi', options);
```

**Key differences:**
- `uri` → `url`
- `IRequestOptions` → `IHttpRequestOptions`
- `requestWithAuthentication` → `httpRequestWithAuthentication`
- No manual `headers: { 'Content-Type': 'application/json' }` needed
- Return type stays `Promise<any>` (add `// eslint-disable-next-line @typescript-eslint/no-explicit-any`)

**IMPORTANT:** Test all API calls after migration. The auth injection behavior is the same, but error handling may differ slightly.

---

## Router Typing — Avoid `any` casts

### The lint error
```
Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any
```

### Fix — Define a resource module interface
```typescript
import type { IExecuteFunctions, INodeExecutionData, INodeProperties } from 'n8n-workflow';

interface ResourceModule {
  description: INodeProperties[];
  execute: (
    this: IExecuteFunctions,
    items: INodeExecutionData[],
  ) => Promise<INodeExecutionData[]>;
}

// Type your resource map
const resources: Record<string, ResourceModule> = {
  contact: contactOperations,
  note: noteOperations,
  // ...
};

// Lookup without any casts
const resource = this.getNodeParameter('resource', 0) as string;
const operation = this.getNodeParameter('operation', 0) as string;
const module = resources[resource];
return await module.execute.call(this, items);
```

---

## resourceLocator — Searchable Dropdowns for ID Fields

### When to use
Any field that takes a raw ID string (MongoDB ObjectID, UUID, etc.) should be a `resourceLocator` if the API has a list/search endpoint for that resource. This gives users two modes:
- **"From List"** — searchable dropdown that queries the API
- **"By ID"** — plain text input for power users and expressions

### TypeScript type for listSearch results
```typescript
// ❌ WRONG — this type doesn't exist
import type { IListSearchItems } from 'n8n-workflow';

// ✅ CORRECT — the actual type name
import type { INodeListSearchItems, INodeListSearchResult } from 'n8n-workflow';
```

### Property definition
```typescript
{
  displayName: 'Contact',  // ← NOT 'Contact ID'
  name: 'contactId',
  type: 'resourceLocator',
  default: { mode: 'list', value: '' },
  required: true,
  modes: [
    {
      displayName: 'From List',
      name: 'list',
      type: 'list',
      typeOptions: { searchListMethod: 'searchContacts', searchable: true },
    },
    {
      displayName: 'By ID',
      name: 'id',
      type: 'string',
      placeholder: 'e.g. 507f1f77bcf86cd799439011',
    },
  ],
}
```

For resources with **no list API** (e.g., deals with no getAll endpoint), use ID-only mode:
```typescript
{
  displayName: 'Deal',
  name: 'dealId',
  type: 'resourceLocator',
  default: { mode: 'id', value: '' },  // ← default to 'id' mode
  modes: [
    { displayName: 'By ID', name: 'id', type: 'string', placeholder: '...' },
  ],
}
```

### listSearch method pattern
```typescript
methods = {
  listSearch: {
    async searchContacts(
      this: ILoadOptionsFunctions,
      filter?: string,
      paginationToken?: string,
    ): Promise<INodeListSearchResult> {
      const credentials = await this.getCredentials('myApi');
      const query: IDataObject = { limit: 20 };
      if (filter) query.searchText = filter;
      if (paginationToken) query.searchAfter = paginationToken;

      const response = await apiRequest.call(this, 'GET', '/contacts', {}, query);
      const items = response?.data?.contacts ?? [];

      const results: INodeListSearchItems[] = items.map((c: IDataObject) => ({
        name: `${c.firstName} ${c.lastName} (${c.email})`,
        value: c._id as string,
        url: '',  // ← required field, can be empty
      }));

      return {
        results,
        paginationToken: items.length >= 20 ? response.data.searchAfter : undefined,
      };
    },
  },
  loadOptions: { /* existing */ },
};
```

### Extracting the value — TWO different patterns

**Top-level resourceLocator field:**
```typescript
// extractValue: true unwraps the resourceLocator object to get the raw string
const contactId = this.getNodeParameter('contactId', i, undefined, {
  extractValue: true,
}) as string;
```

**resourceLocator inside a collection (e.g., additionalFields):**
```typescript
// extractValue does NOT work here — the collection returns the raw RL object
const additionalFields = this.getNodeParameter('additionalFields', i) as IDataObject;
if (additionalFields.contactId) {
  const raw = additionalFields.contactId as IDataObject;
  additionalFields.contactId = (raw.value ?? raw) as string;
}
```

**Why the difference:** `getNodeParameter` with `extractValue` only works on direct parameter reads. When a resourceLocator is nested inside a `collection`, it comes as an object `{ __rl: true, mode: 'list', value: 'the-id' }` that you must unwrap manually.

### For APIs with no search — client-side filtering
```typescript
async searchTasks(
  this: ILoadOptionsFunctions,
  filter?: string,
): Promise<INodeListSearchResult> {
  // Fetch all (API has no search param)
  const response = await apiRequest.call(this, 'GET', '/tasks', {}, { limit: 100 });
  const tasks = response?.data?.tasks ?? [];
  // Filter client-side
  const filtered = filter
    ? tasks.filter((t: IDataObject) =>
        ((t.name as string) || '').toLowerCase().includes(filter.toLowerCase()))
    : tasks;
  return {
    results: filtered.map((t: IDataObject) => ({
      name: (t.name as string) || (t._id as string),
      value: t._id as string,
      url: '',
    })),
  };
}
```

---

## Credential Icon — Required for Cloud Compliance

### The lint error
```
Node/Credential class must have an icon property defined  @n8n/community-nodes/icon-validation
```

### Fix
Add an `icon` property to the credential class AND copy the SVG to the `credentials/` folder:
```typescript
export class MyApiCredentials implements ICredentialType {
  name = 'myApi';
  displayName = 'My API';
  icon = 'file:myservice.svg' as const;  // ← resolves relative to credentials/ folder
  // ...
}
```

The SVG must be in `credentials/myservice.svg` (next to the credential `.ts` file), not in the `nodes/` folder.

---

## Rich-text / JSON content in listSearch display names

### Problem
Your listSearch method calls `.substring()` or other string methods on a field the API returns as a JSON object (e.g., Tiptap/ProseMirror rich-text), causing:
```
TypeError: (n.content || "").substring is not a function
```

### Root cause
The API docs may say a field is a `string`, but the actual API returns it as a nested JSON object (rich-text structure). Calling string methods on an object crashes.

### Fix — Recursive text extraction with type guards
```typescript
function extractText(node: unknown): string {
  if (typeof node === 'string') return node;
  if (!node || typeof node !== 'object') return '';
  const n = node as Record<string, unknown>;
  if (n.text && typeof n.text === 'string') return n.text;
  if (Array.isArray(n.content)) {
    return (n.content as unknown[]).map(extractText).join(' ').trim();
  }
  return '';
}

// In listSearch:
const preview = typeof item.content === 'string'
  ? item.content.substring(0, 80)
  : extractText(item.content).substring(0, 80);
```

**When to apply:** Any listSearch or loadOptions that displays content/description fields. Always use `typeof` checks before calling string methods on API response fields — never trust the API docs about field types.

---

## Multi-resource aggregation in listSearch

### Problem
The API has no "get all" endpoint for a resource, but data can be fetched per sub-resource (e.g., deals exist per stage, not globally). Your listSearch needs to show all items across all sub-resources.

### Fix — Iterate parent resources and aggregate
```typescript
async searchDeals(
  this: ILoadOptionsFunctions,
  filter?: string,
): Promise<INodeListSearchResult> {
  const credentials = await this.getCredentials('myApi');

  // 1. Get all parent resources (pipelines)
  const pipelines = await apiRequest.call(this, 'GET', '/pipelines');

  // 2. Iterate each parent's children (stages) and collect items
  const allDeals: IDataObject[] = [];
  for (const pipeline of pipelines) {
    for (const stage of (pipeline.stages as IDataObject[])) {
      const deals = await apiRequest.call(this, 'GET', `/stages/${stage._id}/deals`);
      // Enrich each item with parent context for display
      for (const deal of deals) {
        deal._pipelineName = pipeline.name;
        deal._stageName = stage.name;
      }
      allDeals.push(...deals);
    }
  }

  // 3. Client-side filter
  const filtered = filter
    ? allDeals.filter((d) => ((d.name as string) || '').toLowerCase().includes(filter.toLowerCase()))
    : allDeals;

  // 4. Rich display name with context
  return {
    results: filtered.map((d) => ({
      name: `${d.name} — ${d._pipelineName} / ${d._stageName}`,
      value: d._id as string,
      url: '',
    })),
  };
}
```

**When to apply:** When the API scatters items across sub-resources with no global list endpoint. Be mindful of API call count — this pattern makes N×M calls (pipelines × stages). Cache or limit when possible.

---

## Anti-patterns to avoid

### 1. Don't mix create + associate in one API call
If the API's "add tags to contact" endpoint accepts both existing tag names AND new tag objects, **don't expose both in the same UI**. It's confusing and error-prone. Use separate operations: "Create Tag" + "Add to Contact".

### 2. Don't trust API pagination claims
Always add `Array.isArray()` guards and `slice(0, limit)` safety nets. APIs lie about their pagination support more often than you'd expect.

### 3. Don't hardcode response extraction paths
Different endpoints for the same API often return data in different structures. Always use fallback chains:
```typescript
const data = response?.data ?? response ?? {};
responseData = (data.items ?? data ?? []) as IDataObject[];
if (!Array.isArray(responseData)) responseData = [];
```

### 4. Don't assume `default` values are dynamic
n8n's `default` property is **static** — it's set once when the field renders. You cannot randomize it per row in a fixedCollection. Handle dynamic defaults in the `execute()` function instead.

### 5. Don't skip the `Array.isArray` guard
Before spreading (`...items`), ALWAYS check `Array.isArray(items)`. An object that isn't iterable will crash with the `Symbol.iterator` error. This one check prevents the #1 most common runtime crash in custom nodes.
