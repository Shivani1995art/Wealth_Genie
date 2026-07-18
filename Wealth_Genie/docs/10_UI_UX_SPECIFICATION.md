# UI / UX Specification

## Page Flow

```
Landing Page
  └─► Login / Register
        └─► Dashboard (empty state if no documents)
              └─► Upload Page
                    └─► Processing Page (polls /analysis/status/{job_id})
                          └─► Report Page
                                └─► Dashboard (updated with new data)
                                      └─► Chat Page
```

## Pages

| Route | Page | Notes |
|-------|------|-------|
| `/` | Landing | Marketing / entry point |
| `/login` | Login | Supabase email + password |
| `/register` | Register | Supabase email + password |
| `/dashboard` | Dashboard | Financial summary, latest report link |
| `/upload` | Upload | File picker + document type selector |
| `/processing/[jobId]` | Processing | Polls status; shows progress indicator |
| `/reports/[id]` | Report | Full AI CFO report |
| `/chat` | Chat | AI Chat grounded in latest financial profile |

## Processing Page Behaviour

The Processing page receives the `analysis_job_id` from the upload response, polls
`GET /analysis/status/{job_id}` every 3 seconds, and redirects to the Report page on
`status: completed`. On `status: failed`, it shows an error with a retry option.