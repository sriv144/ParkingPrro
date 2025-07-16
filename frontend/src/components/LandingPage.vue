<template>
  <div class="landing-page">
    <AppNavbar />

    <!-- HERO SLIDER -->
    <section class="hero">
      <transition-group name="hero-fade" tag="div" class="slides">
        <div
          v-for="(slide,i) in slides"
          :key="i"
          v-show="i === current"
          class="slide"
          :style="{ backgroundImage: `url(${slide.img})` }"
        >
          <div class="hero-content">
            <h1>{{ slide.title }}</h1>
            <p>{{ slide.text }}</p>
            <router-link to="/register" class="btn-primary">Get Started</router-link>
          </div>
        </div>
      </transition-group>
    </section>

    <!-- WHY US -->
    <section id="why-us" class="section full-bg" :style="{ backgroundImage: `url(${bgWhyUs})` }">
      <div class="overlay" />
      <div class="section-inner">
        <h2>Why Choose ParkingPro?</h2>
        <div class="cards">
          <div class="frost-card" v-for="(item,i) in whyUs" :key="i">
            <h3>{{ item.title }}</h3>
            <p>{{ item.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ABOUT US -->
    <section id="about" class="section full-bg" :style="{ backgroundImage: `url(${bgAbout})` }">
      <div class="overlay" />
      <div class="section-inner about">
        <div class="frost-card about-text">
          <h2>About Us</h2>
          <p>
            Since 2020, ParkingPro has transformed parking with real-time availability,
            cashless payments, and 24/7 support. Trusted by thousands to make every
            parking experience effortless.
          </p>
        </div>
      </div>
    </section>

    <!-- OUR SERVICES -->
    <section id="services" class="section full-bg" :style="{ backgroundImage: `url(${bgServices})` }">
      <div class="overlay" />
      <div class="section-inner">
        <h2>Our Services</h2>
        <div class="cards">
          <div class="frost-card" v-for="(svc,i) in services" :key="i">
            <h3>{{ svc.title }}</h3>
            <p>{{ svc.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="site-footer">
      <div class="container">
        <p>© {{ new Date().getFullYear() }} ParkingPro. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script>
import AppNavbar from './Navbar.vue'

export default {
  name: 'LandingPage',
  components: { AppNavbar },
  data() {
    return {
      slides: [
        { img: '/img1.jpg', title: 'Effortless Parking',     text: 'Find, reserve & park in seconds.' },
        { img: '/img2.jpg', title: 'Real-Time Availability', text: 'Live spot status at your fingertips.' },
        { img: '/img3.jpg', title: 'Cashless & Secure',      text: 'Pay via app with bank-grade security.' },
        { img: '/img4.jpg', title: 'On-the-Go Booking',      text: 'Manage your reservations anywhere.' },
      ],
      current: 0,
      whyUs: [
        { title: 'Superior Service',      text: 'Decades of experience delivering top-notch parking management.' },
        { title: 'Innovative Technology', text: 'Cloud-native platform built for scale and reliability.' },
        { title: 'End-to-End Solution',   text: 'From strategy to daily ops, we handle it all.' },
      ],
      services: [
        { title: 'Consultancy Services',  text: 'Tailored advice to maximize your parking ROI.' },
        { title: 'Tech Platforms',        text: 'Scalable booking & payment systems.' },
        { title: 'Operations Management', text: '24/7 on-site support and monitoring.' },
      ],
      bgWhyUs: '/img8.jpg',
      bgAbout: '/img9.jpg',
      bgServices: '/img7.jpg'
    }
  },
  mounted() {
    this.interval = setInterval(() => {
      this.current = (this.current + 1) % this.slides.length
    }, 5000)
  },
  beforeUnmount() {
    clearInterval(this.interval)
  }
}
</script>

<style scoped>
.landing-page { font-family: 'Segoe UI', sans-serif; }

/* HERO */
.hero {
  position: relative;
  height: 100vh;
  overflow: hidden;
}
.slides, .slide {
  position: absolute; top: 0; left: 0;
  width: 100%; height: 100%;
}
.slide {
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hero-fade-enter-active, .hero-fade-leave-active {
  transition: opacity 1.2s ease-in-out;
}
.hero-fade-enter-from, .hero-fade-leave-to {
  opacity: 0;
}
.hero-content {
  text-align: center; color: #fff;
}
.hero-content h1 {
  font-size: 3.5rem; margin-bottom: 1rem;
}
.hero-content p {
  font-size: 1.5rem; margin-bottom: 2rem;
}
.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #00d4ff;
  color: #001f3f;
  border: none;
  border-radius: 6px;
  font-size: 1.1rem;
  text-decoration: none;
}

/* SECTION WRAPPER */
.section {
  position: relative;
  height: 80vh;
  display: flex;
  align-items: center;
}
.full-bg {
  background-size: cover;
  background-position: center;
  color: #fff;
}
.overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.5);
}
.section-inner {
  position: relative;
  z-index: 1;
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}
.section-inner h2 {
  font-size: 2.8rem;
  margin-bottom: 1rem;
}
.cards {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
}
.frost-card {
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(8px);
  padding: 2rem;
  border-radius: 8px;
  flex: 1 1 280px;
  text-align: left;
}
.frost-card h3 {
  font-size: 1.6rem;
  margin-bottom: 0.8rem;
}
.frost-card p {
  font-size: 1.2rem;
  line-height: 1.6;
}

/* ABOUT */
.about .about-text {
  max-width: 600px;
  margin: 0 auto;
  text-align: left;
}

/* FOOTER */
.site-footer {
  background: #001f3f;
  color: #ccc;
  padding: 1rem 0;
  text-align: center;
}
.container {
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
