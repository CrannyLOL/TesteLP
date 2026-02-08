// Importar Firebase via CDN
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-analytics.js";

// Configuração Firebase (a tua)
const firebaseConfig = {
  apiKey: "AIzaSyA07oabCA700zhnZAT2B6xUom4MubdeIqg",
  authDomain: "testelp-8517f.firebaseapp.com",
  databaseURL: "https://testelp-8517f-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "testelp-8517f",
  storageBucket: "testelp-8517f.firebasestorage.app",
  messagingSenderId: "795381651780",
  appId: "1:795381651780:web:d7584145a4bc33cbb59f11",
  measurementId: "G-56VK661XMB"
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Teste (opcional)
console.log("🔥 Firebase ligado com sucesso!");
import { getDatabase, ref, set } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js";

const db = getDatabase(app);

// Exemplo: guardar satisfação
function guardarSatisfacao(nome, avaliacao, comentario) {
  set(ref(db, 'satisfacoes/' + Date.now()), {
    nome: nome,
    avaliacao: avaliacao,
    comentario: comentario
  });
}
