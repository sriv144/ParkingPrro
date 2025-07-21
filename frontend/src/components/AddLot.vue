<template>
<<<<<<< HEAD
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
=======
  <div class="background-wrapper">
    <div class="add-lot-container">
      <h2 class="add-lot-title">New Parking Lot</h2>
      <form @submit.prevent="submitForm" class="add-lot-form">
        <div class="form-row">
          <label>Prime Location Name:</label>
          <input v-model="form.name" type="text" required placeholder="e.g. Velachery Plaza" />
        </div>
        <div class="form-row">
          <label>Address:</label>
          <textarea v-model="form.address" rows="2" required placeholder="Street, City, State"></textarea>
        </div>
        <div class="form-row double">
          <div>
            <label>Pin code:</label>
            <input v-model="form.pincode" type="text" maxlength="6" pattern="[0-9]*" required placeholder="600100" />
          </div>
          <div>
            <label>Price (per hour):</label>
            <input v-model="form.price" type="number" min="0" required placeholder="20" />
          </div>
        </div>
        <div class="form-row double">
          <div>
            <label>Maximum spots:</label>
            <input v-model="form.maxSpots" type="number" min="1" required placeholder="15" />
          </div>
          <div>
            <label>Type:</label>
            <select v-model="form.type">
              <option>Open</option>
              <option>Covered</option>
              <option>Valet</option>
              <option>Multi-level</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <label>Security Level:</label>
          <select v-model="form.security">
            <option>Basic (CCTV only)</option>
            <option>Guarded</option>
            <option>Gated & Secure</option>
          </select>
        </div>
        <div class="form-row">
          <label>Notes / Description:</label>
          <textarea v-model="form.notes" rows="2" placeholder="Extra details (optional)"></textarea>
        </div>
        <div class="form-actions">
          <button class="submit-btn" type="submit">Add</button>
          <button class="cancel-btn" type="button" @click="cancel">Cancel</button>
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
        </div>
      </form>
    </div>
  </div>
</template>

<script>
<<<<<<< HEAD
import axios from 'axios';

=======
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
export default {
  name: 'AddLot',
  data() {
    return {
      form: {
        name: '',
        address: '',
<<<<<<< HEAD
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
=======
        pincode: '',
        price: '',
        maxSpots: '',
        type: 'Open',
        security: 'Basic (CCTV only)',
        notes: ''
      }
    }
  },
  methods: {
    submitForm() {
      // Here you can do form validation, and call an API to save the parking lot.
      alert('Parking Lot added!\n\n' + JSON.stringify(this.form, null, 2));
      this.$router.push('/admin'); // After submission, go to dashboard
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
    },
    cancel() {
      this.$router.push('/admin');
    }
  }
<<<<<<< HEAD
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
=======
}
</script>

<style scoped>
.background-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c0c24 0%, #1a2970 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.add-lot-container {
  background: rgba(30, 34, 50, 0.93);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(24,32,36,0.13);
  max-width: 440px;
  width: 98%;
  margin: 32px 0;
  padding: 30px 32px 24px 32px;
}
.add-lot-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 22px;
  letter-spacing: -.5px;
  color: #f9cf61;
  background: #ffe58a;
  border-radius: 9px;
  padding: 8px 0 6px 0;
  text-align: center;
  box-shadow: 0 2px 8px rgba(255,220,60,0.09);
}
.add-lot-form {
  display: flex;
  flex-direction: column;
  gap: 17px;
}
.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-row.double {
  flex-direction: row;
  gap: 20px;
}
.form-row.double > div { flex: 1; }
label {
  font-size: 1rem;
  color: #f4f4f4;
  font-weight: 600;
}
input, textarea, select {
  border: none;
  border-radius: 8px;
  padding: 9px 13px;
  font-size: 1rem;
  background: #232d3e;
  color: #fff;
  outline: none;
  box-shadow: 0 1px 4px rgba(22,20,60,0.07);
  margin-bottom: 2px;
  transition: background 0.14s, border-color 0.14s;
}
input:focus, textarea:focus, select:focus {
  background: #273771;
  border: 1.5px solid #b1e5fe;
}
.form-actions {
  display: flex;
  gap: 24px;
  justify-content: center;
  margin-top: 10px;
}
.submit-btn {
  background: linear-gradient(90deg, #3cd2fa 50%, #15c3ff 100%);
  color: #1a2970;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 1.15rem;
  padding: 8px 24px;
  cursor: pointer;
  box-shadow: 0 1px 8px #17b3d944;
  transition: background 0.13s, color 0.13s;
}
.submit-btn:hover { background: #12c2f7; color: #fff; }
.cancel-btn {
  background: #e0eafc;
  color: #3e4c8a;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.05rem;
  padding: 8px 24px;
  cursor: pointer;
  box-shadow: 0 1px 8px #212d47aa;
  transition: background 0.13s, color 0.13s;
}
.cancel-btn:hover { background: #bccbe6; color: #0e1743; }

@media (max-width: 600px) {
  .add-lot-container { padding: 12px 6vw; }
  .form-row.double { flex-direction: column; gap: 6px; }
  .add-lot-title { font-size: 1.2rem; padding: 5px 0 5px 0; }
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
}
</style>
