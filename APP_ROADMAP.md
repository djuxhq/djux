# Djux App Roadmap

This file tracks planned official Djux apps and the order to build them.

## Phase 1 - Foundation

- [x] Finalize app manifest format for versioning, dependencies, settings patches, migrations, and update behavior.
- [x] Define app naming rules and package layout conventions.
- [x] Add `djux update <app>` design notes before more apps are released.
- [x] Create smoke-test checklist for every official app.
- [x] Publish updated registry entries under `djuxhq` URLs.

## Phase 2 - Core Django Apps

- [x] `auth` - JWT auth, register, login, refresh, logout, me endpoint.
- [ ] `users` - user profiles, avatars, preferences.
- [ ] `teams` - organizations, team members, invitations, roles.
- [ ] `permissions` - reusable RBAC and permission groups.
- [ ] `files` - uploads, storage backend helpers, signed URLs.
- [ ] `emails` - transactional email templates and sending.
- [ ] `notifications` - in-app and email notifications.
- [ ] `audit-log` - activity tracking and admin audit trails.
- [ ] `settings` - user, team, and app settings API.
- [ ] `api-keys` - API keys, scopes, rotation, revocation.

## Phase 3 - Product Apps

- [ ] `blog` - posts, categories, tags, comments.
- [ ] `cms` - pages, blocks, SEO metadata.
- [ ] `contact` - contact form and lead capture.
- [ ] `newsletter` - subscribers, lists, exports.
- [ ] `billing` - Stripe plans, subscriptions, webhooks.
- [ ] `payments` - payment intents, invoices, receipts.
- [ ] `commerce` - products, carts, orders.
- [ ] `bookings` - appointments, availability, calendar slots.
- [ ] `comments` - generic comments system.
- [ ] `reviews` - ratings and reviews.
- [ ] `analytics` - event tracking and basic metrics.
- [ ] `webhooks` - inbound and outbound webhook framework.

## Phase 4 - Basic AI Templates

- [ ] `ai-models` - provider/model registry, model selection, pricing metadata.
- [ ] `ai-prompts` - prompt templates, variables, versions.
- [ ] `ai-chat` - chat endpoint, conversations, messages.
- [ ] `ai-completions` - simple text generation API.
- [ ] `ai-usage` - token usage, cost tracking, rate limits.
- [ ] `ai-moderation` - moderation checks and policy logs.

## Phase 5 - Advanced AI Apps

- [ ] `ai-embeddings` - embedding generation and storage hooks.
- [ ] `ai-rag` - documents, chunks, embeddings, retrieval API.
- [ ] `ai-doc-chat` - upload documents and chat over them.
- [ ] `ai-assistant` - assistant/thread/message model with run history.
- [ ] `ai-agents` - agent definitions, tools, runs, steps.
- [ ] `ai-images` - image generation request/response storage.
- [ ] `ai-evals` - prompt/model evaluation datasets and runs.

## Phase 6 - Update And Distribution Workflow

- [ ] Add installed app version tracking to `djux.project.json`.
- [ ] Implement `djux outdated`.
- [ ] Implement `djux update <app>`.
- [ ] Detect locally modified app files before update.
- [ ] Generate `.new` files or conflict reports instead of overwriting user changes.
- [ ] Support app-level migration notes and changelogs.
- [ ] Add registry checksum or release metadata for safer downloads.

## Phase 7 - Quality Bar For Each App

Each official app should include:

- [ ] `djux.json` manifest.
- [ ] README with endpoints and installation notes.
- [ ] Django system check passes after install.
- [ ] Migration test passes.
- [ ] API smoke tests pass.
- [ ] Minimal serializer/view tests where applicable.
- [ ] Registry entry points to `djuxhq` repository and download URL.

## Recommended Build Order

1. `auth`
2. `users`
3. `api-keys`
4. `ai-models`
5. `ai-prompts`
6. `ai-chat`
7. `ai-usage`
8. `files`
9. `ai-embeddings`
10. `ai-rag`
