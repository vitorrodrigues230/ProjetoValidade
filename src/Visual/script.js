// --- FUNÇÕES DE NAVEGAÇÃO E INTERFACE ---

  function switchTab(tabId, title) {
    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
      const dot = item.querySelector('.dot');
      if(dot) { dot.classList.remove('dot-blue'); dot.classList.add('dot-gray'); }
    });
    
    const activeNav = document.querySelector(`.nav-item[data-target="${tabId}"]`);
    if(activeNav) {
      activeNav.classList.add('active');
      const dot = activeNav.querySelector('.dot');
      if(dot) { dot.classList.remove('dot-gray'); dot.classList.add('dot-blue'); }
    }
    
    if(title) {
      document.getElementById('page-title-display').innerText = title;
    }
    
    closeMobileMenu();
  }

  function toggleMobileMenu() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebar-overlay').classList.toggle('open');
  }

  function closeMobileMenu() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('open');
  }

  function toggleTheme() {
    document.body.classList.toggle('light-mode');
    const isLight = document.body.classList.contains('light-mode');
    localStorage.setItem('valida_theme', isLight ? 'light' : 'dark');
    updateThemeIcon();
  }

  function updateThemeIcon() {
    const btn = document.getElementById('theme-toggle');
    if(btn) {
      btn.innerText = document.body.classList.contains('light-mode') ? '☾' : '☀';
    }
  }

  // --- INTEGRAÇÃO REAL COM O BACKEND (POSTGRESQL) ---

  async function carregarInventario() {
    try {
      // Faz a chamada para o seu servidor FastAPI
      const response = await fetch('http://127.0.0.1:8000/api/inventario');
      
      if (!response.ok) throw new Error('Servidor offline ou erro na rota');

      const dados = await response.json();
      const tabelaCorpo = document.querySelector('tbody');
      
      // Limpa as linhas aleatórias/estáticas antes de preencher
      tabelaCorpo.innerHTML = ''; 

      dados.forEach(item => {
        const tr = document.createElement('tr');
        
        // Lógica de Estilo Premium (Cores de Fundo e Tags)
        let rowClass = ''; 
        let tagClass = ''; 
        
        // Normaliza o status para evitar erros de acentuação/maíusculas
        const status = item.status.toLowerCase();

        if (status === 'crítico' || status === 'critico') {
          rowClass = 'row-crit'; // Dá o fundo avermelhado na linha toda
          tagClass = 'tag-crit'; // Cor do texto/tag
        } else if (status === 'atenção' || status === 'atencao') {
          rowClass = 'row-warn'; // Dá o fundo amarelado na linha toda
          tagClass = 'tag-warn';
        } else {
          tagClass = 'tag-safe'; // Verde para Seguro
        }

        // Aplica a classe de fundo na linha <tr>
        if (rowClass) tr.classList.add(rowClass);

        // Monta o HTML da linha exatamente como no seu design
        tr.innerHTML = `
          <td>${item.produto}</td>
          <td>${item.categoria}</td>
          <td>${item.validade}</td>
          <td>${item.qtd} un</td>
          <td><span class="status-tag ${tagClass}">${item.status}</span></td>
          <td><i class="fas fa-ellipsis-v icon-menu"></i></td>
        `;
        
        tabelaCorpo.appendChild(tr);
      });

      console.log("Inventário carregado com sucesso do PostgreSQL!");
    } catch (error) {
      console.error("Erro ao conectar com o backend:", error);
    }
  }

  // --- INICIALIZAÇÃO ---

  window.addEventListener('DOMContentLoaded', () => {
    // Aplica o tema salvo
    if(localStorage.getItem('valida_theme') === 'light') {
      document.body.classList.add('light-mode');
    }
    updateThemeIcon();

    // Dispara a busca de dados reais
    carregarInventario();
  });