<template>
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
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddLot',
  data() {
    return {
      form: {
        name: '',
        address: '',
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
    },
    cancel() {
      this.$router.push('/admin');
    }
  }
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
}
</style>
