<!-- src/components/LotList.vue -->
<template>
  <div class="lots-container">
    <h1>Parking Lots</h1>
    <div class="lots-grid">
      <div v-for="lot in lots" :key="lot.id" class="lot-card">
        <h3>{{ lot.name }}</h3>
        <p>Occupied: {{ lot.occupied }} / {{ lot.capacity }}</p>
        <button @click="editLot(lot.id)">Edit</button>
        <button @click="removeLot(lot.id)">Delete</button>
        <div class="spots">
          <span
            v-for="n in lot.capacity"
            :key="n"
            :class="{'spot-occupied': n <= lot.occupied, 'spot-free': n > lot.occupied}"
          ></span>
        </div>
      </div>
    </div>
    <button class="add-lot-btn" @click="$router.push('/admin/lots/new')">
      + Add Lot
    </button>
  </div>
</template>

<script>
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
};
</script>

<style scoped>
.lots-container {
  max-width: 1200px;
  margin: auto;
}
.lots-grid {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}
.lot-card {
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
  background: #00d4ff;
  color: #001f3f;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
