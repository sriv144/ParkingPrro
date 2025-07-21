<template>
  <div class="dashboard">
    <AdminNavbar />

    <!-- This handles child routes like add-lot/edit-lot -->
    <router-view v-if="$route.name !== 'AdminDashboard'" />

    <!-- Dashboard content -->
    <div v-else>
      <div class="dashboard-header">
        <h1>Admin Dashboard</h1>
        <p>Manage all parking lots in your system</p>

        <div class="stats">
          <div class="stat-card">
            <h2>{{ lots.length }}</h2>
            <p>Total Lots</p>
          </div>
          <div class="stat-card">
            <h2>{{ totalOccupied }}</h2>
            <p>Occupied Spots</p>
          </div>
          <div class="stat-card">
            <h2>{{ totalFree }}</h2>
            <p>Free Spots</p>
          </div>
          <div class="stat-card">
            <h2>{{ totalCapacity }}</h2>
            <p>Total Capacity</p>
          </div>
        </div>
      </div>

      <div class="parking-lots">
        <div class="lot-card" v-for="lot in lots" :key="lot.id">
          <h2>{{ lot.name }}</h2>
          <p class="occupied">Occupied: {{ lot.occupied_spots }} / {{ lot.capacity }}</p>

          <div class="slot-grid">
            <button
              v-for="index in lot.capacity"
              :key="index"
              class="slot"
              :class="index <= lot.occupied_spots ? 'occupied-slot' : 'available-slot'"
              :title="index <= lot.occupied_spots ? 'Occupied' : 'Available'"
              disabled
            >
              {{ index }}
            </button>
          </div>

          <div class="actions">
            <router-link :to="`/admin/edit-lot/${lot.id}`" class="edit-btn">Edit</router-link>
            <button @click="deleteLot(lot.id)" class="delete-btn">Delete</button>
          </div>
        </div>
      </div>

      <div class="add-btn-wrapper">
        <router-link to="/admin/add-lot" class="add-btn">+ Add Lot</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import AdminNavbar from './AdminNavbar.vue';

export default {
  name: 'AdminDashboard',
  components: { AdminNavbar },
  data() {
    return {
      lots: []
    };
  },
  computed: {
    totalOccupied() {
      return this.lots.reduce((sum, lot) => sum + lot.occupied_spots, 0);
    },
    totalCapacity() {
      return this.lots.reduce((sum, lot) => sum + lot.capacity, 0);
    },
    totalFree() {
      return this.totalCapacity - this.totalOccupied;
    }
  },
  methods: {
    async fetchLots() {
      try {
        const res = await axios.get('/api/admin/lots', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.lots = res.data.lots;
      } catch (err) {
        console.error('Failed to fetch lots:', err);
      }
    },
    async deleteLot(id) {
      try {
        await axios.delete(`/api/admin/lots/${id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.fetchLots(); // Refresh after deletion
      } catch (err) {
        alert(err.response?.data?.msg || "Failed to delete lot");
      }
    },
    handleLotAdded() {
      this.fetchLots(); // Re-fetch on lot added
    }
  },
  mounted() {
    this.fetchLots();

    // 🔁 Listen for real-time updates via custom event
    window.addEventListener('lot-added', this.handleLotAdded);
  },
  unmounted() {
    window.removeEventListener('lot-added', this.handleLotAdded);
  }
};
</script>

<style scoped>
.dashboard {
  font-family: 'Segoe UI', sans-serif;
  background: linear-gradient(to right, #0d1117, #2e2e2e);
  color: white;
  min-height: 100vh;
  padding-bottom: 3rem;
}
.dashboard-header {
  text-align: center;
  padding-top: 2rem;
}
.dashboard-header h1 {
  font-size: 2.8rem;
  margin-bottom: 0.5rem;
}
.dashboard-header p {
  color: #bbb;
  font-size: 1.2rem;
  margin-bottom: 2rem;
}
.stats {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 3rem;
}
.stat-card {
  background-color: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(8px);
  padding: 1.5rem 2rem;
  border-radius: 12px;
  width: 180px;
  text-align: center;
  box-shadow: 0 4px 14px rgba(0, 255, 255, 0.2);
}
.stat-card h2 {
  color: #00d4ff;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}
.parking-lots {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem;
  padding: 0 1.5rem;
}
.lot-card {
  background-color: #1f2a3a;
  padding: 1.5rem;
  border-radius: 10px;
  width: 280px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  text-align: center;
}
.lot-card h2 {
  font-size: 1.3rem;
  margin-bottom: 0.3rem;
}
.occupied {
  font-size: 1rem;
  margin-bottom: 0.8rem;
  color: #00d4ff;
}
.slot-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.4rem;
  margin: 1rem 0;
}
.slot {
  padding: 0.5rem;
  border-radius: 6px;
  font-weight: bold;
  font-size: 1rem;
  border: none;
  cursor: default;
}
.available-slot {
  background-color: #2ecc71;
  color: #fff;
}
.occupied-slot {
  background-color: #e74c3c;
  color: #fff;
}
.actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}
.edit-btn, .delete-btn {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-weight: bold;
  text-align: center;
  text-decoration: none;
  font-size: 0.9rem;
}
.edit-btn {
  background-color: #00b894;
  color: white;
}
.delete-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  cursor: pointer;
}
.add-btn-wrapper {
  text-align: center;
  margin-top: 2rem;
}
.add-btn {
  background-color: #2980b9;
  color: white;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 10px;
  text-decoration: none;
  font-weight: bold;
  transition: background 0.2s ease;
}
.add-btn:hover {
  background-color: #3498db;
}
</style>
