-- Database schema setup for Wealth Genie (FinPilot AI) MVP

-- Enable extension for generating UUIDs if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Create documents table
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- references auth.users.id (Supabase managed)
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN ('bank_statement', 'credit_card', 'loan', 'salary_slip')),
    status TEXT NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'failed')),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS for documents
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- 2. Create financial_profiles table
CREATE TABLE IF NOT EXISTS public.financial_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- references auth.users.id
    document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    profile_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS for financial_profiles
ALTER TABLE public.financial_profiles ENABLE ROW LEVEL SECURITY;

-- 3. Create recommendations table
CREATE TABLE IF NOT EXISTS public.recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- references auth.users.id
    financial_profile_id UUID NOT NULL REFERENCES public.financial_profiles(id) ON DELETE CASCADE,
    agent TEXT NOT NULL CHECK (agent IN ('debt_agent', 'savings_agent', 'budget_agent', 'ai_cfo')),
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS for recommendations
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;

-- 4. Create reports table
CREATE TABLE IF NOT EXISTS public.reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- references auth.users.id
    financial_profile_id UUID NOT NULL REFERENCES public.financial_profiles(id) ON DELETE CASCADE,
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS for reports
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

-- 5. Create analysis_jobs table
CREATE TABLE IF NOT EXISTS public.analysis_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL, -- references auth.users.id
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    report_id UUID REFERENCES public.reports(id) ON DELETE SET NULL
);

-- Enable RLS for analysis_jobs
ALTER TABLE public.analysis_jobs ENABLE ROW LEVEL SECURITY;

-- Row Level Security Policies (A user may only SELECT, INSERT, or UPDATE rows where user_id = auth.uid())

-- Documents Policies
CREATE POLICY documents_policy ON public.documents
    FOR ALL
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Financial Profiles Policies
CREATE POLICY financial_profiles_policy ON public.financial_profiles
    FOR ALL
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Recommendations Policies
CREATE POLICY recommendations_policy ON public.recommendations
    FOR ALL
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Reports Policies
CREATE POLICY reports_policy ON public.reports
    FOR ALL
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Analysis Jobs Policies
CREATE POLICY analysis_jobs_policy ON public.analysis_jobs
    FOR ALL
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());
