<script>
import dataService from '@/components/dataService.js'
import { useVariablesStore } from '@/store.js'

export default {
  name: 'dialog-create-user',
  emits: ['exit', 'refresh'],
  data() {
    return {
      variablesStore: useVariablesStore(),
      validNewUserData: false,
      newUserUsername: '',
      newUserEmail: '',
      newUserPassword: '',
      newUserPasswordCheck: '',
      showNewUserPassword: false,
      showNewUserPasswordCheck: false,
      loadingCreateUser: false,

      isNewUserPasswordError: false,
      newUserPasswordErrorMessage: ''
    }
  },
  methods: {
    submitNewUser: function () {
      const self = this
      if (this.validNewUserData) {
        this.loadingCreateUser = true
        //Checks if passwords match
        if (this.newUserPassword === this.newUserPasswordCheck) {
          console.log('match')
          dataService
            .createUser(this.newUserEmail, this.newUserUsername, this.newUserPassword)
            .then(function () {
              self.usersList = undefined
              self.loadingCreateUser = false
              self.dialogCreateUser = false
              self.$emit('refresh')
            })
            .catch(function (error) {
              self.errorDialog = true
              self.errorUserDialogText = String(error.message + ': ' + error.response.statusText)
              self.loadingCreateUser = false
              //Also clear all fields? Maybe watch() can be used?
            })
        } else {
          this.isNewUserPasswordError = true
          this.newUserPasswordErrorMessage = 'Passwords do not match!'
          this.loadingCreateUser = false
        }
      }
    }
  }
}
</script>

<template>
  <v-card prepend-icon="mdi-account-plus-outline" title="Create New User">
    <v-form
      v-model="validNewUserData"
      :rules="variablesStore.rulesCreateUser"
      @submit.prevent="submitNewUser"
    >
      <v-card-text>
        <v-text-field
          label="Username"
          required
          v-model="newUserUsername"
          :rules="variablesStore.rulesCreateUser"
        />
        <v-text-field
          label="Email"
          required
          v-model="newUserEmail"
          :rules="variablesStore.rulesCreateUser"
          type="email"
        />
        <v-text-field
          label="Password"
          required
          v-model="newUserPassword"
          :rules="variablesStore.rulesCreateUser"
          :type="showNewUserPassword ? 'text' : 'password'"
          :append-icon="showNewUserPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showNewUserPassword = !showNewUserPassword"
          :error="isNewUserPasswordError"
          :error-messages="newUserPasswordErrorMessage"
        />
        <v-text-field
          label="Password check"
          required
          v-model="newUserPasswordCheck"
          :rules="variablesStore.rulesCreateUser"
          :type="showNewUserPasswordCheck ? 'text' : 'password'"
          :append-icon="showNewUserPasswordCheck ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showNewUserPasswordCheck = !showNewUserPasswordCheck"
          :error="isNewUserPasswordError"
          :error-messages="newUserPasswordErrorMessage"
        />
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="tonal"
          :loading="loadingCreateUser"
          type="submit"
          text="Create"
        />
        <v-btn @click="$emit('exit')" text="Cancel" />
      </v-card-actions>
    </v-form>
  </v-card>
</template>

<style scoped></style>
