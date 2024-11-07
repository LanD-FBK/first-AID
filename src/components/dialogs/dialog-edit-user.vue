<script>
import dataService from '@/components/dataService.js'
import DialogGeneric from '@/components/dialogs/dialog-generic.vue'
import { useLoginStore } from '@/store.js'

export default {
  name: 'dialog-edit-user',
  components: { DialogGeneric },
  emits: ['refresh', 'exit'],
  data() {
    return {
      loginStore: useLoginStore(),
      usersList: undefined,
      dialogModifyUserDetails: false,
      editUser: undefined
    }
  },
  mounted: function () {
    this.updateUsers()
  },
  methods: {
    updateUsers: function () {
      const self = this
      dataService.getUsers().then(function (data) {
        self.usersList = data.data
      })
    },
    openUserModifyDialog: function (index) {
      this.editUser = this.usersList[index]
      this.dialogModifyUserDetails = true
      // console.log(this.usersList[index])
      // this.editUserID = userID
      // this.editUserUsername = username
      // this.editUserEmail = email
      // this.editUserIsActive = Boolean(isActive)
      // this.isUserModifyDialogLoaded = true
    }
  }
}
</script>

<template>
  <v-card prepend-icon="mdi-account-edit-outline" title="Edit User">
    <DialogGeneric
      v-if="loginStore.is_admin"
      v-model="dialogModifyUserDetails"
      component-file="./dialog-user-form.vue"
      :data="{ userData: editUser }"
    ></DialogGeneric>
    <v-progress-circular
      indeterminate
      class="mx-auto"
      v-if="usersList === undefined"
    ></v-progress-circular>
    <v-list lines="two" v-else>
      <v-list-subheader>Select the User to edit</v-list-subheader>
      <v-list-item
        prepend-icon="mdi-account-circle-outline"
        v-for="(user, index) in usersList"
        :key="user.id"
        :title="user.username"
        :subtitle="user.email"
        @click="openUserModifyDialog(index)"
      >
        <template v-slot:append>
          <v-icon icon="mdi-pencil" />
        </template>
      </v-list-item>
    </v-list>
    <v-divider v-if="usersList !== undefined"></v-divider>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn text="Done" variant="tonal" @click="$emit('exit')"></v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped></style>
