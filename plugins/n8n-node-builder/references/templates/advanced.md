# Templates: Advanced Patterns

Load this only when the node needs: sendAndWait (human-in-the-loop), declarative routing with hooks, or the test file.
All templates use `{{PLACEHOLDER}}` substitution — see SKILL.md for the full table.

---

## T26: sendAndWait (human-in-the-loop on action node)

Use when the node should send a message and pause execution until a human responds via webhook.

```typescript
import { SEND_AND_WAIT_OPERATION } from 'n8n-workflow';
import { sendAndWaitWebhook, getSendAndWaitConfig, configureWaitTillDate } from 'n8n-workflow';

// On the V1 node class — add alongside execute():
webhook = sendAndWaitWebhook;

// In router.ts — add a customOperations branch:
customOperations = {
  message: {
    async [SEND_AND_WAIT_OPERATION](this: IExecuteFunctions) {
      const config = getSendAndWaitConfig(this);
      await this.helpers.httpRequestWithAuthentication.call(this, '{{service}}Api', buildMessageRequest(config));
      await this.putExecutionToWait(configureWaitTillDate(this));
      return [this.getInputData()];
    },
  },
};

// buildMessageRequest — construct the API body from config:
function buildMessageRequest(config: any) {
  return {
    method: 'POST' as const,
    url: `{{BASE_URL}}/messages`,
    body: {
      text: config.message,
      // service-specific fields...
    },
    json: true,
  };
}
```

**When to use:** Node needs to send a notification and then wait for approval/response before continuing the workflow. Example: send Slack/Teams/WhatsApp message, pause, resume on button click.

---

## T27: Declarative node with preSend/postReceive hooks

Use for simple 1:1 CRUD operations where you don't need item looping or batching.
Use programmatic router (T8) for complex logic, pagination, or batch processing.

```typescript
// In operation description — routing replaces execute()
{
  routing: {
    request: { method: 'POST', url: '=/{{resource1}}s' },
    send: { preSend: [transformBodyHook] },
    output: { postReceive: [handleErrorsHook] },
  },
}

// preSend — modify the request before it is sent
// nodes/{{SERVICE}}/v1/helpers/hooks.ts
import type { IExecuteSingleFunctions, IHttpRequestOptions } from 'n8n-workflow';

export async function transformBodyHook(
  this: IExecuteSingleFunctions,
  requestOptions: IHttpRequestOptions,
): Promise<IHttpRequestOptions> {
  (requestOptions.body as IDataObject).type = this.getNodeParameter('type') as string;
  return requestOptions;
}

// postReceive — validate or reshape the response
import type { IN8nHttpFullResponse, INodeExecutionData } from 'n8n-workflow';
import { NodeApiError } from 'n8n-workflow';

export async function handleErrorsHook(
  this: IExecuteSingleFunctions,
  data: INodeExecutionData[],
  response: IN8nHttpFullResponse,
): Promise<INodeExecutionData[]> {
  if (response.statusCode >= 400) throw new NodeApiError(this.getNode(), response as any);
  return data;
}
```

**Decision guide:**
- Simple 1:1 field mapping → declarative + hooks (T27)
- Looping items, batching, pagination, conditional logic → programmatic router (T8)

---

## T28: Test file

```typescript
// test/{{SERVICE}}.node.test.ts
import { {{SERVICE}} } from '../nodes/{{SERVICE}}/{{SERVICE}}.node';

describe('{{SERVICE}} Node', () => {
  let node: {{SERVICE}};
  beforeEach(() => { node = new {{SERVICE}}(); });

  it('has correct description', () => {
    expect(node.description.displayName).toBe('{{SERVICE}}');
    expect(node.description.name).toBe('{{service}}');
  });

  it('is usable as a tool', () => {
    expect(node.description.usableAsTool).toBe(true);
  });
});
```
