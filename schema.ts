import { pgTable, serial, text, timestamp, numeric, integer, boolean } from 'drizzle-orm/pg-core';

// Tabela de Utilizadores / Sócios do Clube APPO
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  phone: text('phone'),
  membershipType: text('membership_type').notNull().default('Standard'), // Standard, Premium, VIP
  status: text('status').notNull().default('Ativo'), // Ativo, Pendente, Suspenso
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Tabela de Consultorias Financeiras e Planeamento 50/30/20
export const consultancies = pgTable('consultancies', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id),
  monthlyIncome: numeric('monthly_income', { precision: 12, scale: 2 }).notNull(),
  needsBudget: numeric('needs_budget', { precision: 12, scale: 2 }).notNull(), // 50%
  wantsBudget: numeric('wants_budget', { precision: 12, scale: 2 }).notNull(), // 30%
  savingsBudget: numeric('savings_budget', { precision: 12, scale: 2 }).notNull(), // 20%
  notes: text('notes'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Tabela de Ativos da BODIVA e Investimentos em Angola (Unitel, BAI, BFA, etc.)
export const bodivaAssets = pgTable('bodiva_assets', {
  id: serial('id').primaryKey(),
  ticker: text('ticker').notNull().unique(), // Ex: BAI, BFA, UNITEL
  companyName: text('company_name').notNull(),
  currentPrice: numeric('current_price', { precision: 12, scale: 2 }).notNull(),
  assetType: text('asset_type').notNull(), // Ações, Obrigações
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

// Tabela de Fórum e Artigos Educativos (Educação Financeira)
export const forumPosts = pgTable('forum_posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  content: text('content').notNull(),
  author: text('author').notNull(),
  category: text('category').notNull(), // Investimentos, Orçamento, BODIVA
  createdAt: timestamp('created_at').defaultNow().notNull(),
});