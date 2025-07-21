<template>
  <div class="modal-overlay">
    <div class="modal-card">
      <div class="modal-header">
        <span class="modal-title">Occupied Parking Spot Details</span>
      </div>
      <div class="modal-body">
        <label>
          <span>ID:</span>
          <input :value="props.details.id" readonly />
        </label>
        <label>
          <span>Customer ID:</span>
          <input :value="props.details.customerId" readonly />
        </label>
        <label>
          <span>Vehicle number:</span>
          <input :value="props.details.vehicleNumber" readonly />
        </label>
        <label>
          <span>Date/time of parking:</span>
          <input :value="props.details.parkingTime" readonly />
        </label>
        <label>
          <span>Est. parking cost:</span>
          <input :value="props.details.estimatedCost" readonly />
        </label>
      </div>
      <div class="modal-actions">
        <button class="action-btn action-btn-cancel" @click="$emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
<script setup>
// eslint-disable-next-line no-undef
const props = defineProps(['details']);
</script>
<style scoped>
@import './modal-card.css';
</style>
