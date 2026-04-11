# n8n Platform Limitations & Workarounds

Known limitations of n8n's node framework and practical workarounds discovered through real-world development. Reference this when hitting walls with dynamic UIs.

---

## fixedCollection: No cross-field dependencies within rows

**Problem:** Inside a `fixedCollection` with `multipleValues: true`, you CANNOT make one field (e.g., Value) dynamically change based on another field (e.g., Property Name) in the same row.

- `loadOptionsDependsOn` does NOT work for sibling fields within a fixedCollection row
- `getCurrentNodeParameter` inside `loadOptionsMethod` CANNOT access sibling fields in the same row — it can only read top-level parameters
- You cannot conditionally switch a field's `type` (e.g., from `string` to `options`) based on another field's value

**Status:** Open feature request in n8n community (as of 2025). See: https://community.n8n.io/t/enable-loading-options-based-on-neighboring-values-in-multi-item-fixed-collections/70942

**Workarounds:**
1. **Show hints in the Property dropdown description** — include type info and valid options in the `description` field of each loadOptions result. Truncate long lists (show first 3 + count) and point users to a "Get All" operation for the full list.
2. **Add a dedicated "Get [Resource]" operation** — let users run a separate operation to see all valid values (e.g., "Get Event Definitions" returns all event definitions with their properties and select options).
3. **Validate at execution time** — accept string input and validate against API metadata during `execute()`, returning clear error messages.

**Example — truncating long option lists in loadOptions:**
```typescript
async getEventProperties(this: ILoadOptionsFunctions): Promise<INodePropertyOptions[]> {
  // ... fetch definition ...
  return definition.properties.map((p) => {
    let description = `Type: ${p.fieldType}`;
    if ((p.fieldType === 'select' || p.fieldType === 'multiselect') && p.options?.length) {
      const MAX_INLINE = 5;
      if (p.options.length <= MAX_INLINE) {
        description += ` — Options: ${p.options.map((o) => o.label).join(', ')}`;
      } else {
        const preview = p.options.slice(0, 3).map((o) => o.label).join(', ');
        description += ` — ${p.options.length} options (e.g. ${preview}, …). Use "Get [Resource]" to see all.`;
      }
    }
    return { name: p.label, value: p.name, description };
  });
}
```

---

## loadOptionsDependsOn: Auto-refresh dependent dropdowns

`loadOptionsDependsOn` tells n8n to **automatically re-fetch** a dropdown's options when the specified field(s) change. Without it, users must manually click the 3-dot menu → "Refresh" to reload dependent options.

### Syntax
```typescript
{
  displayName: 'Stage', name: 'stageId', type: 'options',
  typeOptions: {
    loadOptionsMethod: 'getPipelineStages',
    loadOptionsDependsOn: ['pipelineId'],  // ← array of field names
  },
}
```
The value is an **array of top-level parameter names**. When any of them change, n8n calls the loadOptionsMethod again.

### What works

**Top-level field → top-level field:**
```typescript
// Pipeline (top-level) → Stage (top-level) — ✅ WORKS
// pipelineId is a top-level field, stageId has loadOptionsDependsOn: ['pipelineId']
{
  displayName: 'Pipeline', name: 'pipelineId', type: 'options',
  typeOptions: { loadOptionsMethod: 'getWorkspacePipelines' },
  displayOptions: { show: { resource: ['deal'], operation: ['create'] } },
},
{
  displayName: 'Stage', name: 'stageId', type: 'options',
  typeOptions: {
    loadOptionsMethod: 'getPipelineStages',
    loadOptionsDependsOn: ['pipelineId'],
  },
  displayOptions: { show: { resource: ['deal'], operation: ['create'] } },
}
```

**Top-level field → field inside fixedCollection:**
```typescript
// Event Type (top-level) → Property dropdown (inside fixedCollection) — ✅ WORKS
{
  displayName: 'Event Type', name: 'type', type: 'options',
  typeOptions: { loadOptionsMethod: 'getEventDefinitions' },
},
// Inside fixedCollection options:
{
  displayName: 'Property', name: 'name', type: 'options',
  typeOptions: {
    loadOptionsMethod: 'getEventProperties',
    loadOptionsDependsOn: ['type'],  // ← references top-level 'type'
  },
}
```
In the loadOptionsMethod, read the top-level parameter:
```typescript
const eventType = this.getCurrentNodeParameter('type') as string;
```

### What does NOT work

**Sibling field inside fixedCollection row:**
```typescript
// Trying to read a sibling field inside a fixedCollection row — FAILS
const propertyName = this.getCurrentNodeParameter('name') as string; // returns undefined or wrong value
```

**Field inside collection → sibling inside same collection:**
```typescript
// Pipeline (inside collection) → Stage (inside collection) — ❌ DOES NOT WORK
// Both fields are inside 'updateFields' collection — loadOptionsDependsOn cannot reference siblings
```

### Critical workaround: Move dependent fields out of collections

If you have a cascading dependency (Field A → Field B), and both fields are inside a `collection` or `fixedCollection`, **move them to be top-level fields**. `loadOptionsDependsOn` only reliably works when the dependency target is a top-level parameter.

**Before (broken):**
```typescript
{
  displayName: 'Update Fields', name: 'updateFields', type: 'collection',
  options: [
    { displayName: 'Pipeline', name: 'pipelineId', ... },  // inside collection
    { displayName: 'Stage', name: 'stageId', ...           // can't depend on sibling
      typeOptions: { loadOptionsDependsOn: ['pipelineId'] } // ← WON'T WORK
    },
  ],
}
```

**After (working):**
```typescript
// Pipeline and Stage as top-level fields
{ displayName: 'Pipeline', name: 'pipelineId', type: 'options', ... },
{ displayName: 'Stage', name: 'stageId', type: 'options',
  typeOptions: {
    loadOptionsMethod: 'getPipelineStages',
    loadOptionsDependsOn: ['pipelineId'],  // ← WORKS — pipelineId is top-level
  },
},
// Remaining fields stay in collection
{ displayName: 'Update Fields', name: 'updateFields', type: 'collection', ... },
```

In the execute function, read the moved fields separately:
```typescript
const stageId = this.getNodeParameter('stageId', i) as string;
const updateFields = this.getNodeParameter('updateFields', i) as IDataObject;
// pipelineId is UI-only — don't send to API
if (stageId) updateFields.stageId = stageId;
```

### How core n8n nodes handle it

HubSpot and Pipedrive nodes load **all stages across all pipelines** in a single dropdown — no pipeline dependency at all. This is simpler but gives users a long flat list. `loadOptionsDependsOn` is the better UX when the API supports fetching stages per pipeline.

---

## Dynamic field type switching: Not supported

n8n requires field types to be statically declared. You cannot:
- Change a field from `type: 'string'` to `type: 'options'` at runtime
- Conditionally show different field types based on another field's selection
- Use `displayOptions` to swap between two different fields inside the same fixedCollection row based on a sibling's value

**Workaround:** Accept everything as `string` type, add clear descriptions pointing to where valid values can be found, and validate during execution.

---

## notice field: Useful for inline guidance

When you can't make a field dynamic, use a `notice` type field to provide static guidance:
```typescript
{
  displayName: 'For select/multiselect properties, use the "Get Event Definitions" operation to see valid values.',
  name: 'propertyNotice',
  type: 'notice',
  default: '',
  displayOptions: { show: { resource: ['event'], operation: ['create'] } },
}
```

---

## getCurrentNodeParameter context

| Context | Works? | Notes |
|---------|--------|-------|
| Top-level parameter | Yes | `this.getCurrentNodeParameter('resource')` |
| Collection/additionalFields child reading top-level | Yes | Can read parent-level params |
| Collection child reading sibling in same collection | No | Can't resolve which collection value |
| fixedCollection child reading top-level | Yes | `loadOptionsDependsOn` + `getCurrentNodeParameter` |
| fixedCollection sibling (same row) | No | Cannot determine which row is active |
| Nested fixedCollection | No | No row index context available |

**Rule of thumb:** `getCurrentNodeParameter` can only read **top-level** parameters (those with their own `displayOptions`). Anything nested inside `collection`, `fixedCollection`, or `additionalFields` is invisible to it.

---

## Polling trigger: getWorkflowStaticData persistence

`getWorkflowStaticData('node')` persists between poll intervals but is **cleared when the workflow is deactivated and reactivated**. Design accordingly — always handle the "first run" case where static data is empty.

---

## ESLint filename convention vs V1 versioned node pattern

n8n's ESLint rule `node-filename-against-convention` wants all node files to be named `*.node.ts`. However, the V1 versioned node pattern uses `versionDescription.ts` (not `.node.ts`). **Do NOT rename it** — renaming breaks the `VersionedNodeType` architecture and causes `CustomDirectoryLoader` to load it as a standalone node.

**Fix:** Add a file-level eslint-disable:
```typescript
/* eslint-disable n8n-nodes-base/node-filename-against-convention */
export const versionDescription = { ... };
```

This is safe because the rule is designed for standalone nodes, not versioned sub-files.

---

## SVG icons: Path resolution

n8n resolves `file:xxx.svg` relative to the file that defines the `icon` property. This means:
- Icon MUST be next to the entry `.node.ts` file
- Never put icons in `v1/` or a separate `icons/` folder
- Never set `icon` in `versionDescription.ts` — it would resolve relative to the wrong directory
