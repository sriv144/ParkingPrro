<template>
  <div class="container py-3">
    <h2>{{ isEdit ? 'Edit Lot' : 'New Lot' }}</h2>
    <form @submit.prevent="submit">
      <div class="mb-3">
        <label class="form-label">Name</label>
        <input v-model="form.prime_location_name" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Address</label>
        <input v-model="form.address" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Pincode</label>
        <input v-model="form.pin_code" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Price</label>
        <input v-model.number="form.price" type="number" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Number of Spots</label>
        <input v-model.number="form.number_of_spots" type="number" class="form-control" required />
      </div>
      <button class="btn btn-success">{{ isEdit ? 'Update' : 'Create' }}</button>
      <router-link to="/admin/lots" class="btn btn-secondary ms-2">Cancel</router-link>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LotForm',
  props: ['id'],
  data() {
    return {
      form: {
        prime_location_name: '',
        address: '',
        pin_code: '',
        price: 0,
        number_of_spots: 0
      }
    }
  },
  computed: {
    isEdit() { return !!this.id }
  },
  methods: {
    fetchLot() {
      const token = localStorage.getItem('adminToken')
      axios.get(`/api/admin/lots/${this.id}`, { headers: { Authorization: `Bearer ${token}` } })
           .then(r => {
             const d = r.data
             this.form = {
               prime_location_name: d.name,
               address: d.address,
               pin_code: d.pin_code,
               price: d.price,
               number_of_spots: d.capacity
             }
           })
    },
    submit() {
      const token = localStorage.getItem('adminToken')
      const cfg = { headers: { Authorization: `Bearer ${token}` } }
      if (this.isEdit) {
        axios.put(`/api/admin/lots/${this.id}`, this.form, cfg)
             .then(() => this.$router.push('/admin/lots'))
      } else {
        axios.post('/api/admin/lots', this.form, cfg)
             .then(() => this.$router.push('/admin/lots'))
      }
    }
  },
  mounted() {
    if (this.isEdit) this.fetchLot()
  }
}
</script>
