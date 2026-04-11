# Templates: Webhook Trigger

Load this when the node type is **webhook trigger** (service pushes HTTP events to a callback URL).
All templates use `{{PLACEHOLDER}}` substitution — see SKILL.md for the full table.

---

## T24: Webhook Trigger — simple (header auth)

Use for services that POST events to your URL with optional header authentication.
Extends `Node`, uses `webhook()`, `inputs: []`, `webhooks: [...]`. No `execute()`.

```typescript
// nodes/{{SERVICE}}Trigger/{{SERVICE}}Trigger.node.ts
import type { IWebhookFunctions, INodeExecutionData, INodeTypeDescription, IWebhookResponseData, IDataObject } from 'n8n-workflow';
import { Node, NodeConnectionTypes } from 'n8n-workflow';

export class {{SERVICE}}Trigger extends Node {
  description: INodeTypeDescription = {
    displayName: '{{SERVICE}} Trigger',
    name: '{{service}}Trigger',
    icon: 'file:{{service-slug}}.svg',
    group: ['trigger'],
    version: 1,
    description: 'Starts the workflow when {{SERVICE}} sends a webhook event',
    eventTriggerDescription: 'Waiting for you to call the Test URL',
    activationMessage: 'You can now receive {{SERVICE}} webhook events.',
    defaults: { name: '{{SERVICE}} Trigger' },
    inputs: [],
    outputs: [NodeConnectionTypes.Main],
    credentials: [{ name: 'httpHeaderAuth', required: false, displayOptions: { show: { authentication: ['headerAuth'] } } }],
    webhooks: [{ name: 'default', httpMethod: 'POST', responseMode: 'onReceived', path: 'webhook' }],
    properties: [
      {
        displayName: 'Authentication', name: 'authentication', type: 'options',
        options: [{ name: 'Header Auth', value: 'headerAuth' }, { name: 'None', value: 'none' }],
        default: 'none',
      },
      {
        displayName: 'Events', name: 'events', type: 'multiOptions',
        options: [{ name: 'All Events', value: '*' }],
        default: ['*'],
      },
    ],
  };

  async webhook(context: IWebhookFunctions): Promise<IWebhookResponseData> {
    const req = context.getRequestObject();
    const resp = context.getResponseObject();

    // Header auth validation
    const authentication = context.getNodeParameter('authentication') as string;
    if (authentication === 'headerAuth') {
      let credentials: { name: string; value: string } | undefined;
      try { credentials = await context.getCredentials<{ name: string; value: string }>('httpHeaderAuth'); } catch {}
      const headers = context.getHeaderData() as IDataObject;
      if (!credentials?.name || headers[credentials.name.toLowerCase()] !== credentials.value) {
        resp.writeHead(403); resp.end('Unauthorized');
        return { noWebhookResponse: true };
      }
    }

    return {
      workflowData: [[{
        json: {
          headers: req.headers, params: req.params, query: req.query, body: req.body,
          webhookUrl: context.getNodeWebhookUrl('default'),
          executionMode: context.getMode() === 'manual' ? 'test' : 'production',
        },
      }]],
    };
  }
}
```

---

## T25: Webhook Trigger — HMAC + dual-webhook challenge

Use for services like WhatsApp, Facebook, GitHub that:
1. Verify ownership via a GET challenge before sending events
2. Sign POST payloads with HMAC-SHA256
3. Require programmatic webhook registration via their API

```typescript
import { createHmac, timingSafeEqual } from 'crypto';
import type { IWebhookFunctions, IDataObject, IWebhookResponseData, IHookFunctions } from 'n8n-workflow';
import { Node } from 'n8n-workflow';
import { apiRequest } from './transport';

export class {{SERVICE}}Trigger extends Node {
  description = {
    // ... same base fields as T24 but with TWO webhook entries:
    webhooks: [
      { name: 'setup',   httpMethod: 'GET',  responseMode: 'onReceived', path: 'webhook' },
      { name: 'default', httpMethod: 'POST', responseMode: 'onReceived', path: 'webhook' },
    ],
    credentials: [{ name: '{{service}}TriggerApi', required: true }],
    // {{service}}TriggerApi credential has: clientId + clientSecret (both password: true)
  };

  // Programmatic webhook registration (omit if service doesn't require it)
  webhookMethods = {
    default: {
      async checkExists(this: IHookFunctions): Promise<boolean> {
        const webhookData = this.getWorkflowStaticData('node');
        if (!webhookData.webhookId) return false;
        try { await apiRequest.call(this, 'GET', `/webhooks/${webhookData.webhookId}`); return true; }
        catch { return false; }
      },
      async create(this: IHookFunctions): Promise<boolean> {
        const response = await apiRequest.call(this, 'POST', '/webhooks', {
          url: this.getNodeWebhookUrl('default'),
          verify_token: this.getNode().id,   // node ID as verify_token
        });
        this.getWorkflowStaticData('node').webhookId = response.id;
        return true;
      },
      async delete(this: IHookFunctions): Promise<boolean> {
        const webhookData = this.getWorkflowStaticData('node');
        if (webhookData.webhookId) {
          await apiRequest.call(this, 'DELETE', `/webhooks/${webhookData.webhookId}`);
          delete webhookData.webhookId;
        }
        return true;
      },
    },
  };

  async webhook(this: IWebhookFunctions): Promise<IWebhookResponseData> {
    const res = this.getResponseObject();
    const req = this.getRequestObject();
    const query = this.getQueryData() as IDataObject;
    const headerData = this.getHeaderData() as IDataObject;
    const credentials = await this.getCredentials('{{service}}TriggerApi');

    // ── 1. GET challenge (Facebook-style ownership verification) ──
    if (this.getWebhookName() === 'setup') {
      if (query['hub.challenge']) {
        if (this.getNode().id !== query['hub.verify_token']) return {};
        res.status(200).send(query['hub.challenge']).end();
        return { noWebhookResponse: true };
      }
    }

    // ── 2. HMAC-SHA256 signature verification ──
    const computed = createHmac('sha256', credentials.clientSecret as string)
      .update(req.rawBody).digest('hex');
    const received = (headerData['x-hub-signature-256'] as string)?.replace('sha256=', '') ?? '';
    if (!timingSafeEqual(Buffer.from(computed), Buffer.from(received))) return {};  // silent reject

    // ── 3. Parse events ──
    const bodyData = this.getBodyData() as IDataObject;
    const events = (bodyData.entry as IDataObject[] ?? [])
      .flatMap((e) => e.changes as IDataObject[] ?? [])
      .map((change) => ({ ...change.value as IDataObject, field: change.field }));

    if (!events.length) return {};
    return { workflowData: [this.helpers.returnJsonArray(events)] };
  }
}
```

**HMAC header names by service:**
| Service | Header | Format |
|---------|--------|--------|
| Facebook / WhatsApp / Instagram | `x-hub-signature-256` | `sha256=<hex>` |
| GitHub | `x-hub-signature-256` | `sha256=<hex>` |
| Stripe | `stripe-signature` | `t=...,v1=<hex>` |
| Shopify | `x-shopify-hmac-sha256` | base64 |

**IWebhookResponseData shapes:**
```typescript
return { workflowData: [[item]] };           // trigger workflow
return { noWebhookResponse: true };          // suppress response (after res.end())
return {};                                   // silent reject — no workflow, no error
return { webhookResponse: 'ok', workflowData: [[item]] }; // custom body + trigger
```
