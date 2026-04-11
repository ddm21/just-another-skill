# Templates: Polling Trigger

Load this when the node type is **polling trigger** (service has no webhook push support).
All templates use `{{PLACEHOLDER}}` substitution — see SKILL.md for the full table.

---

## T13: Polling Trigger node

Uses `INodeType` with `poll()`. No `execute()`. Runs on a schedule set by the user.

```typescript
// nodes/{{SERVICE}}Trigger/{{SERVICE}}Trigger.node.ts
import type { IPollFunctions, IDataObject, INodeExecutionData, INodeType, INodeTypeDescription } from 'n8n-workflow';
import { NodeConnectionTypes, NodeOperationError } from 'n8n-workflow';
import { apiRequest } from './transport';

export class {{SERVICE}}Trigger implements INodeType {
  description: INodeTypeDescription = {
    displayName: '{{SERVICE}} Trigger',
    name: '{{service}}Trigger',
    icon: 'file:{{service-slug}}.svg',
    group: ['trigger'],
    version: 1,
    subtitle: '={{$parameter["event"]}}',
    description: 'Starts the workflow when {{SERVICE}} events occur',
    defaults: { name: '{{SERVICE}} Trigger' },
    credentials: [{ name: '{{service}}Api', required: true }],
    polling: true,
    inputs: [],
    outputs: [NodeConnectionTypes.Main],
    properties: [
      {
        displayName: 'Event', name: 'event', type: 'options',
        options: [{ name: 'New Item Created', value: 'newItem' }],
        default: 'newItem',
      },
    ],
  };

  async poll(this: IPollFunctions): Promise<INodeExecutionData[][] | null> {
    const webhookData = this.getWorkflowStaticData('node');
    const now = new Date().toISOString();
    const lastCheck = (webhookData.lastTimeChecked as string) ?? now;
    webhookData.lastTimeChecked = now;

    try {
      const response = await apiRequest.call(this, 'GET', '/{{resource1}}s', {}, { created_after: lastCheck });
      const items: IDataObject[] = response.items ?? response.data ?? response ?? [];
      if (!items.length) return null;
      return [this.helpers.returnJsonArray(items)];
    } catch (error) {
      throw new NodeOperationError(this.getNode(), error);
    }
  }
}
```

**Key points:**
- `polling: true` in description — required
- `inputs: []` — trigger nodes have no input
- `webhookData.lastTimeChecked` — persists the last poll timestamp across runs
- Return `null` when no new items (n8n will not execute the workflow)
- The `apiRequest` transport helper is the same as in T12, placed at `./transport/index.ts`
