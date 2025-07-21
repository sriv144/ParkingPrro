<template>
  <div class="dashboard">
    <div class="form-wrapper">
      <h1 class="form-title">Add Parking Lot</h1>
      <form class="lot-form" @submit.prevent="submitForm">
        <div class="form-group">
          <label>Prime Location Name:</label>
          <input v-model="form.name" type="text" required />
        </div>

        <div class="form-group">
          <label>Address:</label>
          <textarea v-model="form.address" required></textarea>
        </div>

        <div class="form-double">
          <div class="form-group">
            <label>Pin Code:</label>
            <input v-model="form.pin_code" required maxlength="6" />
          </div>
          <div class="form-group">
            <label>Price (per hour):</label>
            <input v-model="form.price" type="number" min="1" required />
          </div>
        </div>

        <div class="form-group">
          <label>Number of Spots:</label>
          <input v-model="form.number_of_spots" type="number" min="1" required />
        </div>

        <div class="form-actions">
          <button type="submit" class="submit-btn">Add Lot</button>
          <button type="button" class="cancel-btn" @click="cancel">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AddLot',
  data() {
    return {
      form: {
        name: '',
        address: '',
        pin_code: '',
        price: '',
        number_of_spots: ''
      }
    };
  },
  methods: {
    async submitForm() {
      const token = localStorage.getItem('token');
      const payload = {
        prime_location_name: this.form.name,
        address: this.form.address,
        pin_code: this.form.pin_code,
        price: parseFloat(this.form.price),
        number_of_spots: parseInt(this.form.number_of_spots)
      };

      try {
        const res = await axios.post('/api/admin/lots', payload, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        // Notify AdminDashboard via custom event
        window.dispatchEvent(new CustomEvent('lot-added', {
          detail: {
            id: res.data.lot_id,
            name: payload.prime_location_name,
            address: payload.address,
            pin_code: payload.pin_code,
            price: payload.price,
            capacity: payload.number_of_spots,
            occupied_spots: 0
          }
        }));

        this.$router.push('/admin');
      } catch (err) {
        if (err.response?.data?.msg === 'Token has expired') {
          localStorage.removeItem('token');
          alert('Session expired. Please login again.');
          this.$router.push('/login');
        } else {
          alert(err.response?.data?.msg || 'Failed to add lot');
        }
      }
    },
    cancel() {
      this.$router.push('/admin');
    }
  }
};
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: linear-gradient(to right, #0d1117, #2e2e2e);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}
.form-wrapper {
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(14px);
  padding: 2rem;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 255, 255, 0.1);
}
.form-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 1.5rem;
  color: #00d4ff;
}
.lot-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
label {
  margin-bottom: 0.3rem;
  font-weight: 600;
}
input,
textarea {
  padding: 0.7rem;
  border-radius: 8px;
  border: none;
  background: #1f2a3a;
  color: white;
}
.form-double {
  display: flex;
  gap: 1rem;
}
.form-double .form-group {
  flex: 1;
}
.form-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}
.submit-btn,
.cancel-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
}
.submit-btn {
  background-color: #00d4ff;
  color: black;
}
.submit-btn:hover {
  background-color: #00bcd4;
}
.cancel-btn {
  background-color: #ccc;
}
.cancel-btn:hover {
  background-color: #aaa;
}
</style>
