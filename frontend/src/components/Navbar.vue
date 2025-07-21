<template>
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
}
</script>

<style scoped>
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
}
</style>
