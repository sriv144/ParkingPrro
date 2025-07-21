<template>
  <div class="login-page" :style="{ backgroundImage: 'url(/img10.jpg)' }">
    <Navbar />

    <div class="form-card">
      <h2>Welcome Back</h2>
      <form @submit.prevent="onSubmit">
        <div class="form-group">
          <label><i class="fas fa-envelope"></i> Email Address*</label>
          <input type="email" v-model="form.email" required />
        </div>

        <div class="form-group">
          <label><i class="fas fa-lock"></i> Password*</label>
          <input type="password" v-model="form.password" required />
        </div>

        <div class="form-links">
          <router-link to="/forgot-password">Forgot Password?</router-link>
          <router-link to="/terms">Terms &amp; conditions</router-link>
        </div>


        <div v-if="error" class="form-error">{{ error }}</div>



        <button class="btn-submit" type="submit">Submit</button>
      </form>

      <p class="form-footer">
        Don’t have an account?
        <router-link to="/register">Join Now</router-link>
      </p>
    </div>
  </div>
</template>

<script>

import { ref, inject } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Navbar from './Navbar.vue';

import Navbar from './Navbar.vue'

export default {
  name: 'LoginPage',
  components: { Navbar },

  setup() {
    const router = useRouter();
    const authState = inject('authState');

    const form = ref({
      email: '',
      password: ''
    });

    const error = ref('');

    const onSubmit = async () => {
      try {
        const res = await axios.post('/api/auth/login', {
          email: form.value.email,
          password: form.value.password
        });

        localStorage.setItem('token', res.data.access_token);
        localStorage.setItem('isLoggedIn', 'true');
        authState.isLoggedIn = true;

        axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`;

        router.push('/admin');
      } catch (err) {
        error.value = err.response?.data?.msg || 'Invalid email or password.';
      }
    };

    return { form, error, onSubmit };
  }
};

  data() {
    return {
      form: {
        email: '',
        password: ''
      }
    }
  },
  methods: {
    onSubmit() {
      // TODO: do real login here, then...
      this.$router.push('/admin')
    }
  }
}

</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background-size: cover;
  background-position: center;
  display: flex;
  flex-direction: column;
}
.form-card {
  backdrop-filter: blur(12px);
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  margin: auto;
  color: #00d4ff;
  box-shadow: 0 8px 24px rgba(0,0,0,0.6);
}
.form-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #00d4ff;

}
.form-group {
  margin-bottom: 1.2rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 500;
}
.form-group input {
  width: 100%;
  padding: 0.7rem 1rem;
  border: none;
  border-radius: 6px;
  background: #fff;
  font-size: 1rem;
  color: #333;
}
.form-links {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}
.form-links a {
  color: #00d4ff;
  text-decoration: none;
  font-size: 0.9rem;
}
.form-links a:hover {
  text-decoration: underline;
}
.form-error {
  color: #ff6f6f;
  font-weight: bold;
  text-align: center;
  margin-bottom: 1rem;
}


.btn-submit {
  width: 100%;
  padding: 0.8rem;
  background: #00d4ff;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-submit:hover {
  background: #00b8e6;
}
.form-footer {
  text-align: center;
  margin-top: 1rem;
  color: #fff;
}
.form-footer a {
  color: #00d4ff;
  text-decoration: none;
  font-weight: 600;
}
.form-footer a:hover {
  text-decoration: underline;
}
</style>
