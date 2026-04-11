---
name: n8n-node-builder
description: "Build complete, production-ready n8n community nodes from scratch. Use when the user wants to create, build, or generate an n8n node for any API or service. Handles all node types: action, polling trigger, webhook trigger, webhook sender. Trigger this skill whenever the user mentions building a custom n8n integration, connecting a new API to n8n, or says things like 'I want to use X in n8n' or 'make an n8n node for Y' — even if they don't use the word 'node'."
---

# n8n Node Builder

**This skill is RIGID. Follow every phase in order. Do not skip phases.**

Reference files (load ONLY what you need — never load all at once):
- `references/patterns.md` — node type decision tree, router/pagination/credential patterns
- `references/property-types.md` — INodeProperties type reference with examples
- `references/platform-limitations.md` — known n8n framework limitations & workarounds (fixedCollection cross-field deps, dynamic type switching, getCurrentNodeParameter scope, etc.)
- `references/best-practices-and-fixes.md` — common runtime errors (Symbol.iterator crash, empty pagination, response unwrapping), anti-patterns, shared constants pattern, scope-specific fields, client-side limit enforcement
- `references/templates/project-setup.md` — T1 package.json, T2 tsconfig, T17 node.json, T18 SVG, T19-T21 config files, T22-T23 GitHub Actions, T29 index.ts entry point, T30 .npmignore
- `references/templates/credentials.md` — T3 API key credential, T4 OAuth2 credential
- `references/templates/action-node.md` — T5-T12: full action node stack (entry, V1 class, versionDescription, router, resource, getAll, create, transport)
- `references/templates/trigger-polling.md` — T13: polling trigger (INodeType + poll())
- `references/templates/trigger-webhook.md` — T24: simple webhook trigger, T25: HMAC + dual-webhook + webhookMethods
- `references/templates/methods.md` — T14 listSearch, T15 loadOptions, T16 utils/error handler
- `references/templates/advanced.md` — T26 sendAndWait, T27 declarative+hooks, T28 test file

## SELF-UPDATE — Staying current with n8n

The official n8n community node starter repo is actively maintained:
- **Repository:** `https://github.com/n8n-io/n8n-nodes-starter`

When building or debugging nodes and something doesn't work as expected:
1. **WebFetch** the starter repo's latest `README.md`, `package.json`, and key source files to check for API changes, new patterns, or deprecations
2. **WebSearch** for `n8n community node [topic] site:community.n8n.io` or `n8n [topic] site:docs.n8n.io` for the latest docs and community solutions
3. Check the n8n official docs at `https://docs.n8n.io/integrations/creating-nodes/` for any updated guidance

Do this proactively when:
- A build fails with unfamiliar errors
- An n8n API or SDK type has changed
- The user reports the node doesn't work in a newer n8n version

---

## PHASE 1 — API DISCOVERY

Identify the service name from the user's message, then:

1. `WebSearch` → `[service] API documentation REST`
2. `WebFetch` → load the main API reference page
3. Extract: base URL, auth method(s), main resources, key endpoints, pagination style, rate limits, file upload/download support
4. If docs are inaccessible → skip to Phase 2, ask user for docs URL

---

## PHASE 2 — REQUIREMENTS GATHERING

Ask **one at a time**, wait for each answer:

**Q1 — Node type:**
> 1. **Action node** — manual trigger, performs operations (most common)
> 2. **Polling trigger** — checks for new data on a schedule (service has no push support)
> 3. **Webhook trigger** — receives real-time HTTP pushes (Stripe, GitHub, Shopify, etc.)
> 4. **Webhook sender** — sends a simple outbound HTTP webhook, no auth
>
> Decide 2 vs 3: Can the service push to a callback URL you register? → 3. Only has "list recent" API? → 2.

**Q2 — Auth type** (skip if clear from docs):
> 1. API key in header (`Authorization: Bearer` or `X-API-Key`)
> 2. API key as query param
> 3. OAuth2 (authorization code)
> 4. Basic auth
> 5. No auth

**Q3 — Resources & operations:**
> List resources and operations, e.g. `Record: create, get, update, delete, list` — or say "standard CRUD"

**Q4 — Dynamic fields** (ask only if service has user-defined schemas like Airtable):
> Does [service] have dynamic columns/fields? (yes → add resourceMapper)

**Q4b — Webhook specifics** (ask only if Q1 = 3):
> 1. Must you register the webhook URL via the service API? (yes → implement `webhookMethods`)
> 2. HTTP method the service uses to send events? (default: POST)
> 3. How does the service authenticate its outbound requests? (header secret / HMAC / none)
> 4. Does the service send an event type field or header for filtering? (e.g. `X-GitHub-Event`)
> 5. Does the service send a GET challenge to verify ownership first? (yes → dual-webhook pattern)

**Q5 — Package details:**
> npm package name (default: `n8n-nodes-[service]`) and author name/email (optional)

---

## PHASE 3 — DESIGN REVIEW

Show this before writing any code and wait for confirmation:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  n8n Node Design Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Service:     [ServiceName]
  Node type:   [action | polling trigger | webhook trigger | webhook sender]
  Auth:        [auth type]
  Base URL:    [base url]
  Package:     n8n-nodes-[service]/

  Resources & Operations:
    [resource1]: [op1], [op2], [op3]

  Files to generate:
    package.json, tsconfig.json
    credentials/[Service]Api.credentials.ts
    nodes/[Service]/[Service].node.ts          ← versioned entry (ONLY file with .node.ts suffix)
    nodes/[Service]/v1/[Service]V1.ts            ← NOT .node.ts (see rule 21)
    nodes/[Service]/v1/actions/versionDescription.ts
    nodes/[Service]/v1/actions/router.ts
    nodes/[Service]/v1/actions/[resource]/[Resource].resource.ts
    nodes/[Service]/v1/actions/[resource]/[op].operation.ts  (one per op)
    nodes/[Service]/v1/transport/index.ts
    nodes/[Service]/v1/helpers/utils.ts
    nodes/[Service]/[Service].node.json
    nodes/[Service]/[service].svg                ← MUST be next to the entry .node.ts file
    [methods/listSearch.ts + loadOptions.ts]   ← if dynamic dropdowns
    [methods/resourceMapping.ts]               ← if dynamic fields
    test/[Service].node.test.ts
    .eslintrc.mjs, .prettierrc.js, .gitignore
    .github/workflows/ci.yml + publish.yml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Shall I generate all these files? (yes/no)
```

---

## PHASE 4 — CODE GENERATION

Load the relevant template files from `references/templates/` (see table below). Use these substitutions throughout:

| Placeholder | Example |
|---|---|
| `{{SERVICE}}` | `OpenWeatherMap` (PascalCase) |
| `{{service}}` | `openWeatherMap` (camelCase) |
| `{{service-slug}}` | `open-weather-map` (kebab) |
| `{{CREDENTIAL_NAME}}` | `OpenWeatherMapApi` (PascalCase, used in class name) |
| `{{CREDENTIAL_NAME_CAMEL}}` | `openWeatherMapApi` or `openWeatherMapOAuth2Api` (camelCase, used in `requestWithAuthentication` call — must match credential class `name` field exactly) |
| `{{BASE_URL}}` | `https://api.openweathermap.org/v1` |
| `{{AUTH_HEADER}}` | `X-API-Key` |
| `{{TEST_ENDPOINT}}` | `/status` or `/me` |
| `{{resource1}}` | `record` (camelCase) |
| `{{Resource1}}` | `Record` (PascalCase) |

### Generation rules — always apply every one:

1. `VersionedNodeType` entry wrapper + `V1` implementation class for action nodes
2. `usableAsTool: true` in V1 constructor
3. `subtitle: '={{ $parameter["operation"] + ": " + $parameter["resource"] }}'`
4. `NodeConnectionTypes.Main` — never the string `'main'`
5. `this.helpers.constructExecutionMetaData()` for all output items
6. `pairedItem: { item: i }` on every output item
7. `try/catch` + `this.continueOnFail()` in every item loop
8. `this.helpers.httpRequestWithAuthentication.call(this, credentialType, options)` for all API calls (use `IHttpRequestOptions` with `url`, not deprecated `IRequestOptions` with `uri`)
9. `apiRequestAllItems` pagination helper always present in transport
10. `typeOptions: { password: true }` on every secret/token field
11. `test: ICredentialTestRequest` on every credential class
12. `noDataExpression: true` on resource and operation selectors
13. `NodeOperationError` with `itemIndex` for per-item errors
14. Webhook trigger: extends `Node`, uses `webhook()` not `execute()`, `inputs: []`, `webhooks: [...]`
15. Webhook output always includes: `headers`, `params`, `query`, `body`, `webhookUrl`, `executionMode`
16. `webhookMethods` (checkExists/create/delete) when service requires programmatic registration
17. Dual-webhook (GET challenge + POST events): two entries in `webhooks[]`, dispatch on `this.getWebhookName()`
18. HMAC verification: `createHmac('sha256', secret).update(req.rawBody)` — use `rawBody`, not parsed body
19. Silent reject: return `{}` from `webhook()` for invalid signatures / unrecognized events
20. Declarative + `preSend`/`postReceive` hooks for simple 1:1 CRUD APIs; programmatic router for complex logic
21. **V1 file naming**: V1 class file MUST be `{{SERVICE}}V1.ts` — NEVER `{{SERVICE}}V1.node.ts`. n8n's `CustomDirectoryLoader` globs `**/*.node.js` and loads every match as a standalone node. If V1 has the `.node.ts` suffix, it gets loaded independently without `baseDescription`, registers under the same node type name, overwrites the proper versioned entry, and loses the icon. Only the entry point file (`{{SERVICE}}.node.ts`) should have the `.node.ts` suffix.
22. **Icon placement**: The SVG file MUST live next to the entry `.node.ts` file (e.g., `nodes/{{SERVICE}}/{{service-slug}}.svg`). n8n resolves `file:xxx.svg` relative to the file that defines the `icon` property. Never put icons in a separate `icons/` folder or inside `v1/`.
23. **No `icon` in `versionDescription`**: The `icon` property must ONLY be set in `baseDescription` (inside the `VersionedNodeType` entry). Do NOT set `icon` in `versionDescription.ts`. Since V1 spreads `{ ...baseDescription, ...versionDescription }`, any `icon` in `versionDescription` would override `baseDescription.icon` — and n8n would resolve the path relative to the wrong directory.

### Node type → reference file to load:

| Node type | Load these template files |
|---|---|
| Action node | `action-node.md` |
| Polling trigger | `trigger-polling.md` + `action-node.md` (transport only) |
| Webhook trigger (simple header auth) | `trigger-webhook.md` (T24 section) |
| Webhook trigger (HMAC + challenge) | `trigger-webhook.md` (T25 section) |
| Webhook sender | `action-node.md` (T5, T6, T12 only) |

Always load: `project-setup.md`, `credentials.md`
Load conditionally: `methods.md` (if dynamic dropdowns), `advanced.md` (if sendAndWait or declarative hooks needed)

---

## PHASE 5 — VERIFICATION

After all files are generated, provide:

```bash
cd n8n-nodes-{{service-slug}}
npm install
npm run build    # zero TypeScript errors
npm run lint     # zero lint errors
```

Testing in n8n:
```bash
npm link
# in n8n folder:
npm link n8n-nodes-{{service-slug}}
```

Checklist:
- [ ] `npm run build` passes
- [ ] `npm run lint` passes
- [ ] Credential appears in n8n credentials list
- [ ] Node appears in node palette with correct icon (not broken image placeholder)
- [ ] No `*.node.js` files in `dist/` except the entry point(s) — verify with `find dist -name '*.node.js'`
- [ ] SVG icon is in `dist/nodes/{{SERVICE}}/` next to the entry `.node.js` file
- [ ] `versionDescription.ts` does NOT contain an `icon` property
- [ ] Each operation returns correctly shaped `INodeExecutionData`
- [ ] `pairedItem` set on all output items
- [ ] `continueOnFail` handled in all item loops
- [ ] `usableAsTool: true` is set
