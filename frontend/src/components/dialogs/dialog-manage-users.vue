<script>
import dataService from '@/components/dataService.js'

export default {
  name: 'dialog-manage-users',
  data() {
    return {
      users: undefined,
      editProjectAdminList: [],
      editProjectUserSelect: [],
      originalInfo: {
        users: [],
        admin: []
      }
    }
  },
  props: {
    id: Number
  },
  emits: ['exit'],
  methods: {
    updateInfo: function () {
      let self = this
      // https://stackoverflow.com/questions/1187518/how-to-get-the-difference-between-two-arrays-in-javascript
      let removed = this.originalInfo.users.filter(x => !this.editProjectUserSelect.includes(x))
      let promises = []
      for (let userID of removed) {
        promises.push(dataService.removeUserFromProject(this.id, userID))
      }
      for (let userID of this.editProjectUserSelect) {
        promises.push(dataService.assignUserToProject(this.id, userID, this.editProjectAdminList.includes(userID)))
      }

      Promise.all(promises).then(function () {
        self.$emit('exit')
      }).catch(function () {
        alert("Errore")
      })
    },
    updateAdminUser: function (userID) {
      if (!this.editProjectUserSelect.includes(userID)) {
        const index = this.editProjectAdminList.indexOf(userID)
        if (index > -1) {
          this.editProjectAdminList.splice(index, 1)
        }
      }
    },
    updateAdmin: function (userID) {
      if (!this.editProjectUserSelect.includes(userID)) {
        this.editProjectUserSelect.push(userID)
      }
    },
    editProjectDialogAdminDisplay: function (userID) {
      return this.editProjectAdminList.includes(userID) ? 'Admin User' : 'Normal User'
    },
    updateUsers: function () {
      const self = this
      self.editProjectAdminList = []
      self.editProjectUserSelect = []
      dataService.getUsers().then(function (data) {
        dataService.getProjectByID(self.id).then(function (prData) {
          for (let user of prData.data.users) {
            self.editProjectUserSelect.push(user.user_id)
            if (user.is_project_admin) {
              self.editProjectAdminList.push(user.user_id)
            }
          }
          self.originalInfo.users = [...self.editProjectUserSelect]
          self.originalInfo.admin = [...self.editProjectAdminList]
          self.users = data.data
        })
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
            <template v-slot:prepend>
              <v-list-item-action>
                <v-checkbox-btn
                  v-model="editProjectUserSelect"
                  :value="user.id"
                  @change="updateAdminUser(user.id)"
                ></v-checkbox-btn>
              </v-list-item-action>
            </template>

            <template v-slot:append>
              <v-list-item-action>
                <v-switch
                  v-model="editProjectAdminList"
                  hide-details
                  hint="Is Project Admin?"
                  persistent-hint
                  :label="editProjectDialogAdminDisplay(user.id)"
                  :value="user.id"
                  @change="updateAdmin(user.id)"
                ></v-switch>
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
      <v-btn text="Update" variant="tonal" color="primary" @click="updateInfo"></v-btn>
      <v-btn text="Cancel" variant="tonal" @click="$emit('exit')"></v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped></style>
