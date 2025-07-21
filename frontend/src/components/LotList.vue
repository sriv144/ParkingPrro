<<<<<<< HEAD
=======
<!-- src/components/LotList.vue -->
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
<template>
  <div class="lots-container">
    <h1>Parking Lots</h1>
    <div class="lots-grid">
      <div v-for="lot in lots" :key="lot.id" class="lot-card">
        <h3>{{ lot.name }}</h3>
<<<<<<< HEAD
        <p>Occupied: {{ lot.occupied_spots }} / {{ lot.capacity }}</p>
        <button @click="editLot(lot.id)">Edit</button>
        <button @click="removeLot(lot.id)">Delete</button>

=======
        <p>Occupied: {{ lot.occupied }} / {{ lot.capacity }}</p>
        <button @click="editLot(lot.id)">Edit</button>
        <button @click="removeLot(lot.id)">Delete</button>
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
        <div class="spots">
          <span
            v-for="n in lot.capacity"
            :key="n"
<<<<<<< HEAD
            :class="{
              'spot-occupied': n <= lot.occupied_spots,
              'spot-free': n > lot.occupied_spots
            }"
=======
            :class="{'spot-occupied': n <= lot.occupied, 'spot-free': n > lot.occupied}"
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
          ></span>
        </div>
      </div>
    </div>
<<<<<<< HEAD

    <button class="add-lot-btn" @click="$router.push('/admin/add-lot')">
=======
    <button class="add-lot-btn" @click="$router.push('/admin/lots/new')">
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
      + Add Lot
    </button>
  </div>
</template>

<script>
<<<<<<< HEAD
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
=======
export default {
  name: "LotList",
  data() {
    return {
      // stub data for now
      lots: [
        { id: 1, name: "Lot #1", occupied: 3, capacity: 5 },
        { id: 2, name: "Lot #2", occupied: 4, capacity: 4 },
      ],
    };
  },
  methods: {
    editLot(id) {
      this.$router.push(`/admin/lots/${id}/edit`);
    },
    removeLot(id) {
      // TODO: call backend, then:
      this.lots = this.lots.filter(l => l.id !== id);
    },
  },
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
};
</script>

<style scoped>
.lots-container {
  max-width: 1200px;
  margin: auto;
<<<<<<< HEAD
  padding: 2rem;
  background: linear-gradient(to right, #000000, #2c2c2c);
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.15);
}
.lots-container h1 {
  text-align: center;
  color: #00d4ff;
  margin-bottom: 1.5rem;
=======
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
}
.lots-grid {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}
.lot-card {
<<<<<<< HEAD
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
=======
  flex: 1 1 200px;
  background: rgba(0,0,0,0.05);
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.lot-card .spots {
  display: flex;
  gap: 4px;
  margin-top: 0.75rem;
}
.spot-free {
  width: 16px;
  height: 16px;
  background: #3fae3f;
}
.spot-occupied {
  width: 16px;
  height: 16px;
  background: #e34e4e;
}
.add-lot-btn {
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
  background: #00d4ff;
  color: #001f3f;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
<<<<<<< HEAD
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.add-lot-btn:hover {
  background: #00aacc;
=======
  cursor: pointer;
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
}
</style>
