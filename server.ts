import { Database } from "bun:sqlite";

const db = new Database("clube.db");

const server = Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === "/api/data" && req.method === "GET") {
      const users = db.query("SELECT * FROM users").all();
      const assets = db.query("SELECT * FROM bodiva_assets").all();
      const posts = db.query("SELECT * FROM forum_posts").all();
      const info = db.query("SELECT * FROM club_info").all();
      const financials = db.query("SELECT * FROM financials").all();
      const rawDebts = db.query("SELECT * FROM debts").all();
      const artigos = db.query("SELECT * FROM artigos ORDER BY id DESC").all();

      const publicDebts = rawDebts.map((d: any) => ({
        id: d.id,
        debtorCode: d.debtorCode,
        origin: d.origin,
        amount: d.amount,
        currency: d.currency,
        status: d.status,
        dueDate: d.dueDate
      }));

      return Response.json({ users, assets, posts, info, financials, debts: publicDebts, rawDebts, artigos });
    }

    if (url.pathname === "/api/join" && req.method === "POST") {
      const body = await req.json() as { name: string; email: string; phone: string; membershipType: string };
      db.run(
        "INSERT INTO users (name, email, phone, membershipType, status) VALUES (?, ?, ?, ?, ?)",
        [body.name, body.email, body.phone, body.membershipType || 'Membro Interessado', 'Pendente de Contacto']
      );
      return Response.json({ success: true });
    }

    if (url.pathname === "/api/financial" && req.method === "POST") {
      const body = await req.json() as { type: string; category: string; description: string; amount: number; debtorCode?: string; realName?: string; dueDate?: string };
      if (body.type === 'debt') {
        db.run(
          "INSERT INTO debts (debtorCode, realName, origin, amount, currency, status, dueDate) VALUES (?, ?, ?, ?, ?, ?, ?)",
          [body.debtorCode || 'Devedor #00X', body.realName || 'Confidencial', body.description, body.amount, 'AOA', 'Pendente', body.dueDate || '31/12/2026']
        );
      } else {
        db.run(
          "INSERT INTO financials (category, description, amount, currency) VALUES (?, ?, ?, ?)",
          [body.category, body.description, body.amount, 'AOA']
        );
      }
      return Response.json({ success: true });
    }

    if (url.pathname === "/api/asset" && req.method === "POST") {
      const body = await req.json() as { ticker: string; companyName: string; currentPrice: number; variation?: string };
      db.run(
        "INSERT INTO bodiva_assets (ticker, companyName, currentPrice, currency, lastTrade, market, variation) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [body.ticker, body.companyName, body.currentPrice, 'AOA', '17/09/2026', 'BODIVA DIRECTA', body.variation || '0,00%']
      );
      return Response.json({ success: true });
    }

    if (url.pathname === "/api/artigos/upload" && req.method === "POST") {
      const body = await req.json() as { titulo: string; categoria: string; tags: string; conteudo: string; ficheiro_pdf_original?: string };
      const dataAtual = new Date().toLocaleDateString('pt-PT');
      db.run(
        "INSERT INTO artigos (titulo, categoria, tags, conteudo, data_publicacao, ficheiro_pdf_original) VALUES (?, ?, ?, ?, ?, ?)",
        [body.titulo, body.categoria || 'Educação', body.tags || 'geral', body.conteudo, dataAtual, body.ficheiro_pdf_original || 'Documento.pdf']
      );
      return Response.json({ success: true });
    }

    return new Response(
      `<!DOCTYPE html>
      <html lang="pt">
      <head>
          <meta charset="UTF-8">
          <title>Clube de Investimento APPO</title>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
          <style>
              body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; color: #333333; margin: 0; padding: 0; line-height: 1.6; }
              header { background: #ffffff; border-bottom: 1px solid #e0e0e0; padding: 25px 20px; text-align: center; }
              header h1 { margin: 0; font-size: 2.2em; color: #0a2540; font-weight: 700; }
              header p { margin: 5px 0 0 0; color: #555555; font-size: 1.1em; }
              
              .nav-tabs { display: flex; justify-content: center; background: #ffffff; border-bottom: 1px solid #ddd; padding: 0 20px; gap: 5px; flex-wrap: wrap; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
              .tab-btn { background: none; border: none; padding: 15px 20px; font-size: 0.95em; font-weight: 600; color: #555; cursor: pointer; border-bottom: 3px solid transparent; transition: all 0.2s; }
              .tab-btn:hover, .tab-btn.active { color: #0066cc; border-bottom: 3px solid #0066cc; }
              .tab-btn.admin-tab { color: #b91c1c; }
              .tab-btn.admin-tab.active { border-bottom: 3px solid #b91c1c; }

              .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
              .tab-content { display: none; }
              .tab-content.active { display: block; }

              .card { background: #ffffff; border: 1px solid #e1e4e8; padding: 30px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); margin-bottom: 25px; }
              h2 { color: #0a2540; border-bottom: 2px solid #f0f2f5; padding-bottom: 10px; margin-top: 0; font-size: 1.3em; }
              table { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; }
              th, td { border: 1px solid #e1e4e8; padding: 12px 15px; text-align: left; font-size: 0.95em; }
              th { background: #f8fafc; color: #333; font-weight: 600; }
              tr:nth-child(even) { background: #fafbfc; }
              
              .chart-container { position: relative; width: 100%; max-width: 700px; margin: 20px auto; height: 350px; }
              
              .form-grid { background: #f8fafc; padding: 20px; border-radius: 6px; border: 1px solid #e1e4e8; display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
              .form-grid.full { grid-template-columns: 1fr; }
              input, select, textarea { background: #ffffff; color: #333; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; width: 100%; box-sizing: border-box; font-size: 1em; }
              button { background: #0066cc; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 1em; transition: background 0.2s; }
              button:hover { background: #0052a3; }
              .btn-success { background: #10b981; }
              .btn-success:hover { background: #059669; }
              .btn-danger { background: #ef4444; padding: 6px 12px; font-size: 0.85em; }
              .btn-full { grid-column: span 2; }
              
              .badge { background: #e0f2fe; color: #0369a1; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 600; }
              .badge-pending { background: #fef3c7; color: #d97706; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 600; }
              .badge-admin { background: #fee2e2; color: #b91c1c; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 600; }
              
              /* Cores dinâmicas para variações bolsistas */
              .var-pos { color: #10b981; font-weight: 600; }
              .var-neg { color: #ef4444; font-weight: 600; }
              .var-neutro { color: #64748b; font-weight: 600; }

              .article-card { background: #ffffff; border: 1px solid #e1e4e8; border-left: 4px solid #0066cc; padding: 20px; border-radius: 6px; margin-bottom: 20px; }
              .article-card h3 { margin: 0 0 8px 0; color: #0a2540; font-size: 1.2em; }
              .article-meta { font-size: 0.85em; color: #666; margin-top: 12px; display: flex; gap: 15px; flex-wrap: wrap; align-items: center; }
              
              .login-box { max-width: 400px; margin: 40px auto; background: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e1e4e8; text-align: center; }
          </style>
      </head>
      <body>
          <header>
              <h1>Clube de Investimento APPO</h1>
              <p>Portal Oficial de Cotações BODIVA, Contabilidade Visual e Filosofia de Investimento</p>
          </header>

          <div class="nav-tabs">
              <button class="tab-btn active" onclick="switchTab('educacao', this)">📚 Biblioteca & Princípios</button>
              <button class="tab-btn" onclick="switchTab('cotacoes', this)">📈 Cotações & Activos</button>
              <button class="tab-btn" onclick="switchTab('contabilidade', this)">💼 Contabilidade & Finanças (Gráficos)</button>
              <button class="tab-btn" onclick="switchTab('adesao', this)">📝 Adesão de Sócios</button>
              <button class="tab-btn" onclick="switchTab('sobre', this)">ℹ️ Sobre Nós & Estatutos</button>
              <button class="tab-btn admin-tab" onclick="switchTab('admin', this)">🔒 Painel do Administrador</button>
          </div>

          <div class="container">
              
              <!-- ABAS 1 -->
              <div id="tab-educacao" class="tab-content active">
                  <div class="card">
                      <h2>Princípios, Filosofia de Investimento e Artigos Educativos</h2>
                      <div id="artigosContainer"></div>
                  </div>
              </div>

              <!-- ABAS 2: COTAÇÕES COM CORES CONDICIONAIS -->
              <div id="tab-cotacoes" class="tab-content">
                  <div class="card">
                      <h2>Cotações e Activos BODIVA (Último Pregão)</h2>
                      <table id="assetsTable">
                          <tr><th>Título</th><th>Ticker</th><th>Cotação</th><th>Moeda</th><th>Últ. Cotação</th><th>Mercado</th><th>% Var.</th></tr>
                      </table>
                  </div>
              </div>

              <!-- ABAS 3 -->
              <div id="tab-contabilidade" class="tab-content">
                  <div class="card">
                      <h2>Estrutura Patrimonial e Financeira (Gráfico de Barras)</h2>
                      <div class="chart-container">
                          <canvas id="financialBarChart"></canvas>
                      </div>
                  </div>

                  <div class="card">
                      <h2>Evolução da Alocação de Ativos na Bolsa (Gráfico de Linhas)</h2>
                      <div class="chart-container">
                          <canvas id="assetLineChart"></canvas>
                      </div>
                  </div>

                  <div class="card">
                      <h2>Mapa de Créditos e Regularizações (Anonimizado para Sócios)</h2>
                      <table id="debtsTable">
                          <tr><th>Código do Devedor</th><th>Origem / Descrição</th><th>Montante</th><th>Moeda</th><th>Estado</th><th>Vencimento</th></tr>
                      </table>
                  </div>
              </div>

              <!-- ABAS 4 -->
              <div id="tab-adesao" class="tab-content">
                  <div class="card" style="border-top: 4px solid #10b981;">
                      <h2>Torne-se Membro do Clube de Investimento APPO</h2>
                      <div class="form-grid" style="background: #ffffff; border: none; padding: 0; margin-top: 20px;">
                          <input type="text" id="visitorName" placeholder="Seu Nome Completo">
                          <input type="text" id="visitorEmail" placeholder="Seu E-mail (ex: nome@email.com)">
                          <input type="text" id="visitorPhone" placeholder="Seu Telemóvel (ex: +244 923...)">
                          <select id="visitorType">
                              <option value="Membro Regular">Membro Regular</option>
                              <option value="Membro VIP">Membro VIP</option>
                              <option value="Investidor Institucional">Investidor Institucional</option>
                          </select>
                          <button class="btn-full btn-success" onclick="registerVisitor()">Submeter Pedido de Adesão</button>
                      </div>
                  </div>
              </div>

              <!-- ABAS 5 -->
              <div id="tab-sobre" class="tab-content">
                  <div class="card">
                      <h2>Sobre o Clube & Estatutos</h2>
                      <div id="infoContainer"></div>
                  </div>
              </div>

              <!-- ABAS 6 -->
              <div id="tab-admin" class="tab-content">
                  <div id="adminLoginScreen" class="login-box">
                      <h2>Área Restrita</h2>
                      <p style="font-size: 0.9em; color: #666;">Introduza a palavra-passe de Administrador para aceder.</p>
                      <input type="password" id="adminPasswordInput" placeholder="Palavra-passe de Admin" style="margin-bottom: 15px;">
                      <button style="width: 100%; background: #b91c1c;" onclick="verifyAdmin()">Entrar com Segurança</button>
                  </div>

                  <div id="adminDashboard" style="display: none;">
                      <div class="card" style="border-top: 4px solid #b91c1c;">
                          <div style="display: flex; justify-content: space-between; align-items: center;">
                              <h2>Painel de Controlo Exclusivo do Presidente</h2>
                              <button class="btn-danger" onclick="logoutAdmin()">Terminar Sessão</button>
                          </div>
                      </div>

                      <div class="card">
                          <h2>📊 Balanço Patrimonial Previsional (Controlo Interno)</h2>
                          <table>
                              <tr><th>Activo (Aplicações)</th><th>Montante (Kz)</th><th>Passivo & Capital Próprio (Origens)</th><th>Montante (Kz)</th></tr>
                              <tr><td>Disponibilidades (Liquidez)</td><td>1.780.884,96</td><td>Capital Social Subscrito (Nominal)</td><td>10.000.000,00</td></tr>
                              <tr><td>Investimentos BODIVA (Executados)</td><td>1.866.677,47</td><td><i>(-) Capital por Realizar</i></td><td><i>-5.000.000,00</i></td></tr>
                              <tr><td>Ordens Vivas / Cativas</td><td>1.286.759,71</td><td><b>Capital Realizado Efetivo</b></td><td><b>5.000.000,00</b></td></tr>
                              <tr><td>Créditos a Receber (AFAN)</td><td>7.500.000,00</td><td>Resultados Acumulados / Reservas</td><td>1.434.322,14</td></tr>
                              <tr><td>Ativos Fixos Tangíveis</td><td>3.000.000,00</td><td>Passivo / Obrigações de Curto Prazo</td><td>0,00</td></tr>
                              <tr style="background: #f1f5f9; font-weight: bold;"><td>Total do Activo</td><td>15.434.322,14</td><td>Total do Passivo & Capital Próprio</td><td>15.434.322,14</td></tr>
                          </table>
                      </div>

                      <div class="card">
                          <h2>📈 Demonstração de Resultados Previsional (2026)</h2>
                          <table>
                              <tr><th>Rubrica Operacional / Financeira</th><th>Montante (Kz)</th></tr>
                              <tr><td>Proveitos de Dividendos e Mais-Valias Potenciais (Estimativa)</td><td>850.000,00</td></tr>
                              <tr><td>Custos Administrativos e Comissões de Corretagem BODIVA</td><td>-120.000,00</td></tr>
                              <tr style="background: #f1f5f9; font-weight: bold;"><td>Resultado Líquido Previsional do Exercício</td><td>730.000,00</td></tr>
                          </table>
                      </div>

                      <div class="card">
                          <h2>Controlo Confidencial de Devedores (Visível Apenas para o Admin)</h2>
                          <table id="adminDebtsTable">
                              <tr><th>Código</th><th>Nome Real / Entidade</th><th>Origem</th><th>Montante</th><th>Estado</th></tr>
                          </table>
                      </div>

                      <div class="card">
                          <h2>Diretório de Sócios e Pedidos Pendentes</h2>
                          <table id="usersTable">
                              <tr><th>Nome Completo</th><th>E-mail</th><th>Telemóvel</th><th>Categoria</th><th>Estado</th></tr>
                          </table>
                      </div>

                      <div class="card">
                          <h2>📂 CMS: Carregar Novo Artigo / Princípio via PDF</h2>
                          <div class="form-grid full">
                              <input type="text" id="pdfTitle" placeholder="Título do Artigo / Princípio">
                              <select id="pdfCategory">
                                  <option value="Institucional">Institucional</option>
                                  <option value="Educação">Educação</option>
                                  <option value="Análise de Mercado">Análise de Mercado</option>
                              </select>
                              <input type="text" id="pdfTags" placeholder="Tags (Ex: OPV, rateio)">
                              <input type="text" id="pdfFileName" placeholder="Nome do PDF (Ex: Relatorio.pdf)">
                              <textarea id="pdfContent" rows="5" placeholder="Conteúdo..."></textarea>
                              <button class="btn-success" onclick="uploadArticle()">Publicar Artigo</button>
                          </div>
                      </div>
                  </div>
              </div>

          </div>

          <script>
              let barChartInstance = null;
              let lineChartInstance = null;

              function switchTab(tabId, btn) {
                  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                  document.getElementById('tab-' + tabId).classList.add('active');
                  btn.classList.add('active');
              }

              function verifyAdmin() {
                  const pass = document.getElementById('adminPasswordInput').value.trim();
                  if(pass === 'Alexinha123+1ou2') {
                      document.getElementById('adminLoginScreen').style.display = 'none';
                      document.getElementById('adminDashboard').style.display = 'block';
                      sessionStorage.setItem('isAdmin', 'true');
                  } else {
                      alert('Palavra-passe incorreta!');
                  }
              }

              function logoutAdmin() {
                  sessionStorage.removeItem('isAdmin');
                  document.getElementById('adminLoginScreen').style.display = 'block';
                  document.getElementById('adminDashboard').style.display = 'none';
                  document.getElementById('adminPasswordInput').value = '';
              }

              if(sessionStorage.getItem('isAdmin') === 'true') {
                  document.getElementById('adminLoginScreen').style.display = 'none';
                  document.getElementById('adminDashboard').style.display = 'block';
              }

              function loadData() {
                  fetch('/api/data')
                      .then(res => res.json())
                      .then(data => {
                          const artContainer = document.getElementById('artigosContainer');
                          artContainer.innerHTML = '';
                          data.artigos.forEach(art => {
                              artContainer.innerHTML += \`
                                  <div class="article-card">
                                      <h3>\${art.titulo}</h3>
                                      <p>\${art.conteudo}</p>
                                      <div class="article-meta">
                                          <span><b>Categoria:</b> <span class="badge">\${art.categoria}</span></span>
                                          <span><b>Tags:</b> \${art.tags}</span>
                                          <span><b>Data:</b> \${art.data_publicacao}</span>
                                          <span><b>Origem:</b> <code>\${art.ficheiro_pdf_original}</code></span>
                                      </div>
                                  </div>
                              \`;
                          });

                          const aTable = document.getElementById('assetsTable');
                          aTable.innerHTML = '<tr><th>Título</th><th>Ticker</th><th>Cotação</th><th>Moeda</th><th>Últ. Cotação</th><th>Mercado</th><th>% Var.</th></tr>';
                          data.assets.forEach(a => {
                              // Determinar cor condicional com base no sinal da variação
                              let varClass = 'var-neutro';
                              if (a.variation.includes('+')) {
                                  varClass = 'var-pos';
                              } else if (a.variation.includes('-')) {
                                  varClass = 'var-neg';
                              }

                              aTable.innerHTML += '<tr><td><b>' + a.companyName + '</b></td><td><code>' + a.ticker + '</code></td><td>' + Number(a.currentPrice).toLocaleString() + '</td><td>' + a.currency + '</td><td>' + a.lastTrade + '</td><td><span class="badge">' + a.market + '</span></td><td class="' + varClass + '">' + a.variation + '</td></tr>';
                          });

                          renderCharts(data.financials);

                          const dTable = document.getElementById('debtsTable');
                          dTable.innerHTML = '<tr><th>Código do Devedor</th><th>Origem / Descrição</th><th>Montante</th><th>Moeda</th><th>Estado</th><th>Vencimento</th></tr>';
                          data.debts.forEach(d => {
                              dTable.innerHTML += '<tr><td><b><span class="badge-admin">' + d.debtorCode + '</span></b></td><td>' + d.origin + '</td><td>' + Number(d.amount).toLocaleString() + '</td><td>' + d.currency + '</td><td><span class="badge-pending">' + d.status + '</span></td><td>' + d.dueDate + '</td></tr>';
                          });

                          const adminDTable = document.getElementById('adminDebtsTable');
                          adminDTable.innerHTML = '<tr><th>Código</th><th>Nome Real / Entidade</th><th>Origem</th><th>Montante</th><th>Estado</th></tr>';
                          data.rawDebts.forEach(d => {
                              adminDTable.innerHTML += '<tr><td><b><span class="badge-admin">' + d.debtorCode + '</span></b></td><td><b>' + d.realName + '</b></td><td>' + d.origin + '</td><td>' + Number(d.amount).toLocaleString() + ' Kz</td><td><span class="badge-pending">' + d.status + '</span></td></tr>';
                          });

                          const uTable = document.getElementById('usersTable');
                          uTable.innerHTML = '<tr><th>Nome Completo</th><th>E-mail</th><th>Telemóvel</th><th>Categoria</th><th>Estado</th></tr>';
                          data.users.forEach(u => {
                              const badgeClass = u.status === 'Ativo' ? 'badge' : 'badge-pending';
                              uTable.innerHTML += '<tr><td>' + u.name + '</td><td>' + u.email + '</td><td>' + (u.phone || '-') + '</td><td>' + u.membershipType + '</td><td><span class="' + badgeClass + '">' + u.status + '</span></td></tr>';
                          });

                          const iContainer = document.getElementById('infoContainer');
                          iContainer.innerHTML = '';
                          data.info.forEach(i => {
                              iContainer.innerHTML += '<h3 style="color: #0a2540; margin-top: 20px;">' + i.title + '</h3><p>' + i.content + '</p>';
                          });
                      });
              }

              function renderCharts(financials) {
                  const labels = financials.map(f => f.category);
                  const dataValues = financials.map(f => f.amount);

                  if (barChartInstance) barChartInstance.destroy();
                  if (lineChartInstance) lineChartInstance.destroy();

                  const ctxBar = document.getElementById('financialBarChart').getContext('2d');
                  barChartInstance = new Chart(ctxBar, {
                      type: 'bar',
                      data: {
                          labels: labels,
                          datasets: [{
                              label: 'Montante em Kz',
                              data: dataValues,
                              backgroundColor: ['#0a2540', '#10b981', '#0066cc', '#f59e0b', '#8b5cf6', '#64748b'],
                              borderRadius: 6
                          }]
                      },
                      options: {
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: { legend: { display: false } },
                          scales: { y: { beginAtZero: true } }
                      }
                  });

                  const ctxLine = document.getElementById('assetLineChart').getContext('2d');
                  lineChartInstance = new Chart(ctxLine, {
                      type: 'line',
                      data: {
                          labels: labels,
                          datasets: [{
                              label: 'Tendência Patrimonial (Kz)',
                              data: dataValues,
                              borderColor: '#0066cc',
                              backgroundColor: 'rgba(0, 102, 204, 0.1)',
                              fill: true,
                              tension: 0.3,
                              pointRadius: 5,
                              pointBackgroundColor: '#0a2540'
                          }]
                      },
                      options: {
                          responsive: true,
                          maintainAspectRatio: false,
                          scales: { y: { beginAtZero: true } }
                      }
                  });
              }

              function uploadArticle() {
                  const titulo = document.getElementById('pdfTitle').value;
                  const categoria = document.getElementById('pdfCategory').value;
                  const tags = document.getElementById('pdfTags').value;
                  const conteudo = document.getElementById('pdfContent').value;
                  const ficheiro_pdf_original = document.getElementById('pdfFileName').value || 'Documento.pdf';

                  if(!titulo || !conteudo) { alert('Preencha os campos obrigatórios.'); return; }

                  fetch('/api/artigos/upload', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ titulo, categoria, tags, conteudo, ficheiro_pdf_original })
                  }).then(() => {
                      alert('Artigo publicado com sucesso!');
                      document.getElementById('pdfTitle').value = '';
                      document.getElementById('pdfContent').value = '';
                      loadData();
                  });
              }

              function registerVisitor() {
                  const name = document.getElementById('visitorName').value;
                  const email = document.getElementById('visitorEmail').value;
                  const phone = document.getElementById('visitorPhone').value;
                  const membershipType = document.getElementById('visitorType').value;

                  if(!name || !email || !phone) { alert('Preencha os campos obrigatórios.'); return; }

                  fetch('/api/join', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ name, email, phone, membershipType })
                  }).then(() => {
                      alert('Pedido de adesão submetido com sucesso!');
                      document.getElementById('visitorName').value = '';
                      document.getElementById('visitorEmail').value = '';
                      document.getElementById('visitorPhone').value = '';
                      loadData();
                  });
              }

              loadData();
          </script>
      </body>
      </html>`,
      { headers: { "Content-Type": "text/html; charset=utf-8" } }
    );
  },
});

console.log("Servidor a correr em http://localhost:3000");