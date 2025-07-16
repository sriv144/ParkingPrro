<template>
  <div
    ref="card"
    class="frost-card"
    :class="[ visible ? 'enter' : 'before-enter', slideClass ]"
  >
    <slot/>
  </div>
</template>

<script>
export default {
  name: 'FrostCard',
  props: { slideFrom: { type: String, default: 'left' } },
  data() { return { visible: false } },
  computed: {
    slideClass() {
      return this.slideFrom === 'left'
        ? 'slide-from-left'
        : 'slide-from-right';
    }
  },
  mounted() {
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        this.visible = true;
        obs.disconnect();
      }
    }, { threshold: 0.2 });
    obs.observe(this.$refs.card);
  }
}
</script>

<style scoped>
.frost-card {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  max-width: 360px;
  padding: 2rem;
  color: #fff;
  backdrop-filter: blur(12px);
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 16px;
  opacity: 0;
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}
.before-enter.slide-from-left  { transform: translate(-80px, -50%); }
.before-enter.slide-from-right { transform: translate( 80px, -50%); }
.enter {
  opacity: 1 !important;
  transform: translate(0, -50%) !important;
}
</style>
