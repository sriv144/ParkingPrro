<template>
  <div class="modal-overlay">
    <div class="modal-card">
      <div class="modal-header">
        <span class="modal-title">Edit Parking Lot</span>
      </div>
      <form @submit.prevent="submit">
        <div class="modal-body">
          <label>
            <span>Prime Location Name:</span>
            <input v-model="lot.name" type="text" required />
          </label>
          <label>
            <span>Address:</span>
            <textarea v-model="lot.address" rows="3" required />
          </label>
          <label>
            <span>Pin code:</span>
            <input v-model="lot.pin" type="text" required />
          </label>
          <label>
            <span>Price (per hour):</span>
            <input v-model="lot.price" type="number" required min="0" />
          </label>
          <label>
            <span>Maximum spots:</span>
            <input v-model="lot.maxSpots" type="number" required min="1" />
          </label>
        </div>
        <div class="modal-actions">
          <button type="submit" class="action-btn action-btn-update">Update</button>
          <button type="button" class="action-btn action-btn-cancel" @click="$emit('close')">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>
<script setup>
// eslint-disable-next-line no-undef
const props = defineProps({ lotData: Object })
// eslint-disable-next-line no-undef
const emit = defineEmits(['update', 'close'])
import { reactive } from "vue";
const lot = reactive({ ...props.lotData });
function submit() { emit("update", { ...lot }); }
</script>
<style scoped>
@import './modal-card.css';
.action-btn-update {
  background: linear-gradient(95deg, #58d5f7, #18f0c8 99%);
  color: #003447;
}
.action-btn-update:hover {
  background: #6edfff;
  color: #051721;
}
</style>
