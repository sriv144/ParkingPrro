<template>
<<<<<<< HEAD
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
=======
  <div class="background-wrapper">
    <!-- Navbar -->
    <div class="navbar">
      <button class="nav-btn" @click="$router.push('/admin')">Home</button>
      <button class="nav-btn" @click="$router.push('/admin/users')">Users</button>
      <button class="nav-btn" @click="$router.push('/admin/search')">Search</button>
      <button class="nav-btn" @click="$router.push('/admin/summary')">Summary</button>
      <button class="nav-btn logout-btn" @click="$router.push('/login')">Logout</button>
    </div>

    <div class="container">
      <h1 class="dashboard-title">Parking Lot Overview</h1>

      <div class="lots-grid">
        <div v-for="lot in parkingLots" :key="lot.id" class="lot-card">
          <div class="lot-header">
            <span class="lot-name">Lot #{{ lot.lotNumber }}</span>
            <div class="lot-actions">
              <button class="lot-btn" @click="editLot(lot)">Edit</button>
              <button class="lot-btn" @click="deleteLot(lot)">Delete</button>
            </div>
          </div>

          <div class="lot-occupancy">
            Occupancy:
            <span :style="{color: occupiedCount(lot) ? '#18f04a' : '#ff4141'}">
              {{ occupiedCount(lot) }}/{{ lot.spots.length }}
            </span>
          </div>

          <div class="lot-matrix">
            <span 
              v-for="spot in lot.spots" 
              :key="spot.id"
              :class="spot.occupied ? 'matrix-dot matrix-dot-occupied' : 'matrix-dot matrix-dot-vacant'"
            >
              {{ spot.occupied ? 'O' : 'A' }}
            </span>
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
          </div>
        </div>
      </div>

<<<<<<< HEAD
      <div class="add-btn-wrapper">
        <router-link to="/admin/add-lot" class="add-btn">+ Add Lot</router-link>
      </div>
=======
      <!-- Add Lot Button -->
      <button class="add-lot-btn" @click="addLot">+ Add Lot</button>
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
    </div>
  </div>
</template>

<script>
<<<<<<< HEAD
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
=======
export default {
  name: 'AdminDashboard',
  data() {
    return {
      parkingLots: [
        {
          id: 1,
          lotNumber: 1,
          spots: [
            { id: 1, occupied: true },
            { id: 2, occupied: false },
            { id: 3, occupied: true },
            { id: 4, occupied: false },
            { id: 5, occupied: true }
          ]
        },
        {
          id: 2,
          lotNumber: 2,
          spots: [
            { id: 1, occupied: true },
            { id: 2, occupied: true },
            { id: 3, occupied: true },
            { id: 4, occupied: false }
          ]
        }
      ]
    }
  },
  methods: {
    occupiedCount(lot) {
      return lot.spots.filter(s => s.occupied).length;
    },
    editLot(lot) {
      this.$router.push(`/admin/edit-lot/${lot.id}`);
    },
    deleteLot(lot) {
      if (confirm(`Are you sure you want to delete Lot #${lot.lotNumber}?`)) {
        this.parkingLots = this.parkingLots.filter(l => l.id !== lot.id);
      }
    },
    addLot() {
      this.$router.push('/admin/add-lot');
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

* {
  font-family: 'Poppins', sans-serif;
}

.background-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c0c24 0%, #1a2970 100%);
  color: white;
  padding-bottom: 60px;
}

.navbar {
  display: flex;
  justify-content: flex-start;
  gap: 12px;
  padding: 20px 32px;
  background: rgba(10, 10, 30, 0.9);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
}

.nav-btn {
  background: #1a2970;
  color: #b5ebff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  background: #2a3b8f;
  color: #fff;
}

.logout-btn {
  margin-left: auto;
  background-color: #f44336;
  color: white;
}

.logout-btn:hover {
  background-color: #d32f2f;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.dashboard-title {
  font-size: 2.4rem;
  font-weight: 700;
  margin-bottom: 30px;
  background: linear-gradient(to right, #fff, #b5ebff 70%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.lots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(370px, 1fr));
  gap: 34px 40px;
}

.lot-card {
  background: rgba(30, 34, 50, 0.85);
  border-radius: 18px;
  box-shadow: 0 8px 32px rgba(24,32,36,0.13);
  padding: 26px 32px 24px 32px;
  min-height: 180px;
}

.lot-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 14px;
}

.lot-name {
  font-weight: 700;
  font-size: 1.15rem;
}

.lot-actions {
  display: flex;
  gap: 10px;
}

.lot-btn {
  background: rgba(50,80,120,0.24);
  color: #54c8ff;
  border: none;
  border-radius: 6px;
  padding: 6px 14px;
  cursor: pointer;
}

.lot-btn:hover {
  background: #252f48;
  color: #fff;
}

.lot-occupancy {
  margin-bottom: 8px;
  font-size: 1.1rem;
}

.lot-matrix {
  margin-top: 5px;
  display: flex;
  flex-wrap: wrap;
  gap: 9px 7px;
}

.matrix-dot {
  display: inline-flex;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
  color: #fff;
  background: #222b33;
}

.matrix-dot-occupied {
  background: #ff4141;
}

.matrix-dot-vacant {
  background: #18f04a;
}

.add-lot-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: #03a9f4;
  color: white;
  border: none;
  padding: 14px 22px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 6px 16px rgba(0, 162, 255, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-lot-btn:hover {
  background: #0288d1;
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
}
</style>
