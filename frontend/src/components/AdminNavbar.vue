<template>
  <nav class="admin-navbar">
    <div class="logo">
      🚗 Parking Pro <span class="tag">- Admin</span>
    </div>

    <div class="nav-buttons">
      <router-link
        v-for="(link, index) in navLinks"
        :key="index"
        :to="link.path"
        class="nav-link"
        active-class="active-link"
      >
        {{ link.label }}
      </router-link>
      <button @click="logout" class="btn logout">Logout</button>
    </div>
  </nav>
</template>

<script>
import { inject } from 'vue'

export default {
  name: 'AdminNavbar',
  setup() {
    const authState = inject('authState')

    const logout = () => {
      localStorage.removeItem('token')
      localStorage.setItem('isLoggedIn', 'false')
      authState.isLoggedIn = false
      window.location.href = '/login'
    }

    const navLinks = [
      { path: '/', label: 'Home' },
      { path: '/users', label: 'Users' },
      { path: '/search', label: 'Search' },
      { path: '/summary', label: 'Summary' }
    ]

    return { logout, navLinks }
  }
}
</script>

<style scoped>
.admin-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(10, 10, 10, 0.85);
  padding: 1rem 2rem;
  color: white;
  backdrop-filter: blur(12px);
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
  z-index: 1000;
  position: sticky;
  top: 0;
}

.logo {
  font-size: 1.8rem;
  font-weight: 700;
  color: #00cfff;
}

.logo .tag {
  font-size: 1.1rem;
  color: #ccc;
  font-weight: 400;
}

.nav-buttons {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  font-weight: 600;
  transition: 0.3s ease;
  position: relative;
}

.nav-link:hover {
  background: rgba(0, 217, 255, 0.15);
  color: #00e3ff;
  backdrop-filter: blur(6px);
  transform: translateY(-1px);
}

.active-link {
  background-color: rgba(0, 255, 255, 0.1);
  color: #00e3ff;
  box-shadow: 0 0 6px rgba(0, 255, 255, 0.2);
}

.logout {
  background: #ff3b3b;
  color: white;
  padding: 0.45rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout:hover {
  background-color: #ff5555;
  box-shadow: 0 0 10px rgba(255, 0, 0, 0.3);
  transform: scale(1.05);
}
</style>
