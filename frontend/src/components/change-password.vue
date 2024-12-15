<script>
import dataService from './dataService'

export default {
  data() {
    return {
      ds: dataService,
      loading: false,
      oldPassword: '',
      newPassword: '',
      checkPassword: '',
      showOld: false,
      showNew: false,
      showCheck: false,
      dialog: false,
      validData: false,
      noMatchSnackbar: false,
      wrongAuthSnackbar: false,
      regole: [
        function (value) {
          if (value) return true
          return 'This field cannot be empty'
        }
      ]
    }
  },
  methods: {
    submit: function () {
      const self = this
      this.loading = true
      console.log(this.newPassword)
      console.log(this.checkPassword)
      if (this.newPassword === this.checkPassword) {
        console.log('they match')
        dataService
          .changePassword(this.oldPassword, this.newPassword)
          .then(function (data) {
            console.log(data)
            self.dialog = true //Dialog to show 'success'
            self.loading = false
          })
          .catch(function (error) {
            if (error.response.status == 400) {
              self.wrongAuthSnackbar = true
              self.clearFields()
            }
          })
      } else {
        self.noMatchSnackbar = true
        self.clearFields()
      }
    },
    clearFields: function () {
      this.loading = false
      this.oldPassword = ''
      this.newPassword = ''
      this.checkPassword = ''
    },
    changeSuccess: function () {
      this.dialog = false
      //Go to previous page
      this.$router.go(-1)
    }
  }
}
</script>

<template>
  <v-container>
    <v-sheet class="mx-auto" width="300px">
      <div class="text-h4 py-4">Change Password</div>
      <v-form @submit.prevent="submit" v-model="validData" :rules="regole">
        <v-text-field
          :type="showOld ? 'text' : 'password'"
          label="Old Password"
          v-model="oldPassword"
          :append-icon="showOld ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showOld = !showOld"
        ></v-text-field>

        <v-text-field
          :type="showNew ? 'text' : 'password'"
          label="New Password"
          v-model="newPassword"
          :append-icon="showNew ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showNew = !showNew"
        ></v-text-field>

        <v-text-field
          :type="showCheck ? 'text' : 'password'"
          label="Check New Password"
          v-model="checkPassword"
          :append-icon="showCheck ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showCheck = !showCheck"
        ></v-text-field>

        <v-btn type="submit" align="center" class="ma-2" :loading="loading">Confirm</v-btn>
      </v-form>
    </v-sheet>
    <v-snackbar v-model="noMatchSnackbar" timeout="3000">
      Passwords do not match!

      <template v-slot:actions>
        <v-btn color="red" variant="text" @click="noMatchSnackbar = false"> Close </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar v-model="wrongAuthSnackbar" timeout="3000">
      Wrong Old Password!

      <template v-slot:actions>
        <v-btn color="red" variant="text" @click="wrongAuthSnackbar = false"> Close </v-btn>
      </template>
    </v-snackbar>
    <v-dialog v-model="dialog" width="auto">
      <v-card
        max-width="400"
        prepend-icon="mdi-check-circle-outline"
        text="Password updated successfully. You will now be redirected to the previous page"
        title="Success"
      >
        <template v-slot:actions>
          <v-btn class="ms-auto" text="Ok" @click="changeSuccess()"></v-btn>
        </template>
      </v-card>
    </v-dialog>
  </v-container>
</template>
