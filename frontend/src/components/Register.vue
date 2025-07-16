<template>
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
    </div>
  </div>
</template>

<script>
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
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;       /* vertical center */
  justify-content: center;   /* horizontal center */
}

/* Frost-card container */
.form-card {
  backdrop-filter: blur(12px);
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 900px;
  min-height: 700px;         /* ensure consistent height */
  display: flex;
  flex-direction: column;
  justify-content: center;   /* center content vertically */
  color: #00d4ff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
}

.form-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #00d4ff;
}

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

.btn-submit {
  width: 100%;
  padding: 0.8rem;
  background: #00d4ff;
  color: #001f3f;
  border: none;
  border-radius: 6px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 1rem;
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
