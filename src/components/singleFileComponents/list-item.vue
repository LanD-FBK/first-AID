<script>
import dataService from '../dataService'
import { useNewTaskStore, useVariablesStore } from '@/store'

export default {
  data() {
    return {
      variablesStore: useVariablesStore(),
      newTaskStore: useNewTaskStore(),
      dialogDocs: false,
      dialogUsers: false,
      loadingEditUsers: false,

      //Manage Tasks vars
      dialogTasks: false,
      //TODO: add watcher to empty all fields on dialog closure
      dialogNewTask: false,
      validNewTaskData: false,
      rulesNewTask: [
        function (value) {
          if (value) return true
          return 'Please provide a task name'
        }
      ],
      taskName: '',
      isNewTaskActive: false,
      taskLanguageSelection: undefined,
      initialDataTaskSelection: undefined,
      newTurnTaskSelection: undefined,
      newTaskUsers: [],
      newTaskFiles: [],

      //Initial data vars
      //No further Axios configuration necessary.
      //baseURL does not apply if a full URL is supplied
      initialDataEndpoint: '',
      initialDataMethods: [],
      initialDataRoles: [],
      initialDataButtonLoading: false,
      initialDataError: false,
      initialDataErrorStatus: '',
      selectedInitialDataGenerationMethod: '',

      //New turn vars
      newTurnEndpoint: '',
      newTurnError: false,
      newTurnErrorMessage: '',
      newTurnButtonLoading: false,
      selectedNewTurnGenerationMethod: '',
      newTurnMethods: [],
      newTurnRoles: [],

      //Roles vars
      newTaskRoles: [
        {
          name: 'Speaker 1',
          id: 'speaker_1',
          number: 0
        },
        {
          name: 'Speaker 2',
          id: 'speaker_2',
          number: 1
        }
      ],

      files: undefined,
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
  mounted: function () {
    const self = this
    dataService.getProjectFiles(this.id).then(function (data) {
      self.files = data.data
      console.log(self.files)
    })
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
          console.log('done')
        })
        .catch(function (error) {
          //Gestione errore
        })
    },
    manageDocs: function (projectID) {
      this.dialogDocs = true
    },

    //Document handling
    //Not working
    addDocuments: function () {
      //TODO: Add loading
      const self = this
      dataService.uploadFiles(this.id, this.uploadedFiles).then(function (data) {
        console.log(data)
      })
    },
    removeDocument: function (documentID) {
      dataService.deleteProjectFiles(this.id, documentID).then(function (data) {
        console.log(data)
      })
    },

    manageUsers: function () {
      this.dialogUsers = true
      for (let user of this.users) {
        if (user.is_project_admin) {
          this.editProjectAdminList.push(user.user_id)
        }
      }
      console.log(this.editProjectAdminList)
    },

    //Manage Tasks funcs
    manageTasks: function () {
      this.dialogNewTask = true
    },

    //Consider merge in one function
    //Initial Data retrieval and handling
    getInitialData: function () {
      this.initialDataButtonLoading = true
      const self = this
      dataService
        .getTaskData(this.initialDataEndpoint)
        .then(function (data) {
          //May need to be changed if APIs change
          for (let item of data.data) {
            self.initialDataMethods.push(item.generation_method)
            self.initialDataRoles.push()
          }
          self.initialDataButtonLoading = false
        })
        .catch(function (error) {
          console.log(error)
          self.initialDataButtonLoading = false
          self.initialDataError = true
          self.initialDataErrorStatus = error.message
        })
    },
    //New turn Data retrieval and handling
    getNewTurn: function () {
      this.newTurnButtonLoading = true
      const self = this
      dataService
        .getTaskData(this.newTurnEndpoint)
        .then(function (data) {
          for (let item of data.data) {
            self.newTurnMethods.push(item.generation_method)
          }
          self.newTurnButtonLoading = false
        })
        .catch(function (error) {
          console.log(error)
          self.newTurnButtonLoading = false
          self.newTurnError = true
          self.newTurnErrorMessage = error.message
        })
    },

    submitNewTask: function () {
      //TODO: add loading
    },
    editProjectDialogAdminDisplay(userID) {
      if (this.editProjectAdminList.includes(userID)) return 'Admin User'
      return 'Normal User'
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
    isInitialDataFormDisabled() {
      return this.initialDataTaskSelection === 'Pre-filled' ? false : true
    },
    isNewTurnFormDisabled() {
      return this.newTurnTaskSelection === 'Choice' ? false : true
    },
    isInitialDataSelectionDisabled() {
      if (this.initialDataMethods.length == 0 || this.isInitialDataFormDisabled) return true
      return false
    },
    isNewTurnSelectionDisabled() {
      if (this.newTurnMethods.length == 0 || this.isNewTurnFormDisabled) return true
      return false
    }
  },
  watch: {
    editProjectAdminList(newValue, oldValue) {
      console.warn(newValue)
    },
    dialogUsers(newValue, oldValue) {
      this.editProjectAdminList = []
      this.editProjectUserSelect = []
    }
  }
}
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-row align="center">
            <v-col cols="12" sm="3" md="6" xl="6" xs="6">
              <v-row class="d-flex justify-left">
                <v-col>
                  <!--Wrong position-->
                  <v-card-title>{{ title }}</v-card-title>
                  <v-card-subtitle>Project ID: {{ id }}</v-card-subtitle>
                  <v-card-text>{{ isActive ? 'Active' : 'Not Active' }}</v-card-text>
                  <v-card-text>{{ isButton }}</v-card-text>
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
              <v-card-actions v-if="!isButton">
                <v-btn
                  color="primary"
                  variant="elevated"
                  prepend-icon="mdi-file-document-multiple-outline"
                  text="Manage Docs"
                  @click="manageDocs(id)"
                />
                <v-btn
                  color="primary"
                  variant="elevated"
                  prepend-icon="mdi-account-circle-outline"
                  text="Manage Users"
                  @click="manageUsers()"
                />
                <v-btn
                  color="primary"
                  variant="elevated"
                  prepend-icon="mdi-format-list-checks"
                  text="Manage Tasks"
                  @click="manageTasks()"
                />
                <v-btn
                  color="secondary"
                  variant="elevated"
                  prepend-icon="mdi-book-edit-outline"
                  text="Annotate"
                  @click="console.log('annotate')"
                />
                <v-btn
                  color="error"
                  variant="elevated"
                  prepend-icon="mdi-trash-can-outline"
                  text="Delete"
                  @click="$emit('deleteProject')"
                />
              </v-card-actions>
              <v-card-actions v-else>
                <v-btn
                  color="primary"
                  variant="elevated"
                  icon="mdi-file-document-multiple-outline"
                  @click="manageDocs(id)"
                />
                <v-btn
                  color="primary"
                  variant="elevated"
                  icon="mdi-account-circle-outline"
                  @click="manageUsers()"
                />
                <v-btn
                  color="primary"
                  variant="elevated"
                  icon="mdi-format-list-checks"
                  @click="manageTasks()"
                />
                <v-btn
                  color="secondary"
                  variant="elevated"
                  icon="mdi-book-edit-outline"
                  @click="console.log('annotate')"
                />
                <v-btn
                  color="error"
                  variant="elevated"
                  icon="mdi-trash-can-outline"
                  @click="$emit('deleteProject')"
                />
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
          <v-progress-circular
            indeterminate
            class="mx-auto"
            v-if="files == undefined"
          ></v-progress-circular>
          <small v-else-if="files == 0" class="text-caption text-medium-emphasis"
            >There are no files in this project</small
          >
          <v-list v-else>
            <v-list-item
              variant=""
              v-for="file of files"
              :key="file.id"
              :title="file.name"
              :subtitle="'File ID: ' + file.id"
            >
              <template v-slot:append>
                <v-btn icon="mdi-delete" variant="flat" @click="removeDocument(file.id)" />
              </template>
            </v-list-item>
          </v-list>

          <v-file-input
            v-model="uploadedFiles"
            label="Upload new Files"
            multiple
            @change="console.log('uploadedFiles')"
            class="ma-2"
          >
          </v-file-input>
        </v-card-text>
        <v-card-actions>
          <!--
          <v-btn @click="addDocuments()">Cancel</v-btn>
          -->
          <v-btn color="primary" variant="flat" @click="console.log(uploadedFiles)">Upload</v-btn>
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
                    <v-switch
                      v-model="editProjectAdminList"
                      hide-details
                      hint="Is Project Admin?"
                      persistent-hint
                      :label="editProjectDialogAdminDisplay(user.user.id)"
                      :value="user.user.id"
                    ></v-switch>
                  </v-list-item-action>
                </template>

                <template v-slot:prepend>
                  <v-list-item-action>
                    <v-checkbox-btn
                      v-model="editProjectUserSelect"
                      :value="user.user.id"
                    ></v-checkbox-btn>
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
          <v-btn
            text="Remove Users"
            variant="tonal"
            color="error"
            :disabled="isDeleteButtonEditProjectDialog"
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
    </v-dialog>

    <v-dialog v-model="dialogTasks" :max-width="variablesStore.dialogMaxWidth">
      <v-card prepend-icon="mdi-format-list-checks" title="Manage Tasks">
        <v-list lines="two">
          <v-list-subheader>Select the task you wish to edit</v-list-subheader>
          <v-list-item
            v-for="task of this.tasks"
            :key="task.id"
            :title="task.title"
            :subtitle="task.id"
          >
          </v-list-item>
        </v-list>
        <v-card-actions>
          <v-btn color="primary" variant="elevated" text="Add New" />
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!--New Task Dialog-->
    <v-dialog v-model="dialogNewTask" max-width="90%">
      <v-card title="Add New Task" prepend-icon="mdi-file-document-plus-outline">
        <v-form v-model="validNewTaskData" :rules="rulesNewTask" @submit.prevent="submitNewTask">
          <v-card-text>
            <v-row dense>
              <v-col cols="12" md="8" sm="8">
                <v-text-field label="Task Name" required v-model="taskName" :rules="rulesNewTask" />
              </v-col>

              <v-col cols="12" md="2" sm="2" class="d-flex justify-center">
                <v-select
                  label="Language"
                  v-model="taskLanguageSelection"
                  :items="newTaskStore.language"
                  item-title="complete"
                  item-value="apiFormat"
                />
              </v-col>
              <v-col cols="12" md="2" sm="2" class="d-flex justify-center">
                <v-checkbox label="Is Active" v-model="isNewTaskActive"></v-checkbox>
              </v-col>

              <!--Users list-->
              <v-col cols="6">
                <v-list height="200px">
                  <v-list-subheader>Select users</v-list-subheader>
                  <v-list-item
                    v-for="user in users"
                    :key="user.user.id"
                    :title="user.user.username"
                    :subtitle="user.user.email"
                  >
                    <template v-slot:prepend>
                      <v-list-item-action>
                        <v-checkbox-btn v-model="newTaskUsers" :value="user.user.id" />
                      </v-list-item-action>
                    </template>
                  </v-list-item>
                </v-list>
              </v-col>

              <!--Files list-->
              <v-col cols="6">
                <v-list height="200px">
                  <v-list-subheader>Select files</v-list-subheader>
                  <v-list-item
                    v-for="file of files"
                    :key="file.id"
                    :title="file.name"
                    :subtitle="'File ID: ' + file.id"
                  >
                    <template v-slot:prepend>
                      <v-list-item-action>
                        <v-checkbox-btn v-model="newTaskFiles" :value="file.id" />
                      </v-list-item-action>
                    </template>
                  </v-list-item>
                </v-list>
              </v-col>
              <!--Initial Data and New Turn-->
              <v-col cols="6">
                <v-select
                  label="Initial Data"
                  v-model="initialDataTaskSelection"
                  :items="newTaskStore.initialData"
                ></v-select>
                <!-- text-field and select are enabled only when initial data is 'pre-filled'-->
                <v-text-field
                  v-model="initialDataEndpoint"
                  label="URL"
                  :disabled="isInitialDataFormDisabled"
                  :error="initialDataError"
                  :error-messages="initialDataErrorStatus"
                >
                  <template v-slot:append>
                    <v-btn
                      text="Go"
                      @click="getInitialData()"
                      variant="tonal"
                      :loading="initialDataButtonLoading"
                    />
                  </template>
                </v-text-field>
                <v-select
                  v-model="selectedInitialDataGenerationMethod"
                  label="Generation Method"
                  :items="initialDataMethods"
                  :disabled="isInitialDataSelectionDisabled"
                ></v-select>
              </v-col>
              <v-col cols="6">
                <v-select
                  label="New Turn"
                  v-model="newTurnTaskSelection"
                  :items="newTaskStore.newTurn"
                ></v-select>
                <v-text-field
                  v-model="newTurnEndpoint"
                  label="URL"
                  :disabled="isNewTurnFormDisabled"
                  :error="newTurnError"
                  :error-messages="newTurnErrorMessage"
                >
                  <template v-slot:append>
                    <v-btn
                      text="Go"
                      @click="getNewTurn()"
                      variant="tonal"
                      :loading="newTurnButtonLoading"
                    />
                  </template>
                </v-text-field>
                <v-select
                  v-model="selectedNewTurnGenerationMethod"
                  label="Generation Method"
                  :items="newTurnMethods"
                  :disabled="isNewTurnSelectionDisabled"
                ></v-select>
              </v-col>
              <v-col cols="12">
                <!--
                <p class="text-body-1 mt-2">Roles</p>
                -->
                <v-row dense v-for="role in newTaskRoles" :key="role.number">
                  <v-col>
                    <v-text-field v-model="role.name" label="Speaker Role"></v-text-field>
                  </v-col>
                  <v-col>
                    <v-text-field v-model="role.id" label="Speaker ID">
                      <template v-slot:append>
                        <v-btn icon="mdi-trash-can-outline" variant="tonal" />
                      </template>
                    </v-text-field>
                  </v-col>
                </v-row>
                <v-btn class="mb-4" variant="tonal" text="Add New Role" />
              </v-col>
            </v-row>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text="Cancel" variant="tonal" @click="dialogNewTask = false" />
            <!--type="submit"-->
            <v-btn text="Create" variant="tonal" color="primary" />
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </v-container>
</template>
