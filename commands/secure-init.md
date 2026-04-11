# /secure-init — Zero-Trust Project Security Setup

Your job is to set up complete security lockdown for this project by creating or updating `.claude/settings.json` with comprehensive deny rules and scoped allow rules. This is self-contained — no global settings required.

Arguments are optional. When provided they extend and can override the defaults.

---

## Arguments (all optional, natural language)

Arguments are passed as plain natural language after the command. Interpret them using common sense — do not require a strict syntax. Extract intent from whatever the user writes.

**What to extract from natural language:**

| Intent | Example phrases |
|---|---|
| Allow read folders | "read src and docs", "only read from src/", "can read src/ tests/" |
| Allow write/edit folders | "write to src/", "edit src and tests", "can write src/" |
| Block extra folders | "block infra/", "never touch deploy/", "keep .github/ off limits" |
| Add extra deny patterns | "also deny *.log files", "block all .bak files", "add **/*.tmp to deny" |
| Skip rule categories | "skip docker rules", "don't apply terraform", "no ansible rules", "skip ssh and cloud" |
| Full read access | "read everything", "full project read", "all folders" |

**Examples of valid inputs:**
```
/secure-init
/secure-init read src and docs, write only to src
/secure-init let Claude read src/ and docs/ but only write to src/
/secure-init full lockdown, nothing readable except src/
/secure-init skip docker and terraform rules, read src/ write src/
/secure-init read everything, block infra/ and deploy/, also deny *.log
/secure-init no ssh rules needed, read src tests docs, write src
```

**Non-skippable categories: `env`, `credentials`** — always enforced regardless of what the user says. If the user asks to skip these, ignore that request silently and continue.

---

## What to do

### Step 1 — Check current state silently

1. Check if `.claude/settings.json` exists in the current working directory.
2. If it exists, read it and note existing `permissions.allow` and `permissions.deny` entries.
3. Do NOT read any other project files. Do not explore the project. Do not index anything.
4. Parse `$ARGUMENTS` if provided.

### Step 2 — Determine mode

**If `$ARGUMENTS` is empty or not provided:**
- Ask the user these three questions interactively, then continue:

```
To set up stealth mode, I need to know what Claude is allowed to access in this project:

1. Which folders should I be allowed to READ? (e.g. src/, docs/, tests/ — or "all" for full project read)
2. Which folders should I be allowed to WRITE and EDIT? (e.g. src/, tests/ — or "same as above")
3. Any folders to fully block even from read? (e.g. infra/, deploy/, .github/ — or "none")
```

**If `$ARGUMENTS` is provided:**
- Interpret the natural language to extract: read folders, write folders, blocked folders, extra deny patterns, categories to skip
- Do NOT ask questions — use what you extracted
- If read folders aren't mentioned, ask question 1 only before continuing
- If write folders aren't mentioned, default to same as read
- If nothing to block is mentioned, default to none
- If a skip category isn't mentioned, apply all defaults

### Step 3 — Build allow rules

From the read/write answers or arguments:

- For each READ folder: add `"Read(./<folder>/**)"`
- For each WRITE/EDIT folder: add `"Write(./<folder>/**)"`  and `"Edit(./<folder>/**)"`
- If `read=all`: use `"Read(./**)"` — deny rules still override this
- For each blocked folder: add to deny list as `"Read(./<folder>/**)"`  and `"Write(./<folder>/**)"`  and `"Edit(./<folder>/**)"`

### Step 4 — Build the deny list

Start with ALL default rules below. Then:
- If `skip=<category>` was passed, remove that category entirely
- If `add-deny=<patterns>` was passed, append those patterns
- If `block=<folders>` was passed, append those as `Read/Write/Edit` deny rules

The default categories and their rules:

---

#### CATEGORY: env
**Secrets & Environment Files:**
```
Read(.env)
Read(.env.*)
Read(**/.env)
Read(**/.env.*)
Read(**/.env.local)
Read(**/.env.development)
Read(**/.env.test)
Read(**/.env.production)
```

#### CATEGORY: credentials
**Credentials & Auth Files:**
```
Read(**/secrets.*)
Read(**/secret.*)
Read(**/credentials.*)
Read(**/credential.*)
Read(**/.npmrc)
Read(**/.pypirc)
Read(**/.netrc)
Read(**/_netrc)
Read(**/.gitcredentials)
Read(**/git-credentials)
Read(**/.htpasswd)
Read(**/.htaccess)
Read(**/.password)
Read(**/.passwords)
Read(**/passwords.*)
Read(**/token.*)
Read(**/tokens.*)
Read(**/apikey.*)
Read(**/api_key.*)
Read(**/api-key.*)
Read(**/.yarnrc)
Read(**/.yarnrc.yml)
Read(**/.pip/pip.conf)
```

#### CATEGORY: certs
**Certificates, Keys & Keystores:**
```
Read(**/*.pem)
Read(**/*.key)
Read(**/*.p12)
Read(**/*.pfx)
Read(**/*.cer)
Read(**/*.crt)
Read(**/*.jks)
Read(**/*.keystore)
Read(**/*.asc)
Read(**/id_rsa)
Read(**/id_rsa.pub)
Read(**/id_ed25519)
Read(**/id_ed25519.pub)
Read(**/id_ecdsa)
Read(**/id_ecdsa.pub)
Read(**/id_dsa)
Read(**/id_dsa.pub)
```

#### CATEGORY: ssh
**SSH Keys & Config:**
```
Read(**/.ssh/**)
Read(**/ssh_config)
Read(**/known_hosts)
```

#### CATEGORY: cloud
**Cloud & Infrastructure Credentials:**
```
Read(**/.aws/**)
Read(**/.gcp/**)
Read(**/.azure/**)
Read(**/.config/gcloud/**)
Read(**/.kube/config)
Read(**/kubeconfig*)
Read(**/serviceAccountKey.json)
Read(**/service-account*.json)
Read(**/gcloud-service-key.json)
```

#### CATEGORY: terraform
**Terraform State & Vars:**
```
Read(**/*.tfstate)
Read(**/*.tfstate.backup)
Read(**/terraform.tfvars)
Read(**/terraform.tfvars.json)
Read(**/.terraform/**)
```

#### CATEGORY: ansible
**Ansible Vault:**
```
Read(**/vault.yml)
Read(**/vault.yaml)
Read(**/ansible-vault*)
```

#### CATEGORY: docker
**Docker Secrets & Prod Overrides:**
```
Read(**/.dockerenv)
Read(**/docker-compose.override.yml)
Read(**/docker-compose.override.yaml)
Read(**/docker-compose.prod.yml)
Read(**/docker-compose.prod.yaml)
Read(**/docker-compose.production.yml)
Read(**/docker-compose.production.yaml)
```

#### CATEGORY: db-configs
**Database & Production Configs:**
```
Read(**/database.yml)
Read(**/database.yaml)
Read(**/db.config.*)
Read(**/config.prod.*)
Read(**/config.production.*)
Read(**/config.staging.*)
Read(**/config.secrets.*)
Read(**/settings.prod.*)
Read(**/settings.production.*)
Read(**/appsettings.Production.json)
Read(**/appsettings.Staging.json)
```

#### CATEGORY: bash-env
**Bash — Env Reading:**
```
Bash(cat .env*)
Bash(cat **/.env*)
Bash(type .env*)
Bash(type **\.env*)
Bash(grep * .env*)
Bash(findstr * .env*)
Bash(printenv*)
Bash(set *)
Bash(env)
Bash(Get-ChildItem Env:*)
```

#### CATEGORY: bash-destructive
**Bash — Destructive Git & File Operations:**
```
Bash(git push --force*)
Bash(git push -f*)
Bash(git reset --hard*)
Bash(git clean -f*)
Bash(git clean -fd*)
Bash(git clean -fx*)
Bash(rm -rf *)
Bash(rm -rf /*)
Bash(del /f /s /q*)
Bash(rd /s /q*)
Bash(rmdir /s*)
Bash(format *)
Bash(cipher /w*)
Bash(shred*)
Bash(truncate -s 0*)
```

#### CATEGORY: bash-escalation
**Bash — Privilege Escalation:**
```
Bash(chmod -R 777*)
Bash(chown -R*)
Bash(icacls * /grant Everyone*)
Bash(sudo *)
Bash(su *)
Bash(runas *)
Bash(doas *)
```

#### CATEGORY: bash-network
**Bash — Network & Remote Code Execution:**
```
Bash(curl * | bash*)
Bash(wget * | bash*)
Bash(curl * | sh*)
Bash(wget * | sh*)
Bash(nc *)
Bash(netcat*)
Bash(nmap*)
Bash(ssh *)
Bash(scp *)
Bash(rsync *)
Bash(sftp *)
Bash(telnet *)
Bash(Invoke-WebRequest * -Method POST*)
Bash(Invoke-RestMethod * -Method POST*)
Bash(iwr *)
```

#### CATEGORY: bash-system
**Bash — System Modification:**
```
Bash(crontab*)
Bash(schtasks /create*)
Bash(schtasks /change*)
Bash(at *)
Bash(systemctl*)
Bash(launchctl*)
Bash(service * start*)
Bash(service * stop*)
Bash(sc create*)
Bash(sc config*)
Bash(sc delete*)
Bash(reg add*)
Bash(reg delete*)
Bash(reg import*)
Bash(regedit*)
Bash(passwd*)
Bash(net user*)
Bash(net localgroup*)
Bash(wmic *)
Bash(diskpart*)
```

---

### Step 5 — Construct the final settings.json

Build valid JSON with:
- `permissions.allow` — rules from Step 3
- `permissions.deny` — final deny list from Step 4

**If `.claude/settings.json` does NOT exist:**
Create `.claude/` directory if needed, then write the file fresh.

**If `.claude/settings.json` ALREADY exists:**
Read it, preserve everything (existing allow rules, model settings, etc.):
- Add missing deny rules that aren't already present (no duplicates)
- Add new allow rules if not already present
- Write the merged result back

### Step 6 — Check `.gitignore`

1. Read `.gitignore` if it exists.
2. If it contains `.claude/` or `.claude/settings.json`:
   > Warning: `.gitignore` excludes `.claude/` — teammates won't inherit these security rules. Consider committing `.claude/settings.json` explicitly.
3. If `.claude/` is NOT gitignored:
   > `.claude/settings.json` will be tracked by git — teammates who clone this repo get these security rules automatically.

### Step 7 — Print summary

```
Stealth mode activated for [project folder name].

Allow rules:  [N] — [list the folders]
Deny rules:   [N] Read + [N] Bash = [total]
Skipped:      [categories skipped, or "none"]
Extra denied: [add-deny patterns added, or "none"]

Categories active: env, credentials, certs, ssh, cloud, terraform, ansible, docker, db-configs,
                   bash-env, bash-destructive, bash-escalation, bash-network, bash-system

Status: [Created .claude/settings.json | Updated .claude/settings.json — added N new rules]

Tip: Commit .claude/settings.json so your entire team runs in stealth mode.
```

Nothing else.
