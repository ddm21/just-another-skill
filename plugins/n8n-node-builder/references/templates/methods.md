# Templates: Dynamic Methods & Utilities

Load this when the node needs dynamic dropdowns (listSearch / loadOptions) or a utils helper.
All templates use `{{PLACEHOLDER}}` substitution — see SKILL.md for the full table.

---

## T14: methods/listSearch.ts

Use for `resourceLocator` dropdowns — lets users search and pick items from a paginated list.

```typescript
// nodes/{{SERVICE}}/v1/methods/listSearch.ts
import type { IDataObject, ILoadOptionsFunctions, INodeListSearchResult } from 'n8n-workflow';
import { apiRequest } from '../transport';

export async function search{{Resource1}}(
  this: ILoadOptionsFunctions, filter?: string, paginationToken?: string,
): Promise<INodeListSearchResult> {
  const qs: IDataObject = {};
  if (paginationToken) qs.offset = paginationToken;
  if (filter) qs.search = filter;
  const response = await apiRequest.call(this, 'GET', '/{{resource1}}s', {}, qs);
  const items: IDataObject[] = response.items ?? response.data ?? response ?? [];
  return {
    results: items.map((item) => ({ name: item.name as string, value: item.id as string })),
    paginationToken: response.next_offset ?? undefined,
  };
}
```

Wire up in the V1 node class:
```typescript
methods = { listSearch: { search{{Resource1}} } };
```

Reference in the property:
```typescript
typeOptions: { searchListMethod: 'search{{Resource1}}', searchable: true }
```

---

## T15: methods/loadOptions.ts

Use for `options` / `multiOptions` dropdowns populated from the API at runtime.

```typescript
// nodes/{{SERVICE}}/v1/methods/loadOptions.ts
import type { ILoadOptionsFunctions, INodePropertyOptions } from 'n8n-workflow';
import { apiRequest } from '../transport';

export async function get{{Resource1}}Fields(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
  const response = await apiRequest.call(this, 'GET', '/{{resource1}}/schema');
  return (response.fields ?? []).map((f: { name: string; type: string }) => ({
    name: f.name, value: f.name, description: `Type: ${f.type}`,
  }));
}
```

Wire up in the V1 node class:
```typescript
methods = { loadOptions: { get{{Resource1}}Fields } };
```

Reference in the property:
```typescript
{ type: 'options', typeOptions: { loadOptionsMethod: 'get{{Resource1}}Fields' } }
```

---

## T16: helpers/utils.ts

Standard error handler. Always include; expand as needed.

```typescript
// nodes/{{SERVICE}}/v1/helpers/utils.ts
import type { IDataObject } from 'n8n-workflow';
import { NodeOperationError } from 'n8n-workflow';
import type { IExecuteFunctions } from 'n8n-workflow';

export function process{{SERVICE}}Error(
  error: any,
  node: ReturnType<IExecuteFunctions['getNode']>,
  itemIndex?: number,
): never {
  throw new NodeOperationError(node, error?.response?.body?.message ?? error?.message ?? 'Unknown error', {
    description: error?.response?.body?.details ?? error?.description ?? '',
    itemIndex,
  });
}
```
