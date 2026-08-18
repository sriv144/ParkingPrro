import { createApp, reactive } from 'vue';
import App from './App.vue';
import router from './router/index.js';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';
import '@fortawesome/fontawesome-free/css/all.min.css';

// ✅ Global reactive auth state
const authState = reactive({
  isLoggedIn: localStorage.getItem('isLoggedIn') === 'true',
  token: localStorage.getItem('token') || null
});

// Optionally set Axios default header for authenticated requests
import axios from 'axios';
if (authState.token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${authState.token}`;
}

const app = createApp(App);

// ✅ Make authState available across all components
app.provide('authState', authState);

app.use(router).mount('#app');
