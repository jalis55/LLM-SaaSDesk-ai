# FlowDesk — Fictional Product Documentation

> SAMPLE DATASET ONLY. FlowDesk is a fictional SaaS product for RAG testing. All plans, policies, dates, contact addresses and limits are invented; not legal advice or real company commitments.

Documentation version: 1.0 | Effective: 2026-11-01 | Currency: USD | Time zone: UTC unless specified.

# API Reference — Fictional v1
API access is available on Pro and Business; Free has no API access. Base URL: https://api.flowdesk.example/v1 (example domain, not a live endpoint).

## Authentication
Send Authorization: Bearer <API_KEY>. Owners and Admins may create API keys at Settings > Developer > API Keys. Keys inherit workspace permissions; treat them as secrets.

## Endpoints
GET /projects — list projects (cursor pagination, default 20, maximum 100).
GET /projects/{project_id}/tasks — list tasks in a project.
POST /projects/{project_id}/tasks — create task with required title (1–200 characters).
PATCH /tasks/{task_id} — update task title, status, assignee, or due date.

## Rate limits
Pro: 60 requests per minute per workspace. Business: 300 requests per minute per workspace. Exceeding limits returns HTTP 429 with Retry-After header.

## Errors
400 invalid request; 401 invalid key; 403 insufficient permission; 404 resource not found; 429 rate limited; 500 server error.

## Limitations
No bulk-delete endpoint and no API for billing changes. API keys cannot be used to delete a workspace.
