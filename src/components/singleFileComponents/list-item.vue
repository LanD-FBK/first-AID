<script>
import dataService from '../dataService'
import DynamicButton from './dynamic-button.vue'
import { useNewTaskStore, useVariablesStore } from '@/store'
import TaskDialog from './task-dialog.vue';

export default {
  components: {
    DynamicButton,
    TaskDialog
  },
  data() {
    return {
      variablesStore: useVariablesStore(),
      newTaskStore: useNewTaskStore(),
      dialogDocs: false,
      dialogUsers: false,
      loadingEditUsers: false,

      //Manage Tasks vars
      dialogTasks: false,

      files: null,
      uploadedFiles: undefined,

      dialogAddUserToProject: false,
      editProjectAdminList: [],
      editProjectUserSelect: []
    }
  },
  props: {
    title: String,
    users: Object,
    id: Number,
    tasks: Object,
    isActive: Boolean
  },
  //Not used at the moment, consider deleting
  mounted: function () {
    const self = this
  },
  methods: {
    submitManageUsers: function () {
      const self = this
      this.loadingEditUsers = true
      let submitAdminList = []
      let submitUserList = []
      for (let user of this.users) {
        submitUserList.push(user.user_id)
        if (this.editProjectAdminList.includes(user.user_id)) {
          submitAdminList.push(true)
        } else {
          submitAdminList.push(false)
        }
      }
      dataService
        .editProject(this.id, this.title, this.isActive, submitUserList, submitAdminList)
        .then(function (data) {
          self.loadingEditUsers = false
          self.dialogUsers = false
        })
        .catch(function (error) {
          //Gestione errore
        })
    },
    manageDocs: function (projectID) {
      this.dialogDocs = true
      this.files = undefined
    },

    //Document handling
    uploadDocs: function () {
      const self = this
      let files = document.getElementById('uploadFiles').files
      // console.log(files)
      dataService.uploadFiles(this.id, files).then(function (data) {
        console.log(data)
        //Triggers watcher and refreshes files list
        self.files = undefined
      })
        .catch(function (error) {
          console.log(error)
          //TODO: error handling with error dialog component
        })

    },

    removeDocument: function (documentID) {
      const self = this
      dataService.deleteProjectFiles(this.id, documentID).then(function (data) {
        console.log(data)
        //Triggers watcher and refreshes files list
        self.files = undefined
      })
    },

    manageUsers: function () {
      this.dialogUsers = true
      for (let user of this.users) {
        if (user.is_project_admin) {
          this.editProjectAdminList.push(user.user_id)
        }
      }
      // console.log(this.editProjectAdminList)
    },

    //Manage Tasks funcs
    manageTasks: function () {
      this.dialogTasks = true
    },

    openNewTask: function () {
      this.dialogNewTask = true
    },

    editProjectDialogAdminDisplay: function (userID) {
      if (this.editProjectAdminList.includes(userID)) return 'Admin User'
      return 'Normal User'
    },
    openTaskList: function (id) {
      this.$router.push({
        name: 'tasks',
        params: { projectID: id }
      })
    }
  },
  computed: {
    displaySize() {
      return this.$vuetify.display.name
    },
    isButton() {
      //If true screen size is 'md' or less, so we need to show icons instead of buttons
      return this.$vuetify.display.mdAndDown ? true : false
    },
    isDeleteButtonEditProjectDialog() {
      return this.editProjectUserSelect.length === 0 ? true : false
    },
  },
  watch: {
    editProjectAdminList(newValue, oldValue) {
      console.warn(newValue)
    },
    dialogUsers(newValue, oldValue) {
      this.editProjectAdminList = []
      this.editProjectUserSelect = []
    },
    files(newValue, oldValue) {
      const self = this
      if (newValue == undefined) {
        dataService.getProjectFiles(this.id).then(function (data) {
          self.files = data.data
          console.log(self.files)
        })
      }
    }
  },
}
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card @click.prevent="openTaskList(id)">
          <v-row align="center">
            <v-col cols="12" sm="3" md="6" xl="6" xs="6">
              <v-row class="d-flex justify-left">
                <v-col>
                  <v-card-title>{{ title }}</v-card-title>
                  <v-card-subtitle>Project ID: {{ id }}. Project {{ isActive ? 'Active' : 'Inactive'
                    }}</v-card-subtitle>
                </v-col>
                <!--
                <v-col>
                  <v-btn
                    icon="mdi-pencil-circle-outline"
                    class="ma-2"
                    variant="plain"
                    @click="console.log('icon')"
                  />
                </v-col>
                -->
              </v-row>
            </v-col>
            <v-col cols="12" lg="6" sm="9" md="6" xl="6" xs="6">
              <v-card-actions>
                <DynamicButton :icon="'mdi-file-document-multiple-outline'" :text="'Manage Docs'"
                  @click.stop="manageDocs(id)" />
                <DynamicButton :icon="'mdi-account-circle-outline'" :text="'Manage Users'"
                  @click.stop="manageUsers()" />
                <DynamicButton :icon="'mdi-format-list-checks'" :text="'Manage Tasks'" @click.stop="manageTasks()" />
                <DynamicButton :icon="'mdi-trash-can-outline'" :text="'Delete'" @click.stop="$emit('deleteProject')" />
              </v-card-actions>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <!--Manage Docs dialog-->
    <!--TODO: add spacer before action buttons-->
    <v-dialog v-model="dialogDocs" :max-width="variablesStore.dialogMaxWidth">
      <v-card prepend-icon="mdi-file-document-multiple-outline" title="Manage Project Documents">
        <v-card-text>
          <!--TODO: center spinner-->
          <v-progress-circular indeterminate class="mx-auto" v-if="files == undefined"></v-progress-circular>
          <template v-else-if="files == 0">
            <v-row>
              <!--TODO: fix spacing-->
              <p class="text-caption text-medium-emphasis">There are no files in this project</p>
            </v-row>
            <v-row>
              <input type="file" multiple id="uploadFiles" class="ma-2">
              </input>
            </v-row>
          </template>
          <template v-else>
            <v-list>
              <v-list-item v-for="file of files" :key="file.id" :title="file.name" :subtitle="'File ID: ' + file.id">
                <template v-slot:append>
                  <!--TODO: add spinner after click to let user know that deletion is in progress-->
                  <v-btn icon="mdi-delete" variant="flat" @click="removeDocument(file.id)" />
                </template>
              </v-list-item>
            </v-list>
            <input type="file" multiple id="uploadFiles" class="ma-2">
            </input>
          </template>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" variant="outlined" @click="uploadDocs()">Upload</v-btn>
          <v-btn color="primary" variant="flat" @click="dialogDocs = false">Done</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Manage users dialog-->
    <v-dialog v-model="dialogUsers" :max-width="variablesStore.dialogMaxWidth">
      <v-card prepend-icon="mdi-account-circle-outline" title="Manage Project Users">
        <v-row dense>
          <v-col cols="12">
            <v-list lines="two">
              <v-list-subheader>Select the User to edit</v-list-subheader>
              <v-list-item v-for="user in users" :key="user.user.id">
                <!--Prepend checkbox for project inclusion-->
                <template v-slot:append>
                  <v-list-item-action>
                    <v-switch v-model="editProjectAdminList" hide-details hint="Is Project Admin?" persistent-hint
                      :label="editProjectDialogAdminDisplay(user.user.id)" :value="user.user.id"></v-switch>
                  </v-list-item-action>
                </template>

                <template v-slot:prepend>
                  <v-list-item-action>
                    <v-checkbox-btn v-model="editProjectUserSelect" :value="user.user.id"></v-checkbox-btn>
                  </v-list-item-action>
                </template>

                <v-list-item-title>{{ user.user.username }}</v-list-item-title>
                <v-list-item-subtitle> {{ user.user.email }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text="Remove Users" variant="tonal" color="error" :disabled="isDeleteButtonEditProjectDialog"></v-btn>
          <v-btn text="Add New User" variant="tonal" color="primary" @click="dialogAddUserToProject = true"></v-btn>
          <v-btn text="Done" variant="tonal" @click="submitManageUsers()"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogTasks" :max-width="variablesStore.dialogMaxWidth">
      <v-card prepend-icon="mdi-format-list-checks" title="Manage Tasks">
        <v-list lines="two">
          <v-list-subheader>Select the task you wish to edit</v-list-subheader>
          <v-list-item v-for="task of this.tasks" :key="task.id" :title="task.title" :subtitle="task.id">
          </v-list-item>
        </v-list>
        <v-card-actions>
          <TaskDialog :users="this.users" :files="this.files" />
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
