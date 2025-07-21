<template>
  <div class="edit-container">
    <div class="edit-header">
      <h1>Edit Parking Lot</h1>
      <p class="subtitle">Update parking lot information</p>
    </div>

    <div class="edit-card">
      <form @submit.prevent="updateLot">
        <label>
          Prime Location Name
          <input v-model="lot.name" type="text" required />
        </label>

        <label>
          Address
          <textarea v-model="lot.address" required></textarea>
        </label>

        <label>
          Landmark
          <input v-model="lot.landmark" type="text" />
        </label>

        <label>
          Pin Code
          <input v-model="lot.pincode" type="text" />
        </label>

        <label>
          Price (per hour)
          <input v-model.number="lot.price" type="number" min="0" />
        </label>

        <label>
          Maximum Spots
          <input v-model.number="lot.maxSpots" type="number" min="0" />
        </label>

        <label>
          Contact Number
          <input v-model="lot.contact" type="text" />
        </label>

        <div class="checkbox-row">
          <input v-model="lot.covered" type="checkbox" id="covered" />
          <label for="covered" class="inline-label">Covered Parking?</label>
        </div>

        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="cancelEdit">Cancel</button>
          <button type="submit" class="save-btn">Save Changes</button>
          <button type="button" class="delete-btn">Delete</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "EditParkingLot",
  data() {
    return {
      lot: {
        name: "",
        address: "",
        landmark: "",
        pincode: "",
        price: null,
        maxSpots: null,
        contact: "",
        covered: false,
      },
    };
  },
  methods: {
    updateLot() {
      // Add backend call logic here
    },
    cancelEdit() {
      this.$router.back();
    },
  },
};
</script>

<style scoped>
.edit-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #0e0e0e;
  color: #ffffff;
  min-height: calc(100vh - 72px);
  padding: 30px 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.edit-header {
  width: 100%;
  max-width: 900px;
  margin-bottom: 30px;
}

.edit-header h1 {
  font-size: 2.4rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.subtitle {
  font-size: 1rem;
  color: #94a3b8;
}

.edit-card {
  background-color: #1a1a1a;
  width: 100%;
  max-width: 900px;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #2c2c2c;
}

form label {
  display: block;
  color: #cbd5e1;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1.2rem;
}

form input,
form textarea {
  margin-top: 0.4rem;
  width: 100%;
  padding: 12px;
  background-color: #2a2a2a;
  border: none;
  border-radius: 8px;
  color: #f8fafc;
  font-size: 1rem;
}

form input:focus,
form textarea:focus {
  outline: none;
  border: 1px solid #3b82f6;
}

textarea {
  resize: vertical;
  min-height: 90px;
}

.checkbox-row {
  display: flex;
  align-items: center;
  margin-top: 20px;
  margin-bottom: 25px;
}

.checkbox-row input[type="checkbox"] {
  margin-right: 12px;
  width: 20px;
  height: 20px;
  accent-color: #3b82f6;
}

.inline-label {
  font-size: 1rem;
  color: #cbd5e1;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
  flex-wrap: wrap;
}

button {
  font-size: 1rem;
  font-weight: 600;
  padding: 12px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  color: #fff;
  min-width: 140px;
}

.save-btn {
  background-color: #3b82f6;
}
.save-btn:hover {
  background-color: #2563eb;
}

.cancel-btn {
  background-color: #4b5563;
}
.cancel-btn:hover {
  background-color: #374151;
}

.delete-btn {
  background-color: #ef4444;
}
.delete-btn:hover {
  background-color: #dc2626;
}
</style>
