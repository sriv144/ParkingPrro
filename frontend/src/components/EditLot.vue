<template>
  <div class="edit-container">
    <h1>Edit Parking Lot</h1>
    <p>Update parking lot information</p>
    <div class="form">
      <label>Prime Location Name</label>
      <input type="text" />

      <label>Address</label>
      <textarea></textarea>

      <label>Landmark</label>
      <textarea></textarea>

      <div class="actions">
        <button class="save">Save Changes</button>
        <button class="delete">Delete</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "EditParkingLot",
};
</script>

<style scoped>
.edit-container {
  padding: 2rem;
  background-color: #111;
  color: #fff;
  min-height: 100vh;
}

.edit-container h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.edit-container p {
  margin-bottom: 2rem;
  color: #ccc;
}

.form {
  background-color: #1a1a1a;
  padding: 2rem;
  border-radius: 10px;
}

label {
  display: block;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

input,
textarea {
  width: 100%;
  background-color: #2c2c2c;
  border: none;
  padding: 10px;
  color: #fff;
  border-radius: 5px;
  margin-bottom: 1rem;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

.save {
  background-color: #00bfff;
  border: none;
  padding: 10px 20px;
  color: white;
  border-radius: 5px;
}

.delete {
  background-color: #e74c3c;
  border: none;
  padding: 10px 20px;
  color: white;
  border-radius: 5px;
}
</style>
