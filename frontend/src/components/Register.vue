<template>
  <div class="register-page" :style="{ backgroundImage: 'url(/img10.jpg)' }">
    <Navbar />

    <div class="form-card">
      <h2>Create Account</h2>
      <form @submit.prevent="onSubmit">
        <div class="form-grid">
          <!-- Column 1 -->
          <div class="form-group">
            <label><i class="fas fa-user"></i> Username*</label>
            <input type="text" v-model="form.username" required />
          </div>

          <div class="form-group">
            <label><i class="fas fa-envelope"></i> Email Address*</label>
            <input type="email" v-model="form.email" required />
          </div>

          <div class="form-group">
            <label><i class="fas fa-lock"></i> Password*</label>
            <input type="password" v-model="form.password" required />
          </div>

          <div class="form-group">
            <label><i class="fas fa-phone"></i> Phone Number*</label>
            <input type="text" v-model="form.phone_number" required />
          </div>

          <!-- Column 2 -->
          <div class="form-group">
            <label><i class="fas fa-car"></i> Vehicle Number*</label>
            <input type="text" v-model="form.vehicle_number" required />
          </div>

          <div class="form-group">
            <label><i class="fas fa-motorcycle"></i> Vehicle Type*</label>
            <select v-model="form.vehicle_type" required>
              <option disabled value="">Select</option>
              <option>2-wheeler</option>
              <option>4-wheeler</option>
            </select>
          </div>

          <div class="form-group">
            <label><i class="fas fa-venus-mars"></i> Gender*</label>
            <select v-model="form.gender" required>
              <option disabled value="">Select</option>
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
          </div>

          <div class="form-group">
            <label><i class="fas fa-home"></i> Address*</label>
            <textarea v-model="form.address" required></textarea>
          </div>
        </div>

        <!-- Admin checkbox -->
        <div class="form-bottom-row">
          <div class="checkbox-group">
            <input type="checkbox" v-model="form.is_admin" id="adminCheck" />
            <label for="adminCheck">Register as Admin</label>
          </div>
        </div>

        <div v-if="error" class="form-error">{{ error }}</div>

        <button class="btn-submit" type="submit">Register</button>

        <p class="form-footer">
          Already have an account?
          <router-link to="/login">Login Here</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Navbar from './Navbar.vue';

export default {
  name: 'UserRegister',
  components: { Navbar },
  setup() {
    const router = useRouter();
    const error = ref('');

    const form = ref({
      username: '',
      email: '',
      password: '',
      phone_number: '',
      vehicle_number: '',
      vehicle_type: '',
      gender: '',
      address: '',
      is_admin: false
    });

    const onSubmit = async () => {
      try {
        await axios.post('/api/auth/register', form.value);
        router.push('/login');
      } catch (err) {
        error.value = err.response?.data?.msg || 'Registration failed.';
      }
    };

    return { form, error, onSubmit };
  }
};
</script>

<style scoped>
.register-page {
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
  max-width: 900px;
  margin: auto;
  color: #00d4ff;
  box-shadow: 0 8px 24px rgba(0,0,0,0.6);
}
.form-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #00d4ff;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;
  margin-bottom: 1rem;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 500;
}
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.7rem 1rem;
  border: none;
  border-radius: 6px;
  background: #fff;
  font-size: 1rem;
  color: #333;
}
textarea {
  resize: vertical;
}
.form-bottom-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}
.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: white;
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
