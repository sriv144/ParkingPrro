<template>
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
}
</script>

<style scoped>
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
}
</style>
