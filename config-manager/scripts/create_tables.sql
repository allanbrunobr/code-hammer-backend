-- 1. Users (base table, no dependencies)
CREATE TABLE IF NOT EXISTS public.users (
    id uuid NOT NULL,
    name character varying NOT NULL,
    email character varying NOT NULL,
    firebase_uid character varying,
    stripe_customer_id character varying,
    language character varying,
    country character varying,
    recovery_token character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    PRIMARY KEY (id)
);

-- 2. Plans (base table, no dependencies)
CREATE TABLE IF NOT EXISTS public.plans (
    id uuid NOT NULL,
    name character varying NOT NULL,
    description character varying,
    file_limit integer,
    status character varying,
    stripe_price_id character varying,
    stripe_product_id character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    PRIMARY KEY (id)
);

-- 3. Periods (base table, no dependencies)
CREATE TABLE IF NOT EXISTS public.periods (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    name character varying NOT NULL,
    months integer NOT NULL,
    discount_percentage integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    PRIMARY KEY (id)
);

-- 4. Plan_Periods (depends on plans and periods)
CREATE TABLE IF NOT EXISTS public.plan_periods (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    plan_id uuid NOT NULL,
    period_id uuid NOT NULL,
    price numeric NOT NULL,
    currency character varying NOT NULL,
    stripe_price_id character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    PRIMARY KEY (id),
    CONSTRAINT plan_periods_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.plans (id),
    CONSTRAINT plan_periods_period_id_fkey FOREIGN KEY (period_id) REFERENCES public.periods (id)
);

-- 5. Subscriptions (depends on users and plans)
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    plan_id uuid NOT NULL,
    stripe_subscription_id character varying,
    status character varying NOT NULL,
    auto_renew boolean,
    remaining_file_quota integer,
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    PRIMARY KEY (id),
    CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (id),
    CONSTRAINT subscriptions_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.plans (id)
);

-- 6. Billings (depends on users)
CREATE TABLE IF NOT EXISTS public.billings (
    id uuid NOT NULL,
    user_id uuid,
    plan_id character varying,
    amount character varying NOT NULL,
    currency character varying,
    transaction_id character varying,
    payment_status character varying,
    payment_method character varying,
    payment_date character varying,
    stripe_payment_intent_id character varying,
    stripe_invoice_id character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    PRIMARY KEY (id),
    CONSTRAINT billings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (id)
);

-- 7. Integrations (depends on users)
CREATE TABLE IF NOT EXISTS public.integrations (
    id uuid NOT NULL,
    user_id uuid,
    name character varying NOT NULL,
    repository character varying,
    repository_url character varying,
    repository_user character varying,
    repository_token character varying,
    api_key character varying,
    quality_level character varying,
    analyze_types character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    PRIMARY KEY (id),
    CONSTRAINT integrations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (id)
);

