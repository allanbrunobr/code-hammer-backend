INSERT INTO "public"."users" ("id", "name", "email", "recovery_token", "country", "language", "firebase_uid", "stripe_customer_id", "created_at", "updated_at") VALUES ('f70cf81c-3d1d-4cf0-8598-91be25d49b1e', 'Allan Bruno', 'allanbruno@gmail.com', null, null, null, '51uJzT0odZXaOT2wf2FCsr42GJ62', null, '2025-02-16 02:38:16.980516+00', '2025-03-05 13:17:53.194545+00');

INSERT INTO "public"."plans" ("id", "name", "file_limit", "status", "description", "stripe_price_id", "stripe_product_id", "created_at", "updated_at")
VALUES
('0bc01dd0-f3f1-48db-88ff-2120e3f68c64', 'Standard', '500', 'active', 'Plano intermediário com recursos avançados para equipes pequenas e médias. Inclui análise de código completa, suporte prioritário e integrações extras.', 'price_1QzjDCKg8PaHMKkrZNodMeZs', 'prod_RtWFJQ3fRXkiPP', '2025-02-28 02:11:51.251877+00', null),
('4168b9bb-027d-4985-b227-0d54ed4eff96', 'Pro', '500', 'active', 'Plano premium com todos os recursos disponíveis, ideal para grandes equipes e empresas. Inclui análise de código ilimitada, suporte 24/7, todas as integrações e recursos exclusivos.', 'price_1QzjDAKg8PaHMKkrdBDOwrh1', 'prod_RtWFWVM2bAf4se', '2025-02-28 02:11:51.251877+00', null),
('4fb7a959-cd1d-40f3-a73d-e043604b3f0a', 'Gratuito', '50', 'active', 'Plano gratuito com recursos básicos para experimentar a plataforma. Inclui análise de código limitada e acesso às funcionalidades essenciais.', null, null, '2025-02-28 02:11:51.251877+00', null);
INSERT INTO "public"."subscriptions" ("id", "status", "start_date", "end_date", "remaining_file_quota", "auto_renew", "plan_id", "user_id", "stripe_subscription_id", "created_at", "updated_at")
VALUES
('a4e36568-8afa-436e-a01a-0034448125c6', 'active', '2025-03-01 18:46:41.845742', '2026-03-01 18:46:41.845742', '405', 'true', '4168b9bb-027d-4985-b227-0d54ed4eff96', 'f70cf81c-3d1d-4cf0-8598-91be25d49b1e', null, '2025-03-01 18:46:41.845742+00', '2025-03-05 18:01:41.621713+00');

INSERT INTO "public"."periods" ("id", "name", "months", "discount_percentage", "created_at", "updated_at") VALUES ('2e8e9e14-70a8-4522-908d-855216acbf29', 'quarterly', '3', '10', '2025-02-28 02:10:21.92911+00', null), ('97a95920-192d-4c4f-b552-3d9a59c6ca50', 'semiannual', '6', '20', '2025-02-28 02:10:21.92911+00', null), ('ddc3f894-a68d-4763-962f-954ca3457968', 'monthly', '1', '0', '2025-02-28 02:10:21.92911+00', null);


INSERT INTO "public"."plan_periods" ("id", "plan_id", "period_id", "price", "currency", "stripe_price_id", "created_at", "updated_at")
VALUES
('01b9fb99-71f0-461c-9bf3-27c9e2a2aa63', '0bc01dd0-f3f1-48db-88ff-2120e3f68c64', '2e8e9e14-70a8-4522-908d-855216acbf29', '134.73', 'BRL', 'price_1QzjDBKg8PaHMKkrsVBnmY2B', '2025-02-28 02:13:28.818503+00', null),
('0e250b5a-e8e8-431f-aec9-796734bfe1ca', '0bc01dd0-f3f1-48db-88ff-2120e3f68c64', '97a95920-192d-4c4f-b552-3d9a59c6ca50', '239.52', 'BRL', 'price_1QzjDBKg8PaHMKkrY8lXcOTl', '2025-02-28 02:13:28.818503+00', null),
('0f1267f7-4211-4794-8386-442f0b456e9e', '4168b9bb-027d-4985-b227-0d54ed4eff96', 'ddc3f894-a68d-4763-962f-954ca3457968', '99.90', 'BRL', 'price_1QzjDAKg8PaHMKkrdBDOwrh1', '2025-02-28 02:13:28.818503+00', null),
('2eb29d7d-2688-4ddc-84bb-7f0ca3a462b2', '4fb7a959-cd1d-40f3-a73d-e043604b3f0a', 'ddc3f894-a68d-4763-962f-954ca3457968', '0.00', 'BRL', null, '2025-02-28 02:13:28.818503+00', null),
('7a2ec236-e313-4ec1-928b-4f805e71d58c', '4168b9bb-027d-4985-b227-0d54ed4eff96', '97a95920-192d-4c4f-b552-3d9a59c6ca50', '479.52', 'BRL', 'price_1QzjDAKg8PaHMKkrCyBsWF17', '2025-02-28 02:13:28.818503+00', null),
('af35c7fd-5860-414d-adfe-b23b81cc135f', '0bc01dd0-f3f1-48db-88ff-2120e3f68c64', 'ddc3f894-a68d-4763-962f-954ca3457968', '49.90', 'BRL', 'price_1QzjDCKg8PaHMKkrZNodMeZs', '2025-02-28 02:13:28.818503+00', null),
('b1304631-6430-476f-91ff-2fc8547caaeb', '4168b9bb-027d-4985-b227-0d54ed4eff96', '2e8e9e14-70a8-4522-908d-855216acbf29', '269.73', 'BRL', 'price_1QzjDAKg8PaHMKkrOHlWk6QP', '2025-02-28 02:13:28.818503+00', null);
INSERT INTO "public"."integrations" ("id", "name", "api_key", "repository", "repository_user", "repository_token", "repository_url", "analyze_types", "quality_level", "user_id", "created_at", "updated_at") VALUES ('7942054e-ca2f-43b6-b50b-b78f38fa1c35', 'gcloud-api', '', 'github', '', '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', 'github.com/allanbrunobr/gcp-frontend-react', 'componentizacao,otimizacaoBigO', '', 'f70cf81c-3d1d-4cf0-8598-91be25d49b1e', '2025-03-02 04:04:23.234764+00', '2025-03-03 00:53:59.477905+00');

INSERT INTO "public"."billings" ("id", "amount", "currency", "payment_date", "payment_method", "payment_status", "transaction_id", "plan_id", "user_id", "stripe_invoice_id", "stripe_payment_intent_id", "created_at", "updated_at") VALUES ('a1c7f547-cb84-47b4-8f77-8c7db0b5a193', '99.90', null, '2025-03-02 03:13:35.153458+00', null, 'completed', null, '4168b9bb-027d-4985-b227-0d54ed4eff96', 'f70cf81c-3d1d-4cf0-8598-91be25d49b1e', null, null, '2025-03-02 03:13:35.153458+00', null);
