<template>
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
          </div>
        </div>
      </div>

      <!-- Add Lot Button -->
      <button class="add-lot-btn" @click="addLot">+ Add Lot</button>
    </div>
  </div>
</template>

<script>
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
}
</style>
