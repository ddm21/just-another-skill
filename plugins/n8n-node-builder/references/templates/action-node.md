# Templates: Action Node

Load this when generating a standard action node (most common type).
Covers the full stack: entry point → V1 class → versionDescription → router → resource → operations → transport.
All templates use `{{PLACEHOLDER}}` substitution — see SKILL.md for the full table.

---

## T5: Node entry point (VersionedNodeType)

```typescript
// nodes/{{SERVICE}}/{{SERVICE}}.node.ts
import type { INodeTypeBaseDescription, IVersionedNodeType } from 'n8n-workflow';
import { VersionedNodeType } from 'n8n-workflow';
import { {{SERVICE}}V1 } from './v1/{{SERVICE}}V1';

export class {{SERVICE}} extends VersionedNodeType {
  constructor() {
    const baseDescription: INodeTypeBaseDescription = {
      displayName: '{{SERVICE}}',
      name: '{{service}}',
      icon: 'file:{{service-slug}}.svg',
      group: ['transform'],
      description: 'Interact with the {{SERVICE}} API',
      defaultVersion: 1,
    };
    const nodeVersions: IVersionedNodeType['nodeVersions'] = {
      1: new {{SERVICE}}V1(baseDescription),
    };
    super(nodeVersions, baseDescription);
  }
}
```

## T6: V1 Action Node class

> **CRITICAL FILE NAMING**: This file MUST be named `{{SERVICE}}V1.ts` — NOT `{{SERVICE}}V1.node.ts`.
> n8n's `CustomDirectoryLoader` globs `**/*.node.js` and will pick up any file ending in `.node.js`
> as a standalone node. If the V1 file is named `.node.ts`, it gets loaded independently (without
> `baseDescription`), registers under the same node type name, overwrites the proper entry — and
> loses the icon. Only the entry point (`{{SERVICE}}.node.ts`) should have the `.node.ts` suffix.

```typescript
// nodes/{{SERVICE}}/v1/{{SERVICE}}V1.ts       ← NOT {{SERVICE}}V1.node.ts
import type { IExecuteFunctions, INodeType, INodeTypeDescription, INodeTypeBaseDescription } from 'n8n-workflow';
import { router } from './actions/router';
import { versionDescription } from './actions/versionDescription';
// import { listSearch, loadOptions } from './methods';  // uncomment if needed

export class {{SERVICE}}V1 implements INodeType {
  description: INodeTypeDescription;

  constructor(baseDescription: INodeTypeBaseDescription) {
    this.description = { ...baseDescription, ...versionDescription, usableAsTool: true };
  }

  // methods = { listSearch, loadOptions };  // uncomment if needed

  async execute(this: IExecuteFunctions) {
    return await router.call(this);
  }
}
```

## T7: versionDescription.ts

> **CRITICAL**: Do NOT include `icon` here. The icon is set in `baseDescription` (T5) and passed
> into V1 via the constructor. Since V1 spreads `{ ...baseDescription, ...versionDescription }`,
> any `icon` in `versionDescription` would override `baseDescription.icon`. The icon path resolves
> relative to the file that defines it — if defined here (inside `v1/actions/`), n8n would look for
> the SVG in `v1/actions/` instead of next to the entry point where it actually lives.

```typescript
// nodes/{{SERVICE}}/v1/actions/versionDescription.ts
import { NodeConnectionTypes, type INodeTypeDescription } from 'n8n-workflow';
import * as {{resource1}} from './{{resource1}}/{{Resource1}}.resource';

export const versionDescription: INodeTypeDescription = {
  displayName: '{{SERVICE}}',
  name: '{{service}}',
  // icon is inherited from baseDescription — do NOT set it here
  group: ['transform'],
  version: 1,
  subtitle: '={{ $parameter["operation"] + ": " + $parameter["resource"] }}',
  description: 'Interact with the {{SERVICE}} API',
  defaults: { name: '{{SERVICE}}' },
  inputs: [NodeConnectionTypes.Main],
  outputs: [NodeConnectionTypes.Main],
  credentials: [{ name: '{{service}}Api', required: true }],
  properties: [
    {
      displayName: 'Resource',
      name: 'resource',
      type: 'options',
      noDataExpression: true,
      options: [{ name: '{{Resource1}}', value: '{{resource1}}' }],
      default: '{{resource1}}',
    },
    ...{{resource1}}.description,
  ],
};
```

## T8: router.ts

```typescript
// nodes/{{SERVICE}}/v1/actions/router.ts
import type { IExecuteFunctions, INodeExecutionData } from 'n8n-workflow';
import { NodeOperationError } from 'n8n-workflow';
import * as {{resource1}} from './{{resource1}}/{{Resource1}}.resource';

export async function router(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
  const items = this.getInputData();
  const resource = this.getNodeParameter('resource', 0) as string;
  const operation = this.getNodeParameter('operation', 0) as string;
  let returnData: INodeExecutionData[] = [];

  // Wrap the switch in try/catch so you can enrich error messages before re-throwing
  // (e.g. add hints about Typecast, bad field names, etc.)
  try {
    switch (resource) {
      case '{{resource1}}':
        returnData = await ({{resource1}} as any)[operation].execute.call(this, items);
        break;
      default:
        throw new NodeOperationError(this.getNode(), `Unknown resource: "${resource}"`);
    }
  } catch (error) {
    // Optionally enrich the error description here before re-throwing:
    // if (error.description?.includes('some known issue')) error.description += '. Hint: ...';
    throw error;
  }

  return [returnData];
}
```

## T9: Resource.resource.ts

```typescript
// nodes/{{SERVICE}}/v1/actions/{{resource1}}/{{Resource1}}.resource.ts
import type { INodeProperties } from 'n8n-workflow';
import * as create from './create.operation';
import * as get from './get.operation';
import * as getAll from './getAll.operation';
import * as update from './update.operation';
import * as del from './delete.operation';

export { create, get, getAll, update, del as delete };

export const description: INodeProperties[] = [
  {
    displayName: 'Operation',
    name: 'operation',
    type: 'options',
    noDataExpression: true,
    displayOptions: { show: { resource: ['{{resource1}}'] } },
    options: [
      { name: 'Create',   value: 'create',  action: 'Create a {{resource1}}' },
      { name: 'Delete',   value: 'delete',  action: 'Delete a {{resource1}}' },
      { name: 'Get',      value: 'get',     action: 'Get a {{resource1}}' },
      { name: 'Get Many', value: 'getAll',  action: 'Get many {{resource1}}s' },
      { name: 'Update',   value: 'update',  action: 'Update a {{resource1}}' },
    ],
    default: 'getAll',
  },
  ...create.description,
  ...get.description,
  ...getAll.description,
  ...update.description,
  ...del.description,
];
```

## T10: getAll.operation.ts

```typescript
// nodes/{{SERVICE}}/v1/actions/{{resource1}}/getAll.operation.ts
import type { IDataObject, IExecuteFunctions, INodeExecutionData, INodeProperties } from 'n8n-workflow';
import { apiRequest, apiRequestAllItems } from '../../transport';

export const description: INodeProperties[] = [
  {
    displayName: 'Return All', name: 'returnAll', type: 'boolean', default: false,
    description: 'Whether to return all results or only up to a given limit',
    displayOptions: { show: { resource: ['{{resource1}}'], operation: ['getAll'] } },
  },
  {
    displayName: 'Limit', name: 'limit', type: 'number', default: 50,
    typeOptions: { minValue: 1 },
    displayOptions: { show: { resource: ['{{resource1}}'], operation: ['getAll'], returnAll: [false] } },
  },
  {
    displayName: 'Additional Fields', name: 'additionalFields', type: 'collection',
    placeholder: 'Add Field', default: {},
    displayOptions: { show: { resource: ['{{resource1}}'], operation: ['getAll'] } },
    options: [],
  },
];

export async function execute(this: IExecuteFunctions, items: INodeExecutionData[]): Promise<INodeExecutionData[]> {
  const returnData: INodeExecutionData[] = [];
  for (let i = 0; i < items.length; i++) {
    try {
      const returnAll = this.getNodeParameter('returnAll', i) as boolean;
      const additionalFields = this.getNodeParameter('additionalFields', i) as IDataObject;
      const qs: IDataObject = { ...additionalFields };
      let responseData: IDataObject[];

      if (returnAll) {
        responseData = await apiRequestAllItems.call(this, 'GET', '/{{resource1}}s', {}, qs);
      } else {
        qs.limit = this.getNodeParameter('limit', i) as number;
        const response = await apiRequest.call(this, 'GET', '/{{resource1}}s', {}, qs);
        responseData = response.items ?? response.data ?? response ?? [];
      }

      returnData.push(...this.helpers.constructExecutionMetaData(
        this.helpers.returnJsonArray(responseData), { itemData: { item: i } },
      ));
    } catch (error) {
      if (this.continueOnFail()) { returnData.push({ json: { error: error.message }, pairedItem: { item: i } }); continue; }
      throw error;
    }
  }
  return returnData;
}
```

## T11: create.operation.ts

```typescript
// nodes/{{SERVICE}}/v1/actions/{{resource1}}/create.operation.ts
import type { IDataObject, IExecuteFunctions, INodeExecutionData, INodeProperties } from 'n8n-workflow';
import { apiRequest } from '../../transport';

export const description: INodeProperties[] = [
  {
    displayName: 'Name', name: 'name', type: 'string', required: true, default: '',
    displayOptions: { show: { resource: ['{{resource1}}'], operation: ['create'] } },
  },
  {
    displayName: 'Additional Fields', name: 'additionalFields', type: 'collection',
    placeholder: 'Add Field', default: {},
    displayOptions: { show: { resource: ['{{resource1}}'], operation: ['create'] } },
    options: [],
  },
];

export async function execute(this: IExecuteFunctions, items: INodeExecutionData[]): Promise<INodeExecutionData[]> {
  const returnData: INodeExecutionData[] = [];
  for (let i = 0; i < items.length; i++) {
    try {
      const body: IDataObject = {
        name: this.getNodeParameter('name', i) as string,
        ...this.getNodeParameter('additionalFields', i) as IDataObject,
      };
      const responseData = await apiRequest.call(this, 'POST', '/{{resource1}}s', body);
      returnData.push(...this.helpers.constructExecutionMetaData(
        this.helpers.returnJsonArray(responseData), { itemData: { item: i } },
      ));
    } catch (error) {
      if (this.continueOnFail()) { returnData.push({ json: { error: error.message }, pairedItem: { item: i } }); continue; }
      throw error;
    }
  }
  return returnData;
}
```

## T12: transport/index.ts

```typescript
// nodes/{{SERVICE}}/v1/transport/index.ts
import type { IDataObject, IExecuteFunctions, ILoadOptionsFunctions, IPollFunctions, IHttpRequestMethods, IRequestOptions } from 'n8n-workflow';

const BASE_URL = '{{BASE_URL}}';

export async function apiRequest(
  this: IExecuteFunctions | ILoadOptionsFunctions | IPollFunctions,
  method: IHttpRequestMethods, endpoint: string,
  body: IDataObject = {}, query: IDataObject = {}, uri?: string, option: IDataObject = {},
): Promise<any> {
  const options: IRequestOptions = {
    headers: { 'Content-Type': 'application/json' },
    method, body, qs: query,
    uri: uri ?? `${BASE_URL}${endpoint}`,
    json: true,
  };
  if (Object.keys(option).length) Object.assign(options, option);
  if (!Object.keys(body).length) delete options.body;
  // Use the credential name that matches your credential class's `name` field:
  //   API key auth  → '{{service}}Api'
  //   OAuth2 auth   → '{{service}}OAuth2Api'
  return await this.helpers.requestWithAuthentication.call(this, '{{CREDENTIAL_NAME_CAMEL}}', options);
}

export async function apiRequestAllItems(
  this: IExecuteFunctions | ILoadOptionsFunctions | IPollFunctions,
  method: IHttpRequestMethods, endpoint: string,
  body: IDataObject = {}, query: IDataObject = {},
): Promise<IDataObject[]> {
  const returnData: IDataObject[] = [];
  query.limit = query.limit ?? 100;
  let offset = 0;
  do {
    query.offset = offset;
    const responseData = await apiRequest.call(this, method, endpoint, body, query);
    const items: IDataObject[] = responseData.items ?? responseData.data ?? responseData ?? [];
    returnData.push(...items);
    if (items.length < (query.limit as number)) break;
    offset += items.length;
  } while (true);
  return returnData;
}
```
