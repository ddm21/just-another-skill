---
name: easypanel-template
description: Generate complete Easypanel deployment templates for any self-hosted app. Use this skill whenever the user wants to create an Easypanel template, deploy an app to Easypanel, generate meta.yaml + index.ts files for Easypanel, or package any Docker-based app for the Easypanel template marketplace. Trigger this skill even if the user just says "make an Easypanel template for X" or "I want to deploy X on Easypanel" or "create a template for X app".
---

# Easypanel Template Generator

Generates production-ready Easypanel templates: `meta.yaml` + `index.ts` for any self-hosted app.

## What a Template Is

An Easypanel template = two files that tell the platform how to deploy an app:

- `meta.yaml` — metadata + JSON Schema (becomes the UI input form)
- `index.ts` — TypeScript `generate()` function that turns user inputs into service configs
- `meta.ts` — auto-generated from schema, DO NOT write this manually
- `assets/` — logo.png or logo.svg, optional screenshots

## Step 1: Gather Info from User

Before writing anything, collect:

1. **App name** and Docker image (e.g., `ghcr.io/foo/bar:latest`)
2. **App description** (1-2 sentences, what it does, who it's for)
3. **Architecture** — does it need:
   - Just the app container? (simple)
   - App + PostgreSQL? (standard)
   - App + PostgreSQL + Redis? (complex)
   - App + MySQL? (standard variant)
   - Multiple workers/separate services? (advanced)
   - Docker Compose-based? (compose pattern)
4. **Required environment variables** — what does the app need to start?
5. **Data persistence** — what paths need volume mounts?
6. **Default port** the app listens on
7. **Links** — homepage, docs, GitHub

If the user provides an app name or Docker Hub link, look up the app's Docker environment variables from its docs before asking. Fill in what you can, then confirm.

Read `references/patterns.md` for complete code patterns for each architecture type.

---

## Step 2: Determine Architecture Type

| Pattern | Services | When to use |
|---|---|---|
| Simple | 1 app | No DB needed, stateless or SQLite |
| App + DB | 1 app + 1 postgres/mysql | App requires relational DB |
| App + DB + Redis | 1 app + postgres + redis | App requires caching/queues |
| Multi-service | 2+ app containers | Workers, schedulers, separate API |
| Conditional DB | 1 app + optional postgres | App supports both SQLite and postgres |
| Compose | Docker Compose passthrough | Complex apps best described via compose |

---

## Step 3: Write meta.yaml

### Full Structure

```yaml
name: AppName
description: One sentence about what the app does.
instructions: |
  Optional setup instructions shown to user after deployment.
  Use markdown. Mention default credentials here if any.
changeLog:
  - date: "YYYY-MM-DD"
    description: "Initial release"
links:
  - label: Website
    url: https://example.com
  - label: Documentation
    url: https://docs.example.com
  - label: Github
    url: https://github.com/org/repo
contributors:
  - name: Your Name
    url: https://github.com/yourhandle
schema:
  type: object
  required:
    - appServiceName
    - appServiceImage
  properties:
    appServiceName:
      type: string
      title: App Service Name
      default: myapp
    appServiceImage:
      type: string
      title: App Image
      default: "org/app:1.0.0"
    # Add DB service name if needed:
    databaseServiceName:
      type: string
      title: Database Service Name
      default: myapp-db
    # Add user-facing config fields:
    adminEmail:
      type: string
      title: Admin Email
    adminPassword:
      type: string
      title: Admin Password
```

### Schema Field Types

| Field type | YAML |
|---|---|
| Text input | `type: string` |
| Password | `type: string` (Easypanel detects "password" in key name) |
| Number | `type: number` |
| Boolean toggle | `type: boolean` |
| Dropdown | `type: string` with `oneOf: [{enum: ["val"], title: "Label"}]` |
| Optional field | Omit from `required` array |

---

## Step 4: Write index.ts

### Import pattern (always the same)

```typescript
import { Output, randomPassword, Services } from "~templates-utils";
import { Input } from "./meta";
```

### generate() function skeleton

```typescript
export function generate(input: Input): Output {
  const services: Services = [];
  
  // generate passwords for any DB services
  const databasePassword = randomPassword();
  
  // build and push each service
  services.push(/* app service */);
  services.push(/* db service */);
  
  return { services };
}
```

### App Service Object

```typescript
services.push({
  type: "app",
  data: {
    projectName: input.projectName,
    serviceName: input.appServiceName,
    source: {
      type: "image",
      image: input.appServiceImage,
    },
    domains: [
      {
        host: "$(PRIMARY_DOMAIN)",
        port: 80, // container port the app listens on
      },
    ],
    env: [
      `KEY=value`,
      `DATABASE_URL=postgres://postgres:${databasePassword}@$(PROJECT_NAME)_${input.databaseServiceName}:5432/$(PROJECT_NAME)`,
      `REDIS_URL=redis://default:${redisPassword}@$(PROJECT_NAME)_${input.redisServiceName}:6379`,
      `APP_URL=https://$(PRIMARY_DOMAIN)`,
      `SECRET_KEY=$(SECRET_KEY)`, // auto-generated by platform
    ].join("\n"),
    mounts: [
      {
        type: "volume",
        name: "data",
        mountPath: "/app/data",
      },
    ],
  },
});
```

### PostgreSQL Service Object

```typescript
services.push({
  type: "postgres",
  data: {
    projectName: input.projectName,
    serviceName: input.databaseServiceName,
    password: databasePassword,
  },
});
```

### MySQL Service Object

```typescript
services.push({
  type: "mysql",
  data: {
    projectName: input.projectName,
    serviceName: input.databaseServiceName,
    password: databasePassword,
  },
});
```

### Redis Service Object

```typescript
services.push({
  type: "redis",
  data: {
    projectName: input.projectName,
    serviceName: input.redisServiceName,
    password: redisPassword,
  },
});
```

### MongoDB Service Object

```typescript
services.push({
  type: "mongo",
  data: {
    projectName: input.projectName,
    serviceName: input.databaseServiceName,
    password: databasePassword,
  },
});
```

---

## Platform Variables (use in env strings)

| Variable | Meaning |
|---|---|
| `$(PROJECT_NAME)` | Easypanel project name |
| `$(PRIMARY_DOMAIN)` | The primary domain assigned to the service |
| `$(EASYPANEL_DOMAIN)` | The Easypanel instance domain |
| `$(SECRET_KEY)` | Auto-generated secret, stable per project |

Service-to-service hostnames follow the pattern:
```
$(PROJECT_NAME)_<serviceName>
```
So if your app's DB service name is `myapp-db`, the host is `$(PROJECT_NAME)_myapp-db`.

---

## Special Patterns

### Conditional Database (SQLite vs PostgreSQL)

In meta.yaml schema:
```yaml
databaseType:
  type: string
  title: Database Type
  oneOf:
    - enum: ["sqlite"]
      title: SQLite (built-in)
    - enum: ["postgres"]
      title: PostgreSQL
  default: sqlite
```

In index.ts:
```typescript
const isPostgres = input.databaseType === "postgres";
const databasePassword = isPostgres ? randomPassword() : "";

const env = [
  isPostgres
    ? `DATABASE_URL=postgres://postgres:${databasePassword}@$(PROJECT_NAME)_${input.databaseServiceName}:5432/$(PROJECT_NAME)`
    : `DATABASE_URL=sqlite:////app/data/db.sqlite`,
].join("\n");

if (isPostgres) {
  services.push({ type: "postgres", data: { ... } });
}
```

### Workers / Multiple App Containers

Just push multiple `type: "app"` services. Worker services typically don't need a `domains` field, and they get a different command:

```typescript
services.push({
  type: "app",
  data: {
    projectName: input.projectName,
    serviceName: `${input.appServiceName}-worker`,
    source: { type: "image", image: input.appServiceImage },
    deploy: {
      command: "worker", // or whatever the entrypoint is
    },
    env: sharedEnv,
    mounts: sharedMounts,
  },
});
```

### Bind Mounts (host path)

```typescript
mounts: [
  {
    type: "bind",
    hostPath: "/lib/modules",
    mountPath: "/lib/modules",
  },
]
```

### Custom Capabilities

```typescript
deploy: {
  capAdd: ["NET_ADMIN", "SYS_MODULE"],
}
```

### UDP Ports

```typescript
ports: [
  {
    published: Number(input.appServicePort),
    target: 51820,
    protocol: "udp",
  },
]
```

---

## Output: File Structure to Deliver

Always deliver these files:

```
templates/<appname>/
├── meta.yaml        ← write this
├── index.ts         ← write this
└── assets/
    └── logo.png     ← note: user must add manually, or source from DockerHub/GitHub
```

Do NOT write `meta.ts`. Tell the user it's auto-generated by running `npm run build` in the repo.

---

## Quality Checklist

Before finalising, verify:

- [ ] All DB service names use the `$(PROJECT_NAME)_` prefix in connection strings
- [ ] `randomPassword()` is called for every DB service
- [ ] App domain port matches actual container port the app listens on
- [ ] All user-provided inputs that appear in env strings are sanitised/used correctly
- [ ] `required` array in meta.yaml matches what the generate() function actually uses
- [ ] Volume mounts cover all stateful paths (data, uploads, config)
- [ ] If app has default credentials, they're documented in `instructions` field

---

For full working code examples of each pattern, read `references/patterns.md`.