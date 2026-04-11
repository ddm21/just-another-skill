# Easypanel Template Patterns - Full Code Examples

Complete, copy-ready examples for every architecture pattern.

---

## Pattern 1: Simple Single Service (No Database)

**Use when**: App is stateless, uses SQLite internally, or doesn't need a DB.

### meta.yaml
```yaml
name: MyApp
description: A lightweight self-hosted tool for X.
instructions: |
  After deployment, visit your domain and complete the setup wizard.
changeLog:
  - date: "2024-01-01"
    description: "Initial release"
links:
  - label: Website
    url: https://myapp.io
  - label: Github
    url: https://github.com/org/myapp
contributors:
  - name: Your Name
    url: https://github.com/yourname
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
      default: "org/myapp:latest"
    timezone:
      type: string
      title: Timezone
      default: UTC
```

### index.ts
```typescript
import { Output, Services } from "~templates-utils";
import { Input } from "./meta";

export function generate(input: Input): Output {
  const services: Services = [];

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
          port: 3000,
        },
      ],
      env: [
        `TZ=${input.timezone}`,
        `APP_URL=https://$(PRIMARY_DOMAIN)`,
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

  return { services };
}
```

---

## Pattern 2: App + PostgreSQL

**Use when**: App requires a relational database.

### meta.yaml
```yaml
name: MyApp
description: Self-hosted project management tool.
instructions: |
  Default login: admin@example.com / changeme
  Please change your password after first login.
changeLog:
  - date: "2024-01-01"
    description: "Initial release"
links:
  - label: Website
    url: https://myapp.io
  - label: Documentation
    url: https://docs.myapp.io
  - label: Github
    url: https://github.com/org/myapp
contributors:
  - name: Your Name
    url: https://github.com/yourname
schema:
  type: object
  required:
    - appServiceName
    - appServiceImage
    - databaseServiceName
    - adminEmail
    - adminPassword
  properties:
    appServiceName:
      type: string
      title: App Service Name
      default: myapp
    appServiceImage:
      type: string
      title: App Image
      default: "org/myapp:1.0.0"
    databaseServiceName:
      type: string
      title: Database Service Name
      default: myapp-db
    adminEmail:
      type: string
      title: Admin Email
    adminPassword:
      type: string
      title: Admin Password
```

### index.ts
```typescript
import { Output, randomPassword, Services } from "~templates-utils";
import { Input } from "./meta";

export function generate(input: Input): Output {
  const services: Services = [];
  const databasePassword = randomPassword();

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
          port: 8080,
        },
      ],
      env: [
        `DATABASE_URL=postgres://postgres:${databasePassword}@$(PROJECT_NAME)_${input.databaseServiceName}:5432/$(PROJECT_NAME)`,
        `APP_URL=https://$(PRIMARY_DOMAIN)`,
        `ADMIN_EMAIL=${input.adminEmail}`,
        `ADMIN_PASSWORD=${input.adminPassword}`,
        `SECRET_KEY=$(SECRET_KEY)`,
      ].join("\n"),
      mounts: [
        {
          type: "volume",
          name: "uploads",
          mountPath: "/app/uploads",
        },
      ],
    },
  });

  services.push({
    type: "postgres",
    data: {
      projectName: input.projectName,
      serviceName: input.databaseServiceName,
      password: databasePassword,
    },
  });

  return { services };
}
```

---

## Pattern 3: App + PostgreSQL + Redis

**Use when**: App needs caching, background queues, or sessions in Redis.

### meta.yaml schema additions (add to Pattern 2)
```yaml
    redisServiceName:
      type: string
      title: Redis Service Name
      default: myapp-redis
```

### index.ts
```typescript
import { Output, randomPassword, Services } from "~templates-utils";
import { Input } from "./meta";

export function generate(input: Input): Output {
  const services: Services = [];
  const databasePassword = randomPassword();
  const redisPassword = randomPassword();

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
          port: 3000,
        },
      ],
      env: [
        `DATABASE_URL=postgres://postgres:${databasePassword}@$(PROJECT_NAME)_${input.databaseServiceName}:5432/$(PROJECT_NAME)`,
        `REDIS_URL=redis://default:${redisPassword}@$(PROJECT_NAME)_${input.redisServiceName}:6379`,
        `APP_URL=https://$(PRIMARY_DOMAIN)`,
        `SECRET_KEY=$(SECRET_KEY)`,
        `ADMIN_EMAIL=${input.adminEmail}`,
        `ADMIN_PASSWORD=${input.adminPassword}`,
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

  services.push({
    type: "postgres",
    data: {
      projectName: input.projectName,
      serviceName: input.databaseServiceName,
      password: databasePassword,
    },
  });

  services.push({
    type: "redis",
    data: {
      projectName: input.projectName,
      serviceName: input.redisServiceName,
      password: redisPassword,
    },
  });

  return { services };
}
```

---

## Pattern 4: App + MySQL

**Use when**: App specifically requires MySQL (not PostgreSQL compatible).

### Connection string format:
```
mysql://mysql:${databasePassword}@$(PROJECT_NAME)_${input.databaseServiceName}:3306/$(PROJECT_NAME)
```

### index.ts (DB portion)
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

---

## Pattern 5: Conditional Database (SQLite vs PostgreSQL)

**Use when**: App supports both embedded SQLite and external PostgreSQL.

### meta.yaml schema
```yaml
    databaseType:
      type: string
      title: Database Type
      oneOf:
        - enum: ["sqlite"]
          title: SQLite (simple, built-in)
        - enum: ["postgres"]
          title: PostgreSQL (recommended for production)
      default: sqlite
    databaseServiceName:
      type: string
      title: Database Service Name
      default: myapp-db
```

Note: Only include `databaseServiceName` in `required` if you want it always required. Better to make it optional and only use it when postgres is selected.

### index.ts
```typescript
import { Output, randomPassword, Services } from "~templates-utils";
import { Input } from "./meta";

export function generate(input: Input): Output {
  const services: Services = [];
  const isPostgres = input.databaseType === "postgres";
  const databasePassword = isPostgres ? randomPassword() : "";

  const env = [
    isPostgres
      ? `DATABASE_URL=postgres://postgres:${databasePassword}@$(PROJECT_NAME)_${input.databaseServiceName}:5432/$(PROJECT_NAME)`
      : `DATABASE_URL=sqlite:////app/data/db.sqlite`,
    `APP_URL=https://$(PRIMARY_DOMAIN)`,
    `SECRET_KEY=$(SECRET_KEY)`,
  ].join("\n");

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
          port: 8080,
        },
      ],
      env,
      mounts: [
        {
          type: "volume",
          name: "data",
          mountPath: "/app/data",
        },
      ],
    },
  });

  if (isPostgres) {
    services.push({
      type: "postgres",
      data: {
        projectName: input.projectName,
        serviceName: input.databaseServiceName,
        password: databasePassword,
      },
    });
  }

  return { services };
}
```

---

## Pattern 6: Multi-Service (App + Worker)

**Use when**: App has a separate worker/scheduler/queue processor container using the same image but a different command.

### meta.yaml additions
```yaml
    workerServiceName:
      type: string
      title: Worker Service Name
      default: myapp-worker
```

### index.ts
```typescript
import { Output, randomPassword, Services } from "~templates-utils";
import { Input } from "./meta";

export function generate(input: Input): Output {
  const services: Services = [];
  const databasePassword = randomPassword();
  const redisPassword = randomPassword();

  const sharedEnv = [
    `DATABASE_URL=postgres://postgres:${databasePassword}@$(PROJECT_NAME)_${input.databaseServiceName}:5432/$(PROJECT_NAME)`,
    `REDIS_URL=redis://default:${redisPassword}@$(PROJECT_NAME)_${input.redisServiceName}:6379`,
    `SECRET_KEY=$(SECRET_KEY)`,
  ].join("\n");

  // Main web app
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
          port: 3000,
        },
      ],
      env: sharedEnv,
      mounts: [
        {
          type: "volume",
          name: "data",
          mountPath: "/app/data",
        },
      ],
    },
  });

  // Background worker (same image, different command, no domain)
  services.push({
    type: "app",
    data: {
      projectName: input.projectName,
      serviceName: input.workerServiceName,
      source: {
        type: "image",
        image: input.appServiceImage,
      },
      deploy: {
        command: "worker", // replace with actual worker command
      },
      env: sharedEnv,
      mounts: [
        {
          type: "volume",
          name: "data",
          mountPath: "/app/data",
        },
      ],
    },
  });

  services.push({
    type: "postgres",
    data: {
      projectName: input.projectName,
      serviceName: input.databaseServiceName,
      password: databasePassword,
    },
  });

  services.push({
    type: "redis",
    data: {
      projectName: input.projectName,
      serviceName: input.redisServiceName,
      password: redisPassword,
    },
  });

  return { services };
}
```

---

## Common env var patterns

### App URL
```
APP_URL=https://$(PRIMARY_DOMAIN)
NEXTAUTH_URL=https://$(PRIMARY_DOMAIN)
SITE_URL=https://$(PRIMARY_DOMAIN)
```

### Database URLs
```
# PostgreSQL
DATABASE_URL=postgres://postgres:${dbPass}@$(PROJECT_NAME)_${input.dbServiceName}:5432/$(PROJECT_NAME)

# MySQL
DATABASE_URL=mysql://mysql:${dbPass}@$(PROJECT_NAME)_${input.dbServiceName}:3306/$(PROJECT_NAME)

# MongoDB
MONGO_URL=mongodb://mongodb:${dbPass}@$(PROJECT_NAME)_${input.dbServiceName}:27017
```

### Redis URLs
```
REDIS_URL=redis://default:${redisPass}@$(PROJECT_NAME)_${input.redisServiceName}:6379
CACHE_URL=redis://default:${redisPass}@$(PROJECT_NAME)_${input.redisServiceName}:6379/0
```

### Secrets
```
SECRET_KEY=$(SECRET_KEY)
JWT_SECRET=$(SECRET_KEY)
APP_SECRET=$(SECRET_KEY)
```

---

## Notes

- Service names in env vars must exactly match the `serviceName` you assign, prefixed by `$(PROJECT_NAME)_`
- Never hardcode passwords — always use `randomPassword()`
- The `projectName` field in service data comes from `input.projectName`, which is always available
- Volume names are local to the service — two services can have a volume named "data" without conflict
- If app needs startup delay (waits for DB), add: `deploy: { command: "sh -c 'sleep 5 && <original command>'" }`