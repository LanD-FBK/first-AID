<script>
import dataService from '@/components/dataService.js'
import { useVariablesStore } from '@/store.js'

export default {
  name: 'dialog-user-form',
  emits: ['exit'],
  props: {
    userData: Object
  },
  data() {
    return {
      variablesStore: useVariablesStore(),

      isEditUserPasswordChange: false,
      editUserPassword: '',
      editUSerPasswordCheck: '',
      showEditUserPassword: false,
      showEditUserPasswordCheck: false,
      isEditUserPasswordError: false,
      editPasswordErrorMessage: '',
      editUserIsActiveLoading: false,
      isUserModifyDialogLoaded: false,
      loadingModifyUserDetails: false,

      dialogEditUser: false,
      dialogModifyUserDetails: false,
      validEditUserData: false,

      editUserID: this.userData.id,
      editUserUsername: this.userData.username,
      editUserEmail: this.userData.email,
      editUserIsActive: !!this.userData.is_active,
    }
  },
  methods: {
    submitEditUser: function () {
      const self = this
      if (this.validEditUserData) {
        this.loadingModifyUserDetails = true
        if (this.editUserPassword === this.editUSerPasswordCheck) {
          dataService
            .editUser(
              this.editUserEmail,
              this.editUserUsername,
              this.editUserPassword,
              this.editUserID
            )
            .then(function (data) {
              console.log(data)
              self.loadingModifyUserDetails = false
              self.dialogModifyUserDetails = false
            })
            .catch(function (error) {
              self.errorDialog = true
              self.errorUserDialogText = String(error.message + ': ' + error.response.statusText)
              console.log(error)
            })
        } else {
          this.isEditUserPasswordError = true
          this.editPasswordErrorMessage = 'Passwords do not match!'
        }
      }
    },
  }
}
</script>

<template>
  <v-card title="Edit User" prepend-icon="mdi-account-edit-outline">
    <v-form
      @submit.prevent="submitEditUser"
      v-model="validEditUserData"
      :rules="variablesStore.rulesCreateUser"
    >
      <v-card-text>
        <v-row dense>
          <v-col cols="12" md="9" sm="9">
            <v-text-field
              label="Username"
              type="text"
              v-model="editUserUsername"
              :rules="variablesStore.rulesCreateUser"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3" sm="3">
            <v-checkbox
              label="Is Active"
              class="ml-2"
              v-model="editUserIsActive"
              :undefined="editUserIsActiveLoading"
              :disabled="editUserIsActiveLoading"
            ></v-checkbox>
          </v-col>
          <v-col cols="12">
            <v-text-field label="Email" type="email" v-model="editUserEmail"></v-text-field>
            <v-text-field
              label="Password"
              :type="showEditUserPassword ? 'text' : 'password'"
              :append-icon="showEditUserPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append="showEditUserPassword = !showEditUserPassword"
              v-model="editUserPassword"
              :error="isEditUserPasswordError"
              :error-messages="editPasswordErrorMessage"
            ></v-text-field>
            <v-text-field
              label="Password Check"
              :type="showEditUserPasswordCheck ? 'text' : 'password'"
              :append-icon="showEditUserPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append="showEditUserPassword = !showEditUserPassword"
              v-model="editUSerPasswordCheck"
              :error="isEditUserPasswordError"
              :error-messages="editPasswordErrorMessage"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="$emit('exit')" text="Back" />
        <v-btn
          color="primary"
          variant="tonal"
          :loading="loadingModifyUserDetails"
          type="submit"
          text="Confirm"
        />
      </v-card-actions>
    </v-form>
  </v-card>
</template>

<style scoped></style>