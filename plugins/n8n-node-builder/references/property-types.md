# INodeProperties Type Reference

All `type` values for node properties with minimal examples.

---

## Core types

| type | Use for | Key typeOptions |
|------|---------|----------------|
| `string` | Text input | `password`, `rows`, `maxValue` |
| `number` | Numeric input | `minValue`, `maxValue` |
| `boolean` | Toggle | — |
| `options` | Single-select dropdown | `loadOptionsMethod` for dynamic |
| `multiOptions` | Multi-select | `loadOptionsMethod` for dynamic |
| `collection` | Optional fields group ("Add Field" button) | — |
| `fixedCollection` | Repeatable groups (headers, conditions) | `multipleValues` |
| `resourceLocator` | ID/URL/list picker combo | `searchListMethod` |
| `resourceMapper` | Dynamic column mapping | `resourceMapperMethod`, `mode` |
| `filter` | Built-in conditions UI | `caseSensitive`, `typeValidation` |
| `dateTime` | Date/time picker | — |
| `color` | Color picker | — |
| `json` | JSON editor | `alwaysOpenEditWindow` |
| `notice` | Info/warning banner (no input) | `theme: 'info'|'warning'|'danger'` |
| `hidden` | Hardcoded/computed value, not shown | — |

---

## string

```typescript
// Basic
{ displayName: 'Name', name: 'name', type: 'string', default: '' }

// Password (masked)
{ displayName: 'API Key', name: 'apiKey', type: 'string', typeOptions: { password: true }, default: '' }

// Multiline
{ displayName: 'Body', name: 'body', type: 'string', typeOptions: { rows: 4 }, default: '' }
```

## options

```typescript
{
  displayName: 'Resource', name: 'resource', type: 'options',
  noDataExpression: true,   // always add for resource/operation selectors
  options: [
    { name: 'Record', value: 'record', description: 'Manage records' },
  ],
  default: 'record',
}

// With action (for operation selectors)
{ name: 'Create', value: 'create', description: 'Create a new record', action: 'Create a record' }
```

## collection

```typescript
{
  displayName: 'Additional Fields', name: 'additionalFields',
  type: 'collection', placeholder: 'Add Field', default: {},
  displayOptions: { show: { resource: ['record'], operation: ['create'] } },
  options: [
    { displayName: 'Description', name: 'description', type: 'string', default: '' },
  ],
}
```

## fixedCollection

```typescript
{
  displayName: 'Headers', name: 'headers',
  type: 'fixedCollection', typeOptions: { multipleValues: true },
  placeholder: 'Add Header', default: {},
  options: [{
    name: 'header', displayName: 'Header',
    values: [
      { displayName: 'Name',  name: 'name',  type: 'string', default: '' },
      { displayName: 'Value', name: 'value', type: 'string', default: '' },
    ],
  }],
}

// Reading:
const headers = this.getNodeParameter('headers', i) as { header?: Array<{name: string; value: string}> };
const list = headers.header ?? [];
```

## resourceLocator

```typescript
{
  displayName: 'Record', name: 'recordId', type: 'resourceLocator',
  default: { mode: 'list', value: '' }, required: true,
  modes: [
    {
      displayName: 'From List', name: 'list', type: 'list',
      typeOptions: { searchListMethod: 'searchRecords', searchable: true },
    },
    {
      displayName: 'By ID', name: 'id', type: 'string',
      placeholder: 'rec1234567890abcd',
      validation: [{ type: 'regex', properties: { regex: 'rec[a-zA-Z0-9]{14}', errorMessage: 'Invalid ID' } }],
    },
    {
      displayName: 'By URL', name: 'url', type: 'string',
      extractValue: { type: 'regex', regex: '/([a-zA-Z0-9]+)$' },
    },
  ],
}

// Reading (always use extractValue: true):
const id = this.getNodeParameter('recordId', i, undefined, { extractValue: true }) as string;
```

## resourceMapper

```typescript
{
  displayName: 'Fields to Send', name: 'fieldsToSend',
  type: 'resourceMapper', noDataExpression: true, required: true,
  default: { mappingMode: 'defineBelow', value: null },
  typeOptions: {
    resourceMapper: {
      resourceMapperMethod: 'getColumns',
      mode: 'add',   // 'add' | 'update' | 'upsert'
      fieldWords: { singular: 'field', plural: 'fields' },
      addAllFields: true,
    },
  },
}

// Method (in methods/resourceMapping.ts):
export async function getColumns(this: ILoadOptionsFunctions): Promise<ResourceMapperFields> {
  return { fields: apiFields.map(f => ({
    id: f.name, displayName: f.label, required: false,
    defaultMatch: f.isPrimary ?? false, canBeUsedToMatch: true,
    display: true, type: mapType(f.type), readOnly: f.readOnly ?? false,
  })) };
}
```

## filter

```typescript
{
  displayName: 'Conditions', name: 'conditions', type: 'filter', default: {},
  typeOptions: { filter: { caseSensitive: '={{!$parameter.options.ignoreCase}}', typeValidation: 'strict' } },
}
```

## notice

```typescript
{ displayName: 'Note: requires admin permissions', name: 'adminNotice', type: 'notice', default: '',
  typeOptions: { theme: 'warning' } }
```

## hidden

```typescript
{ displayName: 'Grant Type', name: 'grantType', type: 'hidden', default: 'authorizationCode' }
```

---

## displayOptions

```typescript
// Show when resource=record AND operation=create
displayOptions: { show: { resource: ['record'], operation: ['create'] } }

// Show for multiple operations (OR)
displayOptions: { show: { operation: ['create', 'update'] } }

// Hide when returnAll=true
displayOptions: { hide: { returnAll: [true] } }

// Show based on node version
displayOptions: { show: { '@version': [{ _cnd: { gte: 2 } }] } }
```

## FieldType mapping (for resourceMapper)

| n8n FieldType | API types |
|---|---|
| `string` | text, email, url, phone, varchar |
| `number` | integer, float, decimal, currency |
| `boolean` | boolean, checkbox |
| `dateTime` | datetime, timestamp |
| `options` | enum, select, single-select |
| `array` | array, multi-select, tags |
| `object` | object, JSON |
