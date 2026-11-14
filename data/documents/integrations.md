# FlowDesk — Fictional Product Documentation

> SAMPLE DATASET ONLY. FlowDesk is a fictional SaaS product for RAG testing. All plans, policies, dates, contact addresses and limits are invented; not legal advice or real company commitments.

Documentation version: 1.0 | Effective: 2026-11-01 | Currency: USD | Time zone: UTC unless specified.

# Integrations
## Slack
Slack integration is available on Pro and Business. Connect at Settings > Integrations > Slack. Only Owner or Admin can connect it. It posts task-assignment and due-date notifications to a selected channel. FlowDesk does not sync Slack messages into task comments.

## Google Drive
Google Drive file linking is available on Pro and Business. It creates links to files, not copies of the files. Access to linked Drive files is governed by Google Drive permissions.

## Webhooks
Outgoing webhooks are available on Pro and Business. Supported events: task.created, task.updated, task.completed. Webhooks retry failed deliveries up to three times with exponential backoff. The endpoint must use HTTPS.

## Not supported
Native Jira synchronization, Microsoft Teams integration, and WhatsApp messaging are not available in this release.
