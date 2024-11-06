<script>
import dataService from '@/components/dataService.js'

export default {
  name: 'dialog-manage-users',
  data() {
    return {
      users: undefined,
      editProjectAdminList: [],
      editProjectUserSelect: [],
      dialogAddUserToProject: false
    }
  },
  props: {
    id: Number
  },
  emits: ['exit'],
  methods: {
    submitManageUsers: function () {
      const self = this
      this.loadingEditUsers = true
      let submitAdminList = []
      let submitUserList = []
      for (let user of this.users) {
        submitUserList.push(user.id)
        if (this.editProjectAdminList.includes(user.id)) {
          submitAdminList.push(true)
        } else {
          submitAdminList.push(false)
        }
      }
      dataService
        .editProject(this.id, this.title, this.isActive, submitUserList, submitAdminList)
        .then(function () {
          self.loadingEditUsers = false
          self.$emit('exit')
        })
        .catch(function (error) {
          console.log(error)
          //TODO: error handling with error dialog component
        })
    },
    editProjectDialogAdminDisplay: function (userID) {
      return this.editProjectAdminList.includes(userID) ? 'Admin User' : 'Normal User'
    },
    updateUsers: function () {
      const self = this
      dataService.getUsers().then(function (data) {
        self.users = data.data
        for (let user of self.users) {
          if (user.is_project_admin) {
            this.editProjectAdminList.push(user.user_id)
          }
        }
      })
    }
  },
  mounted() {
    this.updateUsers()
  }
}
</script>

<template>
  <v-card prepend-icon="mdi-account-circle-outline" title="Manage Project Users">
    <v-row dense>
      <v-col cols="12">
        <v-progress-circular
          indeterminate
          class="mx-auto"
          v-if="users === undefined"
        ></v-progress-circular>
        <v-list lines="two" v-else>
          <v-list-subheader>Select the User to edit</v-list-subheader>
          <v-list-item v-for="user in users" :key="user.id">
            <!--Prepend checkbox for project inclusion-->
            <template v-slot:append>
              <v-list-item-action>
                <v-switch
                  v-model="editProjectAdminList"
                  hide-details
                  hint="Is Project Admin?"
                  persistent-hint
                  :label="editProjectDialogAdminDisplay(user.id)"
                  :value="user.id"
                ></v-switch>
              </v-list-item-action>
            </template>

            <template v-slot:prepend>
              <v-list-item-action>
                <v-checkbox-btn
                  v-model="editProjectUserSelect"
                  :value="user.id"
                ></v-checkbox-btn>
              </v-list-item-action>
            </template>

            <v-list-item-title>{{ user.username }}</v-list-item-title>
            <v-list-item-subtitle> {{ user.email }}</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-col>
    </v-row>
    <v-divider></v-divider>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        text="Remove Users"
        variant="tonal"
        color="error"
        :disabled="editProjectUserSelect.length === 0"
      ></v-btn>
      <v-btn
        text="Add New User"
        variant="tonal"
        color="primary"
        @click="dialogAddUserToProject = true"
      ></v-btn>
      <v-btn text="Done" variant="tonal" @click="submitManageUsers()"></v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped></style>
