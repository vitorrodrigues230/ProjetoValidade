

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
        console.log("Dados do item vindo do banco:", item);
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
        const idParaUso = item.id_externo;

        // Dentro do seu dados.forEach no carregarInventario:
        // Dentro do seu dados.forEach no carregarInventario:
tr.innerHTML = `
    <td class="col-produto" style="cursor:pointer; font-weight:bold;" onclick="vincularData(${idParaUso}, '${item.produto}')">
        ${item.produto}
    </td>
    <td class="col-categoria">${item.categoria}</td>
    <td>${item.validade || '---'}</td>
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

  async function vincularData(idExterno, nomeProduto) {
    if (!idExterno) {
        alert("Erro: ID do produto não encontrado.");
        return;
    }
    const dataInput = prompt(`Digite a data para ${nomeProduto} (AAAA-MM-DD):`);
    
    if (dataInput) {
        const payload = {
            id_externo: parseInt(idExterno),
            data_validade: dataInput.trim()
        };
        
        console.log("Enviando para o servidor:", payload); // Isso ajuda a debugar!

        try {
            const response = await fetch('http://127.0.0.1:8000/api/vincular-validade', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert('Sucesso! Validade registrada.');
                location.reload();
            } else {
                const erroDetalhado = await response.json();
                console.error("Erro detalhado do FastAPI:", erroDetalhado);
                alert("Erro de formato. Verifique o console (F12) para detalhes.");
            }
        } catch (error) {
            console.error("Erro na comunicação:", error);
        }
    }
}
async function carregarVencimentosProximos() {
    const response = await fetch('http://127.0.0.1:8000/api/vencimentos_proximos');
    const dados = await response.json();
    
    const container = document.getElementById('lista-vencimentos'); // Verifique esse ID no seu HTML
    container.innerHTML = ''; // Limpa a lista antiga

    dados.forEach((item, index) => {
        const itemHtml = `
            <div class="vencimento-item">
                <span class="numero">${(index + 1).toString().padStart(2, '0')}</span>
                <span class="nome-produto">${item.produto}</span>
                <span class="badge ${item.classe_cor}">${item.dias_texto}</span>
            </div>
        `;
        container.innerHTML += itemHtml;
    });
}


// Chame a função quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    carregarInventario();
    carregarVencimentosProximos();
});
async function carregarVencimentosLaterais() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/vencimentos_proximos');
        const dados = await response.json();
        
        const container = document.getElementById('lista-vencimentos-lateral');
        if (!container) return;
        container.innerHTML = ''; // Limpa os dados estáticos

        dados.forEach((item, index) => {
            // Monta o HTML seguindo exatamente o design do seu print
            const itemHtml = `
                <div class="vencimento-row">
                    <div class="vencimento-info" style="display: flex; align-items: center; gap: 10px;">
                        <span class="vencimento-pos">${(index + 1).toString().padStart(2, '0')}</span>
                        <span class="vencimento-nome">${item.produto}</span>
                    </div>
                    <div class="vencimento-status">
                        <span class="badge-vencimento ${item.classe_cor}">${item.dias_texto}</span>
                    </div>
                </div>
            `;
            container.innerHTML += itemHtml;
        });
    } catch (erro) {
        console.error("Erro ao carregar lista lateral:", erro);
    }
}
document.addEventListener('DOMContentLoaded', () => {
    // Chama as duas funções para popular o dashboard
    carregarInventario(); 
    carregarVencimentosLaterais();
});

// Chame ela no final do arquivo ou dentro do DOMContentLoaded
carregarVencimentosLaterais();
function configurarBusca() {
    const inputBusca = document.getElementById('input-busca');
    // Usamos um seletor mais genérico caso o ID mude
    const tabelaCorpo = document.querySelector('tbody'); 

    if (!inputBusca || !tabelaCorpo) return;

    inputBusca.addEventListener('keyup', () => {
        const termo = inputBusca.value.toLowerCase().trim();
        const linhas = tabelaCorpo.querySelectorAll('tr');

        let linhasEncontradas = 0;

linhas.forEach(linha => {
    const nome = linha.querySelector('.col-produto')?.textContent.toLowerCase() || "";
    const categoria = linha.querySelector('.col-categoria')?.textContent.toLowerCase() || "";

    if (nome.includes(termo) || categoria.includes(termo)) {
        linha.style.display = ""; 
        linhasEncontradas++; // Se encontrou, aumenta o contador
    } else {
        linha.style.display = "none"; 
    }
});
// Fora do loop, você verifica se o contador é zero
const msgVazia = document.getElementById('mensagem-vazia');
if (msgVazia) {
    msgVazia.style.display = (linhasEncontradas === 0 && termo !== "") ? "block" : "none";
}
    });
}


// Lembre-se de chamar a função quando o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    carregarInventario();
    carregarVencimentosLaterais();
    configurarBusca(); // Ativa a busca
});
