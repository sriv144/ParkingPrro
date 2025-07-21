<template>
<<<<<<< HEAD
  <div class="edit-container">
    <h1>Edit Parking Lot</h1>
    <p>Update parking lot information</p>
    <div class="form">
      <label>Prime Location Name</label>
      <input type="text" />

      <label>Address</label>
      <textarea></textarea>

      <label>Landmark</label>
      <textarea></textarea>

      <div class="actions">
        <button class="save">Save Changes</button>
        <button class="delete">Delete</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "EditParkingLot",
};
</script>

<style scoped>
.edit-container {
  padding: 2rem;
  background-color: #111;
  color: #fff;
  min-height: 100vh;
}

.edit-container h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.edit-container p {
  margin-bottom: 2rem;
  color: #ccc;
}

.form {
  background-color: #1a1a1a;
  padding: 2rem;
  border-radius: 10px;
}

label {
  display: block;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

input,
textarea {
  width: 100%;
  background-color: #2c2c2c;
  border: none;
  padding: 10px;
  color: #fff;
  border-radius: 5px;
  margin-bottom: 1rem;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

.save {
  background-color: #00bfff;
  border: none;
  padding: 10px 20px;
  color: white;
  border-radius: 5px;
}

.delete {
  background-color: #e74c3c;
  border: none;
  padding: 10px 20px;
  color: white;
  border-radius: 5px;
=======
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
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
}
</style>
