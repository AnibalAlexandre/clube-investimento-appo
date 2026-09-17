import { Database } from "bun:sqlite";

const db = new Database("clube.db");

db.run("DROP TABLE IF EXISTS users");
db.run("DROP TABLE IF EXISTS bodiva_assets");
db.run("DROP TABLE IF EXISTS forum_posts");
db.run("DROP TABLE IF EXISTS club_info");
db.run("DROP TABLE IF EXISTS financials");
db.run("DROP TABLE IF EXISTS debts");
db.run("DROP TABLE IF EXISTS artigos");

db.run(`
  CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    membershipType TEXT,
    status TEXT
  )
`);

db.run(`
  CREATE TABLE bodiva_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    companyName TEXT,
    currentPrice REAL,
    currency TEXT,
    lastTrade TEXT,
    market TEXT,
    variation TEXT
  )
`);

db.run(`
  CREATE TABLE forum_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    author TEXT,
    category TEXT,
    date TEXT
  )
`);

db.run(`
  CREATE TABLE club_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT,
    title TEXT,
    content TEXT
  )
`);

db.run(`
  CREATE TABLE financials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    description TEXT,
    amount REAL,
    currency TEXT
  )
`);

db.run(`
  CREATE TABLE debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    debtorCode TEXT,
    realName TEXT,
    origin TEXT,
    amount REAL,
    currency TEXT,
    status TEXT,
    dueDate TEXT
  )
`);

db.run(`
  CREATE TABLE artigos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    categoria TEXT,
    tags TEXT,
    conteudo TEXT,
    data_publicacao TEXT,
    ficheiro_pdf_original TEXT
  )
`);

// Administrador
db.run(`
  INSERT INTO users (name, email, phone, membershipType, status) 
  VALUES ('Aníbal Alexandre Pereira da Costa', 'anibal.alexandre.2020@gmail.com', '+244 923 000 000', 'Presidente / Administrador', 'Ativo')
`);

// Ativos BODIVA
db.run(`INSERT INTO bodiva_assets (ticker, companyName, currentPrice, currency, lastTrade, market, variation) VALUES ('UNTLAAAA', 'UNITEL ACÇÃO', 32777.96, 'AOA', '17/09/2026', 'BODIVA DIRECTA', '+1,20%')`);
db.run(`INSERT INTO bodiva_assets (ticker, companyName, currentPrice, currency, lastTrade, market, variation) VALUES ('BAIAAAAA', 'BAI ACÇÃO', 90500.00, 'AOA', '17/09/2026', 'BODIVA DIRECTA', '0,00%')`);
db.run(`INSERT INTO bodiva_assets (ticker, companyName, currentPrice, currency, lastTrade, market, variation) VALUES ('BFAAAAAA', 'BFA ACÇÃO', 96541.73, 'AOA', '17/09/2026', 'BODIVA DIRECTA', '-0,45%')`);
db.run(`INSERT INTO bodiva_assets (ticker, companyName, currentPrice, currency, lastTrade, market, variation) VALUES ('ENSAAAAA', 'ENSA ACÇÃO', 20118.56, 'AOA', '17/09/2026', 'BODIVA DIRECTA', '+0,80%')`);

// Informações Institucionais
db.run(`INSERT INTO club_info (section, title, content) VALUES ('sobre', 'Quem Somos', 'O Clube de Investimento APPO é uma associação privada de membros unidos pelo rigor técnico e pela valorização patrimonial conjunta no mercado de capitais angolano.')`);
db.run(`INSERT INTO club_info (section, title, content) VALUES ('estatutos', 'Estatutos do Clube', 'O clube rege-se pelos princípios da transparência financeira, gestão prudente de reservas, cumprimento estrito das normas da CMF/BODIVA e proteção rigorosa dos interesses e da privacidade dos associados.')`);

// Dados Contabilísticos Corrigidos (Sem duplicações e com rubricas claras)
db.run(`INSERT INTO financials (category, description, amount, currency) VALUES ('Cap. Subscrito', 'Capital total subscrito pelos membros', 10000000.00, 'AOA')`);
db.run(`INSERT INTO financials (category, description, amount, currency) VALUES ('Cap. Realizado', 'Capital efetivamente integralizado', 5000000.00, 'AOA')`);
db.run(`INSERT INTO financials (category, description, amount, currency) VALUES ('Investimentos', 'Portefólio executado na BODIVA', 1866677.47, 'AOA')`);
db.run(`INSERT INTO financials (category, description, amount, currency) VALUES ('Ordens Vivas', 'Capital cativo em trânsito (revogável para liquidez)', 1286759.71, 'AOA')`);
db.run(`INSERT INTO financials (category, description, amount, currency) VALUES ('Liquidez', 'Saldo de negociação disponível', 1780884.96, 'AOA')`);
db.run(`INSERT INTO financials (category, description, amount, currency) VALUES ('Ativos Fixos', 'Computador institucional + Terreno do Clube', 3000000.00, 'AOA')`);

// Devedor
db.run(`INSERT INTO debts (debtorCode, realName, origin, amount, currency, status, dueDate) VALUES ('Devedor #001', 'AFAN (Associação / Entidade Financiamento)', 'Acordo de Regularização e Financiamento Institucional', 7500000.00, 'AOA', 'Em Regularização', '31/12/2026')`);

// Artigos
db.run(`
  INSERT INTO artigos (titulo, categoria, tags, conteudo, data_publicacao, ficheiro_pdf_original) 
  VALUES (
    'Princípios e Filosofia de Investimento do Clube APPO',
    'Institucional',
    'missão, valores, estatutos',
    '<b>Missão:</b> Promover a literacia financeira e o acesso disciplinado ao mercado de capitais angolano (BODIVA), construindo património de forma coletiva e sustentável.<br><br><b>Princípios:</b> Disciplina absoluta, horizonte de longo prazo, diversificação em ativos regulamentados e transparência patrimonial rigorosa.',
    '17/09/2026',
    'Manual_Fundacional_APPO.pdf'
  )
`);

console.log("Base de dados limpa e ajustada com rigor contabilístico!");