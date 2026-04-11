# Templates: Project Setup

Load this for: package.json, tsconfig, node.json, SVG icon, config files, GitHub Actions.
All templates use `{{PLACEHOLDER}}` substitution — see SKILL.md for the full table.

---

## T1: package.json

```json
{
  "name": "n8n-nodes-{{service-slug}}",
  "version": "0.1.0",
  "description": "n8n community node for {{SERVICE}}",
  "license": "MIT",
  "keywords": ["n8n-community-node-package"],
  "author": { "name": "{{AUTHOR_NAME}}", "email": "{{AUTHOR_EMAIL}}" },
  "repository": { "type": "git", "url": "https://github.com/{{GITHUB_USER}}/n8n-nodes-{{service-slug}}.git" },
  "scripts": {
    "build": "n8n-node build",
    "dev": "n8n-node dev",
    "lint": "n8n-node lint",
    "lint:fix": "n8n-node lint --fix",
    "release": "n8n-node release",
    "prepublishOnly": "n8n-node prerelease"
  },
  "files": ["dist"],
  "n8n": {
    "n8nNodesApiVersion": 1,
    "strict": true,
    "credentials": ["dist/credentials/{{CREDENTIAL_NAME}}.credentials.js"],
    "nodes": ["dist/nodes/{{SERVICE}}/{{SERVICE}}.node.js"]
  },
  "devDependencies": {
    "@n8n/node-cli": "*",
    "eslint": "9.39.4",
    "prettier": "3.8.1",
    "release-it": "19.2.4",
    "typescript": "5.9.3"
  },
  "peerDependencies": { "n8n-workflow": "*" }
}
```

## T2: tsconfig.json

```json
{
  "compilerOptions": {
    "strict": true, "module": "commonjs", "moduleResolution": "node",
    "target": "es2019", "lib": ["es2019", "es2020", "es2022.error"],
    "removeComments": true, "useUnknownInCatchVariables": false,
    "noImplicitAny": true, "noImplicitReturns": true, "noUnusedLocals": true,
    "strictNullChecks": true, "esModuleInterop": true, "resolveJsonModule": true,
    "incremental": true, "declaration": true, "sourceMap": true,
    "skipLibCheck": true, "outDir": "./dist/"
  },
  "include": ["credentials/**/*", "nodes/**/*", "nodes/**/*.json", "package.json", "index.ts"]
}
```

## T17: node.json

```json
{
  "node": "n8n-nodes-{{service-slug}}.{{service}}",
  "nodeVersion": "1",
  "codexVersion": "1.0",
  "categories": ["Productivity"],
  "resources": { "primaryDocumentation": [{ "url": "{{DOCS_URL}}" }] },
  "alias": ["{{SERVICE}}", "{{service-slug}}"]
}
```

## T18: SVG icon — nodes/{{SERVICE}}/{{service-slug}}.svg

> **CRITICAL placement**: The SVG MUST live next to the entry `.node.ts` file
> (`nodes/{{SERVICE}}/{{service-slug}}.svg`). n8n resolves `file:xxx.svg` relative to the
> file that defines the `icon` property. Do NOT put it in a separate `icons/` folder.
>
> **SVG format**: Use simple solid fills. Avoid `fill="none"` on the root element, complex
> gradients, or dark-on-transparent designs — these render as invisible/broken on n8n's dark UI.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 60">
  <rect width="60" height="60" rx="12" fill="#6366f1"/>
  <text x="30" y="38" font-family="sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="white">{{SERVICE_INITIAL}}</text>
</svg>
```

## T29: index.ts — npm entry point

Required for npm-installed packages so n8n can resolve the module.

```typescript
// index.ts (project root)
export { {{CREDENTIAL_NAME}} } from './credentials/{{CREDENTIAL_NAME}}.credentials';
```

Add `"main": "dist/index.js"` and `"types": "dist/index.d.ts"` to `package.json`.
Add `"index.ts"` to the `include` array in `tsconfig.json`.

## T30: .npmignore

Excludes source files from the published npm package — only `dist/` should be published.

```
# Source
nodes/
credentials/
index.ts
tsconfig.json
*.tsbuildinfo

# Dev config
.eslintrc*
eslint.config.*
.prettierrc*
.editorconfig

# Git/CI
.git/
.github/
.gitignore

# Dev docs
CHANGELOG.md
DEV-README.md
PLAN-*.md
TEST-*.md
test/

# IDE
.vscode/
.idea/
```

**Verification after build:**
```bash
npm pack --dry-run
```
This shows exactly what files will be in the published package. Verify:
- Only `dist/` contents, `package.json`, `README.md`, and `LICENSE` are included
- No source `.ts` files, no dev configs, no `.github/` workflows

## T19–T21: Config files

**.gitignore:**
```
node_modules/
dist/
.eslintcache
*.tsbuildinfo
```

**.eslintrc.mjs:**
```js
import { defineConfig } from '@n8n/node-cli';
export default defineConfig({ ignorePatterns: ['dist/**', '*.js'] });
```

**.prettierrc.js:**
```js
module.exports = { semi: true, singleQuote: true, printWidth: 100, tabWidth: 2, trailingComma: 'all' };
```

## T22–T23: GitHub Actions

**ci.yml:**
```yaml
name: CI
on:
  push: { branches: [main, master] }
  pull_request: { branches: [main, master] }
jobs:
  build-and-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm run build
      - run: npm run lint
```

**publish.yml:**
```yaml
name: Publish
on:
  push: { tags: ['v*'] }
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions: { contents: read, id-token: write }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', registry-url: 'https://registry.npmjs.org', cache: 'npm' }
      - run: npm ci
      - run: npm publish --provenance --access public
        env: { NODE_AUTH_TOKEN: '${{ secrets.NPM_TOKEN }}' }
```
