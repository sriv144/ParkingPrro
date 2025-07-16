<template>
  <div class="frosted-section">
    <div class="section-header">
      <h2>Search Parking Lots</h2>
    </div>
    <div class="search-row">
      <label>
        <span>Search by</span>
        <select v-model="searchBy">
          <option value="userId">User ID</option>
          <option value="spotId">Parking Spot ID</option>
          <option value="location">Location</option>
        </select>
      </label>
      <input v-model="searchString" placeholder="search string..." />
      <button @click="performSearch">Search</button>
    </div>
    <div class="search-results" v-if="results.length">
      <h3>Example search parking lots <span v-if="searchString">@{{searchString}}</span></h3>
      <div class="lots-grid">
        <div v-for="lot in results" :key="lot.id" class="lot-result-card">
          <div class="lot-header">{{ lot.name }}</div>
          <div class="lot-occupancy">Occupied: {{ lot.occupied }}/{{ lot.spots }}</div>
          <div class="matrix">
            <span v-for="i in lot.spots" :key="i"
              :class="i<=lot.occupied ? 'dot-occupied' : 'dot-vacant'">
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue';
const searchBy = ref("userId");
const searchString = ref("");
const results = ref([
  // Example results
  { id: 12, name: "Parking#12", spots: 10, occupied: 3 },
  { id: 21, name: "Parking#21", spots: 10, occupied: 6 }
]);
function performSearch() {
  // Replace with your API/search logic!
  // This is just mock display.
}
</script>
<style scoped>
.frosted-section {
  background: rgba(30, 34, 50, 0.93);
  border-radius: 18px;
  box-shadow: 0 4px 18px rgba(24,32,36,0.12);
  padding: 30px 20px;
  margin: 32px 0;
}
.section-header h2 { margin-bottom: 20px; color: #b7e4ff; }
.search-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
.search-row select, .search-row input {
  padding: 7px 12px;
  border-radius: 7px;
  border: 1.5px solid #303951;
  background: rgba(24,34,60,0.82);
  color: #f4f7fa;
  font-size: 1rem;
}
.search-row button {
  background: linear-gradient(95deg, #58d5f7, #18f0c8 99%);
  color: #003447;
  border-radius: 7px;
  border: none;
  padding: 7px 20px;
  font-weight: 600;
  cursor: pointer;
}
.lots-grid {
  display: flex;
  gap: 26px;
  margin-top: 14px;
}
.lot-result-card {
  background: rgba(44, 50, 70, 0.96);
  border-radius: 13px;
  box-shadow: 0 2px 8px rgba(24,32,36,0.08);
  padding: 18px 22px 18px 22px;
  min-width: 170px;
}
.lot-header { font-weight: 600; color: #58d5f7; margin-bottom: 6px;}
.lot-occupancy { color: #b2ffad; margin-bottom: 9px; }
.matrix { display: flex; gap: 5px;}
.dot-occupied, .dot-vacant {
  display: inline-block;
  width: 18px; height: 18px; border-radius: 4px;
}
.dot-occupied { background: #ef4444; }
.dot-vacant { background: #10b981; }
</style>
