<template>
<<<<<<< HEAD
  <nav class="navbar">
    <div class="logo">Parking Pro</div>
    <div class="nav-buttons">
      <template v-if="authState.isLoggedIn">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/users" class="nav-link">Users</router-link>
        <router-link to="/search" class="nav-link">Search</router-link>
        <router-link to="/summary" class="nav-link">Summary</router-link>
        <button @click="logout" class="btn logout">Logout</button>
      </template>
      <template v-else>
        <router-link to="/login" class="btn login">Login</router-link>
      </template>
    </div>
  </nav>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'AppNavbar',
  setup() {
    const authState = inject('authState')

    const logout = () => {
      localStorage.removeItem('token')
      localStorage.setItem('isLoggedIn', 'false')
      authState.isLoggedIn = false
      window.location.href = '/login'
    }

    return {
      authState,
      logout
    }
  }
=======
  <div class="container">
    <nav class="navbar-frost">
      <router-link to="/" class="navbar-brand">ParkingPro</router-link>

      <ul class="nav-links">
        <li><a href="#why-us">Why Us</a></li>
        <li><a href="#about">About</a></li>
        <li><a href="#services">Services</a></li>
      </ul>

      <div class="nav-actions">
        <!-- both buttons now use the same primary styling -->
        <router-link to="/login"    class="btn-primary">Login</router-link>
        <router-link to="/register" class="btn-primary">Register</router-link>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'AppNavbar'
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
}
</script>

<style scoped>
<<<<<<< HEAD
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #0a0a0a;
  color: white;
  padding: 1rem 2rem;
}
.logo {
  font-size: 1.6rem;
  font-weight: bold;
  color: #00cfff;
}
.nav-buttons {
  display: flex;
  gap: 1rem;
}
.nav-link, .btn {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  font-weight: bold;
}
.login {
  background-color: orange;
  border-radius: 5px;
}
.logout {
  background-color: red;
  border-radius: 5px;
  border: none;
=======
.navbar-frost {
  position: fixed;
  top: 0; left: 0; right: 0;
  display: flex;
  justify-content: center;
  backdrop-filter: blur(10px);
  background: rgba(0, 0, 20, 0.75);
  padding: 0.5rem 0;
  z-index: 1000;
}
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.navbar-brand {
  font-weight: bold;
  color: #fff;
  text-decoration: none;
  font-size: 1.2rem;
}
.nav-links {
  list-style: none;
  display: flex;
  gap: 1.5rem;
  margin-left: auto;
}
.nav-links a {
  color: #eee;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}
.nav-links a:hover {
  color: #00d4ff;
}

.nav-actions {
  margin-left: 2rem;
  display: flex;
  gap: 0.75rem;
}

/* unified primary button for Login & Register */
.btn-primary {
  padding: 0.6rem 1.2rem;
  background: #00d4ff;
  border: none;
  border-radius: 6px;
  color: #001f3f;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s;
}
.btn-primary:hover {
  background: #00b8e6;
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
}
</style>
