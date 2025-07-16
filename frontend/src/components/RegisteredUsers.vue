<template>
  <div class="frosted-section">
    <div class="section-header">
      <h2>Registered Users</h2>
    </div>
    <table class="users-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>E-Mail</th>
          <th>Full Name</th>
          <th>Address</th>
          <th>Pin code</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in props.users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.fullName }}</td>
          <td>{{ user.address }}</td>
          <td>{{ user.pin }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
// eslint-disable-next-line no-undef
const props = defineProps(['users']);
</script>
<style scoped>
.frosted-section {
  background: rgba(30, 34, 50, 0.93);
  border-radius: 18px;
  box-shadow: 0 4px 18px rgba(24,32,36,0.12);
  padding: 30px 20px;
  margin: 32px 0;
}
.section-header h2 {
  margin-bottom: 20px;
  font-size: 1.22rem;
  color: #b7e4ff;
}
.users-table {
  width: 100%;
  border-collapse: collapse;
}
.users-table th, .users-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #303951;
}
.users-table th {
  color: #58d5f7;
  font-weight: 600;
  background: rgba(50,70,90,0.16);
}
.users-table td {
  color: #f4f7fa;
}
</style>
