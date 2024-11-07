<script>
import { useVariablesStore } from '@/store.js'
import dataService from '@/components/dataService.js'

export default {
  props: {
    usersList: Array
  },
  emits: ['refresh', 'exit'],
  data() {
    return {
      variablesStore: useVariablesStore(),
      validNewProjectData: false,
      projectName: '',
      rulesCreateProject: [
        function (value) {
          if (value) return true
          return 'Please provide a project name'
        }
      ],
      isProjectActive: true,
      projectUsersList: [],
      adminUsersList: [],
      successNewProjectSnackbar: false
    }
  },
  methods: {
    submitNewProject: function () {
      const self = this
      if (this.validNewProjectData) {
        this.loadingCreateProject = true
        //Works but extremely convoluted

        //In order to avoid JS' shallow copy
        let submitAdminList = Array.from(this.projectUsersList)

        for (let user of submitAdminList) {
          submitAdminList[submitAdminList.indexOf(user)] = this.adminUsersList.includes(user)
        }
        dataService
          .createProject(
            this.projectName,
            this.isProjectActive,
            this.projectUsersList,
            submitAdminList
          )
          .then(function () {
            self.$emit('refresh')
          })
          .catch(function (error) {
            self.errorDialog = true
            self.errorUserDialogText = String(error.message + ': ' + error.response.statusText)
          })
      }
    },
    isProjectAdminDisplay: function (userID) {
      return this.adminUsersList.includes(userID) ? 'Admin User' : 'Normal User'
    },
    isAdminButtonDisabled: function (userID) {
      return !this.projectUsersList.includes(userID)
    }
  }
}
</script>

<template>
  <v-card prepend-icon="mdi-plus" title="Create New Project">
    <v-form
      @submit.prevent="submitNewProject"
      v-model="validNewProjectData"
      :rules="rulesCreateProject"
    >
      <v-card-text>
        <v-row dense>
          <v-col cols="12" md="9" sm="9">
            <v-text-field
              label="Project Name"
              required
              v-model="projectName"
              :rules="rulesCreateProject"
            />
          </v-col>

          <v-col cols="12" md="3" sm="3" class="d-flex justify-center">
            <v-checkbox label="Is Active" class="ml-2" v-model="isProjectActive"></v-checkbox>
          </v-col>

          <v-col cols="12">
            <v-progress-circular indeterminate v-if="usersList === undefined"></v-progress-circular>
            <v-list v-else>
              <v-list-subheader>Select Users</v-list-subheader>
              <v-list-item v-for="user in usersList" :key="user.id">
                <!--Prepend checkbox for project inclusion-->
                <template v-slot:prepend>
                  <v-list-item-action>
                    <v-checkbox-btn v-model="projectUsersList" :value="user.id"></v-checkbox-btn>
                  </v-list-item-action>
                </template>

                <template v-slot:append>
                  <v-list-item-action>
                    <v-switch
                      v-model="adminUsersList"
                      hide-details
                      hint="Is Project Admin?"
                      persistent-hint
                      :label="isProjectAdminDisplay(user.id)"
                      :value="user.id"
                      :disabled="isAdminButtonDisabled(user.id)"
                    ></v-switch>
                  </v-list-item-action>
                </template>

                <v-list-item-title>{{ user.username }}</v-list-item-title>
                <v-list-item-subtitle> {{ user.email }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
          <small class="text-caption text-medium-emphasis"
            >These users will be able to access this project.</small
          >
        </v-row>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn text="Cancel" variant="plain" @click.stop="$emit('exit')"></v-btn>

        <v-btn color="primary" text="Create" variant="tonal" type="submit" :loading="false"></v-btn>
      </v-card-actions>
    </v-form>
  </v-card>
</template>

<style scoped></style>
