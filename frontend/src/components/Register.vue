<template>
<<<<<<< HEAD
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
=======
  <div class="register-page" :style="{ backgroundImage: 'url(/img9.jpg)' }">
    <Navbar />

    <div class="form-card">
      <h2>Create your ParkingPro Account</h2>
      <form @submit.prevent="onSubmit">
        <div class="row">
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-user"></i> First Name*</label>
              <input type="text" v-model="form.firstName" required />
            </div>
          </div>
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-user"></i> Last Name*</label>
              <input type="text" v-model="form.lastName" required />
            </div>
          </div>
        </div>

        <!-- email row -->
        <div class="row">
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-envelope"></i> Email Address*</label>
              <input type="email" v-model="form.email" required />
            </div>
          </div>
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-envelope"></i> Confirm Email*</label>
              <input type="email" v-model="form.emailConfirm" required />
            </div>
          </div>
        </div>

        <!-- vehicle/postcode -->
        <div class="row">
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-car"></i> Vehicle Reg. Number*</label>
              <input type="text" v-model="form.vehicleReg" required />
            </div>
          </div>
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-map-marker-alt"></i> Postcode*</label>
              <input type="text" v-model="form.postcode" required />
            </div>
          </div>
        </div>

        <!-- phone/age -->
        <div class="row">
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-phone"></i> Phone Number*</label>
              <input type="tel" v-model="form.phone" required />
            </div>
          </div>
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-user-lock"></i> Age</label>
              <input type="number" v-model="form.age" />
            </div>
          </div>
        </div>

        <!-- password row -->
        <div class="row">
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-lock"></i> Password*</label>
              <input type="password" v-model="form.password" required />
            </div>
          </div>
          <div class="col">
            <div class="form-group">
              <label><i class="fas fa-lock"></i> Confirm Password*</label>
              <input type="password" v-model="form.passwordConfirm" required />
            </div>
          </div>
        </div>

        <div class="form-group checkbox">
          <input type="checkbox" id="terms" v-model="form.agree" />
          <label for="terms">
            I accept the
            <router-link to="/terms">terms &amp; conditions</router-link>
          </label>
        </div>

        <button class="btn-submit" type="submit">Create Account</button>
      </form>

      <p class="form-footer">
        Already have an account?
        <router-link to="/login">Login</router-link>
      </p>
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
    </div>
  </div>
</template>

<script>
<<<<<<< HEAD
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
=======
import Navbar from './Navbar.vue'

export default {
  name: 'RegisterPage',
  components: { Navbar },
  data() {
    return {
      form: {
        firstName: '',
        lastName: '',
        email: '',
        emailConfirm: '',
        vehicleReg: '',
        postcode: '',
        phone: '',
        age: '',
        password: '',
        passwordConfirm: '',
        agree: false
      }
    }
  },
  methods: {
    onSubmit() {
      if (!this.form.agree) {
        alert('You must accept the terms.')
        return
      }
      // TODO: submit registration
      this.$router.push('/login')
    }
  }
}
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background-size: cover;
  background-position: center;
  display: flex;
<<<<<<< HEAD
  flex-direction: column;
}
=======
  align-items: center;       /* vertical center */
  justify-content: center;   /* horizontal center */
}

/* Frost-card container */
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
.form-card {
  backdrop-filter: blur(12px);
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  padding: 2rem;
<<<<<<< HEAD
  max-width: 900px;
  margin: auto;
  color: #00d4ff;
  box-shadow: 0 8px 24px rgba(0,0,0,0.6);
}
=======
  width: 100%;
  max-width: 900px;
  min-height: 700px;         /* ensure consistent height */
  display: flex;
  flex-direction: column;
  justify-content: center;   /* center content vertically */
  color: #00d4ff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
}

>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
.form-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #00d4ff;
}
<<<<<<< HEAD
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;
  margin-bottom: 1rem;
}
.form-group {
  margin-bottom: 1rem;
}
=======

.row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.col {
  flex: 1;
}

.form-group {
  margin-bottom: 0.8rem;
}

>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
.form-group label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 500;
}
<<<<<<< HEAD
.form-group input,
.form-group select,
.form-group textarea {
=======

.form-group input {
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
  width: 100%;
  padding: 0.7rem 1rem;
  border: none;
  border-radius: 6px;
  background: #fff;
  font-size: 1rem;
  color: #333;
}
<<<<<<< HEAD
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
=======

.checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.checkbox input {
  margin-right: 0.5rem;
}

.checkbox label a {
  color: #00d4ff;
  text-decoration: none;
}
.checkbox label a:hover {
  text-decoration: underline;
}

>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
.btn-submit {
  width: 100%;
  padding: 0.8rem;
  background: #00d4ff;
<<<<<<< HEAD
  color: #ffffff;
=======
  color: #001f3f;
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
  border: none;
  border-radius: 6px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
<<<<<<< HEAD
}
.btn-submit:hover {
  background: #00b8e6;
}
=======
  margin-top: 1rem;
}

.btn-submit:hover {
  background: #00b8e6;
}

>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
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
