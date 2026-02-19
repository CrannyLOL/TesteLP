import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-analytics.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";

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

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const database = getDatabase(app);

export { database };
