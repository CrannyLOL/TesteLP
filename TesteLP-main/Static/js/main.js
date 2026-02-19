import { database } from './firebase.js';
import { ref, push, set } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";

let bloqueado = false;
const TEMPO_BLOQUEIO = 2000; // 2 segundos
const TEMPO_FEEDBACK = 4000; // 4 segundos para mostrar feedback

async function votar(grau) {
    // Impedir múltiplos cliques
    if (bloqueado) {
        showMensagem("Aguarde...", "carregando");
        return;
    }
    
    bloqueado = true;
    
    // Desabilitar todos os botões
    disableBotoes(true);
    
    // Mostrar mensagem de carregamento
    showMensagem("Enviando sua resposta...", "carregando");

    try {
        // Obter data e hora atuais
        const hoje = new Date();
        const data = hoje.toISOString().split('T')[0]; // YYYY-MM-DD
        const hora = hoje.toTimeString().split(' ')[0]; // HH:MM:SS
        
        // Dias da semana em português
        const diasSemana = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"];
        const diaSemana = diasSemana[hoje.getDay()];
        
        // Timestamp
        const timestamp = hoje.toISOString();
        
        // Dados do voto
        const voto = {
            grau: grau,
            data: data,
            dia_semana: diaSemana,
            hora: hora,
            criado_em: timestamp
        };
        
        // Salvar no Firebase
        const votosRef = ref(database, 'votos');
        const newVotoRef = push(votosRef);
        await set(newVotoRef, voto);
        
        showMensagem("✅ Voto registado com sucesso! Obrigado.", "sucesso");
    } catch (error) {
        console.error("Erro:", error);
        showMensagem("❌ Erro ao registar a resposta. Tente novamente.", "erro");
    }

    // Voltar a habilitar após o tempo de bloqueio
    setTimeout(() => {
        bloqueado = false;
        disableBotoes(false);
        showMensagem("", "vazio");
    }, TEMPO_BLOQUEIO);
}

// Tornar função global para onclick
window.votar = votar;

function showMensagem(texto, classe) {
    const msg = document.getElementById("mensagem");
    if (!msg) return;
    
    msg.innerText = texto;
    msg.className = "mensagem-feedback " + classe;
    msg.style.display = texto ? "flex" : "none";
}

function disableBotoes(disable) {
    const botoes = document.querySelectorAll(".btn-fullscreen");
    botoes.forEach(btn => {
        btn.disabled = disable;
        btn.style.opacity = disable ? "0.5" : "1";
        btn.style.cursor = disable ? "not-allowed" : "pointer";
    });
}

// Atualizar data e dia da semana ao carregar a página
document.addEventListener("DOMContentLoaded", function() {
    atualizarDataHora();
    
    // Atualizar a cada minuto
    setInterval(atualizarDataHora, 60000);
});

function atualizarDataHora() {
    const hoje = new Date();
    
    // Formatar data (DD/MM/YYYY)
    const dia = String(hoje.getDate()).padStart(2, '0');
    const mes = String(hoje.getMonth() + 1).padStart(2, '0');
    const ano = hoje.getFullYear();
    const dataFormatada = `${dia}/${mes}/${ano}`;
    
    // Obter dia da semana
    const diasSemana = [
        "Domingo", "Segunda", "Terça", "Quarta", 
        "Quinta", "Sexta", "Sábado"
    ];
    const diaAtual = diasSemana[hoje.getDay()];
    
    // Atualizar elementos
    const elemData = document.getElementById("data-atual");
    const elemDia = document.getElementById("dia-atual");
    
    if (elemData) elemData.innerText = dataFormatada;
    if (elemDia) elemDia.innerText = diaAtual;
}

// Tornar funções globais
window.votar = votar;
window.atualizarDataHora = atualizarDataHora;


