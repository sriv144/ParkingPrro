<template>
  <div>
    <slot /> <!-- Render children content (like pages) -->
  </div>
</template>

<style>
:root {
    --primary-accent: #58D5F7;
    --dark-gradient-start: #0c0c0c;
    --dark-gradient-end: #1a1a1a;
    --card-bg: rgba(30, 30, 30, 0.6);
    --light-text: #FFFFFF;
    --gray-text: #9CA3AF;
    --success: #10B981;
    --warning: #F59E0B;
    --error: #EF4444;
}

html, body, #app {
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  color: var(--light-text);
  background: linear-gradient(135deg, var(--dark-gradient-start) 0%, var(--dark-gradient-end) 100%);
  position: relative;
}
body::before, #app::before {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: radial-gradient(circle at top right, rgba(88, 213, 247, 0.1), transparent 60%);
  pointer-events: none;
  z-index: 0;
}
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}
/* Put your navbar and card base styles here if global (copy from base.html) */
</style>
