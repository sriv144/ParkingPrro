<template>
  <div class="container py-3">
    <h2>Users</h2>
    <table class="table">
      <thead>
        <tr>
          <th>ID</th><th>Username</th><th>Email</th><th>Active Spots</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.id }}</td>
          <td>{{ u.username }}</td>
          <td>{{ u.email }}</td>
          <td>{{ u.active_spot_ids.join(', ') || 'None' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserList',
  data() { return { users: [] } },
  methods: {
    fetchUsers() {
      const token = localStorage.getItem('adminToken')
      axios.get('/api/admin/users', { headers: { Authorization: `Bearer ${token}` } })
           .then(r => this.users = r.data.users)
    }
  },
  mounted() { this.fetchUsers() }
}
</script>
