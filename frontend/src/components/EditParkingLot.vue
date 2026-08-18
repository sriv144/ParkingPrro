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
          Pin Code
          <input v-model="lot.pincode" type="text" required />
        </label>

        <label>
          Price (per hour)
          <input v-model.number="lot.price" type="number" min="0" />
        </label>

        <label>
          Maximum Spots
          <input v-model.number="lot.maxSpots" type="number" min="0" />
        </label>

        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="cancelEdit">Cancel</button>
          <button type="submit" class="save-btn">Save Changes</button>
          <button type="button" class="delete-btn" @click="deleteLot">Delete</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "EditParkingLot",
  props: {
    id: { type: [String, Number], required: true },
  },
  data() {
    return {
      lot: {
        name: "",
        address: "",
        pincode: "",
        price: null,
        maxSpots: null,
      },
    };
  },
  methods: {
    requestConfig() {
      return { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } };
    },
    async fetchLot() {
      try {
        const { data } = await axios.get(`/api/admin/lots/${this.id}`, this.requestConfig());
        this.lot = {
          name: data.name,
          address: data.address,
          pincode: data.pin_code,
          price: data.price,
          maxSpots: data.capacity,
        };
      } catch (err) {
        alert(err.response?.data?.msg || "Failed to load parking lot");
        this.$router.push("/admin");
      }
    },
    async updateLot() {
      try {
        await axios.put(`/api/admin/lots/${this.id}`, {
          prime_location_name: this.lot.name,
          address: this.lot.address,
          pin_code: this.lot.pincode,
          price: Number(this.lot.price),
          number_of_spots: Number(this.lot.maxSpots),
        }, this.requestConfig());
        this.$router.push("/admin");
      } catch (err) {
        alert(err.response?.data?.msg || "Failed to update parking lot");
      }
    },
    async deleteLot() {
      try {
        await axios.delete(`/api/admin/lots/${this.id}`, this.requestConfig());
        this.$router.push("/admin");
      } catch (err) {
        alert(err.response?.data?.msg || "Failed to delete parking lot");
      }
    },
    cancelEdit() {
      this.$router.back();
    },
  },
  mounted() {
    this.fetchLot();
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
