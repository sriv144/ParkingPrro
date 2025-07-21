<template>
  <div class="lots-container">
    <h1>Parking Lots</h1>
    <div class="lots-grid">
      <div v-for="lot in lots" :key="lot.id" class="lot-card">
        <h3>{{ lot.name }}</h3>
        <p>Occupied: {{ lot.occupied_spots }} / {{ lot.capacity }}</p>
        <button @click="editLot(lot.id)">Edit</button>
        <button @click="removeLot(lot.id)">Delete</button>

        <div class="spots">
          <span
            v-for="n in lot.capacity"
            :key="n"
            :class="{
              'spot-occupied': n <= lot.occupied_spots,
              'spot-free': n > lot.occupied_spots
            }"
          ></span>
        </div>
      </div>
    </div>

    <button class="add-lot-btn" @click="$router.push('/admin/add-lot')">
      + Add Lot
    </button>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'LotList',
  data() {
    return {
      lots: [],
    };
  },
  methods: {
    async fetchLots() {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('/api/admin/lots', {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.lots = res.data.lots;
      } catch (err) {
        console.error('Error loading lots:', err);
      }
    },
    editLot(id) {
      this.$router.push(`/admin/edit-lot/${id}`);
    },
    async removeLot(id) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`/api/admin/lots/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.fetchLots(); // reload list
      } catch (err) {
        alert(err.response?.data?.msg || 'Error deleting lot.');
      }
    },
  },
  mounted() {
    this.fetchLots();
  },
};
</script>

<style scoped>
.lots-container {
  max-width: 1200px;
  margin: auto;
  padding: 2rem;
  background: linear-gradient(to right, #000000, #2c2c2c);
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.15);
}
.lots-container h1 {
  text-align: center;
  color: #00d4ff;
  margin-bottom: 1.5rem;
}
.lots-grid {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}
.lot-card {
  flex: 1 1 260px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  color: white;
  transition: transform 0.2s;
}
.lot-card:hover {
  transform: translateY(-4px);
  backdrop-filter: blur(6px);
}
.lot-card h3 {
  margin-bottom: 0.3rem;
}
.lot-card button {
  margin-right: 0.5rem;
  margin-top: 0.5rem;
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  background: #00cfff;
  color: #001f3f;
}
.lot-card button:hover {
  background: #00aacc;
}
.lot-card .spots {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 0.75rem;
}
.spot-free,
.spot-occupied {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}
.spot-free {
  background: #3fae3f;
}
.spot-occupied {
  background: #e34e4e;
}
.add-lot-btn {
  display: block;
  margin: auto;
  background: #00d4ff;
  color: #001f3f;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.add-lot-btn:hover {
  background: #00aacc;
}
</style>
